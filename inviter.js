var event={}
var guest={}

function binomialDist(num, prop)
{
  function binomialCoef (n,k) {
    its++;
    if (k==0 || n==k) return 1;

    return (binomialCoef(n-1,k-1) + binomialCoef(n-1,k));
  }

  var res=[];

  for (var i=0; i<=num; i++) {
    var tmp=1;
    tmp*= binomialCoef(num, i);
    tmp*= Math.pow(prop, i);
    tmp*= Math.pow(1-prop, num-i);

    res[i]=tmp;
  }

  return (res)
}

function genDistSVG (num, prop)
{
  var ns= 'http://www.w3.org/2000/svg'

  function line (x1, y1, x2, y2, color) {
    var line= document.createElementNS(ns, 'line');

    line.setAttribute('x1',  x1 + '%');
    line.setAttribute('x2',  x2 + '%');
    
    line.setAttribute('y1',  y1 + '%');
    line.setAttribute('y2',  y2 + '%');

    line.setAttribute('stroke', color);
    line.setAttribute('stroke-width', '1');

    return (line);
  }

  function text(xp, yp, txt) {
    var text= document.createElementNS(ns, 'text');

    text.setAttribute('x', xp + '%');
    text.setAttribute('y', yp + '%');
    text.setAttribute('fill', 'grey');

    text.setAttribute('alignment-baseline', 'middle');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-size', '0.7em');
    
    text.appendChild(document.createTextNode(txt));
    
    return (text);
  }
  
  var svg= document.createElementNS(ns, 'svg');
  svg.setAttribute('id', 'histogram');
  svg.appendChild(line(2, 10,  2, 90, 'grey'));
  svg.appendChild(line(2, 90, 98, 90, 'grey'));

  var dist= binomialDist(num, prop);
  var maxp=0;

  for (var i=0; i<=num; i++) {
    if (dist[i]>maxp) maxp=dist[i];
  }
  
  for (var i=0; i<num; i++) {
    var x1=(i/num)*96+2;
    var x2=((i+1)/num)*96+2;

    var y1=90 - dist[i]/maxp * 80;
    var y2=90 - dist[i+1]/maxp * 80;

    var lne= line(x1, y1, x2, y2, 'blue');

    svg.appendChild(lne);
  }

  for (var i=0; i<=num; i++) {
    var xp=(i/num)*96+2;

    var txt= text(xp, 97.5, i);

    svg.appendChild(txt);
  }


  return (svg)
}

function loadEvent ()
{
  var gtoken= window.location.hash.substring(1, 9);
  var gurl= "/api/guest/" + gtoken;
  
  var greq= new XMLHttpRequest();
  var ereq= new XMLHttpRequest();


  
  function onEventDLStep ()
  {
    if (ereq.readyState != 4) return;    
    if (ereq.status != 200) return;
    
    event = JSON.parse(ereq.responseText);

    var h1= document.getElementById("headline")
    var table= document.getElementById("guesttab")
    var guests= event["guests"]
    
    h1.textContent= event["name"]

    for (i = 0; i < guests.length; i++) {
      console.log(i)
      
      var tr= document.createElement('tr');

      var tname=document.createElement('td');
      var tprop=document.createElement('td');
      var tlink=document.createElement('td');
      var tdel= document.createElement('td');

      tlink.setAttribute('class', 'admin');
      tdel.setAttribute('class', 'admin');
      
      tr.appendChild(tname);
      tr.appendChild(tprop);
      tr.appendChild(tlink);
      tr.appendChild(tdel);

      tname.appendChild(document.createTextNode(guests[i]["name"]));
      tprop.appendChild(document.createTextNode(guests[i]["parprop"]));
      tlink.appendChild(document.createTextNode("link"));
      tdel.appendChild(document.createTextNode("del"));

      table.appendChild(tr);
    }
  }
  
  function onGuestDLStep ()
  {
    if (greq.readyState != 4) return;    
    if (greq.status != 200) return;
    
    guest = JSON.parse(greq.responseText);
    var etoken= guest["event"]


    var eurl= "/api/event/" + etoken;
    
    ereq.onreadystatechange = onEventDLStep;

    ereq.open("GET", eurl, true);
    ereq.send();
  }
  
  greq.onreadystatechange = onGuestDLStep;

  greq.open("GET", gurl, true);
  greq.send();
}

function editGuest()
{
    var command= {};
    var namefield= document.getElementById("guestnamein");
    var propfield= document.getElementById("guestpropin");
    var gtoken= guest["token"]
    
    command["name"]= namefield.value;
    command["parprop"]= parseInt(propfield.value);

    var req= new XMLHttpRequest();
    req.onreadystatechange = function () {
        // TODO: everything
    }

    req.open("PUT", "/api/guest/" + gtoken, true);
    req.setRequestHeader ('Content-Type', 'application/json');
    req.send(JSON.stringify(command))
}

function addGuest()
{
    var command= {};
    command["event"]= event["token"]
    command["auth"]= guest["token"]
    
    var req= new XMLHttpRequest();
    req.onreadystatechange = function () {
        // TODO: everything
    }

    req.open("POST", "/api/guest", true);
    req.setRequestHeader ('Content-Type', 'application/json');
    req.send(JSON.stringify(command))
}

function editEvent()
{
    var command= {};
    command["event"]= event["token"]
    command["auth"]= guest["token"]

    var etoken= event["token"]
    var namefield= document.getElementById("eventnamein");
    
    command["name"]= namefield.value
    
    var req= new XMLHttpRequest();
    req.onreadystatechange = function () {
        // TODO: everything
    }

    req.open("PUT", "/api/event/" + etoken, true);
    req.setRequestHeader ('Content-Type', 'application/json');
    req.send(JSON.stringify(command))
}

function newEvent()
{
    var command= {};
    
    var req= new XMLHttpRequest();
    req.onreadystatechange = function () {
        // TODO: everything
    }

    req.open("POST", "/api/guest", true);
    req.setRequestHeader ('Content-Type', 'application/json');
    req.send(JSON.stringify(command))
}
