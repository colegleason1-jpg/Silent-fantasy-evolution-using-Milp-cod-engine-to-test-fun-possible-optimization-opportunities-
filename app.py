import pygame
import random
import sys
import os
import json
import math

# --- SYSTEM INITIALIZATION ---
pygame.init()
pygame.font.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# --- DISPLAY CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720
FPS = 60

# --- COLOR PALETTE ---
COLOR_BG = (6, 6, 10)
COLOR_PANEL = (16, 16, 26)
COLOR_BORDER = (45, 45, 70)
COLOR_TEXT_LIGHT = (235, 235, 245)
COLOR_TEXT_DIM = (140, 140, 165)
COLOR_RED = (220, 35, 35)
COLOR_GOLD = (255, 215, 0)
COLOR_BLUE = (40, 140, 255)
COLOR_PURPLE = (160, 40, 220)
COLOR_GREEN = (40, 180, 80)

class SoundSynthesizer:
    """Procedurally synthesizes retro sound effects without needing external wav files."""
    @staticmethod
    def play_sound(sound_type):
        try:
            sample_rate = 44100
            if sound_type == "hit":
                duration = 0.15
                freq = 150
            elif sound_type == "magic":
                duration = 0.3
                freq = 600
            elif sound_type == "heal":
                duration = 0.4
                freq = 400
            elif sound_type == "victory":
                duration = 0.6
                freq = 800
            else:
                return
            
            num_samples = int(sample_rate * duration)
            buffer = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Generate simple sine wave with decay envelope
                val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t) * (1.0 - (i / num_samples)))
                buffer.extend(val.to_bytes(2, byteorder='little', signed=True))
                buffer.extend(val.to_bytes(2, byteorder='little', signed=True))
            
            sound = pygame.mixer.Sound(buffer=bytes(buffer))
            sound.play()
        except Exception:
            pass # Fail gracefully if audio driver is unavailable on stream pc

class UIManager:
    """Manages fonts, UI boxes, custom rendering helpers, and panels."""
    def __init__(self):
        self.fonts = {
            "title": pygame.font.SysFont("Cinzel", 42, bold=True),
            "header": pygame.font.SysFont("Arial", 24, bold=True),
            "body": pygame.font.SysFont("Arial", 16),
            "small": pygame.font.SysFont("Arial", 12)
        }

    def draw_panel(self, surface, rect, bg_color=COLOR_PANEL, border_color=COLOR_BORDER, border_radius=10):
        pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=border_radius)

    def draw_bar(self, surface, x, y, w, h, current, max_val, color):
        if max_val <= 0: max_val = 1
        ratio = max(0, min(1, current / max_val))
        pygame.draw.rect(surface, (30, 30, 45), (x, y, w, h), border_radius=4)
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h), border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDER, (x, y, w, h), 1, border_radius=4)

class PlayerCharacter:
    """Core protagonist structure tracking stats, magic trees, inventory, and gear."""
    def __init__(self):
        self.level = 1
        self.max_levels = 100
        self.hp = 160
        self.max_hp = 160
        self.mp = 90
        self.max_mp = 90
        self.attack = 28
        self.magic_power = 45
        self.gold = 0
        self.demon_allied = False
        
        self.inventory = [
            {"name": "Iron Longsword", "type": "weapon", "val": 10},
            {"name": "Restorative Flask", "type": "consumable", "val": 70},
            {"name": "Greater Mana Potion", "type": "consumable", "val": 50},
            {"name": "Amulet of the Outcast", "type": "accessory", "val": 15}
        ]
        
        self.skill_tree = {
            "Hellfire Slash": {"unlocked": True, "cost": 0, "desc": "Infuses blade with dark flames."},
            "Abyssal Nova": {"unlocked": False, "cost": 100, "desc": "Unleashes wave of demonic magic."},
            "Divine Shield Break": {"unlocked": False, "cost": 250, "desc": "Bypasses angelic wards."}
        }

    def to_dict(self):
        return {
            "level": self.level, "hp": self.hp, "max_hp": self.max_hp,
            "mp": self.mp, "max_mp": self.max_mp, "attack": self.attack,
            "magic_power": self.magic_power, "gold": self.gold,
            "demon_allied": self.demon_allied, "inventory": self.inventory,
            "skill_tree": self.skill_tree
        }

    def load_from_dict(self, data):
        self.level = data.get("level", 1)
        self.hp = data.get("hp", 160)
        self.max_hp = data.get("max_hp", 160)
        self.mp = data.get("mp", 90)
        self.max_mp = data.get("max_mp", 90)
        self.attack = data.get("attack", 28)
        self.magic_power = data.get("magic_power", 45)
        self.gold = data.get("gold", 0)
        self.demon_allied = data.get("demon_allied", False)
        self.inventory = data.get("inventory", self.inventory)
        self.skill_tree = data.get("skill_tree", self.skill_tree)

class CampaignDatabase:
    """Master database scaling all 100 quests, distinct factions, and major bosses."""
    @staticmethod
    def generate_encounter(lvl):
        if lvl < 25:
            names = ["Goblin Marauder", "Feral Werewolf", "Corrupted Elf Archer", "Shadow Beast", "Dark Cultist"]
            return {
                "name": f"Quest {lvl}: {random.choice(names)}",
                "hp": 90 + (lvl * 16), "max_hp": 90 + (lvl * 16),
                "atk": 16 + (lvl * 2.5), "type": "mortal", "color": (110, 160, 110)
            }
        elif lvl == 25:
            return {
                "name": "Quest 25: The Arch-Demon of the Abyss",
                "hp": 1200, "max_hp": 1200, "atk": 55, "type": "demon_boss", "color": (220, 60, 0)
            }
        elif lvl < 50:
            names = ["Fairy Executioner", "Choir Warlock", "Seraphic Hound", "Angelic Sentinel"]
            return {
                "name": f"Quest {lvl}: {random.choice(names)}",
                "hp": 280 + (lvl * 20), "max_hp": 280 + (lvl * 20),
                "atk": 38 + (lvl * 3.5), "type": "angelic", "color": (100, 210, 255)
            }
        elif lvl == 50:
            return {
                "name": "Quest 50: Archangel Gabriel",
                "hp": 2500, "max_hp": 2500, "atk": 85, "type": "angel_boss", "color": (255, 255, 120)
            }
        elif lvl < 75:
            names = ["Apostle's Phantom", "False Prophet", "Heavenly Templar", "Disciple of Light"]
            return {
                "name": f"Quest {lvl}: {random.choice(names)}",
                "hp": 600 + (lvl * 25), "max_hp": 600 + (lvl * 25),
                "atk": 65 + (lvl * 4.5), "type": "prophet", "color": (190, 110, 255)
            }
        elif lvl == 75:
            return {
                "name": "Quest 75: Jesus of Nazareth (The Son)",
                "hp": 7000, "max_hp": 7000, "atk": 120, 
                "type": "jesus_boss", "regen": 350, "color": (255, 255, 255)
            }
        elif lvl < 100:
            names = ["Throne Guardian", "Seraphim Elite", "Cherubim Executioner", "Ophanim Wheel"]
            return {
                "name": f"Quest {lvl}: {random.choice(names)}",
                "hp": 1400 + (lvl * 32), "max_hp": 1400 + (lvl * 32),
                "atk": 100 + (lvl * 5.5), "type": "guardian", "color": (210, 160, 60)
            }
        else:
            return {
                "name": "QUEST 100: GOD ALMIGHTY (The Creator)",
                "hp": 30000, "max_hp": 30000, "atk": 250, 
                "type": "god_boss", "color": (255, 215, 0)
            }

class KillGodGame:
    """Main Streamlined Engine Managing States, Screens, Loops, and Input Rendering."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Kill God - Ultimate Stream Edition (100 Quests)")
        self.clock = pygame.time.Clock()
        self.ui = UIManager()
        self.player = PlayerCharacter()
        
        self.state = "MENU" # MENU, HUB, COMBAT, INVENTORY, SKILLS, VICTORY, GAME_OVER
        self.current_enemy = None
        self.battle_log = "The gates of judgment stand before you."
        self.screen_shake = 0
        self.anim_timer = 0

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_RETURN:
                        self.state = "HUB"
                        self.current_enemy = CampaignDatabase.generate_encounter(self.player.level)
                    elif event.key == pygame.K_l:
                        self.load_game_state()

                elif self.state == "HUB":
                    if event.key == pygame.K_RETURN:
                        self.state = "COMBAT"
                        self.current_enemy = CampaignDatabase.generate_encounter(self.player.level)
                    elif event.key == pygame.K_i:
                        self.state = "INVENTORY"
                    elif event.key == pygame.K_k:
                        self.state = "SKILLS"
                    elif event.key == pygame.K_s:
                        self.save_game_state()
                    elif event.key == pygame.K_p and self.player.level == 25 and not self.player.demon_allied:
                        self.player.demon_allied = True
                        self.player.attack += 40
                        self.player.magic_power += 60
                        self.battle_log = "Demon Pact Forged! Hellfire powers unlocked."
                        SoundSynthesizer.play_sound("victory")

                elif self.state in ["INVENTORY", "SKILLS"]:
                    if event.key == pygame.K_ESCAPE or event.key in [pygame.K_i, pygame.K_k]:
                        self.state = "HUB"

                elif self.state == "COMBAT":
                    enemy = self.current_enemy
                    if enemy:
                        if event.key == pygame.K_1: # Melee Strike
                            dmg = random.randint(self.player.attack - 6, self.player.attack + 12)
                            self.execute_turn(dmg, is_magic=False)
                        elif event.key == pygame.K_2: # Magic Spell
                            if self.player.mp >= 20:
                                self.player.mp -= 20
                                mdmg = random.randint(self.player.magic_power - 10, self.player.magic_power + 20)
                                self.execute_turn(mdmg, is_magic=True)
                            else:
                                self.battle_log = "Insufficient Mana for spell casting!"
                        elif event.key == pygame.K_3: # Use Healing Draft
                            self.player.hp = min(self.player.max_hp, self.player.hp + 80)
                            self.battle_log = "Drank healing draft, recovering HP."
                            SoundSynthesizer.play_sound("heal")
                            self.trigger_enemy_counter()

                elif self.state in ["GAME_OVER", "VICTORY"]:
                    if event.key == pygame.K_r:
                        self.player = PlayerCharacter()
                        self.state = "MENU"

    def execute_turn(self, damage, is_magic):
        enemy = self.current_enemy
        enemy["hp"] -= damage
        self.screen_shake = 12
        
        stype = "Arcane spell" if is_magic else "Melee strike"
        self.battle_log = f"You unleashed a {stype} dealing {damage} damage to {enemy['name']}!"
        SoundSynthesizer.play_sound("magic" if is_magic else "hit")

        if enemy["hp"] <= 0:
            self.player.gold += self.player.level * 25
            SoundSynthesizer.play_sound("victory")
            if self.player.level >= self.player.max_levels:
                self.state = "VICTORY"
            else:
                self.player.level += 1
                self.state = "HUB"
                self.battle_log = f"Quest cleared! Advancing to Quest Tier {self.player.level}."
            return

        self.trigger_enemy_counter()

    def trigger_enemy_counter(self):
        enemy = self.current_enemy
        if not enemy: return

        # Jesus Boss Regeneration Mechanic
        if enemy.get("type") == "jesus_boss":
            regen = enemy.get("regen", 350)
            enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + regen)
            self.battle_log += f" | Jesus triggers Divine Regeneration (+{regen} HP)!"

        edmg = random.randint(int(enemy["atk"] * 0.8), int(enemy["atk"] * 1.2))
        self.player.hp -= edmg
        self.battle_log += f" | {enemy['name']} counter-attacks for {edmg} damage!"
        
        if self.player.hp <= 0:
            self.state = "GAME_OVER"

    def save_game_state(self):
        data = self.player.to_dict()
        with open("kill_god_save.json", "w") as f:
            json.dump(data, f)
        self.battle_log = "Crusade progress saved successfully to disk."

    def load_game_state(self):
        if os.path.exists("kill_god_save.json"):
            with open("kill_god_save.json", "r") as f:
                data = json.load(f)
                self.player.load_from_dict(data)
            self.battle_log = "Save file loaded successfully!"

    def update(self):
        if self.screen_shake > 0:
            self.screen_shake -= 1
        self.anim_timer += 0.05

    def render(self):
        self.screen.fill(COLOR_BG)
        
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        if self.state == "MENU":
            title = self.ui.fonts["title"].render("KILL GOD: THE REBELLION", True, COLOR_RED)
            sub = self.ui.fonts["header"].render("Press [ENTER] to Begin Crusade  |  [L] Load Save Data", True, COLOR_TEXT_LIGHT)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2 + shake_x, HEIGHT//2 - 60 + shake_y))
            self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

        elif self.state == "HUB":
            t = self.ui.fonts["title"].render(f"Sanctuary - Quest Tier {self.player.level} / {self.player.max_levels}", True, COLOR_GOLD)
            sub = self.ui.fonts["header"].render("Press [ENTER] Enter Combat  |  [I] Inventory  |  [K] Skills  |  [S] Save", True, COLOR_TEXT_LIGHT)
            stats = self.ui.fonts["body"].render(f"HP: {self.player.hp}/{self.player.max_hp} | MP: {self.player.mp}/{self.player.max_mp} | Gold: {self.player.gold} | Demon Pact: {self.player.demon_allied}", True, COLOR_TEXT_LIGHT)
            
            self.screen.blit(t, (100 + shake_x, 70 + shake_y))
            self.screen.blit(sub, (100, 140))
            self.screen.blit(stats, (100, 200))

            if self.player.level == 25 and not self.player.demon_allied:
                pact = self.ui.fonts["header"].render("Press [P] to Accept the Devil's Dark Alliance", True, COLOR_RED)
                self.screen.blit(pact, (100, 260))

        elif self.state == "INVENTORY":
            t = self.ui.fonts["title"].render("Crusader Inventory", True, COLOR_BLUE)
            self.screen.blit(t, (100, 70))
            y = 150
            for item in self.player.inventory:
                txt = self.ui.fonts["body"].render(f"• {item['name']} ({item['type'].upper()}) - Value: {item['val']}", True, COLOR_TEXT_LIGHT)
                self.screen.blit(txt, (120, y))
                y += 35
            back = self.ui.fonts["header"].render("Press [ESC] or [I] to Return", True, COLOR_GOLD)
            self.screen.blit(back, (120, HEIGHT - 100))

        elif self.state == "SKILLS":
            t = self.ui.fonts["title"].render("Magic Skill Tree", True, COLOR_PURPLE)
            self.screen.blit(t, (100, 70))
            y = 150
            for sname, data in self.player.skill_tree.items():
                status = "UNLOCKED" if data["unlocked"] else f"Cost: {data['cost']} Gold"
                txt = self.ui.fonts["body"].render(f"• {sname} [{status}] - {data['desc']}", True, COLOR_TEXT_LIGHT)
                self.screen.blit(txt, (120, y))
                y += 40
            back = self.ui.fonts["header"].render("Press [ESC] or [K] to Return", True, COLOR_GOLD)
            self.screen.blit(back, (120, HEIGHT - 100))

        elif self.state == "COMBAT":
            enemy = self.current_enemy
            
            # Panels
            self.ui.draw_panel(self.screen, (100 + shake_x, 100 + shake_y, 480, 260))
            self.ui.draw_panel(self.screen, (700 + shake_x, 100 + shake_y, 480, 260))

            # Player Info
            p_name = self.ui.fonts["header"].render("Protagonist (Crusader)", True, COLOR_TEXT_LIGHT)
            self.screen.blit(p_name, (130, 130))
            self.ui.draw_bar(self.screen, 130, 180, 420, 22, self.player.hp, self.player.max_hp, COLOR_GREEN)
            p_hp_txt = self.ui.fonts["small"].render(f"HP: {self.player.hp} / {self.player.max_hp}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(p_hp_txt, (140, 182))
            
            self.ui.draw_bar(self.screen, 130, 220, 420, 18, self.player.mp, self.player.max_mp, COLOR_BLUE)
            p_mp_txt = self.ui.fonts["small"].render(f"MP: {self.player.mp} / {self.player.max_mp}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(p_mp_txt, (140, 222))

            # Enemy Info
            e_name = self.ui.fonts["header"].render(enemy["name"], True, enemy["color"])
            self.screen.blit(e_name, (730, 130))
            self.ui.draw_bar(self.screen, 730, 180, 420, 22, enemy["hp"], enemy["max_hp"], COLOR_RED)
            e_hp_txt = self.ui.fonts["small"].render(f"HP: {enemy['hp']} / {enemy['max_hp']}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(e_hp_txt, (740, 182))

            # Log & Controls Panel
            self.ui.draw_panel(self.screen, (100, 430, 1080, 220))
            log_surf = self.ui.fonts["body"].render(f"Log: {self.battle_log}", True, COLOR_TEXT_LIGHT)
            controls = self.ui.fonts["header"].render("Controls: [1] Melee Strike  |  [2] Magic Spell  |  [3] Healing Draft", True, COLOR_GOLD)
            self.screen.blit(log_surf, (130, 470))
            self.screen.blit(controls, (130, 560))

        elif self.state == "GAME_OVER":
            go = self.ui.fonts["title"].render("YOU HAVE FALLEN", True, COLOR_RED)
            sub = self.ui.fonts["header"].render("Press [R] to Retry Crusade", True, COLOR_TEXT_LIGHT)
            self.screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 40))
            self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))

        elif self.state == "VICTORY":
            vic = self.ui.fonts["title"].render("GOD IS DEAD. YOU HAVE WON.", True, COLOR_GOLD)
            sub = self.ui.fonts["header"].render("Press [R] to Play Again", True, COLOR_TEXT_LIGHT)
            self.screen.blit(vic, (WIDTH//2 - vic.get_width()//2, HEIGHT//2 - 40))
            self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))

        pygame.display.flip()

if __name__ == "__main__":
    game = KillGodGame()
    game.run()
