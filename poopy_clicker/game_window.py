import os
import sys
import random
import time
import math
import json
import webbrowser
from collections import deque
from urllib.request import urlopen, Request
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QDialog, QProgressBar,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QTabWidget, QCheckBox, QFrame, QSlider,
)
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont, QCursor, QPixmap, QGuiApplication, QPainter, QColor, QLinearGradient

from .constants import (
    ASSET_PATH, format_number, MAX_GOOBERS, CLICK_SPAWN_THRESHOLD,
    PASSIVE_SPAWN_INTERVAL_MS, EVENT_CHECK_INTERVAL_MS,
    EVENT_TRIGGER_CHANCE, SECRET_SHOP_UNLOCK_CLICKS,
    BOSS_SPAWN_CHANCE, GOOBER_INFO,
    RARITY_INFO, EXTRA_GOOBER_DATA, EVENT_INFO, EVENT_RARITY_INFO,
    COLLECTION_REWARDS, _collection_unique_seen,
    _collection_unique_clicked, UI_THEMES, PERK_DEFS,
    AUTO_SAVE_INTERVAL_MS, RARITY_SPAWN_WEIGHT,
    ACTIVE_SKILLS, VERSION, REPO,
)
from .game_state import GameState, ACHIEVEMENT_DEFS
from .play_area import PlayArea
from .goober import Goober
from .events import EventBubble
from .missions import MissionCard

from .particles import burst
from . import save_load
from .sound_manager import SoundManager

SKILL_PURCHASE_ATTRS = {
    "cleanse": "cleanse_bought",
    "frenzy": "frenzy_bought",
    "skill_shield": "skill_shield_bought",
    "coinburst": "coinburst_bought",
}

def _dialog_size(w_pct, h_pct):
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return (480, 420)
    geo = screen.availableGeometry()
    return (int(geo.width() * w_pct / 100), int(geo.height() * h_pct / 100))

SHOP_ITEM_DEFS = [
    {"key": "charm",  "name": "Goober Charm",  "cost": 8,  "desc": "Goobers param para descansar com metade da frequência",      "attr": "goober_charm_bought"},
    {"key": "heavy",  "name": "Heavy Button",  "cost": 12, "desc": "Reduz a força do empurrão normal de 6x para 3x",               "attr": "heavy_button_bought"},
    {"key": "paws",   "name": "Lucky Paws",    "cost": 15, "desc": "Ganha +1 moeda extra por clique em Goober",                    "attr": "lucky_paws_bought"},
    {"key": "profit", "name": "Sneaky Profit", "cost": 20, "desc": "Aumenta o auto click em 25%",                                 "attr": "sneaky_profit_bought"},
    {"key": "shield", "name": "Panic Shield",  "cost": 18, "desc": "Reduz a força do empurrão de pânico de 28x para 18x",          "attr": "panic_shield_bought"},
    {"key": "beacon", "name": "Boss Beacon",   "cost": 25, "desc": "+3% chance de spawnar boss",                                  "attr": "boss_beacon_bought"},
    {"key": "magnet", "name": "Essence Magnet","cost": 22, "desc": "18% chance de essence extra em goobers especiais",              "attr": "essence_magnet_bought"},
    {"key": "radar",  "name": "Mission Radar", "cost": 18, "desc": "Missões dão 1.2x mais dinheiro e +1 moeda",                   "attr": "mission_radar_bought"},
    {"key": "skill_cleanse",    "name": "🧹 Limpeza",    "cost": 30, "desc": "Habilidade: destrói todos os goobers na tela (60s cooldown)",     "attr": "cleanse_bought"},
    {"key": "skill_frenzy",     "name": "⚡ Frenesi",     "cost": 40, "desc": "Habilidade: 2x clique por 8s (90s cooldown)",                    "attr": "frenzy_bought"},
    {"key": "skill_shield",     "name": "🛡️ Escudo",     "cost": 35, "desc": "Habilidade: bloqueia eventos por 10s (75s cooldown)",             "attr": "skill_shield_bought"},
    {"key": "skill_coinburst",  "name": "💰 Explosão",   "cost": 50, "desc": "Habilidade: 3x moedas por 12s (120s cooldown)",                   "attr": "coinburst_bought"},
]


class Game(QWidget):
    def __init__(self):
        super().__init__()

        self.state = GameState()
        self.sound = SoundManager(ASSET_PATH)
        self.sound.load_all()
        self.upgrade_btn = None
        self.auto_btn = None
        self._goober_tab_info_label = None
        self._goober_tab_desc_label = None
        self.secret_buttons = {}
        self.secret_upgrade_items = []
        self.theme_shop_buttons = {}
        self.achievement_btn = None
        self.goobers = []
        self.click_spawn_counter = 0
        self.boss_active = False
        self.active_event = None
        self.event_end_time = 0
        self.event_total_duration = 0
        self.event_title = ""
        self.event_desc = ""
        self.event_color = "#8bd3ff"
        self.event_timer = QTimer(self)
        self.event_timer.timeout.connect(self.update_event_state)
        self.event_timer.start(260)
        self.random_event_timer = QTimer(self)
        self.random_event_timer.timeout.connect(self.try_random_event)
        self.random_event_timer.start(EVENT_CHECK_INTERVAL_MS)
        self._orbit_angle = 0.0
        self.combo_decay_timer = QTimer(self)
        self.combo_decay_timer.setSingleShot(True)
        self.combo_decay_timer.timeout.connect(self.reset_combo)

        self.setWindowTitle("poopy clicker")
        self.resize(*_dialog_size(64, 70))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        label_font = QFont()
        label_font.setPointSize(14)

        button_font = QFont()
        button_font.setPointSize(11)

        money_font = QFont()
        money_font.setPointSize(22)
        money_font.setBold(True)

        chip_font = QFont()
        chip_font.setPointSize(10)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(money_font)
        main_layout.addWidget(self.label)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(12)

        self.auto_label = QLabel()
        self.auto_label.setFont(chip_font)
        chip_row.addWidget(self.auto_label)

        self.combo_label = QLabel()
        self.combo_label.setFont(chip_font)
        chip_row.addWidget(self.combo_label)

        self.essence_label = QLabel()
        self.essence_label.setFont(chip_font)
        chip_row.addWidget(self.essence_label)

        self.prestige_label = QLabel()
        self.prestige_label.setFont(chip_font)
        chip_row.addWidget(self.prestige_label)

        self.goober_label = QLabel()
        self.goober_label.setFont(chip_font)
        chip_row.addWidget(self.goober_label)

        self.mission_label = QLabel()
        self.mission_label.setFont(chip_font)
        chip_row.addWidget(self.mission_label)

        chip_row.addStretch()
        main_layout.addLayout(chip_row)

        skill_row = QHBoxLayout()
        skill_row.setSpacing(6)
        self.skill_buttons = {}
        small_font = QFont(); small_font.setPointSize(9)
        for sk in ACTIVE_SKILLS:
            btn = QPushButton(f"{sk['name']}")
            btn.setFont(small_font)
            btn.setFixedHeight(30)
            btn.setToolTip(sk["desc"])
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda checked, k=sk["key"]: self._use_skill(k))
            skill_row.addWidget(btn)
            self.skill_buttons[sk["key"]] = btn
        skill_row.addStretch()
        main_layout.addLayout(skill_row)

        self._skill_timer = QTimer(self)
        self._skill_timer.timeout.connect(self._tick_skill_cooldowns)
        self._skill_timer.start(1000)

        self.play_area = PlayArea(self)
        main_layout.addWidget(self.play_area, 1)

        self.event_bubble = EventBubble(self.play_area)
        self.event_bubble.setFixedWidth(220)
        self.event_bubble.move(14, 14)

        self.click_btn = QPushButton("click", self.play_area)
        self.click_btn.setToolTip("Clique para ganhar dinheiro! Cada clique ativa o combo e pode spawnar goobers.")
        self._btn_original_size = (110, 48)
        self.click_btn.resize(*self._btn_original_size)
        self.click_btn.setFont(button_font)
        self.click_btn.clicked.connect(self.click)
        self.click_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)
        nav_row.addStretch()

        menu_btn = QPushButton("📋 Menu")
        menu_btn.setMinimumSize(80, 42)
        nf = QFont(); nf.setPointSize(11)
        menu_btn.setFont(nf)
        menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        menu_btn.clicked.connect(self.open_menu)
        nav_row.addWidget(menu_btn)

        nav_row.addStretch()
        main_layout.addLayout(nav_row)

        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_loop)
        self.timer.start(1000)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.try_spawn_goober)
        self.spawn_timer.start(PASSIVE_SPAWN_INTERVAL_MS)

        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.save)
        self.autosave_timer.start(AUTO_SAVE_INTERVAL_MS)

        self._click_tick = 0
        self._last_click_tick = -1
        self._last_clicks = deque()
        self._orig_stylesheets = {}
        self._skill_frenzy_active = False
        self._skill_shield_active = False
        self._skill_coinburst_active = False
        self.recenter_timer = QTimer()
        self.recenter_timer.timeout.connect(self._check_recenter)
        self.recenter_timer.start(20000)

        self.refresh_all()
        QTimer.singleShot(0, self.center_click_button)
        QTimer.singleShot(0, self.load)
        QTimer.singleShot(200, lambda: [self.try_spawn_goober() for _ in range(2)])
        QTimer.singleShot(100, self.apply_ui_theme)
        QTimer.singleShot(3000, self._check_updates)

    def _apply_theme_dict(self, theme, widget=None):
        target = widget or self
        bg = theme['bg']
        panel = theme['panel']
        text_c = theme['text']
        accent = theme['accent']
        style = theme['button_style']
        target.setStyleSheet(f"""
            QWidget {{ background: {bg}; color: {text_c}; }}
            QDialog {{ background: {bg}; color: {text_c}; }}
            QLabel {{ color: {text_c}; background: transparent; }}
            QPushButton {{ {style} }}
            QTabWidget::pane {{ border: 1px solid {accent}; background: {panel}; border-radius: 10px; }}
            QTabBar::tab {{ background: rgba(255,255,255,16); color: {text_c}; padding: 8px 12px; margin: 2px; border-radius: 10px; }}
            QTabBar::tab:selected {{ background: {accent}; color: #111; font-weight: bold; }}
        """)

    def _style_play_area(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        self.play_area.setStyleSheet(
            f"background: {theme['panel']}; border: 1px solid {theme['accent']}; border-radius: 20px;"
        )

    def _style_chips(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        for w in (self.label, self.auto_label, self.combo_label,
                  self.goober_label, self.prestige_label,
                  self.mission_label, self.essence_label):
            ss = (f"background: {theme['panel']}; border-radius: 12px; "
                  f"padding: 8px; color: {theme['text']};")
            self._orig_stylesheets[w] = ss
            w.setStyleSheet(ss)

    def _style_buttons(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        for btn in self.findChildren(QPushButton):
            try:
                btn.setStyleSheet(theme['button_style'])
            except RuntimeError:
                pass

    def apply_ui_theme(self):
        theme_id = self.state.selected_ui_theme
        if theme_id not in UI_THEMES:
            theme_id = "default"
            self.state.selected_ui_theme = theme_id
        theme = UI_THEMES[theme_id]
        self._apply_theme_dict(theme)
        self._style_play_area()
        self._style_chips()
        self._style_buttons()
        self.event_bubble.apply_theme(accent=theme["accent"], text=theme["text"], bg=theme["bg"])
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.keep_click_button_inside()

        for goober in self.goobers:
            if goober.isVisible():
                goober.keep_inside_after_resize()

    def refresh_all(self):
        self.update_ui()
        self.update_shop_buttons()
        self.update_secret_shop_buttons()

    def update_ui(self):
        self.label.setText(f"voce tem ${format_number(self.state.count)}!")
        now = time.time()
        while self._last_clicks and now - self._last_clicks[0] > 1.0:
            self._last_clicks.popleft()
        manual_cps = len(self._last_clicks)
        auto_val = self.state.get_auto_value()
        if auto_val > 0:
            self.auto_label.setText(f"{format_number(manual_cps)} + {format_number(auto_val)}/s")
        else:
            self.auto_label.setText(f"{format_number(manual_cps)}/s")

        if self.state.secret_shop_unlocked:
            self.goober_label.setText(f"🪙 {format_number(self.state.goober_coins)} gc")
        else:
            self.goober_label.setText(f"🪙 {format_number(self.state.goober_coins)} gc 🔒")

        bonus_pct = int((self.state.get_prestige_bonus_click() - 1) * 100)
        self.prestige_label.setText(f"✨ P{self.state.prestige_level} (+{bonus_pct}%)")

        self.essence_label.setText(f"💜 {format_number(self.state.poopy_essence)}")

        slots = self.state.mission_state.get("slots", [])
        if slots:
            parts = []
            for m in slots[:3]:
                p = int(m.get("progress", 0))
                t = int(m.get("target", 1))
                parts.append(f"{m.get('title', '?')} {p}/{t}")
            self.mission_label.setText("📋 " + " | ".join(parts))
        else:
            self.mission_label.setText("📋 Nenhuma missão ativa")

        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        for sk in ACTIVE_SKILLS:
            btn = self.skill_buttons.get(sk["key"])
            if btn is None:
                continue
            bought_attr = SKILL_PURCHASE_ATTRS.get(sk["key"])
            if bought_attr and not getattr(self.state, bought_attr, False):
                btn.setVisible(False)
                continue
            btn.setVisible(True)
            cd = self.state.skill_cooldowns.get(sk["key"], 0)
            if cd > 0:
                btn.setText(f"{sk['name']} ({cd}s)")
                btn.setEnabled(False)
                btn.setStyleSheet(f"background: rgba(255,255,255,12); color: {theme['accent2']}; border: none; border-radius: 6px;")
            else:
                btn.setText(sk["name"])
                btn.setEnabled(True)
                btn.setStyleSheet(f"background: {theme['accent']}; color: {theme['bg']}; border: none; border-radius: 6px; font-weight: bold;")

        for label in (self._goober_tab_info_label,):
            try:
                if label is not None:
                    label.setText(f"goober coins: {format_number(self.state.goober_coins)}")
            except RuntimeError:
                pass

        for label in (self._goober_tab_desc_label,):
            try:
                if label is not None:
                    label.setText("Compre itens para melhorar seus ganhos e desbloquear habilidades especiais.")
            except RuntimeError:
                pass

        self.update_secret_shop_buttons()

    def _show_onboarding(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("👋 Bem-vindo ao Poopy Clicker!")
        dialog.resize(440, 360)
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")
        l = QVBoxLayout(dialog)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(12)

        items = [
            ("🖱️ Clique!", "Clique no botão para ganhar dinheiro. Compre upgrades para ganhar mais."),
            ("👾 Goobers", "Goobers aparecem na tela. Clique neles para ganhar moedas e recompensas!"),
            ("🎲 Eventos", "Eventos aleatórios mudam o jogo — alguns ajudam, outros atrapalham."),
            ("💜 Essência", "Ao prestigiar, ganhe essência para comprar perks permanentes."),
            ("📋 Menu", "Use o botão Menu para acessar loja, missões, perks e configurações."),
        ]
        for emoji, text in items:
            title = QLabel(f"<b>{emoji}</b>")
            title.setWordWrap(True)
            title.setStyleSheet(f"font-size: 13pt; color: {theme['accent']};")
            l.addWidget(title)
            desc = QLabel(text)
            desc.setWordWrap(True)
            desc.setStyleSheet(f"font-size: 10pt; color: {theme['text']};")
            l.addWidget(desc)

        l.addStretch()
        btn = QPushButton("Entendi! ✅")
        btn.setMinimumHeight(40)
        btn.setStyleSheet(f"background: {theme['accent']}; color: {theme['bg']}; font-weight: bold; border-radius: 10px;")
        btn.clicked.connect(lambda: (dialog.accept(), self.state.settings.__setitem__("onboarding_done", True), self.save()))
        l.addWidget(btn)
        dialog.exec()

    def open_menu(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Menu")
        dialog.resize(*_dialog_size(28, 40))
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        self._apply_theme_dict(theme, widget=dialog)

        l = QVBoxLayout(dialog)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(8)

        btn_font = QFont()
        btn_font.setPointSize(12)
        btn_style = f"""
            QPushButton {{
                background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 10px;
                padding: 14px;
            }}
            QPushButton:hover {{ background: {theme['accent2']}; }}
        """

        cat = [
            ("🛒 Loja", self._open_shop_dialog),
            ("📚 Coleção", self._open_collection_dialog),
            ("📊 Progresso", self._open_progress_dialog),
            ("⚙️ Sistema", self._open_system_dialog),
        ]
        for text, handler in cat:
            btn = QPushButton(text)
            btn.setFont(btn_font)
            btn.setMinimumHeight(44)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda _, h=handler: (h(), dialog.close()))
            l.addWidget(btn)

        l.addStretch()
        close_btn = QPushButton("fechar")
        close_btn.setMinimumHeight(36)
        close_btn.setStyleSheet(theme['button_style'])
        close_btn.clicked.connect(dialog.close)
        l.addWidget(close_btn)
        dialog.exec()

    def _open_shop_dialog(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        d = QDialog(self)
        d.setWindowTitle("🛒 Loja")
        d.resize(*_dialog_size(32, 56))
        self._apply_theme_dict(theme, widget=d)
        tabs = QTabWidget()
        tabs.addTab(self._make_upgrade_tab(), "🛒 Loja")
        tabs.addTab(self._make_goober_tab(), "💎 Goobers")
        tabs.addTab(self._make_theme_tab(), "🎨 Temas")
        l = QVBoxLayout(d)
        l.addWidget(tabs)
        btn = QPushButton("fechar")
        btn.setMinimumHeight(36)
        btn.clicked.connect(d.close)
        l.addWidget(btn)
        d.finished.connect(self._compras_closed)
        d.exec()

    def _open_collection_dialog(self):
        self._open_tabbed_dialog("📚 Coleção", 32, 52, [
            (self._make_gooberario_tab(), "🐾 Gooberário"),
            (self._make_achievements_tab(), "🏆 Conquistas"),
        ])

    def _open_progress_dialog(self):
        self._open_tabbed_dialog("📊 Progresso", 36, 56, [
            (self._make_missions_tab(), "⚡ Missões"),
            (self._make_perks_tab(), "💜 Perks"),
            (self._make_prestige_tab(), "✨ Prestígio"),
        ])

    def _open_system_dialog(self):
        self._open_tabbed_dialog("⚙️ Sistema", 34, 56, [
            (self._make_settings_tab(), "⚙️ Config"),
            (self._make_stats_tab(), "📊 Stats"),
            (self._make_save_tab(), "💾 Save"),
            (self._make_credits_tab(), "📝 Créditos"),
        ])

    def _open_tabbed_dialog(self, title, w_pct, h_pct, tabs):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        d = QDialog(self)
        d.setWindowTitle(title)
        d.resize(*_dialog_size(w_pct, h_pct))
        self._apply_theme_dict(theme, widget=d)
        tw = QTabWidget()
        for widget_fn, tab_title in tabs:
            tw.addTab(widget_fn, tab_title)
        l = QVBoxLayout(d)
        l.addWidget(tw)
        btn = QPushButton("fechar")
        btn.setMinimumHeight(36)
        btn.clicked.connect(d.close)
        l.addWidget(btn)
        d.exec()

    def _make_upgrade_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(12)
        sf = QFont(); sf.setPointSize(11)
        smf = QFont(); smf.setPointSize(10)

        self.upgrade_bar = QProgressBar()
        self.upgrade_bar.setRange(0, 2000)
        self.upgrade_bar.setTextVisible(False)
        self.upgrade_bar.setFixedHeight(10)
        l.addWidget(self.upgrade_bar)
        ur = QHBoxLayout()
        self.upgrade_btn = QPushButton()
        self.upgrade_btn.setMinimumHeight(42); self.upgrade_btn.setFont(sf)
        self.upgrade_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 10px; font-size: 11pt; }}
            QPushButton:disabled {{ background: rgba(255,255,255,12); color: {theme['accent2']}; }}
        """)
        self.upgrade_btn.clicked.connect(self.buy_upgrade)
        self.upgrade_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        ur.addWidget(self.upgrade_btn, 1)
        self.upgrade_cost_label = QLabel()
        self.upgrade_cost_label.setFont(smf)
        self.upgrade_cost_label.setStyleSheet(f"color: {theme['accent2']};")
        self.upgrade_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ur.addWidget(self.upgrade_cost_label)
        l.addLayout(ur)

        self.auto_bar = QProgressBar()
        self.auto_bar.setRange(0, 2000)
        self.auto_bar.setTextVisible(False)
        self.auto_bar.setFixedHeight(10)
        l.addWidget(self.auto_bar)
        ar = QHBoxLayout()
        self.auto_btn = QPushButton()
        self.auto_btn.setMinimumHeight(42); self.auto_btn.setFont(sf)
        self.auto_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 10px; font-size: 11pt; }}
            QPushButton:disabled {{ background: rgba(255,255,255,12); color: {theme['accent2']}; }}
        """)
        self.auto_btn.clicked.connect(self.buy_auto)
        self.auto_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        ar.addWidget(self.auto_btn, 1)
        self.auto_cost_label = QLabel()
        self.auto_cost_label.setFont(smf)
        self.auto_cost_label.setStyleSheet(f"color: {theme['accent2']};")
        self.auto_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ar.addWidget(self.auto_cost_label)
        l.addLayout(ar)
        self.update_shop_buttons()
        l.addStretch()
        return w

    def _make_goober_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(8)
        smf = QFont(); smf.setPointSize(10)
        if self.state.secret_shop_unlocked:
            self._goober_tab_info_label = QLabel()
            self._goober_tab_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._goober_tab_info_label.setFont(smf)
            self._goober_tab_info_label.setStyleSheet(f"color: {theme['text']};")
            l.addWidget(self._goober_tab_info_label)
            self._goober_tab_desc_label = QLabel()
            self._goober_tab_desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self._goober_tab_desc_label.setWordWrap(True)
            self._goober_tab_desc_label.setFont(smf)
            self._goober_tab_desc_label.setStyleSheet(f"color: {theme['accent2']};")
            l.addWidget(self._goober_tab_desc_label)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}")
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            inner = QWidget()
            inner.setStyleSheet("background: transparent;")
            il = QVBoxLayout(inner)
            il.setContentsMargins(0, 0, 0, 0)
            il.setSpacing(6)
            self.secret_upgrade_items = list(SHOP_ITEM_DEFS)
            self.secret_buttons = {}
            for item in SHOP_ITEM_DEFS:
                widget = QWidget()
                widget.setCursor(Qt.CursorShape.PointingHandCursor)
                widget.setMinimumHeight(52)
                widget.setToolTip(item["desc"])
                il2 = QVBoxLayout(widget)
                il2.setContentsMargins(10, 7, 10, 7)
                il2.setSpacing(1)
                name_lbl = QLabel(f"{item['name']} — {item['cost']} gc")
                name_lbl.setStyleSheet(f"color: {theme['bg']}; font-weight: bold; font-size: 10pt; background: transparent;")
                il2.addWidget(name_lbl)
                desc_lbl = QLabel(item['desc'])
                desc_lbl.setStyleSheet(f"color: {theme['bg']}aa; font-size: 8pt; background: transparent;")
                desc_lbl.setWordWrap(True)
                il2.addWidget(desc_lbl)
                widget.mouseReleaseEvent = lambda e, k=item["key"], w=widget: e.button() == Qt.MouseButton.LeftButton and w.isEnabled() and self.buy_shop_item(k)
                il.addWidget(widget)
                self.secret_buttons[item["key"]] = {"widget": widget, "name": name_lbl, "desc": desc_lbl}
                self._update_shop_btn_text(self.secret_buttons[item["key"]], item, getattr(self.state, item["attr"]))
            il.addStretch()
            scroll.setWidget(inner)
            l.addWidget(scroll, 1)
        else:
            locked = QLabel("🔒 Desbloqueie clicando em goobers.")
            locked.setStyleSheet(f"color: {theme['accent2']}; font-size: 10pt;")
            locked.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(locked)
        return w

    def _make_theme_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(6)
        smf = QFont(); smf.setPointSize(10)
        self.theme_shop_buttons = {}
        for tid in UI_THEMES:
            tdata = UI_THEMES[tid]
            btn = QPushButton()
            btn.setMinimumHeight(40)
            btn.setFont(smf)
            btn.setStyleSheet(f"""
                QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                    font-weight: bold; border: none; border-radius: 8px; font-size: 10pt; }}
                QPushButton:disabled {{ background: rgba(255,255,255,12); color: {theme['accent2']}; }}
            """)
            btn.clicked.connect(lambda _, t=tid: self._handle_theme_click(t))
            l.addWidget(btn)
            self.theme_shop_buttons[tid] = btn
        self._refresh_theme_buttons()
        l.addStretch()
        return w

    def _make_gooberario_tab(self):
        from bestiary import open_bestiary
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(16, 16, 16, 16)
        lbl = QLabel("Veja todos os tipos de goober que você já encontrou.")
        lbl.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
        l.addWidget(lbl)
        btn = QPushButton("📚 Abrir Gooberário")
        btn.setMinimumHeight(42)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 10px; font-size: 11pt;
            }}
        """)
        btn.clicked.connect(lambda: open_bestiary(self, self.state))
        l.addWidget(btn)
        l.addStretch()
        return w

    def _make_achievements_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setStyleSheet(f"QScrollArea {{ background: {theme['panel']}; border: none; }}")
        cw = QWidget()
        cw.setStyleSheet(f"background: {theme['panel']};")
        cl = QVBoxLayout(cw)
        cl.setSpacing(4)
        total = len(ACHIEVEMENT_DEFS)
        unlocked_count = len(self.state.unlocked_achievements)
        header = QLabel(f"Conquistas: {unlocked_count}/{total}")
        header.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {theme['text']};")
        cl.addWidget(header)
        for ach in ACHIEVEMENT_DEFS:
            aid, aname, adesc, areq = ach
            unlocked = aid in self.state.unlocked_achievements
            icon = "✅" if unlocked else "🔒"
            txt = f"{icon} <b style='color:{theme['text']};'>{aname}<br></b><span style='color:{theme['accent2']};font-size:8pt;'>{adesc}</span>"
            lbl = QLabel(txt)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 9pt; padding: 2px 0;")
            cl.addWidget(lbl)
        cl.addStretch()
        sa.setWidget(cw)
        l.addWidget(sa)
        return w

    def _make_missions_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)

        completed = self.state.mission_state.get("completed_total", 0)
        header = QLabel(f"📋 Missões concluídas: {completed}")
        header.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {theme['text']};")
        l.addWidget(header)

        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}")

        def rebuild_mission_list():
            cw = QWidget()
            cw.setStyleSheet(f"background: transparent;")
            cl = QVBoxLayout(cw)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(6)
            slots = self.state.mission_state.get("slots", [])
            if slots:
                for m in slots:
                    card = MissionCard(m, theme)
                    cl.addWidget(card)
            else:
                nl = QLabel("Nenhuma missão ativa.")
                nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                nl.setStyleSheet(f"color: {theme['accent2']}; font-size: 10pt; padding: 20px;")
                cl.addWidget(nl)
            cl.addStretch()
            sa.setWidget(cw)

        rebuild_mission_list()
        l.addWidget(sa)

        refresh_btn = QPushButton("🔄 Atualizar Missões")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; }}
        """)
        refresh_btn.clicked.connect(lambda: (
            self.ensure_missions(force=True), self.update_missions(),
            rebuild_mission_list()
        ))
        l.addWidget(refresh_btn)

        return w

    def _make_perks_tab(self):
        from PyQt6.QtWidgets import QHBoxLayout
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        self._perk_tab_widgets = {}
        self._perk_defs_by_key = {p["key"]: p for p in PERK_DEFS}
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)

        for pdata in PERK_DEFS:
            key = pdata["key"]
            max_lvl = pdata.get("max_level", 10)
            row = QHBoxLayout()
            text = QLabel()
            text.setWordWrap(True)
            text.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
            row.addWidget(text, 1)
            btn = QPushButton()
            btn.setMinimumHeight(36)
            btn.setStyleSheet(f"""
                QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                    font-weight: bold; border: none; border-radius: 8px; }}
                QPushButton:disabled {{ background: rgba(255,255,255,12); color: {theme['accent2']}; }}
            """)
            btn.clicked.connect(lambda _, k=key, b=pdata.get("base_cost", 5): self._buy_perk_from_tab(k, b))
            row.addWidget(btn)
            l.addLayout(row)
            self._perk_tab_widgets[key] = (text, btn, max_lvl)

        self._refresh_perks_tab()
        l.addStretch()
        return w

    def _refresh_perks_tab(self):
        for key, (text, btn, max_lvl) in self._perk_tab_widgets.items():
            level = self.state.perks.get(key, 0)
            pd = self._perk_defs_by_key.get(key, {})
            cost = pd.get("base_cost", 5) * (level + 1)
            text.setText(f"{pd.get('name', key)}: {level}/{max_lvl}")
            if level >= max_lvl:
                btn.setText("MAX")
                btn.setEnabled(False)
            else:
                btn.setText(f"↑ {cost} 💜")
                btn.setEnabled(self.state.poopy_essence >= cost)

    def _buy_perk_from_tab(self, key, base_cost):
        level = self.state.perks.get(key, 0)
        cost = base_cost * (level + 1)
        if self.state.poopy_essence >= cost:
            self.state.poopy_essence -= cost
            self.state.perks[key] = level + 1
            self.save()
            self.update_ui()
        self._refresh_perks_tab()

    def _make_prestige_tab(self):
        from constants import PRESTIGE_MILESTONES
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)

        cost = self.state.get_prestige_cost()
        info = QLabel(
            f"Nível: {self.state.prestige_level}\n"
            f"Custo: ${format_number(cost)}\n"
            f"Essência estimada: +{self.state.calculate_prestige_gain()}\n"
            f"Bônus de clique: +{int((self.state.get_prestige_bonus_click() - 1) * 100)}%\n"
            f"Bônus de auto: +{int((self.state.get_prestige_bonus_auto() - 1) * 100)}%"
        )
        info.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
        l.addWidget(info)

        btn = QPushButton("✨ Prestigiar!")
        btn.setMinimumHeight(42)
        btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; font-size: 12pt; }}
            QPushButton:disabled {{ background: rgba(255,255,255,12); color: {theme['accent2']}; }}
        """)
        btn.setEnabled(self.state.count >= cost)
        btn.clicked.connect(self.do_prestige)
        l.addWidget(btn)

        mt = QLabel("Marcos de Prestígio")
        mt.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {theme['text']}; margin-top: 8px;")
        l.addWidget(mt)
        for level, name, desc in PRESTIGE_MILESTONES:
            unlocked = self.state.prestige_level >= level
            prefix = "✅" if unlocked else f"🔒"
            ml = QLabel(f"{prefix}  Lv.{level} — {name}: {desc}")
            ml.setWordWrap(True)
            ml.setStyleSheet(f"color: {theme['text']}; font-size: 9pt;")
            l.addWidget(ml)

        l.addStretch()
        return w

    def _make_settings_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)
        smf = QFont(); smf.setPointSize(10)

        toggles = [
            ("Textos flutuantes", "show_floating_text", True),
            ("Partículas", "show_particles", True),
            ("Animar goobers", "animate_goobers", True),
            ("Movimento reduzido", "reduced_motion", False),
            ("Modo baixo consumo", "low_power_mode", False),
            ("Ganhos offline", "offline_progress", True),
        ]
        for text, key, default in toggles:
            cb = QCheckBox(text)
            cb.setChecked(self.state.settings.get(key, default))
            cb.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
            cb.stateChanged.connect(lambda _, k=key, cb=cb: (
                self.state.settings.__setitem__(k, cb.isChecked()), self.save()
            ))
            l.addWidget(cb)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {theme['accent']}; margin: 6px 0;")
        l.addWidget(sep)

        sound_label = QLabel("🔊 Áudio")
        sound_label.setStyleSheet(f"color: {theme['text']}; font-size: 11pt; font-weight: bold;")
        l.addWidget(sound_label)

        sound_cb = QCheckBox("Efeitos sonoros")
        sound_cb.setChecked(self.state.settings.get("sound_enabled", True))
        sound_cb.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
        def _on_sound_toggle(v, cb=sound_cb):
            en = cb.isChecked()
            self.state.settings["sound_enabled"] = en
            self.sound.set_sfx_enabled(en)
            self.save()
        sound_cb.stateChanged.connect(_on_sound_toggle)
        l.addWidget(sound_cb)

        sfx_vol = QSlider(Qt.Orientation.Horizontal)
        sfx_vol.setRange(0, 100)
        sfx_vol.setValue(int(self.state.settings.get("sfx_volume", 0.7) * 100))
        sfx_vol.setStyleSheet(f"""
            QSlider::groove:horizontal {{ background: {theme['panel']}; height: 4px; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {theme['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
            QSlider::sub-page:horizontal {{ background: {theme['accent']}; border-radius: 2px; }}
        """)
        def _on_sfx_vol(v):
            vol = v / 100.0
            self.state.settings["sfx_volume"] = vol
            self.sound.set_sfx_volume(vol)
            self.save()
        sfx_vol.valueChanged.connect(_on_sfx_vol)
        l.addWidget(sfx_vol)

        music_sep = QFrame()
        music_sep.setFrameShape(QFrame.Shape.HLine)
        music_sep.setStyleSheet(f"color: {theme['accent']}; margin: 6px 0;")
        l.addWidget(music_sep)

        music_btn = QPushButton("🎵 Abrir player de música")
        music_btn.setMinimumHeight(38)
        music_btn.setFont(smf)
        music_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; font-size: 10pt; }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
        music_btn.clicked.connect(self._open_music_player)
        l.addWidget(music_btn)

        l.addStretch()
        return w

    def _open_music_player(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        d = QDialog(self)
        d.setWindowTitle("🎵 Player de Música")
        d.resize(*_dialog_size(28, 56))
        self._apply_theme_dict(theme, widget=d)

        l = QVBoxLayout(d)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(10)

        bf = QFont(); bf.setPointSize(14)
        mf = QFont(); mf.setPointSize(11)
        smf = QFont(); smf.setPointSize(10)

        cover = QLabel()
        cover.setFixedSize(160, 160)
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_pix = QPixmap(160, 160)
        cover_pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(cover_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, 160, 160)
        grad.setColorAt(0.0, QColor(theme['accent']).lighter(140))
        grad.setColorAt(1.0, QColor(theme['accent2']).lighter(120))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 160, 160, 16, 16)
        painter.setPen(QColor(theme['bg']))
        nf = QFont(); nf.setPointSize(48)
        painter.setFont(nf)
        painter.drawText(cover_pix.rect(), Qt.AlignmentFlag.AlignCenter, "🎵")
        painter.end()
        cover.setPixmap(cover_pix)
        l.addWidget(cover, 0, Qt.AlignmentFlag.AlignCenter)

        self._music_now_playing = QLabel("Nenhuma faixa selecionada")
        self._music_now_playing.setFont(mf)
        self._music_now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._music_now_playing.setStyleSheet(f"color: {theme['accent']}; font-weight: bold;")
        self._music_now_playing.setWordWrap(True)
        l.addWidget(self._music_now_playing)

        controls = QHBoxLayout()
        self._music_play_btn = QPushButton("⏸️" if self.sound.get_music_enabled() and self.sound.get_current_track_index() >= 0 else "▶️")
        self._music_play_btn.setMinimumSize(48, 36)
        self._music_play_btn.setFont(mf)
        self._music_play_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; }}
        """)
        self._music_play_btn.clicked.connect(self._toggle_music_play)
        controls.addWidget(self._music_play_btn)

        stop_btn = QPushButton("⏹️")
        stop_btn.setMinimumSize(48, 36)
        stop_btn.setFont(mf)
        stop_btn.setStyleSheet(f"""
            QPushButton {{ background: rgba(255,255,255,12); color: {theme['text']};
                border: none; border-radius: 8px; }}
            QPushButton:hover {{ background: rgba(255,255,255,22); }}
        """)
        stop_btn.clicked.connect(self._stop_music)
        controls.addWidget(stop_btn)
        l.addLayout(controls)

        vol_label = QLabel(f"Volume: {int(self.sound.get_music_volume() * 100)}%")
        vol_label.setFont(smf)
        vol_label.setStyleSheet(f"color: {theme['text']};")
        l.addWidget(vol_label)

        music_vol = QSlider(Qt.Orientation.Horizontal)
        music_vol.setRange(0, 100)
        music_vol.setValue(int(self.sound.get_music_volume() * 100))
        music_vol.setStyleSheet(f"""
            QSlider::groove:horizontal {{ background: {theme['panel']}; height: 4px; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {theme['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
            QSlider::sub-page:horizontal {{ background: {theme['accent']}; border-radius: 2px; }}
        """)
        def _on_music_vol(v, lbl=vol_label):
            vol = v / 100.0
            self.state.settings["music_volume"] = vol
            self.sound.set_music_volume(vol)
            lbl.setText(f"Volume: {v}%")
            self.save()
        music_vol.valueChanged.connect(_on_music_vol)
        l.addWidget(music_vol)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {theme['accent']}; margin: 4px 0;")
        l.addWidget(sep)

        track_header = QLabel("🎶 Faixas")
        track_header.setFont(mf)
        track_header.setStyleSheet(f"color: {theme['accent2']}; font-weight: bold;")
        l.addWidget(track_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        il = QVBoxLayout(inner)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(4)

        tracks = self.sound.get_tracks()
        if tracks:
            self._music_track_btns = {}
            for i, t in enumerate(tracks):
                btn = QPushButton(t["name"])
                btn.setMinimumHeight(34)
                btn.setFont(smf)
                playing = (i == self.sound.get_current_track_index()) and self.sound.get_music_enabled()
                if playing:
                    btn.setStyleSheet(f"""
                        QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                            font-weight: bold; border: none; border-radius: 6px; font-size: 9pt;
                            text-align: left; padding-left: 10px; }}
                    """)
                    self._music_now_playing.setText(f"▶ Tocando: {t['name']}")
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{ background: rgba(255,255,255,10); color: {theme['text']};
                            border: none; border-radius: 6px; font-size: 9pt;
                            text-align: left; padding-left: 10px; }}
                        QPushButton:hover {{ background: rgba(255,255,255,20); }}
                    """)
                btn.clicked.connect(lambda _, idx=i: self._select_track_from_player(idx))
                il.addWidget(btn)
                self._music_track_btns[i] = btn
        else:
            no_tracks = QLabel("📂 Nenhuma música encontrada.\nColoque arquivos .mp3/.ogg/.wav\nem assets/music/")
            no_tracks.setWordWrap(True)
            no_tracks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_tracks.setStyleSheet(f"color: {theme['accent2']}; font-size: 9pt; padding: 12px 0;")
            il.addWidget(no_tracks)
        il.addStretch()
        scroll.setWidget(inner)
        l.addWidget(scroll, 1)

        close_btn = QPushButton("fechar")
        close_btn.setMinimumHeight(34)
        close_btn.setStyleSheet(theme['button_style'])
        close_btn.clicked.connect(d.close)
        l.addWidget(close_btn)

        d.exec()

    def _toggle_music_play(self):
        enabled = not self.sound.get_music_enabled()
        self.sound.set_music_enabled(enabled)
        self.state.settings["music_enabled"] = enabled
        self.save()
        self._music_play_btn.setText("⏸️" if enabled and self.sound.get_current_track_index() >= 0 else "▶️")

    def _stop_music(self):
        self.sound.stop_music()
        self.state.settings["music_enabled"] = False
        self.save()
        self._music_play_btn.setText("▶️")
        self._music_now_playing.setText("Nenhuma faixa selecionada")
        for btn in self._music_track_btns.values():
            theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
            btn.setStyleSheet(f"""
                QPushButton {{ background: rgba(255,255,255,10); color: {theme['text']};
                    border: none; border-radius: 6px; font-size: 9pt;
                    text-align: left; padding-left: 10px; }}
                QPushButton:hover {{ background: rgba(255,255,255,20); }}
            """)

    def _select_track_from_player(self, index):
        self.sound.play_track(index)
        self.state.settings["selected_music_track"] = self.sound.get_tracks()[index]["name"]
        self.state.settings["music_enabled"] = True
        self.save()
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        self._music_now_playing.setText(f"▶ Tocando: {self.sound.get_tracks()[index]['name']}")
        self._music_play_btn.setText("⏸️")
        for i, btn in self._music_track_btns.items():
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                        font-weight: bold; border: none; border-radius: 6px; font-size: 9pt;
                        text-align: left; padding-left: 10px; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{ background: rgba(255,255,255,10); color: {theme['text']};
                        border: none; border-radius: 6px; font-size: 9pt;
                        text-align: left; padding-left: 10px; }}
                    QPushButton:hover {{ background: rgba(255,255,255,20); }}
                """)

    def _make_stats_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)

        s = self.state.stats
        text = (
            f"Dinheiro total: ${format_number(s.get('money_earned', 0))}\n"
            f"Cliques totais: {format_number(s.get('total_clicks', 0))}\n"
            f"Goobers clicados: {format_number(s.get('goobers_clicked', 0))}\n"
            f"Bosses derrotados: {format_number(s.get('boss_defeated', 0))}\n"
            f"RGB derrotados: {format_number(s.get('rgb_defeated', 0))}\n"
            f"Prestígios: {format_number(s.get('prestiges_done', 0))}\n"
            f"Maior combo: {format_number(s.get('highest_combo', 0))}\n"
            f"Offline ganho: ${format_number(s.get('offline_earned_total', 0))}"
        )
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
        l.addWidget(lbl)

        active = self.state.get_active_synergies()
        if active:
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet(f"color: {theme['accent']}; margin: 4px 0;")
            l.addWidget(sep2)
            syn_header = QLabel("⚡ Sinergias ativas")
            syn_header.setStyleSheet(f"color: {theme['accent']}; font-size: 10pt; font-weight: bold;")
            l.addWidget(syn_header)
            for syn in active:
                sl = QLabel(f"  ✅ {syn['name']}: {syn['desc']}")
                sl.setWordWrap(True)
                sl.setStyleSheet(f"color: {theme['text']}; font-size: 9pt;")
                l.addWidget(sl)

        l.addStretch()
        return w

    def _make_save_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)

        info = QLabel("Salve ou carregue seu progresso manualmente.")
        info.setStyleSheet(f"color: {theme['accent2']}; font-size: 10pt;")
        l.addWidget(info)

        def btn_style():
            return f"""
                QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                    font-weight: bold; border: none; border-radius: 8px; font-size: 11pt; }}
            """
        save_btn = QPushButton("💾 Salvar")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet(btn_style())
        save_btn.clicked.connect(lambda: (self.save(), self.show_floating_text("salvo!", QPoint(self.play_area.width() // 2, 80), "#9cf6ff")))
        l.addWidget(save_btn)

        load_btn = QPushButton("📂 Carregar")
        load_btn.setMinimumHeight(40)
        load_btn.setStyleSheet(btn_style())
        load_btn.clicked.connect(lambda: (self.load(), self.show_floating_text("carregado!", QPoint(self.play_area.width() // 2, 80), "#9cf6ff")))
        l.addWidget(load_btn)
        l.addStretch()
        return w

    def _make_credits_tab(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w = QWidget()
        w.setStyleSheet(f"background: {theme['panel']};")
        l = QVBoxLayout(w)
        l.setContentsMargins(12, 12, 12, 12)
        l.setSpacing(8)

        import os
        from PyQt6.QtGui import QPixmap

        for line, sz in [("🐍 Código: mafuzyk & Julia", 11), ("🎨 Arte por: mafuzyk", 10)]:
            lbl = QLabel(line)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {theme['text']}; font-size: {sz}pt;")
            l.addWidget(lbl)

        art_path = os.path.join(os.path.dirname(__file__), "assets", "Algo.png")
        if os.path.exists(art_path):
            pix = QPixmap(art_path)
            if not pix.isNull():
                pix = pix.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                art = QLabel()
                art.setPixmap(pix)
                art.setAlignment(Qt.AlignmentFlag.AlignCenter)
                l.addWidget(art)

        link = QLabel('<a href="https://jiggle-systems.neocities.org" style="color: #8bd3ff;">🔗 Julia — jiggle-systems.neocities.org</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link.setStyleSheet(f"font-size: 10pt;")
        l.addWidget(link)

        thanks = QLabel("💜 Obrigado por jogar!")
        thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks.setStyleSheet(f"color: {theme['text']}; font-size: 10pt;")
        l.addWidget(thanks)
        l.addStretch()
        return w

    def center_click_button(self):
        area_w = self.play_area.width()
        area_h = self.play_area.height()
        btn_w = self.click_btn.width()
        btn_h = self.click_btn.height()

        x = max(12, (area_w - btn_w) // 2)
        y = max(12, (area_h - btn_h) // 2)
        self.click_btn.move(x, y)

    def keep_click_button_inside(self):
        area_w = self.play_area.width()
        area_h = self.play_area.height()
        btn_w = self.click_btn.width()
        btn_h = self.click_btn.height()

        max_x = max(12, area_w - btn_w - 12)
        max_y = max(12, area_h - btn_h - 12)

        x = min(max(12, self.click_btn.x()), max_x)
        y = min(max(12, self.click_btn.y()), max_y)

        self.click_btn.move(x, y)

    def move_click_button_randomly(self):
        active = EVENT_INFO.get(self.active_event, {})
        step = int(self.state.get_difficulty_step() * self.current_button_move_bonus())
        if self.state.settings.get("low_power_mode", False):
            step = max(3, int(step * 0.8))

        area_w = self.play_area.width()
        area_h = self.play_area.height()
        margin = 12
        bw = self.click_btn.width()
        bh = self.click_btn.height()
        min_x = margin
        max_x = max(margin, area_w - bw - margin)
        min_y = margin
        max_y = max(margin, area_h - bh - margin)

        cx = min_x + (max_x - min_x) / 2
        cy = min_y + (max_y - min_y) / 2

        current_x = self.click_btn.x()
        current_y = self.click_btn.y()

        drift_x = random.randint(-step, step)
        drift_y = random.randint(-step // 2, step // 2)

        if active.get("gravity"):
            drift_y += 16

        if random.random() < 0.18:
            drift_x += random.choice([-1, 1]) * (step // 2)

        if active.get("invert_move"):
            drift_x = int(-drift_x * 0.85)
            drift_y = int(-drift_y * 0.85)

        if current_x < min_x + 8 and drift_x <= 0:
            drift_x = random.randint(max(1, step // 3), max(2, step))
        if current_x > max_x - 8 and drift_x >= 0:
            drift_x = -random.randint(max(1, step // 3), max(2, step))
        if current_y < min_y + 8 and drift_y <= 0:
            drift_y = random.randint(1, max(1, step // 3))
        if current_y > max_y - 8 and drift_y >= 0:
            drift_y = -random.randint(1, max(1, step // 3))

        new_x = current_x + drift_x
        new_y = current_y + drift_y

        new_x = max(min_x, min(new_x, max_x))
        new_y = max(min_y, min(new_y, max_y))

        self.click_btn.move(new_x, new_y)

    def rarity_for_goober(self, goober_type):
        return GOOBER_INFO.get(goober_type, GOOBER_INFO["normal"])["rarity"]

    def get_rarity_money_multiplier(self, goober_type):
        base = RARITY_INFO[self.rarity_for_goober(goober_type)]["mult"]
        return (base + (self.state.perks.get("goober_luck", 0) * 0.05)) * self.state.get_collection_money_bonus()

    def choose_goober_type(self):
        boss_bonus = self.state.perks.get("boss_hunter", 0) * 0.01
        if self.state.prestige_level >= 10:
            boss_bonus += 0.02
        if self.state.boss_beacon_bought:
            boss_bonus += 0.03
        active = EVENT_INFO.get(self.active_event, {})
        boss_bonus += float(active.get("boss_bonus", 0.0))
        if (not self.boss_active and self.state.stats["money_earned"] > 10000
                and random.random() < BOSS_SPAWN_CHANCE + boss_bonus):
            return "boss"

        luck_bonus = self.state.perks.get("goober_luck", 0) * 0.0015 + self.state.get_collection_luck_bonus()
        if self.state.prestige_level >= 5:
            luck_bonus += 0.002
        luck_bonus += float(active.get("rare_bonus", 0.0))

        rarities = ["common", "rare", "epic", "legendary", "mythic"]
        rw = [RARITY_SPAWN_WEIGHT[r] for r in rarities]
        for i in range(len(rw)):
            rw[i] *= (1.0 + luck_bonus * 40.0 * (i + 1))

        chosen = random.choices(rarities, weights=rw, k=1)[0]
        candidates = [k for k, v in GOOBER_INFO.items() if v["rarity"] == chosen and k != "boss"]
        if not candidates:
            return "normal"
        return random.choice(candidates)

    def try_spawn_goober(self):
        alive_or_visible = sum(1 for g in self.goobers if g.isVisible())
        active = EVENT_INFO.get(self.active_event, {})
        limit = MAX_GOOBERS + self.state.perks.get("goober_luck", 0) + int(active.get("spawn_bonus", 0))
        if alive_or_visible >= limit:
            return

        goober_type = self.choose_goober_type()
        if goober_type == "boss":
            self.boss_active = True
            self.sound.play("boss_hit")
        else:
            self.sound.play("goober_spawn")
        goober = Goober(self.play_area, self, self.state, goober_type=goober_type)
        goober.show()
        self.goobers.append(goober)

    def register_goober_seen(self, goober_type):
        if goober_type not in self.state.bestiary_counts:
            self.state.bestiary_counts[goober_type] = {"seen": 0, "clicked": 0}
        self.state.bestiary_counts[goober_type]["seen"] += 1
        if self.rarity_for_goober(goober_type) != "common":
            self.state.stats["rare_seen"] += 1
        self.check_collection_rewards()

    def register_goober_clicked(self, goober_type):
        if goober_type not in self.state.bestiary_counts:
            self.state.bestiary_counts[goober_type] = {"seen": 0, "clicked": 0}
        self.state.bestiary_counts[goober_type]["clicked"] += 1

    def check_collection_rewards(self):
        changed = False
        claimed = self.state.stats.get("collection_rewards_claimed", [])
        for reward in COLLECTION_REWARDS:
            if reward["id"] not in claimed and reward["req"](self.state):
                claimed.append(reward["id"])
                self.show_floating_text(f"Coleção: {reward['name']}!", QPoint(self.play_area.width() // 2, 110), "#8cecff")
                self.sound.play("collection")
                changed = True
        self.state.stats["collection_rewards_claimed"] = claimed
        if changed:
            self.save()

    def show_floating_text(self, text, pos, color="#ffffff"):
        if not self.state.settings.get("show_floating_text", True):
            return
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        label = QLabel(text, self.play_area)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label.setStyleSheet(
            f"""
            color: {color};
            font-size: 12pt;
            font-weight: bold;
            background: {theme['panel']};
            border-radius: 8px;
            padding: 2px 6px;
            """
        )
        label.adjustSize()
        centered_pos = QPoint(pos.x() - label.width() // 2, pos.y() - label.height() // 2)
        label.move(centered_pos)
        anim = QPropertyAnimation(label, b"pos", label)
        anim.setDuration(950)
        anim.setStartValue(centered_pos)
        anim.setEndValue(centered_pos + QPoint(0, -20))
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.finished.connect(label.deleteLater)
        label.show()
        anim.start()

    def adjusted_event_duration(self, name, base_duration):
        info = EVENT_INFO.get(name, {})
        if info.get("good") is True:
            return int(base_duration * (1.0 + self.state.perks.get("good_events", 0) * 0.07))
        if info.get("good") is False:
            return max(3, int(base_duration * (1.0 - self.state.perks.get("bad_events", 0) * 0.06)))
        return base_duration

    def start_event(self, event_name, duration, title, desc, color):
        info = EVENT_INFO.get(event_name, {})
        duration = int(info.get("duration", duration))
        duration = self.adjusted_event_duration(event_name, duration)
        self.active_event = event_name
        self.state.stats["events_seen"] = self.state.stats.get("events_seen", 0) + 1
        self.event_end_time = time.time() + duration
        self.event_total_duration = duration
        self.event_title = title
        self.event_desc = desc
        self.event_color = color
        self.event_bubble.apply_theme(accent=color, text=UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"]).get("text", "#ffffff"), bg=UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"]).get("bg", "#000000"))
        rarity = EVENT_RARITY_INFO.get(info.get("rarity", "common"), {}).get("label", "")
        self.event_bubble.title.setText(f"{title} • {rarity}" if rarity else title)
        self.event_bubble.desc.setText(desc)
        self.event_bubble.bar.setValue(100)
        self.event_bubble.setVisible(True)
        scale_mult = float(info.get("scale_mult", 1.0))
        bw, bh = self._btn_original_size
        self.click_btn.resize(int(bw * scale_mult), int(bh * scale_mult))
        self.keep_click_button_inside()
        if info.get("invert_colors"):
            theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
            inverted = dict(theme.get("inverted", theme))
            inverted.setdefault("button_style", theme["button_style"])
            self._apply_theme_dict(inverted)
        self.show_floating_text(title, QPoint(self.play_area.width() // 2, 80), color)
        self.sound.play("event_start")
        self.update_ui()

    def clear_event(self):
        self.active_event = None
        self.event_end_time = 0
        self.event_total_duration = 0
        self.event_title = ""
        self.event_desc = ""
        self.event_color = "#8bd3ff"
        self.event_bubble.setVisible(False)
        self.click_btn.resize(*self._btn_original_size)
        self.keep_click_button_inside()
        self.apply_ui_theme()
        self.sound.play("event_end")
        self.update_ui()

    def update_event_state(self):
        if self.active_event is None:
            self.event_bubble.setVisible(False)
            return
        remaining = max(0.0, self.event_end_time - time.time())
        if remaining <= 0:
            self.clear_event()
            return
        progress = int((remaining / max(0.001, self.event_total_duration)) * 100)
        self.event_bubble.bar.setValue(progress)
        self.event_bubble.setVisible(True)
        self.apply_mouse_flee()

    def try_random_event(self):
        if self.active_event is not None:
            return
        if self._skill_shield_active:
            return
        if random.random() > EVENT_TRIGGER_CHANCE:
            return

        rarities = ["common", "rare", "epic", "legendary", "mythic"]
        rw = [EVENT_RARITY_INFO[r]["weight"] for r in rarities]

        if self.state.prestige_level >= 3:
            for i in range(len(rw)):
                if rarities[i] in ("rare", "epic"):
                    rw[i] *= 1.08

        chosen = random.choices(rarities, weights=rw, k=1)[0]
        candidates = [k for k, v in EVENT_INFO.items() if v["rarity"] == chosen]
        if not candidates:
            return
        event_name = random.choice(candidates)
        info = EVENT_INFO[event_name]
        self.start_event(event_name, info["duration"], info["name"], info["desc"], info["color"])

    def apply_mouse_flee(self):
        active = EVENT_INFO.get(self.active_event, {})
        if not active:
            return

        if active.get("center_pull"):
            center_x = (self.play_area.width() - self.click_btn.width()) // 2
            center_y = (self.play_area.height() - self.click_btn.height()) // 2
            self.click_btn.move(
                self.click_btn.x() + int((center_x - self.click_btn.x()) * 0.08),
                self.click_btn.y() + int((center_y - self.click_btn.y()) * 0.08),
            )
            self.keep_click_button_inside()

        if active.get("orbit"):
            self._orbit_angle += 0.12
            radius = 42
            center_x = (self.play_area.width() - self.click_btn.width()) // 2
            center_y = (self.play_area.height() - self.click_btn.height()) // 2
            new_x = center_x + int(math.cos(self._orbit_angle) * radius)
            new_y = center_y + int(math.sin(self._orbit_angle) * radius)
            self.click_btn.move(new_x, new_y)
            self.keep_click_button_inside()

        if not (active.get("mouse_flee") or active.get("blink")):
            return

        cursor_local = self.play_area.mapFromGlobal(QCursor.pos())
        if not self.play_area.rect().contains(cursor_local):
            return

        btn_center = QPoint(self.click_btn.x() + self.click_btn.width() // 2,
                            self.click_btn.y() + self.click_btn.height() // 2)
        dx = btn_center.x() - cursor_local.x()
        dy = btn_center.y() - cursor_local.y()
        distance_sq = dx * dx + dy * dy

        if active.get("blink"):
            if distance_sq < 180 * 180 and random.random() < 0.14:
                jump = 55
                self.click_btn.move(
                    self.click_btn.x() + random.randint(-jump, jump),
                    self.click_btn.y() + random.randint(-jump, jump)
                )
                self.keep_click_button_inside()
            if not active.get("mouse_flee"):
                return

        flee_range = 220 + int(self.state.get_difficulty_step() * 1.5)
        if active.get("mouse_flee") and distance_sq < flee_range * flee_range:
            from_level = self.state.prestige_level * 1.8
            from_wealth = min(self.state.lifetime_money / 300_000, 2.5)
            from_upgrades = (self.state.upgrade_level + self.state.auto_level) * 0.6
            flee_strength = int(28 + from_level + from_wealth + from_upgrades)
            if dx != 0:
                self.click_btn.move(
                    self.click_btn.x() + int(flee_strength * (1 if dx > 0 else -1)),
                    self.click_btn.y()
                )
            if dy != 0:
                self.click_btn.move(
                    self.click_btn.x(),
                    self.click_btn.y() + int(flee_strength * (1 if dy > 0 else -1))
                )
            self.keep_click_button_inside()

    def current_event_modifier(self, key, default=0.0):
        active = EVENT_INFO.get(self.active_event, {})
        return float(active.get(key, default))

    def current_event_click_mult(self):
        return self.current_event_modifier("click_mult", 1.0)

    def current_event_auto_mult(self):
        return self.current_event_modifier("auto_mult", 1.0)

    def current_button_move_bonus(self):
        active = EVENT_INFO.get(self.active_event, {})
        mult = float(active.get("move_mult", 1.0))
        if self.state.settings.get("reduced_motion", False):
            mult *= 0.7
        return mult

    def add_combo(self):
        self.state.combo_count += 1
        self.state.combo_multiplier = 1.0 + (self.state.combo_count * 0.05)
        self.sound.play("combo_up")
        if self.state.combo_count > self.state.stats.get("highest_combo", 0):
            self.state.stats["highest_combo"] = self.state.combo_count
        grace = int(self.current_event_modifier("combo_grace", 0))
        self.combo_decay_timer.start(1800 + grace)
        self.update_combo_label()

    def reset_combo(self):
        self.state.combo_count = 0
        self.state.combo_multiplier = 1.0
        self.sound.play("combo_break")
        self.update_combo_label()

    def update_combo_label(self):
        if self.state.combo_count > 0:
            self.combo_label.setText(f"🔥 Combo x{self.state.combo_count} ({self.state.combo_multiplier:.1f}x)")
        else:
            self.combo_label.setText("")

    def get_max_mission_slots(self):
        slots = 3
        if self.state.prestige_level >= 1:
            slots += 1
        if self.state.prestige_level >= 6:
            slots += 1
        return slots

    def mission_progress_for_key(self, key):
        mapping = {
            "clicks": self.state.stats["total_clicks"],
            "money": self.state.stats["money_earned"],
            "goobers": (
                self.state.stats["gold_clicked"] + self.state.stats["angry_clicked"] +
                self.state.stats["tiny_clicked"] + self.state.stats["giant_clicked"] +
                self.state.stats["frozen_clicked"] + self.state.stats["bomb_clicked"] +
                self.state.stats["rgb_defeated"]
            ),
            "rare_seen": self.state.stats["rare_seen"],
            "boss": self.state.stats["boss_defeated"],
        }
        return int(mapping.get(key, 0))

    def make_mission(self):
        templates = [
            {"key": "clicks", "title": "Spam amigável", "desc": "Faça 60 cliques.", "target": 60 + self.state.prestige_level * 5, "money": 700, "coins": 2},
            {"key": "money", "title": "Cheirinho de lucro", "desc": "Ganhe dinheiro no total.", "target": 4000 + self.state.prestige_level * 600, "money": 1500, "coins": 3},
            {"key": "goobers", "title": "Goober patrol", "desc": "Clique goobers especiais.", "target": 5 + self.state.prestige_level, "money": 2000, "coins": 4},
            {"key": "rare_seen", "title": "Olho clínico", "desc": "Veja goobers raros aparecerem.", "target": 6 + self.state.prestige_level, "money": 1800, "coins": 2},
            {"key": "boss", "title": "Caça ao boss", "desc": "Derrote 1 boss.", "target": 1, "money": 5000, "coins": 6},
            {"key": "clicks", "title": "Maratona", "desc": "Faça uma sequência longa de cliques.", "target": 140 + self.state.prestige_level * 10, "money": 2600, "coins": 4},
            {"key": "money", "title": "Boom de caixa", "desc": "Ganhe um grande valor em dinheiro.", "target": 12000 + self.state.prestige_level * 1000, "money": 4500, "coins": 5},
            {"key": "goobers", "title": "Caçadora variada", "desc": "Clique vários especiais em uma run.", "target": 10 + self.state.prestige_level * 2, "money": 3200, "coins": 4},
            {"key": "rare_seen", "title": "Radar místico", "desc": "Encontre muitos raros.", "target": 12 + self.state.prestige_level * 2, "money": 3800, "coins": 4},
            {"key": "money", "title": "Economia girando", "desc": "Faça a run render alto.", "target": 25000 + self.state.prestige_level * 1500, "money": 7000, "coins": 6},
            {"key": "clicks", "title": "Dedinho turbo", "desc": "Faça muitos cliques rapidamente.", "target": 220 + self.state.prestige_level * 12, "money": 4200, "coins": 5},
            {"key": "goobers", "title": "Colecionadora", "desc": "Clique muitos goobers especiais.", "target": 18 + self.state.prestige_level * 2, "money": 5200, "coins": 6},
            {"key": "money", "title": "Fortuna poopy", "desc": "Ganhe muito dinheiro no total.", "target": 50000 + self.state.prestige_level * 2200, "money": 9000, "coins": 7},
            {"key": "rare_seen", "title": "Visão de raio-x", "desc": "Veja raros sem parar.", "target": 18 + self.state.prestige_level * 2, "money": 5600, "coins": 5},
            {"key": "boss", "title": "Linha de frente", "desc": "Derrote 2 bosses.", "target": 2, "money": 12000, "coins": 8},
            {"key": "clicks", "title": "Ritmo perfeito", "desc": "Mantenha a mão quente por bastante tempo.", "target": 320 + self.state.prestige_level * 14, "money": 6800, "coins": 6},
            {"key": "money", "title": "Mercado goober", "desc": "Ganhe muito dinheiro numa run avançada.", "target": 90000 + self.state.prestige_level * 3000, "money": 13000, "coins": 9},
        ]
        chosen = random.choice(templates)
        target = int(chosen["target"])
        start_value = self.mission_progress_for_key(chosen["key"])
        mult = 1.2 if self.state.mission_radar_bought else 1.0
        reward_money = int(chosen["money"] * mult)
        reward_coins = chosen["coins"] + (1 if self.state.mission_radar_bought else 0)
        return {
            "key": chosen["key"],
            "title": chosen["title"],
            "description": chosen["desc"],
            "target": target,
            "progress": 0,
            "start_value": start_value,
            "reward_type": "mixed",
            "reward_money": reward_money,
            "reward_coins": reward_coins,
            "reward_text": f"${format_number(reward_money)} + {reward_coins} gc",
            "claimed": False,
        }

    def ensure_missions(self, force=False):
        wanted = self.get_max_mission_slots()
        if force or not self.state.mission_state.get("slots"):
            self.state.mission_state["slots"] = [self.make_mission() for _ in range(wanted)]
        else:
            while len(self.state.mission_state["slots"]) < wanted:
                self.state.mission_state["slots"].append(self.make_mission())
        self.update_missions()

    def update_missions(self):
        slots = self.state.mission_state.get("slots", [])
        if not isinstance(slots, list):
            self.state.mission_state["slots"] = []
            slots = self.state.mission_state["slots"]

        completed_count = 0

        for mission in slots:
            if mission.get("claimed", False):
                continue

            key = mission.get("key", "")
            start_value = int(mission.get("start_value", 0))
            current_value = self.mission_progress_for_key(key)
            progress = max(0, current_value - start_value)
            mission["progress"] = min(progress, int(mission.get("target", progress)))

            if mission["progress"] >= int(mission.get("target", 0)):
                reward_money = int(mission.get("reward_money", 0))
                reward_coins = int(mission.get("reward_coins", 0))

                if reward_money > 0:
                    self.state.count += reward_money
                    self.state.lifetime_money += reward_money
                    self.state.stats["money_earned"] += reward_money
                if reward_coins > 0:
                    self.state.goober_coins += reward_coins

                self.show_floating_text(
                    f"Missão completa! +${format_number(reward_money)} +{reward_coins} gc",
                    QPoint(self.play_area.width() // 2, 90),
                    "#a5ff90"
                )
                mission["claimed"] = True
                completed_count += 1
                self.sound.play("mission_done")

        if completed_count:
            self.state.mission_state["completed_total"] = (
                self.state.mission_state.get("completed_total", 0) + completed_count
            )
            self.state.mission_state["slots"] = [m for m in slots if not m.get("claimed")]
            self.ensure_missions()
            self.save()

        self.update_ui()

    def _flash_label(self, label, color="#4CAF50"):
        orig = self._orig_stylesheets.get(label, label.styleSheet())
        label.setStyleSheet(f"color: {color}; font-weight: bold;")
        QTimer.singleShot(150, lambda l=label, o=orig: l.setStyleSheet(o))

    def click(self):
        event_mult = self.current_event_click_mult()
        frenzy_mult = 2.0 if self._skill_frenzy_active else 1.0
        click_gain = int(self.state.get_click_value(event_mult) * self.state.combo_multiplier * frenzy_mult)
        self.state.count += click_gain
        self.state.lifetime_money += click_gain
        self.state.stats["total_clicks"] += 1
        self.state.stats["money_earned"] += click_gain
        coin_bonus = int(self.current_event_modifier("click_coin_bonus", 0))
        if coin_bonus > 0 and self.state.secret_shop_unlocked:
            self.state.goober_coins += coin_bonus
            self.show_floating_text(f"+{coin_bonus} gc", QPoint(self.click_btn.x(), self.click_btn.y() - 12), "#ffe082")
            self.sound.play("coin")
        if self.active_event == "sticky":
            self.click_btn.move(
                self.click_btn.x() + random.randint(-5, 5),
                self.click_btn.y() + random.randint(-3, 3)
            )
            self.keep_click_button_inside()

        self.add_combo()

        self.sound.play("click_combo" if self.state.combo_count >= 5 else "click")
        self._flash_label(self.label)
        self._last_clicks.append(time.time())
        self.update_ui()
        self.move_click_button_randomly()
        self._click_tick += 1
        if self.state.settings.get("show_particles", True):
            x = self.click_btn.x() + self.click_btn.width() // 2
            y = self.click_btn.y() + self.click_btn.height() // 2
            burst(self.play_area, x, y, 2, ["#8bd3ff", "#ffffff"])

        self.click_spawn_counter += 1
        if self.click_spawn_counter >= CLICK_SPAWN_THRESHOLD:
            self.click_spawn_counter = 0
            self.try_spawn_goober()

        self._check_achievements()
        self.update_missions()

    def auto_loop(self):
        gain = self.state.get_auto_value(self.current_event_auto_mult())
        if gain > 0:
            self.sound.play("auto_tick")
        self.state.count += gain
        self.state.lifetime_money += gain
        self.state.stats["money_earned"] += gain
        self._flash_label(self.auto_label, "#2196F3")
        self.update_ui()
        self._check_achievements()
        self.update_missions()

    def _check_recenter(self):
        if self._click_tick == self._last_click_tick:
            self.center_click_button()
        self._last_click_tick = self._click_tick

    def do_prestige(self):
        cost = self.state.get_prestige_cost()
        if self.state.count < cost:
            return

        click_bonus = int((self.state.get_prestige_bonus_click() - 1) * 100)
        auto_bonus = int((self.state.get_prestige_bonus_auto() - 1) * 100)
        next_level = self.state.prestige_level + 1

        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Prestígio")
        dialog.resize(380, 260)
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)

        essence_est = self.state.calculate_prestige_gain()
        msg = QLabel(
            f"Tem certeza que deseja prestigiar?\n\n"
            f"Custo: ${format_number(cost)}\n"
            f"Nível atual: {self.state.prestige_level}\n"
            f"Próximo nível: {next_level}\n"
            f"Bônus de clique: +{click_bonus}%\n"
            f"Bônus de auto: +{auto_bonus}%\n"
            f"Essência estimada: +{essence_est}\n\n"
            "Seu dinheiro, upgrades e loja secreta\n"
            "serão resetados!"
        )
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet(f"color: {theme['text']}; font-size: 11pt;")
        layout.addWidget(msg)

        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("✨ Prestigiar!")
        yes_btn.setMinimumHeight(38)
        yes_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; }}
        """)
        yes_btn.clicked.connect(dialog.accept)
        no_btn = QPushButton("cancelar")
        no_btn.setMinimumHeight(38)
        no_btn.setStyleSheet(f"""
            QPushButton {{ background: rgba(255,255,255,12); color: {theme['text']};
                border: 1px solid {theme['accent']}; border-radius: 8px; }}
        """)
        no_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        essence_before = self.state.poopy_essence
        self.state.prestige()
        essence_gain = self.state.poopy_essence - essence_before
        for g in self.goobers:
            g.deleteLater()
        self.goobers.clear()
        self.click_spawn_counter = 0
        self.update_ui()
        self.update_shop_buttons()
        self.update_secret_shop_buttons()
        self._check_achievements()
        self.save()
        self.sound.play("prestige")
        if essence_gain > 0:
            self.sound.play("prestige_essence")
            self.show_floating_text(
                f"+{essence_gain} essence!",
                QPoint(self.play_area.width() // 2, 40),
                "#ff9de6"
            )
        burst(self.play_area, self.play_area.width() // 2, self.play_area.height() // 2, 20, ["#ff9de6", "#c9b1ff", "#8bd3ff"], enabled=self.state.settings.get("show_particles", True))
        QTimer.singleShot(200, lambda: [self.try_spawn_goober() for _ in range(2)])

    def _check_achievements(self):
        new_achs = self.state.check_new_achievements()
        if new_achs:
            self.sound.play("achievement")
            self._show_achievement_notification(new_achs)
            burst(self.play_area, self.play_area.width() // 2, self.play_area.height() // 2, 16,
                  ["#ffd700", "#ff6b6b", "#6bcb77"], enabled=self.state.settings.get("show_particles", True))

    def _show_achievement_notification(self, achievements):
        names = "\n".join(f"- {a[1]}: {a[2]}" for a in achievements)
        plural = "Conquista" if len(achievements) == 1 else "Conquistas"
        msg = f"{plural} desbloqueada(s)!\n\n{names}"

        dialog = QDialog(self)
        dialog.setWindowTitle("🏆 Conquista!")
        dialog.resize(320, 200)
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)

        label = QLabel(msg)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {theme['text']}; font-size: 12pt;")
        layout.addWidget(label)

        ok_btn = QPushButton("🎉 Legal!")
        ok_btn.setMinimumHeight(36)
        ok_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; }}
        """)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.open()

    def save(self):
        self.state.last_saved_at = time.time()
        save_load.save_game(self.state)

    def load(self):
        save_load.load_game(self.state)
        self.ensure_missions()
        self.refresh_all()
        self.apply_offline_earnings()
        self.apply_ui_theme()
        self.sound.apply_settings(self.state.settings)
        if not self.state.settings.get("onboarding_done", False):
            QTimer.singleShot(200, self._show_onboarding)

    def apply_offline_earnings(self):
        if not self.state.settings.get("offline_progress", True):
            return
        elapsed = time.time() - self.state.last_saved_at
        if elapsed <= 0:
            return
        cap = self.state.get_offline_hours_cap() * 3600
        elapsed = min(elapsed, cap)
        auto_val = self.state.get_auto_value()
        if auto_val <= 0:
            return
        gain = int(auto_val * elapsed)
        if gain <= 0:
            return
        self.state.count += gain
        self.state.lifetime_money += gain
        self.state.stats["money_earned"] += gain
        self.state.stats["offline_earned_total"] = self.state.stats.get("offline_earned_total", 0) + gain
        self.state.stats["offline_seconds"] = self.state.stats.get("offline_seconds", 0) + int(elapsed)
        hours = elapsed / 3600.0
        self.sound.play("offline_earnings")
        self.show_floating_text(
            f"+${format_number(gain)} offline",
            QPoint(self.play_area.width() // 2, 60),
            "#9cf6ff"
        )
        QTimer.singleShot(200, lambda g=gain, h=hours: self._show_offline_dialog(g, h))

    def _show_offline_dialog(self, gain, hours):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ganhos offline")
        dialog.resize(440, 200)
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Ganhos offline")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {theme['text']}; font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        body = QLabel(
            f"Enquanto você estava fora, o auto click trabalhou\n"
            f"por {hours:.2f}h.\n\n"
            f"Você ganhou ${format_number(gain)} no total."
        )
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setStyleSheet(f"color: {theme['text']}; font-size: 11pt;")
        layout.addWidget(body)

        ok_btn = QPushButton("Fechar")
        ok_btn.setMinimumHeight(38)
        ok_btn.setStyleSheet(f"""
            QPushButton {{ background: {theme['accent']}; color: {theme['bg']};
                font-weight: bold; border: none; border-radius: 8px; }}
        """)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.exec()

    def update_shop_buttons(self):
        try:
            if self.upgrade_btn is not None and hasattr(self, 'upgrade_bar'):
                level = self.state.upgrade_level
                cost = self.state.get_click_upgrade_cost()
                self.upgrade_bar.setValue(level)
                next_value = 2 ** (level + 1)
                self.upgrade_btn.setText(f"upgrade de click  |  {format_number(next_value)}x")
                self.upgrade_btn.setEnabled(self.state.count >= cost)
                self.upgrade_cost_label.setText(f"${format_number(cost)}")

            if self.auto_btn is not None and hasattr(self, 'auto_bar'):
                level = self.state.auto_level
                cost = self.state.get_auto_upgrade_cost()
                self.auto_bar.setValue(level)
                next_value = 2 ** level
                self.auto_btn.setText(f"auto click  |  {format_number(next_value)}/s")
                self.auto_btn.setEnabled(self.state.count >= cost)
                self.auto_cost_label.setText(f"${format_number(cost)}")
            if hasattr(self, 'upgrade_bar'):
                self._update_shop_bar_colors()
        except RuntimeError:
            pass

    def _update_shop_bar_colors(self):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        accent = theme['accent']
        for bar in (self.upgrade_bar, self.auto_bar):
            if bar is not None:
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid {accent}; border-radius: 5px;
                        background: {theme['panel']};
                    }}
                    QProgressBar::chunk {{
                        background: {accent}; border-radius: 4px;
                    }}
                """)

    def buy_upgrade(self):
        cost = self.state.get_click_upgrade_cost()
        if self.state.count >= cost:
            self.state.count -= cost
            self.state.upgrade_level += 1
            self.sound.play("upgrade")
            self.refresh_all()
            self._check_achievements()
            burst(self.play_area, self.click_btn.x() + 55, self.click_btn.y() + 24, 6,
                  ["#4CAF50", "#81C784", "#A5D6A7"],
                  enabled=self.state.settings.get("show_particles", True))

    def buy_auto(self):
        cost = self.state.get_auto_upgrade_cost()
        if self.state.count >= cost:
            self.state.count -= cost
            self.state.auto_level += 1
            self.sound.play("upgrade")
            self.refresh_all()
            self._check_achievements()

    def _refresh_theme_buttons(self):
        for tid, btn in self.theme_shop_buttons.items():
            tdata = UI_THEMES[tid]
            name, cost = tdata["name"], tdata["cost"]
            if tid == self.state.selected_ui_theme:
                btn.setText(f"{name} ✓ equipado")
                btn.setEnabled(False)
            elif tid in self.state.owned_ui_themes:
                btn.setText(f"{name} — equipar")
                btn.setEnabled(True)
            else:
                btn.setText(f"{name} — {cost} gc")
                btn.setEnabled(self.state.goober_coins >= cost)

    def _handle_theme_click(self, tid):
        tdata = UI_THEMES[tid]
        cost = tdata["cost"]
        if tid in self.state.owned_ui_themes:
            self.state.selected_ui_theme = tid
        elif self.state.goober_coins >= cost:
            self.state.goober_coins -= cost
            self.state.owned_ui_themes.append(tid)
            self.state.selected_ui_theme = tid
        else:
            return
        self.apply_ui_theme()
        for d in self.findChildren(QDialog):
            try:
                self._apply_theme_dict(tdata, widget=d)
            except RuntimeError:
                pass
        self._refresh_theme_buttons()
        self.update_ui()
        self.save()

    def _compras_closed(self):
        self._goober_tab_info_label = None
        self._goober_tab_desc_label = None
        self.secret_buttons = {}
        self.theme_shop_buttons = {}
    def _update_shop_btn_text(self, data, item, bought):
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        w, name_lbl, desc_lbl = data["widget"], data["name"], data["desc"]
        enabled = not bought and self.state.goober_coins >= item["cost"]
        w.setEnabled(enabled)
        if enabled:
            w.setStyleSheet(f"background: {theme['accent']}; border-radius: 8px;")
            name_lbl.setStyleSheet(f"color: {theme['bg']}; font-weight: bold; font-size: 10pt; background: transparent;")
            desc_lbl.setStyleSheet(f"color: {theme['bg']}aa; font-size: 8pt; background: transparent;")
        else:
            w.setStyleSheet(f"background: rgba(255,255,255,10); border-radius: 8px;")
            name_lbl.setStyleSheet(f"color: {theme['accent2']}; font-weight: bold; font-size: 10pt; background: transparent;")
            desc_lbl.setStyleSheet(f"color: {theme['accent2']}88; font-size: 8pt; background: transparent;")
        name_lbl.setText(f"{item['name']} — {item['cost']} gc")
        if bought:
            desc_lbl.setText("COMPRADO ✓")
        else:
            desc_lbl.setText(item['desc'])

    def update_secret_shop_buttons(self):
        if not self.secret_buttons:
            return
        for item in SHOP_ITEM_DEFS:
            key = item["key"]
            data = self.secret_buttons.get(key)
            if data is None:
                continue
            bought = getattr(self.state, item["attr"])
            self._update_shop_btn_text(data, item, bought)

    def buy_shop_item(self, key):
        for item in SHOP_ITEM_DEFS:
            if item["key"] != key:
                continue
            if getattr(self.state, item["attr"]):
                return
            if self.state.goober_coins < item["cost"]:
                return
            self.state.goober_coins -= item["cost"]
            setattr(self.state, item["attr"], True)
            if key == "charm":
                for goober in self.goobers:
                    goober.behavior_timer.start(random.randint(3000, 5000))
            self.sound.play("buy")
            self.update_secret_shop_buttons()
            self.update_ui()
            self._check_achievements()
            self.save()
            return

    def _use_skill(self, key):
        if self.state.skill_cooldowns.get(key, 0) > 0:
            return
        if key == "cleanse":
            total = 0
            for g in list(self.goobers):
                if g.isVisible():
                    if g.goober_type in EXTRA_GOOBER_DATA or g.goober_type in ("boss", "rgb"):
                        g.give_special_rewards()
                    else:
                        total += 1
                g.deleteLater()
            self.goobers.clear()
            self.boss_active = False
            self.show_floating_text(f"Limpeza! +{total} goobers eliminados",
                                    QPoint(self.play_area.width() // 2, 100), "#ff6b6b")
            self.sound.play("clear_event")
        elif key == "frenzy":
            self._skill_frenzy_active = True
            self._skill_frenzy_timer = QTimer(self)
            self._skill_frenzy_timer.setSingleShot(True)
            self._skill_frenzy_timer.timeout.connect(self._end_frenzy)
            self._skill_frenzy_timer.start(8000)
            self.show_floating_text("Frenesi! 2x clique por 8s",
                                    QPoint(self.play_area.width() // 2, 80), "#ffd700")
            self.sound.play("event_start")
        elif key == "skill_shield":
            self._skill_shield_active = True
            if self.active_event:
                self.clear_event()
            QTimer.singleShot(10000, self._end_shield)
            self.show_floating_text("Escudo ativo! 10s sem eventos",
                                    QPoint(self.play_area.width() // 2, 80), "#8bd3ff")
            self.sound.play("event_start")
        elif key == "coinburst":
            self._skill_coinburst_active = True
            QTimer.singleShot(12000, self._end_coinburst)
            self.show_floating_text("Explosão! 3x moedas por 12s",
                                    QPoint(self.play_area.width() // 2, 80), "#ffd166")
            self.sound.play("event_start")
        self.state.skill_cooldowns[key] = next(s["cooldown"] for s in ACTIVE_SKILLS if s["key"] == key)
        self.update_ui()

    def _end_frenzy(self):
        self._skill_frenzy_active = False
        self.show_floating_text("Frenesi acabou", QPoint(self.play_area.width() // 2, 80), "#ff6b6b")

    def _end_shield(self):
        self._skill_shield_active = False
        self.show_floating_text("Escudo caiu", QPoint(self.play_area.width() // 2, 80), "#8bd3ff")

    def _end_coinburst(self):
        self._skill_coinburst_active = False
        self.show_floating_text("Explosão acabou", QPoint(self.play_area.width() // 2, 80), "#ffd166")

    def _check_updates(self):
        try:
            req = Request(
                f"https://api.github.com/repos/{REPO}/releases/latest",
                headers={"User-Agent": "poopy-clicker", "Accept": "application/vnd.github.v3+json"},
            )
            resp = urlopen(req, timeout=5)
            data = json.loads(resp.read().decode("utf-8"))
            latest_tag = data.get("tag_name", "")
            if not latest_tag or not latest_tag.startswith("v"):
                return
            latest_ver = latest_tag.lstrip("v")
            current_ver = VERSION
            if not self._is_newer(latest_ver, current_ver):
                return
            body = data.get("body", "")
            assets = data.get("assets", [])
            setup_asset = next(
                (a for a in assets if "Setup" in a.get("name", "")),
                None,
            )
            exe_asset = next(
                (a for a in assets if a.get("name", "").endswith(".exe") and "Setup" not in a.get("name", "")),
                None,
            )
            self._show_update_dialog(latest_tag, body, setup_asset, exe_asset)
        except Exception:
            pass

    @staticmethod
    def _is_newer(latest, current):
        try:
            lp = tuple(int(x) for x in latest.split("."))
            cp = tuple(int(x) for x in current.split("."))
            return lp > cp
        except (ValueError, TypeError):
            return False

    def _show_update_dialog(self, tag, body, setup_asset, exe_asset):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Atualização disponível — {tag}")
        dialog.resize(400, 320)
        theme = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
        dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)

        title = QLabel(f'Nova versão <b>{tag}</b> disponível!')
        title.setWordWrap(True)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        changelog = QLabel(body.replace("\n", "<br>"))
        changelog.setWordWrap(True)
        changelog_font = QFont()
        changelog_font.setPointSize(9)
        changelog.setFont(changelog_font)
        scroll = QScrollArea()
        scroll.setWidget(changelog)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: {theme['panel']}; border: 1px solid {theme['accent']}; border-radius: 8px;")
        layout.addWidget(scroll, 1)

        btn_layout = QHBoxLayout()

        later_btn = QPushButton("Agora não")
        later_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        later_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(later_btn)

        is_frozen = getattr(sys, "frozen", False)
        if is_frozen:
            dl_url = None
            dl_name = None
            if setup_asset:
                dl_url = setup_asset.get("browser_download_url")
                dl_name = "Baixar instalador"
            elif exe_asset:
                dl_url = exe_asset.get("browser_download_url")
                dl_name = "Baixar .exe"
            if dl_url:
                dl_btn = QPushButton(dl_name)
                dl_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                dl_btn.clicked.connect(lambda: webbrowser.open(dl_url))
                btn_layout.addWidget(dl_btn)
        else:
            gh_btn = QPushButton("Abrir release no GitHub")
            gh_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            gh_btn.clicked.connect(lambda: webbrowser.open(f"https://github.com/{REPO}/releases/tag/{tag}"))
            btn_layout.addWidget(gh_btn)

        layout.addLayout(btn_layout)
        dialog.exec()

    def _tick_skill_cooldowns(self):
        changed = False
        for k in self.state.skill_cooldowns:
            if self.state.skill_cooldowns[k] > 0:
                self.state.skill_cooldowns[k] -= 1
                changed = True
        if changed:
            self.update_ui()
