import random
import os
import time
from PyQt6.QtWidgets import QLabel, QProgressBar
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve, QPoint
from PyQt6.QtGui import QMovie, QTransform, QColor, QPainter, QPixmap, QCursor

from .constants import ASSET_PATH, SECRET_SHOP_UNLOCK_CLICKS, COSMETIC_COLOR_CHANCE
from .constants import GOOBER_COLORS, GOOBER_INFO, EXTRA_GOOBER_DATA, RARITY_INFO
from .constants import format_number
from .particles import burst


class Goober(QLabel):
    def __init__(self, parent, game_window, state, goober_type="normal"):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.game_window = game_window
        self.state = state
        self.goober_type = goober_type
        self.anim_refs = []
        self.anim_state = "walk"
        self.push_cooldown = 0
        self._scared = False
        self._fleeing_off = False
        self._chasing = False
        self._move_cooldown = 0

        self.base_size = 96
        self.facing_left = False

        self.current_movie = None

        self.idle_movie = QMovie(os.path.join(ASSET_PATH, "Goober_idle.webp"))
        self.walk_movie = QMovie(os.path.join(ASSET_PATH, "Goober_run.webp"))
        self.scare_movie = QMovie(os.path.join(ASSET_PATH, "Goober_scare.webp"))
        self.panic_movie = QMovie(os.path.join(ASSET_PATH, "Goober_run_scare.webp"))

        self.idle_movie.frameChanged.connect(self._movie_frame_changed)
        self.walk_movie.frameChanged.connect(self._movie_frame_changed)
        self.scare_movie.frameChanged.connect(self._movie_frame_changed)
        self.panic_movie.frameChanged.connect(self._movie_frame_changed)

        self.color_tint = None
        self._frame_cache = {}
        self.rgb_hue = random.randint(0, 359)
        self.hit_points = 1
        self.max_hits = 1
        self.money_reward = 0
        self.coin_reward = 0
        self.essence_reward = 0
        self.click_progress_reward = 0
        self.speed_min = 1
        self.speed_max = 2
        self.size_multiplier = 1.0
        self.normal_push = 6
        self.panic_push = 28
        self.label_name = "goober"

        self._setup_type()

        if self.max_hits > 1:
            from .constants import UI_THEMES
            th = UI_THEMES.get(self.state.selected_ui_theme, UI_THEMES["default"])
            self.hp_bar = QProgressBar(self)
            self.hp_bar.setFixedHeight(6)
            self.hp_bar.setTextVisible(False)
            self.hp_bar.setRange(0, self.max_hits)
            self.hp_bar.setValue(self.hit_points)
            self.hp_bar.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid {th['accent']}88; border-radius: 3px; background: {th['bg']}; }}
                QProgressBar::chunk {{ background: #ff6b6b; border-radius: 2px; }}
            """)
        else:
            self.hp_bar = None

        speed_scale = self._get_progression_speed_mult()
        self.vx = random.choice([-1, 1]) * int(random.randint(self.speed_min, self.speed_max) * speed_scale)
        self.vy = random.choice([-1, 1]) * int(random.randint(1, 2) * speed_scale)

        self.update_scale()
        self.set_movie(self.walk_movie)
        self.reset_position(initial=True)

        if self.goober_type == "angry":
            self._chasing = True
            self._play_animation("panic")
            btn = self.game_window.click_btn
            cx = btn.x() + btn.width() // 2
            cy = btn.y() + btn.height() // 2
            dx = cx - self.x()
            dy = cy - self.y()
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            spd = (self.speed_min + self.speed_max) * 1.3
            self.vx = int(dx / dist * spd)
            self.vy = int(dy / dist * spd)
            self.update_facing()

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_movement)
        self.move_timer.start(30)

        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.random_behavior)
        self.behavior_timer.start(random.randint(3600, 5200))

        self.game_window.register_goober_seen(self.goober_type)

    def _setup_type(self):
        if self.goober_type in EXTRA_GOOBER_DATA:
            data = EXTRA_GOOBER_DATA[self.goober_type]
            self.max_hits = int(data.get("hits", 1))
            self.hit_points = self.max_hits
            self.money_reward = int(data.get("money_reward", 0))
            self.coin_reward = int(data.get("coin_reward", 0))
            self.essence_reward = int(data.get("essence_reward", 0))
            self.click_progress_reward = int(data.get("click_progress_reward", 1))
            self.speed_min = int(data.get("speed_min", 1))
            self.speed_max = int(data.get("speed_max", 2))
            self.size_multiplier = float(data.get("size_multiplier", 1.0))
            self.normal_push = int(data.get("normal_push", 6))
            self.panic_push = int(data.get("panic_push", 28))
            self.label_name = data.get("label_name", self.goober_type.upper())
            color = data.get("color")
            if color:
                self.color_tint = QColor(*color)
            return

        if self.goober_type == "boss":
            self.max_hits = 18 + self.state.prestige_level * 3 + self.state.perks.get("boss_hunter", 0) * 2
            self.hit_points = self.max_hits
            self.money_reward = 60000
            self.coin_reward = 18
            self.essence_reward = 1
            self.click_progress_reward = 20
            self.speed_min = 1
            self.speed_max = 2
            self.size_multiplier = 1.95
            self.normal_push = 13
            self.panic_push = 45
            self.label_name = "BOSS"
            self.color_tint = QColor(255, 180, 80, 170)
        elif self.goober_type == "rgb":
            self.max_hits = 5
            self.hit_points = 5
            self.money_reward = 25000
            self.coin_reward = 15
            self.click_progress_reward = 10
            self.speed_min = 2
            self.speed_max = 3
            self.size_multiplier = 1.45
            self.normal_push = 8
            self.panic_push = 36
            self.label_name = "RGB"
        elif self.goober_type == "gold":
            self.money_reward = 5000
            self.coin_reward = 5
            self.click_progress_reward = 4
            self.speed_min = 1
            self.speed_max = 2
            self.size_multiplier = 1.12
            self.normal_push = 7
            self.panic_push = 30
            self.label_name = "GOLD"
            self.color_tint = QColor(255, 215, 70, 150)
        elif self.goober_type == "angry":
            self.money_reward = 1500
            self.coin_reward = 2
            self.click_progress_reward = 2
            self.speed_min = 2
            self.speed_max = 3
            self.size_multiplier = 1.0
            self.normal_push = 10
            self.panic_push = 34
            self.label_name = "ANGRY"
            self.color_tint = QColor(255, 80, 80, 150)
        elif self.goober_type == "tiny":
            self.money_reward = 1200
            self.coin_reward = 2
            self.click_progress_reward = 2
            self.speed_min = 3
            self.speed_max = 4
            self.size_multiplier = 0.74
            self.normal_push = 4
            self.panic_push = 22
            self.label_name = "TINY"
            self.color_tint = QColor(120, 255, 255, 140)
        elif self.goober_type == "giant":
            self.money_reward = 7000
            self.coin_reward = 6
            self.click_progress_reward = 5
            self.speed_min = 1
            self.speed_max = 1
            self.size_multiplier = 1.42
            self.normal_push = 9
            self.panic_push = 32
            self.label_name = "GIANT"
            self.color_tint = QColor(190, 120, 255, 145)
        elif self.goober_type == "frozen":
            self.money_reward = 2500
            self.coin_reward = 3
            self.click_progress_reward = 3
            self.speed_min = 1
            self.speed_max = 2
            self.size_multiplier = 1.05
            self.normal_push = 5
            self.panic_push = 24
            self.label_name = "FROZEN"
            self.color_tint = QColor(120, 220, 255, 155)
        elif self.goober_type == "bomb":
            self.money_reward = 3000
            self.coin_reward = 3
            self.click_progress_reward = 3
            self.speed_min = 2
            self.speed_max = 2
            self.size_multiplier = 1.08
            self.normal_push = 8
            self.panic_push = 38
            self.label_name = "BOMB"
            self.color_tint = QColor(255, 120, 40, 155)
        else:
            self.money_reward = 0
            self.coin_reward = 1
            self.click_progress_reward = 1
            self.speed_min = 1
            self.speed_max = 2
            self.size_multiplier = 1.0
            self.normal_push = 6
            self.panic_push = 28
            self.label_name = "GOOBER"
            self.color_tint = None

        self.maybe_apply_cosmetic_color()

    def maybe_apply_cosmetic_color(self):
        if self.goober_type == "normal":
            if random.random() < COSMETIC_COLOR_CHANCE:
                color_tuple = random.choice(GOOBER_COLORS)
                self.color_tint = QColor(*color_tuple)
            else:
                self.color_tint = None

    def get_tint_color(self):
        if self.goober_type == "rgb":
            return QColor.fromHsv(self.rgb_hue % 360, 255, 255, 160)
        return self.color_tint

    def apply_tint(self, pixmap):
        tint = self.get_tint_color()
        if tint is None:
            return pixmap
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        painter.fillRect(result.rect(), tint)
        painter.end()
        return result

    def _movie_frame_changed(self):
        self.refresh_current_frame()

    def update_scale(self):
        area_h = max(300, self.parent().height())
        base = max(72, min(int(area_h * 0.22), 140))
        self.base_size = int(base * self.size_multiplier)
        if self.anim_state == "idle":
            self.resize(self.base_size, int(self.base_size * 1.08))
        else:
            self.resize(self.base_size, self.base_size)
        self.refresh_current_frame()
        self._update_hp_bar_pos()

    def _update_hp_bar_pos(self):
        if self.hp_bar is not None:
            bw = max(30, self.width() - 10)
            self.hp_bar.setGeometry((self.width() - bw) // 2, self.height() - 8, bw, 6)

    def _update_hp_bar(self):
        if self.hp_bar is not None:
            self.hp_bar.setValue(self.hit_points)
            self.hp_bar.setRange(0, self.max_hits)

    def refresh_current_frame(self):
        if self.current_movie is None:
            return
        frame = self.current_movie.currentFrameNumber()
        sz = self.size()
        key = (frame, sz.width(), sz.height(), self.facing_left)
        if key in self._frame_cache:
            self.setPixmap(self._frame_cache[key])
            return
        pixmap = self.current_movie.currentPixmap()
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(
            sz,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        scaled = self.apply_tint(scaled)
        if self.facing_left:
            scaled = scaled.transformed(QTransform().scale(-1, 1))
        self._frame_cache[key] = scaled
        if len(self._frame_cache) > 200:
            self._frame_cache.clear()
        self.setPixmap(scaled)

    def update_facing(self):
        self.facing_left = self.vx < 0
        self.refresh_current_frame()

    def set_movie(self, movie):
        self.current_movie = movie
        self._frame_cache.clear()
        movie.jumpToFrame(0)
        if self.state.settings.get("animate_goobers", True):
            movie.start()
        else:
            movie.stop()
        self.refresh_current_frame()

    def _on_scare_frame(self, frame):
        if frame >= self.scare_movie.frameCount() - 1:
            self.scare_movie.stop()
            self.scare_movie.frameChanged.disconnect(self._on_scare_frame)

    def _play_animation(self, state_name):
        self.anim_state = state_name
        movie_map = {
            "idle": self.idle_movie,
            "walk": self.walk_movie,
            "scare": self.scare_movie,
            "panic": self.panic_movie,
        }
        self.set_movie(movie_map[state_name])
        if state_name == "scare":
            try:
                self.scare_movie.frameChanged.disconnect(self._on_scare_frame)
            except TypeError:
                pass
            self.scare_movie.frameChanged.connect(self._on_scare_frame)

    def _get_progression_speed_mult(self):
        state = self.state
        base = 1.0
        from_level = state.prestige_level * 0.08
        from_wealth = min(state.lifetime_money / 500_000, 1.5)
        from_upgrades = (state.upgrade_level + state.auto_level) * 0.03
        return base + from_level + from_wealth + from_upgrades

    def reset_position(self, initial=False):
        self._play_animation("walk")
        self.hit_points = self.max_hits
        self._scared = False
        self._fleeing_off = False
        self._update_hp_bar()
        speed_scale = self._get_progression_speed_mult()
        self.vx = random.choice([-1, 1]) * int(random.randint(self.speed_min, self.speed_max) * speed_scale)
        self.vy = random.choice([-1, 1]) * int(random.randint(1, 2) * speed_scale)
        self.update_facing()
        self.push_cooldown = 0
        self._move_cooldown = 0

        if self.goober_type == "rgb":
            self.rgb_hue = random.randint(0, 359)
        else:
            self.maybe_apply_cosmetic_color()

        self.update_scale()

        max_x = max(0, self.parent().width() - self.width())
        max_y = max(0, self.parent().height() - self.height())

        self.move(
            random.randint(0, max_x),
            random.randint(0, max_y)
        )

        if not initial:
            self.show()

        if self.goober_type == "angry":
            self._chasing = True
            self._play_animation("panic")
            btn = self.game_window.click_btn
            cx = btn.x() + btn.width() // 2
            cy = btn.y() + btn.height() // 2
            dx = cx - self.x()
            dy = cy - self.y()
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            spd = (self.speed_min + self.speed_max) * 1.3
            self.vx = int(dx / dist * spd)
            self.vy = int(dy / dist * spd)
            self.update_facing()

    def random_behavior(self):
        if self.anim_state != "walk":
            return

        idle_chance = 0.25
        if self.state.goober_charm_bought:
            idle_chance = 0.12
        if self.goober_type == "rgb":
            idle_chance *= 0.45
        elif self.goober_type == "angry":
            idle_chance *= 0.5
        elif self.goober_type == "tiny":
            idle_chance *= 0.7
        elif self.goober_type == "giant":
            idle_chance *= 1.2

        if random.random() < idle_chance:
            self._play_animation("idle")
            idle_ms = random.randint(700, 1400)
            QTimer.singleShot(idle_ms, self.resume_walk)

    def resume_walk(self):
        if self.anim_state == "idle":
            self.update_scale()
            self._play_animation("walk")

    def update_movement(self):
        if not self.isVisible():
            return

        if self.goober_type == "rgb":
            self.rgb_hue = (self.rgb_hue + 6) % 360
            self.refresh_current_frame()

        if self.push_cooldown > 0:
            self.push_cooldown -= 1

        if self._move_cooldown > 0:
            self._move_cooldown -= 1

        speed_scale = self._get_progression_speed_mult()

        if self._scared and not self._fleeing_off:
            cursor = self.parent().mapFromGlobal(QCursor.pos())
            dx = self.x() - cursor.x()
            dy = self.y() - cursor.y()
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            spd = int((self.speed_max + 3) * speed_scale)
            self.vx = int(dx / dist * spd)
            self.vy = int(dy / dist * spd)
            self.update_facing()
        elif self._chasing and not self._scared:
            btn = self.game_window.click_btn
            cx = btn.x() + btn.width() // 2
            cy = btn.y() + btn.height() // 2
            dx = cx - self.x()
            dy = cy - self.y()
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            spd = int((self.speed_min + self.speed_max) * 1.3 * speed_scale)
            self.vx = int(dx / dist * spd)
            self.vy = int(dy / dist * spd)
            self.update_facing()

        if self.anim_state in ["walk", "panic"] and self._move_cooldown == 0:
            self.move(self.x() + self.vx, self.y() + self.vy)

        if self._fleeing_off:
            if self.x() > self.parent().width() + 60 or self.x() < -self.width() - 60:
                self.hide()
        elif self._scared or self._chasing:
            pw = self.parent().width()
            ph = self.parent().height()
            cx = max(0, min(self.x(), pw - self.width()))
            cy = max(0, min(self.y(), ph - self.height()))
            if cx != self.x() or cy != self.y():
                self.move(cx, cy)
        elif self.anim_state != "panic":
            bounced = False
            if self.x() <= 0 or self.x() >= self.parent().width() - self.width():
                self.vx *= -1
                bounced = True
            if self.y() <= 0 or self.y() >= self.parent().height() - self.height():
                self.vy *= -1
                bounced = True
            if bounced:
                self.update_facing()
        else:
            if self.x() > self.parent().width() + 60 or self.x() < -self.width() - 60:
                self.hide()

        self.push_click_button()

    def get_push_values(self):
        if self.anim_state == "panic":
            push = self.panic_push
            if self.state.panic_shield_bought:
                push = max(12, push - 10)
        else:
            push = self.normal_push
            if self.state.heavy_button_bought:
                push = max(2, push - 3)
        panic_reduce = int(self.game_window.current_event_modifier("panic_reduce", 0))
        push = max(1, push - panic_reduce)
        push = max(1, int(push / self.state.get_synergy_push_reduce()))
        return push

    def push_click_button(self):
        if self.push_cooldown > 0:
            return

        btn = self.game_window.click_btn
        if not self.geometry().intersects(btn.geometry()):
            return

        push_multiplier = self.get_push_values()
        if self.game_window.active_event == "invert_move":
            push_multiplier = int(push_multiplier * -0.75)
        push_x = int(self.vx * push_multiplier)
        push_y = int(self.vy * push_multiplier)
        if self.game_window.active_event == "gravity":
            push_y += 18

        area = self.parent()
        new_x = btn.x() + push_x
        new_y = btn.y() + push_y

        max_x = max(0, area.width() - btn.width())
        max_y = max(0, area.height() - btn.height())

        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        btn.move(new_x, new_y)
        self.push_cooldown = 8

    def _cleanup_anim(self, anim):
        if anim in self.anim_refs:
            self.anim_refs.remove(anim)
        anim.deleteLater()

    def do_jump(self):
        start_rect = self.geometry()
        jump_height = int(self.height() * 0.2)

        top_rect = QRect(
            start_rect.x(),
            max(0, start_rect.y() - jump_height),
            start_rect.width(),
            start_rect.height()
        )

        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(200)
        anim.setStartValue(start_rect)
        anim.setKeyValueAt(0.45, top_rect)
        anim.setEndValue(start_rect)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.anim_refs.append(anim)
        anim.finished.connect(lambda a=anim: self._cleanup_anim(a))
        anim.start()

    def register_click_stat(self):
        self.state.stats["goobers_clicked"] += 1
        t = self.goober_type
        if t == "boss":
            self.state.stats["boss_clicked"] += 1
            self.state.stats["boss_defeated"] += 1
        elif t == "rgb":
            self.state.stats["rgb_defeated"] += 1
        elif t == "gold":
            self.state.stats["gold_clicked"] += 1
        elif t == "angry":
            self.state.stats["angry_clicked"] += 1
        elif t == "tiny":
            self.state.stats["tiny_clicked"] += 1
        elif t == "giant":
            self.state.stats["giant_clicked"] += 1
        elif t == "frozen":
            self.state.stats["frozen_clicked"] += 1
        elif t == "bomb":
            self.state.stats["bomb_clicked"] += 1
        else:
            self.state.stats["normal_clicked"] += 1
        self.game_window.register_goober_clicked(self.goober_type)

    def give_special_rewards(self):
        rarity = GOOBER_INFO.get(self.goober_type, GOOBER_INFO["normal"])["rarity"]
        money_mult = RARITY_INFO[rarity]["mult"] + (self.state.perks.get("goober_luck", 0) * 0.05)
        money_mult *= self.state.get_collection_money_bonus()
        payout = int(self.money_reward * money_mult)

        is_special = self.goober_type != "normal"
        ev_money_mult = self.game_window.current_event_modifier("special_money_mult", 1.0)
        if is_special and ev_money_mult > 1.0:
            payout = int(payout * ev_money_mult)

        if payout > 0:
            self.state.count += payout
            self.state.lifetime_money += payout
            self.state.stats["money_earned"] += payout

        if self.state.secret_shop_unlocked:
            coin_mult = 3 if getattr(self.game_window, '_skill_coinburst_active', False) else 1
            gained = (self.coin_reward + self.state.prestige_level // 2) * coin_mult
            if self.state.lucky_paws_bought and is_special:
                gained += 1 * coin_mult
            ev_coin_bonus = int(self.game_window.current_event_modifier("special_coin_bonus", 0))
            if is_special and ev_coin_bonus > 0:
                gained += ev_coin_bonus
            self.state.goober_coins += gained
        else:
            self.state.goober_clicks_total += self.click_progress_reward
            if self.state.goober_clicks_total >= SECRET_SHOP_UNLOCK_CLICKS:
                self.state.secret_shop_unlocked = True
                self.game_window.update_secret_shop_buttons()

        if self.essence_reward > 0:
            extra = self.state.perks.get("essence_boost", 0)
            gain = self.essence_reward + (1 if extra >= 3 else 0)
            ev_essence_bonus = int(self.game_window.current_event_modifier("special_essence_bonus", 0))
            if is_special and ev_essence_bonus > 0:
                gain += ev_essence_bonus
            self.state.poopy_essence += gain
            self.game_window.sound.play("essence")
        elif self.state.essence_magnet_bought and is_special and random.random() < 0.18:
            self.state.poopy_essence += 1
            self.game_window.sound.play("essence")

        self.game_window.update_ui()

    def _handle_multi_hit_death(self, center_x, sound_name, burst_count, burst_colors=None):
        self.register_click_stat()
        self.game_window.sound.play(sound_name)
        self.give_special_rewards()
        burst(self.parent(), center_x, self.y(), burst_count, colors=burst_colors,
              enabled=self.state.settings.get("show_particles", True))
        self.game_window._check_achievements()
        self._flee_off_screen()

    def _do_multi_hit(self):
        self.hit_points -= 1
        self._update_hp_bar()
        self.game_window.sound.play("goober_pop")
        if self.hit_points > 0:
            self._enter_scared()
            return True
        return False

    def mousePressEvent(self, event):
        if self.anim_state in ["scare", "panic"] and not self._scared and not self._chasing:
            return

        center_x = self.x() + self.width() // 2

        if self.goober_type in EXTRA_GOOBER_DATA:
            if self._do_multi_hit():
                return
            data = EXTRA_GOOBER_DATA[self.goober_type]
            event_payload = data.get("event_on_click")
            if event_payload:
                ev_name, dur, ev_title, ev_desc, ev_color = event_payload
                self.game_window.start_event(ev_name, dur, ev_title, ev_desc, ev_color)
            self._handle_multi_hit_death(center_x, "goober_pop", 10)
            return

        elif self.goober_type == "boss":
            if self._do_multi_hit():
                return
            self._handle_multi_hit_death(center_x, "boss_death", 18,
                                         ["#ffcf66", "#ffd700", "#ff9f4a"])
            return

        elif self.goober_type == "rgb":
            if self._do_multi_hit():
                return
            self._handle_multi_hit_death(center_x, "rgb_death", 14,
                                         ["#ff66ff", "#66ff66", "#6666ff", "#ff6666"])
            return

        else:
            self.game_window.sound.play("goober_pop")
            self.register_click_stat()
            self.state.goober_clicks_total += 1
            if not self.state.secret_shop_unlocked and self.state.goober_clicks_total >= SECRET_SHOP_UNLOCK_CLICKS:
                self.state.secret_shop_unlocked = True
                self.game_window.update_secret_shop_buttons()
            if self.state.secret_shop_unlocked:
                gain = (2 if self.state.lucky_paws_bought else 1) + self.state.prestige_level // 2
                self.state.goober_coins += gain
            self.game_window.update_ui()

        self.game_window._check_achievements()
        self._chasing = False
        self._play_animation("scare")
        self.vx = 0
        self.vy = 0
        self.do_jump()
        QTimer.singleShot(1100, self.start_panic)

    def start_panic(self):
        if self.anim_state != "scare":
            return

        self._play_animation("panic")
        self.game_window.sound.play("panic")

        direction = 1 if self.x() < self.parent().width() // 2 else -1
        base = self.speed_max + 4
        if self.goober_type == "angry":
            base = int(base * 1.7)
        self.vx = direction * random.randint(base, base + 3)
        self.vy = random.randint(-2, 2)
        self.update_facing()

    def keep_inside_after_resize(self):
        self.update_scale()

        if self.anim_state == "panic":
            return

        max_x = max(0, self.parent().width() - self.width())
        max_y = max(0, self.parent().height() - self.height())

        x = min(max(0, self.x()), max_x)
        y = min(max(0, self.y()), max_y)
        self.move(x, y)

    def _enter_scared(self):
        self._scared = True
        self._play_animation("panic")
        cursor = self.parent().mapFromGlobal(QCursor.pos())
        dx = self.x() - cursor.x()
        dy = self.y() - cursor.y()
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        spd = self.speed_max + 3
        self.vx = int(dx / dist * spd)
        self.vy = int(dy / dist * spd)
        self.update_facing()

    def _flee_off_screen(self):
        self._fleeing_off = True
        self._scared = False
        self._play_animation("panic")
        center_x = self.parent().width() // 2
        direction = 1 if self.x() < center_x else -1
        self.vx = direction * (self.speed_max + 6)
        self.vy = random.randint(-2, 2)
        self.update_facing()
