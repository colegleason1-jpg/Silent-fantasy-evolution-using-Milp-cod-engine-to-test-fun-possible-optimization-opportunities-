import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random

def creature_key(creature):
    return creature.get('id') or f"{creature.get('type', '')}|{creature.get('name', '')}|{creature.get('x', '')}|{creature.get('z', '')}"

def get_live_creatures():
    creatures = st.session_state.get('creatures', [])
    defeated_keys = st.session_state.get('defeated_enemy_keys', set())
    keep_defeated_until = st.session_state.get('keep_defeated_until_quest', 100)
    current_quest = st.session_state.get('quest_stage', 1)
    if current_quest >= keep_defeated_until:
        defeated_keys = set()
        st.session_state.defeated_enemy_keys = defeated_keys
    st.session_state.creatures = [
        c for c in creatures
        if c.get('type') == 'npc' or (c.get('hp', 0) > 0 and creature_key(c) not in defeated_keys)
    ]
    if 'world_data' in st.session_state:
        st.session_state.world_data['creatures'] = st.session_state.creatures
    return st.session_state.creatures

def remove_creature_from_world(target):
    target['alive'] = False
    target['hp'] = 0
    if 'defeated_enemy_keys' not in st.session_state:
        st.session_state.defeated_enemy_keys = set()
    target_key = creature_key(target)
    st.session_state.defeated_enemy_keys.add(target_key)
    st.session_state.creatures = [
        c for c in st.session_state.get('creatures', [])
        if creature_key(c) != target_key
    ]
    if 'world_data' in st.session_state:
        st.session_state.world_data['creatures'] = st.session_state.creatures


st.set_page_config(page_title="KILLGOD", page_icon="✝️", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin: 0; padding: 0; background: #080404; color: #fff;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1.5rem; padding-right: 1.5rem;}
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
        return "All divine constraints satisfied"

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
# MAGIC SYSTEM & WORLD GENERATION (MYTHIC / BIBLICAL ENTITIES)
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
        Intervention("PR", "Minor Prophet", "Seers guarding holy realms", 50000.0, 90.0, 30.0, 200.0),    
        Intervention("ZE", "Zealot", "Fanatical temple guards", 10000.0, 20.0, 8.0, 30.0),    
        Intervention("NE", "Nephilim", "Ancient giant hybrid warriors", 30000.0, 60.0, 15.0, 10.0),    
        Intervention("CS", "Cherubim Sentinel", "Winged guardians of the divine", 8000.0, 15.0, 5.0, 20.0),    
        Intervention("BE", "Behemoth", "Mythic beast of the land", 12000.0, 25.0, 6.0, 40.0),    
        Intervention("SE", "Seraphim", "Fiery six-winged celestial beings", 20000.0, 70.0, 20.0, 5.0),    
    )    
    dependencies = (Dependency("NE", "CS"), Dependency("PR", "NE"))    
    bundles = (Bundle("Heavenly_Host", 15000.0, ("NE", "CS")), Bundle("Divine_Wrath", 25000.0, ("PR", "NE")))    
    prices = PriceBook(5000.0, 1000.0, 50.0, 5, 0.10, "game-calibrated")    
    
    network = SupplyNetwork(100.0 + dynamic_risk_offset, species_interventions, dependencies, bundles)    
    gold_val = st.session_state.get('gold', 150)
    result = solve(OptimizationRequest(network=network, objective=MonetaryNPVObjective(prices=prices), risk_response=AllocationConcaveResponse(exponent=0.85), budget=float(gold_val + 100000.0)))    
    
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
                poi = {'type': 'holy_sanctuary', 'name': 'Mount Sinai Shrine', 'element': dom_element}    
            elif biome == 'forest' and dom_strength > 0.5:    
                poi = {'type': 'eden_grove', 'name': 'Edenic Outpost', 'element': dom_element}    
            elif biome == 'swamp' and dom_strength > 0.4:    
                poi = {'type': 'abyss_rift', 'name': 'Gehenna Depths', 'element': dom_element}    
            biomes.append({'x': x, 'z': z, 'height': round(height, 1), 'biome': biome,    
                          'magic_element': dom_element, 'magic_strength': round(dom_strength, 2), 'poi': poi})    
            
    creatures = []    
    species_map = {    
        'PR': {'name': 'Minor Prophet', 'biome': 'mountain', 'speed': 8, 'strength': 10, 'magic': 9, 'stealth': 3, 'hp': 2},    
        'ZE': {'name': 'Zealot', 'biome': 'swamp', 'speed': 4, 'strength': 3, 'magic': 2, 'stealth': 7, 'hp': 1},    
        'NE': {'name': 'Nephilim', 'biome': 'forest', 'speed': 6, 'strength': 4, 'magic': 8, 'stealth': 6, 'hp': 2},    
        'CS': {'name': 'Cherubim Sentinel', 'biome': 'plains', 'speed': 7, 'strength': 5, 'magic': 1, 'stealth': 8, 'hp': 2},    
        'BE': {'name': 'Behemoth', 'biome': 'forest', 'speed': 3, 'strength': 8, 'magic': 1, 'stealth': 4, 'hp': 3},    
        'SE': {'name': 'Seraphim', 'biome': 'forest', 'speed': 9, 'strength': 1, 'magic': 10, 'stealth': 9, 'hp': 2}    
    }    
    for node_id, alloc in species_allocations.items():    
        if node_id in species_map:    
            sp = species_map[node_id]    
            count = max(2, int(alloc['scale'] * 5))    
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
    
    # GUARANTEED STARTING ENEMIES NEAR PLAYER SPAWN (24, 24) FOR QUEST 1 COMPLETION
    starter_offsets = [(2, 0), (-2, 2), (0, -2)]
    starter_types = ['Zealot', 'Cherubim Sentinel', 'Zealot']
    for idx, (ox, oz) in enumerate(starter_offsets):
        sx = max(0, min(48, 24 + ox))
        sz = max(0, min(48, 24 + oz))
        s_height = terrain[sx][sz]
        creatures.append({
            'id': f"starter-{idx}-{sx}-{sz}",
            'name': starter_types[idx], 'x': sx, 'z': sz, 'height': round(s_height, 1),
            'stats': {'speed': 5, 'strength': 4, 'magic': 3, 'stealth': 5},
            'element': 'light', 'hp': 1, 'max_hp': 1, 'alive': True,
            'scale': 0.5, 'type': 'enemy'
        })
                    
    oracle_biome = random.choice([b for b in biomes if b['biome'] == 'mountain' or b['biome'] == 'forest'])    
    creatures.append({    
        'name': 'The Devil (Protagonist)', 'x': oracle_biome['x'], 'z': oracle_biome['z'], 'height': oracle_biome['height'],
        'stats': {'speed': 7, 'strength': 9, 'magic': 10, 'stealth': 5},    
        'element': 'shadow', 'hp': 999, 'max_hp': 999, 'alive': True,    
        'scale': 1.0, 'type': 'npc',    
        'dialogues': [    
            "The heavenly gates stand guarded. We strike the prophets down first.",    
            "Gather dark souls and ascend the mountain. God awaits our judgment.",    
            "Your dark magic grows stronger. Unleash hellfire upon the righteous.",    
            "The angels tremble. Keep marching forward."  
        ]    
    })    

    # JESUS: ENDGAME PROTECTOR (WILL BE TOUGH TO KILL BEFORE FACING GOD)
    jesus_biome = random.choice([b for b in biomes if b['biome'] == 'mountain'])
    creatures.append({
        'id': 'boss-jesus-protector',
        'name': 'Jesus (Protector of Heaven)', 'x': jesus_biome['x'], 'z': jesus_biome['z'], 'height': jesus_biome['height'],
        'stats': {'speed': 9, 'strength': 10, 'magic': 10, 'stealth': 10},
        'element': 'light', 'hp': 10, 'max_hp': 10, 'alive': True,
        'scale': 1.2, 'type': 'boss'
    })

    return {    
        'terrain': terrain, 'magic_grid': magic, 'biomes': biomes, 'creatures': creatures,    
        'optimization_result': {'status': result.status, 'objective': result.objective_value,    
                               'risk_reduction': result.risk_reduction_pts,    
                               'active_bundles': list(result.active_bundles)}    
    }

# ============================================================    
# STREAMLIT STATE INITIALIZATION & MEMORY
# ============================================================    

def init_game_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.turn = 1
        st.session_state.health = 100
        st.session_state.max_health = 100
        st.session_state.gold = 150
        st.session_state.kills = 0
        st.session_state.quest_stage = 1
        st.session_state.player_x = 24
        st.session_state.player_z = 24
        st.session_state.render_counter = 0  
        st.session_state.message = "KILLGOD Campaign Initialized: Strike down the holy vanguard surrounding your spawn point!"
        st.session_state.faction_standing = {'Heavenly Host': -50, 'Prophets': -30, 'Nephilim': 10, 'Demonic Legions': 50}
        st.session_state.turn_log = []
        
        world = generate_world()
        st.session_state.world_data = world
        st.session_state.creatures = world['creatures']
        
        st.session_state.active_quest = "Chapter 1: Slay 3 holy zealots or sentinels near spawn."
        st.session_state.quest_target_kills = 3

init_game_state()

def check_quest_progress():
    if st.session_state.kills >= 3 and st.session_state.quest_stage == 1:
        st.session_state.quest_stage = 2
        st.session_state.active_quest = "Chapter 2: Breach higher mountain ranges and defeat 4 Nephilim, Prophets, or Sentinels."
        st.session_state.quest_target_kills = 7
        st.session_state.message = "⚡ Chapter 2 Unlocked: The higher celestial forces mobilize against you!"
    elif st.session_state.kills >= 7 and st.session_state.quest_stage == 2:
        st.session_state.quest_stage = 3
        st.session_state.active_quest = "Chapter 3: Defeat Jesus, the Protector of Heaven, to reach God."
        st.session_state.quest_target_kills = 8
        st.session_state.message = "👑 Chapter 3 Unlocked: Jesus descends to protect the gates! Defeat him to reach God."

def process_turn_advance(action_name: str, health_delta=0, gold_delta=0, faction_updates=None):
    st.session_state.turn += 1
    st.session_state.render_counter += 1  
    st.session_state.health = max(0, min(st.session_state.max_health, st.session_state.health + health_delta))
    st.session_state.gold = max(0, st.session_state.gold + gold_delta)    
    if faction_updates:
        for faction, delta in faction_updates.items():
            if faction in st.session_state.faction_standing:
                st.session_state.faction_standing[faction] = max(-100, min(100, st.session_state.faction_standing[faction] + delta))
                
    st.session_state.turn_log.append(f"Turn {st.session_state.turn - 1}: {action_name}")
    if 'world_data' in st.session_state:
        st.session_state.world_data['creatures'] = st.session_state.creatures
    check_quest_progress()

world = st.session_state.world_data 

# ============================================================ 
# STREAMLIT USER INTERFACE LAYOUT 
# ============================================================ 

st.markdown("### ✝️ KILLGOD: The Divine Crusade")

col1, col2 = st.columns([2.3, 1])

with col1:
    st.info(st.session_state.message)
    
    terrain_json = json.dumps(world['terrain'])
    
    active_creatures_for_render = get_live_creatures()
    creatures_json = json.dumps([{
        'id': c.get('id', creature_key(c)),
        'name': c['name'], 'x': c['x'], 'z': c['z'], 'height': c.get('height', 0), 
        'alive': c['alive'], 'type': c['type'], 'hp': c['hp'], 'max_hp': c['max_hp']
    } for c in active_creatures_for_render])

    # We encode the render counter directly inside an HTML comment / dynamic token in the string 
    # to guarantee a complete refresh of the markup iframe without using the unsupported key parameter.
    three_html = f"""
    <!-- render_id: {st.session_state.render_counter} -->
    <div style="background: #05050a; border: 1px solid #3a1a1a; border-radius: 6px; padding: 4px; text-align: center; position: relative;">
        <div id="canvas-container" style="width: 100%; height: 280px; border-radius: 4px; overflow: hidden; box-shadow: inset 0 0 20px rgba(0,0,0,0.9); position: relative;">
            <div id="labels-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; overflow: hidden;"></div>
        </div>
        <div style="margin-top: 8px; display: flex; justify-content: center; gap: 8px;">
            <button id="btn-attack" style="background:#cc2222; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">⚔️ Dark Strike (Nearest)</button>
            <button id="btn-magic" style="background:#8800ff; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">🔮 Hellfire Blast</button>
            <button id="btn-rest" style="background:#333344; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">🌑 Dark Ritual (20G)</button>
        </div>
        <p style="color: #ff4444; font-size: 10px; margin: 4px 0 0 0; font-family: monospace;">
            CHAPTER: {st.session_state.quest_stage} | POS X:{st.session_state.player_x} | Z:{st.session_state.player_z} | SOULS HARVESTED: {st.session_state.kills}
        </p>
    </div>
    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.0/build/three.module.js';

        const container = document.getElementById('canvas-container');
        const labelsContainer = document.getElementById('labels-overlay');
        const width = container.clientWidth;
        const height = container.clientHeight;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0404);
        scene.fog = new THREE.FogExp2(0x0a0404, 0.035);

        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(width, height);
        renderer.shadowMap.enabled = true;
        container.insertBefore(renderer.domElement, labelsContainer);

        const ambientLight = new THREE.AmbientLight(0x442233, 1.8);
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
            color: 0x221115, 
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

        const playerGeo = new THREE.ConeGeometry(0.6, 1.5, 5);
        const playerMat = new THREE.MeshStandardMaterial({{ color: 0xff0044, emissive: 0x660011, roughness: 0.1, metalness: 0.9 }});
        const playerMesh = new THREE.Mesh(playerGeo, playerMat);
        playerMesh.position.set(pX, pY, pZ);
        scene.add(playerMesh);

        const creaturesData = {creatures_json};
        const trackedEntities = [];
        
        let bloodParticles = null;
        let fireballMesh = null;
        let targetEnemyGroup = null;

        let targetEnemyX = pX;
        let targetEnemyZ = pZ;
        let targetEnemyY = pY;
        let targetIsKilled = false;
        let hasValidTarget = false;
        let minDist = Infinity;

        creaturesData.forEach((c, idx) => {{
            const cx = (c.x - 24) * 0.7;
            const cz = (c.z - 24) * 0.7;
            const cy = (c.height * 0.4) + 0.6;
            const group = new THREE.Group();

            if (c.type === 'npc') {{
                const npcMat = new THREE.MeshStandardMaterial({{ color: 0xffcc00, roughness: 0.2, emissive: 0x665500 }});
                const npcMesh = new THREE.Mesh(new THREE.SphereGeometry(0.5, 12, 12), npcMat);
                npcMesh.position.y = 0.5;
                group.add(npcMesh);
            }} else if (c.type === 'boss') {{
                const bossMat = new THREE.MeshStandardMaterial({{ color: 0x00ffff, roughness: 0.2, emissive: 0x005555 }});
                const bossMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.5, 1.8, 8), bossMat);
                bossMesh.position.y = 0.9;
                group.add(bossMesh);
            }} else {{
                const enemyMat = new THREE.MeshStandardMaterial({{ color: 0xeeaa33, roughness: 0.5 }});
                const body = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 1.2, 6), enemyMat);
                body.position.y = 0.6;
                group.add(body);
            }}

            group.position.set(cx, cy, cz);
            scene.add(group);

            const labelEl = document.createElement('div');
            labelEl.className = 'entity-label';
            const badgeColor = c.type === 'npc' ? '#ffcc00' : (c.type === 'boss' ? '#00ffff' : '#ff4444');
            labelEl.innerHTML = `<span style="background: rgba(0,0,0,0.85); color: ${{badgeColor}}; border: 1px solid ${{badgeColor}}; padding: 1px 5px; border-radius: 3px; font-size: 9px; font-family: monospace; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">${{c.name}} ${{c.type !== 'npc' ? '(' + c.hp + '/' + c.max_hp + 'HP)' : ''}}</span>`;
            labelEl.style.position = 'absolute';
            labelEl.style.transform = 'translate(-50%, -100%)';
            labelsContainer.appendChild(labelEl);

            trackedEntities.push({{ group: group, element: labelEl, heightOffset: c.type === 'npc' ? 1.2 : 1.8 }});

            if (c.type === 'enemy' || c.type === 'boss') {{
                const dist = Math.hypot(cx - pX, cz - pZ);
                if (dist < minDist && dist <= 14.0) {{
                    minDist = dist;
                    targetEnemyX = cx;
                    targetEnemyZ = cz;
                    targetEnemyY = cy;
                    targetEnemyGroup = group;
                    targetIsKilled = (c.hp <= 1); 
                    hasValidTarget = true;
                }}
            }}
        }});

        function triggerEnhancedBloodSplatter(x, y, z) {{
            const pCount = 200;
            const bloodGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(pCount * 3);
            const velocities = [];

            for (let i = 0; i < pCount * 3; i += 3) {{
                positions[i] = x + (Math.random() - 0.5) * 0.2;
                positions[i + 1] = y + 0.4 + (Math.random() - 0.5) * 0.2;
                positions[i + 2] = z + (Math.random() - 0.5) * 0.2;
                
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 0.6 + 0.2;
                velocities.push({{
                    x: Math.cos(angle) * speed,
                    y: Math.random() * 0.8 + 0.4,
                    z: Math.sin(angle) * speed
                }});
            }}
            bloodGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            
            const bloodMat = new THREE.PointsMaterial({{ color: 0xffaa00, size: 0.3, transparent: true, opacity: 1.0 }});
            bloodParticles = new THREE.Points(bloodGeo, bloodMat);
            scene.add(bloodParticles);
            window.bloodVelocities = velocities;
        }}

        camera.position.set(pX, pY + 4, pZ + 6.5);
        camera.lookAt(pX, pY, pZ);

        let isAnimating = false;
        let animType = null;
        let animStep = 0;
        let magicStep = 0;
        let dieStep = 0;

        document.getElementById('btn-attack').addEventListener('click', () => {{
            if (isAnimating || !hasValidTarget) return;
            isAnimating = true;
            animType = 'attack';
            animStep = 0;
        }});

        document.getElementById('btn-magic').addEventListener('click', () => {{
            if (isAnimating || !hasValidTarget) return;
            isAnimating = true;
            animType = 'magic';
            magicStep = 0;
            const fbGeo = new THREE.SphereGeometry(0.45, 12, 12);
            const fbMat = new THREE.MeshBasicMaterial({{ color: 0x9900ff }});
            fireballMesh = new THREE.Mesh(fbGeo, fbMat);
            fireballMesh.position.set(pX, pY + 0.5, pZ);
            scene.add(fireballMesh);
        }});

        document.getElementById('btn-rest').addEventListener('click', () => {{
            if (isAnimating) return;
            isAnimating = true;
            animType = 'rest';
            animStep = 0;
        }});

        function updateLabels() {{
            const wp = new THREE.Vector3();
            trackedEntities.forEach(item => {{
                wp.copy(item.group.position);
                wp.y += item.heightOffset;
                wp.project(camera);

                const x = (wp.x *  .5 + .5) * width;
                const y = (wp.y * -.5 + .5) * height;

                if (wp.z < 1.0 && x >= 0 && x <= width && y >= 0 && y <= height) {{
                    item.element.style.display = 'block';
                    item.element.style.left = `${{x}}px`;
                    item.element.style.top = `${{y}}px`;
                }} else {{
                    item.element.style.display = 'none';
                }}
            }});
        }}

        function animate() {{
            requestAnimationFrame(animate);

            if (isAnimating) {{
                if (animType === 'attack') {{
                    animStep += 0.05;
                    const lungeProg = Math.sin(animStep);
                    if (animStep <= Math.PI) {{
                        playerMesh.position.x = pX + (targetEnemyX - pX) * (lungeProg * 0.6);
                        playerMesh.position.z = pZ + (targetEnemyZ - pZ) * (lungeProg * 0.6);
                    }} else if (animStep <= Math.PI * 2) {{
                        playerMesh.position.x = pX;
                        playerMesh.position.z = pZ;
                    }} else {{
                        triggerEnhancedBloodSplatter(targetEnemyX, targetEnemyY, targetEnemyZ);
                        animType = targetIsKilled ? 'die' : 'done';
                        dieStep = 0;
                    }}
                }} else if (animType === 'magic') {{
                    magicStep += 0.025;
                    if (fireballMesh) {{
                        fireballMesh.position.x = pX + (targetEnemyX - pX) * magicStep;
                        fireballMesh.position.z = pZ + (targetEnemyZ - pZ) * magicStep;
                        fireballMesh.position.y = (pY + 0.5) + (targetEnemyY - (pY + 0.5)) * magicStep + Math.sin(magicStep * Math.PI) * 1.5;
                    }}
                    if (magicStep >= 1.0) {{
                        if (fireballMesh) {{
                            scene.remove(fireballMesh);
                            fireballMesh = null;
                        }}
                        triggerEnhancedBloodSplatter(targetEnemyX, targetEnemyY, targetEnemyZ);
                        animType = targetIsKilled ? 'die' : 'done';
                        dieStep = 0;
                    }}
                }} else if (animType === 'done') {{
                    dieStep += 0.08;
                    if (targetEnemyGroup) {{
                        targetEnemyGroup.traverse(child => {{
                            if (child.material) {{
                                child.material.color.setHex(Math.sin(dieStep * 10) > 0 ? 0xffffff : 0xeeaa33);
                            }}
                        }});
                    }}
                    if (dieStep >= Math.PI) {{
                        isAnimating = false;
                    }}
                }} else if (animType === 'die') {{
                    dieStep += 0.04;
                    if (targetEnemyGroup) {{
                        targetEnemyGroup.rotation.z = Math.min(Math.PI / 2, dieStep * 2);
                        targetEnemyGroup.position.y = Math.max(targetEnemyY - 0.4, targetEnemyY - dieStep * 0.4);
                        targetEnemyGroup.traverse(child => {{
                            if (child.material) {{
                                child.material.transparent = true;
                                child.material.opacity = Math.max(0, 1.0 - dieStep * 1.2);
                            }}
                        }});
                    }}
                    if (dieStep >= 1.2) {{
                        if (targetEnemyGroup) {{
                            scene.remove(targetEnemyGroup);
                        }}
                        isAnimating = false;
                    }}
                }} else if (animType === 'rest') {{
                    animStep += 0.04;
                    playerMesh.position.y = pY + Math.sin(animStep * 3) * 0.5;
                    if (animStep >= Math.PI * 2) {{
                        isAnimating = false;
                    }}
                }}
            }} else {{
                playerMesh.rotation.y += 0.025;
                playerMesh.position.y = pY + Math.sin(Date.now() * 0.003) * 0.15;
            }}

            if (bloodParticles) {{
                const posArr = bloodParticles.geometry.attributes.position.array;
                const vels = window.bloodVelocities;
                for (let i = 0; i < vels.length; i++) {{
                    posArr[i * 3] += vels[i].x;
                    posArr[i * 3 + 1] += vels[i].y;
                    posArr[i * 3 + 2] += vels[i].z;
                    vels[i].y -= 0.02;
                }}
                bloodParticles.geometry.attributes.position.needsUpdate = true;
                bloodParticles.material.opacity -= 0.012;
            }}

            renderer.render(scene, camera);
            updateLabels();
        }}
        animate();
    </script>
    """
    
    # Fixed: Removed the incompatible 'key=' parameter from components.html. 
    # Because `st.session_state.render_counter` is embedded directly into the HTML string, 
    # Streamlit natively treats the HTML payload as updated and re-mounts the iframe safely on every turn.
    components.html(three_html, height=310, scrolling=False)

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc2:
        if st.button("⬆️ North", use_container_width=True):
            st.session_state.player_z = max(0, min(48, st.session_state.player_z - 2))
            process_turn_advance("Crusade Movement (North)")
            st.rerun()
    with mc3:
        if st.button("⬅️ West", use_container_width=True):
            st.session_state.player_x = max(0, min(48, st.session_state.player_x - 2))
            process_turn_advance("Crusade Movement (West)")
            st.rerun()
    with mc4:
        if st.button("➡️ East", use_container_width=True):
            st.session_state.player_x = max(0, min(48, st.session_state.player_x + 2))
            process_turn_advance("Crusade Movement (East)")
            st.rerun()
    with mc5:
        if st.button("⬇️ South", use_container_width=True):
            st.session_state.player_z = max(0, min(48, st.session_state.player_z + 2))
            process_turn_advance("Crusade Movement (South)")
            st.rerun()
            
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("⚔️ Strike (Nearest)", use_container_width=True):
            live_enemies = [c for c in get_live_creatures() if c['type'] in ['enemy', 'boss']]
            if live_enemies:
                live_enemies.sort(key=lambda c: math.hypot(c['x'] - st.session_state.player_x, c['z'] - st.session_state.player_z))
                target = live_enemies[0]
                target_id = creature_key(target)
                dist = math.hypot(target['x'] - st.session_state.player_x, target['z'] - st.session_state.player_z)

                if dist <= 14:
                    backend_target = next((c for c in st.session_state.creatures if creature_key(c) == target_id), None)
                    if backend_target is None:
                        process_turn_advance("Target lock failed; enemy state desynced.", gold_delta=0)
                    else:
                        backend_target['hp'] -= 1
                        if backend_target['hp'] <= 0:
                            slain_name = backend_target['name']
                            remove_creature_from_world(backend_target)
                            st.session_state.kills += 1
                            msg = f"Permanently vanquished {slain_name}! Soul harvested."
                        else:
                            msg = f"Damaged {backend_target['name']}! ({backend_target['hp']}/{backend_target['max_hp']} HP left)"
                        process_turn_advance(msg, gold_delta=25, faction_updates={'Heavenly Host': -5})
                else:
                    process_turn_advance("Target is out of striking range.", gold_delta=0)
            else:
                process_turn_advance("No holy entities remaining nearby.", gold_delta=0)
            st.rerun()
    with ac2:
        if st.button("🗣️ Consult Oracle", use_container_width=True):
            npcs = [c for c in get_live_creatures() if c['type'] == 'npc']
            if npcs:
                npcs.sort(key=lambda c: math.hypot(c['x'] - st.session_state.player_x, c['z'] - st.session_state.player_z))
                npc = npcs[0]
                dist = math.hypot(npc['x'] - st.session_state.player_x, npc['z'] - st.session_state.player_z)
                if dist <= 10:
                    st.session_state.active_quest = "Inner Council: Purge all remaining celestial guards."
                    process_turn_advance("Consulted inner dark forces. Quests updated!")
                else:
                    st.session_state.message = "You must approach the dark oracle to consult."
            st.rerun()

with col2:
    st.subheader("Crusade Status")
    st.markdown(f"**HP:** {st.session_state.health}/{st.session_state.max_health} | **Souls/Gold:** {st.session_state.gold}G")
    st.markdown(f"**Kills:** {st.session_state.kills} | **Turn:** {st.session_state.turn}")
    
    st.markdown("---")
    st.markdown("### 📜 Quest Log: KILLGOD")
    stage = st.session_state.quest_stage
    if stage == 1:
        st.markdown("**Chapter 1: Vanguard of the Righteous**")
        st.write(f"* Objective: Slay holy temple sentinels.")
        st.write(f"* Progress: {st.session_state.kills} / 3 Kills")
        st.progress(min(1.0, st.session_state.kills / 3))
    elif stage == 2:
        st.markdown("**Chapter 2: Mountain of Prophets**")
        st.write(f"* Objective: Cleanse holy mountains.")
        st.write(f"* Progress: {st.session_state.kills} / 7 Kills")
        st.progress(min(1.0, st.session_state.kills / 7))
    else:
        st.markdown("**Chapter 3: The Protector Approaches**")
        st.write(f"* Objective: Defeat Jesus to breach God's throne.")
        st.write(f"👑 **Face Jesus (Endgame Protector)!**")
        st.progress(1.0)
        
    st.info(st.session_state.active_quest)
    if st.session_state.quest_target_kills > 0:
        remaining = st.session_state.quest_target_kills - st.session_state.kills
        st.write(f"**Targets Left:** {max(0, remaining)}")
    st.markdown("---")
    
    st.markdown("### Divine Radar")
    active_targets = [c for c in st.session_state.creatures if c.get('alive', True) and c['type'] in ['enemy', 'boss']]
    closest_enemy = min(active_targets, key=lambda c: math.hypot(c['x'] - st.session_state.player_x, c['z'] - st.session_state.player_z), default=None)
    
    if closest_enemy:
        dist = math.hypot(closest_enemy['x'] - st.session_state.player_x, closest_enemy['z'] - st.session_state.player_z)
        status = "🔴 In Strike Range" if dist <= 14 else "⚪ Distant"
        st.write(f"**Target:** {closest_enemy['name']} ({closest_enemy['hp']}/{closest_enemy['max_hp']} HP)")
        st.write(f"**Range:** {int(dist)} units {status}")

    st.markdown("### Faction Alignment")
    for faction, score in st.session_state.faction_standing.items():
        st.write(f"**{faction}**: {score} pts")
        st.progress((score + 100) / 200)

    opt = world['optimization_result']
    st.markdown(f"**System Power Index:** ${opt['objective']:,.0f}")
    
    if st.button("🔄 Restart Crusade", use_container_width=True):
        st.session_state.clear()
        st.rerun()