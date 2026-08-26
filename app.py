# app.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Dragon Realm",
    page_icon="🐉",
    layout="wide"
)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin: 0; padding: 0;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
</style>
""", unsafe_allow_html=True)

# The full 3D game HTML
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#000;overflow:hidden;font-family:sans-serif;color:#fff}
  canvas{display:block;width:100vw;height:100dvh}
  #hud{position:absolute;top:10px;left:10px;font-size:14px;text-shadow:0 2px 4px #000;pointer-events:none;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:8px;z-index:10}
  #controls{position:absolute;bottom:20px;left:0;right:0;display:flex;justify-content:center;gap:14px;pointer-events:auto;z-index:10}
  button{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);color:#fff;font-size:18px;padding:12px 24px;border-radius:28px;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);min-width:50px;touch-action:manipulation}
  button:active{background:rgba(255,255,255,0.35);transform:scale(0.95)}
  #compass{position:absolute;bottom:90px;right:20px;width:60px;height:60px;border-radius:50%;background:rgba(0,0,0,0.5);border:2px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:10;font-size:24px}
  #minimap{position:absolute;top:10px;right:10px;width:80px;height:80px;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.15);border-radius:4px;pointer-events:none;z-index:10}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hud">🐉 Dragon Realm<br><span id="info">Loading...</span></div>
<div id="controls">
  <button id="bW">▲</button>
  <button id="bS">▼</button>
  <button id="bA">◄</button>
  <button id="bD">►</button>
  <button id="bF">🐉 Call</button>
</div>
<div id="compass">🧭</div>
<canvas id="minimap" width="80" height="80"></canvas>

<script>
const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');
const mm=document.getElementById('minimap'), mx=mm.getContext('2d');
const info=document.getElementById('info');

let W,H;
let player={x:0,y:0,z:0,angle:0};
let world=[];
let dragon={x:30,y:0,z:20,angle:0,wingPhase:0};
let particles=[];
let frame=0;

function resize(){
  W=window.innerWidth; H=window.innerHeight;
  canvas.width=W; canvas.height=H;
}
window.addEventListener('resize',resize);resize();

function project(x,y,z){
  const fov=250;
  const dx=x-player.x;
  const dy=y-player.y;
  const dz=z-player.z;
  const cosA=Math.cos(player.angle), sinA=Math.sin(player.angle);
 ​const rx=dx*cosA-dz*sinA;
  const rz=dx*sinA+dz*cosA;
  if(rz<1) return null;
  const sx=W/2+(rx*fov)/rz;
  const sy=H/2-(dy*fov)/rz;
  return{x:sx,y:sy,scale:fov/rz};
}

function generateWorld(){
  world=[];
  // Ground
  for(let x=-25;x<=25;x+=2){
    for(let z=-25;z<=25;z+=2){
      const h=Math.sin(x*0.3)*Math.cos(z*0.4)*2+
              Math.sin(x*0.7+z*0.5)*1.5+
              Math.sin(x*0.1+z*0.15)*4;
      const dist=Math.sqrt(x*x+z*z);
      const mountain=Math.max(0,10-dist*0.25);
      world.push({x,y:h+mountain,z,color:'#3a7a32'});
    }
  }
  // Trees
  for(let i=0;i<40;i++){
    const angle=Math.random()*Math.PI*2;
    const dist=5+Math.random()*18;
    const x=Math.cos(angle)*dist;
    const z=Math.sin(angle)*dist;
    const h=Math.sin(x*0.3)*Math.cos(z*0.4)*2+
            Math.sin(x*0.7+z*0.5)*1.5+
            Math.sin(x*0.1+z*0.15)*4+
            Math.max(0,10-Math.sqrt(x*x+z*z)*0.25);
    world.push({x,y:h,z,type:'tree',size:1+Math.random()*2,color:'#2d5a27'});
    world.push({x,y:h+2.5,z,type:'treeTop',size:1.5+Math.random()*1.5,color:'#1a3a1a'});
  }
  // Castle ruins
  for(let i=0;i<10;i++){
    const angle=Math.PI*2*i/10;
    const r=14;
    const x=Math.cos(angle)*r;
    const z=Math.sin(angle)*r;
    const h=Math.sin(x*0.3)*Math.cos(z*0.4)*2+
            Math.sin(x*0.7+z*0.5)*1.5+
            Math.sin(x*0.1+z*0.15)*4+
            Math.max(0,10-Math.sqrt(x*x+z*z)*0.25);
    world.push({x,y:h,z,type:'pillar',height:3+Math.sin(i*3)*2,color:'#8a8a7a'});
  }
  // Dragon lair
  world.push({x:0,y:0,z:0,type:'lair',color:'#ff6644',glow:true});
}

function drawDragon(d){
  ctx.shadowColor='#ff6644';
  ctx.shadowBlur=20;
  
  // Body segments
  const segs=14;
  for(let i=0;i<segs;i++){
    const t=i/segs;
    const bx=d.x+Math.sin(t*Math.PI*4+d.angle)*2.5;
    const by=d.y+Math.sin(t*Math.PI*3+d.wingPhase)*2;
    const bz=d.z+Math.cos(t*Math.PI*4+d.angle)*2.5-t*5;
    const p=project(bx,by,bz);
    if(p){
      if(i===0){
        // Head
        ctx.fillStyle='#ff8844';
        ctx.shadowBlur=25;
        ctx.beginPath();
        ctx.arc(p.x,p.y,5,0,Math.PI*2);
        ctx.fill();
        // Eyes
        ctx.fillStyle='#ff0000';
        ctx.shadowBlur=30;
        ctx.beginPath();
        ctx.arc(p.x-3,p.y-2,2,0,Math.PI*2);
        ctx.arc(p.x+3,p.y-2,2,0,Math.PI*2);
        ctx.fill();
        // Horns
        ctx.strokeStyle='#ffaa44';
        ctx.lineWidth=2;
        ctx.beginPath();
        ctx.moveTo(p.x-3,p.y-4);
        ctx.lineTo(p.x-5,p.y-10);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(p.x+3,p.y-4);
        ctx.lineTo(p.x+5,p.y-10);
        ctx.stroke();
      }
      if(i>0){
        const pt=project(
          d.x+Math.sin((t-1/segs)*Math.PI*4+d.angle)*2.5,
          d.y+Math.sin((t-1/segs)*Math.PI*3+d.wingPhase)*2,
          d.z+Math.cos((t-1/segs)*Math.PI*4+d.angle)*2.5-(t-1/segs)*5
        );
        if(pt){
          ctx.strokeStyle='#ff6644';
          ctx.lineWidth=3;
          ctx.beginPath();
          ctx.moveTo(pt.x,pt.y);
          ctx.lineTo(p.x,p.y);
          ctx.stroke();
        }
      }
    }
  }
  
  // Wings
  ctx.shadowBlur=25;
  for(let side=-1;side<=1;side+=2){
    const wx=d.x+side*4;
    const wy=d.y+Math.sin(d.wingPhase)*4;
    const wz=d.z-1;
    const p1=project(wx,wy,wz);
    const p2=project(wx+side*5,wy-3+Math.sin(d.wingPhase)*3,wz-3);
    const p3=project(wx+side*3,wy+2+Math.sin(d.wingPhase+1)*3,wz-4);
    if(p1&&p2&&p3){
      ctx.strokeStyle='rgba(255,100,50,0.5)';
      ctx.lineWidth=1.5;
      ctx.fillStyle='rgba(255,100,50,0.08)';
      ctx.beginPath();
      ctx.moveTo(p1.x,p1.y);
      ctx.lineTo(p2.x,p2.y);
      ctx.lineTo(p3.x,p3.y);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }
  
  // Fire breath
  if(Math.sin(frame*0.08)>0.85){
    const fp=project(d.x+Math.cos(d.angle)*6,d.y-1.5,d.z+Math.sin(d.angle)*6-5);
    if(fp){
      ctx.shadowBlur=40;
      for(let i=0;i<5;i++){
        ctx.fillStyle=`rgba(255,${150+Math.random()*100},0,${0.2+Math.random()*0.3})`;
        ctx.beginPath();
        ctx.arc(fp.x+Math.random()*10-5,fp.y+Math.random()*10-5,6+Math.random()*8,0,Math.PI*2);
        ctx.fill();
      }
    }
  }
  
  ctx.shadowBlur=0;
}

function render(){
  ctx.fillStyle='#0a0a1a';
  ctx.fillRect(0,0,W,H);
  
  // Stars
  for(let i=0;i<100;i++){
    const sx=(i*137.5)%W;
    const sy=(i*97.3)%(H*0.6);
    ctx.fillStyle='#fff';
    ctx.globalAlpha=0.2+Math.sin(i+frame*0.03)*0.2;
    ctx.beginPath();
    ctx.arc(sx,sy,0.5+Math.sin(i*3+frame)*0.3,0,Math.PI*2);
    ctx.fill();
  }
  ctx.globalAlpha=1;
  
  // Sort by distance
  const sorted=[...world].sort((a,b)=>{
    const da=(a.x-player.x)**2+(a.z-player.z)**2;
    const db=(b.x-player.x)**2+(b.z-player.z)**2;
    return db-da;
  });
  
  // Draw world
  for(const w of sorted){
    const p=project(w.x,w.y,w.z);
    if(!p||p.scale<0.01) continue;
    
    if(w.type==='tree'){
      ctx.shadowBlur=8;
      ctx.shadowColor='#2d5a27';
      ctx.fillStyle=w.color;
      ctx.beginPath();
      ctx.arc(p.x,p.y,w.size*p.scale*0.3,0,Math.PI*2);
      ctx.fill();
    }else if(w.type==='treeTop'){
      ctx.shadowBlur=0;
      ctx.fillStyle=w.color;
      ctx.beginPath();
      ctx.arc(p.x,p.y-4*p.scale*0.3,w.size*p.scale*0.4,0,Math.PI*2);
      ctx.fill();
    }else if(w.type==='pillar'){
      ctx.shadowBlur=0;
      ctx.strokeStyle=w.color;
      ctx.lineWidth=2;
      const h=w.height*p.scale*0.3;
      ctx.beginPath();
      ctx.moveTo(p.x-4,p.y);
      ctx.lineTo(p.x-4,p.y-h);
      ctx.lineTo(p.x+4,p.y-h);
      ctx.lineTo(p.x+4,p.y);
      ctx.stroke();
      // Top
      ctx.fillStyle=w.color;
      ctx.beginPath();
      ctx.arc(p.x,p.y-h,5,0,Math.PI*2);
      ctx.fill();
    }else if(w.type==='lair'){
      ctx.shadowBlur=30;
      ctx.shadowColor='#ff6644';
      ctx.fillStyle='rgba(255,100,50,0.12)';
      ctx.beginPath();
      ctx.arc(p.x,p.y,25*p.scale*0.3,0,Math.PI*2);
      ctx.fill();
      ctx.fillStyle='#ff8844';
      ctx.shadowBlur=20;
      ctx.beginPath();
      ctx.arc(p.x,p.y,6*p.scale*0.3,0,Math.PI*2);
      ctx.fill();
    }else{
      // Ground
      const dist=Math.sqrt(w.x*w.x+w.z*w.z);
      const brightness=Math.max(0.15,1-dist/35);
      ctx.globalAlpha=brightness;
      ctx.fillStyle=w.color;
      ctx.shadowBlur=0;
      const s=Math.max(1,p.scale*0.4);
      ctx.fillRect(p.x-s/2,p.y-s/2,s,s);
      ctx.globalAlpha=1;
    }
  }
  
  // Dragon
  drawDragon(dragon);
  
 ​// Particles
  for(const p of particles){
    const pp=project(p.x,p.y,p.z);
    if(pp){
      ctx.shadowBlur=15;
      ctx.shadowColor=p.color;
      ctx.fillStyle=p.color;
      ctx.globalAlpha=p.life/30;
      ctx.beginPath();
      ctx.arc(pp.x,pp.y,3*pp.scale*0.2,0,Math.PI*2);
      ctx.fill();
      ctx.globalAlpha=1;
    }
  }
  
  // Minimap
  mx.fillStyle='#0a0a12';
  mx.fillRect(0,0,80,80);
  for(const w of world){
    if(!w.type){
      const mx=40+w.x*1.5;
      const my=40+w.z*1.5;
      if(mx>=0&&mx<=80&&my>=0&&my<=80){
        const dist=Math.sqrt(w.x*w.x+w.z*w.z);
        const b=Math.max(0.2,1-dist/35);
        mx.fillStyle=`rgba(58,122,50,${b})`;
        mx.fillRect(mx,my,1,1);
      }
    }
  }
  // Dragon on minimap
  mx.fillStyle='#ff6644';
  mx.beginPath();
  mx.arc(40+dragon.x*1.5,40+dragon.z*1.5,2,0,Math.PI*2);
  mx.fill();
  // Player on minimap
  mx.fillStyle='#fff';
  mx.beginPath();
  mx.arc(40+player.x*1.5,40+player.z*1.5,1.5,0,Math.PI*2);
  mx.fill();
  
  // HUD
  const dist=Math.sqrt((dragon.x-player.x)**2+(dragon.z-player.z)**2);
  info.textContent=`📍 ${Math.round(player.x)},${Math.round(player.z)} | 🐉 ${Math.round(dist)}m`;
  
  requestAnimationFrame(render);
}

function update(){
  frame++;
  
  // Dragon AI
  const dx=player.x-dragon.x;
  const dz=player.z-dragon.z;
  const dist=Math.sqrt(dx*dx+dz*dz);
  
  if(dist<12){
    dragon.angle+=0.03;
    dragon.x=player.x+Math.cos(dragon.angle)*8;
    dragon.z=player.z+Math.sin(dragon.angle)*8;
    dragon.y=4+Math.sin(frame*0.04)*2;
    dragon.wingPhase=frame*0.1;
    if(dist<6&&Math.random()<0.05){
      particles.push({x:dragon.x+Math.cos(dragon.angle)*5,y:dragon.y-1.5,z:dragon.z+Math.sin(dragon.angle)*5,vx:Math.cos(dragon.angle)*0.4,vy:-0.15,vz:Math.sin(dragon.angle)*0.4,life:40,color:'#ff6600'});
    }
  }else{
    dragon.angle=Math.atan2(dz,dx);
    dragon.x+=Math.cos(dragon.angle)*0.08;
    dragon.z+=Math.sin(dragon.angle)*0.08;
    dragon.y=6+Math.sin(frame*0.06)*3;
    dragon.wingPhase=frame*0.12;
  }
  
  // Update particles
  for(let i=particles.length-1;i>=0;i--){
    const p=particles[i];
    p.x+=p.vx;
    p.y+=p.vy;
    p.z+=p.vz;
    p.life--;
    p.vy+=0.008;
    if(p.life<=0) particles.splice(i,1);
  }
  
  render();
}

// Controls
document.addEventListener('keydown',e)=>{
  const sp=0.4;
  switch(e.key){
    case 'w':case 'ArrowUp':player.x+=Math.cos(player.angle)*sp;player.z+=Math.sin(player.angle)*sp;break;
    case 's':case 'ArrowDown':player.x-=Math.cos(player.angle)*sp;player.z-=Math.sin(player.angle)*sp;break;
    case 'a':case 'ArrowLeft':player.angle-=0.12;break;
    case 'd':case 'ArrowRight':player.angle+=0.12;break;
    case 'f':case 'F':
      dragon.x=player.x+Math.cos(player.angle)*10;
      dragon.z=player.z+Math.sin(player.angle)*10;
      break;
  }
});

document.getElementById('bW').onclick=()=>{player.x+=Math.cos(player.angle)*0.4;player.z+=Math.sin(player.angle)*0.4;};
document.getElementById('bS').onclick=()=>{player.x-=Math.cos(player.angle)*0.4;player.z-=Math.sin(player.angle)*0.4;};
document.getElementById('bA').onclick=()=>player.angle-=0.15;
document.getElementById('bD').onclick=()=>player.angle+=0.15;
document.getElementById('bF').onclick=()=>{
  dragon.x=player.x+Math.cos(player.angle)*10;
  dragon.z=player.z+Math.sin(player.angle)*10;
};

// Touch controls
let tx=0,ty=0;
canvas.addEventListener('touchstart',e=>{const t=e.touches[0];tx=t.clientX;ty=t.clientY;});
canvas.addEventListener('touchmove',e=>{
  e.preventDefault();
  const t=e.touches[0];
  const dx=t.clientX-tx, dy=t.clientY-ty;
  if(Math.abs(dx)>10){player.angle+=dx*0.005;tx=t.clientX;}
  if(Math.abs(dy)>10){player.x+=Math.cos(player.angle)*dy*0.01;player.z+=Math.sin(player.angle)*dy*0.01;ty=t.clientY;}
},{passive:false});

// Init
generateWorld();
dragon.x=30; dragon.z=20;
update();
</script>
</body>
</html>
"""

components.html(game_html, height=1000, scrolling=False)
