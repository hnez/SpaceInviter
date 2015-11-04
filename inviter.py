#!/usr/bin/env python

"""
  inviter.py, wsgi server backend of the
  SpaceInviter web application.

  Copyright (C) 2015 Leonard Goehrs

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation, either version 3 of the
  License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import bottle as bo
import sqlobject as so
import random
import string

class DictSQLObject(so.SQLObject):
    """Add dict like addressing to SQLObjects"""
    def __getitem__ (self, key):
        return (getattr(self, key))

    def __setitem__ (self, key, value):
        setattr(self, key, value)

class Event (DictSQLObject):
    """
    Collects information about Events
    Referenced to by the Guest and ChatMsg Tables
    """
    name = so.UnicodeCol()
    description = so.UnicodeCol()

class Guest (DictSQLObject):
    """
    Collects information about Guests
    Refrenced to by the ChatMsg Table
    """
    name = so.UnicodeCol()
    admin = so.BoolCol(default=False)
    parprop = so.IntCol(default=-1)
    token = so.StringCol(length=8)
    event = so.ForeignKey('Event')

class ChatMsg (DictSQLObject):
    guest = so.ForeignKey('Guest')
    event = so.ForeignKey('Event')
    content = so.UnicodeCol()
    msgid= so.StringCol(length=8)

class WebApi(bo.Bottle):
    def __init__(self, dburi='sqlite:/:memory:'):
        super(WebApi, self).__init__()

        # Guest api endpoints
        self.get('/api/token/<token>', callback=self.api_get_guest)
        self.put('/api/token/<token>', callback=self.api_edit_guest)
        self.post('/api/token/<token>', callback=self.api_new_guest)
        self.post('/api/token', callback=self.api_new_event)

        # Event api endpoints
        self.get('/api/token/<token>/event', callback=self.api_get_event)
        self.put('/api/token/<token>/event', callback=self.api_edit_event)

        # Chat api endpoints
        self.get('/api/token/<token>/chat', callback=self.api_get_chat)
        self.post('/api/token/<token>/chat', callback=self.api_new_message)
        self.get('/api/token/<token>/chat/<msgid>', callback=self.api_get_message)
        self.put('/api/token/<token>/chat/<msgid>', callback=self.api_edit_message)
        self.delete('/api/token/<token>/chat/<msgid>', callback=self.api_del_message)

        # Static files
        self.get('/', callback=self.get_static('index.html'))
        self.get('/event', callback=self.get_static('event.html'))

        for f in ['inviter.js', 'histogram.js', 'frontend.js', 'style.css', 'spinner.gif']:
            self.get('/' + f, callback=self.get_static(f))

        # Create tables that do not exist
        self.db= so.connectionForURI(dburi)
        Event.createTable(True, connection=self.db)
        Guest.createTable(True, connection=self.db)
        ChatMsg.createTable(True, connection=self.db)

    def gentoken (self, length=8):
        """generate a random token string"""
        s=''.join([random.choice(string.lowercase) for i in range(length)])

        return (s)

    def guest_by_token (self, token):
        """select a single guest from the database by token or None"""
        guest= Guest.selectBy(self.db, token=token)

        return (guest.getOne(None))

    def guests_by_event (self, event):
        """get a list of guest for a event"""

        # SQLObject select results can not be addressed by index.
        # This hack creates an array of the results
        guests= [g for g in Guest.selectBy(self.db, event=event.id)]

        return (guests)

    def chats_by_event (self, event):
        """get a list of chat messages for a event"""

        query= ChatMsg.selectBy(self.db, event=event.id)

        chats= [c for c in query.orderBy(ChatMsg.q.id)]

        return (chats)

    def msg_by_msgid (self, msgid):
        """get a single message by message id or None"""

        msg= ChatMsg.selectBy(self.db, msgid=msgid)

        return (msg.getOne(None))


    def create_guest(self, event, info):
        """create a new guest providing defaults for fields not in info"""

        clean={}
        clean['name']='John Doe'
        clean['admin']=False
        clean['parprop']=-1
        clean['token']=self.gentoken()
        clean['event']=event

        for k in ['name', 'admin', 'parprop']:
            if (k in info):
                clean[k]=info[k]

        guest= Guest(connection=self.db, **clean)

        return(guest)

    def create_message(self, guest, info):
        """create a new message providing defaults for fields not in info"""

        clean={}

        clean['content']=''
        clean['msgid']= self.gentoken()
        clean['event']= guest.event
        clean['guest']= guest

        for k in ['content']:
            if (k in info):
                clean[k]=info[k]

        msg= ChatMsg(connection=self.db, **clean)

        return(msg)

    def get_static(self, path):
        """helper to serve static files from disk"""

        def file_cb ():
            return (bo.static_file(path, root='.'))

        return (file_cb)

    def api_get_event (self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        ret={}

        guest= self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        event= guest.event

        for k in ['name', 'description']:
            ret[k]= event[k]

        guests= self.guests_by_event(event)

        ret['guests']=[]
        for g in guests:
            clean={}
            for k in ['name', 'parprop', 'admin']:
                clean[k]= g[k]

            if (guest.admin):
                clean['token']= g['token']
                ret['guests'].append(clean)

            elif (g['parprop'] > 0):
                ret['guests'].append(clean)

        return (ret)

    def api_edit_event(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest= self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        event= guest.event

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        if (not guest.admin):
            bo.abort(403, 'authentification failed')

        for k in ['name', 'description']:
            if (k in req):
                event[k]=req[k]

        bo.response.status= 204

    def api_get_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest = self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        ret = {}
        for k in ['token', 'name', 'parprop', 'admin']:
            ret[k]= guest[k]

        return (ret)

    def api_edit_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest = self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        for k in ['name', 'parprop']:
            if (k in req):
                guest[k]=req[k]

        bo.response.status= 204

    def api_new_event(self):
        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        info={}
        info['name']='New Event'
        info['description']='Please edit your description'
        event= Event(connection=self.db, **info)

        guest= self.create_guest(event, req)

        bo.redirect('/api/token/' + guest.token, 201)

    def api_new_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest= self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        event= guest.event

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        if (not guest.admin):
            bo.abort(403, 'authentification failed')

        newg= self.create_guest(event, req)

        bo.redirect('/api/token/' + newg.token, 201)

    def api_get_chat(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest= self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        event= guest.event

        etag= bo.request.headers.get('If-None-Match')

        msgs= self.chats_by_event(event)
        lastid= msgs[-1].msgid if len(msgs) else 'empty'

        if (etag == lastid):
            bo.abort(304, 'not modified')
        else:
            bo.response.set_header('ETag', lastid)

        ret={}
        ret['msgs']= []

        for m in msgs:
            clean={}

            for k in ['content', 'msgid']:
                clean[k]= m[k]

            clean['author']= m.guest.name

            ret['msgs'].append(clean)

        return (ret)

    def api_new_message(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        guest= self.guest_by_token(token)

        if (guest is None):
            bo.abort(404, 'token not found')

        event= guest.event

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        newm= self.create_message(guest, req)

        link= '/api/token/' + guest.token + '/chat/' + newm.msgid
        bo.redirect(link, 201)

    def api_get_message(self, token, msgid):
        bo.abort(501, 'me much lazy')

    def api_edit_message(self, token, msgid):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        if (len(msgid) != 8):
            bo.abort(404, 'invalid msgid')

        guest= self.guest_by_token(token)
        msg= self.msg_bs_msgid(msgid)

        if (guest is None):
            bo.abort(404, 'token not found')

        if (msg is None):
            bo.abort(404, 'msgid not found')

        event= guest.event

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json

        if (not (guest.admin or msg.guest==guest)):
            bo.abort(403, 'authentification failed')

        for k in ['content']:
            if k in req:
                msg[k]=req[k]

        bo.response.status= 204

    def api_del_message(self, token, msgid):
        bo.abort(501, 'me much lazy')


if __name__ == '__main__':
    import sys

    dburi= sys.argv[1] if len(sys.argv) > 1 else "sqlite:///tmp/inviter.db"
    
    app = WebApi(dburi)
    app.run(host='localhost', port=8080)
