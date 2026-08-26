import streamlit as st
import random
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kill God - Animated RPG",
    page_icon="⚔️",
    layout="wide"
)

# --- GAME STATE INITIALIZATION ---
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "screen": "menu",
        "level": 1,
        "max_levels": 100,
        "hp": 100,
        "max_hp": 100,
        "mp": 50,
        "max_mp": 50,
        "attack": 15,
        "magic_power": 20,
        "gold": 0,
        "demon_allied": False,
        "inventory": ["Rusty Sword", "Minor Mana Potion"],
        "quest_log": "Awaken in the mortal realm. Slay the beasts.",
        "enemy": None,
        # Animation state triggers
        "anim_player": "idle",
        "anim_enemy": "idle",
        "level_transition": False
    }

gs = st.session_state.game_state

# --- ADVANCED CSS ANIMATION STYLES ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b0e;
        color: #e0e0e0;
        font-family: 'Cinzel', serif, sans-serif;
    }
    .stButton>button {
        background-color: #3b0909;
        color: white;
        border: 1px solid #ff4b4b;
        border-radius: 4px;
        font-weight: bold;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #5c0e0e;
        border-color: #ff7676;
        transform: scale(1.02);
    }
    
    /* --- COMBAT SPRITE / CARD BOXES --- */
    .battlefield {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: #141419;
        border: 2px solid #2b2b36;
        border-radius: 10px;
        padding: 30px;
        margin-bottom: 20px;
    }
    .combatant {
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        background: #1a1a24;
        width: 40%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    /* --- ANIMATION KEYFRAMES --- */
    @keyframes lungeRight {
        0% { transform: translateX(0); }
        50% { transform: translateX(60px) scale(1.05); }
        100% { transform: translateX(0); }
    }
    @keyframes lungeLeft {
        0% { transform: translateX(0); }
        50% { transform: translateX(-60px) scale(1.05); }
        100% { transform: translateX(0); }
    }
    @keyframes hitFlash {
        0% { background-color: #1a1a24; filter: brightness(1); }
        30% { background-color: #ff4b4b; filter: brightness(2); transform: scale(0.95); }
        100% { background-color: #1a1a24; filter: brightness(1); }
    }
    @keyframes healGlow {
        0% { background-color: #1a1a24; box-shadow: 0 0 0px #00ff66; }
        50% { background-color: #0b3d19; box-shadow: 0 0 25px #00ff66; transform: scale(1.03); }
        100% { background-color: #1a1a24; box-shadow: 0 0 0px #00ff66; }
    }
    @keyframes deathFade {
        0% { opacity: 1; transform: scale(1); filter: grayscale(0%); }
        100% { opacity: 0.1; transform: scale(0.8) rotate(5deg); filter: grayscale(100%) blur(2px); }
    }
    @keyframes levelSlideIn {
        0% { opacity: 0; transform: translateY(-30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* --- CSS CLASSES FOR ANIMATION TRIGGERS --- */
    .anim-attack-player { animation: lungeRight 0.4s ease; }
    .anim-attack-enemy { animation: lungeLeft 0.4s ease; }
    .anim-hit { animation: hitFlash 0.5s ease; }
    .anim-heal { animation: healGlow 0.6s ease; }
    .anim-death { animation: deathFade 0.8s forwards; }
    .anim-level-up { animation: levelSlideIn 0.6s ease; }
</style>
""", unsafe_allow_html=True)

# --- ENEMY GENERATOR ENGINE ---
def get_enemy_for_level(lvl):
    if lvl < 25:
        names = ["Goblin Scavenger", "Feral Werewolf", "Corrupted Elf", "Dark Beast"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 40 + (lvl * 5), "max_hp": 40 + (lvl * 5), "atk": 8 + (lvl * 2), "type": "mortal", "icon": "👺"}
    elif lvl == 25:
        return {"name": "The Arch-Demon of the Abyss", "hp": 500, "max_hp": 500, "atk": 35, "type": "boss_demon", "icon": "🔥"}
    elif lvl < 50:
        names = ["Fairy of False Light", "Warlock of the Choir", "Seraphic Hound"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 120 + (lvl * 8), "max_hp": 120 + (lvl * 8), "atk": 20 + (lvl * 3), "type": "angelic", "icon": "🧚"}
    elif lvl == 50:
        return {"name": "Archangel Gabriel", "hp": 1200, "max_hp": 1200, "atk": 55, "type": "boss_angel", "icon": "🕊️"}
    elif lvl < 75:
        names = ["Apostle Peter's Phantom", "False Prophet", "Heavenly Templar"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 250 + (lvl * 12), "max_hp": 250 + (lvl * 12), "atk": 40 + (lvl * 4), "type": "prophet", "icon": "📜"}
    elif lvl == 75:
        return {"name": "Jesus of Nazareth (The Son)", "hp": 3000, "max_hp": 3000, "atk": 80, "type": "boss_jesus", "regen": 150, "icon": "✝️"}
    elif lvl < 100:
        return {"name": f"Lvl {lvl} Throne Guardian", "hp": 500 + (lvl * 15), "max_hp": 500 + (lvl * 15), "atk": 70 + (lvl * 5), "type": "guardian", "icon": "🛡️"}
    else:
        return {"name": "GOD ALMIGHTY (The Creator)", "hp": 10000, "max_hp": 10000, "atk": 150, "type": "boss_god", "icon": "👁️"}

# --- SCREENS ---

# 1. MAIN MENU
if gs["screen"] == "menu":
    st.title("⚔️ KILL GOD: THE REBELLION")
    st.markdown("### *Animated Tactical Dark Fantasy RPG*")
    st.write("Advance through 100 stages of animated combat, unleash melee combos, cast infernal spells, and overthrow the heavens.")
    
    if st.button("Begin Crusade"):
        gs["screen"] = "hub"
        gs["enemy"] = get_enemy_for_level(gs["level"])
        gs["anim_player"] = "idle"
        gs["anim_enemy"] = "idle"
        st.rerun()

# 2. SANCTUARY / HUB
elif gs["screen"] == "hub":
    st.sidebar.title("Player Status")
    st.sidebar.write(f"**Level:** {gs['level']} / {gs['max_levels']}")
    st.sidebar.write(f"**HP:** {gs['hp']} / {gs['max_hp']}")
    st.sidebar.write(f"**MP:** {gs['mp']} / {gs['max_mp']}")
    st.sidebar.write(f"**Attack:** {gs['attack']}")
    st.sidebar.write(f"**Magic Power:** {gs['magic_power']}")
    st.sidebar.write(f"**Gold:** {gs['gold']}")
    st.sidebar.write(f"**Demon Alliance:** {'Active 🔥' if gs['demon_allied'] else 'None'}")

    st.markdown('<div class="anim-level-up">', unsafe_allow_html=True)
    st.title(f"🏰 Sanctuary - Level {gs['level']} Approach")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if gs["level"] == 25 and not gs["demon_allied"]:
        st.warning("🔥 **The Demon Lord appears before you!** He offers an alliance to overthrow the Heavens.")
        if st.button("Form Pact with the Devil"):
            gs["demon_allied"] = True
            gs["attack"] += 20
            gs["magic_power"] += 30
            st.success("Hellfire pact signed! Demon Alliance Active.")
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Quest Progression")
        st.info(gs["quest_log"])
        if st.button("🚀 Enter Next Battle Stage", use_container_width=True):
            gs["enemy"] = get_enemy_for_level(gs["level"])
            gs["screen"] = "combat"
            gs["anim_player"] = "idle"
            gs["anim_enemy"] = "idle"
            st.rerun()
            
    with col2:
        st.subheader("Camp Upgrades")
        st.write(f"Inventory: {', '.join(gs['inventory'])}")
        if st.button("Rest & Heal (Cost: 20 Gold)") and gs["gold"] >= 20:
            gs["gold"] -= 20
            gs["hp"] = gs["max_hp"]
            gs["mp"] = gs["max_mp"]
            gs["anim_player"] = "anim-heal"
            st.success("Fully healed and rested!")
            st.rerun()

# 3. COMBAT ENGINE WITH ANIMATIONS
elif gs["screen"] == "combat":
    st.title(f"⚔️ Battle Stage: Quest {gs['level']}")
    enemy = gs["enemy"]
    
    # Render Battlefield Arena with dynamic CSS animation classes
    p_anim = gs["anim_player"]
    e_anim = gs["anim_enemy"]
    
    st.markdown(f"""
    <div class="battlefield">
        <div class="combatant {p_anim}">
            <h2>🛡️ Protagonist</h2>
            <p><b>HP:</b> {gs['hp']}/{gs['max_hp']}</p>
            <p><b>MP:</b> {gs['mp']}/{gs['max_mp']}</p>
        </div>
        <div style="font-size: 35px; color: #ff4b4b;">VS</div>
        <div class="combatant {e_anim}">
            <h2>{enemy['icon']} {enemy['name']}</h2>
            <p><b>HP:</b> {enemy['hp']}/{enemy['max_hp']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset animation flags after render frame so they can be triggered fresh next step
    gs["anim_player"] = "idle"
    gs["anim_enemy"] = "idle"

    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        c_col1, c_col2, c_col3 = st.columns(3)
        
        with c_col1:
            if st.button("🗡️ Melee Strike", use_container_width=True):
                gs["anim_player"] = "anim-attack-player"
                gs["anim_enemy"] = "anim-hit"
                dmg = random.randint(gs["attack"] - 3, gs["attack"] + 5)
                enemy["hp"] -= dmg
                st.toast(f"You struck for {dmg} physical damage!")
                time.sleep(0.3)
                st.rerun()
                
        with c_col2:
            if st.button("✨ Magic Spell", use_container_width=True):
                if gs["mp"] >= 10:
                    gs["mp"] -= 10
                    gs["anim_player"] = "anim-attack-player"
                    gs["anim_enemy"] = "anim-hit"
                    mdmg = random.randint(gs["magic_power"] - 5, gs["magic_power"] + 10)
                    enemy["hp"] -= mdmg
                    st.toast(f"Arcane spell dealt {mdmg} damage!")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.warning("Not enough Mana!")
                    
        with c_col3:
            if st.button("🧪 Use Heal", use_container_width=True):
                gs["anim_player"] = "anim-heal"
                gs["hp"] = min(gs["max_hp"], gs["hp"] + 50)
                st.toast("Healed for 50 HP!")
                time.sleep(0.3)
                st.rerun()

        # Enemy Reaction & Turn Logic
        if enemy["hp"] > 0:
            if enemy.get("type") == "boss_jesus":
                enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + enemy["regen"])
                st.warning(f"Jesus uses Divine Regeneration! Recovers {enemy['regen']} HP.")
            
            # Enemy attacks player back
            if st.button("Proceed Enemy Turn"):
                gs["anim_enemy"] = "anim-attack-enemy"
                gs["anim_player"] = "anim-hit"
                edmg = random.randint(int(enemy["atk"] * 0.8), int(enemy["atk"] * 1.2))
                gs["hp"] -= edmg
                st.toast(f"{enemy['name']} hits you for {edmg} damage!")
                time.sleep(0.3)
                
                if gs["hp"] <= 0:
                    gs["anim_player"] = "anim-death"
                    gs["screen"] = "game_over"
                st.rerun()
        else:
            # Enemy Defeated / Death Animation Trigger
            gs["anim_enemy"] = "anim-death"
            st.success(f"You defeated {enemy['name']}!")
            gs["gold"] += gs["level"] * 5
            time.sleep(0.5)
            
            if gs["level"] >= gs["max_levels"]:
                gs["screen"] = "victory"
            else:
                gs["level"] += 1
                gs["screen"] = "hub"
                gs["quest_log"] = f"Cleared Stage {gs['level']-1}. Advancing deeper into the realms."
            st.rerun()

    with col_c2:
        st.subheader("Stream Visual Feed")
        st.info("Watch the tactical battle nodes. Attack frames lunge forward, damage triggers a crimson flash, healing creates a glowing aura, and kills execute a fade animation.")

# 4. GAME OVER
elif gs["screen"] == "game_over":
    st.title("💀 YOU HAVE FALLEN")
    st.write("Your physical form has been obliterated.")
    if st.button("Retry Crusade"):
        gs["level"] = 1
        gs["hp"] = 100
        gs["mp"] = 50
        gs["gold"] = 0
        gs["demon_allied"] = False
        gs["screen"] = "menu"
        st.rerun()

# 5. VICTORY SCREEN
elif gs["screen"] == "victory":
    st.title("🏆 GOD IS DEAD. YOU HAVE WON.")
    st.balloons()
    st.write("You climbed 100 levels, fought beasts, angels, apostles, Jesus, and finally destroyed the Almighty Creator.")
    if st.button("Play Again"):
        gs["level"] = 1
        gs["hp"] = 200
        gs["screen"] = "menu"
        st.rerun()
