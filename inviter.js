/*
  inviter.js, low level functions to communicate
  with the SpaceInviter server.

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
*/

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
