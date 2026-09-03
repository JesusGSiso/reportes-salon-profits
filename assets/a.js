const D=JSON.parse(document.getElementById('d').textContent);
const T='#2F6F68',C='#C0522F',A='#C9BFA9',G='#8FA8A4';
let H='';
document.title='Reporte de Gestión — '+D.nombre;
H+='<header><div class="w"><div class="eb">Reporte de gestión</div><h1>'+D.nombre+'</h1><div class="sub">'+D.rango+' · Salon Profits</div></div></header><div class="w">';

/* ---- estados sin reporte completo ---- */
if(D.estado==='no_medible'||D.estado==='sin_leads'){
  H+='<div class="msg">'+(D.mensaje||(D.estado==='sin_leads'?'Esta semana no entraron leads de anuncio, así que no hay gestión que medir. En cuanto vuelva a entrar pauta, aquí aparece tu reporte.':'Esta semana no pudimos medir tu gestión desde el sistema. Tu equipo de Salon Profits te contacta para revisarlo.'))+'</div>';
  H+=trend();H+='<footer>'+(D.pie||'')+'</footer></div>';document.body.innerHTML=H;
}else{

/* ---- tasa de agendamiento (número principal) ---- */
const t=D.tasa;
H+='<div class="hero"><div><div class="n">'+t.pct+'%</div></div><div><div class="lab">Tasa de agendamiento</div><div class="det">'+t.num+' de '+t.den+' leads de anuncio agendaron</div><div class="ant">'+(t.pctAnt==null?'primera semana medida':'la semana pasada: '+t.pctAnt+'%')+'</div></div>';
const segs=[['El bot sola',t.botSola,T],['Tú',t.ella,C],['Esfuerzo de los dos',t.mutuo,G]];if(t.leadSola>0)segs.push(['Ella sola, por el enlace',t.leadSola,A]);
H+='<div class="split">'+segs.map(s=>'<i style="width:'+s[1]+'%;background:'+s[2]+'"></i>').join('')+'</div>';
H+='<div class="slg">'+segs.map(s=>'<span><i style="background:'+s[2]+'"></i>'+s[0]+' <b>'+s[1]+'%</b></span>').join('')+'</div></div>';

H+='<h2>Lo más importante de esta semana</h2>';D.intro.forEach(p=>H+='<p>'+p+'</p>');

/* ---- seis números ---- */
H+='<h2>Tu semana en números</h2><div class="kpis">';
D.kpis.forEach(k=>{const dif=k.v-k.ant,cls=dif>0?'up':(dif<0?'dn2':''),fl=dif>0?'▲':(dif<0?'▼':'=');H+='<div class="kpi"><div class="k">'+k.k+'</div><div class="v">'+k.t+'</div><div class="d"><i class="'+cls+'">'+fl+'</i> antes: '+k.at+'</div></div>'});
H+='</div>';
const mx=Math.max(...D.kpis.map(k=>Math.max(k.v,k.ant)))||1;
H+='<div class="card"><div class="chart">';
D.kpis.forEach(k=>{H+='<div class="grp"><div class="bx b1" style="height:'+(k.ant/mx*100)+'%"><span>'+k.ant+'</span></div><div class="bx b2" style="height:'+(k.v/mx*100)+'%"><span>'+k.v+'</span></div></div>'});
H+='</div><div class="xlab">'+D.kpis.map(k=>'<div>'+k.s+'</div>').join('')+'</div><div class="leg"><span><i style="background:'+A+'"></i>'+D.rangoAnt+'</span><span><i style="background:'+T+'"></i>'+D.rangoCorto+'</span></div></div>';

H+=trend();

/* ---- tres barras ---- */
H+='<h2>Dónde estás parada</h2><p>Estas son tus tres acciones. La línea punteada es la meta que nos pusimos, no una ley: sirve para ver de un vistazo qué tan lejos quedó cada una.</p><div class="card">';
D.barras.forEach(b=>{if(!b.den){H+='<div class="bar"><div class="bhead"><span>'+b.label+'</span></div><div style="font-size:13.5px;color:#6B6B63">'+(b.vacio||'Esta semana no aplica.')+'</div></div>';return}
const pc=Math.round(b.num/b.den*100),col=pc>=b.meta?'#3F7D4A':(pc>=b.meta/2?'#B0741C':C);
H+='<div class="bar"><div class="bhead"><span>'+b.label+'</span><span class="bval">'+b.num+' de '+b.den+' · '+pc+'%</span></div><div class="btrack"><div class="bfill" style="width:'+Math.min(pc,100)+'%;background:'+col+'"></div><div class="bmeta" style="left:'+b.meta+'%"><span>meta '+b.meta+'%</span></div></div></div>'});
H+='</div><p class="bnote">La de nota de voz es nueva y todavía la estamos calibrando. Las otras dos ya sabemos que mueven el resultado.</p>';

/* ---- quién agendó ---- */
H+='<h2>Quién agendó las citas</h2>';
if(D.origen&&D.origen.length){const tot=D.origen.reduce((a,b)=>a+b.v,0),R=54,CC=2*Math.PI*R;let off=0,sg='';
D.origen.forEach(o=>{const L=o.v/tot*CC;sg+='<circle r="'+R+'" cx="70" cy="70" fill="none" stroke="'+o.c+'" stroke-width="22" stroke-dasharray="'+L+' '+(CC-L)+'" stroke-dashoffset="'+(-off)+'" transform="rotate(-90 70 70)"/>';off+=L});
H+='<div class="card dwrap"><svg class="donut" viewBox="0 0 140 140">'+sg+'<text class="dn" x="70" y="72" text-anchor="middle">'+tot+'</text><text class="dl" x="70" y="86" text-anchor="middle">CITAS CREADAS</text></svg><div class="dleg">'+D.origen.map(o=>'<div><i style="background:'+o.c+'"></i>'+o.k+' — '+o.v+'</div>').join('')+'</div></div>'}
H+='<p>'+D.origenNota+'</p>';

/* ---- método ---- */
H+='<h2>Lo que enseñamos vs. lo que estás haciendo</h2>';
D.metodo.forEach(m=>{H+='<div class="row"><div class="cell"><div class="lb">En la clase te enseñamos</div><p>'+m.c+'</p></div><div class="cell"><div class="lb">Lo que hiciste esta semana</div><p>'+m.h+'</p></div><div class="cell"><div class="lb">Lo que pasó</div><p>'+m.p+'</p></div></div>'});
H+='<p style="margin-top:14px">'+D.cierre+'</p>';
H+='<h2>Lo que sí funcionó</h2><div class="win">'+D.funciono+'</div>';
H+='<h2>Qué hacer esta semana</h2><div class="act">';
D.acciones.forEach((a,i)=>{H+='<div class="a"><b>'+(i+1)+'. '+a.t+'</b>'+a.d+(a.g?'<div class="guion">'+a.g+'</div>':'')+'</div>'});
H+='</div><footer>'+D.pie+'</footer></div>';
document.body.innerHTML=H;
}

/* ---- tendencia: tasa de agendamiento, últimas semanas ---- */
function trend(){const h=(D.historico||[]).filter(x=>x&&x.tasa!=null);
  let s='<h2>Tendencia</h2>';
  if(h.length<2){return s+'<div class="msg">A partir de la próxima semana aquí verás cómo va tu tasa de agendamiento semana a semana.</div>'}
  const W=Math.max(300,Math.min(680,document.documentElement.clientWidth-72)),Hh=200,L=36,R=52,Tp=26,B=40,n=h.length,mxv=Math.max(30,...h.map(x=>x.tasa));
  const X=i=>L+(W-L-R)*i/(n-1),Y=v=>Tp+(Hh-Tp-B)*(1-v/mxv);
  let g='';[0,.5,1].forEach(f=>{const v=Math.round(mxv*f),y=Y(v);g+='<line class="gl" x1="'+L+'" x2="'+(W-R)+'" y1="'+y+'" y2="'+y+'"/><text x="'+(L-6)+'" y="'+(y+4)+'" text-anchor="end">'+v+'%</text>'});
  const pts=h.map((x,i)=>X(i)+','+Y(x.tasa)).join(' ');
  const area='M'+X(0)+','+Y(0)+' L'+pts.replace(/ /g,' L')+' L'+X(n-1)+','+Y(0)+' Z';
  let lab='';h.forEach((x,i)=>{if(i===0||i===n-1||(n>5&&i%2===0))lab+='<text x="'+X(i)+'" y="'+(Hh-14)+'" text-anchor="middle">'+x.etq+'</text>'});
  let dots='';h.forEach((x,i)=>{dots+='<circle class="pt'+(i===n-1?' last':'')+'" cx="'+X(i)+'" cy="'+Y(x.tasa)+'" r="4"/>'});
  const last=h[n-1];
  return s+'<div class="card"><svg class="trend" viewBox="0 0 '+W+' '+Hh+'">'+g+'<path class="ar" d="'+area+'"/><polyline class="ln" points="'+pts+'"/>'+dots+'<text class="big" x="'+(X(n-1)+10)+'" y="'+(Y(last.tasa)+5)+'">'+last.tasa+'%</text>'+lab+'</svg><div class="leg" style="margin-top:6px"><span>% de leads de anuncio que agendaron, últimas '+n+' semanas</span></div></div>';
}
