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
    token = so.StringCol(length=8)

class Guest (DictSQLObject):
    name = so.UnicodeCol()
    admin = so.BoolCol(default=False)
    parprop = so.IntCol(default=-1)
    token = so.StringCol(length=8)
    event = so.StringCol(length=8)

class WebApi(bo.Bottle):
    def __init__(self, dburi='sqlite:/:memory:'):
        super(WebApi, self).__init__()

        self.get('/api/event/<token>', callback=self.get_event)
        self.put('/api/event/<token>', callback=self.edit_event)

        self.get('/api/guest/<token>', callback=self.get_guest)
        self.put('/api/guest/<token>', callback=self.edit_guest)
        self.post('/api/guest', callback=self.new_guest)

        self.get('/', callback=self.get_static('index.html'))
        self.get('/event', callback=self.get_static('event.html'))
        self.get('/inviter.js', callback=self.get_static('inviter.js'))
        self.get('/style.css', callback=self.get_static('style.css'))

        self.db= so.connectionForURI(dburi)
        #Event.createTable(connection=self.db)
        #Guest.createTable(connection=self.db)
        
    def gentoken (self):
        s=''.join([random.choice(string.lowercase) for i in range(8)])

        return (s)

    def event_by_token (self, etoken):
        event= [g for g in  Event.selectBy(self.db, token=etoken)]

        if (len(event) != 1):
            return (None)
        else:
            return (event[0])

    def guest_by_token (self, gtoken, adminonly=False):
        guest=None

        if adminonly:
            guest= [g for g in Guest.selectBy(self.db, token=gtoken, admin=True)]
        else:
            guest= [g for g in Guest.selectBy(self.db, token=gtoken)]
        
        if (len(guest) != 1):
            return (None)
        else:
            return (guest[0])
        
    def guests_by_event (self, etoken):
        guests= [g for g in Guest.selectBy(self.db, event=etoken)]

        return (guests)

    def get_static(self, path):
        def file_cb ():
            return (bo.static_file(path, root='.'))

        return (file_cb)

    def get_event (self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')

        ret={}
        event = self.event_by_token(token)
        guests = self.guests_by_event(token)
        
        if (event is None):
            bo.abort(404, 'token not found')

        for k in ['token', 'name', 'description']:
            ret[k]= event[k]

        ret['guests']=[]
        for g in guests:
            clean={}
            for k in ['name', 'parprop', 'admin']:
                clean[k]= g[k]
            
            ret['guests'].append(clean)

        return (ret)
    
    def edit_event(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        event = self.event_by_token(token)
        
        if (event is None):
            bo.abort(404, 'token not found')

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')
            
        req= bo.request.json

        if (('auth' not in req) or (len(req['auth']) != 8)):
            bo.arbort(403, 'auth field required')

        admin = self.guest_by_token(req['auth'], True)

        if (admin is None):
            bo.arbort(403, 'authentification failed')

        for k in ['name', 'description']:
            if (k in req):
                event[k]=req[k]

        bo.response.status= 204

    def get_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        guest = self.guest_by_token(token)
        
        if (guest is None):
            bo.abort(404, 'token not found')

        ret = {}
        for k in ['token', 'name', 'parprop', 'admin', 'event']:
            ret[k]= guest[k]

        return (ret)

    def edit_guest(self, token):
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

    def new_guest(self):
        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json
        token= self.gentoken()

        opts= {}
        
        if ('event' in req):
            opts['event'] = req['event'][:8]
            opts['admin'] = False
        else:
            etoken = self.gentoken()

            event=Event(
                connection= self.db,
                name='New Event',
                description='Enter a description',
                token=etoken)

            opts['event'] = etoken
            opts['admin'] = True

        if('name' in req):
            opts['name'] = req['name']
        else:
            opts['name'] = 'John Doe'

        opts['token'] = token
        opts['parprop'] = -1

        guest= Guest(connection= self.db, **opts)

        bo.redirect('/api/guest/' + token, 201)
        
app = WebApi("sqlite:///media/Pastebin/test.db")
app.run(host='localhost', port=8080)
