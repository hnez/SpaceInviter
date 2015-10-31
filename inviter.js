var event={}
var guest={}

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
}

function addGuest()
{
}

function editEvent()
{
}

function newEvent()
{
}
