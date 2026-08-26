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
            terrain[x][z] = ((terrain[x][z] - min_val) / (max_val - min_val)) * 10    
            
    magic = MagicSystem.generate_magic_grid(50)    
    biomes = []    
    for x in range(0, 50, 2):    
        for z in range(0, 50, 2):    
            height = terrain[x][z]    
            if height > 7: biome = 'mountain'    
            elif height > 4: biome = 'forest'    
            elif height > 2: biome = 'plains'    
            elif height > 1: biome = 'swamp'    
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
            count = max(1, int(alloc['scale'] * 4))    
            suitable = [b for b in biomes if b['biome'] == sp['biome']]    
            for i in range(count):    
                if suitable:    
                    loc = random.choice(suitable)    
                    creatures.append({    
                        'name': sp['name'], 'x': loc['x'], 'z': loc['z'], 'height': loc['height'],
                        'stats': {'speed': sp['speed'], 'strength': sp['strength'], 'magic': sp['magic'], 'stealth': sp['stealth']},    
                        'element': loc['magic_element'], 'hp': sp['hp'], 'max_hp': sp['hp'], 'alive': True,    
                        'scale': round(alloc['scale'], 3), 'type': 'enemy'    
                    })    
                    
    devil_biome = random.choice([b for b in biomes if b['biome'] == 'mountain' or b['biome'] == 'forest'])    
    creatures.append({    
        'name': 'Devil', 'x': devil_biome['x'], 'z': devil_biome['z'], 'height': devil_biome['height'],
        'stats': {'speed': 7, 'strength': 9, 'magic': 10, 'stealth': 5},    
        'element': 'shadow', 'hp': 200, 'max_hp': 200, 'alive': True,    
        'scale': 1.0, 'type': 'npc',    
        'dialogues': [    
            "I am the Devil of this realm. Fear not, I mean you no harm.",    
            "The dragon power grows. You must stop it.",    
            "I can teach you forbidden magic... for a price.",    
            "The shadows whisper of an ancient evil awakening."  
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
        st.session_state.message = "Immersive 3D Fantasy Realm loaded successfully!"
        st.session_state.faction_standing = {'Dragons': -10, 'Elves': 20, 'Goblins': -5, 'Fairies': 30}
        st.session_state.turn_log = []
        st.session_state.world_data = generate_world()
        st.session_state.attack_nonce = 0  # Persistent counter to force animation triggers

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
    
    # Increment attack nonce so the 3D canvas detects a fresh animation trigger every single time
    st.session_state.attack_nonce += 1
    
    if hit_target:
        dmg = random.randint(25, 45)
        hit_target['hp'] -= dmg
        if hit_target['hp'] <= 0:
            hit_target['alive'] = False
            st.session_state.kills += 1
            st.session_state.message = f"⚔️ Vanquished {hit_target['name']} with a brutal strike! Blood splattered everywhere. Looted 40 Gold."
            process_turn_advance(f"Defeated {hit_target['name']}", gold_delta=40, faction_updates={'Dragons': -8})
        else:
            st.session_state.message = f"⚔️ Struck {hit_target['name']} for {dmg} damage, causing a blood splatter! ({hit_target['hp']} HP left)"
            process_turn_advance(f"Attacked {hit_target['name']}")
    else:
        st.session_state.message = "⚠️ Swung blade at empty air! No targets within range."

def execute_magic():
    world = st.session_state.world_data
    if st.session_state.gold >= 10:
        st.session_state.message = "✨ Cast Arcane Nova! Damaged all nearby entities with magical feedback."
        for c in world['creatures']:
            if c['alive'] and abs(c['x'] - st.session_state.player_x) <= 6 and abs(c['z'] - st.session_state.player_z) <= 6:
                c['hp'] -= 40
                if c['hp'] <= 0:
                    c['alive'] = False
                    st.session_state.kills += 1
        process_turn_advance("Cast Spell", gold_delta=-10, faction_updates={'Fairies': 10})
    else:
        st.session_state.message = "⚠️ Not enough gold/mana essence to cast spells!"

world = st.session_state.world_data 

# ============================================================ 
# STREAMLIT USER INTERFACE LAYOUT
# ============================================================ 

st.title("🐉 Dragon Realm: Fantasy 3D World")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive 3D Realm Viewport")
    st.info(st.session_state.message)
    
    terrain_json = json.dumps(world['terrain'])
    creatures_json = json.dumps([{
        'name': c['name'], 'x': c['x'], 'z': c['z'], 'height': c.get('height', 0), 
        'alive': c['alive'], 'type': c['type'], 'hp': c['hp']
    } for c in world['creatures']])
    attack_nonce = st.session_state.attack_nonce

    # 3D Engine with explicit nonced trigger check
    three_html = f"""
    <div style="background: #05050a; border: 1px solid #2a2a40; border-radius: 8px; padding: 10px; text-align: center;">
        <div id="canvas-container" style="width: 100%; height: 320px; border-radius: 6px; overflow: hidden; box-shadow: inset 0 0 25px rgba(0,0,0,0.9);"></div>
        <p style="color: #00ffcc; font-size: 12px; margin-top: 8px; font-family: monospace;">
            3D REALM ENGINE: Player X:{st.session_state.player_x} | Z:{st.session_state.player_z} | Kills: {st.session_state.kills}
        </p>
    </div>
    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.0/build/three.module.js';

        const container = document.getElementById('canvas-container');
        const width = container.clientWidth;
        const height = container.clientHeight;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x05050f);
        scene.fog = new THREE.FogExp2(0x05050f, 0.035);

        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(width, height);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0x333355, 1.8);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 2.5);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);

        const terrainData = {terrain_json};
        const size = 50;
        const geometry = new THREE.PlaneGeometry(35, 35, size - 1, size - 1);
        geometry.rotateX(-Math.PI / 2);

        const pos = geometry.attributes.position;
        for (let i = 0; i < pos.count; i++) {{
            const ix = Math.floor(i / size);
            const iz = i % size;
            if (terrainData[ix] && terrainData[ix][iz] !== undefined) {{
                pos.setY(i, terrainData[ix][iz] * 0.4);
            }}
        }}
        geometry.computeVertexNormals();

        const terrainMat = new THREE.MeshStandardMaterial({{ 
            color: 0x1a3a2a, 
            roughness: 0.8, 
            metalness: 0.1,
            flatShading: true
        }});
        const terrainMesh = new THREE.Mesh(geometry, terrainMat);
        scene.add(terrainMesh);

        const pX = ({st.session_state.player_x} - 24) * 0.7;
        const pZ = ({st.session_state.player_z} - 24) * 0.7;
        let pY = 1.0;
        if (terrainData[{st.session_state.player_x}] && terrainData[{st.session_state.player_x}][{st.session_state.player_z}] !== undefined) {{
            pY = terrainData[{st.session_state.player_x}][{st.session_state.player_z}] * 0.4 + 0.8;
        }}

        const playerGeo = new THREE.OctahedronGeometry(0.7, 0);
        const playerMat = new THREE.MeshStandardMaterial({{ color: 0x00ffcc, emissive: 0x005544, roughness: 0.1, metalness: 0.9 }});
        const playerMesh = new THREE.Mesh(playerGeo, playerMat);
        playerMesh.position.set(pX, pY, pZ);
        scene.add(playerMesh);

        const creaturesData = {creatures_json};
        const attackNonce = {attack_nonce};
        
        // Track the last seen attack nonce in session storage to guarantee it animates on change
        const lastNonce = sessionStorage.getItem('last_attack_nonce') || '0';
        const doAttackAnim = attackNonce > parseInt(lastNonce);
        if (doAttackAnim) {{
            sessionStorage.setItem('last_attack_nonce', attackNonce.toString());
        }}

        let bloodParticles = null;

        creaturesData.forEach(c => {{
            const cx = (c.x - 24) * 0.7;
            const cz = (c.z - 24) * 0.7;
            const cy = (c.height * 0.4) + 0.6;

            const group = new THREE.Group();

            if (c.name === 'Dragon') {{
                const bodyMat = new THREE.MeshStandardMaterial({{ color: c.alive ? 0xff4500 : 0x441100, roughness: 0.3, metalness: 0.4 }});
                const body = new THREE.Mesh(new THREE.ConeGeometry(0.6, 1.4, 6), bodyMat);
                body.rotation.x = Math.PI / 2;
                group.add(body);
            }} else {{
                const beastColor = c.alive ? 0xcc3333 : 0x551111;
                const beastMat = new THREE.MeshStandardMaterial({{ color: beastColor, roughness: 0.6 }});
                const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.25, 0.5, 4, 8), beastMat);
                torso.rotation.x = Math.PI / 2;
                torso.position.y = 0.3;
                group.add(torso);
            }}

            if (!c.alive) {{
                group.rotation.z = Math.PI / 2;
                group.position.set(cx, cy - 0.4, cz);
            }} else {{
                group.position.set(cx, cy, cz);
            }}
            scene.add(group);
        }});

        if (doAttackAnim) {{
            let targetX = pX, targetZ = pZ + 1.5;
            creaturesData.forEach(c => {{
                if (c.alive && c.type === 'enemy') {{
                    targetX = (c.x - 24) * 0.7;
                    targetZ = (c.z - 24) * 0.7;
                }}
            }});

            const pCount = 50;
            const bloodGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(pCount * 3);
            const velocities = [];

            for (let i = 0; i < pCount * 3; i += 3) {{
                positions[i] = targetX;
                positions[i + 1] = pY + 0.5;
                positions[i + 2] = targetZ;
                velocities.push({{
                    x: (Math.random() - 0.5) * 0.3,
                    y: Math.random() * 0.3 + 0.1,
                    z: (Math.random() - 0.5) * 0.3
                }});
            }}
            bloodGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const bloodMat = new THREE.PointsMaterial({{ color: 0xff0000, size: 0.25, transparent: true, opacity: 1.0 }});
            bloodParticles = new THREE.Points(bloodGeo, bloodMat);
            scene.add(bloodParticles);
            window.bloodVelocities = velocities;
        }}

        camera.position.set(pX, pY + 4, pZ + 7);
        camera.lookAt(pX, pY, pZ);

        let animStep = 0;
        function animate() {{
            requestAnimationFrame(animate);
            animStep += 0.08;

            if (doAttackAnim && animStep < Math.PI * 1.5) {{
                playerMesh.position.z = pZ - Math.sin(animStep) * 1.5;
                playerMesh.rotation.y += 0.2;
            }} else {{
                playerMesh.rotation.y += 0.03;
                playerMesh.position.y = pY + Math.sin(Date.now() * 0.003) * 0.2;
            }}

            if (bloodParticles) {{
                const posArr = bloodParticles.geometry.attributes.position.array;
                const vels = window.bloodVelocities;
                for (let i = 0; i < vels.length; i++) {{
                    posArr[i * 3] += vels[i].x;
                    posArr[i * 3 + 1] += vels[i].y;
                    posArr[i * 3 + 2] += vels[i].z;
                    vels[i].y -= 0.015;
                }}
                bloodParticles.geometry.attributes.position.needsUpdate = true;
                bloodParticles.material.opacity -= 0.015;
            }}

            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_html, height=360)

    c1, c2, c3 = st.columns(3)
    c2.button("⬆️ Move North", use_container_width=True, on_click=move_player, args=(0, -2))
    
    c4, c5, c6 = st.columns(3)
    c4.button("⬅️ Move West", use_container_width=True, on_click=move_player, args=(-2, 0))
    c6.button("➡️ Move East", use_container_width=True, on_click=move_player, args=(2, 0))
    
    c7, c8, c9 = st.columns(3)
    c8.button("⬇️ Move South", use_container_width=True, on_click=move_player, args=(0, 2))

    st.markdown("---")
    
    ac1, ac2, ac3 = st.columns(3)
    ac1.button("⚔️ Attack Enemy", use_container_width=True, on_click=execute_attack)
    ac2.button("✨ Cast Magic Spell", use_container_width=True, on_click=execute_magic)
    ac3.button("⛺ Rest & Recover (15G)", use_container_width=True, on_click=execute_rest)

with col2:
    st.subheader("Player Status")
    st.metric("Turn", st.session_state.turn)
    st.metric("Health", f"{st.session_state.health} / {st.session_state.max_health}")
    st.metric("Gold", f"{st.session_state.gold} G")
    st.metric("Vanquished", st.session_state.kills)
    st.markdown(f"**Coordinates:** X: {st.session_state.player_x}, Z: {st.session_state.player_z}")
    
    current_biome = next((b for b in world['biomes'] if abs(b['x'] - st.session_state.player_x) <= 2 and abs(b['z'] - st.session_state.player_z) <= 2), None)
    if current_biome:
        st.markdown(f"**Biome:** {current_biome['biome'].capitalize()}")
        st.markdown(f"**Magic Affinity:** {current_biome['magic_element'].upper()} ({current_biome['magic_strength']*105:.0f}%)")
        if current_biome['poi']:
            st.warning(f"📍 Landmark: {current_biome['poi']['name']}")

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
