<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#0a0a12;overflow:hidden;font-family:monospace;color:#fff}
    canvas{display:block;width:100vw;height:100vh;touch-action:none}
    #hud{position:absolute;top:10px;left:10px;font-size:11px;text-shadow:0 2px 4px #000;background:rgba(0,0,0,0.7);padding:8px 12px;border-radius:8px;z-index:10;pointer-events:none}
    #crosshair{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:24px;text-shadow:0 0 10px #fff;z-index:10;pointer-events:none;opacity:0.5}
    #controls{position:absolute;bottom:20px;left:0;right:0;display:flex;justify-content:center;gap:10px;z-index:10}
    button{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff;font-size:14px;padding:10px 16px;border-radius:20px;min-width:44px;touch-action:manipulation;backdrop-filter:blur(4px)}
    button:active{background:rgba(255,255,255,0.3);transform:scale(0.95)}
    #attackBtn{background:rgba(255,50,50,0.3);border-color:rgba(255,50,50,0.5)}
    #talkBtn{background:rgba(100,50,255,0.3);border-color:rgba(100,50,255,0.5)}
    .blood-splatter{position:absolute;pointer-events:none;z-index:5;font-size:20px;animation:bloodFade 1s forwards}
    @keyframes bloodFade{0%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(2)}}
    #dialogue{position:absolute;bottom:100px;left:10%;right:10%;background:rgba(0,0,0,0.8);border:1px solid rgba(100,50,255,0.5);border-radius:10px;padding:15px;text-align:center;z-index:20;display:none;backdrop-filter:blur(8px)}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hud">
    <div id="info">Loading...</div>
    <div id="combatInfo" style="font-size:10px;color:#ff6666;margin-top:4px;"></div>
</div>
<div id="crosshair">+</div>
<div id="dialogue"></div>
<div id="controls">
    <button id="attackBtn" ontouchstart="attack()" onmousedown="attack()">&#9876;</button>
    <button id="talkBtn" ontouchstart="talkToNPC()" onmousedown="talkToNPC()">&#128172;</button>
    <button ontouchstart="move(0,-2)" onmousedown="move(0,-2)">&#9650;</button>
    <button ontouchstart="move(0,2)" onmousedown="move(0,2)">&#9660;</button>
</div>
<script>
var terrain = __TERRAIN_DATA__;
var biomes = __BIOMES_DATA__;
var creatures = __CREATURES_DATA__;

var canvas=document.getElementById("c");
var ctx=canvas.getContext("2d");
var info=document.getElementById("info");
var combatInfo=document.getElementById("combatInfo");
var dialogueEl=document.getElementById("dialogue");

var W, H;
var player = {x: 25, z: 25, angle: 0};
var frame = 0;
var attackCooldown = 0;

function resize() {W=window.innerWidth; H=window.innerHeight; canvas.width=W; canvas.height=H;}
window.addEventListener("resize", resize); resize();

function project(x, z, y) {
    var fov = 250;
    var dx = x - player.x;
    var dz = z - player.z;
    var cosA = Math.cos(player.angle);
    var sinA = Math.sin(player.angle);
    var rx = dx * cosA - dz * sinA;
    var rz = dx * sinA + dz * cosA;
    if(rz < 0.5) return null;
    var sx = W/2 + (rx * fov) / rz;
    var sy = H/2 - (y * fov) / rz;
    return {x: sx, y: sy, scale: fov/rz};
}

function getBiome(x, z) {
    for(var i=0; i<biomes.length; i++) {
        var b = biomes[i];
        if(b.x === x && b.z === z) return b;
    }
    return null;
}

function getClosestCreature() {
    var closest = null;
    var minDist = 999;
    for(var i=0; i<creatures.length; i++) {
        var c = creatures[i];
        if(!c.alive) continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist < minDist) {
            minDist = dist;
            closest = c;
        }
    }
    return closest;
}

function spawnBlood(x, y) {
    var colors = ["#ff0000","#cc0000","#ff4444","#aa0000","#ff6666"];
    for(var i=0; i<5; i++) {
        var el = document.createElement("div");
        el.className = "blood-splatter";
        el.textContent = "&#128128;";
        el.style.left = (x + Math.random()*40 - 20) + "px";
        el.style.top = (y + Math.random()*40 - 20) + "px";
        el.style.color = colors[i];
        el.style.fontSize = (15 + Math.random()*20) + "px";
        document.body.appendChild(el);
        setTimeout(function() {el.remove();}, 1000);
    }
}

function attack() {
    if(attackCooldown > 0) return;
    attackCooldown = 15;
    
    var target = getClosestCreature();
    if(target && Math.sqrt((target.x - player.x)*(target.x - player.x) + (target.z - player.z)*(target.z - player.z)) < 5) {
        var damage = 10 + Math.floor(Math.random() * 10);
        target.hp -= damage;
        
        var p = project(target.x, 0, 1);
        if(p) spawnBlood(p.x, p.y);
        
        combatInfo.textContent = "HIT! " + target.name + " took " + damage + " damage! HP: " + Math.max(0,target.hp) + "/" + target.max_hp;
        
        if(target.hp <= 0) {
            target.alive = false;
            combatInfo.textContent = "KILLED " + target.name + "!";
            for(var b=0; b<10; b++) {
                setTimeout(function() {
                    var pp = project(target.x, 0, 1);
                    if(pp) spawnBlood(pp.x, pp.y);
                }, b * 100);
            }
        }
    } else {
        combatInfo.textContent = "No enemies nearby!";
    }
}

function talkToNPC() {
    for(var i=0; i<creatures.length; i++) {
        var c = creatures[i];
        if(!c.alive || c.type !== "npc") continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist < 5) {
            var dialogue = c.dialogues[Math.floor(Math.random() * c.dialogues.length)];
            dialogueEl.style.display = "block";
            dialogueEl.innerHTML = "<b style='color:#8844aa;'>" + c.name + ":</b> " + dialogue;
            setTimeout(function() {dialogueEl.style.display = "none";}, 5000);
            return;
        }
    }
    combatInfo.textContent = "No NPCs nearby to talk to.";
}

var biomeColors = {
    "mountain": "#6a6a7a", "forest": "#2d5a27", "cliffs": "#8a7a5a",
    "plains": "#6a8a4a", "desert": "#c2a65a", "swamp": "#3a5a3a",
    "grassland": "#5a7a3a", "water": "#2a4a6a"
};

var elementColors = {
    "fire": "#ff4400", "water": "#4488ff", "earth": "#886644",
    "air": "#aaddff", "light": "#ffff88", "shadow": "#8844aa"
};

function render() {
    ctx.fillStyle = "#0a0a12";
    ctx.fillRect(0, 0, W, H);
    
    for(var i=0; i<80; i++) {
        ctx.fillStyle = "#fff";
        ctx.globalAlpha = 0.15 + Math.sin(i + frame * 0.01) * 0.15;
        ctx.beginPath();
        ctx.arc((i * 137.5) % W, (i * 97.3) % (H * 0.6), 0.5 + Math.sin(i)*0.5, 0, Math.PI*2);
        ctx.fill();
    }
    ctx.globalAlpha = 1;
    
    for(var i=-10; i<=10; i+=2) {
        for(var j=-10; j<=10; j+=2) {
            var p = project(player.x + i, player.z + j, 0);
            if(!p || p.scale < 0.01) continue;
            ctx.fillStyle = "#1a1a2a";
            ctx.globalAlpha = Math.min(0.5, p.scale * 0.01);
            ctx.fillRect(p.x - 1, p.y - 1, 2, 2);
        }
    }
    ctx.globalAlpha = 1;
    
    for(var i=0; i<biomes.length; i++) {
        var b = biomes[i];
        var p = project(b.x, 0, b.height * 0.3);
        if(!p || p.scale < 0.01) continue;
        
        var dist = Math.sqrt((b.x - player.x)*(b.x - player.x) + (b.z - player.z)*(b.z - player.z));
        var brightness = Math.max(0.05, 1 - dist / 25);
        ctx.globalAlpha = brightness;
        ctx.fillStyle = biomeColors[b.biome] || "#444";
        var s = Math.max(0.5, p.scale * 0.2);
        ctx.fillRect(p.x - s/2, p.y - s/2, s, s);
        
        if(b.magic_strength > 0.6) {
            ctx.shadowBlur = 8;
            ctx.shadowColor = elementColors[b.magic_element] || "#fff";
            ctx.fillStyle = elementColors[b.magic_element] || "#fff";
            ctx.globalAlpha = b.magic_strength * 0.15;
            ctx.beginPath();
            ctx.arc(p.x, p.y, s * 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
        
        if(b.poi) {
            ctx.fillStyle = "#ffc864";
            ctx.globalAlpha = 0.7;
            ctx.beginPath();
            ctx.arc(p.x, p.y - s, s * 0.8, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    ctx.globalAlpha = 1;
    
    for(var i=0; i<creatures.length; i++) {
        var c = creatures[i];
        if(!c.alive) continue;
        var p = project(c.x, 0, 1);
        if(!p) continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist > 20) continue;
        
        var size = c.type === "npc" ? 5 : 3 + c.stats.speed * 0.3;
        var hpPct = c.hp / c.max_hp;
        
        if(c.type === "npc") {
            ctx.fillStyle = "#8844aa";
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#8844aa";
        } else {
            ctx.fillStyle = elementColors[c.element] || "#fff";
            ctx.shadowBlur = 6;
            ctx.shadowColor = elementColors[c.element] || "#fff";
        }
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        
        ctx.fillStyle = "#333";
        ctx.fillRect(p.x - size, p.y - size - 4, size * 2, 2);
        ctx.fillStyle = hpPct > 0.5 ? "#4f4" : hpPct > 0.25 ? "#ff4" : "#f44";
        ctx.fillRect(p.x - size, p.y - size - 4, size * 2 * hpPct, 2);
        
        ctx.fillStyle = "#fff";
        ctx.font = c.type === "npc" ? "9px monospace" : "7px monospace";
        ctx.textAlign = "center";
        ctx.fillText(c.name, p.x, p.y - size - 6);
        
        if(c.type !== "npc") {
            var closest = getClosestCreature();
            if(closest && closest === c) {
                ctx.strokeStyle = "#ff0";
                ctx.globalAlpha = 0.3 + Math.sin(frame * 0.1) * 0.3;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, size + 3, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
    }
    ctx.globalAlpha = 1;
    
    var pp = project(player.x, 0, 0.3);
    if(pp) {
        ctx.fillStyle = "#fff";
        ctx.shadowBlur = 10;
        ctx.shadowColor = "#fff";
        ctx.beginPath();
        ctx.arc(pp.x, pp.y, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }
    
    var biome = getBiome(Math.round(player.x), Math.round(player.z));
    var hudText = "Pos: (" + Math.round(player.x) + ", " + Math.round(player.z) + ")";
    if(biome) {
        hudText += " | " + biome.biome.toUpperCase();
        hudText += " | " + biome.magic_element.toUpperCase() + " (" + (biome.magic_strength * 100).toFixed(0) + "%)";
    }
    info.textContent = hudText;
    
    if(attackCooldown > 0) attackCooldown--;
    frame++;
    requestAnimationFrame(render);
}

function move(dx, dz) {
    var nx = player.x + dx;
    var nz = player.z + dz;
    if(nx >= 0 && nx < 50 && nz >= 0 && nz < 50) {
        player.x = nx;
        player.z = nz;
    }
}

var tx = 0, ty = 0;
canvas.addEventListener("touchstart", function(e) {
    var t = e.touches[0];
    tx = t.clientX;
    ty = t.clientY;
});
canvas.addEventListener("touchmove", function(e) {
    e.preventDefault();
    var t = e.touches[0];
    var dx = t.clientX - tx;
    if(Math.abs(dx) > 15) {
        player.angle += dx * 0.005;
        tx = t.clientX;
    }
}, {passive: false});

render();
</script>
</body>
</html>
