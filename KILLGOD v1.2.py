import streamlit as st
import streamlit.components.v1 as components
import json
import math
import random

st.set_page_config(page_title="KILLGOD", page_icon="✝️", layout="wide")

ENEMY_TYPES = {"enemy", "boss"}

CHAPTERS = [
    {"stage": 1, "title": "Chapter 1: Goblin Purge", "objective": "Kill 3 goblins and prove yourself to the Devil.", "target_kills": 3, "spawn_pool": ["Goblin Raider", "Goblin Archer", "Goblin Shaman"], "message": "The Devil sends you into the wastes. Break the goblin packs first."},
    {"stage": 2, "title": "Chapter 2: Demon Pact", "objective": "Kill 6 enemies total and draw demon allies to your side.", "target_kills": 6, "spawn_pool": ["Goblin Brute", "Hellhound", "Infernal Acolyte"], "message": "Your slaughter is attracting demons. The underworld starts to answer your call."},
    {"stage": 3, "title": "Chapter 3: Angel Hunt", "objective": "Kill 10 enemies total and break the first angelic lines.", "target_kills": 10, "spawn_pool": ["Zealot", "Watcher Angel", "Cherubim Sentinel"], "message": "The gates of Heaven stir. Angels descend to stop your march."},
    {"stage": 4, "title": "Chapter 4: High Heaven War", "objective": "Kill 14 enemies total and cut down the high angels.", "target_kills": 14, "spawn_pool": ["Dominion", "Seraphim", "Throne Guardian"], "message": "You have become a real threat. High angels now answer your blasphemy."},
    {"stage": 5, "title": "Chapter 5: Slay God", "objective": "Defeat God and finish the campaign.", "target_kills": 15, "spawn_pool": ["God"], "message": "The throne of creation stands before you. End it."},
]

ENEMY_LIBRARY = {
    "Goblin Raider": {"hp": 1, "attack": 6, "element": "earth", "color": "#6f8a3c", "kind": "enemy"},
    "Goblin Archer": {"hp": 1, "attack": 5, "element": "air", "color": "#8ca65c", "kind": "enemy"},
    "Goblin Shaman": {"hp": 2, "attack": 7, "element": "shadow", "color": "#6a4ab6", "kind": "enemy"},
    "Goblin Brute": {"hp": 2, "attack": 8, "element": "earth", "color": "#607232", "kind": "enemy"},
    "Hellhound": {"hp": 2, "attack": 9, "element": "fire", "color": "#d84a24", "kind": "enemy"},
    "Infernal Acolyte": {"hp": 2, "attack": 10, "element": "shadow", "color": "#7f2de2", "kind": "enemy"},
    "Zealot": {"hp": 2, "attack": 10, "element": "light", "color": "#d8d0aa", "kind": "enemy"},
    "Watcher Angel": {"hp": 3, "attack": 11, "element": "light", "color": "#efe6b0", "kind": "enemy"},
    "Cherubim Sentinel": {"hp": 3, "attack": 12, "element": "light", "color": "#fff3c2", "kind": "enemy"},
    "Dominion": {"hp": 4, "attack": 14, "element": "light", "color": "#ffe79d", "kind": "enemy"},
    "Seraphim": {"hp": 4, "attack": 15, "element": "fire", "color": "#ffb35c", "kind": "enemy"},
    "Throne Guardian": {"hp": 5, "attack": 17, "element": "light", "color": "#fff6dc", "kind": "boss"},
    "God": {"hp": 12, "attack": 25, "element": "light", "color": "#ffffff", "kind": "boss"},
}

DEMON_COMPANIONS = [
    {"name": "Moloch", "unlock_kills": 4, "bonus": "+1 melee damage", "element": "fire"},
    {"name": "Astaroth", "unlock_kills": 7, "bonus": "+1 spell damage", "element": "shadow"},
    {"name": "Legion", "unlock_kills": 11, "bonus": "Occasional double strike", "element": "shadow"},
]


def chapter_by_stage(stage):
    for chapter in CHAPTERS:
        if chapter["stage"] == stage:
            return chapter
    return CHAPTERS[-1]


def ensure_state():
    if "initialized" in st.session_state:
        return
    st.session_state.initialized = True
    st.session_state.turn = 1
    st.session_state.health = 100
    st.session_state.max_health = 100
    st.session_state.gold = 100
    st.session_state.kills = 0
    st.session_state.quest_stage = 1
    st.session_state.player_x = 24
    st.session_state.player_z = 24
    st.session_state.player_position = 0
    st.session_state.enemy_uid_counter = 1
    st.session_state.turn_log = []
    st.session_state.render_counter = 0
    st.session_state.companions = []
    st.session_state.message = CHAPTERS[0]["message"]
    st.session_state.creatures = []
    st.session_state.active_quest = CHAPTERS[0]["objective"]
    st.session_state.quest_target_kills = CHAPTERS[0]["target_kills"]
    spawn_story_world()


def next_enemy_id():
    eid = st.session_state.enemy_uid_counter
    st.session_state.enemy_uid_counter += 1
    return eid


def create_enemy(name, x, z):
    spec = ENEMY_LIBRARY[name]
    return {"id": next_enemy_id(), "name": name, "x": x, "z": z, "height": random.uniform(0.4, 2.4), "hp": spec["hp"], "max_hp": spec["hp"], "attack": spec["attack"], "element": spec["element"], "color": spec["color"], "type": spec["kind"]}


def create_npc(name, x, z, element="shadow"):
    return {"name": name, "x": x, "z": z, "height": 1.0, "hp": 999, "max_hp": 999, "attack": 0, "element": element, "color": "#7f2de2", "type": "npc"}


def chapter_spawn_names(stage):
    chapter = chapter_by_stage(stage)
    if stage == 5:
        return ["God"]
    return chapter["spawn_pool"]


def spawn_story_world():
    st.session_state.creatures = [create_npc("The Devil", 24, 24)]
    populate_hostiles_for_stage(force=True)


def current_hostiles():
    return [c for c in st.session_state.creatures if c.get("type") in ENEMY_TYPES]


def purge_dead_hostiles():
    st.session_state.creatures = [c for c in st.session_state.creatures if c.get("type") not in ENEMY_TYPES or c.get("hp", 0) > 0]


def populate_hostiles_for_stage(force=False):
    purge_dead_hostiles()
    hostiles = current_hostiles()
    stage = st.session_state.quest_stage
    if stage == 5:
        if not any(c["name"] == "God" for c in hostiles):
            st.session_state.creatures.append(create_enemy("God", 40, 40))
        return
    desired = 5
    if not force and len(hostiles) >= desired:
        return
    names = chapter_spawn_names(stage)
    while len(current_hostiles()) < desired:
        ex = max(2, min(46, st.session_state.player_x + random.randint(-12, 12)))
        ez = max(2, min(46, st.session_state.player_z + random.randint(-12, 12)))
        st.session_state.creatures.append(create_enemy(random.choice(names), ex, ez))


def update_companions():
    st.session_state.companions = [d for d in DEMON_COMPANIONS if st.session_state.kills >= d["unlock_kills"]]


def update_quest_progress():
    current = chapter_by_stage(st.session_state.quest_stage)
    if st.session_state.quest_stage < 5 and st.session_state.kills >= current["target_kills"]:
        st.session_state.quest_stage += 1
        nxt = chapter_by_stage(st.session_state.quest_stage)
        st.session_state.active_quest = nxt["objective"]
        st.session_state.quest_target_kills = nxt["target_kills"]
        st.session_state.message = nxt["message"]
        populate_hostiles_for_stage(force=True)
    elif st.session_state.quest_stage == 5 and not any(c["name"] == "God" for c in current_hostiles()):
        st.session_state.message = "God has fallen. KILLGOD is complete."
        st.session_state.active_quest = "Campaign complete."


def process_turn(action_name, health_delta=0, gold_delta=0):
    purge_dead_hostiles()
    st.session_state.turn += 1
    st.session_state.render_counter += 1
    st.session_state.health = max(0, min(st.session_state.max_health, st.session_state.health + health_delta))
    st.session_state.gold = max(0, st.session_state.gold + gold_delta)
    st.session_state.turn_log.append(f"Turn {st.session_state.turn - 1}: {action_name}")
    update_companions()
    update_quest_progress()
    populate_hostiles_for_stage()


def nearest_hostile():
    hostiles = current_hostiles()
    if not hostiles:
        return None, None
    hostiles.sort(key=lambda c: math.hypot(c["x"] - st.session_state.player_x, c["z"] - st.session_state.player_z))
    target = hostiles[0]
    dist = math.hypot(target["x"] - st.session_state.player_x, target["z"] - st.session_state.player_z)
    return target, dist


def melee_damage():
    dmg = 1
    if any(c["name"] == "Moloch" for c in st.session_state.companions):
        dmg += 1
    if any(c["name"] == "Legion" for c in st.session_state.companions) and random.random() < 0.25:
        dmg += 1
    return dmg


def spell_damage():
    dmg = 1
    if any(c["name"] == "Astaroth" for c in st.session_state.companions):
        dmg += 1
    return dmg


def remove_enemy(enemy_id):
    slain = None
    survivors = []
    for creature in st.session_state.creatures:
        if creature.get("id") == enemy_id and creature.get("type") in ENEMY_TYPES:
            slain = creature["name"]
            continue
        survivors.append(creature)
    st.session_state.creatures = survivors
    return slain


def attack_nearest():
    purge_dead_hostiles()
    target, dist = nearest_hostile()
    if not target:
        st.session_state.message = "No enemy remains in range."
        return
    if dist > 12:
        st.session_state.message = f"{target['name']} is too far away. Move closer."
        process_turn("Missed melee strike")
        return
    target["hp"] -= melee_damage()
    if target["hp"] <= 0:
        slain = remove_enemy(target["id"])
        st.session_state.kills += 1
        st.session_state.gold += 12
        st.session_state.message = f"You slaughtered {slain}. Its name is erased from the battlefield."
        process_turn("Executed enemy")
    else:
        st.session_state.message = f"You hit {target['name']}. {target['hp']}/{target['max_hp']} HP remains."
        process_turn("Melee strike")


def cast_hellfire():
    purge_dead_hostiles()
    hostiles = list(current_hostiles())
    if not hostiles:
        st.session_state.message = "No enemies remain for Hellfire."
        return
    slain = []
    hits = 0
    dmg = spell_damage()
    for target in hostiles:
        dist = math.hypot(target["x"] - st.session_state.player_x, target["z"] - st.session_state.player_z)
        if dist <= 16:
            hits += 1
            target["hp"] -= dmg
            if target["hp"] <= 0:
                slain.append(target["id"])
    for enemy_id in slain:
        remove_enemy(enemy_id)
        st.session_state.kills += 1
        st.session_state.gold += 8
    st.session_state.message = "Hellfire erupted, but no enemy was close enough." if hits == 0 else f"Hellfire hit {hits} enemies and destroyed {len(slain)} of them."
    process_turn("Hellfire blast")


def dark_ritual():
    if st.session_state.gold < 20:
        st.session_state.message = "You need 20 gold for a dark ritual."
        return
    st.session_state.message = "A dark ritual restores your body and deepens your pact."
    process_turn("Dark ritual", health_delta=25, gold_delta=-20)


def move_player(dx=0, dz=0, label="Move"):
    st.session_state.player_x = max(0, min(48, st.session_state.player_x + dx))
    st.session_state.player_z = max(0, min(48, st.session_state.player_z + dz))
    st.session_state.player_position += abs(dx) + abs(dz)
    process_turn(label)


def render_scene():
    creatures = [{"name": c["name"], "x": c["x"], "z": c["z"], "height": c.get("height", 1), "hp": c.get("hp", 1), "max_hp": c.get("max_hp", 1), "type": c.get("type", "npc"), "element": c.get("element", "shadow"), "color": c.get("color", "#7f2de2")} for c in st.session_state.creatures]
    terrain = [[round((math.sin(x * 0.18) + math.cos(z * 0.14)) * 1.8, 2) for z in range(50)] for x in range(50)]
    creatures_json = json.dumps(creatures)
    terrain_json = json.dumps(terrain)
    html = f"""
    <!-- render_id: {st.session_state.render_counter} -->
    <div style='background:#05050a;border:1px solid #311;padding:6px;border-radius:8px;'>
      <div id='canvas-container' style='width:100%;height:420px;border-radius:8px;overflow:hidden;position:relative;'></div>
      <div id='labels-overlay' style='position:relative;margin-top:-420px;height:420px;pointer-events:none;'></div>
      <div style='margin-top:8px;color:#ff6464;font-family:monospace;font-size:12px;text-align:center;'>CHAPTER {st.session_state.quest_stage} | X:{st.session_state.player_x} Z:{st.session_state.player_z} | KILLS:{st.session_state.kills}</div>
    </div>
    <script type='module'>
      import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.0/build/three.module.js';
      const container = document.getElementById('canvas-container');
      const labelsOverlay = document.getElementById('labels-overlay');
      const width = container.clientWidth;
      const height = container.clientHeight;
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x05050a);
      scene.fog = new THREE.FogExp2(0x05050a, 0.025);
      const camera = new THREE.PerspectiveCamera(58, width / height, 0.1, 1000);
      camera.position.set(25, 34, 34);
      camera.lookAt(25, 0, 25);
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(width, height);
      container.appendChild(renderer.domElement);
      const ambient = new THREE.AmbientLight(0x9a87ff, 0.85);
      scene.add(ambient);
      const dir = new THREE.DirectionalLight(0xffddbb, 1.2);
      dir.position.set(15, 30, 15);
      scene.add(dir);
      const terrain = {terrain_json};
      const creatures = {creatures_json};
      const floor = new THREE.Group();
      for (let x = 0; x < 50; x += 2) {{
        for (let z = 0; z < 50; z += 2) {{
          const h = terrain[x][z];
          const color = h > 2 ? 0x504028 : h > 0 ? 0x273419 : 0x161616;
          const cube = new THREE.Mesh(new THREE.BoxGeometry(2, Math.max(0.5, h + 2), 2), new THREE.MeshStandardMaterial({{ color, roughness: 0.95 }}));
          cube.position.set(x, h / 2, z);
          floor.add(cube);
        }}
      }}
      scene.add(floor);
      const clock = new THREE.Clock();
      const actorMeshes = [];
      function makeActor(c) {{
        const group = new THREE.Group();
        const color = new THREE.Color(c.color || '#7f2de2');
        const body = new THREE.Mesh(new THREE.CapsuleGeometry(c.type === 'boss' ? 0.8 : 0.45, c.type === 'boss' ? 2.5 : 1.4, 6, 12), new THREE.MeshStandardMaterial({{ color: 0x1f1f29, emissive: color, emissiveIntensity: 0.28, roughness: 0.65 }}));
        body.position.y = c.type === 'boss' ? 2.8 : 1.7;
        group.add(body);
        const head = new THREE.Mesh(new THREE.SphereGeometry(c.type === 'boss' ? 0.48 : 0.30, 16, 16), new THREE.MeshStandardMaterial({{ color, emissive: color, emissiveIntensity: 0.55 }}));
        head.position.y = c.type === 'boss' ? 4.3 : 2.9;
        group.add(head);
        const aura = new THREE.Mesh(new THREE.RingGeometry(0.6, c.type === 'boss' ? 1.3 : 0.95, 28), new THREE.MeshBasicMaterial({{ color, transparent: true, opacity: 0.35, side: THREE.DoubleSide }}));
        aura.rotation.x = -Math.PI / 2;
        aura.position.y = 0.08;
        group.add(aura);
        if (c.name === 'The Devil') {{
          const crown = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.7, 5), new THREE.MeshStandardMaterial({{ color: 0xff3b3b, emissive: 0x7f0015, emissiveIntensity: 0.55 }}));
          crown.position.y = 3.55;
          group.add(crown);
        }}
        if (c.type === 'boss') {{
          const halo = new THREE.Mesh(new THREE.TorusGeometry(0.82, 0.08, 16, 40), new THREE.MeshBasicMaterial({{ color: 0xfff0b0 }}));
          halo.position.y = 5.1;
          halo.rotation.x = Math.PI / 2;
          group.add(halo);
          group.userData.halo = halo;
        }}
        group.position.set(c.x, c.height, c.z);
        group.userData.baseY = c.height;
        group.userData.meta = c;
        group.userData.aura = aura;
        scene.add(group);
        actorMeshes.push(group);
      }}
      creatures.forEach(makeActor);
      function updateLabels() {{
        labelsOverlay.innerHTML = '';
        actorMeshes.forEach(actor => {{
          const meta = actor.userData.meta;
          if (meta.type === 'npc') return;
          const vector = actor.position.clone().project(camera);
          const x = (vector.x * 0.5 + 0.5) * width;
          const y = (-vector.y * 0.5 + 0.5) * height;
          if (x < 0 || x > width || y < 0 || y > height) return;
          const wrap = document.createElement('div');
          wrap.style.position = 'absolute';
          wrap.style.left = `${x - 40}px`;
          wrap.style.top = `${y - 48}px`;
          wrap.style.width = '80px';
          wrap.style.textAlign = 'center';
          wrap.innerHTML = `<div style="color:#fff;font-size:11px;font-family:monospace;text-shadow:0 0 6px #000;">${meta.name}</div><div style="height:6px;background:#220000;border:1px solid #550000;border-radius:4px;overflow:hidden;"><div style="width:${(meta.hp / meta.max_hp) * 100}%;height:100%;background:linear-gradient(90deg,#ff2a2a,#ffb347);"></div></div>`;
          labelsOverlay.appendChild(wrap);
        }});
      }}
      function animate() {{
        requestAnimationFrame(animate);
        const t = clock.getElapsedTime();
        actorMeshes.forEach(actor => {{
          const meta = actor.userData.meta;
          const pace = meta.type === 'boss' ? 1.4 : meta.type === 'npc' ? 2.0 : 2.8;
          actor.position.y = actor.userData.baseY + Math.sin(t * pace + meta.x * 0.15) * 0.16;
          actor.rotation.y += meta.type === 'npc' ? 0.0022 : 0.0012;
          actor.userData.aura.rotation.z += 0.012;
          actor.userData.aura.material.opacity = 0.18 + (Math.sin(t * 2.8 + meta.z * 0.12) + 1) * 0.08;
          if (actor.userData.halo) actor.userData.halo.rotation.z += 0.04;
        }});
        renderer.render(scene, camera);
        updateLabels();
      }}
      animate();
    </script>
    """
    components.html(html, height=450, scrolling=False)


ensure_state()
st.markdown("### ✝️ KILLGOD: The Adventure of the Devil")
left, right = st.columns([2.25, 1])
with left:
    st.info(st.session_state.message)
    render_scene()
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        if st.button("Advance", use_container_width=True):
            move_player(dx=2, dz=0, label="Advanced through the wastes")
            st.rerun()
    with m2:
        if st.button("North", use_container_width=True):
            move_player(dz=-2, label="Moved north")
            st.rerun()
    with m3:
        if st.button("West", use_container_width=True):
            move_player(dx=-2, label="Moved west")
            st.rerun()
    with m4:
        if st.button("East", use_container_width=True):
            move_player(dx=2, label="Moved east")
            st.rerun()
    with m5:
        if st.button("South", use_container_width=True):
            move_player(dz=2, label="Moved south")
            st.rerun()
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Strike", use_container_width=True):
            attack_nearest()
            st.rerun()
    with a2:
        if st.button("Hellfire", use_container_width=True):
            cast_hellfire()
            st.rerun()
    with a3:
        if st.button("Dark Ritual", use_container_width=True):
            dark_ritual()
            st.rerun()
with right:
    chapter = chapter_by_stage(st.session_state.quest_stage)
    st.markdown(f"#### {chapter['title']}")
    st.write(st.session_state.active_quest)
    st.metric("Turn", st.session_state.turn)
    st.metric("Health", f"{st.session_state.health}/{st.session_state.max_health}")
    st.metric("Gold", st.session_state.gold)
    st.metric("Kills", st.session_state.kills)
    st.metric("Position", st.session_state.player_position)
    remaining = current_hostiles()
    st.metric("Active enemies", len(remaining))
    st.markdown("#### Demon companions")
    if st.session_state.companions:
        for demon in st.session_state.companions:
            st.write(f"- {demon['name']} — {demon['bonus']}")
    else:
        st.write("No demons recruited yet.")
    st.markdown("#### Active enemies")
    if remaining:
        for enemy in sorted(remaining, key=lambda c: math.hypot(c['x'] - st.session_state.player_x, c['z'] - st.session_state.player_z))[:8]:
            dist = round(math.hypot(enemy['x'] - st.session_state.player_x, enemy['z'] - st.session_state.player_z), 1)
            st.write(f"- {enemy['name']} — {enemy['hp']}/{enemy['max_hp']} HP — dist {dist}")
    else:
        st.write("No active enemies on the field.")
    st.markdown("#### Turn log")
    for line in st.session_state.turn_log[-8:][::-1]:
        st.caption(line)
