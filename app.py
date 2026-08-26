# app.py
import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random
import sys

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
# IMPORT SCRCAE ENGINE
# ============================================================
try:
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
    SCRCAE_AVAILABLE = True
except ImportError:
    st.error("SCRCAE engine not installed. Please add 'scrcae' to requirements.txt")
    SCRCAE_AVAILABLE = False
    st.stop()

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
# WORLD GENERATION USING SCRCAE
# ============================================================

def generate_world():
    """Generate world using SCRCAE optimization engine"""
    
    # Define species as SCRCAE interventions
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
    
    # Dependencies
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
    
    # Extract species allocations
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
    
    # Generate creatures
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
                            'speed': sp['speed'],
                            'strength': sp['strength'],
                            'magic': sp['magic'],
                            'stealth': sp['stealth']
                        },
                        'element': loc['magic_element'],
                        'scale': round(alloc['scale'], 3)
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
            'constraint_report': str(result.constraint_report.summary())
        }
    }

# ============================================================
# STREAMLIT UI
# ============================================================

