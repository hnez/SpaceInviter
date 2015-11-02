
function ivGetInfo(url, cb)
{
  var xhr= new XMLHttpRequest();
  
  xhr.onreadystatechange= function() {
    if (xhr.readyState == 4) {
      
      if(xhr.status != 200) {
        console.warn('server request failed');
        return;
      }

      if (xhr.getResponseHeader('Content-Type') !=
          'application/json') {
        console.warn('response is not json encoded');
        return;
      }

      if(cb) {
        cb(JSON.parse(xhr.responseText));
      }
    }
  };
  
  xhr.open('GET', url, true);
  xhr.send();
}

function ivSetInfo(url, info, cb)
{
  var xhr= new XMLHttpRequest();
  
  xhr.onreadystatechange= function() {
    if (xhr.readyState == 4) {
      
      if(xhr.status != 204) {
        console.warn('server request failed');
        return;
      }

      if(cb) {
        cb();
      }
    }
  };
  
  xhr.open('PUT', url, true);
  xhr.setRequestHeader ('Content-Type', 'application/json');
  xhr.send(JSON.stringify(info));
}

function ivCreate(url, info, cb)
{
  var xhr= new XMLHttpRequest();
  
  xhr.onreadystatechange= function() {
    if (xhr.readyState == 4) {
      
      if(xhr.status != 201) {
        console.warn('server request failed');
        return;
      }

      var location = xhr.getResponseHeader('Location');
      
      if(cb) {
        cb(location);
      }
    }
  };
  
  xhr.open('POST', url, true);
  xhr.setRequestHeader ('Content-Type', 'application/json');
  xhr.send(JSON.stringify(info));
}

function ivGetEventInfo(token, cb)
{
  var url= '/api/token/' + token + '/event';

  ivGetInfo(url, cb);
}

function ivGetMyInfo(token, cb)
{
  var url= '/api/token/' + token;

  ivGetInfo(url, cb);
}

function ivSetEventInfo(token, info, cb)
{
  var url= '/api/token/' + token + '/event';

  ivSetInfo(url, info, cb);
}

function ivSetMyInfo(token, info, cb)
{
  var url= '/api/token/' + token;

  ivSetInfo(url, info, cb);
}

function ivCreateGuest(token, info, cb)
{
  var url= '/api/token/' + token;

  ivCreate(url, info, cb);
}

function ivCreateEvent(info, cb)
{
  var url= '/api/token';

  ivCreate(url, info, cb);
}

function ivGetMessages(token, cb)
{
  var url= '/api/token/' + token + '/chat';

  ivGetInfo(url, cb);
}

function ivCreateMsg(token, info, cb)
{
  var url= '/api/token/' + token + '/chat';

  ivCreate(url, info, cb);
}

function ivEditMsg(token, msgid, info, cb)
{
  var url= '/api/token/' + token + '/chat/' + msgid;

  ivSetInfo(url, info, cb);
}
