import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QTabWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie, QPixmap, QPainter, QColor, QGuiApplication

from .constants import (
    ASSET_PATH, GOOBER_INFO, EXTRA_GOOBER_DATA, RARITY_INFO,
    EVENT_INFO, EVENT_RARITY_INFO, COLLECTION_REWARDS,
    UI_THEMES, format_number,
)


def _theme_for(state):
    return UI_THEMES.get(state.selected_ui_theme, UI_THEMES["default"])


def _make_row_bg(i):
    return f"rgba(255,255,255,{6 if i % 2 == 0 else 12})"


def open_bestiary(parent, state):
    theme = _theme_for(state)

    dialog = QDialog(parent)
    dialog.setWindowTitle("Gooberário")
    screen = QGuiApplication.primaryScreen()
    geo = screen.availableGeometry() if screen else None
    if geo:
        dialog.resize(int(geo.width() * 0.32), int(geo.height() * 0.52))
    else:
        dialog.resize(520, 420)
    dialog.setStyleSheet(f"background: {theme['bg']}; color: {theme['text']};")

    outer = QVBoxLayout(dialog)
    outer.setContentsMargins(14, 14, 14, 14)
    outer.setSpacing(10)

    title = QLabel("📚 Gooberário")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet(f"font-size: 15pt; font-weight: bold; color: {theme['text']};")
    outer.addWidget(title)

    tabs = QTabWidget()
    tabs.setDocumentMode(True)
    tabs.setStyleSheet(f"""
        QTabWidget::pane {{ background: transparent; border: none; }}
        QTabBar::tab {{ background: {theme['bg']}; color: {theme['text']};
            padding: 8px 16px; border: none; font-size: 10pt; }}
        QTabBar::tab:selected {{ background: {theme['accent']}; color: {theme['bg']}; font-weight: bold; }}
        QTabBar::tab:hover {{ background: {theme['panel']}; }}
    """)

    # ── Goobers Tab ──────────────────────────────────────────────
    goober_desc = {
        "normal": "O padrão da run. Quase sempre inofensivo.",
        "gold": "Raro e valioso. Ótimo para a economia.",
        "angry": "Agressivo. Acelera e pressiona o botão.",
        "tiny": "Pequeno e rápido. Fácil de perder no caos.",
        "giant": "Grande e recompensador. Ocupa espaço na arena.",
        "frozen": "Traz uma pausa no ritmo. Deixa o botão confortável.",
        "bomb": "Recompensa boa, mas explode em caos na arena.",
        "rgb": "Mítico. Aguenta vários cliques e muda de cor.",
        "boss": "Chefe com barra de vida e muito loot.",
        "slime": "Escorrega e acelera o dinheiro sem assustar.",
        "shadow": "Difícil de ler e rápido de reagir.",
        "candy": "Doce e amigável. Um respiro na run.",
        "crystal": "Brilha e paga bem. Sempre bem-vindo.",
        "storm": "Instável. Pode puxar um evento ao estourar.",
        "glitch": "Visual quebrado e ótima recompensa.",
        "toxic": "Efeito ruim leve, mas compensa no farm.",
        "magnet": "Puxa o botão ao centro por alguns segundos.",
        "sleepy": "Lento e útil para acalmar o fluxo.",
        "speedy": "Corre demais. Testa reflexo puro.",
        "royal": "Recompensa alta. Gosto de jackpot.",
        "plasma": "Explosivo e excelente para dinheiro rápido.",
        "stone": "Pesado e previsível. Ocupa espaço.",
        "ghost": "Escapa da leitura visual. Teleporta.",
        "lava": "Traz tensão. Cobra atenção.",
        "clockwork": "Mexe com o ritmo da run.",
        "neon": "Visual forte e clique satisfatório.",
        "pirate": "Spawn de loot e clima de tesouro.",
        "angel": "Raríssimo. Ajuda a run.",
        "devil": "Muito retorno, muito caos.",
        "moss": "Calmo e natural. Ótimo para runs suaves.",
        "prism": "Mítico. Mais de um clique, explosão de recompensa.",
        "voidling": "Janela rara. Muda a vibe da tela.",
        "chef": "Descanso tático para o combo respirar.",
        "samurai": "Rápido e recompensador. Duelo curto.",
        "arcade": "Minigame. Paga bem em moedas.",
        "bubble": "Leve. Ótimo quando a tela está cheia.",
        "crown": "Realeza de endgame. Muito valor.",
        "fairy": "Pequena, rápida e traz sorte.",
    }

    goober_content = QWidget()
    goober_content.setStyleSheet("background: transparent;")
    goober_lay = QVBoxLayout(goober_content)
    goober_lay.setContentsMargins(0, 0, 0, 0)
    goober_lay.setSpacing(2)

    catalog = [
        ("normal", goober_desc["normal"], None, 1.0, False),
        ("gold", goober_desc["gold"], QColor(255, 215, 70, 150), 1.12, False),
        ("angry", goober_desc["angry"], QColor(255, 80, 80, 150), 1.0, False),
        ("tiny", goober_desc["tiny"], QColor(120, 255, 255, 140), 0.74, False),
        ("giant", goober_desc["giant"], QColor(190, 120, 255, 145), 1.42, False),
        ("frozen", goober_desc["frozen"], QColor(120, 220, 255, 155), 1.05, False),
        ("bomb", goober_desc["bomb"], QColor(255, 120, 40, 155), 1.08, False),
        ("rgb", goober_desc["rgb"], None, 1.45, True),
        ("boss", goober_desc["boss"], QColor(255, 180, 80, 170), 1.95, False),
    ]
    for key, data in EXTRA_GOOBER_DATA.items():
        tint = QColor(*data["color"]) if data.get("color") else None
        catalog.append((
            key,
            goober_desc.get(key, data.get("desc", "Novo goober.")),
            tint,
            data.get("size_multiplier", 1.0),
            False,
        ))

    for idx, (goober_key, desc, tint, size_mult, rgb_flag) in enumerate(catalog):
        counts = state.bestiary_counts.get(goober_key, {"seen": 0, "clicked": 0})
        info = GOOBER_INFO.get(goober_key, GOOBER_INFO["normal"])
        rarity = info["rarity"]
        rarity_color = RARITY_INFO[rarity]["color"]

        row = QFrame()
        row.setFrameShape(QFrame.Shape.NoFrame)
        row.setStyleSheet(f"QFrame {{ background: {_make_row_bg(idx)}; border-radius: 6px; }}")

        rl = QHBoxLayout(row)
        rl.setContentsMargins(8, 6, 8, 6)
        rl.setSpacing(10)

        pix_label = QLabel()
        pix_label.setFixedSize(48, 48)
        gif_path = os.path.join(ASSET_PATH, "Goober_idle.webp")
        movie = QMovie(gif_path)
        movie.start()
        movie.jumpToFrame(0)
        pix = movie.currentPixmap()
        if pix.isNull():
            pix = QPixmap(48, 48)
            pix.fill(Qt.GlobalColor.transparent)
        ts = int(40 * size_mult)
        pix = pix.scaled(QSize(ts, ts), Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
        if rgb_flag:
            tint = QColor.fromHsv(300, 255, 255, 160)
        if tint is not None:
            rp = QPixmap(pix.size())
            rp.fill(Qt.GlobalColor.transparent)
            p = QPainter(rp)
            p.drawPixmap(0, 0, pix)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            p.fillRect(rp.rect(), tint)
            p.end()
            pix = rp
        pix_label.setPixmap(pix)
        pix_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(pix_label)

        rarity_dot = QLabel("●")
        rarity_dot.setStyleSheet(f"color: {rarity_color}; font-size: 10pt;")
        rarity_dot.setFixedWidth(14)
        rl.addWidget(rarity_dot)

        vl = QVBoxLayout()
        vl.setSpacing(1)
        nl = QLabel(info["name"])
        nl.setStyleSheet(f"font-weight: bold; font-size: 10pt; color: {theme['text']};")
        vl.addWidget(nl)
        dl = QLabel(desc)
        dl.setWordWrap(True)
        dl.setStyleSheet(f"font-size: 8pt; color: {theme['accent2']};")
        vl.addWidget(dl)
        rl.addLayout(vl, 1)

        extra_parts = [
            f"visto {counts.get('seen', 0)}x",
            f"clicado {counts.get('clicked', 0)}x",
        ]
        if goober_key == "rgb":
            extra_parts.append("5 hits")
        elif goober_key == "boss":
            extra_parts.append("HP bar")
        elif goober_key in EXTRA_GOOBER_DATA and EXTRA_GOOBER_DATA[goober_key].get("event_on_click"):
            extra_parts.append("evento")
        st = QLabel(" | ".join(extra_parts))
        st.setStyleSheet(f"font-size: 8pt; color: {theme['text']}88;")
        st.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(st)

        goober_lay.addWidget(row)

    goober_lay.addStretch()
    goober_scroll = QScrollArea()
    goober_scroll.setWidgetResizable(True)
    goober_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    goober_scroll.setWidget(goober_content)
    tabs.addTab(goober_scroll, "👾 Goobers")

    # ── Events Tab ────────────────────────────────────────────────
    event_desc = {
        "double_click": "Dobra o valor do clique.",
        "double_auto": "Turbina o auto click.",
        "big_button": "Botão maior e mais fácil.",
        "tiny_button": "Botão menor e mais exigente.",
        "chaos": "Mais deslocamento e imprevisibilidade.",
        "calm": "Respira e recupera controle.",
        "invert_colors": "Cores invertidas temporárias.",
        "invert_move": "Movimento espelhado.",
        "gravity": "Botão puxado para baixo.",
        "sticky": "Botão quase trava.",
        "frenzy": "Mais goobers na tela.",
        "mouse_flee": "Botão foge do cursor.",
        "blink": "Teletransportes curtos.",
        "storm_mode": "Vento e gravidade em caos.",
        "glitch_flip": "Movimento e visual quebrados.",
        "center_pull": "Botão volta ao centro.",
        "hyper_button": "Botão maior e mais arisco.",
        "heatwave": "Mais fuga, vibração e pressão.",
        "time_dilation": "Velocidade reduzida.",
        "treasure_tide": "Festival de moedas.",
        "blessing": "Mais valor, menos caos.",
        "hellrush": "Poder alto com descontrole.",
        "void_window": "Janela rara com chance melhor.",
        "snack_break": "Combo cai mais devagar.",
        "jackpot_mode": "Especialistas pagam mais.",
        "lucky_wave": "Sorte da run aumenta.",
        "coin_rain": "Cliques viram moedas.",
        "essence_bloom": "Essence extra em especiais.",
        "boss_hour": "Mais chances de boss.",
        "moonlight": "Tela suave e movimentos amigáveis.",
        "mirror_world": "Espelho com mais controle.",
        "safe_zone": "Menos pressão dos goobers.",
        "orbital": "Botão orbita o centro.",
        "overclock": "Mais auto e mais spawns.",
        "party_mode": "Mais raros e mais moedas.",
    }

    events_scroll = QScrollArea()
    events_scroll.setWidgetResizable(True)
    events_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    events_content = QWidget()
    events_content.setStyleSheet("background: transparent;")
    events_lay = QVBoxLayout(events_content)
    events_lay.setContentsMargins(0, 0, 0, 0)
    events_lay.setSpacing(2)

    for idx, event_key in enumerate(EVENT_INFO.keys()):
        info = EVENT_INFO[event_key]
        rar_info = EVENT_RARITY_INFO[info["rarity"]]

        row = QFrame()
        row.setFrameShape(QFrame.Shape.NoFrame)
        row.setStyleSheet(f"QFrame {{ background: {_make_row_bg(idx)}; border-radius: 6px; }}")

        rl = QHBoxLayout(row)
        rl.setContentsMargins(10, 6, 10, 6)
        rl.setSpacing(10)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {rar_info['color']}; font-size: 12pt;")
        dot.setFixedWidth(16)
        rl.addWidget(dot)

        vl = QVBoxLayout()
        vl.setSpacing(1)
        en = QLabel(info["name"])
        en.setStyleSheet(f"font-weight: bold; font-size: 10pt; color: {theme['text']};")
        vl.addWidget(en)
        ed = QLabel(event_desc.get(event_key, info["desc"]))
        ed.setStyleSheet(f"font-size: 8pt; color: {theme['accent2']};")
        vl.addWidget(ed)
        rl.addLayout(vl, 1)

        mods = []
        for k in ("click_mult", "auto_mult", "spawn_bonus", "combo_grace", "panic_reduce"):
            v = info.get(k)
            if v and v != 1.0:
                mods.append(f"{k.replace('_', ' ')} x{v}")
        if mods:
            ml = QLabel(" | ".join(mods))
            ml.setStyleSheet(f"font-size: 7pt; color: {theme['accent']};")
            ml.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            rl.addWidget(ml)

        events_lay.addWidget(row)

    events_lay.addStretch()
    events_scroll.setWidget(events_content)
    tabs.addTab(events_scroll, "🎲 Eventos")

    # ── Collection Tab ────────────────────────────────────────────
    collection_tab = QWidget()
    collection_tab.setStyleSheet("background: transparent;")
    cl = QVBoxLayout(collection_tab)
    cl.setContentsMargins(0, 0, 0, 0)
    cl.setSpacing(2)

    claimed = state.stats.get("collection_rewards_claimed", [])
    for idx, reward in enumerate(COLLECTION_REWARDS):
        unlocked = reward["id"] in claimed
        row = QFrame()
        row.setFrameShape(QFrame.Shape.NoFrame)
        row.setStyleSheet(f"QFrame {{ background: {_make_row_bg(idx)}; border-radius: 6px; }}")

        rl = QHBoxLayout(row)
        rl.setContentsMargins(10, 8, 10, 8)
        rl.setSpacing(10)

        icon = QLabel("✅" if unlocked else "🔒")
        icon.setStyleSheet("font-size: 12pt;")
        rl.addWidget(icon)

        vl = QVBoxLayout()
        vl.setSpacing(1)
        rn = QLabel(reward["name"])
        rn.setStyleSheet(f"font-weight: bold; font-size: 10pt; color: {theme['text']};")
        vl.addWidget(rn)
        rd = QLabel(reward["desc"])
        rd.setWordWrap(True)
        rd.setStyleSheet(f"font-size: 8pt; color: {theme['accent2']};")
        vl.addWidget(rd)
        rl.addLayout(vl, 1)

        cl.addWidget(row)

    cl.addStretch()
    cs = QScrollArea()
    cs.setWidgetResizable(True)
    cs.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    cs.setWidget(collection_tab)
    tabs.addTab(cs, "🏆 Coleção")

    outer.addWidget(tabs)

    close_btn = QPushButton("fechar")
    close_btn.setMinimumHeight(36)
    close_btn.setStyleSheet(f"""
        QPushButton {{
            background: {theme['accent']}; color: {theme['bg']};
            font-weight: bold; border: none; border-radius: 8px;
        }}
    """)
    close_btn.clicked.connect(dialog.accept)
    outer.addWidget(close_btn)

    dialog.exec()
