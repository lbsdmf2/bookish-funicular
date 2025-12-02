import json
import random

class AnimationManager:
    """
    五个槽位：
    slot1, slot2 → 抽奖动画组 (rare + normal)
    slot3, slot4, slot5 → 普通 mp4 文件
    """

    def __init__(self, config_path="config/animation_slots.json"):
        self.config_path = config_path

        self.rare = {}     # 稀有动画组：{slot1: "xx.mp4"}
        self.normal = {}   # 普通动画组：{slot1: "xx.mp4"}
        self.single = {}   # 单个动画：{slot3: "xx.mp4"}

        self.enabled = []  # 用户勾选使用

        self.load()

    def load(self):
        with open(self.config_path, "r", encoding="utf8") as f:
            cfg = json.load(f)

        self.rare = cfg["rare"]
        self.normal = cfg["normal"]
        self.single = cfg["single"]
        self.enabled = cfg["enabled"]

    def save(self):
        with open(self.config_path, "w", encoding="utf8") as f:
            json.dump({
                "rare": self.rare,
                "normal": self.normal,
                "single": self.single,
                "enabled": self.enabled
            }, f, indent=4, ensure_ascii=False)

    def get_weighted_animation(self):
        groups = []
        singles = []

        for slot in self.enabled:
            if slot in self.single:
                singles.append(slot)
            elif slot in self.rare and slot in self.normal:
                groups.append(slot)

        total = len(groups) + len(singles)
        if total == 0:
            return None

        W = 1 / total

        choices = []
        weights = []

        for s in singles:
            choices.append(("single", self.single[s]))
            weights.append(W)

        for g in groups:
            rare_file = self.rare[g]
            normal_file = self.normal[g]

            choices.append(("rare", rare_file))
            weights.append(W * 0.1)

            choices.append(("normal", normal_file))
            weights.append(W * 0.9)

        return random.choices(choices, weights=weights, k=1)[0]
