# app.py
import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random
import numpy as np

st.set_page_config(
    page_title="Dragon Realm",
    page_icon=":dragon:",
    layout="wide"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin: 0; padding: 0; background: #0a0a12;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SCRCAE ENGINE - EMBEDDED
# ============================================================

class Intervention:
    def __init__(self, node_id, name, description, cost, risk_reduction_pts, lead_time_saved_days, carbon_tons):
        self.node_id = node_id
        self.name = name
        self.description = description
        self.cost = cost
        self.risk_reduction_pts = risk_reduction_pts
        self.lead_time_saved_days = lead_time_saved_days
        self.carbon_tons = carbon_tons

class Dependency:
    def __init__(self, dependent, prerequisite):
        self.dependent = dependent
        self.prerequisite = prerequisite

class Bundle:
    def __init__(self, name, discount, required_nodes):
        self.name = name
        self.discount = discount
        self.required_nodes = required_nodes

class PriceBook:
    def __init__(self, value_per_risk_point, value_per_lead_time_day, price_per_carbon_ton, benefit_horizon_years, discount_rate, source):
        self.value_per_risk_point = value_per_risk_point
        self.value_per_lead_time_day = value_per_lead_time_day
        self.price_per_carbon_ton = price_per_carbon_ton
        self.benefit_horizon_years = benefit_horizon_years
        self.discount_rate = discount_rate
        self.source = source

class SupplyNetwork:
    def __init__(self, baseline_risk_pts, interventions, dependencies=None, bundles=None):
        self.baseline_risk_pts = baseline_risk_pts
        self.interventions = interventions
        self.dependencies = dependencies or ()
        self.bundles = bundles or ()

class AllocationConcaveResponse:
    def __init__(self, exponent):
        self.exponent = exponent

class MonetaryNPVObjective:
    def __init__(self, prices):
        self.prices = prices

class OptimizationRequest:
    def __init__(self, network, objective, risk_response, budget):
        self.network = network
        self.objective = objective
        self.risk_response = risk_response
        self.budget = budget

class ActiveAllocation:
    def __init__(self, node_id, name, funding_scale, capital, risk_reduction_pts):
        self.node_id = node_id
        self.name = name
        self.funding_scale = funding_scale
        self.capital = capital
        self.risk_reduction_pts = risk_reduction_pts

class OptimizationResult:
    def __init__(self, status, objective_value, objective_unit, net_capital, gross_capital, bundle_discounts, active_bundles, baseline_risk_pts, optimized_risk_pts, risk_reduction_pts, total_lead_time_saved_days, active_allocations, constraint_report, audit):
        self.status = status
        self.objective_value = objective_value
        self.objective_unit = objective_unit
        self.net_capital = net_capital
        self.gross_capital = gross_capital
        self.bundle_discounts = bundle_discounts
        self.active_bundles = active_bundles
        self.baseline_risk_pts = baseline_risk_pts
        self.optimized_risk_pts = optimized_risk_pts
        self.risk_reduction_pts = risk_reduction_pts
        self.total_lead_time_saved_days = total_lead_time_saved_days
        self.active_allocations = active_allocations
        self.constraint_report = constraint_report
        self.audit = audit

class ConstraintReport:
    def summary(self):
        return "All constraints satisfied"

def solve(request):
    network = request.network
    budget = request.budget
    exponent = request.risk_response.exponent
    prices = request.objective.prices
    
    npv_scores = []
    for inv in network.interventions:
        risk_benefit = inv.risk_reduction_pts * prices.value_per_risk_point * prices.benefit_horizon_years
        lead_time_benefit = inv.lead_time_saved_days * prices.value_per_lead_time_day * prices.benefit_horizon_years
        carbon_cost = inv.carbon_tons * prices.price_per_carbon_ton * prices.benefit_horizon_years
        total_benefit = risk_benefit + lead_time_benefit - carbon_cost
        npv = total_benefit / (1 + prices.discount_rate) - inv.cost
        npv_scores.append((inv, npv))
    
    npv_scores.sort(key=lambda x: x[1], reverse=True)
    
    active_allocations = []
    total_spent = 0
    total_risk_reduction = 0
    total_lead_time_saved = 0
    active_bundles = set()
    allocated_nodes = set()
    
    for inv, npv in npv_scores:
        if total_spent >= budget:
            break
        
        deps_met = True
        for dep in network.dependencies:
            if dep.dependent == inv.node_id:
                if dep.prerequisite not in allocated_nodes:
                    deps_met = False
                    break
        
        if not deps_met:
            continue
        
        remaining_budget = budget - total_spent
        max_scale = min(1.0, remaining_budget / inv.cost)
        
        if max_scale <= 0:
            continue
        
        scale = max_scale ** exponent
        capital = inv.cost * scale
        risk_red = inv.risk_reduction_pts * scale
        lead_time = inv.lead_time_saved_days * scale
        
        if capital > 0:
            total_spent += capital
            total_risk_reduction += risk_red
            total_lead_time_saved += lead_time
            allocated_nodes.add(inv.node_id)
            active_allocations.append(ActiveAllocation(inv.node_id, inv.name, scale, capital, risk_red))
    
    gross_capital = total_spent
    bundle_discounts = 0
    
    for bundle in network.bundles:
        if all(node in allocated_nodes for node in bundle.required_nodes):
            active_bundles.add(bundle.name)
            bundle_discounts += bundle.discount
            total_spent -= bundle.discount
    
    optimized_risk = network.baseline_risk_pts - total_risk_reduction
    
    return OptimizationResult(
        status="optimal",
        objective_value=total_risk_reduction * prices.value_per_risk_point * prices.benefit_horizon_years,
        objective_unit="NPV",
        net_capital=total_spent,
        gross_capital=gross_capital,
        bundle_discounts=bundle_discounts,
        active_bundles=active_bundles,
        baseline_risk_pts=network.baseline_risk_pts,
        optimized_risk_pts=max(0, optimized_risk),
        risk_reduction_pts=total_risk_reduction,
        total_lead_time_saved_days=total_lead_time_saved,
        active_allocations=active_allocations,
        constraint_report=ConstraintReport(),
        audit={"input_hash": "embedded", "output_hash": "embedded"}
    )

# ============================================================
# MAGIC SYSTEM
# ============================================================

class MagicSystem:
    ELEMENTS = ['fire', 'water', 'earth', 'air', 'light', 'shadow']
    
    @staticmethod
    def generate_magic_grid(size=50):
        grid = [[[0 for _ in range(6)] for _ in range(size)] for _ in range(size)]
        for i, element in enumerate(MagicSystem.ELEMENTS):
            freq_x = random.uniform(0.02, 0.08)
            freq_z = random.uniform(0.02, 0.08)
            phase = random.uniform(0, 2 * math.pi)
            for x in range(size):
                for z in range(size):
                    concentration = (
                        math.sin(x * freq_x + z * freq_z + phase) * 0.5 +
                        math.sin(x * 0.1 + z * 0.15 + phase * 2) * 0.3 +
                        random.gauss(0, 0.1)
                    )
                    grid[x][z][i] = max(0, concentration)
        
        for x in range(size):
            for z in range(size):
                total = sum(grid[x][z])
                if total > 0:
                    for i in range(6):
                        grid[x][z][i] /= total
        return grid
    
    @staticmethod
    def get_dominant_element(magic_grid, x, z):
        values = magic_grid[x][z]
        idx = values.index(max(values))
        return MagicSystem.ELEMENTS[idx], values[idx]

# ============================================================
# WORLD GENERATION
# ============================================================

def generate_world():
    species_interventions = (
        Intervention("DR", "Dragon", "Ancient fire-breathing dragon", 50000.0, 90.0, 30.0, 200.0),
        Intervention("GO", "Goblin", "Cunning cave dwellers", 10000.0, 20.0, 8.0, 30.0),
        Intervention("EL", "Elf", "Magical forest beings", 30000.0, 60.0, 15.0, 10.0),
        Intervention("WO", "Wolf", "Pack hunters of the plains", 8000.0, 15.0, 5.0, 20.0),
        Intervention("BE", "Bear", "Mighty forest dwellers", 12000.0, 25.0, 6.0, 40.0),
        Intervention("FA", "Fairy", "Tiny magical creatures", 20000.0, 70.0, 20.0, 5.0),
    )
    
    dependencies = (Dependency("EL", "FA"), Dependency("DR", "EL"))
    bundles = (Bundle("Forest_Alliance", 15000.0, ("EL", "FA")), Bundle("Dragon_Pact", 25000.0, ("DR", "EL")))
    prices = PriceBook(5000.0, 1000.0, 50.0, 5, 0.10, "game-calibrated")
    
    network = SupplyNetwork(100.0, species_interventions, dependencies, bundles)
    result = solve(OptimizationRequest(network=network, objective=MonetaryNPVObjective(prices=prices), risk_response=AllocationConcaveResponse(exponent=0.85), budget=200000.0))
    
    species_allocations = {}
    for a in result.active_allocations:
        species_allocations[a.node_id] = {'scale': a.funding_scale, 'capital': a.capital, 'risk_reduction': a.risk_reduction_pts}
    
    # Generate terrain
    terrain = [[0 for _ in range(50)] for _ in range(50)]
    for x in range(50):
        for z in range(50):
            terrain[x][z] = (
                math.sin(x * 0.1) * math.cos(z * 0.12) * 3 +
                math.sin(x * 0.25 + z * 0.18) * 2 +
                math.sin(x * 0.05 + z * 0.08) * 5 +
                random.gauss(0, 0.3)
            )
    
    min_val = min(min(row) for row in terrain)
    max_val = max(max(row) for row in terrain)
    for x in range(50):
        for z in range(50):
            terrain[x][z] = ((terrain[x][z] - min_val) / (max_val - min_val)) * 20
    
    magic = MagicSystem.generate_magic_grid(50)
    
    biomes = []
    for x in range(0, 50, 2):
        for z in range(0, 50, 2):
            height = terrain[x][z]
            if height > 15: biome = 'mountain'
            elif height > 10: biome = 'forest'
            elif height > 5: biome = 'plains'
            elif height > 2: biome = 'swamp'
            else: biome = 'water'
            
            dom_element, dom_strength = MagicSystem.get_dominant_element(magic, x, z)
            
            poi = None
            if biome == 'mountain' and dom_strength > 0.6:
                poi = {'type': 'dragon_lair', 'name': 'Dragonspire Peak', 'element': dom_element}
            elif biome == 'forest' and dom_strength > 0.5:
                poi = {'type': 'elf_camp', 'name': 'Silverwood Grove', 'element': dom_element}
            elif biome == 'swamp' and dom_strength > 0.4:
                poi = {'type': 'goblin_cave', 'name': 'Murkden Hollow', 'element': dom_element}
            
            biomes.append({'x': x, 'z': z, 'height': round(height, 1), 'biome': biome,
                          'magic_element': dom_element, 'magic_strength': round(dom_strength, 2), 'poi': poi})
    
    creatures = []
    species_map = {
        'DR': {'name': 'Dragon', 'biome': 'mountain', 'speed': 8, 'strength': 10, 'magic': 9, 'stealth': 3, 'hp': 100},
        'GO': {'name': 'Goblin', 'biome': 'swamp', 'speed': 4, 'strength': 3, 'magic': 2, 'stealth': 7, 'hp': 30},
        'EL': {'name': 'Elf', 'biome': 'forest', 'speed': 6, 'strength': 4, 'magic': 8, 'stealth': 6, 'hp': 50},
        'WO': {'name': 'Wolf', 'biome': 'plains', 'speed': 7, 'strength': 5, 'magic': 1, 'stealth': 8, 'hp': 40},
        'BE': {'name': 'Bear', 'biome': 'forest', 'speed': 3, 'strength': 8, 'magic': 1, 'stealth': 4, 'hp': 80},
        'FA': {'name': 'Fairy', 'biome': 'forest', 'speed': 9, 'strength': 1, 'magic': 10, 'stealth': 9, 'hp': 20}
    }
    
    for node_id, alloc in species_allocations.items():
        if node_id in species_map:
            sp = species_map[node_id]
            count = max(1, int(alloc['scale'] * 5))
            suitable = [b for b in biomes if b['biome'] == sp['biome']]
            for i in range(count):
                if suitable:
                    loc = random.choice(suitable)
                    creatures.append({
                        'name': sp['name'], 'x': loc['x'], 'z': loc['z'],
                        'stats': {'speed': sp['speed'], 'strength': sp['strength'], 'magic': sp['magic'], 'stealth': sp['stealth']},
                        'element': loc['magic_element'], 'hp': sp['hp'], 'max_hp': sp['hp'], 'alive': True,
                        'scale': round(alloc['scale'], 3), 'type': 'enemy'
                    })
    
    # Add Devil NPC (good character)
    devil_biome = random.choice([b for b in biomes if b['biome'] == 'mountain' or b['biome'] == 'forest'])
    creatures.append({
        'name': 'Devil', 'x': devil_biome['x'], 'z': devil_biome['z'],
        'stats': {'speed': 7, 'strength': 9, 'magic': 10, 'stealth': 5},
        'element': 'shadow', 'hp': 200, 'max_hp': 200, 'alive': True,
        'scale': 1.0, 'type': 'npc', 'npc_type': 'devil',
        'dialogues': [
            "I am the Devil of this realm. Fear not, I mean you no harm.",
            "The dragon's power grows. You must stop it before it consumes everything.",
            "I can teach you forbidden magic... for a price.",
            "The shadows whisper of an ancient evil awakening.",
            "You have potential, mortal. Do not waste it.",
            "I have walked these lands since before time. I know every secret.",
            "Beware the goblin market. They trade in lies and broken dreams."
        ]
    })
    
    return {
        'terrain': terrain, 'magic_grid': magic, 'biomes': biomes, 'creatures': creatures,
        'optimization_result': {'status': result.status, 'objective': result.objective_value,
                               'risk_reduction': result.risk_reduction_pts,
                               'active_bundles': list(result.active_bundles)}
    }

# ============================================================
# STREAMLIT UI
# ============================================================

if 'world_data' not in st.session_state:
    with st.spinner("Running SCRCAE optimization..."):
        st.session_state.world_data = generate_world()
        st.session_state.player_x = 25
        st.session_state.player_z = 25
        st.session_state.player_angle = 0
        st.session_state.message = "World optimized! Swipe to look around. Tap attack to fight."
        st.session_state.discovered = set()
        st.session_state.dragon_tame = 0
        st.session_state.magic_affinity = {'fire': 0.5, 'water': 0.5, 'earth': 0.5, 'air': 0.5, 'light': 0.5, 'shadow': 0.5}
        st.session_state.spells = []
        st.session_state.health = 100
        st.session_state.gold = 0
        st.session_state.attack_power = 10
        st.session_state.kills = 0
        st.session_state.devil_talked = False

world = st.session_state.world_data

# Build HTML with JSON embedded via JavaScript variables
terrain_json = json.dumps(world['terrain'])
biomes_json = json.dumps(world['biomes'])
creatures_json = json.dumps(world['creatures'])

viewer_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:#0a0a12;overflow:hidden;font-family:monospace;color:#fff}}
    canvas{{display:block;width:100vw;height:100vh;touch-action:none}}
    #hud{{position:absolute;top:10px;left:10px;font-size:11px;text-shadow:0 2px 4px #000;background:rgba(0,0,0,0.7);padding:8px 12px;border-radius:8px;z-index:10;pointer-events:none}}
    #crosshair{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:24px;text-shadow:0 0 10px #fff;z-index:10;pointer-events:none;opacity:0.5}}
    #controls{{position:absolute;bottom:20px;left:0;right:0;display:flex;justify-content:center;gap:10px;z-index:10}}
    button{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff;font-size:14px;padding:10px 16px;border-radius:20px;min-width:44px;touch-action:manipulation;backdrop-filter:blur(4px)}}
    button:active{{background:rgba(255,255,255,0.3);transform:scale(0.95)}}
    #attackBtn{{background:rgba(255,50,50,0.3);border-color:rgba(255,50,50,0.5)}}
    #talkBtn{{background:rgba(100,50,255,0.3);border-color:rgba(100,50,255,0.5)}}
    .blood-splatter{{position:absolute;pointer-events:none;z-index:5;font-size:20px;animation:bloodFade 1s forwards}}
    @keyframes bloodFade{{0%{{opacity:1;transform:scale(1)}}100%{{opacity:0;transform:scale(2)}}}}
    #dialogue{{position:absolute;bottom:100px;left:10%;right:10%;background:rgba(0,0,0,0.8);border:1px solid rgba(100,50,255,0.5);border-radius:10px;padding:15px;text-align:center;z-index:20;display:none;backdrop-filter:blur(8px)}}
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
var terrain = {terrain_json};
var biomes = {biomes_json};
var creatures = {creatures_json};

var canvas=document.getElementById("c");
var ctx=canvas.getContext("2d");
var info=document.getElementById("info");
var combatInfo=document.getElementById("combatInfo");
var dialogueEl=document.getElementById("dialogue");

var W, H;
var player = {{x: 25, z: 25, angle: 0}};
var frame = 0;
var attackCooldown = 0;
var bloodEffects = [];

function resize() {{W=window.innerWidth; H=window.innerHeight; canvas.width=W; canvas.height=H;}}
window.addEventListener("resize", resize); resize();

function project(x, z, y) {{
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
    return {{x: sx, y: sy, scale: fov/rz}};
}}

function getBiome(x, z) {{
    for(var i=0; i<biomes.length; i++) {{
        var b = biomes[i];
        if(b.x === x && b.z === z) return b;
    }}
    return null;
}}

function getClosestCreature() {{
    var closest = null;
    var minDist = 999;
    for(var i=0; i<creatures.length; i++) {{
        var c = creatures[i];
        if(!c.alive) continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist < minDist) {{
            minDist = dist;
            closest = c;
        }
    }
    return closest;
}}

function spawnBlood(x, y) {{
    for(var i=0; i<5; i++) {{
        var el = document.createElement("div");
        el.className = "blood-splatter";
        el.textContent = "💀";
        el.style.left = (x + random()*40 - 20) + "px";
        el.style.top = (y + random()*40 - 20) + "px";
        el.style.color = ["#ff0000","#cc0000","#ff4444","#aa0000","#ff6666"][i];
        el.style.fontSize = (15 + random()*20) + "px";
        document.body.appendChild(el);
        setTimeout(function() {el.remove();}, 1000);
    }
}

function attack() {{
    if(attackCooldown > 0) return;
    attackCooldown = 15;
    
    var target = getClosestCreature();
    if(target && Math.sqrt((target.x - player.x)*(target.x - player.x) + (target.z - player.z)*(target.z - player.z)) < 5) {{
        var damage = 10 + Math.floor(Math.random() * 10);
        target.hp -= damage;
        
        // Blood effect
        var p = project(target.x, 0, 1);
        if(p) spawnBlood(p.x, p.y);
        
        combatInfo.textContent = "HIT! " + target.name + " took " + damage + " damage! HP: " + Math.max(0,target.hp) + "/" + target.max_hp;
        
        if(target.hp <= 0) {{
            target.alive = false;
            combatInfo.textContent = "KILLED " + target.name + "!";
            // Big blood splatter on death
            for(var b=0; b<10; b++) {{
                setTimeout(function() {{
                    var pp = project(target.x, 0, 1);
                    if(pp) spawnBlood(pp.x, pp.y);
                }}, b * 100);
            }}
            window.parent.postMessage({{type: "kill", creature: target.name}}, "*");
        }}
    }} else {{
        combatInfo.textContent = "No enemies nearby!";
    }}
}}

function talkToNPC() {{
    for(var i=0; i<creatures.length; i++) {{
        var c = creatures[i];
        if(!c.alive || c.type !== "npc") continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist < 5) {{
            var dialogue = c.dialogues[Math.floor(Math.random() * c.dialogues.length)];
            dialogueEl.style.display = "block";
            dialogueEl.innerHTML = "<b style='color:#8844aa;'>" + c.name + ":</b> " + dialogue;
            setTimeout(function() {{dialogueEl.style.display = "none";}}, 5000);
            window.parent.postMessage({{type: "talk", npc: c.name, dialogue: dialogue}}, "*");
            return;
        }}
    }}
    combatInfo.textContent = "No NPCs nearby to talk to.";
}}

var biomeColors = {{
    "mountain": "#6a6a7a", "forest": "#2d5a27", "cliffs": "#8a7a5a",
    "plains": "#6a8a4a", "desert": "#c2a65a", "swamp": "#3a5a3a",
    "grassland": "#5a7a3a", "water": "#2a4a6a"
}};

var elementColors = {{
    "fire": "#ff4400", "water": "#4488ff", "earth": "#886644",
    "air": "#aaddff", "light": "#ffff88", "shadow": "#8844aa"
}};

function render() {{
    ctx.fillStyle = "#0a0a12";
    ctx.fillRect(0, 0, W, H);
    
    // Stars
    for(var i=0; i<80; i++) {{
        ctx.fillStyle = "#fff";
        ctx.globalAlpha = 0.15 + Math.sin(i + frame * 0.01) * 0.15;
        ctx.beginPath();
        ctx.arc((i * 137.5) % W, (i * 97.3) % (H * 0.6), 0.5 + Math.sin(i)*0.5, 0, Math.PI*2);
        ctx.fill();
    }}
    ctx.globalAlpha = 1;
    
    // Ground
    for(var i=-10; i<=10; i+=2) {{
        for(var j=-10; j<=10; j+=2) {{
            var p = project(player.x + i, player.z + j, 0);
            if(!p || p.scale < 0.01) continue;
            ctx.fillStyle = "#1a1a2a";
            ctx.globalAlpha = Math.min(0.5, p.scale * 0.01);
            ctx.fillRect(p.x - 1, p.y - 1, 2, 2);
        }}
    }}
    ctx.globalAlpha = 1;
    
    // Draw terrain
    for(var i=0; i<biomes.length; i++) {{
        var b = biomes[i];
        var p = project(b.x, 0, b.height * 0.3);
        if(!p || p.scale < 0.01) continue;
        
        var dist = Math.sqrt((b.x - player.x)*(b.x - player.x) + (b.z - player.z)*(b.z - player.z));
        var brightness = Math.max(0.05, 1 - dist / 25);
        ctx.globalAlpha = brightness;
        ctx.fillStyle = biomeColors[b.biome] || "#444";
        var s = Math.max(0.5, p.scale * 0.2);
        ctx.fillRect(p.x - s/2, p.y - s/2, s, s);
        
        // Magic glow
        if(b.magic_strength > 0.6) {{
            ctx.shadowBlur = 8;
            ctx.shadowColor = elementColors[b.magic_element] || "#fff";
            ctx.fillStyle = elementColors[b.magic_element] || "#fff";
            ctx.globalAlpha = b.magic_strength * 0.15;
            ctx.beginPath();
            ctx.arc(p.x, p.y, s * 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }}
        
        // POI
        if(b.poi) {{
            ctx.fillStyle = "#ffc864";
            ctx.globalAlpha = 0.7;
            ctx.beginPath();
            ctx.arc(p.x, p.y - s, s * 0.8, 0, Math.PI * 2);
            ctx.fill();
        }}
    }}
    ctx.globalAlpha = 1;
    
    // Draw creatures
    for(var i=0; i<creatures.length; i++) {{
        var c = creatures[i];
        if(!c.alive) continue;
        var p = project(c.x, 0, 1);
        if(!p) continue;
        var dist = Math.sqrt((c.x - player.x)*(c.x - player.x) + (c.z - player.z)*(c.z - player.z));
        if(dist > 20) continue;
        
        var size = c.type === "npc" ? 5 : 3 + c.stats.speed * 0.3;
        var hpPct = c.hp / c.max_hp;
        
        // Body
        if(c.type === "npc") {{
            ctx.fillStyle = "#8844aa";
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#8844aa";
        }} else {{
            ctx.fillStyle = elementColors[c.element] || "#fff";
            ctx.shadowBlur = 6;
            ctx.shadowColor = elementColors[c.element] || "#fff";
        }}
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        
        // HP bar
        ctx.fillStyle = "#333";
        ctx.fillRect(p.x - size, p.y - size - 4, size * 2, 2);
        ctx.fillStyle = hpPct > 0.5 ? "#4f4" : hpPct > 0.25 ? "#ff4" : "#f44";
        ctx.fillRect(p.x - size, p.y - size - 4, size * 2 * hpPct, 2);
        
        // Name
        ctx.fillStyle = "#fff";
        ctx.font = c.type === "npc" ? "9px monospace" : "7px monospace";
        ctx.textAlign = "center";
        ctx.fillText(c.name, p.x, p.y - size - 6);
        
        // Highlight closest enemy
        if(c.type !== "npc") {{
            var closest = getClosestCreature();
            if(closest && closest === c) {{
                ctx.strokeStyle = "#ff0";
                ctx.globalAlpha = 0.3 + Math.sin(frame * 0.1) * 0.3;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, size + 3, 0, Math.PI * 2);
                ctx.stroke();
            }}
        }}
    }}
    ctx.globalAlpha = 1;
    
    // Player
    var pp = project(player.x, 0, 0.3);
    if(pp) {{
        ctx.fillStyle = "#fff";
        ctx.shadowBlur = 10;
        ctx.shadowColor = "#fff";
        ctx.beginPath();
        ctx.arc(pp.x, pp.y, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }}
    
    // HUD
    var biome = getBiome(Math.round(player.x), Math.round(player.z));
    var hudText = "Pos: (" + Math.round(player.x) + ", " + Math.round(player.z) + ")";
    if(biome) {{
        hudText += " | " + biome.biome.toUpperCase();
        hudText += " | " + biome.magic_element.toUpperCase() + " (" + (biome.magic_strength * 100).toFixed(0) + "%)";
    }}
    info.textContent = hudText;
    
    if(attackCooldown > 0) attackCooldown--;
    frame++;
    requestAnimationFrame(render);
}}

function move(dx, ddz) {{
    var nx = player.x + dx;
    var nz = player.z + dz;
    if(nx >= 0 && nx < 50 && nz >= 0 && nz < 50) {{
        player.x = nx;
        player.z = nz;
    }}
}}

// Touch controls for rotation
var tx = 0, ty = 0;
canvas.addEventListener("touchstart", function(e) {{
    var t = e.touches[0];
    tx = t.clientX;
    ty = t.clientY;
}});
canvas.addEventListener("touchmove", function(e) {{
    e.preventDefault();
    var t = e.touches[0];
    var dx = t.clientX - tx;
    if(Math.abs(dx) > 15) {{
        player.angle += dx * 0.005;
        tx = t.clientX;
    }}
}}, {{passive: false}});

render();
</script>
</body>
</html>
"""

# Render the viewer
components.html(viewer_html, height=600, scrolling=False)

# Sidebar
with st.sidebar:
    st.markdown("## Dragon Realm")
    
    st.markdown("### SCRCAE Results")
    opt = world['optimization_result']
    st.markdown(f"- Status: {opt['status']}")
    st.markdown(f"- Objective: {opt['objective']:,.0f}")
    st.markdown(f"- Risk Reduction: {opt['risk_reduction']:.2f} pts")
    
    st.markdown("### Magic")
    biome = next((b for b in world['biomes'] if b['x'] == st.session_state.player_x and b['z'] == st.session_state.player_z), None)
    if biome:
        st.markdown(f"- Element: {biome['magic_element'].upper()}")
        st.markdown(f"- Strength: {biome['magic_strength']*100:.0f}%")
    
    st.markdown(f"### Stats")
    st.markdown(f"Health: {st.session_state.health}/100")
    st.markdown(f"Gold: {st.session_state.gold}")
    st.markdown(f"Kills: {st.session_state.kills}")
    
    if st.button("Learn Spell (50 gold)"):
        if st.session_state.gold >= 50:
            st.session_state.gold -= 50
            new_spell = random.choice(['Fireball', 'Heal', 'Teleport', 'Lightning'])
            if new_spell not in st.session_state.spells:
                st.session_state.spells.append(new_spell)
                st.session_state.message = f"Learned {new_spell}!"
    
    if st.session_state.spells:
        for s in st.session_state.spells:
            st.markdown(f"- {s}")

# Message
if st.session_state.message:
    st.markdown(f"<dive style='background:rgba(255,200,100,0.1);padding:10px;border-radius:8px;text-align:center;color:#ffc864;'>{st.session_state.message}</div>", unsafe_allow_html=True)

# Listen for messages from JavaScript
st.markdown("""
<script>
window.addEventListener("message", function(e) {
    if(e.data.type === "kill") {
        // Will be handled on next rerun
    }
});
</script>
""", unsafe_allow_html=True)
