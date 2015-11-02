import bottle as bo
import sqlobject as so
import random
import string

class DictSQLObject(so.SQLObject):
    def __getitem__ (self, key):
        return (getattr(self, key))

    def __setitem__ (self, key, value):
        setattr(self, key, value)

class Event (DictSQLObject):
    name = so.UnicodeCol()
    description = so.UnicodeCol()

class Guest (DictSQLObject):
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

        self.get('/api/token/<token>', callback=self.api_get_guest)
        self.put('/api/token/<token>', callback=self.api_edit_guest)
        self.post('/api/token/<token>', callback=self.api_new_guest)
        self.post('/api/token', callback=self.api_new_event)

        self.get('/api/token/<token>/event', callback=self.api_get_event)
        self.put('/api/token/<token>/event', callback=self.api_edit_event)

        self.get('/api/token/<token>/chat', callback=self.api_get_chat)
        self.post('/api/token/<token>/chat', callback=self.api_new_message)
        self.get('/api/token/<token>/chat/<msgid>', callback=self.api_get_message)
        self.put('/api/token/<token>/chat/<msgid>', callback=self.api_edit_message)
        self.delete('/api/token/<token>/chat/<msgid>', callback=self.api_del_message)
        
        self.get('/', callback=self.get_static('index.html'))
        self.get('/event', callback=self.get_static('event.html'))
        self.get('/inviter.js', callback=self.get_static('inviter.js'))
        self.get('/histogram.js', callback=self.get_static('histogram.js'))
        self.get('/frontend.js', callback=self.get_static('frontend.js'))
        self.get('/style.css', callback=self.get_static('style.css'))
        self.get('/spinner.gif', callback=self.get_static('spinner.gif'))

        self.db= so.connectionForURI(dburi)
        Event.createTable(True,connection=self.db)
        Guest.createTable(True,connection=self.db)
        ChatMsg.createTable(True, connection=self.db)
        
    def gentoken (self):
        s=''.join([random.choice(string.lowercase) for i in range(8)])

        return (s)

    def guest_by_token (self, token):
        guest= Guest.selectBy(self.db, token=token)
        
        return (guest.getOne(None))

    def guests_by_event (self, event):
        guests= [g for g in Guest.selectBy(self.db, event=event.id)]

        return (guests)

    def chats_by_event (self, event):
        chats= [c for c in ChatMsg.selectBy(self.db, event=event.id)]

        return (chats)

    def msg_by_msgid (self, msgid):
        msg= ChatMsg.selectBy(self.db, msgid=msgid)
        
        return (msg.getOne(None))

    
    def create_guest(self, event, info):       
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

        msgs= self.chats_by_event(event)
        
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

        
app = WebApi("sqlite:///media/Pastebin/test.db")
app.run(host='localhost', port=8080)
