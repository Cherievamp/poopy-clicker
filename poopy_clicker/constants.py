import sys
import os


def get_base_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = get_base_path()
ASSET_PATH = os.path.join(BASE_PATH, "assets")
SAVE_PATH = os.path.join(os.path.expanduser("~"), ".poopy-clicker", "save.json")

MAX_GOOBERS = 10
CLICK_SPAWN_THRESHOLD = 15
PASSIVE_SPAWN_INTERVAL_MS = 12000
SECRET_SHOP_UNLOCK_CLICKS = 40
BOSS_SPAWN_CHANCE = 0.05
COSMETIC_COLOR_CHANCE = 0.14
EVENT_CHECK_INTERVAL_MS = 9000
EVENT_TRIGGER_CHANCE = 0.22
AUTO_SAVE_INTERVAL_MS = 60000

GOOBER_COLORS = [
    (255, 120, 120, 120), (120, 180, 255, 120), (140, 255, 160, 120),
    (255, 220, 120, 120), (220, 140, 255, 120), (255, 170, 220, 120),
]

RARITY_INFO = {
    "common":    {"label": "Comum",     "color": "#d9d9d9", "mult": 1.0},
    "rare":      {"label": "Raro",      "color": "#76d7ff", "mult": 1.25},
    "epic":      {"label": "Épico",     "color": "#c792ea", "mult": 1.6},
    "legendary": {"label": "Lendário",  "color": "#ffcf66", "mult": 2.1},
    "mythic":    {"label": "Mítico",    "color": "#ff66ff", "mult": 3.0},
}

RARITY_SPAWN_WEIGHT = {
    "common": 1.0, "rare": 0.6, "epic": 0.35, "legendary": 0.15, "mythic": 0.08,
}

GOOBER_INFO = {
    "normal": {"name": "Normal", "rarity": "common"},
    "gold": {"name": "Gold", "rarity": "rare"},
    "angry": {"name": "Angry", "rarity": "epic"},
    "tiny": {"name": "Tiny", "rarity": "epic"},
    "giant": {"name": "Giant", "rarity": "epic"},
    "frozen": {"name": "Frozen", "rarity": "rare"},
    "bomb": {"name": "Bomb", "rarity": "rare"},
    "rgb": {"name": "RGB", "rarity": "mythic"},
    "boss": {"name": "Boss", "rarity": "legendary"},
    "slime": {"name": "Slime", "rarity": "common"},
    "shadow": {"name": "Shadow", "rarity": "rare"},
    "candy": {"name": "Candy", "rarity": "common"},
    "crystal": {"name": "Crystal", "rarity": "rare"},
    "storm": {"name": "Storm", "rarity": "legendary"},
    "glitch": {"name": "Glitch", "rarity": "legendary"},
    "toxic": {"name": "Toxic", "rarity": "epic"},
    "magnet": {"name": "Magnet", "rarity": "epic"},
    "sleepy": {"name": "Sleepy", "rarity": "rare"},
    "speedy": {"name": "Speedy", "rarity": "common"},
    "royal": {"name": "Royal", "rarity": "legendary"},
    "plasma": {"name": "Plasma", "rarity": "legendary"},
    "stone": {"name": "Stone", "rarity": "common"},
    "ghost": {"name": "Ghost", "rarity": "epic"},
    "lava": {"name": "Lava", "rarity": "legendary"},
    "clockwork": {"name": "Clockwork", "rarity": "epic"},
    "neon": {"name": "Neon", "rarity": "rare"},
    "pirate": {"name": "Pirate", "rarity": "legendary"},
    "angel": {"name": "Angel", "rarity": "mythic"},
    "devil": {"name": "Devil", "rarity": "mythic"},
    "moss": {"name": "Moss", "rarity": "common"},
    "prism": {"name": "Prism", "rarity": "mythic"},
    "voidling": {"name": "Voidling", "rarity": "legendary"},
    "chef": {"name": "Chef", "rarity": "rare"},
    "samurai": {"name": "Samurai", "rarity": "epic"},
    "arcade": {"name": "Arcade", "rarity": "epic"},
    "bubble": {"name": "Bubble", "rarity": "common"},
    "crown": {"name": "Crown", "rarity": "legendary"},
    "fairy": {"name": "Fairy", "rarity": "legendary"},
}

EXTRA_GOOBER_DATA = {
    "slime": {"name": "Slime", "rarity": "common", "money_reward": 220, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 2, "size_multiplier": 0.95, "normal_push": 5, "panic_push": 20, "label_name": "SLIME", "color": (120, 255, 120, 135), "desc": "Escorrega pela tela e rende um dinheirinho extra."},
    "shadow": {"name": "Shadow", "rarity": "rare", "money_reward": 1500, "coin_reward": 2, "click_progress_reward": 2, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.0, "normal_push": 9, "panic_push": 32, "label_name": "SHADOW", "color": (120, 120, 120, 150), "desc": "Escuro e furtivo, puxa um pouco mais o ritmo da run."},
    "candy": {"name": "Candy", "rarity": "common", "money_reward": 480, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.0, "normal_push": 6, "panic_push": 24, "label_name": "CANDY", "color": (255, 140, 210, 150), "desc": "Fofo, doce e comum. Um bom respiro entre os caos."},
    "crystal": {"name": "Crystal", "rarity": "rare", "money_reward": 2400, "coin_reward": 3, "click_progress_reward": 2, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.1, "normal_push": 6, "panic_push": 26, "label_name": "CRYSTAL", "color": (120, 240, 255, 160), "desc": "Brilha bastante e paga bem."},
    "storm": {"name": "Storm", "rarity": "legendary", "money_reward": 3600, "coin_reward": 3, "click_progress_reward": 3, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.05, "normal_push": 10, "panic_push": 35, "label_name": "STORM", "color": (160, 190, 255, 150), "event_on_click": ("storm_mode", 7, "Storm mode", "vento e gravidade bagunçam o botão", "#9fb8ff"), "desc": "Chama uma tempestade curta quando clicado."},
    "glitch": {"name": "Glitch", "rarity": "legendary", "money_reward": 4200, "coin_reward": 4, "click_progress_reward": 3, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.05, "normal_push": 8, "panic_push": 30, "label_name": "GLITCH", "color": (255, 120, 255, 145), "event_on_click": ("glitch_flip", 6, "Glitch flip", "os movimentos ficam esquisitos", "#ff9de6"), "desc": "Desafia a interface e traz comportamento bugadinho."},
    "toxic": {"name": "Toxic", "rarity": "epic", "money_reward": 2100, "coin_reward": 2, "click_progress_reward": 2, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.02, "normal_push": 7, "panic_push": 27, "label_name": "TOXIC", "color": (150, 255, 90, 145), "event_on_click": ("sticky", 6, "Nuvem tóxica", "o botão fica meio grudento", "#c4ff9a"), "desc": "Espalha um debuff leve quando estoura."},
    "magnet": {"name": "Magnet", "rarity": "epic", "money_reward": 2600, "coin_reward": 3, "click_progress_reward": 2, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.02, "normal_push": 5, "panic_push": 24, "label_name": "MAGNET", "color": (255, 120, 120, 145), "event_on_click": ("center_pull", 7, "Center pull", "o botão tenta voltar ao centro", "#ffd166"), "desc": "Puxa o botão para o meio por alguns segundos."},
    "sleepy": {"name": "Sleepy", "rarity": "rare", "money_reward": 260, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 1, "size_multiplier": 1.08, "normal_push": 3, "panic_push": 15, "label_name": "SLEEPY", "color": (170, 170, 255, 130), "event_on_click": ("calm", 7, "Soneca", "o botão fica mais tranquilo", "#b8ffcf"), "desc": "Lento e sonolento. Acalma a partida."},
    "speedy": {"name": "Speedy", "rarity": "common", "money_reward": 340, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 3, "speed_max": 4, "size_multiplier": 0.88, "normal_push": 7, "panic_push": 26, "label_name": "SPEEDY", "color": (255, 255, 140, 135), "desc": "Corre muito e some rápido se você vacilar."},
    "royal": {"name": "Royal", "rarity": "legendary", "money_reward": 8000, "coin_reward": 7, "click_progress_reward": 5, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.18, "normal_push": 7, "panic_push": 28, "label_name": "ROYAL", "color": (255, 215, 90, 155), "essence_reward": 1, "desc": "Nobre, brilhante e muito recompensador."},
    "plasma": {"name": "Plasma", "rarity": "legendary", "money_reward": 5200, "coin_reward": 5, "click_progress_reward": 4, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.1, "normal_push": 9, "panic_push": 32, "label_name": "PLASMA", "color": (120, 255, 255, 155), "event_on_click": ("hyper_button", 7, "Hyper button", "o botão cresce e acelera", "#76d7ff"), "desc": "Energia pura. Explode em velocidade e brilho."},
    "stone": {"name": "Stone", "rarity": "common", "money_reward": 650, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 1, "size_multiplier": 1.18, "normal_push": 4, "panic_push": 16, "label_name": "STONE", "color": (180, 180, 180, 150), "desc": "Pesado, estável e fácil de prever."},
    "ghost": {"name": "Ghost", "rarity": "epic", "money_reward": 3000, "coin_reward": 3, "click_progress_reward": 2, "speed_min": 1, "speed_max": 3, "size_multiplier": 0.98, "normal_push": 6, "panic_push": 22, "label_name": "GHOST", "color": (230, 230, 255, 115), "event_on_click": ("blink", 6, "Fantasma", "o botão dá pulinhos curtos", "#c9b6ff"), "desc": "Fantasmagórico e imprevisível."},
    "lava": {"name": "Lava", "rarity": "legendary", "money_reward": 6000, "coin_reward": 5, "click_progress_reward": 4, "speed_min": 2, "speed_max": 2, "size_multiplier": 1.15, "normal_push": 9, "panic_push": 34, "label_name": "LAVA", "color": (255, 100, 60, 155), "event_on_click": ("heatwave", 7, "Heatwave", "o botão vibra e foge um pouco mais", "#ff9f43"), "desc": "Quente demais. Transforma a tela num mini caos."},
    "clockwork": {"name": "Clockwork", "rarity": "epic", "money_reward": 2800, "coin_reward": 3, "click_progress_reward": 2, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.0, "normal_push": 5, "panic_push": 22, "label_name": "CLOCK", "color": (240, 210, 140, 150), "event_on_click": ("time_dilation", 7, "Time dilation", "a movimentação muda de ritmo", "#ffd29f"), "desc": "Todo certinho. Mexe com o ritmo do jogo."},
    "neon": {"name": "Neon", "rarity": "rare", "money_reward": 2500, "coin_reward": 2, "click_progress_reward": 2, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.0, "normal_push": 7, "panic_push": 28, "label_name": "NEON", "color": (90, 255, 180, 150), "desc": "Brilha demais e é gostoso de acertar."},
    "pirate": {"name": "Pirate", "rarity": "legendary", "money_reward": 3600, "coin_reward": 4, "click_progress_reward": 3, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.08, "normal_push": 8, "panic_push": 30, "label_name": "PIRATE", "color": (210, 170, 110, 150), "event_on_click": ("treasure_tide", 8, "Treasure tide", "especialistas pagam mais por um tempo", "#ffd166"), "desc": "Chega com cheiro de loot e dinheiro fácil."},
    "angel": {"name": "Angel", "rarity": "mythic", "money_reward": 7000, "coin_reward": 5, "click_progress_reward": 4, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.12, "normal_push": 5, "panic_push": 18, "label_name": "ANGEL", "color": (255, 255, 220, 150), "essence_reward": 1, "event_on_click": ("blessing", 8, "Blessing", "mais click, mais auto e menos caos", "#fff4bf"), "desc": "Muito raro. Dá blessing e pode render essence."},
    "devil": {"name": "Devil", "rarity": "mythic", "money_reward": 7600, "coin_reward": 6, "click_progress_reward": 4, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.12, "normal_push": 10, "panic_push": 36, "label_name": "DEVIL", "color": (255, 90, 90, 150), "event_on_click": ("hellrush", 7, "Hellrush", "mais click e mais caos ao mesmo tempo", "#ff6b6b"), "desc": "Perigoso, valioso e caótico."},
    "moss": {"name": "Moss", "rarity": "common", "money_reward": 300, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 1, "size_multiplier": 1.0, "normal_push": 4, "panic_push": 18, "label_name": "MOSS", "color": (110, 180, 110, 140), "desc": "Calminho e natural. Um comum relaxante."},
    "prism": {"name": "Prism", "rarity": "mythic", "money_reward": 12000, "coin_reward": 8, "click_progress_reward": 5, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.22, "normal_push": 9, "panic_push": 30, "label_name": "PRISM", "color": (255, 200, 255, 150), "hits": 3, "essence_reward": 1, "desc": "Mítico. Precisa de 3 cliques e explode em loot."},
    "voidling": {"name": "Voidling", "rarity": "legendary", "money_reward": 9200, "coin_reward": 6, "click_progress_reward": 4, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.12, "normal_push": 9, "panic_push": 32, "label_name": "VOID", "color": (170, 120, 255, 150), "event_on_click": ("void_window", 7, "Void window", "mais raros e visual estranho", "#b48cff"), "desc": "Cria uma janela curta de raridade elevada."},
    "chef": {"name": "Chef", "rarity": "rare", "money_reward": 420, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.0, "normal_push": 5, "panic_push": 18, "label_name": "CHEF", "color": (255, 230, 180, 140), "event_on_click": ("snack_break", 6, "Snack break", "combo decai mais devagar", "#ffd29f"), "desc": "Serve uma pausa boa para combos."},
    "samurai": {"name": "Samurai", "rarity": "epic", "money_reward": 4700, "coin_reward": 4, "click_progress_reward": 3, "speed_min": 2, "speed_max": 3, "size_multiplier": 1.05, "normal_push": 8, "panic_push": 30, "label_name": "SAMURAI", "color": (220, 220, 220, 150), "desc": "Ágil, preciso e com ótimo retorno."},
    "arcade": {"name": "Arcade", "rarity": "epic", "money_reward": 2600, "coin_reward": 3, "click_progress_reward": 2, "speed_min": 2, "speed_max": 3, "size_multiplier": 0.96, "normal_push": 7, "panic_push": 24, "label_name": "ARCADE", "color": (120, 200, 255, 145), "event_on_click": ("jackpot_mode", 7, "Jackpot mode", "especialistas rendem mais moedas", "#76d7ff"), "desc": "Parece saído de um gabinete retrô."},
    "bubble": {"name": "Bubble", "rarity": "common", "money_reward": 380, "coin_reward": 1, "click_progress_reward": 1, "speed_min": 1, "speed_max": 2, "size_multiplier": 0.92, "normal_push": 4, "panic_push": 16, "label_name": "BUBBLE", "color": (180, 220, 255, 120), "desc": "Leve e saltitante, quase não empurra o botão."},
    "crown": {"name": "Crown", "rarity": "legendary", "money_reward": 9800, "coin_reward": 7, "click_progress_reward": 5, "speed_min": 1, "speed_max": 2, "size_multiplier": 1.18, "normal_push": 7, "panic_push": 26, "label_name": "CROWN", "color": (255, 220, 100, 155), "essence_reward": 1, "desc": "Realeza pura. Muito dinheiro, muitas moedas."},
    "fairy": {"name": "Fairy", "rarity": "legendary", "money_reward": 3600, "coin_reward": 3, "click_progress_reward": 3, "speed_min": 2, "speed_max": 4, "size_multiplier": 0.82, "normal_push": 5, "panic_push": 18, "label_name": "FAIRY", "color": (255, 180, 255, 145), "event_on_click": ("lucky_wave", 8, "Lucky wave", "a sorte dos raros sobe um pouco", "#ffb6ff"), "desc": "Pequenina, rápida e ajuda a puxar raros."},
}

EVENT_RARITY_INFO = {
    "common":    {"label": "Comum",     "color": "#d9d9d9", "weight": 5.0},
    "rare":      {"label": "Raro",      "color": "#76d7ff", "weight": 2.5},
    "epic":      {"label": "Épico",     "color": "#c792ea", "weight": 1.2},
    "legendary": {"label": "Lendário",  "color": "#ffcf66", "weight": 0.5},
    "mythic":    {"label": "Mítico",    "color": "#ff66ff", "weight": 0.15},
}

EVENT_INFO = {
    "double_click": {"good": True, "name": "2x click", "rarity": "rare", "desc": "Seus cliques valem o dobro por alguns segundos.", "duration": 8, "color": "#a5ff90", "click_mult": 2.0},
    "double_auto": {"good": True, "name": "2x auto", "rarity": "rare", "desc": "Seu auto click fica dobrado temporariamente.", "duration": 8, "color": "#9cf6ff", "auto_mult": 2.0},
    "big_button": {"good": True, "name": "Botão maior", "rarity": "common", "desc": "O botão fica maior e mais fácil de clicar.", "duration": 7, "color": "#fff199", "scale_mult": 1.22},
    "tiny_button": {"good": False, "name": "Botão menor", "rarity": "common", "desc": "O botão fica menor e mais difícil de clicar.", "duration": 6, "color": "#ffb3b3", "scale_mult": 0.78},
    "chaos": {"good": False, "name": "Caos", "rarity": "rare", "desc": "O botão se move bem mais do que o normal.", "duration": 7, "color": "#ff9f43", "move_mult": 1.35},
    "calm": {"good": True, "name": "Calmaria", "rarity": "common", "desc": "O botão se move menos por um tempo.", "duration": 7, "color": "#b8ffcf", "move_mult": 0.65},
    "invert_colors": {"good": False, "name": "Cores invertidas", "rarity": "epic", "desc": "A interface muda temporariamente para um visual invertido limpo.", "duration": 6, "color": "#fca5ff", "invert_colors": True},
    "invert_move": {"good": False, "name": "Inversão", "rarity": "rare", "desc": "O movimento do botão fica estranho e invertido, mas controlável.", "duration": 6, "color": "#c9b6ff", "invert_move": True},
    "gravity": {"good": False, "name": "Gravidade", "rarity": "rare", "desc": "O botão tende a cair para baixo.", "duration": 7, "color": "#8cb4ff", "gravity": True},
    "sticky": {"good": False, "name": "Grudento", "rarity": "common", "desc": "O botão quase não se move.", "duration": 6, "color": "#c4ff9a", "move_mult": 0.35},
    "frenzy": {"good": True, "name": "Frenesi", "rarity": "epic", "desc": "Mais goobers podem surgir durante o evento.", "duration": 8, "color": "#ffda7a", "spawn_bonus": 4},
    "mouse_flee": {"name": "Fujão", "rarity": "legendary", "desc": "O botão tenta fugir do mouse.", "duration": 7, "color": "#ff8cc6", "mouse_flee": True},
    "blink": {"name": "Pisca-pisca", "rarity": "legendary", "desc": "O botão teleporta de leve quando você chega perto.", "duration": 6, "color": "#9fb8ff", "blink": True},
    "storm_mode": {"good": False, "name": "Storm mode", "rarity": "epic", "desc": "Vento e gravidade bagunçam o botão ao mesmo tempo.", "duration": 7, "color": "#9fb8ff", "move_mult": 1.25, "gravity": True},
    "glitch_flip": {"good": False, "name": "Glitch flip", "rarity": "epic", "desc": "O botão alterna movimentos esquisitos, mas sem quebrar o controle.", "duration": 6, "color": "#ff9de6", "invert_move": True, "blink": True},
    "center_pull": {"name": "Center pull", "rarity": "rare", "desc": "O botão tenta voltar ao centro da tela.", "duration": 7, "color": "#ffd166", "center_pull": True},
    "hyper_button": {"name": "Hyper button", "rarity": "epic", "desc": "O botão cresce e ganha energia.", "duration": 7, "color": "#76d7ff", "scale_mult": 1.18, "move_mult": 1.12},
    "heatwave": {"good": False, "name": "Heatwave", "rarity": "epic", "desc": "A tela entra num calor caótico com o botão mais arisco.", "duration": 7, "color": "#ff9f43", "move_mult": 1.45, "mouse_flee": True},
    "time_dilation": {"good": True, "name": "Time dilation", "rarity": "rare", "desc": "A movimentação desacelera, mas o auto acelera um pouco.", "duration": 7, "color": "#ffd29f", "move_mult": 0.75, "auto_mult": 1.25},
    "treasure_tide": {"good": True, "name": "Treasure tide", "rarity": "epic", "desc": "Goobers especiais rendem mais dinheiro e moedas.", "duration": 8, "color": "#ffd166", "special_money_mult": 1.5, "special_coin_bonus": 2},
    "blessing": {"good": True, "name": "Blessing", "rarity": "legendary", "desc": "Um evento muito bom: mais click, mais auto e menos caos.", "duration": 8, "color": "#fff4bf", "click_mult": 1.6, "auto_mult": 1.6, "move_mult": 0.7, "special_essence_bonus": 1},
    "hellrush": {"good": False, "name": "Hellrush", "rarity": "legendary", "desc": "Poder e caos ao mesmo tempo.", "duration": 7, "color": "#ff6b6b", "click_mult": 1.5, "move_mult": 1.55, "spawn_bonus": 2},
    "void_window": {"good": False, "name": "Void window", "rarity": "legendary", "desc": "A janela do vazio aumenta a chance de raros e RGB.", "duration": 7, "color": "#b48cff", "rare_bonus": 0.01, "invert_colors": True},
    "snack_break": {"good": True, "name": "Snack break", "rarity": "common", "desc": "Seu combo demora mais para cair.", "duration": 6, "color": "#ffd29f", "combo_grace": 900},
    "jackpot_mode": {"good": True, "name": "Jackpot mode", "rarity": "epic", "desc": "Especialistas rendem muito mais goober coins.", "duration": 7, "color": "#76d7ff", "special_coin_bonus": 3},
    "lucky_wave": {"good": True, "name": "Lucky wave", "rarity": "epic", "desc": "Uma onda de sorte melhora bastante os spawns especiais.", "duration": 8, "color": "#ffb6ff", "rare_bonus": 0.008},
    "coin_rain": {"good": True, "name": "Coin rain", "rarity": "rare", "desc": "Cada clique gera uma goober coin extra por um tempo.", "duration": 7, "color": "#ffe082", "click_coin_bonus": 1},
    "essence_bloom": {"good": True, "name": "Essence bloom", "rarity": "legendary", "desc": "Goobers especiais podem render essence extra.", "duration": 8, "color": "#ff9de6", "special_essence_bonus": 1},
    "boss_hour": {"name": "Boss hour", "rarity": "epic", "desc": "A chance de boss sobe durante o evento.", "duration": 8, "color": "#ffcf66", "boss_bonus": 0.05},
    "moonlight": {"good": True, "name": "Moonlight", "rarity": "common", "desc": "Tudo fica mais suave e previsível.", "duration": 7, "color": "#d8e6ff", "move_mult": 0.55, "rare_bonus": 0.002},
    "mirror_world": {"good": False, "name": "Mirror world", "rarity": "epic", "desc": "Visual invertido com movimento espelhado, mas estável.", "duration": 6, "color": "#dcb5ff", "invert_colors": True, "invert_move": True},
    "safe_zone": {"good": True, "name": "Safe zone", "rarity": "rare", "desc": "Os empurrões dos goobers ficam mais fracos.", "duration": 7, "color": "#b8ffcf", "panic_reduce": 8, "move_mult": 0.8},
    "orbital": {"name": "Orbital", "rarity": "epic", "desc": "O botão fica orbitando suavemente em torno do centro.", "duration": 7, "color": "#9fd8ff", "orbit": True},
    "overclock": {"good": True, "name": "Overclock", "rarity": "epic", "desc": "Auto click e spawn de goobers sobem juntos.", "duration": 8, "color": "#8cecff", "auto_mult": 1.8, "spawn_bonus": 3},
    "party_mode": {"good": True, "name": "Party mode", "rarity": "rare", "desc": "Mais especiais e mais moedas por clique em clima de festa.", "duration": 8, "color": "#ffb6d9", "rare_bonus": 0.004, "click_coin_bonus": 1, "special_coin_bonus": 1}
}

UI_THEMES = {
    "default": {
        "name": "Default", "cost": 0,
        "bg": "#20242b", "panel": "rgba(255,255,255,18)", "text": "#f3f5f7",
        "accent": "#8bd3ff", "accent2": "#ffd166",
        "button_style": """
            QPushButton {
                background: rgba(255,255,255,18); border: 1px solid #8bd3ff;
                border-radius: 12px; color: #f3f5f7; font-weight: bold; padding: 6px;
            }
            QPushButton:hover { background: rgba(255,255,255,28); border-color: #ffd166; }
        """,
        "inverted": {"bg": "#181c24", "panel": "rgba(139,211,255,18)", "text": "#c8dce8",
                     "accent": "#4a9fc9", "accent2": "#c49a3e"},
    },
    "gold": {
        "name": "Gold", "cost": 12,
        "bg": "#2f2712", "panel": "rgba(255,215,100,28)", "text": "#fff6d8",
        "accent": "#ffd700", "accent2": "#ffef99",
        "button_style": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #fff3a0, stop:1 #d4a017);
                border: 2px solid #7a5b00; border-radius: 12px; color: #2b1d00; font-weight: bold; padding: 6px;
            }
        """,
        "inverted": {"bg": "#1f1a10", "panel": "rgba(255,215,100,20)", "text": "#e8dbb0",
                     "accent": "#b8960e", "accent2": "#7a5b00"},
    },
    "ice": {
        "name": "Ice", "cost": 10,
        "bg": "#14222b", "panel": "rgba(150,240,255,24)", "text": "#eaffff",
        "accent": "#8cecff", "accent2": "#d8f8ff",
        "button_style": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #d8f7ff, stop:1 #84d8ff);
                border: 2px solid #2d7ea6; border-radius: 12px; color: #113344; font-weight: bold; padding: 6px;
            }
        """,
        "inverted": {"bg": "#0f1f26", "panel": "rgba(140,236,255,20)", "text": "#b8dee8",
                     "accent": "#3a9ebe", "accent2": "#6abfdf"},
    },
    "void": {
        "name": "Void", "cost": 18,
        "bg": "#120f18", "panel": "rgba(160,100,255,24)", "text": "#f5e9ff",
        "accent": "#b48cff", "accent2": "#ff9de6",
        "button_style": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2b2035, stop:1 #0d0911);
                border: 2px solid #a66cff; border-radius: 12px; color: #f5e9ff; font-weight: bold; padding: 6px;
            }
        """,
        "inverted": {"bg": "#18121f", "panel": "rgba(160,100,255,20)", "text": "#dcc8f0",
                     "accent": "#9a6fdf", "accent2": "#df6fcf"},
    },
    "candy": {
        "name": "Candy", "cost": 14,
        "bg": "#2b1621", "panel": "rgba(255,160,210,24)", "text": "#fff0f8",
        "accent": "#ff9ccc", "accent2": "#ffd3ea",
        "button_style": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffb6d9, stop:1 #ff86b5);
                border: 2px solid #cc4e8e; border-radius: 12px; color: #5c1033; font-weight: bold; padding: 6px;
            }
        """,
        "inverted": {"bg": "#1f1219", "panel": "rgba(255,160,210,20)", "text": "#e8c8d8",
                     "accent": "#df6fa6", "accent2": "#ff86b5"},
    },
    "matrix": {
        "name": "Matrix", "cost": 20,
        "bg": "#081108", "panel": "rgba(70,255,120,20)", "text": "#d9ffe0",
        "accent": "#6bff82", "accent2": "#9effaa",
        "button_style": """
            QPushButton {
                background: #0f1f12; border: 2px solid #57ff7d;
                border-radius: 12px; color: #c9ffd4; font-weight: bold; padding: 6px;
            }
            QPushButton:hover { background: #143019; }
        """,
        "inverted": {"bg": "#0a140d", "panel": "rgba(70,255,120,20)", "text": "#b0d9b8",
                     "accent": "#2faf50", "accent2": "#57ff7d"},
    },
    "sunset": {
        "name": "Sunset", "cost": 16,
        "bg": "#2c1522", "panel": "rgba(255,140,90,22)", "text": "#fff2e8",
        "accent": "#ff9f6e", "accent2": "#ffd29f",
        "button_style": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffcf99, stop:1 #ff8b73);
                border: 2px solid #b84c37; border-radius: 12px; color: #402114; font-weight: bold; padding: 6px;
            }
        """,
        "inverted": {"bg": "#221014", "panel": "rgba(255,140,90,20)", "text": "#e0c8b8",
                     "accent": "#df7f50", "accent2": "#b84c37"},
    },
}

PRESTIGE_MILESTONES = [
    (1,  "Starter boost",  "Missões sobem para 4 slots."),
    (3,  "Chaos tuning",   "Eventos bons ganham mais peso."),
    (5,  "Lucky archive",  "Chance extra de raro."),
    (8,  "Collectionist",  "Bônus de coleção ficam mais fortes."),
    (10, "Endgame prep",   "Ganhos offline e bosses melhoram."),
]

PERK_DEFS = [
    {"key": "economy_click",  "name": "Economy Click",  "desc": "+5% clique por nível",     "base_cost": 1, "max_level": 10},
    {"key": "economy_auto",   "name": "Economy Auto",   "desc": "+5% auto por nível",       "base_cost": 1, "max_level": 10},
    {"key": "goober_luck",    "name": "Goober Luck",    "desc": "Aumenta raros e capacidade", "base_cost": 2,"max_level": 5},
    {"key": "boss_hunter",    "name": "Boss Hunter",    "desc": "+1% boss, +HP e loot",     "base_cost": 2, "max_level": 5},
    {"key": "good_events",    "name": "Good Events",    "desc": "+7% duração bons eventos",  "base_cost": 1, "max_level": 8},
    {"key": "bad_events",     "name": "Bad Events",     "desc": "-6% duração maus eventos",  "base_cost": 1, "max_level": 8},
    {"key": "essence_boost",  "name": "Essence Boost",  "desc": "Melhora drops de essence",  "base_cost": 3, "max_level": 3},
]

ACHIEVEMENT_DEFS = [
    ("first_click",   "Primeiro passo",      "Faça 1 clique e dê início ao caos.",        lambda s: s.stats["total_clicks"] >= 1),
    ("hundred_clicks","Clicadora nata",       "Faça 100 cliques.",                         lambda s: s.stats["total_clicks"] >= 100),
    ("money_10k",     "Dinheiruda",           "Ganhe $10K no total.",                      lambda s: s.stats["money_earned"] >= 10000),
    ("money_1m",      "Economia paralela",    "Ganhe $1M ao longo das runs.",              lambda s: s.stats["money_earned"] >= 1_000_000),
    ("normal_25",     "Amiga dos goobers",    "Clique 25 goobers normais.",                lambda s: s.stats.get("normal_clicked", 0) >= 25),
    ("gold_3",        "Caça-ouro",            "Clique 3 goobers gold.",                    lambda s: s.stats.get("gold_clicked", 0) >= 3),
    ("rgb_1",         "Lenda RGB",            "Derrote 1 goober RGB.",                     lambda s: s.stats.get("rgb_defeated", 0) >= 1),
    ("boss_1",        "Boss hunter",          "Derrote 1 boss.",                           lambda s: s.stats.get("boss_defeated", 0) >= 1),
    ("boss_5",        "Predadora de chefes",  "Derrote 5 bosses.",                         lambda s: s.stats.get("boss_defeated", 0) >= 5),
    ("combo_25",      "Flow state",           "Chegue a combo x25.",                       lambda s: s.stats.get("highest_combo", 0) >= 25),
    ("combo_75",      "Mão impossível",       "Chegue a combo x75.",                       lambda s: s.stats.get("highest_combo", 0) >= 75),
    ("missions_10",   "Trabalhadora do mês",  "Complete 10 missões.",                      lambda s: s.mission_state.get("completed_total", 0) >= 10),
    ("missions_30",   "Painel limpo",         "Complete 30 missões.",                      lambda s: s.mission_state.get("completed_total", 0) >= 30),
    ("collector_20",  "Arquivo vivo",         "Veja 20 tipos diferentes de goober.",       lambda s: _collection_unique_seen(s) >= 20),
    ("hands_on_15",   "Mão certeira",         "Clique em 15 tipos diferentes de goober.",  lambda s: _collection_unique_clicked(s) >= 15),
    ("essence_25",    "Cheiro de meta",       "Junte 25 poopy essence.",                   lambda s: s.poopy_essence >= 25),
    ("prestige_1",    "Essência poopy",       "Faça 1 prestígio.",                         lambda s: s.prestige_level >= 1),
    ("prestige_5",    "Recomeço afiado",      "Chegue ao prestígio 5.",                    lambda s: s.prestige_level >= 5),
    ("goober_40",     "Segredo revelado",     "Desbloqueie a loja goobers.",               lambda s: s.secret_shop_unlocked),
    # --- 35 novos achievements ---
    ("clicks_1k",     "Dedos ágeis",          "Faça 1.000 cliques.",                        lambda s: s.stats["total_clicks"] >= 1000),
    ("clicks_10k",    "Mão turbinada",        "Faça 10.000 cliques.",                       lambda s: s.stats["total_clicks"] >= 10000),
    ("clicks_100k",   "Clicadora implacável", "Faça 100.000 cliques.",                      lambda s: s.stats["total_clicks"] >= 100_000),
    ("clicks_1m",     "Lenda dos cliques",    "Faça 1.000.000 de cliques.",                  lambda s: s.stats["total_clicks"] >= 1_000_000),
    ("money_10m",     "Milhonária",           "Ganhe $10M no total.",                       lambda s: s.stats["money_earned"] >= 10_000_000),
    ("money_1b",      "Bilionária",           "Ganhe $1B no total.",                        lambda s: s.stats["money_earned"] >= 1_000_000_000),
    ("money_1t",      "Trilhonária",          "Ganhe $1T no total.",                        lambda s: s.stats["money_earned"] >= 1_000_000_000_000),
    ("angry_5",       "Rivais",               "Clique 5 angry goobers.",                    lambda s: s.stats.get("angry_clicked", 0) >= 5),
    ("tiny_5",        "Pequenina",            "Clique 5 tiny goobers.",                     lambda s: s.stats.get("tiny_clicked", 0) >= 5),
    ("giant_5",       "Gigantona",            "Clique 5 giant goobers.",                    lambda s: s.stats.get("giant_clicked", 0) >= 5),
    ("frozen_5",      "Coração gelado",       "Clique 5 frozen goobers.",                   lambda s: s.stats.get("frozen_clicked", 0) >= 5),
    ("bomb_5",        "Desarmadora",          "Clique 5 bomb goobers.",                     lambda s: s.stats.get("bomb_clicked", 0) >= 5),
    ("boss_10",       "Caça-troféus",         "Derrote 10 bosses.",                         lambda s: s.stats.get("boss_defeated", 0) >= 10),
    ("boss_25",       "Exterminadora",        "Derrote 25 bosses.",                         lambda s: s.stats.get("boss_defeated", 0) >= 25),
    ("boss_50",       "Lenda dos bosses",     "Derrote 50 bosses.",                         lambda s: s.stats.get("boss_defeated", 0) >= 50),
    ("rgb_5",         "Arco-íris mortal",     "Derrote 5 RGB goobers.",                     lambda s: s.stats.get("rgb_defeated", 0) >= 5),
    ("rgb_10",        "Prisma destruído",     "Derrote 10 RGB goobers.",                    lambda s: s.stats.get("rgb_defeated", 0) >= 10),
    ("combo_150",     "Incontrolável",        "Chegue a combo x150.",                       lambda s: s.stats.get("highest_combo", 0) >= 150),
    ("combo_300",     "Deusa do ritmo",       "Chegue a combo x300.",                       lambda s: s.stats.get("highest_combo", 0) >= 300),
    ("missions_50",   "Meta cumprida",        "Complete 50 missões.",                       lambda s: s.mission_state.get("completed_total", 0) >= 50),
    ("missions_100",  "Missões infinitas",    "Complete 100 missões.",                      lambda s: s.mission_state.get("completed_total", 0) >= 100),
    ("collector_30",  "Arquivo completo",     "Veja 30 tipos de goober.",                   lambda s: _collection_unique_seen(s) >= 30),
    ("collector_all", "Enciclopédia viva",    "Veja todos os 38 tipos de goober.",          lambda s: _collection_unique_seen(s) >= 38),
    ("hands_on_25",   "Mão de vaca",          "Clique em 25 tipos.",                        lambda s: _collection_unique_clicked(s) >= 25),
    ("prestige_10",   "Renascida",            "Chegue ao prestígio 10.",                    lambda s: s.prestige_level >= 10),
    ("prestige_25",   "Fênix",                "Chegue ao prestígio 25.",                    lambda s: s.prestige_level >= 25),
    ("prestige_50",   "Imortal",              "Chegue ao prestígio 50.",                    lambda s: s.prestige_level >= 50),
    ("upgrade_50",    "Upgradeira",           "Tenha um upgrade no nível 50.",              lambda s: s.upgrade_level >= 50 or s.auto_level >= 50),
    ("upgrade_100",   "Upgrade supremo",      "Tenha um upgrade no nível 100.",             lambda s: s.upgrade_level >= 100 or s.auto_level >= 100),
    ("perk_max",      "Mestre das perks",     "Tenha uma perk no nível máximo.",            lambda s: any(v >= p["max_level"] for p in PERK_DEFS for k, v in s.perks.items() if k == p["key"])),
    ("shop_all",      "Colecionadora GC",     "Compre todos os itens da loja.",             lambda s: all(getattr(s, item["attr"]) for item in [
        {"attr": "goober_charm_bought"}, {"attr": "heavy_button_bought"}, {"attr": "lucky_paws_bought"},
        {"attr": "sneaky_profit_bought"}, {"attr": "panic_shield_bought"}, {"attr": "boss_beacon_bought"},
        {"attr": "essence_magnet_bought"}, {"attr": "mission_radar_bought"},
        {"attr": "cleanse_bought"}, {"attr": "frenzy_bought"}, {"attr": "skill_shield_bought"}, {"attr": "coinburst_bought"},
    ])),
    ("events_25",     "Eventeira",            "Presencie 25 eventos.",                      lambda s: s.stats.get("events_seen", 0) >= 25),
    ("events_100",    "Caos programado",      "Presencie 100 eventos.",                     lambda s: s.stats.get("events_seen", 0) >= 100),
    ("sound_off",     "Silêncio",             "Desligue o som nas configurações.",          lambda s: not s.settings.get("sound_enabled", True)),
    ("offline_10h",   "Dorminhoca",           "Acumule 10 horas offline no total.",         lambda s: s.stats.get("offline_seconds", 0) >= 36000),
]

COLLECTION_REWARDS = [
    {"id": "special_seen",    "name": "Colecionadora",   "req": lambda s: all(s.bestiary_counts.get(t,{}).get("seen",0) > 0 for t in ["gold","angry","tiny","giant","frozen","bomb","rgb","boss"]),
     "desc": "Veja todos os especiais básicos", "money_bonus": 0.04, "luck_bonus": 0.002},
    {"id": "special_clicked", "name": "Mão firme",      "req": lambda s: all(s.bestiary_counts.get(t,{}).get("clicked",0) > 0 for t in ["gold","angry","tiny","giant","frozen","bomb","rgb","boss"]),
     "desc": "Clique em todos os especiais básicos", "money_bonus": 0.06, "luck_bonus": 0.003},
    {"id": "boss_master",     "name": "Mestre dos Boss","req": lambda s: s.stats.get("boss_defeated",0) >= 5,
     "desc": "Derrote 5 bosses", "money_bonus": 0.10, "luck_bonus": 0.004},
    {"id": "collector_20",    "name": "Arquivo Vivo",   "req": lambda s: _collection_unique_seen(s) >= 20,
     "desc": "Veja 20 tipos", "money_bonus": 0.05, "luck_bonus": 0.002},
    {"id": "hands_on_15",     "name": "Mão Certeira",   "req": lambda s: _collection_unique_clicked(s) >= 15,
     "desc": "Clique em 15 tipos", "money_bonus": 0.07, "luck_bonus": 0.003},
    {"id": "endgame",         "name": "Endgame",        "req": lambda s: s.stats.get("boss_defeated",0) >= 10 and s.stats.get("rgb_defeated",0) >= 3 and s.prestige_level >= 3,
     "desc": "10 bosses, 3 RGB, prestígio 3", "money_bonus": 0.12, "luck_bonus": 0.005},
    {"id": "collector_30",    "name": "Bestiário Vivo", "req": lambda s: _collection_unique_seen(s) >= 30,
     "desc": "Veja 30 tipos", "money_bonus": 0.08, "luck_bonus": 0.004},
    {"id": "hands_on_25",     "name": "Mão de Mestre",  "req": lambda s: _collection_unique_clicked(s) >= 25,
     "desc": "Clique em 25 tipos", "money_bonus": 0.10, "luck_bonus": 0.005},
    {"id": "boss_25",         "name": "Caça Maior",     "req": lambda s: s.stats.get("boss_defeated",0) >= 25,
     "desc": "Derrote 25 bosses", "money_bonus": 0.15, "luck_bonus": 0.006},
    {"id": "prestige_10",     "name": "Transcendente",  "req": lambda s: s.prestige_level >= 10,
     "desc": "Prestígio 10+", "money_bonus": 0.10, "luck_bonus": 0.003},
    {"id": "upgrade_master",  "name": "Upgrade Total",  "req": lambda s: s.upgrade_level >= 50 and s.auto_level >= 50,
     "desc": "Click e auto level 50", "money_bonus": 0.15, "luck_bonus": 0.005},
]

SYNERGY_BONUSES = [
    {"id": "defense",    "name": "Muralha",       "req": lambda s: s.heavy_button_bought and s.panic_shield_bought,
     "desc": "Heavy Button + Panic Shield: empurrão reduzido em mais 50%", "click_mult": 0, "auto_mult": 0, "push_reduce": 0.5},
    {"id": "wealth",     "name": "Império",       "req": lambda s: s.sneaky_profit_bought and s.lucky_paws_bought,
     "desc": "Sneaky Profit + Lucky Paws: +15% dinheiro de goobers", "click_mult": 0, "auto_mult": 0, "goober_money": 0.15},
    {"id": "hunting",    "name": "Caçadora",      "req": lambda s: s.boss_beacon_bought and s.essence_magnet_bought,
     "desc": "Boss Beacon + Essence Magnet: bosses dropam 2x essence", "click_mult": 0, "auto_mult": 0, "boss_essence": 2.0},
    {"id": "radar",      "name": "Visão Total",   "req": lambda s: s.mission_radar_bought and s.goober_charm_bought,
     "desc": "Mission Radar + Goober Charm: missões rendem +1 moeda e +5% dinheiro", "click_mult": 0, "auto_mult": 0, "mission_money": 0.05, "mission_coins": 1},
    {"id": "click_master","name": "Clique Supremo","req": lambda s: s.upgrade_level >= 100 and s.auto_level >= 100,
     "desc": "Click e auto level 100: +25% clique e auto", "click_mult": 0.25, "auto_mult": 0.25, "push_reduce": 0},
    {"id": "economy",     "name": "Economia Total","req": lambda s: s.perks.get("economy_click", 0) >= 10 and s.perks.get("economy_auto", 0) >= 10,
     "desc": "Economy perks no máximo: +20% clique e auto", "click_mult": 0.20, "auto_mult": 0.20, "push_reduce": 0},
]

ACTIVE_SKILLS = [
    {"key": "cleanse",     "name": "🧹 Limpeza",      "cooldown": 60,  "desc": "Destrói todos os goobers na tela e ganha o dinheiro deles"},
    {"key": "frenzy",      "name": "⚡ Frenesi",       "cooldown": 90,  "desc": "Dobra ganhos de clique por 8s"},
    {"key": "skill_shield","name": "🛡️ Escudo",       "cooldown": 75,  "desc": "Evento atual é cancelado e novos bloqueados por 10s"},
    {"key": "coinburst",   "name": "💰 Explosão",     "cooldown": 120, "desc": "Goobers dropam 3x moedas por 12s"},
]

DEFAULT_SETTINGS = {
    "show_floating_text": True,
    "show_particles": True,
    "animate_goobers": True,
    "reduced_motion": False,
    "low_power_mode": False,
    "offline_progress": True,
    "ui_scale": "normal",
    "onboarding_done": False,
    "sound_enabled": True,
    "music_enabled": True,
    "sfx_volume": 0.7,
    "music_volume": 0.5,
    "selected_music_track": "",
}

DEFAULT_PERKS = {
    "economy_click": 0, "economy_auto": 0, "goober_luck": 0,
    "boss_hunter": 0, "good_events": 0, "bad_events": 0, "essence_boost": 0,
}

def _collection_unique_seen(state):
    return sum(1 for v in state.bestiary_counts.values() if v.get("seen", 0) > 0)

def _collection_unique_clicked(state):
    return sum(1 for v in state.bestiary_counts.values() if v.get("clicked", 0) > 0)

def format_number(n):
    suffixes = ["", "K", "M", "B", "T", "Q", "Qi", "Sx", "Sp", "Oc", "No", "Dc"]
    i = 0
    n = float(n)
    while n >= 1000 and i < len(suffixes) - 1:
        n /= 1000
        i += 1
    text = f"{n:.1f}".rstrip("0").rstrip(".")
    if text.replace(".", "").replace("-", "").isdigit() and float(text) >= 1000 and i < len(suffixes) - 1:
        text = f"{float(text) / 1000:.1f}".rstrip("0").rstrip(".")
        i += 1
    if i == 0:
        return str(int(n))
    return f"{text}{suffixes[i]}"
