import sys, os, random
from PySide6.QtCore import Qt, QUrl, QTimer, Slot
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QComboBox, QMessageBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


CONFIG_FILE = "prizes.txt"
VIDEO_NORMAL = "animation_normal.mp4"
VIDEO_RARE = "animation_rare.mp4"


class LotteryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎁 抽奖系统")
        self.showFullScreen()
        self.setStyleSheet("""
            QWidget { background-color: #fafafa; color: #333; font-family: 'Microsoft YaHei'; }
            QPushButton {
                background-color: #4a90e2; color: white; font-size: 18px;
                border-radius: 8px; padding: 10px 20px;
            }
            QPushButton:hover { background-color: #357ab8; }
        """)

        # 读取奖品
        self.prizes = self.load_prizes(CONFIG_FILE)
        self.remaining = self.prizes.copy()

        self.mode = "视频动画"  # 默认模式
        self.stack = QStackedWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stack)

        self.init_settings_page()
        self.init_lottery_page()
        self.init_result_page()

        self.stack.setCurrentWidget(self.settings_page)

    # ------------------- 页面定义 -------------------

    def init_settings_page(self):
        self.settings_page = QWidget()
        layout = QVBoxLayout(self.settings_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("⚙️ 抽奖设置")
        title.setStyleSheet("font-size: 40px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["视频动画", "老虎机动画"])
        self.mode_select.setFixedWidth(200)
        self.mode_select.setStyleSheet("font-size: 20px; padding: 5px;")

        start_button = QPushButton("开始抽奖")
        start_button.setFixedWidth(200)
        start_button.clicked.connect(self.start_lottery_screen)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(QLabel("选择抽奖动画模式：", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(self.mode_select)
        layout.addSpacing(40)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.settings_page)

    def init_lottery_page(self):
        self.lottery_page = QWidget()
        self.lottery_layout = QVBoxLayout(self.lottery_page)
        self.lottery_layout.setContentsMargins(0, 0, 0, 0)
        self.lottery_layout.setSpacing(0)

        # 视频组件
        self.video_widget = QVideoWidget()
        self.video_widget.hide()

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        # 老虎机模拟文本
        self.slot_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.slot_label.setStyleSheet("font-size: 60px; color: #222; font-weight: bold;")

        # 半透明跳过按钮
        self.skip_button = QPushButton("⏩ 跳过动画")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 160);
                color: #333; font-size: 22px; border-radius: 12px;
                padding: 10px 30px;
            }
            QPushButton:hover { background-color: rgba(200, 200, 200, 180); }
        """)
        self.skip_button.clicked.connect(self.skip_animation)
        self.skip_button.hide()

        self.lottery_layout.addWidget(self.video_widget)
        self.lottery_layout.addWidget(self.slot_label)
        self.lottery_layout.addWidget(self.skip_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.lottery_page)

    def init_result_page(self):
        self.result_page = QWidget()
        layout = QVBoxLayout(self.result_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.result_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 36px; color: #222; font-weight: bold;")

        btn_layout = QHBoxLayout()
        self.return_button = QPushButton("返回设置")
        self.retry_button = QPushButton("再来一次")

        self.return_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        self.retry_button.clicked.connect(self.start_lottery_screen)

        btn_layout.addWidget(self.return_button)
        btn_layout.addWidget(self.retry_button)

        layout.addWidget(self.result_label)
        layout.addSpacing(40)
        layout.addLayout(btn_layout)

        self.stack.addWidget(self.result_page)

    # ------------------- 逻辑控制 -------------------

    def load_prizes(self, file_path):
        prizes = {}
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", f"未找到配置文件：{file_path}")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    name, count = [x.strip() for x in line.split(",")]
                    prizes[name] = int(count)
                except ValueError:
                    continue
        return prizes

    def weighted_draw(self):
        avg = sum(self.remaining.values()) / len(self.remaining)
        diffs = {k: abs(v - avg) for k, v in self.remaining.items()}
        min_diff = min(diffs.values())
        adjust_candidates = [k for k, v in self.remaining.items()
                             if v < 2 and abs(v - avg) == min_diff]

        names = list(self.remaining.keys())
        weights = []
        for name in names:
            w = self.remaining[name]
            if name in adjust_candidates:
                w *= 3
            weights.append(w)
        return random.choices(names, weights=weights, k=1)[0]

    def start_lottery_screen(self):
        self.mode = self.mode_select.currentText()
        self.stack.setCurrentWidget(self.lottery_page)

        self.video_widget.hide()
        self.slot_label.hide()
        self.skip_button.show()

        if self.mode == "视频动画":
            self.play_video_animation()
        else:
            self.play_slot_animation()

    def play_video_animation(self):
        use_rare = random.random() < 0.05
        video_file = VIDEO_RARE if use_rare else VIDEO_NORMAL
        if not os.path.exists(video_file):
            self.show_result("❌ 未找到动画文件")
            return

        self.video_widget.show()
        self.media_player.setSource(QUrl.fromLocalFile(os.path.abspath(video_file)))
        self.media_player.play()

    def play_slot_animation(self):
        self.slot_label.show()
        self.slot_label.setText("🎰 🎰 🎰")
        self.slot_timer = QTimer()
        self.slot_timer.timeout.connect(self.update_slot)
        self.slot_timer.start(100)
        self.slot_elapsed = 0
        self.slot_duration = 5000
        QTimer.singleShot(self.slot_duration, self.finish_lottery)

    def update_slot(self):
        symbols = ["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣"]
        text = " ".join(random.choices(symbols, k=3))
        self.slot_label.setText(text)
        self.slot_elapsed += 100
        if self.slot_elapsed >= self.slot_duration:
            self.slot_timer.stop()

    @Slot()
    def skip_animation(self):
        self.media_player.stop()
        self.finish_lottery()

    @Slot()
    def on_media_status_changed(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.finish_lottery()

    def finish_lottery(self):
        self.skip_button.hide()

        if not self.remaining:
            self.show_result("🎉 所有奖品已抽完！")
            return

        winner = self.weighted_draw()
        self.remaining[winner] -= 1
        if self.remaining[winner] <= 0:
            del self.remaining[winner]

        self.show_result(f"🏆 恭喜获得【{winner}】！")

    def show_result(self, text):
        self.result_label.setText(text)
        self.stack.setCurrentWidget(self.result_page)


# ------------------- 运行入口 -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.show()
    sys.exit(app.exec())
