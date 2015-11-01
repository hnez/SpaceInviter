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

class WebApi(bo.Bottle):
    def __init__(self, dburi='sqlite:/:memory:'):
        super(WebApi, self).__init__()

        self.get('/api/guest/<token>', callback=self.api_get_guest)
        self.put('/api/guest/<token>', callback=self.api_edit_guest)
        self.post('/api/guest/<token>', callback=self.api_new_guest)
        self.post('/api/guest', callback=self.api_new_event)

        self.get('/api/guest/<token>/event', callback=self.api_get_event)
        self.put('/api/guest/<token>/event', callback=self.api_edit_event)
        
        self.get('/', callback=self.get_static('index.html'))
        self.get('/event', callback=self.get_static('event.html'))
        self.get('/inviter.js', callback=self.get_static('inviter.js'))
        self.get('/histogram.js', callback=self.get_static('histogram.js'))
        self.get('/frontend.js', callback=self.get_static('frontend.js'))
        self.get('/style.css', callback=self.get_static('style.css'))
        self.get('/spinner.gif', callback=self.get_static('spinner.gif'))

        self.db= so.connectionForURI(dburi)
        #Event.createTable(connection=self.db)
        #Guest.createTable(connection=self.db)
        
    def gentoken (self):
        s=''.join([random.choice(string.lowercase) for i in range(8)])

        return (s)

    def guest_by_token (self, token):
        guest= Guest.selectBy(self.db, token=token)
        
        return (guest.getOne(None))

    def guests_by_event (self, event):
        guests= [g for g in Guest.selectBy(self.db, event=event.id)]

        return (guests)

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

            if guest.admin:
                clean['token']= g['token']
            
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

        bo.redirect('/api/guest/' + guest.token, 201)
        
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
                   
        bo.redirect('/api/guest/' + newg.token, 201)
        
app = WebApi("sqlite:///media/Pastebin/test.db")
app.run(host='localhost', port=8080)
