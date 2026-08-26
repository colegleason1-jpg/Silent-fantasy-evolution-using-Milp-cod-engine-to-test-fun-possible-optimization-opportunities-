import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random

st.set_page_config(page_title="Dragon Realm", page_icon="🐉", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin: 0; padding: 0; background: #0a0a12; color: #fff;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SCRCAE ENGINE & DOMAIN MODELS
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
# MAGIC SYSTEM & WORLD GENERATION
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

def generate_world(dynamic_risk_offset=0.0):    
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
    
    network = SupplyNetwork(100.0 + dynamic_risk_offset, species_interventions, dependencies, bundles)    
    result = solve(OptimizationRequest(network=network, objective=MonetaryNPVObjective(prices=prices), risk_response=AllocationConcaveResponse(exponent=0.85), budget=float(st.session_state.gold + 100000.0)))    
    
    species_allocations = {}    
    for a in result.active_allocations:    
        species_allocations[a.node_id] = {'scale': a.funding_scale, 'capital': a.capital, 'risk_reduction': a.risk_reduction_pts}    
    
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
                    
    devil_biome = random.choice([b for b in biomes if b['biome'] == 'mountain' or b['biome'] == 'forest'])    
    creatures.append({    
        'name': 'Devil', 'x': devil_biome['x'], 'z': devil_biome['z'],    
        'stats': {'speed': 7, 'strength': 9, 'magic': 10, 'stealth': 5},    
        'element': 'shadow', 'hp': 200, 'max_hp': 200, 'alive': True,    
        'scale': 1.0, 'type': 'npc',    
        'dialogues': [    
            "I am the Devil of this realm. Fear not, I mean you no harm.",    
            "The dragon power grows. You must stop it.",    
            "I can teach you forbidden magic... for a price.",    
            "The shadows whisper of an ancient evil awakening.",    
            "You have potential, mortal. Do not waste it.",    
            "I have walked these lands since before time.",    
            "Beware the goblin market. They trade in lies."    
        ]    
    })    
    return {    
        'terrain': terrain, 'magic_grid': magic, 'biomes': biomes, 'creatures': creatures,    
        'optimization_result': {'status': result.status, 'objective': result.objective_value,    
                               'risk_reduction': result.risk_reduction_pts,    
                               'active_bundles': list(result.active_bundles)}    
    }

# ============================================================    
# STREAMLIT STATE INITIALIZATION & TURN CALLBACKS
# ============================================================    

def init_game_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.turn = 1
        st.session_state.health = 100
        st.session_state.max_health = 100
        st.session_state.gold = 150
        st.session_state.kills = 0
        st.session_state.player_x = 24
        st.session_state.player_z = 24
        st.session_state.message = "World optimized and loaded successfully!"
        st.session_state.faction_standing = {'Dragons': -10, 'Elves': 20, 'Goblins': -5, 'Fairies': 30}
        st.session_state.turn_log = []
        st.session_state.world_data = generate_world()

init_game_state()

def process_turn_advance(action_name: str, health_delta=0, gold_delta=0, faction_updates=None):
    st.session_state.turn += 1
    st.session_state.health = max(0, min(st.session_state.max_health, st.session_state.health + health_delta))
    st.session_state.gold = max(0, st.session_state.gold + gold_delta)
    
    if faction_updates:
        for faction, delta in faction_updates.items():
            if faction in st.session_state.faction_standing:
                st.session_state.faction_standing[faction] = max(-100, min(100, st.session_state.faction_standing[faction] + delta))
                
    elf_fav = st.session_state.faction_standing.get('Elves', 0)
    risk_offset = - (elf_fav * 0.3)
    st.session_state.world_data = generate_world(dynamic_risk_offset=risk_offset)
    
    st.session_state.turn_log.append(f"Turn {st.session_state.turn - 1}: {action_name}")

def move_player(dx: int, dz: int):
    st.session_state.player_x = max(0, min(48, st.session_state.player_x + dx))
    st.session_state.player_z = max(0, min(48, st.session_state.player_z + dz))
    st.session_state.message = f"Traveled to coordinates ({st.session_state.player_x}, {st.session_state.player_z})."
    process_turn_advance("Exploration Movement")

def execute_rest():
    if st.session_state.gold >= 15:
        st.session_state.message = "Rested at camp. Restored +30 Health."
        process_turn_advance("Camp Rest", health_delta=30, gold_delta=-15)
    else:
        st.session_state.message = "Not enough gold to set up a secure camp!"

def execute_attack():
    hit_target = None
    world = st.session_state.world_data
    for c in world['creatures']:
        if c['alive'] and abs(c['x'] - st.session_state.player_x) <= 4 and abs(c['z'] - st.session_state.player_z) <= 4:
            hit_target = c
            break
    if hit_target:
        dmg = random.randint(20, 35)
        hit_target['hp'] -= dmg
        if hit_target['hp'] <= 0:
            hit_target['alive'] = False
            st.session_state.kills += 1
            st.session_state.message = f"Successfully vanquished {hit_target['name']}! Looted 35 Gold."
            process_turn_advance(f"Defeated {hit_target['name']}", gold_delta=35, faction_updates={'Dragons': -5})
        else:
            st.session_state.message = f"Struck {hit_target['name']} for {dmg} damage!"
            process_turn_advance(f"Attacked {hit_target['name']}")
    else:
        st.session_state.message = "No targets within weapon range."

def execute_talk():
    world = st.session_state.world_data
    talked = False
    for c in world['creatures']:
        if c['alive'] and c['type'] == 'npc' and abs(c['x'] - st.session_state.player_x) <= 4 and abs(c['z'] - st.session_state.player_z) <= 4:
            dialogue = random.choice(c['dialogues'])
            st.session_state.message = f"{c['name']}: \"{dialogue}\""
            talked = True
            break
    if not talked:
        st.session_state.message = "No NPCs nearby to talk to."
    else:
        process_turn_advance("NPC Conversation", faction_updates={'Fairies': 5})

world = st.session_state.world_data 

# ============================================================ 
# STREAMLIT USER INTERFACE LAYOUT
# ============================================================ 

st.title("🐉 Dragon Realm: SCRCAE Explorer")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("World Navigation & Action Controls")
    st.info(st.session_state.message)
    
    # Low-Level Graphics & Physics Viewport (HTML5 Canvas)
    canvas_html = f"""
    <div style="background: #12121e; border: 1px solid #33334d; border-radius: 8px; padding: 10px; text-align: center;">
        <canvas id="gameCanvas" width="450" height="220" style="background: #06060c; border-radius: 4px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8);"></canvas>
        <p style="color: #8888aa; font-size: 12px; margin-top: 6px; font-family: monospace;">
            LIVE RADAR: Player Position X:{st.session_state.player_x} | Z:{st.session_state.player_z}
        </p>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        let px = {st.session_state.player_x} * 9;
        let pz = {st.session_state.player_z} * 4.4;
        
        // Particle system for ambient magic physics
        let particles = [];
        for(let i=0; i<30; i++) {{
            particles.push({{
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.8,
                vy: (Math.random() - 0.5) * 0.8,
                radius: Math.random() * 2 + 1,
                color: ['#ff4b4b', '#4b9fff', '#b04bff'][Math.floor(Math.random() * 3)]
            }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid lines
            ctx.strokeStyle = '#1a1a2e';
            ctx.lineWidth = 1;
            for(let x=0; x<canvas.width; x+=30) {{
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }}
            for(let y=0; y<canvas.height; y+=30) {{
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }}
            
            // Update & draw magic physics particles
            for(let p of particles) {{
                p.x += p.vx;
                p.y += p.vy;
                if(p.x < 0) p.x = canvas.width;
                if(p.x > canvas.width) p.x = 0;
                if(p.y < 0) p.y = canvas.height;
                if(p.y > canvas.height) p.y = 0;
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
            }}
            
            // Draw Player Node with glowing aura
            ctx.beginPath();
            ctx.arc(px, pz, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#00ffcc';
            ctx.shadowBlur = 12;
            ctx.shadowColor = '#00ffcc';
            ctx.fill();
            ctx.shadowBlur = 0;
            
            requestAnimationFrame(draw);
        }}
        draw();
    </script>
    """
    components.html(canvas_html, height=270)

    # Movement Matrix using Callbacks
    c1, c2, c3 = st.columns(3)
    c2.button("⬆️ Move North", use_container_width=True, on_click=move_player, args=(0, -2))
    
    c4, c5, c6 = st.columns(3)
    c4.button("⬅️ Move West", use_container_width=True, on_click=move_player, args=(-2, 0))
    c6.button("➡️ Move East", use_container_width=True, on_click=move_player, args=(2, 0))
    
    c7, c8, c9 = st.columns(3)
    c8.button("⬇️ Move South", use_container_width=True, on_click=move_player, args=(0, 2))

    st.markdown("---")
    
    ac1, ac2, ac3 = st.columns(3)
    ac1.button("⚔️ Attack Target", use_container_width=True, on_click=execute_attack)
    ac2.button("💬 Talk / Interact", use_container_width=True, on_click=execute_talk)
    ac3.button("⛺ Rest (15 G)", use_container_width=True, on_click=execute_rest)

with col2:
    st.subheader("Player Status")
    st.metric("Turn", st.session_state.turn)
    st.metric("Health", f"{st.session_state.health} / {st.session_state.max_health}")
    st.metric("Gold", f"{st.session_state.gold} G")
    st.metric("Kills", st.session_state.kills)
    st.markdown(f"**Coordinates:** X: {st.session_state.player_x}, Z: {st.session_state.player_z}")
    
    current_biome = next((b for b in world['biomes'] if abs(b['x'] - st.session_state.player_x) <= 2 and abs(b['z'] - st.session_state.player_z) <= 2), None)
    if current_biome:
        st.markdown(f"**Biome:** {current_biome['biome'].capitalize()}")
        st.markdown(f"**Magic Affinity:** {current_biome['magic_element'].upper()} ({current_biome['magic_strength']*105:.0f}%)")
        if current_biome['poi']:
            st.warning(f"📍 Landmark: {current_biome['poi']['name']} ({current_biome['poi']['type'].replace('_', ' ').title()})")

# Sidebar Optimization Metrics
with st.sidebar:
    st.markdown("## 🛡️ SCRCAE Engine Feed")
    opt = world['optimization_result']
    st.markdown(f"**Status:** {opt['status']}")
    st.markdown(f"**Objective NPV:** ${opt['objective']:,.0f}")
    st.markdown(f"**Risk Reduction:** {opt['risk_reduction']:.2f} pts")
    
    st.markdown("### Faction Standings")
    for faction, score in st.session_state.faction_standing.items():
        st.write(f"**{faction}**: {score} pts")
        st.progress((score + 100) / 200)

    st.markdown("### Active Bundles")
    if opt['active_bundles']:
        for b in opt['active_bundles']:
            st.code(b)
    else:
        st.caption("None active yet")
