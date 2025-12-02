import threading
import time

class DrawEngine:
    """
    控制抽奖 → 动画半程计算 → 跳过 → 显示结果
    """

    def __init__(self, prize_manager, animation_manager):
        self.pm = prize_manager
        self.am = animation_manager

        self.result = None
        self.calculated = False

    def start_draw(self, animation_callback, finish_callback):
        """
        animation_callback → 播放动画
        finish_callback → 动画结束/跳过后显示结果
        """

        # ① 先随机选择动画
        anim_type, anim_file = self.am.get_weighted_animation()
        self.calculated = False
        self.result = None

        # 开始播放动画
        animation_callback(anim_file)

        # ② 新线程用于计算抽奖结果
        def compute():
            time.sleep(2.5)  # 动画3秒，半程计算
            self.result = self.pm.draw_prize()
            self.calculated = True

        threading.Thread(target=compute).start()

        # ③ 结束动画的回调由 UI 调用 finish_callback()
        return anim_type, anim_file
