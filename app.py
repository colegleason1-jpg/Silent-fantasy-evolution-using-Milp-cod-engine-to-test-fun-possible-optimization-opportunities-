"""
KILL GOD: THE REBELLION
========================
A 100-quest dark fantasy RPG built with Streamlit.

Premise:
  You are a mortal outcast. You climb from the mud of the fantasy realm,
  fighting goblins, werewolves and corrupted elves, until the Devil himself
  offers you a pact. Empowered by Hell, you march upward through choirs of
  false angels, the twelve Apostles, and finally the Son and the Father
  themselves, to shatter the divine hierarchy for good.

Systems:
  - Turn-based combat with melee / magic / skills / items
  - Equipment (weapons + armor) purchased at the Sanctuary shop
  - A skill tree with Melee and Arcane/Demonic branches
  - Status effects: Poison, Stun, Shield, Regeneration, Burn
  - 4 phases of 25 quests each, with named mini-boss and boss fights
  - Multi-phase final battle against God Almighty
  - Achievements + a persistent run log

Run with:  streamlit run kill_god_rpg.py
"""

import streamlit as st
import random

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Kill God - RPG",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# STYLING (Dark Fantasy Theme)
# =====================================================================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #14060a 0%, #0b0b0e 60%);
        color: #e6dcd0;
    }
    .stButton>button {
        background-color: #3b0909;
        color: #f2e6d8;
        border: 1px solid #ff4b4b;
        border-radius: 6px;
        font-weight: 700;
        letter-spacing: 0.3px;
        transition: all 0.15s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #6e0f0f;
        border-color: #ffb86c;
        color: #fff3e0;
    }
    .stButton>button:disabled {
        opacity: 0.35;
    }
    h1, h2, h3 {
        color: #ff4b4b;
        font-family: 'Cinzel', 'Georgia', serif;
        text-shadow: 0 0 12px rgba(255, 75, 75, 0.25);
    }
    .phase-mortal   { color: #c9a86a; }
    .phase-angelic  { color: #9fd3ff; }
    .phase-prophet  { color: #e0c48c; }
    .phase-heaven   { color: #ffffff; }
    .boss-banner {
        border: 1px solid #ff4b4b;
        border-radius: 8px;
        padding: 10px 16px;
        background: linear-gradient(90deg, rgba(120,0,0,0.35), rgba(0,0,0,0));
        margin-bottom: 10px;
    }
    .log-line { font-size: 0.92rem; opacity: 0.92; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# STATIC GAME DATA
# =====================================================================

MAX_LEVEL = 100

# ---- Equipment -------------------------------------------------------
WEAPONS = {
    "Rusty Sword":        {"atk": 0,  "cost": 0,   "req": 1,  "desc": "A pitted blade. Better than fists, barely."},
    "Iron Longsword":      {"atk": 8,  "cost": 60,  "req": 3,  "desc": "Honest steel, honestly sharpened."},
    "Werewolf Fang Blade":  {"atk": 14, "cost": 140, "req": 8,  "desc": "Carved from a beast's own jaw."},
    "Elven Moonsteel Rapier": {"atk": 20, "cost": 260, "req": 15, "desc": "Stolen from a corrupted elf lord."},
    "Hellforged Cleaver":   {"atk": 32, "cost": 420, "req": 26, "desc": "Quenched in the Devil's own blood."},
    "Seraph-Slayer Glaive": {"atk": 46, "cost": 650, "req": 40, "desc": "Forged to cut through holy light itself."},
    "Apostle's Broken Cross": {"atk": 60, "cost": 900, "req": 58, "desc": "A relic weapon, reforged as a weapon of war."},
    "Excalibur, Inverted":  {"atk": 78, "cost": 1300, "req": 74, "desc": "The blade of kings, turned against Heaven."},
    "Godsbane":             {"atk": 100, "cost": 1900, "req": 90, "desc": "There is only one thing left worth killing."},
}

ARMORS = {
    "Tattered Cloak":       {"hp": 0,  "cost": 0,   "req": 1,  "desc": "Barely stops the wind."},
    "Boiled Leather":       {"hp": 30, "cost": 60,  "req": 3,  "desc": "Cheap, but it's saved you before."},
    "Chainmail Hauberk":    {"hp": 60, "cost": 150, "req": 8,  "desc": "Heavy, reliable, dependable."},
    "Elven Warded Plate":   {"hp": 100, "cost": 280, "req": 15, "desc": "Enchantments still flicker across it."},
    "Demonhide Vestment":   {"hp": 160, "cost": 430, "req": 26, "desc": "A gift, sewn from the Devil's own retinue."},
    "Choir-Breaker Plate":  {"hp": 220, "cost": 660, "req": 40, "desc": "Built to survive a hymn of judgement."},
    "Martyr's Aegis":       {"hp": 300, "cost": 900, "req": 58, "desc": "Once worn by a saint. Not anymore."},
    "Armor of the Fallen Choir": {"hp": 400, "cost": 1300, "req": 74, "desc": "Feathers of a thousand cast-out angels."},
    "Aegis of the Usurper": {"hp": 550, "cost": 1900, "req": 90, "desc": "Made to withstand the wrath of Heaven's throne."},
}

# ---- Consumables -------------------------------------------------------
CONSUMABLES = {
    "Minor Mana Potion":  {"type": "mp", "amount": 25, "cost": 20, "desc": "Restores a modest pool of mana."},
    "Health Draught":     {"type": "hp", "amount": 50, "cost": 25, "desc": "Bitter, but it closes wounds fast."},
    "Greater Elixir":     {"type": "full", "amount": 0, "cost": 90, "desc": "Fully restores HP and MP."},
    "Cleansing Herb":     {"type": "cleanse", "amount": 0, "cost": 35, "desc": "Removes poison, stun, and burn."},
    "Phoenix Down":       {"type": "revive", "amount": 0, "cost": 150, "desc": "Cheats death once, mid-battle."},
}

# ---- Skill Tree -------------------------------------------------------
# type: melee / magic / demonic
SKILLS = {
    "power_strike": {
        "name": "Power Strike", "branch": "melee", "cost_sp": 1, "mp_cost": 0,
        "unlock_level": 1, "power_mult": 1.6,
        "desc": "A heavy blow relying on raw strength.",
    },
    "whirlwind": {
        "name": "Whirlwind Slash", "branch": "melee", "cost_sp": 2, "mp_cost": 5,
        "unlock_level": 10, "power_mult": 2.1,
        "desc": "Spin through your enemy's guard.",
    },
    "executioners_arc": {
        "name": "Executioner's Arc", "branch": "melee", "cost_sp": 3, "mp_cost": 10,
        "unlock_level": 30, "power_mult": 2.8,
        "desc": "A finishing strike that ignores half of enemy defense.",
    },
    "arcane_bolt": {
        "name": "Arcane Bolt", "branch": "magic", "cost_sp": 1, "mp_cost": 8,
        "unlock_level": 1, "power_mult": 1.7,
        "desc": "A basic bolt of raw arcane force.",
    },
    "fireball": {
        "name": "Fireball", "branch": "magic", "cost_sp": 2, "mp_cost": 14,
        "unlock_level": 12, "power_mult": 2.3, "burn": True,
        "desc": "Explosive fire that leaves the enemy burning.",
    },
    "mind_shatter": {
        "name": "Mind Shatter", "branch": "magic", "cost_sp": 3, "mp_cost": 20,
        "unlock_level": 35, "power_mult": 2.6, "stun": True,
        "desc": "Overloads the enemy's mind, has a chance to stun.",
    },
    "hellfire_nova": {
        "name": "Hellfire Nova", "branch": "demonic", "cost_sp": 3, "mp_cost": 22,
        "unlock_level": 26, "power_mult": 3.2, "burn": True, "requires_pact": True,
        "desc": "Unholy fire granted by your pact with the Devil.",
    },
    "abyssal_grip": {
        "name": "Abyssal Grip", "branch": "demonic", "cost_sp": 4, "mp_cost": 18,
        "unlock_level": 45, "power_mult": 2.4, "stun": True, "requires_pact": True,
        "desc": "Chains of shadow drag the enemy still.",
    },
    "kings_ruin": {
        "name": "The King's Ruin", "branch": "demonic", "cost_sp": 6, "mp_cost": 35,
        "unlock_level": 70, "power_mult": 4.0, "requires_pact": True,
        "desc": "A cataclysmic strike, borrowed straight from Hell's throne.",
    },
}

# ---- Enemy pools by phase ----------------------------------------------
PHASE1_POOL = [  # levels 1-24: mortal beasts
    {"name": "Goblin Scavenger", "hp": 38, "atk": 7, "ability": None},
    {"name": "Feral Werewolf", "hp": 52, "atk": 10, "ability": None},
    {"name": "Corrupted Elf Archer", "hp": 44, "atk": 9, "ability": "poison"},
    {"name": "Dark Beast", "hp": 60, "atk": 11, "ability": None},
    {"name": "Bandit Cutthroat", "hp": 40, "atk": 8, "ability": None},
    {"name": "Cave Spider Broodmother", "hp": 46, "atk": 9, "ability": "poison"},
    {"name": "Restless Wraith", "hp": 50, "atk": 12, "ability": "stun"},
    {"name": "Hill Troll", "hp": 75, "atk": 13, "ability": None},
    {"name": "Screeching Harpy", "hp": 42, "atk": 10, "ability": None},
    {"name": "Blood Cultist", "hp": 48, "atk": 9, "ability": "burn"},
]

PHASE2_POOL = [  # levels 26-49: angelic/demonic hybrids
    {"name": "Fairy of False Light", "hp": 140, "atk": 24, "ability": "stun"},
    {"name": "Warlock of the Choir", "hp": 155, "atk": 26, "ability": "burn"},
    {"name": "Seraphic Hound", "hp": 165, "atk": 28, "ability": None},
    {"name": "Cherub Swarm", "hp": 120, "atk": 22, "ability": "poison"},
    {"name": "Fallen Watcher", "hp": 175, "atk": 27, "ability": None},
    {"name": "Choir Acolyte", "hp": 145, "atk": 23, "ability": None},
    {"name": "Radiant Imp (Allied)", "hp": 130, "atk": 21, "ability": "burn"},
    {"name": "Hymnal Construct", "hp": 190, "atk": 30, "ability": "stun"},
]

PHASE3_POOL = [  # levels 51-74: prophets and disciples
    {"name": "Apostle's Zealous Phantom", "hp": 320, "atk": 46, "ability": "burn"},
    {"name": "False Prophet", "hp": 300, "atk": 44, "ability": "poison"},
    {"name": "Heavenly Templar", "hp": 360, "atk": 50, "ability": None},
    {"name": "Chorister of Judgement", "hp": 330, "atk": 47, "ability": "stun"},
    {"name": "Martyr Reborn", "hp": 340, "atk": 48, "ability": None},
    {"name": "Inquisition Paladin", "hp": 370, "atk": 52, "ability": "burn"},
]

PHASE4_POOL = [  # levels 76-99: higher heaven
    {"name": "Throne Guardian", "hp": 620, "atk": 78, "ability": "stun"},
    {"name": "Dominion Sentinel", "hp": 650, "atk": 82, "ability": None},
    {"name": "Principality Warbringer", "hp": 680, "atk": 85, "ability": "burn"},
    {"name": "Virtue of the Last Choir", "hp": 700, "atk": 88, "ability": "poison"},
    {"name": "Power, Unbound", "hp": 730, "atk": 92, "ability": None},
]

# ---- Named boss / mini-boss encounters (fixed levels) -------------------
def boss_arch_demon():
    return {"name": "The Arch-Demon of the Abyss", "hp": 500, "atk": 35,
            "type": "boss_demon", "ability": "burn",
            "intro": "A crack splits the sky. The Arch-Demon descends, curious rather than hostile."}

def boss_gabriel():
    return {"name": "Archangel Gabriel", "hp": 1400, "atk": 60,
            "type": "boss_angel", "ability": "stun", "summons": True,
            "intro": "Gabriel's trumpet sounds. Lesser angels flock to his call."}

def boss_apostle(name, hp, atk, ability):
    return {"name": name, "hp": hp, "atk": atk, "type": "boss_apostle", "ability": ability,
            "intro": f"{name} bars your path, radiant with borrowed authority."}

def boss_michael():
    return {"name": "Archangel Michael, the Swordbearer", "hp": 2600, "atk": 95,
            "type": "boss_angel", "ability": "burn", "summons": True,
            "intro": "Michael descends in full battle-glory, blade already drawn."}

def boss_raphael():
    return {"name": "Archangel Raphael, the Healer", "hp": 2800, "atk": 90,
            "type": "boss_angel", "ability": None, "regen": 220,
            "intro": "Raphael's light mends the world around him as he fights."}

def boss_jesus():
    return {"name": "Jesus of Nazareth (The Son)", "hp": 4200, "atk": 100,
            "type": "boss_jesus", "ability": None, "regen": 180,
            "intro": "He does not raise a weapon. He does not need to."}

def boss_god():
    return {"name": "GOD ALMIGHTY (The Creator)", "hp": 14000, "atk": 165,
            "type": "boss_god", "ability": "stun", "phase": 1,
            "intro": "Reality itself holds its breath. There is nowhere left to climb but here."}

FIXED_BOSSES = {
    25: boss_arch_demon,
    50: boss_gabriel,
    55: lambda: boss_apostle("Apostle Peter's Phantom", 700, 62, "stun"),
    60: lambda: boss_apostle("Apostle Paul, the Zealot Reborn", 780, 66, "burn"),
    65: lambda: boss_apostle("Apostle John, the Revelator", 860, 70, "poison"),
    70: lambda: boss_apostle("Apostle Judas, the Betrayer's Ghost", 940, 76, None),
    75: boss_jesus,
    85: boss_michael,
    95: boss_raphael,
    100: boss_god,
}

BOSS_LEVELS = set(FIXED_BOSSES.keys())

ACHIEVEMENTS = {
    "first_blood":   "First Blood - Win your first battle",
    "pact_sealed":   "Pact Sealed - Ally with the Devil",
    "fall_of_heaven": "Fall of Heaven - Defeat Archangel Gabriel",
    "twelve_silenced": "Twelve Silenced - Defeat all four Apostle bosses",
    "son_undone":    "The Son, Undone - Defeat Jesus of Nazareth",
    "swordbearer_broken": "Swordbearer Broken - Defeat Archangel Michael",
    "healer_stilled": "Healer, Stilled - Defeat Archangel Raphael",
    "deicide":       "Deicide - Defeat God Almighty and finish the game",
    "well_equipped": "Well Equipped - Own a full matching gear set",
    "close_call":    "Close Call - Win a battle with 5 HP or less remaining",
}


# =====================================================================
# GAME STATE
# =====================================================================
def new_game_state():
    return {
        "screen": "menu",
        "level": 1,
        "hp": 100, "max_hp": 100,
        "mp": 50, "max_mp": 50,
        "base_attack": 15, "base_magic": 20,
        "gold": 30,
        "skill_points": 1,
        "demon_allied": False,
        "weapon": "Rusty Sword",
        "armor": "Tattered Cloak",
        "inventory": {"Minor Mana Potion": 2, "Health Draught": 2},
        "skills_unlocked": [],
        "quest_log": "Awaken in the mortal realm. Slay the beasts that hunt travelers on the low road.",
        "enemy": None,
        "enemy_status": {},
        "player_status": {},
        "combat_log": [],
        "achievements": set(),
        "apostles_defeated": 0,
        "used_phoenix_this_fight": False,
        "class_choice": None,
    }


if "game_state" not in st.session_state:
    st.session_state.game_state = new_game_state()

gs = st.session_state.game_state


def grant_achievement(key):
    if key not in gs["achievements"]:
        gs["achievements"].add(key)
        st.toast(f"🏆 Achievement unlocked: {ACHIEVEMENTS[key]}")


def total_attack():
    return gs["base_attack"] + WEAPONS[gs["weapon"]]["atk"]


def total_magic():
    return gs["base_magic"] + (10 if gs["demon_allied"] else 0)


def total_max_hp():
    return gs["max_hp"] + ARMORS[gs["armor"]]["hp"]


def log(msg):
    gs["combat_log"].append(msg)
    gs["combat_log"] = gs["combat_log"][-14:]


# =====================================================================
# ENEMY GENERATION
# =====================================================================
def phase_for_level(lvl):
    if lvl <= 25:
        return 1
    if lvl <= 50:
        return 2
    if lvl <= 75:
        return 3
    return 4


def get_enemy_for_level(lvl):
    if lvl in FIXED_BOSSES:
        boss = FIXED_BOSSES[lvl]()
        boss["max_hp"] = boss["hp"]
        boss["is_boss"] = True
        return boss

    phase = phase_for_level(lvl)
    pool = {1: PHASE1_POOL, 2: PHASE2_POOL, 3: PHASE3_POOL, 4: PHASE4_POOL}[phase]
    template = random.choice(pool)
    scale = 1 + (lvl * 0.045)
    enemy = {
        "name": f"Lvl {lvl} {template['name']}",
        "hp": int(template["hp"] * scale),
        "max_hp": int(template["hp"] * scale),
        "atk": int(template["atk"] * scale),
        "ability": template["ability"],
        "type": "regular",
        "is_boss": False,
    }
    return enemy


PHASE_CLASS = {1: "phase-mortal", 2: "phase-angelic", 3: "phase-prophet", 4: "phase-heaven"}


# =====================================================================
# COMBAT MECHANICS
# =====================================================================
def apply_ability_to_player(ability):
    if ability == "poison":
        gs["player_status"]["poison"] = gs["player_status"].get("poison", 0) + 3
        log("You've been poisoned!")
    elif ability == "stun" and random.random() < 0.35:
        gs["player_status"]["stunned"] = True
        log("You are stunned and stumble!")
    elif ability == "burn":
        gs["player_status"]["burn"] = gs["player_status"].get("burn", 0) + 3
        log("Flames catch on your armor!")


def apply_ability_to_enemy(enemy, ability):
    if ability == "burn":
        gs["enemy_status"]["burn"] = gs["enemy_status"].get("burn", 0) + 3
    elif ability == "stun" and random.random() < 0.30:
        gs["enemy_status"]["stunned"] = True
        log(f"{enemy['name']} is stunned!")


def tick_status(status_dict, target_hp_key, is_player):
    """Apply DOT effects at the start of a turn. Returns updated hp."""
    dmg = 0
    if status_dict.get("poison", 0) > 0:
        dmg += 6
        status_dict["poison"] -= 1
    if status_dict.get("burn", 0) > 0:
        dmg += 8
        status_dict["burn"] -= 1
    if dmg > 0:
        who = "You take" if is_player else f"{gs['enemy']['name']} takes"
        log(f"{who} {dmg} damage from lingering effects.")
    return dmg


def player_action_melee():
    atk = total_attack()
    dmg = random.randint(max(1, atk - 4), atk + 6)
    gs["enemy"]["hp"] -= dmg
    log(f"You strike with your {gs['weapon']} for {dmg} physical damage!")


def player_action_magic():
    cost = 10
    if gs["mp"] < cost:
        st.warning("Not enough Mana!")
        return False
    gs["mp"] -= cost
    mag = total_magic()
    dmg = random.randint(max(1, mag - 5), mag + 10)
    gs["enemy"]["hp"] -= dmg
    log(f"Your spell sears the enemy for {dmg} arcane damage!")
    return True


def player_action_skill(skill_id):
    skill = SKILLS[skill_id]
    if gs["mp"] < skill["mp_cost"]:
        st.warning("Not enough Mana for that skill!")
        return False
    gs["mp"] -= skill["mp_cost"]
    base = total_attack() if skill["branch"] == "melee" else total_magic()
    dmg = int(random.randint(int(base * 0.9), int(base * 1.1)) * skill["power_mult"])
    gs["enemy"]["hp"] -= dmg
    log(f"You unleash {skill['name']} for {dmg} damage!")
    if skill.get("burn"):
        apply_ability_to_enemy(gs["enemy"], "burn")
        log(f"{gs['enemy']['name']} is set ablaze!")
    if skill.get("stun") and random.random() < 0.45:
        gs["enemy_status"]["stunned"] = True
        log(f"{gs['enemy']['name']} reels, stunned!")
    return True


def use_item(item_name):
    item = CONSUMABLES[item_name]
    if gs["inventory"].get(item_name, 0) <= 0:
        return False
    if item["type"] == "hp":
        gs["hp"] = min(total_max_hp(), gs["hp"] + item["amount"])
        log(f"You drink a {item_name}, restoring {item['amount']} HP.")
    elif item["type"] == "mp":
        gs["mp"] = min(gs["max_mp"], gs["mp"] + item["amount"])
        log(f"You drink a {item_name}, restoring {item['amount']} MP.")
    elif item["type"] == "full":
        gs["hp"] = total_max_hp()
        gs["mp"] = gs["max_mp"]
        log(f"The {item_name} fully restores your HP and MP.")
    elif item["type"] == "cleanse":
        gs["player_status"] = {}
        log(f"The {item_name} burns away every lingering ailment.")
    elif item["type"] == "revive":
        gs["used_phoenix_this_fight"] = "ready"
        log("A Phoenix Down glows faintly in your hand, ready if you fall.")
    gs["inventory"][item_name] -= 1
    return True


def enemy_turn():
    enemy = gs["enemy"]
    if enemy["hp"] <= 0:
        return

    if gs["enemy_status"].get("stunned"):
        log(f"{enemy['name']} is stunned and cannot act!")
        gs["enemy_status"]["stunned"] = False
        return

    # Boss-specific behavior
    etype = enemy.get("type")
    if etype == "boss_jesus" and enemy.get("regen"):
        heal = enemy["regen"]
        enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + heal)
        log(f"Jesus calls on Divine Regeneration, recovering {heal} HP.")
    elif etype == "boss_angel" and enemy.get("regen"):
        heal = enemy["regen"]
        enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + heal)
        log(f"{enemy['name']} mends himself, recovering {heal} HP.")
    elif etype == "boss_angel" and enemy.get("summons") and random.random() < 0.25:
        chip = random.randint(8, 16)
        gs["hp"] -= chip
        log(f"{enemy['name']} summons lesser angels! They chip {chip} extra damage.")
    elif etype == "boss_god":
        _god_phase_check(enemy)

    edmg = random.randint(int(enemy["atk"] * 0.8), int(enemy["atk"] * 1.2))
    gs["hp"] -= edmg
    log(f"{enemy['name']} strikes back for {edmg} damage!")

    if enemy.get("ability"):
        apply_ability_to_player(enemy["ability"])


def _god_phase_check(enemy):
    """God Almighty has multiple escalating phases as HP drops."""
    ratio = enemy["hp"] / enemy["max_hp"]
    phase = enemy.get("phase", 1)
    if ratio < 0.66 and phase == 1:
        enemy["phase"] = 2
        enemy["atk"] = int(enemy["atk"] * 1.25)
        log("⚡ GOD ALMIGHTY unleashes the Second Verse. His wrath intensifies.")
    elif ratio < 0.33 and phase == 2:
        enemy["phase"] = 3
        enemy["atk"] = int(enemy["atk"] * 1.35)
        log("⚡ GOD ALMIGHTY speaks the Final Word. The battlefield itself trembles.")


def resolve_death_or_continue():
    """Called after damage is dealt, before enemy turn, to check for enemy death."""
    enemy = gs["enemy"]
    if enemy["hp"] <= 0:
        handle_victory_against_enemy()
        return True
    return False


def handle_victory_against_enemy():
    enemy = gs["enemy"]
    lvl = gs["level"]
    gold_gain = lvl * 5 + (enemy["max_hp"] // 20 if enemy.get("is_boss") else 0)
    gs["gold"] += gold_gain
    log(f"You defeated {enemy['name']}! (+{gold_gain} gold)")

    if "first_blood" not in gs["achievements"]:
        grant_achievement("first_blood")
    if gs["hp"] <= 5:
        grant_achievement("close_call")

    if enemy.get("type") == "boss_angel" and enemy["name"].startswith("Archangel Gabriel"):
        grant_achievement("fall_of_heaven")
    if enemy.get("type") == "boss_apostle":
        gs["apostles_defeated"] += 1
        if gs["apostles_defeated"] >= 4:
            grant_achievement("twelve_silenced")
    if enemy.get("type") == "boss_jesus":
        grant_achievement("son_undone")
    if enemy.get("name", "").startswith("Archangel Michael"):
        grant_achievement("swordbearer_broken")
    if enemy.get("name", "").startswith("Archangel Raphael"):
        grant_achievement("healer_stilled")
    if enemy.get("type") == "boss_god":
        grant_achievement("deicide")
        gs["screen"] = "victory"
        return

    gs["skill_points"] += 1
    if lvl % 3 == 0:
        gs["max_hp"] += 8
        gs["max_mp"] += 4
        gs["base_attack"] += 2
        gs["base_magic"] += 2
        log("Your ordeal has strengthened you. Base stats increased.")

    gs["enemy_status"] = {}
    gs["player_status"] = {}
    gs["used_phoenix_this_fight"] = False

    if lvl >= MAX_LEVEL:
        gs["screen"] = "victory"
    else:
        gs["level"] += 1
        gs["screen"] = "hub"
        gs["quest_log"] = quest_flavor_for_level(gs["level"])


def quest_flavor_for_level(lvl):
    phase = phase_for_level(lvl)
    if lvl in BOSS_LEVELS:
        return f"A power beyond the ordinary bars your path at quest {lvl}. Prepare yourself."
    flavor = {
        1: "Beasts and outlaws thin the roads. Clear them.",
        2: "Fresh from your pact, the Devil's chosen enemies await: false angels and choirs of light.",
        3: "The Apostles and their zealots stand between you and the higher heavens.",
        4: "Only the throne itself, and its last guardians, remain.",
    }[phase]
    return f"Quest {lvl}: {flavor}"


def check_player_death():
    if gs["hp"] > 0:
        return False
    if gs.get("used_phoenix_this_fight") == "ready":
        gs["hp"] = total_max_hp() // 2
        gs["used_phoenix_this_fight"] = "spent"
        log("🔥 The Phoenix Down ignites! You are dragged back from death's door.")
        return False
    gs["screen"] = "game_over"
    return True


# =====================================================================
# SIDEBAR
# =====================================================================
def render_sidebar():
    st.sidebar.title("⚔️ Player Status")
    st.sidebar.write(f"**Quest:** {gs['level']} / {MAX_LEVEL}")
    st.sidebar.progress(min(1.0, gs["hp"] / max(1, total_max_hp())), text=f"HP {max(0, gs['hp'])}/{total_max_hp()}")
    st.sidebar.progress(min(1.0, gs["mp"] / max(1, gs["max_mp"])), text=f"MP {max(0, gs['mp'])}/{gs['max_mp']}")
    st.sidebar.write(f"**Attack:** {total_attack()}  |  **Magic:** {total_magic()}")
    st.sidebar.write(f"**Gold:** {gs['gold']} 🪙")
    st.sidebar.write(f"**Skill Points:** {gs['skill_points']}")
    st.sidebar.write(f"**Weapon:** {gs['weapon']}")
    st.sidebar.write(f"**Armor:** {gs['armor']}")
    st.sidebar.write(f"**Demon Pact:** {'Active 🔥' if gs['demon_allied'] else 'None'}")
    if gs["achievements"]:
        with st.sidebar.expander(f"🏆 Achievements ({len(gs['achievements'])}/{len(ACHIEVEMENTS)})"):
            for key in gs["achievements"]:
                st.write(f"- {ACHIEVEMENTS[key]}")


# =====================================================================
# SCREENS
# =====================================================================
def screen_menu():
    st.title("⚔️ KILL GOD: THE REBELLION")
    st.markdown("### *From mortal mud to the gates of Heaven. The Devil is your ally.*")
    st.write(
        "You are an outcast destined to shatter the divine hierarchy. Fight through "
        "100 grueling quests, manage your melee and magic builds, broker a pact with Hell, "
        "silence the Apostles, break the Archangels, undo the Son, and finally climb the "
        "throne to strike down the Creator Himself."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Choose your calling")
        choice = st.radio(
            "This shapes your starting stats — you can still learn every skill later.",
            ["Warrior (High Attack, High HP)", "Battlemage (High Magic, High MP)", "Duelist (Balanced)"],
        )
    with col2:
        st.subheader("The Vow")
        st.info(gs.get("quest_log", "Awaken in the mortal realm. Slay the beasts."))

    if st.button("Begin Crusade", use_container_width=True, type="primary"):
        fresh = new_game_state()
        if choice.startswith("Warrior"):
            fresh["base_attack"] += 6
            fresh["max_hp"] += 25
            fresh["class_choice"] = "warrior"
        elif choice.startswith("Battlemage"):
            fresh["base_magic"] += 10
            fresh["max_mp"] += 20
            fresh["class_choice"] = "battlemage"
        else:
            fresh["base_attack"] += 3
            fresh["base_magic"] += 3
            fresh["class_choice"] = "duelist"
        fresh["hp"] = fresh["max_hp"]
        fresh["mp"] = fresh["max_mp"]
        fresh["screen"] = "hub"
        fresh["enemy"] = get_enemy_for_level(1)
        st.session_state.game_state = fresh
        st.rerun()


def screen_hub():
    render_sidebar()
    st.title(f"🏰 The Sanctuary — Quest {gs['level']}")

    if gs["level"] == 25 and not gs["demon_allied"]:
        st.markdown('<div class="boss-banner">', unsafe_allow_html=True)
        st.warning("🔥 **The Arch-Demon offers a pact.** Ally with Hell to overthrow the Heavens?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Form Pact with the Devil", use_container_width=True):
                gs["demon_allied"] = True
                gs["base_attack"] += 10
                gs["base_magic"] += 15
                grant_achievement("pact_sealed")
                st.success("The Devil grants you Hellfire powers! Demon Alliance Active.")
                st.rerun()
        with c2:
            if st.button("Refuse the Pact (harder run)", use_container_width=True):
                st.info("You refuse. The road ahead grows steeper without demonic aid.")
                gs["demon_allied"] = False
        st.markdown('</div>', unsafe_allow_html=True)

    phase = phase_for_level(gs["level"])
    css_class = PHASE_CLASS[phase]
    st.markdown(f'<p class="{css_class}">Phase {phase} of 4</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Current Objective")
        st.info(gs["quest_log"])
        label = "⚔️ Face the Boss" if gs["level"] in BOSS_LEVELS else "🚀 Embark on Next Quest"
        if st.button(label, use_container_width=True, type="primary"):
            gs["enemy"] = get_enemy_for_level(gs["level"])
            gs["enemy_status"] = {}
            gs["player_status"] = {}
            gs["combat_log"] = []
            gs["used_phoenix_this_fight"] = False
            gs["screen"] = "combat"
            st.rerun()

    with col2:
        st.subheader("Rest")
        st.write("Recover before the next quest.")
        cost = 20
        if st.button(f"Rest & Heal (Cost: {cost} Gold)", use_container_width=True):
            if gs["gold"] >= cost:
                gs["gold"] -= cost
                gs["hp"] = total_max_hp()
                gs["mp"] = gs["max_mp"]
                gs["player_status"] = {}
                st.success("You recovered your health and mana.")
                st.rerun()
            else:
                st.warning("Not enough gold to rest.")

    with col3:
        st.subheader("Navigate")
        if st.button("🛒 Visit the Shop", use_container_width=True):
            gs["screen"] = "shop"
            st.rerun()
        if st.button("🌟 Skill Tree", use_container_width=True):
            gs["screen"] = "skills"
            st.rerun()

    st.divider()
    st.subheader("Inventory")
    if gs["inventory"]:
        inv_str = ", ".join(f"{name} x{qty}" for name, qty in gs["inventory"].items() if qty > 0)
        st.write(inv_str if inv_str else "Empty.")
    else:
        st.write("Empty.")


def screen_shop():
    render_sidebar()
    st.title("🛒 The Black Market of the Sanctuary")
    if st.button("⬅ Back to Sanctuary"):
        gs["screen"] = "hub"
        st.rerun()

    tab_w, tab_a, tab_c = st.tabs(["Weapons", "Armor", "Consumables"])

    with tab_w:
        for name, data in WEAPONS.items():
            owned = gs["weapon"] == name
            locked = gs["level"] < data["req"]
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(f"**{name}** — ATK +{data['atk']}  \n*{data['desc']}*")
            cols[1].write(f"{data['cost']}g")
            cols[2].write(f"Req Lv.{data['req']}")
            btn_label = "Equipped" if owned else ("Locked" if locked else ("Equip (Owned)" if data["cost"] == 0 else f"Buy & Equip"))
            if cols[3].button(btn_label, key=f"buy_w_{name}", disabled=owned or locked):
                if gs["gold"] >= data["cost"]:
                    gs["gold"] -= data["cost"]
                    gs["weapon"] = name
                    st.rerun()
                else:
                    st.warning("Not enough gold.")

    with tab_a:
        for name, data in ARMORS.items():
            owned = gs["armor"] == name
            locked = gs["level"] < data["req"]
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(f"**{name}** — HP +{data['hp']}  \n*{data['desc']}*")
            cols[1].write(f"{data['cost']}g")
            cols[2].write(f"Req Lv.{data['req']}")
            btn_label = "Equipped" if owned else ("Locked" if locked else "Buy & Equip")
            if cols[3].button(btn_label, key=f"buy_a_{name}", disabled=owned or locked):
                if gs["gold"] >= data["cost"]:
                    gs["gold"] -= data["cost"]
                    gs["armor"] = name
                    st.rerun()
                else:
                    st.warning("Not enough gold.")

    with tab_c:
        for name, data in CONSUMABLES.items():
            cols = st.columns([3, 1, 2])
            cols[0].write(f"**{name}** — *{data['desc']}*")
            cols[1].write(f"{data['cost']}g")
            if cols[2].button("Buy", key=f"buy_c_{name}"):
                if gs["gold"] >= data["cost"]:
                    gs["gold"] -= data["cost"]
                    gs["inventory"][name] = gs["inventory"].get(name, 0) + 1
                    st.rerun()
                else:
                    st.warning("Not enough gold.")


def screen_skills():
    render_sidebar()
    st.title("🌟 Skill Tree")
    st.write(f"Available Skill Points: **{gs['skill_points']}**")
    if st.button("⬅ Back to Sanctuary"):
        gs["screen"] = "hub"
        st.rerun()

    branches = {"melee": "⚔️ Melee Path", "magic": "✨ Arcane Path", "demonic": "🔥 Demonic Path (requires pact)"}
    for branch, title in branches.items():
        st.subheader(title)
        for skill_id, skill in SKILLS.items():
            if skill["branch"] != branch:
                continue
            unlocked = skill_id in gs["skills_unlocked"]
            level_ok = gs["level"] >= skill["unlock_level"]
            pact_ok = (not skill.get("requires_pact")) or gs["demon_allied"]
            can_learn = level_ok and pact_ok and gs["skill_points"] >= skill["cost_sp"] and not unlocked
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(f"**{skill['name']}** — *{skill['desc']}*")
            cols[1].write(f"{skill['cost_sp']} SP")
            cols[2].write(f"MP {skill['mp_cost']}")
            label = "Learned" if unlocked else ("Learn" if can_learn else f"Req Lv.{skill['unlock_level']}")
            if cols[3].button(label, key=f"skill_{skill_id}", disabled=not can_learn):
                gs["skill_points"] -= skill["cost_sp"]
                gs["skills_unlocked"].append(skill_id)
                st.rerun()


def screen_combat():
    render_sidebar()
    enemy = gs["enemy"]
    is_boss = enemy.get("is_boss")

    if is_boss:
        st.markdown('<div class="boss-banner">', unsafe_allow_html=True)
        st.title(f"👑 BOSS: {enemy['name']}")
        if enemy.get("intro"):
            st.caption(enemy["intro"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title(f"⚔️ Combat — Quest {gs['level']}")

    col_main, col_log = st.columns([2, 1])

    with col_main:
        st.markdown(f"### Enemy: **{enemy['name']}**")
        st.progress(max(0.0, enemy["hp"] / enemy["max_hp"]))
        st.write(f"Enemy HP: {max(0, enemy['hp'])} / {enemy['max_hp']}  |  Attack: {enemy['atk']}")
        status_bits = []
        if gs["enemy_status"].get("burn"): status_bits.append("🔥 Burning")
        if gs["enemy_status"].get("stunned"): status_bits.append("💫 Stunned")
        if status_bits:
            st.caption(" | ".join(status_bits))

        st.markdown("---")
        st.markdown("### You")
        st.progress(max(0.0, gs["hp"] / total_max_hp()))
        st.write(f"Your HP: {max(0, gs['hp'])} / {total_max_hp()}  |  MP: {gs['mp']} / {gs['max_mp']}")
        pstatus_bits = []
        if gs["player_status"].get("poison"): pstatus_bits.append("☠️ Poisoned")
        if gs["player_status"].get("burn"): pstatus_bits.append("🔥 Burning")
        if pstatus_bits:
            st.caption(" | ".join(pstatus_bits))

        st.markdown("#### Actions")
        stunned = gs["player_status"].get("stunned", False)
        if stunned:
            st.warning("You are stunned this turn!")

        a1, a2, a3 = st.columns(3)
        action_taken = False

        with a1:
            if st.button("🗡️ Melee Strike", use_container_width=True, disabled=stunned):
                player_action_melee()
                action_taken = True
        with a2:
            if st.button("✨ Magic Bolt", use_container_width=True, disabled=stunned):
                if player_action_magic():
                    action_taken = True
        with a3:
            item_choice = st.selectbox(
                "Item",
                options=["-- select --"] + [f"{k} (x{v})" for k, v in gs["inventory"].items() if v > 0],
                key="item_select",
                label_visibility="collapsed",
            )
            if st.button("🧪 Use Item", use_container_width=True):
                if item_choice != "-- select --":
                    item_name = item_choice.split(" (x")[0]
                    use_item(item_name)
                    action_taken = True
                else:
                    st.warning("Select an item first.")

        if gs["skills_unlocked"]:
            st.markdown("#### Skills")
            skill_cols = st.columns(min(3, len(gs["skills_unlocked"])) or 1)
            for i, skill_id in enumerate(gs["skills_unlocked"]):
                skill = SKILLS[skill_id]
                with skill_cols[i % len(skill_cols)]:
                    if st.button(f"{skill['name']} (MP {skill['mp_cost']})", key=f"use_{skill_id}", use_container_width=True, disabled=stunned):
                        if player_action_skill(skill_id):
                            action_taken = True

        if st.button("🏳️ Flee (return to Sanctuary)", disabled=is_boss):
            gs["screen"] = "hub"
            gs["combat_log"] = []
            st.rerun()

        if action_taken:
            if stunned:
                gs["player_status"]["stunned"] = False
            if not resolve_death_or_continue():
                dmg_e = tick_status(gs["enemy_status"], "hp", is_player=False)
                gs["enemy"]["hp"] -= dmg_e
                if not resolve_death_or_continue():
                    dmg_p = tick_status(gs["player_status"], "hp", is_player=True)
                    gs["hp"] -= dmg_p
                    if not check_player_death():
                        enemy_turn()
                        check_player_death()
            st.rerun()

    with col_log:
        st.subheader("Battle Log")
        if not gs["combat_log"]:
            st.info("The battle has just begun. Choose your first move.")
        else:
            for line in reversed(gs["combat_log"]):
                st.markdown(f'<div class="log-line">• {line}</div>', unsafe_allow_html=True)


def screen_game_over():
    st.title("💀 YOU HAVE FALLEN")
    st.write(
        "Your soul is cast into the void. The Sanctuary fades. God's dominion "
        "remains unchallenged... for now."
    )
    st.write(f"You fell at Quest {gs['level']}, having gathered {gs['gold']} gold along the way.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Retry from Quest 1 (New Save)", use_container_width=True):
            st.session_state.game_state = new_game_state()
            st.rerun()
    with c2:
        if st.button("Retry this Quest (keep gear)", use_container_width=True):
            gs["hp"] = total_max_hp()
            gs["mp"] = gs["max_mp"]
            gs["player_status"] = {}
            gs["screen"] = "hub"
            st.rerun()


def screen_victory():
    st.title("🏆 GOD IS DEAD. YOU HAVE WON.")
    st.balloons()
    st.write(
        "You climbed 100 tiers of reality: forged a pact with Hell, dismantled the "
        "angelic hosts, silenced the Apostles, broke the Archangels Gabriel, Michael "
        "and Raphael, undid the Son's regeneration, and struck down the Creator "
        "Himself upon His own throne."
    )
    st.write("The cosmos is yours to remake.")
    st.subheader(f"Final Achievements: {len(gs['achievements'])}/{len(ACHIEVEMENTS)}")
    for key in gs["achievements"]:
        st.write(f"🏆 {ACHIEVEMENTS[key]}")

    if st.button("Play Again (New Game+)", use_container_width=True, type="primary"):
        fresh = new_game_state()
        fresh["max_hp"] = 200
        fresh["hp"] = 200
        fresh["screen"] = "menu"
        st.session_state.game_state = fresh
        st.rerun()


# =====================================================================
# ROUTER
# =====================================================================
SCREENS = {
    "menu": screen_menu,
    "hub": screen_hub,
    "shop": screen_shop,
    "skills": screen_skills,
    "combat": screen_combat,
    "game_over": screen_game_over,
    "victory": screen_victory,
}

SCREENS.get(gs["screen"], screen_menu)()
