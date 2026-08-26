import streamlit as st
import random
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kill God - RPG",
    page_icon="⚔️",
    layout="wide"
)

# --- GAME STATE INITIALIZATION ---
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "screen": "menu",  # menu, town, quest, combat, victory, game_over
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
        "enemy": None
    }

gs = st.session_state.game_state

# --- STYLING (Dark Fantasy Theme) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b0e;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #3b0909;
        color: white;
        border: 1px solid #ff4b4b;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #5c0e0e;
        border-color: #ff7676;
    }
    h1, h2, h3 {
        color: #ff4b4b;
        font-family: 'Cinzel', serif, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- ENEMY GENERATOR ENGINE ---
def get_enemy_for_level(lvl):
    if lvl < 25:
        # Phase 1: Mortal Realm / Beasts & Goblins
        names = ["Goblin Scavenger", "Feral Werewolf", "Corrupted Elf", "Dark Beast"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 40 + (lvl * 5), "max_hp": 40 + (lvl * 5), "atk": 8 + (lvl * 2), "type": "mortal"}
    elif lvl == 25:
        return {"name": "The Arch-Demon of the Abyss", "hp": 500, "max_hp": 500, "atk": 35, "type": "boss_demon"}
    elif lvl < 50:
        # Phase 2: Demonic Pact & Angelic Beasts
        names = ["Fairy of False Light", "Warlock of the Choir", "Seraphic Hound"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 120 + (lvl * 8), "max_hp": 120 + (lvl * 8), "atk": 20 + (lvl * 3), "type": "angelic"}
    elif lvl == 50:
        return {"name": "Archangel Gabriel", "hp": 1200, "max_hp": 1200, "atk": 55, "type": "boss_angel"}
    elif lvl < 75:
        # Phase 3: Prophets & Apostles
        names = ["Apostle Peter's Phantom", "False Prophet", "Heavenly Templar"]
        name = random.choice(names)
        return {"name": f"Lvl {lvl} {name}", "hp": 250 + (lvl * 12), "max_hp": 250 + (lvl * 12), "atk": 40 + (lvl * 4), "type": "prophet"}
    elif lvl == 75:
        return {"name": "Jesus of Nazareth (The Son)", "hp": 3000, "max_hp": 3000, "atk": 80, "type": "boss_jesus", "regen": 150}
    elif lvl < 100:
        # Phase 4: Higher Heavens
        return {"name": f"Lvl {lvl} Throne Guardian", "hp": 500 + (lvl * 15), "max_hp": 500 + (lvl * 15), "atk": 70 + (lvl * 5), "type": "guardian"}
    else:
        # Phase 5: Omega Boss
        return {"name": "GOD ALMIGHTY (The Creator)", "hp": 10000, "max_hp": 10000, "atk": 150, "type": "boss_god"}

# --- SCREENS ---

# 1. MAIN MENU
if gs["screen"] == "menu":
    st.title("⚔️ KILL GOD: THE REBELLION")
    st.markdown("### *From mortal mud to the gates of Heaven. The Devil is your ally.*")
    st.write("You are an outcast destined to shatter the divine hierarchy. Fight through 100 grueling quests, manage your melee and magic builds, broker dark pacts, and execute God.")
    
    if st.button("Begin Crusade"):
        gs["screen"] = "hub"
        gs["enemy"] = get_enemy_for_level(gs["level"])
        st.rerun()

# 2. SANCTUARY / HUB
elif gs["screen"] == "hub":
    st.sidebar.title("Player Status")
    st.sidebar.write(f"**Level:** {gs['level']} / {gs['max_levels']}")
    st.sidebar.write(f"**HP:** {gs['hp']} / {gs['max_hp']}")
    st.sidebar.write(f"**MP:** {gs['mp']} / {gs['max_mp']}")
    st.sidebar.write(f"**Attack (Melee):** {gs['attack']}")
    st.sidebar.write(f"**Magic Power:** {gs['magic_power']}")
    st.sidebar.write(f"**Gold:** {gs['gold']}")
    st.sidebar.write(f"**Demon Pact:** {'Active 🔥' in str(gs['demon_allied']) or ('Active' if gs['demon_allied'] else 'None')}")

    st.title(f"Quest Hub - Level {gs['level']}")
    
    if gs["level"] == 25 and not gs["demon_allied"]:
        st.warning("🔥 **The Demon Lord appears before you!** He offers an alliance to overthrow the Heavens.")
        if st.button("Form Pact with the Devil"):
            gs["demon_allied"] = True
            gs["attack"] += 20
            gs["magic_power"] += 30
            st.success("The Devil grants you Hellfire powers! Demon Alliance Active.")
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Objective")
        st.info(gs["quest_log"])
        if st.button("🚀 Embark on Next Quest", use_container_width=True):
            gs["enemy"] = get_enemy_for_level(gs["level"])
            gs["screen"] = "combat"
            st.rerun()
            
    with col2:
        st.subheader("Inventory & Upgrades")
        st.write(f"Items: {', '.join(gs['inventory'])}")
        if st.button("Rest & Heal (Cost: 20 Gold)") and gs["gold"] >= 20:
            gs["gold"] -= 20
            gs["hp"] = gs["max_hp"]
            gs["mp"] = gs["max_mp"]
            st.success("You recovered your health and mana.")
            st.rerun()

# 3. COMBAT ENGINE
elif gs["screen"] == "combat":
    st.title(f"⚔️ Combat: Quest {gs['level']}")
    enemy = gs["enemy"]
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.markdown(f"### Enemy: **{enemy['name']}**")
        st.progress(enemy["hp"] / enemy["max_hp"])
        st.write(f"Enemy HP: {enemy['hp']} / {enemy['max_hp']} | Attack: {enemy['atk']}")
        
        st.markdown("---")
        st.markdown(f"### Your Stats")
        st.progress(gs["hp"] / gs["max_hp"])
        st.write(f"Your HP: {gs['hp']} / {gs['max_hp']} | MP: {gs['mp']} / {gs['max_mp']}")
        
        # Combat Actions
        c_col1, c_col2, c_col3 = st.columns(3)
        
        with c_col1:
            if st.button("🗡️ Melee Strike", use_container_width=True):
                dmg = random.randint(gs["attack"] - 3, gs["attack"] + 5)
                enemy["hp"] -= dmg
                st.toast(f"You struck for {dmg} physical damage!")
                
        with c_col2:
            if st.button("✨ Magic Spell", use_container_width=True):
                if gs["mp"] >= 10:
                    gs["mp"] -= 10
                    mdmg = random.randint(gs["magic_power"] - 5, gs["magic_power"] + 10)
                    enemy["hp"] -= mdmg
                    st.toast(f"Your spell dealt {mdmg} arcane damage!")
                else:
                    st.warning("Not enough Mana!")
                    
        with c_col3:
            if st.button("🧪 Drink Potion", use_container_width=True):
                if "Minor Mana Potion" in gs["inventory"] or gs["gold"] >= 10:
                    gs["hp"] = min(gs["max_hp"], gs["hp"] + 40)
                    st.toast("Restored 40 HP!")
                else:
                    st.warning("No potions available!")

        # Boss / Enemy turn execution logic
        if enemy["hp"] > 0:
            # Special Boss Mechanics
            if enemy.get("type") == "boss_jesus":
                enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + enemy["regen"])
                st.warning(f"Jesus uses Divine Regeneration! He recovers {enemy['regen']} HP.")
            
            # Regular Enemy Attack
            edmg = random.randint(int(enemy["atk"] * 0.8), int(enemy["atk"] * 1.2))
            gs["hp"] -= edmg
            st.warning(f"{enemy['name']} counterattacks and deals {edmg} damage to you!")
            
            if gs["hp"] <= 0:
                gs["screen"] = "game_over"
                st.rerun()
        else:
            # Victory against current enemy
            st.success(f"You defeated {enemy['name']}!")
            gs["gold"] += gs["level"] * 5
            
            if gs["level"] >= gs["max_levels"]:
                gs["screen"] = "victory"
            else:
                gs["level"] += 1
                gs["screen"] = "hub"
                gs["quest_log"] = f"Progressed past level {gs['level']-1}. The path upward continues."
            st.rerun()

    with col_c2:
        st.subheader("Battle Log")
        st.info(f"Fighting against {enemy['name']}. Choose your moves wisely. Combine melee combos with demon magic to bypass angelic shields.")

# 4. GAME OVER
elif gs["screen"] == "game_over":
    st.title("💀 YOU HAVE FALLEN")
    st.write("Your soul has been cast into the void. God's dominion remains unchallenged... for now.")
    if st.button("Try Again"):
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
    st.write("You climbed 100 tiers of reality, forged a pact with Hell, dismantled the angelic hosts, crushed the prophets, bypassed Jesus's regeneration, and struck down the Creator Himself.")
    st.write("The cosmos is yours to remake.")
    if st.button("Play Again (New Game+)"):
        gs["level"] = 1
        gs["hp"] = 200
        gs["max_hp"] = 200
        gs["screen"] = "menu"
        st.rerun()
