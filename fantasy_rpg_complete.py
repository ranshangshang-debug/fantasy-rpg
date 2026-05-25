"""
奇幻冒险RPG - 完整版（含UI和音频）
开放式角色扮演游戏
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
from kivy.animation import Animation
from kivy.lang import Builder
import random
import math
import os

# 设置窗口
Window.size = (360, 640)
Window.clearcolor = (0.1, 0.1, 0.15, 1)

# ==================== 游戏数据类 ====================

class GameEntity:
    """游戏实体"""
    def __init__(self, x, y, name, hp, attack, defense):
        self.x = x
        self.y = y
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.level = 1
        self.exp = 0
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 2)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def is_alive(self):
        return self.hp > 0
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)


class Player(GameEntity):
    """玩家角色"""
    def __init__(self, x, y):
        super().__init__(x, y, "勇者", 120, 18, 6)
        self.mp = 60
        self.max_mp = 60
        self.gold = 50
        self.spells = [
            {"name": "火球术", "damage": 28, "mp_cost": 10, "element": "fire", "desc": "发射火球攻击敌人"},
            {"name": "冰霜新星", "damage": 24, "mp_cost": 12, "element": "ice", "desc": "冰冻周围敌人"},
            {"name": "雷电术", "damage": 35, "mp_cost": 15, "element": "thunder", "desc": "召唤雷电打击"},
            {"name": "治愈之光", "heal": 35, "mp_cost": 18, "element": "holy", "desc": "恢复生命值"},
            {"name": "火焰风暴", "damage": 45, "mp_cost": 25, "element": "fire", "desc": "强力范围魔法"},
            {"name": "神圣护盾", "shield": True, "mp_cost": 20, "element": "holy", "desc": "减少受到的伤害"}
        ]
        self.inventory = [
            {"name": "药草", "type": "consumable", "effect": "heal", "value": 30, "count": 5},
            {"name": "魔法药水", "type": "consumable", "effect": "mp", "value": 25, "count": 3}
        ]
        self.has_shield = False
        self.shield_turns = 0
        
    def level_up(self):
        exp_needed = self.level * 100 + 50
        if self.exp >= exp_needed:
            self.level += 1
            self.max_hp += 15 + self.level * 2
            self.hp = self.max_hp
            self.max_mp += 8 + self.level
            self.mp = self.max_mp
            self.attack += 4 + self.level
            self.defense += 2 + self.level // 2
            self.exp -= exp_needed
            
            # 学习新技能
            if self.level == 3 and len(self.spells) < 5:
                self.spells.append({"name": "火焰风暴", "damage": 45, "mp_cost": 25, "element": "fire", "desc": "强力范围魔法"})
            elif self.level == 5 and len(self.spells) < 6:
                self.spells.append({"name": "神圣护盾", "shield": True, "mp_cost": 20, "element": "holy", "desc": "减少受到的伤害"})
            
            return True
        return False


class Monster(GameEntity):
    """怪物"""
    MONSTER_DATA = {
        "slime": {
            "name": "史莱姆", "hp": 35, "attack": 10, "defense": 3,
            "exp": 18, "gold": (8, 15), "color": (0.4, 0.85, 0.4),
            "skills": ["普通攻击"], "element": "normal"
        },
        "goblin": {
            "name": "哥布林", "hp": 55, "attack": 14, "defense": 5,
            "exp": 28, "gold": (12, 22), "color": (0.55, 0.75, 0.35),
            "skills": ["普通攻击", "快速突刺"], "element": "normal"
        },
        "skeleton": {
            "name": "骷髅战士", "hp": 75, "attack": 20, "defense": 7,
            "exp": 42, "gold": (18, 30), "color": (0.92, 0.92, 0.85),
            "skills": ["普通攻击", "骨刺"], "element": "normal"
        },
        "dark_knight": {
            "name": "暗黑骑士", "hp": 100, "attack": 26, "defense": 10,
            "exp": 60, "gold": (25, 40), "color": (0.3, 0.25, 0.4),
            "skills": ["普通攻击", "暗影斩", "黑暗 aura"], "element": "dark"
        },
        "orc_warrior": {
            "name": "兽人勇士", "hp": 110, "attack": 28, "defense": 11,
            "exp": 68, "gold": (28, 45), "color": (0.6, 0.45, 0.35),
            "skills": ["普通攻击", "猛击", "咆哮"], "element": "normal"
        },
        "fire_dragon": {
            "name": "炎龙", "hp": 180, "attack": 38, "defense": 14,
            "exp": 120, "gold": (60, 100), "color": (0.85, 0.3, 0.15),
            "skills": ["普通攻击", "烈焰吐息", "龙尾横扫", "火焰风暴"],
            "element": "fire"
        },
        "ice_dragon": {
            "name": "冰霜巨龙", "hp": 200, "attack": 35, "defense": 16,
            "exp": 140, "gold": (70, 120), "color": (0.4, 0.75, 0.95),
            "skills": ["普通攻击", "冰冻吐息", "暴风雪", "绝对零度"],
            "element": "ice"
        }
    }
    
    def __init__(self, x, y, monster_type, level_multiplier=1.0):
        data = self.MONSTER_DATA.get(monster_type, self.MONSTER_DATA["slime"])
        
        super().__init__(
            x, y,
            data["name"],
            int(data["hp"] * level_multiplier),
            int(data["attack"] * level_multiplier),
            int(data["defense"] * level_multiplier)
        )
        
        self.monster_type = monster_type
        self.base_exp = int(data["exp"] * level_multiplier)
        self.gold_range = data["gold"]
        self.color = data["color"]
        self.skills = data["skills"]
        self.element = data["element"]
        self.level_mult = level_multiplier
        
    def get_gold(self):
        return random.randint(*self.gold_range)
    
    def get_skill(self):
        if len(self.skills) > 1 and random.random() < 0.35:
            return random.choice(self.skills[1:])
        return self.skills[0]


class NPC:
    """NPC类"""
    def __init__(self, x, y, name, dialog, quest=None):
        self.x = x
        self.y = y
        self.name = name
        self.dialog = dialog
        self.quest = quest
        self.talked = False


class Chest:
    """宝箱类"""
    def __init__(self, x, y, content):
        self.x = x
        self.y = y
        self.content = content
        self.opened = False


# ==================== 游戏地图 ====================

class WorldMap:
    """世界地图"""
    def __init__(self, width=1000, height=800):
        self.width = width
        self.height = height
        self.tiles = []
        self.decorations = []
        self.npcs = []
        self.chests = []
        self.portals = []  # 传送点
        self.generate()
    
    def generate(self):
        """生成地图"""
        # 地形: 0=草地 1=浅水 2=深水 3=森林 4=山地 5=路 6=沙地 7=城镇地面 8=花田
        tile_w, tile_h = 40, 40
        cols = self.width // tile_w
        rows = self.height // tile_h
        
        # 使用简化的噪声生成地形
        for row in range(rows):
            tile_row = []
            for col in range(cols):
                x, y = col * tile_w, row * tile_h
                
                # 基础噪声
                n1 = math.sin(col * 0.15) * math.cos(row * 0.15)
                n2 = math.sin(col * 0.08 + 1.5) * math.cos(row * 0.12 + 0.8)
                noise = (n1 + n2) / 2
                
                # 起始区域保护
                if col < 6 and row < 6:
                    tile_type = 0
                elif noise > 0.5:
                    tile_type = random.choice([3, 3, 4])  # 森林或山
                elif noise > 0.2:
                    tile_type = random.choice([0, 0, 8])   # 草地或花田
                elif noise > -0.2:
                    tile_type = 5                           # 路
                elif noise > -0.5:
                    tile_type = 6                           # 沙地
                else:
                    tile_type = 1                           # 水
                
                tile_row.append(tile_type)
            self.tiles.append(tile_row)
        
        # 创建城镇区域
        self.town_center = (400, 350)
        for dy in range(-3, 4):
            for dx in range(-4, 5):
                tx, ty = (self.town_center[0]//40)+dx, (self.town_center[1]//40)+dy
                if 0 <= ty < rows and 0 <= tx < cols:
                    self.tiles[ty][tx] = 7
        
        # 添加NPC
        self.npcs = [
            NPC(360, 310, "村长", 
                "欢迎来到冒险者之村！\n东边的森林里有强大的怪物，\n西边可以找到宝藏。",
                {"type": "main", "target": "dark_knight", "reward_exp": 200}),
            NPC(450, 360, "神秘商人",
                "我有最好的装备...\n不过你需要金币来购买。\n探索世界获取更多金币吧！"),
            NPC(380, 400, "老炼金术士",
                "我能感受到你身上的力量在成长...\n小心那些元素属性的怪物，\n用相克的元素攻击它们！"),
            NPC(320, 370, "吟游诗人",
                "*弹奏着悠扬的乐曲*\n要我为你演奏一曲吗？\n音乐能治愈疲惫的心灵。")
        ]
        
        # 添加宝箱
        chest_contents = [
            {"name": "金币袋", "gold": 100},
            {"name": "强化药水", "type": "buff", "stat": "attack", "value": 5},
            {"name": "铁剑", "type": "weapon", "attack": 10},
            {"name": "魔法卷轴", "type": "spell_scroll"},
            {"name": "稀有宝石", "sell_price": 150},
            {"name": "精灵之泪", "type": "consumable", "full_heal": True},
            {"name": "古代护符", "type": "accessory", "defense": 8}
        ]
        
        positions = [(180, 250), (600, 200), (750, 500), (250, 600), (550, 650),
                     (850, 300), (100, 500)]
        
        for i, pos in enumerate(positions):
            if i < len(chest_contents):
                self.chests.append(Chest(pos[0], pos[1], chest_contents[i]))
        
        # 添加装饰物（树、石头等）
        for _ in range(30):
            dx = random.randint(50, self.width-50)
            dy = random.randint(50, self.height-50)
            # 避开城镇
            if abs(dx - self.town_center[0]) > 100 or abs(dy - self.town_center[1]) > 80:
                decor_type = random.choice(["tree", "rock", "flower", "bush"])
                self.decorations.append((dx, dy, decor_type))
    
    def get_tile_color(self, tile_type):
        """获取地形的颜色"""
        colors = {
            0: (0.25, 0.58, 0.25),    # 草地
            1: (0.25, 0.45, 0.75),    # 浅水
            2: (0.15, 0.35, 0.65),    # 深水
            3: (0.15, 0.42, 0.15),    # 森林
            4: (0.52, 0.45, 0.37),    # 山地
            5: (0.62, 0.57, 0.45),    # 路
            6: (0.78, 0.72, 0.52),    # 沙地
            7: (0.72, 0.67, 0.52),    # 城镇
            8: (0.45, 0.65, 0.35)     # 花田
        }
        return colors.get(tile_type, (0.3, 0.5, 0.3))
    
    def is_walkable(self, x, y):
        """检查是否可通行"""
        if x < 10 or x >= self.width-10 or y < 10 or y >= self.height-10:
            return False
        
        tile_x = int(x // 40)
        tile_y = int(y // 40)
        
        if 0 <= tile_y < len(self.tiles) and 0 <= tile_x < len(self.tiles[0]):
            tile = self.tiles[tile_y][tile_x]
            return tile not in [2]  # 只有深水不可通行
        
        return True
    
    def get_encounter_rate(self, x, y):
        """获取遭遇战概率（根据区域）"""
        base_rate = 0.003
        
        # 危险区域
        if x > 700 or y > 600 or x < 150 or y < 150:
            base_rate = 0.006
        elif x > 500 or y > 450:
            base_rate = 0.004
        
        return base_rate
    
    def get_monster_pool(self, x, y):
        """获取当前区域的怪物池"""
        dist_from_town = math.sqrt((x - self.town_center[0])**2 + (y - self.town_center[1])**2)
        
        if dist_from_town < 150:
            return [("slime", 1.0)]
        elif dist_from_town < 300:
            return [("slime", 0.4), ("goblin", 0.5), ("skeleton", 0.1)]
        elif dist_from_town < 450:
            return [("goblin", 0.3), ("skeleton", 0.45), ("dark_knight", 0.2), ("orc_warrior", 0.05)]
        else:
            return [("skeleton", 0.2), ("dark_knight", 0.35), ("orc_warrior", 0.3),
                    ("fire_dragon", 0.08), ("ice_dragon", 0.07)]


# ==================== 主游戏界面 ====================

class RPGGame(FloatLayout):
    """游戏主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 游戏状态
        self.state = "title"  # title, playing, battle, menu, shop, talk, gameover, victory
        self.player = None
        self.world = None
        self.current_monster = None
        self.battle_turn = "player"  # player, enemy, selecting
        self.battle_log = []
        self.camera = [0, 0]
        self.particles = []
        self.current_npc = None
        self.selected_spell_idx = 0
        self.battle_menu_page = "main"  # main, magic, items
        self.monster_action_text = ""
        self.player_action_text = ""
        self.animation_queue = []
        self.animating = False
        self.turn_delay = 0
        
        # 统计数据
        self.stats = {
            "monsters_defeated": 0,
            "battles_won": 0,
            "chests_opened": 0,
            "steps_taken": 0,
            "play_time": 0
        }
        
        # 输入状态
        self.keys_pressed = set()
        self._keyboard = Window.request_keyboard(self._on_kb_close, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down)
            self._keyboard.bind(on_key_up=self._on_key_up)
        
        # 触摸/鼠标控制
        self.touch_start = None
        self.virtual_joystick_active = False
        self.joystick_vector = [0, 0]
        
        # 游戏循环
        Clock.schedule_interval(self.update, 1/60)
        
        # 初始化UI
        self.setup_ui()
    
    def _on_kb_close(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
    
    def _on_key_down(self, kb, keycode, text, mod):
        self.keys_pressed.add(keycode[1])
        
        # 战斗中的快捷键
        if self.state == "battle" and not self.animating:
            if keycode[1] == '1':
                self.do_attack()
            elif keycode[1] == '2':
                self.battle_menu_page = "magic"
                self.canvas.clear()
            elif keycode[1] == '3':
                self.battle_menu_page = "items"
                self.canvas.clear()
            elif keycode[1] == 'escape' or keycode[1] == 'backspace':
                if self.battle_menu_page != "main":
                    self.battle_menu_page = "main"
                    self.canvas.clear()
    
    def _on_key_up(self, kb, keycode):
        self.keys_pressed.discard(keycode[1])
    
    def on_touch_down(self, touch):
        self.touch_start = (touch.x, touch.y)
        
        # 处理战斗UI点击
        if self.state == "battle" and not self.animating:
            self.handle_battle_touch(touch.x, touch.y)
        elif self.state == "talk":
            # 关闭对话
            self.state = "playing"
            self.current_npc = None
        elif self.state == "title":
            # 点击开始游戏
            self.start_new_game()
        elif self.state == "gameover":
            # 点击重新开始
            self.state = "title"
            self.canvas.clear()
    
    def on_touch_move(self, touch):
        if self.touch_start and self.state == "playing":
            dx = touch.x - self.touch_start[0]
            dy = touch.y - self.touch_start[1]
            
            if abs(dx) > 20 or abs(dy) > 20:
                self.virtual_joystick_active = True
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    self.joystick_vector = [dx/length, dy/length]
    
    def on_touch_up(self, touch):
        self.touch_start = None
        self.virtual_joystick_active = False
        self.joystick_vector = [0, 0]
    
    def setup_ui(self):
        """设置UI元素"""
        pass  # 我们使用canvas绘制所有UI
    
    def start_new_game(self):
        """开始新游戏"""
        self.player = Player(160, 160)
        self.world = WorldMap()
        self.state = "playing"
        self.stats = {k: 0 for k in self.stats}
        self.add_log("欢迎来到奇幻冒险世界！", "system")
        self.add_log("使用 WASD/方向键移动，空格键互动", "system")
        self.add_log("探索世界，变强，击败强大的敌人！", "system")
    
    def update(self, dt):
        """游戏更新"""
        self.stats["play_time"] += dt
        
        if self.state == "playing":
            self.handle_input(dt)
            self.update_particles(dt)
            self.check_events()
            self.draw_world()
            
        elif self.state == "battle":
            self.update_particles(dt)
            self.process_battle(dt)
            self.draw_battle_screen()
            
        elif self.state == "title":
            self.draw_title_screen()
            
        elif self.state == "gameover":
            self.draw_gameover_screen()
            
        elif self.state == "talk":
            self.draw_talk_screen()
    
    def handle_input(self, dt):
        """处理输入"""
        speed = 140 * dt
        dx, dy = 0, 0
        
        # 键盘输入
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            dy = speed
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            dy = -speed
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            dx = -speed
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            dx = speed
        
        # 虚拟摇杆输入
        if self.virtual_joystick_active:
            dx += self.joystick_vector[0] * speed * 1.2
            dy += self.joystick_vector[1] * speed * 1.2
        
        if dx != 0 or dy != 0:
            new_x = self.player.x + dx
            new_y = self.player.y + dy
            
            # 分轴碰撞检测
            if self.world.is_walkable(new_x, self.player.y):
                self.player.x = new_x
                self.stats["steps_taken"] += 1
            if self.world.is_walkable(self.player.x, new_y):
                self.player.y = new_y
                self.stats["steps_taken"] += 1
            
            # 更新相机
            target_cx = self.player.x - Window.width / 2
            target_cy = self.player.y - Window.height / 2
            self.camera[0] += (target_cx - self.camera[0]) * 0.15
            self.camera[1] += (target_cy - self.camera[1]) * 0.15
            
            # 限制相机
            self.camera[0] = max(0, min(self.camera[0], self.world.width - Window.width))
            self.camera[1] = max(0, min(self.camera[1], self.world.height - Window.height))
        
        # 空格键互动
        if 'spacebar' in self.keys_pressed or 'enter' in self.keys_pressed:
            self.interact()
            self.keys_pressed.discard('spacebar')
            self.keys_pressed.discard('enter')
    
    def interact(self):
        """互动"""
        # 检查NPC
        for npc in self.world.npcs:
            dist = math.sqrt((self.player.x - npc.x)**2 + (self.player.y - npc.y)**2)
            if dist < 60:
                self.current_npc = npc
                self.state = "talk"
                return
        
        # 检查宝箱
        for chest in self.world.chests:
            if not chest.opened:
                dist = math.sqrt((self.player.x - chest.x)**2 + (self.player.y - chest.y)**2)
                if dist < 50:
                    self.open_chest(chest)
                    return
    
    def open_chest(self, chest):
        """打开宝箱"""
        chest.opened = True
        self.stats["chests_opened"] += 1
        content = chest.content
        
        if "gold" in content:
            self.player.gold += content["gold"]
            self.add_log(f"获得 {content['gold']} 金币！", "item")
        elif content.get("type") == "consumable":
            if content.get("full_heal"):
                self.player.hp = self.player.max_hp
                self.player.mp = self.player.max_mp
                self.add_log(f"获得 {content['name']}！完全恢复！", "item")
            else:
                self.player.inventory.append({**content, "count": 1})
                self.add_log(f"获得 {content['name']}！", "item")
        elif content.get("type") == "weapon":
            self.player.attack += content.get("attack", 0)
            self.add_log(f"装备了 {content['name']}！攻击力+{content['attack']}", "item")
        elif content.get("type") == "accessory":
            self.player.defense += content.get("defense", 0)
            self.add_log(f"装备了 {content['name']}！防御力+{content['defense']}", "item")
        elif content.get("sell_price"):
            self.player.gold += content["sell_price"]
            self.add_log(f"出售 {content['name']} 获得 {content['sell_price']} 金币", "item")
        else:
            self.player.inventory.append({**content, "count": 1})
            self.add_log(f"获得 {content['name']}！", "item")
        
        # 特效
        self.spawn_particles(chest.x, chest.y, (1, 0.85, 0.2), 15)
    
    def check_events(self):
        """检查随机事件"""
        # 遭遇战
        rate = self.world.get_encounter_rate(self.player.x, self.player.y)
        if random.random() < rate:
            self.start_encounter()
    
    def start_encounter(self):
        """开始遭遇战"""
        pool = self.world.get_monster_pool(self.player.x, self.player.y)
        
        # 根据权重选择怪物
        total_weight = sum(w for _, w in pool)
        r = random.random() * total_weight
        cumulative = 0
        monster_type = pool[0][0]
        
        for mtype, weight in pool:
            cumulative += weight
            if r <= cumulative:
                monster_type = mtype
                break
        
        # 等级加成
        level_mult = 1.0 + (self.player.level - 1) * 0.15
        level_mult = min(level_mult, 2.5)  # 上限
        
        mx = self.player.x + random.randint(-80, 80)
        my = self.player.y + random.randint(-80, 80)
        
        self.current_monster = Monster(mx, my, monster_type, level_mult)
        self.state = "battle"
        self.battle_turn = "player"
        self.battle_menu_page = "main"
        self.battle_log = []
        self.player.has_shield = False
        self.player.shield_turns = 0
        self.animating = False
        
        self.add_log(f"野生 {self.current_monster.name} 出现了！", "enemy")
        self.spawn_particles(Window.width/2, Window.height/2 - 50, (0.9, 0.2, 0.2), 25)
    
    def process_battle(self, dt):
        """处理战斗逻辑"""
        if self.turn_delay > 0:
            self.turn_delay -= dt
            return
        
        if self.animating:
            return
    
    def handle_battle_touch(self, tx, ty):
        """处理战斗界面点击"""
        btn_h, btn_w, margin = 48, 165, 10
        start_y = 95
        
        if self.battle_menu_page == "main":
            buttons = [
                (margin, start_y, "attack"),
                (margin*2+btn_w, start_y, "magic"),
                (margin, start_y-btn_h-margin, "items"),
                (margin*2+btn_w, start_y-btn_h-margin, "flee")
            ]
        elif self.battle_menu_page == "magic":
            # 显示技能列表
            spell_buttons = []
            for i, spell in enumerate(self.player.spells[:4]):
                row = i // 2
                col = i % 2
                bx = margin + col * (btn_w + margin)
                by = start_y - row * (btn_h + margin)
                spell_buttons.append((bx, by, f"spell_{i}"))
            buttons = spell_buttons
            # 返回按钮
            buttons.append((Window.width-70, 15, "back"))
        elif self.battle_menu_page == "items":
            item_buttons = []
            for i, item in enumerate(self.player.inventory[:4]):
                row = i // 2
                col = i % 2
                bx = margin + col * (btn_w + margin)
                by = start_y - row * (btn_h + margin)
                item_buttons.append((bx, by, f"item_{i}"))
            buttons = item_buttons
            buttons.append((Window.width-70, 15, "back"))
        else:
            return
        
        for bx, by, action in buttons:
            if bx <= tx <= bx + btn_w and by <= ty <= by + btn_h:
                self.execute_battle_action(action)
                return
    
    def execute_battle_action(self, action):
        """执行战斗动作"""
        if action == "attack":
            self.do_attack()
        elif action == "magic":
            self.battle_menu_page = "magic"
            self.canvas.clear()
        elif action == "items":
            self.battle_menu_page = "items"
            self.canvas.clear()
        elif action == "flee":
            self.try_flee()
        elif action.startswith("spell_"):
            idx = int(action.split("_")[1])
            self.cast_spell(idx)
        elif action.startswith("item_"):
            idx = int(action.split("_")[1])
            self.use_item(idx)
        elif action == "back":
            self.battle_menu_page = "main"
            self.canvas.clear()
    
    def do_attack(self):
        """普通攻击"""
        if self.animating or not self.current_monster or not self.current_monster.is_alive():
            return
        
        self.animating = True
        damage = self.current_monster.take_damage(self.player.attack)
        self.player_action_text = f"攻击造成 {damage} 点伤害！"
        self.add_log(f"你攻击了 {self.current_monster.name}，造成 {damage} 点伤害！", "player")
        
        self.spawn_particles(Window.width/2, Window.height/2 - 80, (1, 0.5, 0.2), 12)
        
        if not self.current_monster.is_alive():
            Clock.schedule_once(lambda d: self.on_monster_defeated(), 0.8)
        else:
            Clock.schedule_once(lambda d: self.enemy_turn(), 1.0)
    
    def cast_spell(self, idx):
        """施放魔法"""
        if self.animating or idx >= len(self.player.spells):
            return
        
        spell = self.player.spells[idx]
        
        if self.player.mp < spell["mp_cost"]:
            self.add_log("MP不足！", "error")
            return
        
        self.animating = True
        self.player.mp -= spell["mp_cost"]
        
        element_colors = {
            "fire": (1, 0.4, 0.1),
            "ice": (0.3, 0.7, 1),
            "thunder": (1, 1, 0.2),
            "holy": (1, 1, 0.9),
            "dark": (0.6, 0.2, 0.8)
        }
        
        if "heal" in spell:
            heal_amt = spell["heal"]
            self.player.heal(heal_amt)
            self.player_action_text = f"{spell['name']} 恢复了 {heal_amt} HP！"
            self.add_log(f"你使用了 {spell['name']}，恢复了 {heal_amt} 点生命！", "magic")
            self.spawn_particles(80, 230, element_colors.get(spell["element"], (0.2, 0.9, 0.3)), 20)
            Clock.schedule_once(lambda d: self.enemy_turn(), 1.0)
            
        elif "shield" in spell:
            self.player.has_shield = True
            self.player.shield_turns = 3
            self.player_action_text = f"激活了 {spell['name']}！"
            self.add_log(f"你使用了 {spell['name']}，获得了神圣护盾！", "magic")
            self.spawn_particles(80, 230, element_colors.get(spell["element"], (1, 1, 0.9)), 20)
            Clock.schedule_once(lambda d: self.enemy_turn(), 1.0)
            
        else:
            damage = spell["damage"]
            # 元素克制
            elem = spell["element"]
            mon_elem = self.current_monster.element
            
            advantage = {
                ("fire", "ice"): 1.5, ("ice", "fire"): 1.5,
                ("thunder", "water"): 1.5, ("thunder", "ice"): 1.3,
                ("holy", "dark"): 1.5, ("dark", "holy"): 1.5
            }
            
            key = (elem, mon_elem)
            if key in advantage:
                damage = int(damage * advantage[key])
                self.add_log("元素克制！伤害提升！", "magic")
            
            actual_dmg = self.current_monster.take_damage(damage)
            self.player_action_text = f"{spell['name']} 造成 {actual_dmg} 点伤害！"
            self.add_log(f"你使用了 {spell['name']}，造成 {actual_dmg} 点伤害！", "magic")
            
            color = element_colors.get(elem, (1, 0.5, 0))
            self.spawn_particles(Window.width/2, Window.height/2 - 80, color, 25)
            
            if not self.current_monster.is_alive():
                Clock.schedule_once(lambda d: self.on_monster_defeated(), 0.8)
            else:
                Clock.schedule_once(lambda d: self.enemy_turn(), 1.0)
    
    def use_item(self, idx):
        """使用物品"""
        if self.animating or idx >= len(self.player.inventory):
            return
        
        item = self.player.inventory[idx]
        
        if item["count"] <= 0:
            self.add_log("物品已用完！", "error")
            return
        
        self.animating = True
        item["count"] -= 1
        
        if item.get("effect") == "heal":
            heal_val = item.get("value", 30)
            self.player.heal(heal_val)
            self.player_action_text = f"使用了 {item['name']}，恢复 {heal_val} HP！"
            self.add_log(f"使用了 {item['name']}，恢复了 {heal_val} 点生命！", "item")
        elif item.get("effect") == "mp":
            mp_val = item.get("value", 25)
            self.player.mp = min(self.player.max_mp, self.player.mp + mp_val)
            self.player_action_text = f"使用了 {item['name']}，恢复 {mp_val} MP！"
            self.add_log(f"使用了 {item['name']}，恢复了 {mp_val} 点魔法值！", "item")
        
        # 清理空物品
        if item["count"] <= 0:
            self.player.inventory.pop(idx)
        
        self.spawn_particles(80, 230, (0.2, 0.9, 0.3), 15)
        Clock.schedule_once(lambda d: self.enemy_turn(), 0.8)
    
    def try_flee(self):
        """尝试逃跑"""
        if self.animating:
            return
        
        flee_chance = 0.5 + (self.player.level - (self.current_monster.level if hasattr(self.current_monster, 'level') else 1)) * 0.05
        flee_chance = max(0.2, min(0.9, flee_chance))
        
        if random.random() < flee_chance:
            self.add_log("成功逃跑了！", "system")
            self.end_battle(fled=True)
        else:
            self.add_log("逃跑失败！", "error")
            self.enemy_turn()
    
    def enemy_turn(self):
        """敌人回合"""
        if not self.current_monster or not self.current_monster.is_alive():
            return
        
        skill_name = self.current_monster.get_skill()
        
        # 计算伤害
        damage = self.current_monster.attack
        if skill_name != "普通攻击":
            damage = int(damage * 1.3)
            self.monster_action_text = f"{self.current_monster.name} 使用了 {skill_name}！"
        else:
            self.monster_action_text = f"{self.current_monster.name} 的攻击！"
        
        # 护盾减伤
        if self.player.has_shield:
            damage = int(damage * 0.5)
            self.player.shield_turns -= 1
            if self.player.shield_turns <= 0:
                self.player.has_shield = False
                self.add_log("神圣护盾消散了...", "system")
        
        actual_dmg = self.player.take_damage(damage)
        self.add_log(f"{self.current_monster.name} 对你造成 {actual_dmg} 点伤害！", "enemy")
        
        self.spawn_particles(80, 230, (0.8, 0.2, 0.2), 10)
        
        if not self.player.is_alive():
            Clock.schedule_once(lambda d: self.on_player_defeated(), 0.5)
        else:
            self.animating = False
            self.battle_menu_page = "main"
            self.turn_delay = 0.3
            self.canvas.clear()
    
    def on_monster_defeated(self):
        """怪物被击败"""
        self.stats["monsters_defeated"] += 1
        self.stats["battles_won"] += 1
        
        gold = self.current_monster.get_gold()
        exp = self.current_monster.base_exp
        
        self.player.gold += gold
        self.player.exp += exp
        
        self.add_log(f"战斗胜利！获得 {exp} 经验值 和 {gold} 金币！", "victory")
        self.spawn_particles(Window.width/2, Window.height/2, (1, 0.85, 0.2), 30)
        
        leveled = False
        while self.player.level_up():
            self.add_log(f"升级了！当前等级：{self.player.level}！", "levelup")
            leveled = True
            self.spawn_particles(80, 230, (1, 1, 0.3), 25)
        
        Clock.schedule_once(lambda d: self.end_battle(), 2.0 if leveled else 1.5)
    
    def on_player_defeated(self):
        """玩家被击败"""
        self.state = "gameover"
        self.add_log("你被击败了...", "defeat")
    
    def end_battle(self, fled=False):
        """结束战斗"""
        self.state = "playing"
        self.current_monster = None
        self.battle_log = []
        self.animating = False
        self.battle_menu_page = "main"
        self.canvas.clear()
    
    def add_log(self, msg, msg_type="normal"):
        """添加战斗日志"""
        self.battle_log.append({"text": msg, "type": msg_type})
        if len(self.battle_log) > 6:
            self.battle_log.pop(0)
    
    def spawn_particles(self, x, y, color, count=10):
        """生成粒子特效"""
        for _ in range(count):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-120, 120),
                'vy': random.uniform(-120, 120),
                'life': random.uniform(0.5, 1.5),
                'max_life': 1.5,
                'color': color,
                'size': random.uniform(3, 8)
            })
    
    def update_particles(self, dt):
        """更新粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vx'] *= 0.96
            p['vy'] *= 0.96
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)
    
    # ==================== 绘制函数 ====================
    
    def draw_title_screen(self):
        """绘制标题画面"""
        self.canvas.clear()
        with self.canvas:
            # 渐变背景
            Color(0.08, 0.06, 0.15, 1)
            Rectangle(pos=(0, 0), size=Window.size)
            
            # 星星效果
            for i in range(30):
                sx = (i * 137 + self.stats["play_time"] * 10 * (i%3+1)) % Window.width
                sy = (i * 89) % (Window.height - 200)
                brightness = 0.3 + 0.7 * abs(math.sin(self.stats["play_time"] * 2 + i))
                Color(brightness, brightness, brightness * 0.9, 1)
                Ellipse(pos=(sx, sy), size=(3, 3))
            
            # 标题框
            Color(0.15, 0.12, 0.25, 0.95)
            Rectangle(pos=(30, Window.height-220), size=(Window.width-60, 170))
            
            # 标题装饰边框
            Color(0.85, 0.7, 0.25, 1)
            Line(rectangle=(32, Window.height-218, Window.width-64, 166), width=2)
            
            # 标题文字区域（装饰）
            Color(0.9, 0.75, 0.3, 1)
            Rectangle(pos=(Window.width/2-130, Window.height-180), size=(260, 60))
            
            Color(0.2, 0.15, 0.3, 1)
            Rectangle(pos=(Window.width/2-125, Window.height-175), size=(250, 50))
            
            # 剑图标装饰
            Color(0.85, 0.85, 0.9, 1)
            Ellipse(pos=(Window.width/2-140, Window.height-165), size=(30, 30))
            Ellipse(pos=(Window.width/2+110, Window.height-165), size=(30, 30))
            
            # 开始提示
            pulse = 0.5 + 0.5 * math.sin(self.stats["play_time"] * 3)
            Color(1, 1, 1, pulse)
            Rectangle(pos=(Window.width/2-80, 180), size=(160, 40))
            
            # 版本信息
            Color(0.5, 0.5, 0.55, 1)
            Rectangle(pos=(10, 10), size=(150, 25))
    
    def draw_gameover_screen(self):
        """绘制游戏结束画面"""
        self.canvas.clear()
        with self.canvas:
            Color(0.1, 0.05, 0.1, 0.95)
            Rectangle(pos=(0, 0), size=Window.size)
            
            Color(0.6, 0.1, 0.15, 1)
            Rectangle(pos=(40, Window.height/2-80), size=(Window.width-80, 160))
            
            Color(0.9, 0.2, 0.2, 1)
            Rectangle(pos=(50, Window.height/2-70), size=(Window.width-100, 50))
            
            # 统计信息
            Color(0.8, 0.8, 0.8, 1)
            stats_text = f"Lv.{self.player.level} | 击败:{self.stats['monsters_defeated']} | 宝箱:{self.stats['chests_opened']}"
            Rectangle(pos=(60, Window.height/2-130), size=(Window.width-120, 30))
            
            Color(0.6, 0.6, 0.65, 1)
            Rectangle(pos=(Window.width/2-90, Window.height/2-170), size=(180, 35))
    
    def draw_world(self):
        """绘制世界地图"""
        self.canvas.clear()
        with self.canvas:
            cx, cy = self.camera
            
            # 绘制地图块
            tile_size = 40
            start_col = max(0, int(cx // tile_size))
            end_col = min(len(self.world.tiles[0]), int((cx + Window.width) // tile_size) + 2)
            start_row = max(0, int(cy // tile_size))
            end_row = min(len(self.world.tiles), int((cy + Window.height) // tile_size) + 2)
            
            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    tile = self.world.tiles[row][col]
                    color = self.world.get_tile_color(tile)
                    
                    screen_x = col * tile_size - cx
                    screen_y = row * tile_size - cy
                    
                    Color(*color, 1)
                    Rectangle(pos=(screen_x, screen_y), size=(tile_size, tile_size))
                    
                    # 添加网格线（微弱）
                    if tile != 7:  # 非城镇
                        Color(0, 0, 0, 0.05)
                        Line(points=[screen_x, screen_y, screen_x+tile_size, screen_y,
                                    screen_x+tile_size, screen_y, screen_x+tile_size, screen_y+tile_size],
                              width=0.5)
            
            # 绘制装饰物
            for dx, dy, dtype in self.world.decorations:
                sx, sy = dx - cx, dy - cy
                if -20 < sx < Window.width+20 and -20 < sy < Window.height+20:
                    if dtype == "tree":
                        Color(0.35, 0.22, 0.12, 1)
                        Rectangle(pos=(sx-5, sy-15), size=(10, 20))
                        Color(0.15, 0.45, 0.15, 1)
                        Ellipse(pos=(sx-18, sy), size=(36, 36))
                    elif dtype == "rock":
                        Color(0.5, 0.48, 0.45, 1)
                        Ellipse(pos=(sx-12, sy-8), size=(24, 16))
                    elif dtype == "flower":
                        Color(0.2, 0.5, 0.2, 1)
                        Ellipse(pos=(sx-2, sy-6), size=(4, 10))
                        Color(random.choice([(1,0.3,0.4),(1,0.8,0.2),(0.9,0.5,1)]))
                        Ellipse(pos=(sx-4, sy-4), size=(8, 8))
                    elif dtype == "bush":
                        Color(0.2, 0.4, 0.18, 1)
                        Ellipse(pos=(sx-10, sy-6), size=(20, 12))
            
            # 绘制宝箱
            for chest in self.world.chests:
                sx, sy = chest.x - cx, chest.y - cy
                if 0 < sx < Window.width and 0 < sy < Window.height:
                    if chest.opened:
                        Color(0.45, 0.4, 0.35, 1)
                    else:
                        Color(0.85, 0.7, 0.25, 1)
                        # 发光效果
                        glow = 0.5 + 0.5 * math.sin(self.stats["play_time"] * 4)
                        Color(0.9, 0.8, 0.3, glow * 0.3)
                        Ellipse(pos=(sx-18, sy-18), size=(36, 36))
                        Color(0.85, 0.7, 0.25, 1)
                    Rectangle(pos=(sx-12, sy-8), size=(24, 16))
                    Color(0.6, 0.5, 0.3, 1)
                    Rectangle(pos=(sx-10, sy-6), size=(20, 3))
            
            # 绘制NPC
            for npc in self.world.npcs:
                sx, sy = npc.x - cx, npc.y - cy
                if 0 < sx < Window.width and 0 < sy < Window.height:
                    # 身体
                    Color(0.35, 0.5, 0.8, 1)
                    Ellipse(pos=(sx-14, sy-14), size=(28, 28))
                    # 脸
                    Color(0.95, 0.88, 0.82, 1)
                    Ellipse(pos=(sx-9, sy-5), size=(18, 16))
                    # 名字标记
                    Color(1, 1, 1, 0.8)
                    Rectangle(pos=(sx-25, sy+18), size=(50, 14))
                    # 问号
                    Color(1, 0.85, 0.2, 1)
                    Ellipse(pos=(sx+10, sy-20), size=(12, 12))
            
            # 绘制玩家
            px, py = self.player.x - cx, self.player.y - cy
            
            # 影子
            Color(0, 0, 0, 0.25)
            Ellipse(pos=(px-12, py-18), size=(24, 10))
            
            # 身体
            Color(0.2, 0.35, 0.8, 1)
            Ellipse(pos=(px-16, py-16), size=(32, 32))
            
            # 披风/装饰
            Color(0.15, 0.25, 0.6, 1)
            Ellipse(pos=(px-18, py-8), size=(12, 20))
            
            # 脸
            Color(0.98, 0.92, 0.85, 1)
            Ellipse(pos=(px-10, py-4), size=(20, 18))
            
            # 眼睛
            Color(0.15, 0.25, 0.5, 1)
            Ellipse(pos=(px-6, py+2), size=(5, 5))
            Ellipse(pos=(px+2, py+2), size=(5, 5))
            
            # 绘制粒子
            for p in self.particles:
                alpha = p['life'] / p['max_life']
                Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                size = p['size'] * alpha
                Ellipse(pos=(p['x']-cx-size/2, p['y']-cy-size/2), size=(size, size))
            
            # UI层
            self.draw_hud()
    
    def draw_hud(self):
        """绘制HUD"""
        with self.canvas:
            # HUD背景
            Color(0.1, 0.12, 0.18, 0.88)
            Rectangle(pos=(0, Window.height-70), size=(Window.width, 70))
            
            Color(0.2, 0.22, 0.3, 0.5)
            Line(points=[0, Window.height-70, Window.width, Window.height-70], width=1)
            
            # HP条背景
            Color(0.25, 0.2, 0.2, 1)
            Rectangle(pos=(10, Window.height-30), size=(200, 18))
            
            # HP条
            hp_ratio = self.player.hp / self.player.max_hp
            hp_color = (0.2, 0.8, 0.3) if hp_ratio > 0.3 else (0.9, 0.4, 0.2)
            Color(*hp_color, 1)
            Rectangle(pos=(10, Window.height-30), size=(200 * hp_ratio, 18))
            
            # MP条背景
            Color(0.2, 0.2, 0.28, 1)
            Rectangle(pos=(10, Window.height-55), size=(160, 16))
            
            # MP条
            mp_ratio = self.player.mp / self.player.max_mp
            Color(0.25, 0.45, 0.9, 1)
            Rectangle(pos=(10, Window.height-55), size=(160 * mp_ratio, 16))
            
            # 文字区域
            Color(1, 1, 1, 0.92)
            Rectangle(pos=(220, Window.height-55), size=(130, 43))
            
            # 金币显示
            Color(1, 0.85, 0.2, 1)
            Ellipse(pos=(225, Window.height-50), size=(18, 18))
            
            # 小地图
            Color(0.08, 0.1, 0.15, 0.8)
            Rectangle(pos=(Window.width-85, Window.height-85), size=(75, 75))
            Color(0.15, 0.18, 0.25, 1)
            Line(rectangle=(Window.width-85, Window.height-85, 75, 75), width=1)
            
            # 小地图上的玩家点
            minimap_px = Window.width - 85 + (self.player.x / self.world.width) * 75
            minimap_py = Window.height - 85 + (self.player.y / self.world.height) * 75
            Color(0.2, 0.5, 1, 1)
            Ellipse(pos=(minimap_px-3, minimap_py-3), size=(6, 6))
            
            # 城镇位置
            town_mx = Window.width - 85 + (self.world.town_center[0] / self.world.width) * 75
            town_my = Window.height - 85 + (self.world.town_center[1] / self.world.height) * 75
            Color(0.8, 0.7, 0.3, 1)
            Rectangle(pos=(town_mx-3, town_my-3), size=(6, 6))
    
    def draw_battle_screen(self):
        """绘制战斗界面"""
        with self.canvas:
            # 背景
            Color(0.12, 0.08, 0.18, 1)
            Rectangle(pos=(0, 0), size=Window.size)
            
            # 怪物区域背景
            Color(0.18, 0.12, 0.25, 1)
            Rectangle(pos=(20, Window.height-290), size=(Window.width-40, 260))
            
            # 怪物区域装饰
            Color(0.3, 0.2, 0.4, 0.5)
            for i in range(5):
                rx = random.randint(30, Window.width-50)
                ry = Window.height-280 + random.randint(0, 240)
                Ellipse(pos=(rx, ry), size=(random.randint(2, 6), random.randint(2, 6)))
            
            if self.current_monster:
                # 怪物阴影
                Color(0, 0, 0, 0.3)
                Ellipse(pos=(Window.width/2-45, Window.height-210), size=(90, 25))
                
                # 怪物身体
                mc = self.current_monster.color
                Color(*mc, 1)
                
                # 根据类型绘制不同形状
                mt = self.current_monster.monster_type
                if mt == "slime":
                    # 史莱姆 - 果冻状
                    Ellipse(pos=(Window.width/2-40, Window.height-190), size=(80, 65))
                    Color(mc[0]*0.8, mc[1]*0.9, mc[2]*0.8, 0.7)
                    Ellipse(pos=(Window.width/2-30, Window.height-175), size=(60, 35))
                elif "dragon" in mt:
                    # 龙 - 大型
                    Ellipse(pos=(Window.width/2-55, Window.height-210), size=(110, 90))
                    # 翅膀
                    Color(mc[0]*0.7, mc[1]*0.7, mc[2]*0.8, 0.8)
                    Ellipse(pos=(Window.width/2-80, Window.height-195), size=(50, 55))
                    Ellipse(pos=(Window.width/2+30, Window.height-195), size=(50, 55))
                    Color(*mc, 1)
                else:
                    # 其他怪物
                    Ellipse(pos=(Window.width/2-38, Window.height-185), size=(76, 80))
                
                # 眼睛
                eye_y = Window.height-155 if mt == "slime" else Window.height-145
                eye_offset = 18 if mt in ["dragon"] else 14
                
                Color(1, 1, 1, 1)
                Ellipse(pos=(Window.width/2-eye_offset, eye_y), size=(16, 18))
                Ellipse(pos=(Window.width/2+eye_offset-16, eye_y), size=(16, 18))
                
                # 瞳孔
                Color(0.15, 0.1, 0.2, 1)
                Ellipse(pos=(Window.width/2-eye_offset+4, eye_y+4), size=(8, 10))
                Ellipse(pos=(Window.width/2+eye_offset-12, eye_y+4), size=(8, 10))
                
                # 怪物名称标签
                Color(0.15, 0.12, 0.22, 0.92)
                name_width = len(self.current_monster.name) * 14 + 30
                Rectangle(pos=(Window.width/2-name_width/2, Window.height-275), size=(name_width, 26))
                
                Color(0.9, 0.2, 0.2, 1)
                Rectangle(pos=(Window.width/2-name_width/2+2, Window.height-273), size=(name_width-4, 22))
                
                # 怪物血条
                Color(0.2, 0.18, 0.2, 1)
                Rectangle(pos=(40, Window.height-300), size=(Window.width-80, 14))
                
                hp_ratio = self.current_monster.hp / self.current_monster.max_hp
                if hp_ratio > 0.5:
                    Color(0.85, 0.25, 0.2, 1)
                elif hp_ratio > 0.25:
                    Color(0.9, 0.7, 0.15, 1)
                else:
                    Color(0.9, 0.3, 0.3, 1)
                    # 低血量闪烁
                    if int(self.stats["play_time"] * 4) % 2:
                        Color(1, 0.1, 0.1, 1)
                
                Rectangle(pos=(40, Window.height-300), size=((Window.width-80) * hp_ratio, 14))
                
                # HP文字
                Color(1, 1, 1, 0.93)
                Rectangle(pos=(Window.width/2-40, Window.height-298), size=(80, 10))
            
            # 玩家状态面板
            Color(0.12, 0.15, 0.22, 0.94)
            Rectangle(pos=(8, 155), size=(Window.width-16, 135))
            
            Color(0.25, 0.28, 0.38, 0.6)
            Line(rectangle=(8, 155, Window.width-16, 135), width=1)
            
            # 玩家头像圆圈
            Color(0.2, 0.35, 0.75, 1)
            Ellipse(pos=(18, 222), size=(56, 56))
            
            Color(0.15, 0.25, 0.6, 1)
            Ellipse(pos=(26, 238), size=(40, 32))
            
            Color(0.95, 0.9, 0.85, 1)
            Ellipse(pos=(30, 245), size=(32, 26))
            
            # HP条
            Color(0.2, 0.18, 0.18, 1)
            Rectangle(pos=(85, 270), size=(Window.width-100, 16))
            
            hp_r = self.player.hp / self.player.max_hp
            Color(0.25, 0.82, 0.3, 1)
            Rectangle(pos=(85, 270), size=((Window.width-100) * hp_r, 16))
            
            # MP条
            Color(0.18, 0.18, 0.25, 1)
            Rectangle(pos=(85, 248), size=(Window.width-100, 14))
            
            mp_r = self.player.mp / self.player.max_mp
            Color(0.28, 0.5, 0.92, 1)
            Rectangle(pos=(85, 248), size=((Window.width-100) * mp_r, 14))
            
            # EXP条
            Color(0.18, 0.17, 0.18, 1)
            Rectangle(pos=(85, 228), size=(Window.width-100, 10))
            
            exp_needed = self.player.level * 100 + 50
            exp_r = self.player.exp / exp_needed if exp_needed > 0 else 0
            Color(0.92, 0.82, 0.22, 1)
            Rectangle(pos=(85, 228), size=((Window.width-100) * exp_r, 10))
            
            # 护盾指示器
            if self.player.has_shield:
                shield_pulse = 0.5 + 0.5 * math.sin(self.stats["play_time"] * 5)
                Color(1, 1, 0.8, shield_pulse * 0.6)
                Ellipse(pos=(14, 218), size=(64, 66))
            
            # 战斗操作区
            Color(0.13, 0.16, 0.24, 0.96)
            Rectangle(pos=(6, 8), size=(Window.width-12, 140))
            
            Color(0.28, 0.3, 0.42, 0.5)
            Line(rectangle=(6, 8, Window.width-12, 140), width=1)
            
            # 按钮
            if self.battle_menu_page == "main":
                buttons = [
                    (12, 97, (0.28, 0.62, 0.32), "攻 击"),
                    (183, 97, (0.32, 0.42, 0.78), "魔 法"),
                    (12, 44, (0.82, 0.72, 0.28), "物 品"),
                    (183, 44, (0.72, 0.32, 0.32), "逃 跑")
                ]
            elif self.battle_menu_page == "magic":
                buttons = []
                for i, spell in enumerate(self.player.spells[:4]):
                    row, col = i // 2, i % 2
                    bx = 12 + col * 171
                    by = 97 - row * 53
                    can_cast = self.player.mp >= spell["mp_cost"]
                    color = (0.3, 0.4, 0.7) if can_cast else (0.35, 0.35, 0.35)
                    buttons.append((bx, by, color, f"{spell['name']} ({spell['mp_cost']}MP)"))
                # 返回按钮
                buttons.append((Window.width-72, 12, (0.5, 0.35, 0.35), "返回"))
            elif self.battle_menu_page == "items":
                buttons = []
                for i, item in enumerate(self.player.inventory[:4]):
                    row, col = i // 2, i % 2
                    bx = 12 + col * 171
                    by = 97 - row * 53
                    count_str = f"x{item.get('count', 1)}" if item.get('count', 1) > 1 else ""
                    buttons.append((bx, by, (0.35, 0.6, 0.35), f"{item['name']} {count_str}"))
                buttons.append((Window.width-72, 12, (0.5, 0.35, 0.35), "返回"))
            else:
                buttons = []
            
            for bx, by, bc, text in buttons:
                bw, bh = 159, 46
                Color(*bc, 1)
                Rectangle(pos=(bx, by), size=(bw, bh))
                
                # 按钮高光
                Color(1, 1, 1, 0.12)
                Rectangle(pos=(bx, by+bh-4), size=(bw, 4))
                
                Color(1, 1, 1, 0.92)
                text_w = len(text) * 8 + 16
                Rectangle(pos=(bx+(bw-text_w)/2, by+(bh-20)/2), size=(text_w, 20))
            
            # 战斗日志
            Color(0.08, 0.08, 0.12, 0.92)
            Rectangle(pos=(8, 298), size=(Window.width-16, 125))
            
            Color(0.22, 0.2, 0.28, 0.6)
            Line(rectangle=(8, 298, Window.width-16, 125), width=1)
            
            # 日志文字
            log_y = 412
            for log_entry in self.battle_log[-5:]:
                ltype = log_entry["type"]
                if ltype == "player":
                    Color(0.4, 0.75, 1, 1)
                elif ltype == "enemy":
                    Color(1, 0.4, 0.4, 1)
                elif ltype == "magic":
                    Color(0.9, 0.5, 1, 1)
                elif ltype == "item":
                    Color(0.4, 1, 0.5, 1)
                elif ltype == "victory":
                    Color(1, 0.85, 0.2, 1)
                elif ltype == "levelup":
                    Color(1, 1, 0.3, 1)
                elif ltype == "error":
                    Color(1, 0.5, 0.5, 1)
                else:
                    Color(0.85, 0.85, 0.85, 1)
                
                Rectangle(pos=(14, log_y-14), size=(Window.width-28, 18))
                log_y -= 20
            
            # 动作文字
            if self.player_action_text:
                Color(0.3, 0.8, 1, 0.95)
                Rectangle(pos=(Window.width/2-100, 195), size=(200, 22))
            
            if self.monster_action_text:
                Color(1, 0.4, 0.4, 0.95)
                Rectangle(pos=(Window.width/2-100, Window.height-235), size=(200, 22))
            
            # 绘制粒子
            for p in self.particles:
                alpha = p['life'] / p['max_life']
                Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                sz = p['size'] * alpha
                Ellipse(pos=(p['x']-sz/2, p['y']-sz/2), size=(sz, sz))
    
    def draw_talk_screen(self):
        """绘制对话界面"""
        # 先绘制世界
        self.draw_world()
        
        with self.canvas:
            # 对话框背景
            Color(0.1, 0.08, 0.15, 0.95)
            Rectangle(pos=(15, 15), size=(Window.width-30, 160))
            
            Color(0.3, 0.25, 0.4, 0.8)
            Line(rectangle=(15, 15, Window.width-30, 160), width=2)
            
            # NPC名称
            if self.current_npc:
                Color(0.2, 0.18, 0.28, 1)
                name_w = len(self.current_npc.name) * 16 + 24
                Rectangle(pos=(22, 148), size=(name_w, 24))
                
                Color(0.9, 0.75, 0.35, 1)
                Rectangle(pos=(24, 150), size=(name_w-4, 20))
                
                # 对话内容
                Color(0.92, 0.9, 0.88, 0.95)
                lines = self.current_npc.dialog.split('\n')
                line_y = 125
                for line in lines[:4]:
                    Rectangle(pos=(28, line_y-12), size=(Window.width-56, 18))
                    line_y -= 22
                
                # 提示
                pulse = 0.4 + 0.6 * abs(math.sin(self.stats["play_time"] * 3))
                Color(1, 1, 1, pulse)
                Rectangle(pos=(Window.width-100, 25), size=(80, 18))


class FantasyRPGApp(App):
    """应用入口"""
    def build(self):
        self.title = "Fantasy RPG Adventure"
        Window.bind(on_keyboard=self._on_back)
        return RPGGame()
    
    def _on_back(self, window, key, *args):
        if key == 27:  # Back button
            # 可以在这里处理后退键
            pass
        return True


if __name__ == '__main__':
    FantasyRPGApp().run()
