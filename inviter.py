import bottle as bo
import sqlobject as so
import random
import string

class WebApi(bo.Bottle):
    def __init__(self):
        super(WebApi, self).__init__()

        self.events={}
        self.guests={}

        self.get('/api/event/<token>', callback=self.get_event)
        self.put('/api/event/<token>', callback=self.edit_event)

        self.get('/api/guest/<token>', callback=self.get_guest)
        self.put('/api/guest/<token>', callback=self.edit_guest)
        self.post('/api/guest', callback=self.new_guest)

        self.get('/', callback=self.get_static('index.html'))
        self.get('/event', callback=self.get_static('event.html'))
        self.get('/inviter.js', callback=self.get_static('inviter.js'))
        self.get('/style.css', callback=self.get_static('style.css'))

    def get_static(self, path):
        def file_cb ():
            return (bo.static_file(path, root='.'))

        return (file_cb)

    def gentoken (self):
        s=''.join([random.choice(string.lowercase) for i in range(8)])

        return (s)
        
    def get_event (self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        if (token not in self.events):
            bo.abort(404, 'token not found')

        event= self.events[token]
        
        ret = {}
        ret['token']=event['token']
        ret['name']=event['name']
        ret['guests']=[{'name' : 'Udo Baummann', 'parprop' : 99}]

        return (ret)
    
    def edit_event(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        if (token not in self.events):
            bo.abort(404, 'token not found')

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')
            
        event= self.events[token]
        req= bo.request.json

        if ('name' in req):
            event['name']=req['name']

        bo.response.status= 204

    def get_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        if (token not in self.guests):
            bo.abort(404, 'token not found')

        guest= self.guests[token]
            
        ret = {}
        ret['token']=guest['token']
        ret['name']=guest['name']
        ret['event']=guest['event']

        return (ret)

    def edit_guest(self, token):
        if (len(token) != 8):
            bo.abort(404, 'invalid token')
          
        if (token not in self.guests):
            bo.abort(404, 'token not found')

        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')
        
        guest= self.guests[token]
        req= bo.request.json
        
        if ('name' in req):
            guest['name']=req['name']

        bo.response.status= 204

    def new_guest(self):
        if (bo.request.json is None):
            bo.abort(400, 'request not json encoded')

        req= bo.request.json
        token= self.gentoken()
        guest= {}
        
        if ('event' in req):
            guest['event'] = req['event'][:8]
        else:
            etoken = self.gentoken()

            event={}

            event['name']= 'New Event'
            event['token']= etoken
            
            self.events[etoken]=event

            guest['event'] = etoken

        if('name' in req):
            guest['name'] = req['name']
        else:
            guest['name'] = 'John Doe'

        guest['token'] = token
            
        self.guests[token]= guest

        bo.redirect('/api/guest/' + token, 201)
        
app = WebApi()
app.run(host='localhost', port=8080)
