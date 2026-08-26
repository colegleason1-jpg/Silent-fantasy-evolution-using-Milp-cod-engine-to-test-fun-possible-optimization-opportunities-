# app.py
import streamlit as st
import random
import math
import time

st.set_page_config(
    page_title="Dragon Realm",
    page_icon="🐉",
    layout="centered"
)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background: #0a0a1a;}
    .stButton button {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: #fff;
        font-size: 18px;
        padding: 15px 25px;
        border-radius: 30px;
        width: 100%;
    }
    .stButton button:active {
        background: rgba(255,255,255,0.25);
    }
    .stText {color: #c8c8d0;}
    h1, h2, h3 {color: #ffc864 !important;}
    .element-container {margin-bottom: 0 !important;}
    div[data-testid="column"] {padding: 0 4px !important;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.player_x = 0
    st.session_state.player_z = 0
    st.session_state.player_angle = 0
    st.session_state.dragon_x = 30
    st.session_state.dragon_z = 20
    st.session_state.dragon_visible = False
    st.session_state.dragon_tame = 0
    st.session_state.health = 100
    st.session_state.gold = 0
    st.session_state.inventory = []
    st.session_state.message = "Welcome to Dragon Realm!"
    st.session_state.step = 0
    st.session_state.discovered_places = set()

# World data
places = {
    (0, 0): {"name": "Dragon's Lair", "desc": "A glowing cave entrance. Heat radiates from within.", "type": "lair"},
    (5, 3): {"name": "Whisperwood Forest", "desc": "Ancient trees with glowing blue leaves.", "type": "forest"},
    (-4, 6): {"name": "Crystal Lake", "desc": "Water so clear you can see gold coins at the bottom.", "type": "lake"},
    (8, -2): {"name": "Ruined Tower", "desc": "A crumbling tower with strange runes.", "type": "ruin"},
    (-6, -5): {"name": "Goblin Market", "desc": "A bustling underground market.", "type": "market"},
    (3, -7): {"name": "Frozen Pass", "desc": "Wind howls through the mountain pass.", "type": "mountain"},
    (-8, 3): {"name": "Sunken Temple", "desc": "Half-buried in sand, a temple glows faintly.", "type": "temple"},
    (10, 5): {"name": "Golden Fields", "desc": "Wheat as tall as a person, swaying in the wind.", "type": "plains"},
    (-3, -8): {"name": "Dark Hollow", "desc": "A pit with strange whispers echoing up.", "type": "dungeon"},
    (7, -6): {"name": "Storm Peak", "desc": "The highest peak, lightning strikes constantly.", "type": "peak"}
}

# Dragon behavior
def update_dragon():
    dx = st.session_state.player_x - st.session_state.dragon_x
    dz = st.session_state.player_z - st.session_state.dragon_z
    dist = math.sqrt(dx*dx + dz*dz)
    
    if dist < 5:
        st.session_state.dragon_visible = True
        if st.session_state.dragon_tame < 50:
            st.session_state.message = "🐉 The dragon circles you warily. It doesn't trust you yet."
            # Dragon fire damage if too close
            if random.random() < 0.1:
                st.session_state.health -= 5
                st.session_state.message = "🔥 The dragon's fire breath singes you! (-5 HP)"
        else:
            st.session_state.message = "🐉 The dragon lands beside you and nuzzles your hand."
    elif dist < 15:
        st.session_state.dragon_visible = True
        st.session_state.dragon_x += dx * 0.02
        st.session_state.dragon_z += dz * 0.02
        if st.session_state.message == "Welcome to Dragon Realm!":
            st.session_state.message = "🐉 A dragon circles overhead..."
    else:
        st.session_state.dragon_visible = False
        # Dragon wanders
        st.session_state.dragon_x += random.random() * 0.2 - 0.1
        st.session_state.dragon_z += random.random() * 0.2 - 0.1

# Title screen
if not st.session_state.game_started:
    st.markdown(""<hi style='text-align: center; font-size: 48px; margin-top: 60px;'>🐉</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #ffc864;'>Dragon Realm</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>A Fantasy Adventure</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⚔ Begin Your Journey", use_container_width=True):
        st.session_state.game_started = True
        st.session_state.message = "You stand at the edge of the world. A dragon roars in the distance..."
        st.rerun()
    
    st.markdown("<br><br><p style='text-align: center; color: #555; font-size: 12px;'>Swipe or use buttons to explore</p>", unsafe_allow_html=True)
    st.stop()

# Game loop
update_dragon()
st.session_state.step += 1

# Header
col1, col2, col3 = st.columns([1,2,1])
with col1:
    st.markdown(f"<p style='color: #ff6; font-size: 14px;'>❤️ {st.session_state.health}</p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<: style='text-align: center; color: #ffc864;'>🐉 Dragon Realm</h3>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<p style='color: #ffd700; font-size: 14px; text-align: right;'>� {st.session_state.gold}</p>", unsafe_allow_html=True)

# World view (ASCII map)
st.markdown("<br>", unsafe_allow_html=True)

# Generate view based on player position
view_size = 5
view = ""
for z in range(-view_size, view_size + 1):
    for x in range(-view_size, view_size + 1):
        wx = st.session_state.player_x + x
        wz = st.session_state.player_z + z
        
        if x == 0 and z == 0:
            view += "🧑"
        elif (wx, wz) in places:
            p = places[(wx, wz)]
            if p["type"] == "lair":
                view += "🔥"
            elif p["type"] == "forest":
                view += "🌲"
            elif p["type"] == "lake":
                view += "🌊"
            elif p["type"] == "ruin":
                view += "🏚"
            elif p["type"] == "market":
                view += "🏪"
            elif p["type"] == "mountain":
                view += "🏔"
            elif p["type"] == "temple":
                view += "🏛"
            elif p["type"] == "plains":
                view += "🌾"
            elif p["type"] == "dungeon":
                view += "🕳"
            elif p["type"] == "peak":
                view += "⛰"
            else:
                view += "⬛"
        elif st.session_state.dragon_visible and abs(wx - st.session_state.dragon_x) < 1 and abs(wz - st.session_state.dragon_z) < 1:
            view += "🐉"
        else:
            # Distance fog
            dist = math.sqrt(x*x + z*z)
            if dist < 2:
                view += "⬜"
            elif dist < 3:
                view += "⬛"
            else:
                view += "⬛"
    view += "\n"

st.markdown(f"<pre style='background: #0a0a1a; color: #fff; font-size: 22px; line-height: 1.2; text-align: center; border: none; padding: 10px;'>{view}</pre>", unsafe_allow_html=True)

# Compass
angle = st.session_state.player_angle
dirs = ["🧭 N", "↗ NE", "→ E", "↘ SE", "↓ S", "↙ SW", "← W", "↖ NW"]
dir_idx = int((angle % (math.pi*2)) / (math.pi*2)) * 8) % 8
st.markdown(f"<: style='text-align: center; color: #888; font-size: 14px;'>{dirs[dir_idx]}</p>", unsafe_allow_html=True)

# Current location
current_pos = (st.session_state.player_x, st.session_state.player_z)
if current_pos in places:
    p = places[current_pos]
    st.markdown(f"<div style='background: rgba(255,200,100,0.1); border: 1px solid rgba(255,200,100,0.2); border-radius: 10px; padding: 12px; margin: 8px 0;'><h3 style='margin: 0; color: #ffc864;'>{p['name']}</h3><p style='color: #aaa; margin: 4px 0 0 0;'>{p['desc']}</p></div>", unsafe_allow_html=True)
    
    # Interaction
    if p["type"] == "lair":
        if st.button("🔥 Enter the Lair"):
            if st.session_state.dragon_tame < 30:
                st.session_state.message = "The dragon blocks your path with a wall of flame!"
                st.session_state.health -= 10
            else:
                st.session_state.message = "The dragon allows you into its lair. You find a chest of gold!"
                st.session_state.gold += 50
    elif p["type"] == "forest":
        if st.button("🌲 Search the Forest"):
            if random.random() < 0.5:
                found = random.choice(["Magic Herb", "Golden Acorn", "Fairy Dust"])
                st.session_state.inventory.append(found)
                st.session_state.message = f"You found {found}!"
            else:
                st.session_state.message = "You find nothing but peace and quiet."
    elif p["type"] == "lake":
        if st.button("🌊 Search the Lake"):
            gold_found = random.randint(1, 10)
            st.session_state.gold += gold_found
            st.session_state.message = f"You dive and find {gold_found} gold coins!"
    elif p["type"] == "ruin":
        if st.button("🏚 Explore the Ruins"):
            if random.random() < 0.3:
                st.session_state.message = "You trigger an ancient trap! (-15 HP)"
                st.session_state.health -= 15
            else:
                found = random.choice(["Ancient Rune Stone", "Silver Crown", "Old Map"])
                st.session_state.inventory.append(found)
                st.session_state.message = f"You discover {found}!"
    elif p["type"] == "market":
        if st.button("🏪 Visit the Market"):
            if st.session_state.gold >= 20:
                st.session_state.gold -= 20
                item = random.choice(["Health Potion", "Dragon Treat", "Magic Compass"])
                st.session_state.inventory.append(item)
                st.session_state.message = f"You bought {item}!"
            else:
                st.session_state.message = "You don't have enough gold."
    elif p["type"] == "mountain":
        if st.button("🏔 Climb the Pass"):
            if "Health Potion" in st.session_state.inventory:
                st.session_state.inventory.remove("Health Potion")
                st.session_state.message = "You brave the pass! At the top, you see the entire realm."
                st.session_state.gold += 20
            else:
                st.session_state.message = "The wind is too strong. You need a Health Potion to survive."
    elif p["type"] == "temple":
        if st.button("🏛 Enter the Temple"):
            if "Ancient Rune Stone" in st.session_state.inventory:
                st.session_state.message = "The rune stone glows! A hidden door opens revealing treasure!"
                st.session_state.gold += 100
                st.session_state.inventory.remove("Ancient Rune Stone")
            else:
                st.session_state.message = "The door is sealed. A rune stone might open it..."
    elif p["type"] == "plains":
        if st.button("🌾 Search the Fields"):
            st.session_state.message = "You find a hidden path! (+5 gold)"
            st.session_state.gold += 5
    elif p["type"] == "dungeon":
        if st.button("🕳 Descend into Darkness"):
            if random.random() < 0.4:
                st.session_state.health -= 20
                st.session_state.message = "Something attacks in the dark! (-20 HP)"
            else:
                found = random.choice(["Dragon Scale", "Shadow Gem", "Bone Key"])
                st.session_state.inventory.append(found)
                st.session_state.message = f"You found {found} in the depths!"
    elif p["type"] == "peak":
        if st.button("⛰ Reach the Summit"):
            st.session_state.message = "Lightning crackles around you! You feel powerful!"
            st.session_state.health = min(100, st.session_state.health + 20)

# Message
st.markdown(f"<div style='background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; margin: 8px 0; text-align: center;'><p style='color: #ffc864; margin: 0;'>{st.session_state.message}</p></div>", unsafe_allow_html=True)

# Dragon status
if st.session_state.dragon_visible:
    tame_pct = min(100, st.session_state.dragon_tame)
    st.markdown(f"<p style='text-align: center; color: #ff8844; font-size: 13px;'>🐉 Dragon Trust: {tame_pct}%</p>", unsafe_allow_html=True)
    if st.button("🎵 Call Dragon", use_container_width=True):
        if st.session_state.dragon_tame < 100:
            st.session_state.dragon_tame += 5
            st.session_state.message = f"You call out. The dragon seems more curious... (+5 trust)"
        else:
            st.session_state.message = "The dragon is now your companion! You can ride the skies!"
            st.session_state.inventory.append("Dragon Companion")

# Movement buttons
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("◄ Left"):
        st.session_state.player_angle -= math.pi/4
        st.rerun()
with col2:
    if st.button("▲ Forward"):
        st.session_state.player_x += math.cos(st.session_state.player_angle) * 1
        st.session_state.player_z += math.sin(st.session_state.player_angle) * 1
        st.session_state.step += 1
        st.rerun()
with col3:
    if st.button("► Right"):
        st.session_state.player_angle += math.pi/4
        st.rerun()
with col4:
    if st.button("▼ Back"):
        st.session_state.player_x -= math.cos(st.session_state.player_angle) * 1
        st.session_state.player_z -= math.sin(st.session_state.player_angle) * 1
        st.rerun()

# Inventory
if st.session_state.inventory:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🎒 Inventory", expanded=False):
        for item in st.session_state.inventory:
            st.markdown(f"- {item}")
        if "Health Potion" in st.session_state.inventory and st.session_state.health < 100:
            if st.button("💊 Use Health Potion"):
                st.session_state.inventory.remove("Health Potion")
                st.session_state.health = min(100, st.session_state.health + 30)
                st.session_state.message = "You drink the potion. (+30 HP)"
                st.rerun()
        if "Dragon Treat" in st.session_state.inventory and st.session_state.dragon_visible:
            if st.button("🍖 Feed Dragon Treat"):
                st.session_state.inventory.remove("Dragon Treat")
                st.session_state.dragon_tame += 20
                st.session_state.message = "The dragon eats from your hand! (+20 trust)"
                st.rerun()

# Check death
if st.session_state.health <= 0:
    st.markdown("<h1 style='text-align: center; color: #ff4444;'>💀 You have fallen...</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Gold collected: {st.session_state.gold} | Places discovered: {len(st.session_state.discovered_places)}</p>", unsafe_allow_html=True)
    if st.button("🔄 Start New Journey"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
