function convDist(props)
{
  var dist=[1];

  for (i=0;i<props.length;i++) {
    var cur=[];

    for(j=0;j<=dist.length;j++) {
      cur[j]= (j>=1 ? dist[j-1] : 0)*props[i]
        +(j<dist.length ? dist[j] : 0)*(1-props[i]);
    }

    dist=cur;
  }

  return (dist);
}

function genDistSVG (props)
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

  var dist= convDist(props);
  var num= props.length;
  var maxp=0;

  if (num != 0) {
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
  }

  return (svg)
}
