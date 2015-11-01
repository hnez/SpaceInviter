function updateHistogram (guests)
{
  var props=[];
  var i=0;
  for (var g in guests) {
    var parprop= guests[g]['parprop'];

    if (parprop > 0) {
      props[i]=parprop / 100;
      i++;
    }
  }
  
  var div= document.getElementById('dhistogram');
  var svg= genDistSVG(props);
  
  div.replaceChild(svg, div.firstElementChild);
}

function updateGuestList(guests)
{
  var table= document.createElement('table');
  table.setAttribute('id', 'guesttab');
  
  for (var g in guests) {
    var tr= document.createElement('tr');
    
    var tname=document.createElement('td');
    var tprop=document.createElement('td');
    var tlink=document.createElement('td');
    var tdel= document.createElement('td');

    var alink=document.createElement('a')

    tname.textContent= guests[g].name;
    tprop.textContent=
      (guests[g].parprop > 0) ? guests[g].parprop + '%' : '?';

    if(guests[g].token) {
      var gtoken= guests[g].token;
      
      alink.textContent='link'
      alink.href='/event#' + gtoken
      tlink.appendChild(alink);
      
      tdel.textContent= 'remove';
      tdel.onclick=
        'onDeleteGuestButton(' + gtoken + ')';
    }
    else {
      tlink.style.display='none';
      tdel.style.display='none'
    }
      
    tr.appendChild(tname);
    tr.appendChild(tprop);
    tr.appendChild(tlink);
    tr.appendChild(tdel);

    table.appendChild(tr);
  }

  var oldtable= document.getElementById('guesttab');

  oldtable.parentElement.replaceChild(table, oldtable);
}

function reloadMyInfo()
{
  function onReceiveMyInfo(guest) {
    console.log(guest);

    var namein= document.getElementById('guestnamein');
    var propin= document.getElementById('guestpropin');
    
    namein.value= guest.name;
    propin.value= guest.parprop;

    var domObjs= document.getElementsByClassName('admin');
    for (var k=0; k<domObjs.length; k++) {
      domObjs[k].style.display= guest.admin ? '' : 'none';
    }
  }

  var token= window.location.hash.substring(1);

  ivGetMyInfo(token, onReceiveMyInfo);
}

function reloadEventInfo()
{
  function onReceiveEventInfo(event) {
    console.log(event)
    
    var guests= event.guests;

    guests.sort(function (a,b) {
      return (b.parprop - a.parprop);
    });
    
    updateHistogram(guests);
    updateGuestList(guests);

    var headline= document.getElementById('headline');
    var pagetitle= document.getElementById('pagetitle');
    
    headline.textContent= event.name;
    pagetitle.textContent= event.name;

    var namein= document.getElementById('eventnamein');
    var descin= document.getElementById('eventdescin');
    
    namein.value= event.name;
    descin.value= event.description;
    
    var desclines= event.description.split('\n');

    var div= document.createElement('div');
    div.setAttribute('id', 'ddescription');
    div.setAttribute('class', 'framed');

    for (lne in desclines) {
      var p= document.createElement('p');

      p.textContent= desclines[lne];
      
      div.appendChild(p);
    }

    var olddiv= document.getElementById('ddescription');
    olddiv.parentElement.replaceChild(div, olddiv);
  }

  var token= window.location.hash.substring(1);

  ivGetEventInfo(token, onReceiveEventInfo);
}

function onPageLoad()
{
  reloadMyInfo();
  reloadEventInfo();
}

function onEditGuestButton()
{ 
  function onGuestEdited() {
    reloadEventInfo();
  }
 
  var token= window.location.hash.substring(1);
  var namein= document.getElementById('guestnamein');
  var propin= document.getElementById('guestpropin');
 
  var info={};
  
  info['name']= namein.value;
  info['parprop']= parseInt(propin.value);
  
  ivSetMyInfo(token, info, onGuestEdited);
}

function onAddGuestButton()
{
  function onGuestAdded(loc) {
    reloadEventInfo();
  }
  
  var token= window.location.hash.substring(1);
  var namein= document.getElementById('guestnamein');
  var propin= document.getElementById('guestpropin');
  
  var info={};
  
  info['name']= namein.value;
  info['parprop']= parseInt(propin.value);
  
  ivCreateGuest(token, info, onGuestAdded);
}

function onEditEventButton()
{
  function onEventEdited() {
    reloadEventInfo();
  }
 
  var token= window.location.hash.substring(1);
  var namein= document.getElementById('eventnamein');
  var descin= document.getElementById('eventdescin');
  
  var info={};
  
  info['name']= namein.value;
  info['description']= descin.value;
  
  ivSetEventInfo(token, info, onEventEdited);  
}

function onAddEventButton()
{
  function onEventAdded(loc) {
    var locs= loc.split('/')

    var token= locs[locs.length-1];

    window.location= '/event#' + token;
  }
  
  var info={};

  info['admin']= true;

  ivCreateEvent(info, onEventAdded);
}