import time
import math

from .constants import (
    ACHIEVEMENT_DEFS,
    GOOBER_INFO, DEFAULT_SETTINGS, DEFAULT_PERKS,
    COLLECTION_REWARDS, SYNERGY_BONUSES, ACTIVE_SKILLS, UI_THEMES,
)

__all__ = ["GameState", "ACHIEVEMENT_DEFS"]


class GameState:
    def __init__(self):
        self.count = 0
        self.upgrade_level = 0
        self.auto_level = 0
        self.goober_clicks_total = 0
        self.goober_coins = 0
        self.poopy_essence = 0
        self.prestige_level = 0
        self.lifetime_money = 0

        self.secret_shop_unlocked = False
        self.goober_charm_bought = False
        self.heavy_button_bought = False
        self.lucky_paws_bought = False
        self.sneaky_profit_bought = False
        self.panic_shield_bought = False
        self.boss_beacon_bought = False
        self.essence_magnet_bought = False
        self.mission_radar_bought = False

        self.cleanse_bought = False
        self.frenzy_bought = False
        self.skill_shield_bought = False
        self.coinburst_bought = False

        self.unlocked_achievements = set()

        self.selected_ui_theme = "default"
        self.owned_ui_themes = ["default"]

        self.bestiary_counts = {k: {"seen": 0, "clicked": 0} for k in GOOBER_INFO}

        self.mission_state = {
            "slots": [],
            "completed_total": 0,
            "rerolls_used": 0,
        }

        self.perks = dict(DEFAULT_PERKS)

        self.stats = {
            "total_clicks": 0,
            "money_earned": 0,
            "goobers_clicked": 0,
            "rgb_defeated": 0,
            "gold_clicked": 0,
            "angry_clicked": 0,
            "tiny_clicked": 0,
            "giant_clicked": 0,
            "frozen_clicked": 0,
            "bomb_clicked": 0,
            "boss_clicked": 0,
            "normal_clicked": 0,
            "rare_seen": 0,
            "boss_defeated": 0,
            "highest_combo": 0,
            "prestiges_done": 0,
            "offline_earned_total": 0,
            "collection_rewards_claimed": [],
        }

        self.settings = dict(DEFAULT_SETTINGS)

        self.skill_cooldowns = {s["key"]: 0 for s in ACTIVE_SKILLS}

        self.combo_count = 0
        self.combo_multiplier = 1.0

        self.last_saved_at = 0

    def get_prestige_cost(self):
        return max(50000, 250000 * (self.prestige_level + 1))

    def get_prestige_bonus_click(self):
        return 1.0 + (self.prestige_level * 0.12)

    def get_prestige_bonus_auto(self):
        return 1.0 + (self.prestige_level * 0.10)

    def get_collection_money_bonus(self):
        bonus = 1.0
        claimed = self.stats.get("collection_rewards_claimed", [])
        for reward in COLLECTION_REWARDS:
            if reward["id"] in claimed:
                bonus += reward.get("money_bonus", 0)
        if self.prestige_level >= 8:
            bonus = 1.0 + (bonus - 1.0) * 1.25
        return bonus

    def get_collection_luck_bonus(self):
        bonus = 0.0
        claimed = self.stats.get("collection_rewards_claimed", [])
        for reward in COLLECTION_REWARDS:
            if reward["id"] in claimed:
                bonus += reward.get("luck_bonus", 0)
        if self.prestige_level >= 8:
            bonus *= 1.25
        return bonus

    def get_active_synergies(self):
        active = []
        for syn in SYNERGY_BONUSES:
            if syn["req"](self):
                active.append(syn)
        return active

    def get_synergy_click_mult(self):
        return 1.0 + sum(s.get("click_mult", 0) for s in self.get_active_synergies())

    def get_synergy_auto_mult(self):
        return 1.0 + sum(s.get("auto_mult", 0) for s in self.get_active_synergies())

    def get_synergy_push_reduce(self):
        return 1.0 + sum(s.get("push_reduce", 0) for s in self.get_active_synergies())

    def get_click_value(self, event_mult=1.0):
        base = int((2 ** self.upgrade_level) * self.get_prestige_bonus_click() * self.get_collection_money_bonus())
        perk_mult = 1.0 + (self.perks.get("economy_click", 0) * 0.05)
        synergy_mult = self.get_synergy_click_mult()
        return int(base * perk_mult * event_mult * synergy_mult)

    def get_auto_value(self, event_mult=1.0):
        if self.auto_level == 0:
            return 0
        base = 2 ** (self.auto_level - 1)
        if self.sneaky_profit_bought:
            base = int(base * 1.25)
        base = int(base * self.get_prestige_bonus_auto() * self.get_collection_money_bonus())
        perk_mult = 1.0 + (self.perks.get("economy_auto", 0) * 0.05)
        synergy_mult = self.get_synergy_auto_mult()
        return int(base * perk_mult * event_mult * synergy_mult)

    def get_click_upgrade_cost(self):
        return 200 * (2 ** self.upgrade_level)

    def get_auto_upgrade_cost(self):
        return 500 * (2 ** self.auto_level)

    def get_difficulty_step(self):
        total_upgrades = self.upgrade_level + self.auto_level
        return min(28 + (total_upgrades * 3), 120)

    def get_offline_hours_cap(self):
        cap = 4
        if self.prestige_level >= 3:
            cap = 6
        if self.prestige_level >= 10:
            cap = 10
        return cap

    def calculate_prestige_gain(self):
        base = int(math.sqrt(max(0, self.lifetime_money)) // 120)
        bonus = self.perks.get("essence_boost", 0) // 2
        return max(0, base + bonus)

    def prestige(self):
        cost = self.get_prestige_cost()
        if self.count < cost:
            return False
        essence_gain = self.calculate_prestige_gain()
        self.poopy_essence += essence_gain
        self.prestige_level += 1
        self.stats["prestiges_done"] += 1
        self.count = 0
        self.lifetime_money = 0
        self.upgrade_level = 0
        self.auto_level = 0
        self.goober_clicks_total = 0
        self.goober_coins = 0
        self.secret_shop_unlocked = False
        self.goober_charm_bought = False
        self.heavy_button_bought = False
        self.lucky_paws_bought = False
        self.sneaky_profit_bought = False
        self.panic_shield_bought = False
        self.boss_beacon_bought = False
        self.essence_magnet_bought = False
        self.mission_radar_bought = False
        self.cleanse_bought = False
        self.frenzy_bought = False
        self.skill_shield_bought = False
        self.coinburst_bought = False
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.mission_state = {"slots": [], "completed_total": 0, "rerolls_used": 0}
        return True

    def check_new_achievements(self):
        newly_unlocked = []
        for ach in ACHIEVEMENT_DEFS:
            ach_id = ach[0]
            if ach_id not in self.unlocked_achievements and ach[3](self):
                self.unlocked_achievements.add(ach_id)
                newly_unlocked.append(ach)
        return newly_unlocked

    def to_dict(self):
        return {
            "count": self.count,
            "upgrade_level": self.upgrade_level,
            "auto_level": self.auto_level,
            "goober_clicks_total": self.goober_clicks_total,
            "goober_coins": self.goober_coins,
            "poopy_essence": self.poopy_essence,
            "prestige_level": self.prestige_level,
            "lifetime_money": self.lifetime_money,
            "secret_shop_unlocked": self.secret_shop_unlocked,
            "goober_charm_bought": self.goober_charm_bought,
            "heavy_button_bought": self.heavy_button_bought,
            "lucky_paws_bought": self.lucky_paws_bought,
            "sneaky_profit_bought": self.sneaky_profit_bought,
            "panic_shield_bought": self.panic_shield_bought,
            "boss_beacon_bought": self.boss_beacon_bought,
            "essence_magnet_bought": self.essence_magnet_bought,
            "mission_radar_bought": self.mission_radar_bought,
            "cleanse_bought": self.cleanse_bought,
            "frenzy_bought": self.frenzy_bought,
            "skill_shield_bought": self.skill_shield_bought,
            "coinburst_bought": self.coinburst_bought,
            "unlocked_achievements": list(self.unlocked_achievements),
            "selected_ui_theme": self.selected_ui_theme,
            "owned_ui_themes": self.owned_ui_themes,
            "bestiary_counts": self.bestiary_counts,
            "mission_state": self.mission_state,
            "perks": self.perks,
            "stats": self.stats,
            "settings": self.settings,
            "combo_count": self.combo_count,
            "combo_multiplier": self.combo_multiplier,
            "last_saved_at": self.last_saved_at,
        }

    def from_dict(self, data):
        self.count = data.get("count", 0)
        self.upgrade_level = data.get("upgrade_level", 0)
        self.auto_level = data.get("auto_level", 0)
        self.goober_clicks_total = data.get("goober_clicks_total", 0)
        self.goober_coins = data.get("goober_coins", 0)
        self.poopy_essence = data.get("poopy_essence", 0)
        self.prestige_level = data.get("prestige_level", 0)
        self.lifetime_money = data.get("lifetime_money", 0)
        self.secret_shop_unlocked = data.get("secret_shop_unlocked", False)
        self.goober_charm_bought = data.get("goober_charm_bought", False)
        self.heavy_button_bought = data.get("heavy_button_bought", False)
        self.lucky_paws_bought = data.get("lucky_paws_bought", False)
        self.sneaky_profit_bought = data.get("sneaky_profit_bought", False)
        self.panic_shield_bought = data.get("panic_shield_bought", False)
        self.boss_beacon_bought = data.get("boss_beacon_bought", False)
        self.essence_magnet_bought = data.get("essence_magnet_bought", False)
        self.mission_radar_bought = data.get("mission_radar_bought", False)
        self.cleanse_bought = data.get("cleanse_bought", False)
        self.frenzy_bought = data.get("frenzy_bought", False)
        self.skill_shield_bought = data.get("skill_shield_bought", False)
        self.coinburst_bought = data.get("coinburst_bought", False)
        raw_achs = data.get("unlocked_achievements", [])
        self.unlocked_achievements = set(raw_achs)
        raw_theme = data.get("selected_ui_theme", "default")
        self.selected_ui_theme = raw_theme if isinstance(raw_theme, str) and raw_theme in UI_THEMES else "default"
        raw_owned = data.get("owned_ui_themes", ["default"])
        self.owned_ui_themes = [t for t in raw_owned if isinstance(t, str) and t in UI_THEMES] or ["default"]

        loaded_bestiary = data.get("bestiary_counts", {})
        fresh_bestiary = {k: {"seen": 0, "clicked": 0} for k in GOOBER_INFO}
        for key in fresh_bestiary:
            if key in loaded_bestiary:
                fresh_bestiary[key] = loaded_bestiary[key]
        self.bestiary_counts = fresh_bestiary

        self.mission_state = data.get("mission_state", {"slots": [], "completed_total": 0, "rerolls_used": 0})
        if "slots" not in self.mission_state:
            self.mission_state = {"slots": [], "completed_total": 0, "rerolls_used": 0}

        loaded_perks = data.get("perks", {})
        fresh_perks = dict(DEFAULT_PERKS)
        for key in fresh_perks:
            if key in loaded_perks:
                fresh_perks[key] = loaded_perks[key]
        self.perks = fresh_perks

        loaded_stats = data.get("stats", {})
        for key in self.stats:
            if key in loaded_stats:
                self.stats[key] = loaded_stats[key]

        loaded_settings = data.get("settings", {})
        for key in self.settings:
            if key in loaded_settings:
                self.settings[key] = loaded_settings[key]

        self.combo_count = data.get("combo_count", 0)
        self.combo_multiplier = data.get("combo_multiplier", 1.0)
        self.last_saved_at = data.get("last_saved_at", 0)
