# app.py
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import minimize
import json
import math
import random

st.set_page_config(
    page_title="Dragon Realm",
    page_icon=":dragon:",
    layout="wide"
)

# Hide Streamlit branding
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
# SCRCAE ENGINE
# ============================================================

class CalibratedValue:
    def __init__(self, value, source='asserted', confidence=0.95, method='', evidence=''):
        self.value = value
        self.source = source
        self.confidence = confidence
        self.method = method
        self.evidence = evidence
    
    def to_dict(self):
        return {
            'value': round(self.value, 3),
            'source': self.source,
            'confidence': round(self.confidence, 3),
            'method': self.method,
            'evidence': self.evidence
        }

class MagicSystem:
    """Elemental magic system with calibrated affinities"""
    
    ELEMENTS = ['fire', 'water', 'earth', 'air', 'light', 'shadow']
    
    @staticmethod
    def generate_magic_grid(size=50):
        """Generate a magic field across the world using optimization"""
        grid = np.zeros((size, size, 6))
        
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
                    grid[x, z, i] = max(0, concentration)
        
        for x in range(size):
            for z in range(size):
                total = sum(grid[x, z, :])
                if total > 0:
                    grid[x, z, :] /= total
        
        return grid
    
    @staticmethod
    def get_dominant_element(magic_grid, x, z):
        values = magic_grid[x, z, :]
        idx = np.argmax(values)
        return MagicSystem.ELEMENTS[idx], values[idx]

class EcosystemOptimizer:
    @staticmethod
    def allocate_resources(total_resources, species_demands):
        """
        Use SciPy optimization to allocate resources among species.
        """
        species_names = list(species_demands.keys())
        demands = np.array([species_demands[s] for s in species_names])
        n_species = len(species_names)
        
        # Objective: maximize weighted allocation
        def objective(x):
            return -np.sum(x * (1.0 / n_species))
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_resources},  # Total = available
        ]
        
        # Bounds: 0 to demand for each species
        bounds = [(0, d) for d in demands]
        
        # Initial guess
        x0 = np.array([total_resources / n_species] * n_species)
        
        # Solve
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        results = {}
        for i, s in enumerate(species_names):
            results[s] = max(0, result.x[i])
        
        return results
    
    @staticmethod
    def evolve_creature(base_stats, environment_pressure, generations=100):
        stats = dict(base_stats)
        
        for g in range(generations):
            for stat_name in stats:
                if stat_name in environment_pressure:
                    error = stats[stat_name] - environment_pressure[stat_name]
                    stats[stat_name] -= 0.01 * error * 0.1
            
            if random.random() < 0.05:
                mutation_stat = random.choice(list(stats.keys()))
                stats[mutation_stat] += random.gauss(0, 0.2)
                stats[mutation_stat] = max(0.1, stats[mutation_stat])
        
        return stats

# ============================================================
# WORLD GENERATION
# ============================================================

def generate_world():
    species = {
        'dragon': {'food': 50, 'territory': 80, 'magic': 90, 'water': 30},
        'goblin': {'food': 20, 'territory': 30, 'magic': 10, 'water': 25},
        'elf': {'food': 15, 'territory': 25, 'magic': 60, 'water': 20},
        'wolf': {'food': 25, 'territory': 20, 'magic': 5, 'water': 15},
        'bear': {'food': 30, 'territory': 25, 'magic': 8, 'water': 20},
        'fairy': {'food': 5, 'territory': 10, 'magic': 95, 'water': 10}
    }
    
    total_resources = {'food': 200, 'territory': 300, 'magic': 150, 'water': 180}
    
    optimizer = EcosystemOptimizer()
    allocations = {}
    for resource, total in total_resources.items():
        demands = {s: d[resource] for s, d in species.items()}
        alloc = optimizer.allocate_resources(total, demands)
        allocations[resource] = alloc
    
    # Generate terrain
    terrain = np.zeros((50, 50))
    for x in range(50):
        for z in range(50):
            terrain[x, z] = (
                math.sin(x * 0.1) * math.cos(z * 0.12) * 3 +
                math.sin(x * 0.25 + z * 0.18) * 2 +
                math.sin(x * 0.05 + z * 0.08) * 5 +
                random.gauss(0, 0.3)
            )
    
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    terrain = terrain * 20
    
    # Generate magic grid
    magic = MagicSystem.generate_magic_grid(50)
    
    # Generate biomes
    biomes = []
    for x in range(0, 50, 2):
        for z in range(0, 50, 2):
            height = terrain[x, z]
            local_food = allocations['food']['dragon'] * 0.1 + random.random() * 5
            local_magic_val = np.sum(magic[x, z, :]) * 5
            
            if height > 15:
                biome = 'mountain'
            elif height > 10:
                biome = 'forest' if local_food > 3 else 'cliffs'
            elif height > 5:
                biome = 'plains' if local_food > 4 else 'desert'
            elif height > 2:
                biome = 'swamp' if local_magic_val > 2 else 'grassland'
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
    
    # Generate creatures
    creatures = []
    for species_name, base_stats in {
        'dragon': {'speed': 8, 'strength': 10, 'magic': 9, 'stealth': 3},
        'goblin': {'speed': 4, 'strength': 3, 'magic': 2, 'stealth': 7},
        'elf': {'speed': 6, 'strength': 4, 'magic': 8, 'stealth': 6},
        'wolf': {'speed': 7, 'strength': 5, 'magic': 1, 'stealth': 8},
        'bear': {'speed': 3, 'strength': 8, 'magic': 1, 'stealth': 4},
        'fairy': {'speed': 9, 'strength': 1, 'magic': 10, 'stealth': 9}
    }.items():
        env_pressure = {
            'speed': allocations['territory'].get(species_name, 20) / 30,
            'strength': allocations['food'].get(species_name, 20) / 30,
            'magic': allocations['magic'].get(species_name, 20) / 30,
            'stealth': allocations['water'].get(species_name, 20) / 30
        }
        
        evolved_stats = optimizer.evolve_creature(base_stats, env_pressure, generations=50)
        
        count = int(allocations['food'].get(species_name, 10) / 5)
        for i in range(count):
            biome_pref = {
                'dragon': 'mountain',
                'goblin': 'swamp',
                'elf': 'forest',
                'wolf': 'plains',
                'bear': 'forest',
                'fairy': 'forest'
            }[species_name]
            
            suitable = [b for b in biomes if b['biome'] == biome_pref]
            if suitable:
                loc = random.choice(suitable)
                creatures.append({
                    'name': species_name,
                    'x': loc['x'],
                    'z': loc['z'],
                    'stats': {k: {'value': round(v, 2), 'source': 'calibrated', 'confidence': 0.9} 
                             for k, v in evolved_stats.items()},
                    'element': loc['magic_element'],
                    'provenance': [f"MILP allocation: {allocations['food'][species_name]:.1f} food units"]
                })
    
    return {
        'terrain': terrain.tolist(),
        'magic_grid': magic.tolist(),
        'biomes': biomes,
        'creatures': creatures,
        'allocations': allocations
    }

# ============================================================
# STREAMLIT UI
# ============================================================

if 'world_data' not in st.session_state:
    with st.spinner("Optimizing the realm..."):
        st.session_state.world_data = generate_world()
        st.session_state.player_x = 25
        st.session_state.player_z = 25
        st.session_state.player_angle = 0
        st.session_state.message = "The realm has been optimized. Explore!"
        st.session_state.discovered = set()
        st.session_state.dragon_tame = 0
        st.session_state.magic_affinity = {'fire': 0.5, 'water': 0.5, 'earth': 0.5, 'air': 0.5, 'light': 0.5, 'shadow': 0.5}
        st.session_state.spells = []
        st.session_state.health = 100
        st.session_state.gold = 0

world = st.session_state.world_data

# Build the 3D viewer
def build_viewer_html():
    terrain_data = json.dumps(world['terrain'])
    biomes_data = json.dumps(world['biomes'])
    creatures_data = json.dumps(world['creatures'])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#0a0a12;overflow:hidden;font-family:monospace;color:#fff}}
        canvas{{display:block;width:100vw;height:100vh}}
        #hud{{position:absolute;top:10px;left:10px;font-size:12px;text-shadow:0 2px 4px #000;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:8px;pointer-events:none;z-index:10}}
        #controls{{position:absolute;bottom:20px;left:0;right:0;display:flex;justify-content:center;gap:10px;z-index:10}}
        button{{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:#fff;font-size:16px;padding:12px 20px;border-radius:24px;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);min-width:44px;touch-action:manipulation}}
        button:active{{background:rgba(255,255,255,0.25);transform:scale(0.95)}}
    </style>
    </head>
    <body>
    <canvas id="c"></canvas>
    <div id="hud">
        <div id="info">Loading...</div>
        <div id="magicInfo" style="font-size:10px;color:#aa88ff;margin-top:4px;"></div>
    </div>
    <div id="controls">
        <button id="bA" ontouchstart="move(-1,0)" onmousedown="move(-1,0)">L</button>
        <button id="bW" ontouchstart="move(0,-1)" onmousedown="move(0,-1)">F</button>
        <button id="bD" ontouchstart="move(1,0)" onmousedown="move(1,0)">R</button>
        <button id="bS" ontouchstart="move(0,1)" onmousedown="move(0,1)">B</button>
    </div>
    <script>
        const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');
        const info=document.getElementById('info');
        const magicInfo=document.getElementById('magicInfo');
        
        const terrain = {terrain_data};
        const biomes = {biomes_data};
        const creatures = {creatures_data};
        
        let W, H;
        let player = {{x: 25, z: 25, angle: 0}};
        let frame = 0;
        
        function resize(){{W=window.innerWidth; H=window.innerHeight; canvas.width=W; canvas.height=H;}}
        window.addEventListener('resize', resize); resize();
        
        function project(x, z, y) {{
            const fov = 200;
            const dx = x - player.x;
            const dz = z - player.z;
            const cosA = Math.cos(player.angle);
            const sinA = Math.sin(player.angle);
            const rx = dx * cosA - dz * sinA;
            const rz = dx * sinA + dz * cosA;
            if(rz < 1) return null;
            const sx = W/2 + (rx * fov) / rz;
            const sy = H/2 - (y * fov) / rz;
            return {{x: sx, y: sy, scale: fov/rz}};
        }}
        
        function getBiome(x, z) {{
            for(const b of biomes) {{
                if(b.x === x && b.z === z) return b;
            }}
            return null;
        }}
        
        function getCreatures(x, z) {{
            return creatures.filter(c => Math.abs(c.x - x) < 3 && Math.abs(c.z - z) < 3);
        }}
        
        const biomeColors = {{
            'mountain': '#6a6a7a',
            'forest': '#2d5a27',
            'cliffs': '#8a7a5a',
            'plains': '#6a8a4a',
            'desert': '#c2a65a',
            'swamp': '#3a5a3a',
            'grassland': '#5a7a3a',
            'water': '#2a4a6a'
        }};
        
        const elementColors = {{
            'fire': '#ff4400',
            'water': '#4488ff',
            'earth': '#886644',
            'air': '#aaddff',
            'light': '#ffff88',
            'shadow': '#8844aa'
        }};
        
        function render() {{
            ctx.fillStyle = '#0a0a12';
            ctx.fillRect(0, 0, W, H);
            
            // Stars
            for(let i = 0; i < 50; i++) {{
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.2 + Math.sin(i + frame * 0.02) * 0.2;
                ctx.beginPath();
                ctx.arc((i * 137.5) % W, (i * 97.3) % (H * 0.5), 0.5, 0, Math.PI * 2);
                ctx.fill();
            }}
            ctx.globalAlpha = 1;
            
            // Draw terrain
            for(const b of biomes) {{
                const p = project(b.x, 0, b.height * 0.5);
                if(!p || p.scale < 0.01) continue;
                
                const dist = Math.sqrt((b.x - player.x)**2 + (b.z - player.z)**2);
                const brightness = Math.max(0.1, 1 - dist / 30);
                ctx.globalAlpha = brightness;
                ctx.fillStyle = biomeColors[b.biome] || '#444';
                const s = Math.max(1, p.scale * 0.3);
                ctx.fillRect(p.x - s/2, p.y - s/2, s, s);
                
                // Magic glow
                if(b.magic_strength > 0.6) {{
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = elementColors[b.magic_element] || '#fff';
                    ctx.fillStyle = elementColors[b.magic_element] || '#fff';
                    ctx.globalAlpha = b.magic_strength * 0.2;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, s * 2, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;
                }}
                
                // POI
                if(b.poi) {{
                    ctx.fillStyle = '#ffc864';
                    ctx.globalAlpha = 0.8;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y - s, s * 0.8, 0, Math.PI * 2);
                    ctx.fill();
                }}
            }}
            ctx.globalAlpha = 1;
            
            // Draw creatures
            for(const c of creatures) {{
                const p = project(c.x, 0, 1);
                if(!p) continue;
                const dist = Math.sqrt((c.x - player.x)**2 + (c.z - player.z)**2);
                if(dist > 15) continue;
                
                ctx.fillStyle = elementColors[c.element] || '#fff';
                ctx.shadowBlur = 8;
                ctx.shadowColor = elementColors[c.element] || '#fff';
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3 + c.stats.speed.value * 0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                
                ctx.fillStyle = '#fff';
                ctx.font = '8px monospace';
                ctx.textAlign = 'center';
                ctx.fillText(c.name, p.x, p.y - 8);
            }}
            
            // Player
            const pp = project(player.x, 0, 0.5);
            if(pp) {{
                ctx.fillStyle = '#fff';
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#fff';
                ctx.beginPath();
                ctx.arc(pp.x, pp.y, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }}
            
            // HUD
            const biome = getBiome(Math.round(player.x), Math.round(player.z));
            const nearby = getCreatures(Math.round(player.x), Math.round(player.z));
            let hudText = `Loc: (${{Math.round(player.x)}}, ${{Math.round(player.z)}})`;
            if(biome) {{
                hudText += ` | ${{biome.biome.toUpperCase()}}`;
                hudText += ` | Magic: ${{biome.magic_element.toUpperCase()}} (${{(biome.magic_strength * 100).toFixed(0)}}%)`;
            }}
            hudText += ` | Creatures: ${{nearby.length}}`;
            info.textContent = hudText;
            
            if(biome) {{
                magicInfo.textContent = `Element: ${{biome.magic_element}} | Strength: ${{(biome.magic_strength * 100).toFixed(0)}}%`;
                magicInfo.style.color = elementColors[biome.magic_element] || '#aa88ff';
            }}
            
            frame++;
