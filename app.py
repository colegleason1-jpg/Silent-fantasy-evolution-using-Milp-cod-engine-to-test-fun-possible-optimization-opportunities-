# app.py
import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random

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
# IMPORT YOUR SCRCAE ENGINE
# ============================================================
from scrcae import (
    Bundle,
    Dependency,
    Intervention,
    MonetaryNPVObjective,
    OptimizationRequest,
    PriceBook,
    SupplyNetwork,
    solve,
)
from scrcae.risk import AllocationConcaveResponse

# ============================================================
# WORLD GENERATION USING SCRCAE
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
        
        # Normalize
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

def generate_world():
    """Generate world using SCRCAE optimization engine"""
    
    # Define game elements as SCRCAE interventions
    species_interventions = (
        Intervention(
            "DR", "Dragon", "Ancient fire-breathing dragon",
            cost=50000.0, risk_reduction_pts=90.0,
            lead_time_saved_days=30.0, carbon_tons=200.0,
        ),
        Intervention(
            "GO", "Goblin", "Cunning cave dwellers",
            cost=10000.0, risk_reduction_pts=20.0,
            lead_time_saved_days=8.0, carbon_tons=30.0,
        ),
        Intervention(
            "EL", "Elf", "Magical forest beings",
            cost=30000.0, risk_reduction_pts=60.0,
            lead_time_saved_days=15.0, carbon_tons=10.0,
        ),
        Intervention(
            "WO", "Wolf", "Pack hunters of the plains",
            cost=8000.0, risk_reduction_pts=15.0,
            lead_time_saved_days=5.0, carbon_tons=20.0,
        ),
        Intervention(
            "BE", "Bear", "Mighty forest dwellers",
            cost=12000.0, risk_reduction_pts=25.0,
            lead_time_saved_days=6.0, carbon_tons=40.0,
        ),
        Intervention(
            "FA", "Fairy", "Tiny magical creatures",
            cost=20000.0, risk_reduction_pts=70.0,
            lead_time_saved_days=20.0, carbon_tons=5.0,
        ),
    )
    
    # Dependencies (e.g., Fairy magic enables Elf magic)
    dependencies = (
        Dependency(dependent="EL", prerequisite="FA"),
        Dependency(dependent="DR", prerequisite="EL"),
    )
    
    # Bundles
    bundles = (
        Bundle(name="Forest_Alliance", discount=15000.0,
               required_nodes=("EL", "FA")),
        Bundle(name="Dragon_Pact", discount=25000.0,
               required_nodes=("DR", "EL")),
    )
    
    # Price book
    prices = PriceBook(
        value_per_risk_point=5000.0,
        value_per_lead_time_day=1000.0,
        price_per_carbon_ton=50.0,
        benefit_horizon_years=5,
        discount_rate=0.10,
        source="game-calibrated",
    )
    
    # Build network
    network = SupplyNetwork(
        baseline_risk_pts=100.0,
        interventions=species_interventions,
        dependencies=dependencies,
        bundles=bundles,
    )
    
    # Solve optimization
    result = solve(
        OptimizationRequest(
            network=network,
            objective=MonetaryNPVObjective(prices=prices),
            risk_response=AllocationConcaveResponse(exponent=0.85),
            budget=200000.0,
        )
    )
    
    # Extract species allocations from optimization results
    species_allocations = {}
    for a in result.active_allocations:
        species_allocations[a.node_id] = {
            'scale': a.funding_scale,
            'capital': a.capital,
            'risk_reduction': a.risk_reduction_pts
        }
    
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
    
    # Normalize terrain
    min_val = min(min(row) for row in terrain)
    max_val = max(max(row) for row in terrain)
    for x in range(50):
        for z in range(50):
            terrain[x][z] = ((terrain[x][z] - min_val) / (max_val - min_val)) * 20
    
    # Generate magic grid
    magic = MagicSystem.generate_magic_grid(50)
    
    # Generate biomes
    biomes = []
    for x in range(0, 50, 2):
        for z in range(0, 50, 2):
            height = terrain[x][z]
            
            if height > 15:
                biome = 'mountain'
            elif height > 10:
                biome = 'forest'
            elif height > 5:
                biome = 'plains'
            elif height > 2:
                biome = 'swamp'
            else:
                biome = 'water'
            
            dom_element, dom_strength = MagicSystem.get_dominant_element(magic, x, z)
            
            poi = None
            if biome == 'mountain' and dom_strength > 0.6:
                poi = {'type': 'dragon_lair', 'name': 'Dragonspire Peak', 'element': dom_element}
            elif biome == 'forest' and dom_strength > 0.5:
                poi = {'type': 'elf_camp', 'name': 'Silverwood Grove', 'element': dom_element}
            elif biome == 'swamp' and dom_strength > 0.4:
                poi = {'type': 'goblin_cave', 'name': 'Murkden Hollow', 'element': dom_element}
            
            biomes.append({
                'x': x, 'z': z,
                'height': round(height, 1),
                'biome': biome,
                'magic_element': dom_element,
                'magic_strength': round(dom_strength, 2),
                'poi': poi
            })
    
    # Generate creatures using SCRCAE allocations
    creatures = []
    species_map = {
        'DR': {'name': 'Dragon', 'biome': 'mountain', 'speed': 8, 'strength': 10, 'magic': 9, 'stealth': 3},
        'GO': {'name': 'Goblin', 'biome': 'swamp', 'speed': 4, 'strength': 3, 'magic': 2, 'stealth': 7},
        'EL': {'name': 'Elf', 'biome': 'forest', 'speed': 6, 'strength': 4, 'magic': 8, 'stealth': 6},
        'WO': {'name': 'Wolf', 'biome': 'plains', 'speed': 7, 'strength': 5, 'magic': 1, 'stealth': 8},
        'BE': {'name': 'Bear', 'biome': 'forest', 'speed': 3, 'strength': 8, 'magic': 1, 'stealth': 4},
        'FA': {'name': 'Fairy', 'biome': 'forest', 'speed': 9, 'strength': 1, 'magic': 10, 'stealth': 9}
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
                        'name': sp['name'],
                        'x': loc['x'],
                        'z': loc['z'],
                        'stats': {
                            'speed': {'value': sp['speed'], 'source': 'calibrated'},
                            'strength': {'value': sp['strength'], 'source': 'calibrated'},
                            'magic': {'value': sp['magic'], 'source': 'calibrated'},
                            'stealth': {'value': sp['stealth'], 'source': 'calibrated'}
                        },
                        'element': loc['magic_element'],
                        'scale': round(alloc['scale'], 3),
                        'capital': round(alloc['capital'], 0)
                    })
    
    return {
        'terrain': terrain,
        'magic_grid': magic,
        'biomes': biomes,
        'creatures': creatures,
        'optimization_result': {
            'status': result.status,
            'objective': result.objective_value,
            'risk_reduction': result.risk_reduction_pts,
            'active_bundles': list(result.active_bundles),
            'constraint_report': result.constraint_report.summary()
        }
    }

# ============================================================
# STREAMLIT UI
# ============================================================

if 'world_data' not in st.session_state:
    with st.spinner("Running SCRCAE optimization..."):
        st.session_state.world_data = generate_world()
        st.session_state.player_x = 25
        st.session_state.player_z = 25
        st.session_state.message = "World optimized with SCRCAE engine!"
        st.session_state.discovered = set()
        st.session_state.dragon_tame = 0
        st.session_state.magic_affinity = {'fire': 0.5, 'water': 0.5, 'earth': 0.5, 'air': 0.5, 'light': 0.5, 'shadow': 0.5}
        st.session_state.spells = []
        st.session_state.health = 100
        st.session_state.gold = 0

world = st.session_state.world_data

# SIMPLIFIED 2D VIEWER - This will definitely work
def get_viewer_html():
    terrain_data = json.dumps(world['terrain'])
    biomes_data = json.dumps(world['biomes'])
    creatures_data = json.dumps(world['creatures'])
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a12;overflow:hidden;font-family:monospace;color:#fff}
        #game{width:100vw;height:100vh;position:relative;background:#0a0a12}
        #map{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-wrap:wrap;align-content:flex-start;padding:10px}
        .tile{width:8px;height:8px;margin:0;padding:0}
        #hud{position:absolute;top:10px;left:10px;font-size:12px;text-shadow:0 2px 4px #000;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:8px;z-index:10}
        #controls{position:absolute;bottom:20px;left:0;right:0;display:flex;justify-content:center;gap:10px;z-index:10}
        button{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:#fff;font-size:16px;padding:12px 20px;border-radius:24px;min-width:44px;touch-action:manipulation}
        button:active{background:rgba(255,255,255,0.25);transform:scale(0.95)}
    </style>
    </head>
    <body>
    <div id="game">
        <div id="hud">
            <div id="info">Loading...</div>
        </div>
        <div id="map"></div>
        <div id="controls">
            <button onclick="move(-2,0)">L</button>
            <button onclick="move(0,-2)">F</button>
            <button onclick="move(2,0)">R</button>
            <button onclick="move(0,2)">B</button>
        </div>
    </div>
    <script>
        var terrain = ''' + terrain_data + ''';
        var biomes = ''' + biomes_data + ''';
        var creatures = ''' + creatures_data + ''';
        
        var player = {x: 25, z: 25};
        var mapEl = document.getElementById("map");
        var infoEl = document.getElementById("info");
        
        var biomeColors = {
            "mountain": "#6a6a7a",
            "forest": "#2d5a27",
            "cliffs": "#8a7a5a",
            "plains": "#6a8a4a",
            "desert": "#c2a65a",
            "swamp": "#3a5a3a",
            "grassland": "#5a7a3a",
            "water": "#2a4a6a"
        };
        
        var elementColors = {
            "fire": "#ff4400",
            "water": "#4488ff",
            "earth": "#886644",
            "air": "#aaddff",
            "light": "#ffff88",
            "shadow": "#8844aa"
        };
        
        function getBiome(x, z) {
            for(var i=0; i<biomes.length; i++) {
                var b = biomes[i];
                if(b.x === x && b.z === z) return b;
            }
            return null;
        }
        
        function render() {
            mapEl.innerHTML = "";
            var viewSize = 12;
            
            for(var dz = -viewSize; dz <= viewSize; dz++) {
                for(var dx = -viewSize; dx <= viewSize; dx++) {
                    var wx = player.x + dx;
                    var wz = player.z + dz;
                    
                    var tile = document.createElement("div");
                    tile.className = "tile";
                    tile.style.width = "8px";
                    tile.style.height = "8px";
                    
                    if(dx === 0 && dz === 0) {
                        tile.style.background = "#fff";
                        tile.style.boxShadow = "0 0 4px #fff";
                    } else {
                        var biome = getBiome(wx, wz);
                        if(biome) {
                            var dist = Math.sqrt(dx*dx + dz*dz);
                            var brightness = Math.max(0.2, 1 - dist/viewSize);
                            tile.style.background = biomeColors[biome.biome] || "#444";
                            tile.style.opacity = brightness;
                            
                            // Check for creatures
                            for(var i=0; i<creatures.length; i++) {
                                var c = creatures[i];
                                if(c.x === wx && c.z === wz) {
                                    tile.style.background = elementColors[c.element] || "#fff";
                                    tile.style.boxShadow = "0 0 4px " + (elementColors[c.element] || "#fff");
                                    break;
                                }
                            }
                            
                            // Check for POI
                            if(biome.poi) {
                                tile.style.background = "#ffc864";
                                tile.style.boxShadow = "0 0 6px #ffc864";
                            }
                            
                            // Magic glow
                            if(biome.magic_strength > 0.7) {
                                tile.style.boxShadow = "0 0 6px " + (elementColors[biome.magic_element] || "#fff");
                            }
                        } else {
                            tile.style.background = "#111";
                            tile.style.opacity = 0.3;
                        }
                    }
                    mapEl.appendChild(tile);
                }
            }
            
            // Update HUD
            var biome = getBiome(player.x, player.z);
            var nearby = 0;
            for(var i=0; i<creatures.length; i++) {
                var c = creatures[i];
                if(Math.abs(c.x - player.x) < 5 && Math.abs(c.z - player.z) < 5) {
                    nearby++;
                }
            }
            
            var hudText = "Pos: (" + player.x + ", " + player.z + ")";
            if(biome) {
                hudText += " | " + biome.biome.toUpperCase();
                hudText += " | " + biome.magic_element.toUpperCase() + " (" + (biome.magic_strength * 100).toFixed(0) + "%)";
            }
            hudText += " | Creatures: " + nearby;
            infoEl.textContent = hudText;
        }
        
        function move(dx, dz) {
            var nx = player.x + dx;
            var nz = player.z + dz;
            if(nx >= 0 && nx < 50 && nz >= 0 && nz < 50) {
                player.x = nx;
                player.z = nz;
                render();
            }
        }
        
        // Touch controls
        var tx = 0, ty = 0;
        document.addEventListener("touchstart", function(e) {
            var t = e.touches[0];
            tx = t.clientX;
            ty = t.clientY;
        });
        document.addEventListener("touchmove", function(e) {
            e.preventDefault();
            var t = e.touches[0];
            var dx = t.clientX - tx;
            var dy = t.clientY - ty;
            if(Math.abs(dx) > 30) {
                move(dx > 0 ? 2 : -2, 0);
                tx = t.clientX;
            }
            if(Math.abs(dy) > 30) {
                move(0, dy > 0 ? 2 : -2);
                ty = t.clientY;
            }
        }, {passive: false});
        
        render();
    </script>
    </body>
    </html>
    '''
    return html

# Render the viewer
viewer_html = get_viewer_html()
components.html(viewer_html, height=600, scrolling=False)

# Sidebar
with st.sidebar:
    st.markdown("## Dragon Realm")
    st.markdown("### SCRCAE Optimization Results")
    
    opt = world['optimization_result']
    st.markdown(f"""
    - **Status:** {opt['status']}
    - **Objective:** {opt['objective']:,.0f}
    - **Risk Reduction:** {opt['risk_reduction']:.2f} pts
    - **Active Bundles:** {', '.join(opt['active_bundles']) if opt['active_bundles'] else 'None'}
    - **Constraints:** {opt['constraint_report']}
    """)
    
    st.markdown("### Magic System")
    biome = next((b for b in world['biomes'] 
                  if b['x'] == st.session_state.player_x and b['z'] == st.session_state.player_z), None)
    
    if biome:
        color_map = {'fire': '#ff4400', 'water': '#4488ff', 'earth': '#886644', 
                     'air': '#aaddff', 'light': '#ffff88', 'shadow': '#8844aa'}
        element_color = color_map.get(biome['magic_element'], '#aa88ff')
        
        st.markdown(f"""
        <div style="background: rgba(170, 136, 255, 0.1); border: 1px solid rgba(170, 136, 255, 0.2); 
                    border-radius: 8px; padding: 10px; margin: 10px 0;">
            <p style="margin: 5px 0; color: #ccc;">
                Element: <b style="color: {element_color};">{biome['magic_element'].upper()}</b>
            </p>
            <p style="margin: 5px 0; color: #ccc;">
                Strength: {biome['magic_strength'] * 100:.0f}%
            </p>
            <p style="margin: 5px 0; color: #ccc;">
                Biome: {biome['biome'].upper()}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Spells")
    if st.button("Learn Spell (50 gold)"):
        if st.session_state.gold >= 50:
            st.session_state.gold -= 50
            new_spell = random.choice(['Fireball', 'Heal', 'Teleport', 'Lightning', 'Shield', 'Invisibility'])
            if new_spell not in st.session_state.spells:
                st.session_state.spells.append(new_spell)
                st.session_state.message = f"You learned {new_spell}!"
            else:
                st.session_state.message = "You already know that spell."
        else:
            st.session_state.message = "Not enough gold!"
    
    if st.session_state.spells:
        for spell in st.session_state.spells:
            st.markdown(f"- {spell}")
    
    st.markdown(f"Health: {st.session_state.health}/100")
    st.markdown(f"Gold: {st.session_state.gold}")
    
    if st.button("Explore"):
        if biome:
            st.session_state.discovered.add((biome['x'], biome['z']))
            st.session_state.gold += random.randint(1, 5)
            st.session_state.message = f"You explored the {biome['biome']}!"

# Message
if st.session_state.message:
    st.markdown(f"""
    <div style="background: rgba(255, 200, 100, 0.1); border: 1px solid rgba(255, 200, 100, 0.2); 
                border-radius: 8px; padding: 10px; text-align: center; margin-top: 10px;">
        <p style="color: #ffc864; margin: 0;">{st.session_state.message}</p>
    </div>
    """, unsafe_allow_html=True)
