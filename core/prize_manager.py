import json
import random
from collections import deque

class PrizeManager:
    def __init__(self, config_path="config/prizes.json"):
        self.config_path = config_path
        self.prizes = {}           # {name: {"count": x}}
        self.weights = {}          # {name: weight}
        self.recent = deque(maxlen=5)  # 最近 5 次抽取
        self.load()

    def load(self):
        with open(self.config_path, "r", encoding="utf8") as f:
            data = json.load(f)
        self.prizes = data["prizes"]
        self.recent = deque(data["recent"], maxlen=5)
        self.recalculate_weights()

    def save(self):
        with open(self.config_path, "w", encoding="utf8") as f:
            json.dump({
                "prizes": self.prizes,
                "recent": list(self.recent)
            }, f, indent=4, ensure_ascii=False)

    def recalculate_weights(self):
        """根据最近5次抽取记录调整概率"""
        self.weights = {}

        all_names = list(self.prizes.keys())

        # 统计频率
        freq = {name: 0 for name in all_names}
        for p in self.recent:
            freq[p] += 1

        for name in all_names:
            remaining = self.prizes[name]["count"]
            if remaining <= 0:
                self.weights[name] = 0
                continue

            base = 1

            # 没出现 → 增加
            if freq[name] == 0:
                base *= 1.5

            # 连续两次 → 降低
            if len(self.recent) >= 2 and self.recent[-1] == name and self.recent[-2] == name:
                base *= 0.3

            self.weights[name] = base

        # 归一化
        total = sum(self.weights.values())
        for name in all_names:
            self.weights[name] /= (total if total > 0 else 1)

    def draw_prize(self):
        names = list(self.weights.keys())
        w = list(self.weights.values())
        result = random.choices(names, weights=w, k=1)[0]

        # 数量减少
        self.prizes[result]["count"] -= 1

        # 记录最近结果
        self.recent.append(result)

        # 重算
        self.recalculate_weights()
        self.save()

        return result
