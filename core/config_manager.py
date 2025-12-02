import os
import json

class ConfigManager:
    @staticmethod
    def ensure_default():
        # 创建初始 prize 配置
        if not os.path.exists("config/prizes.json"):
            with open("config/prizes.json", "w", encoding="utf8") as f:
                json.dump({
                    "prizes": {
                        "奖品A": {"count": 5},
                        "奖品B": {"count": 5},
                        "奖品C": {"count": 5}
                    },
                    "recent": []
                }, f, indent=4, ensure_ascii=False)

        # 创建初始 animation 配置
        if not os.path.exists("config/animation_slots.json"):
            with open("config/animation_slots.json", "w", encoding="utf8") as f:
                json.dump({
                    "rare": {"slot1": "assets/animations/sample_rare.mp4"},
                    "normal": {"slot1": "assets/animations/sample_normal.mp4"},
                    "single": {"slot3": "assets/animations/sample_single.mp4"},
                    "enabled": ["slot1", "slot3"]
                }, f, indent=4, ensure_ascii=False)
