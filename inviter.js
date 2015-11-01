
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
  var url= '/api/guest/' + token + '/event';

  ivGetInfo(url, cb);
}

function ivGetMyInfo(token, cb)
{
  var url= '/api/guest/' + token;

  ivGetInfo(url, cb);
}

function ivSetEventInfo(token, info, cb)
{
  var url= '/api/guest/' + token + '/event';

  ivSetInfo(url, info, cb);
}

function ivSetMyInfo(token, info, cb)
{
  var url= '/api/guest/' + token;

  ivSetInfo(url, info, cb);
}

function ivCreateGuest(token, info, cb)
{
  var url= '/api/guest/' + token;

  ivCreate(url, info, cb);
}

function ivCreateEvent(info, cb)
{
  var url= '/api/guest';

  ivCreate(url, info, cb);
}
