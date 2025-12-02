# ui/main_window.py
import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QApplication,
                               QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt
from .title_bar import TitleBar
from .settings_window import SettingsWindow
from .draw_window import DrawWindow
from .result_window import ResultWindow
from core.config_manager import ConfigManager
from core.prize_manager import PrizeManager
from core.animation_manager import AnimationManager
from core.draw_engine import DrawEngine

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(900, 600)
        self.setObjectName("mainWindow")

        # ensure config exists
        ConfigManager.ensure_default()

        # core managers
        self.pm = PrizeManager()
        self.am = AnimationManager()
        self.engine = DrawEngine(self.pm, self.am)

        self.title = TitleBar("抽奖程序")
        self.title.minimizeRequested.connect(self.showMinimized)
        self.title.maximizeRequested.connect(self.toggle_max)
        self.title.closeRequested.connect(self.close)

        self.title.setFixedHeight(36)

        self.settingsWindow = SettingsWindow(self.am)
        self.settingsWindow.settingsChanged.connect(self._on_settings_changed)

        self.drawWindow = DrawWindow(self.engine)
        self.drawWindow.finished.connect(self._on_draw_finished)

        self.resultWindow = ResultWindow()
        self.resultWindow.retryRequested.connect(self._on_retry)
        self.resultWindow.backRequested.connect(self._on_back)

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6,6,6,6)
        self.layout.addWidget(self.title)

        content = QHBoxLayout()
        left = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setObjectName("settingsFrame")
        lf_layout = QVBoxLayout(left_frame)
        lbl = QLabel("设置 / 控制")
        lbl.setProperty("class", "title")
        lf_layout.addWidget(lbl)

        btnOpenSettings = QPushButton("打开自定义动画设置")
        btnStart = QPushButton("开始抽奖(使用已启用动画)")
        btnOpenSettings.clicked.connect(self._open_settings)
        btnStart.clicked.connect(self._start_draw)

        lf_layout.addWidget(btnOpenSettings)
        lf_layout.addWidget(btnStart)
        left.addWidget(left_frame)
        content.addLayout(left, 1)

        # center area: drawWindow placeholder or result
        self.centerFrame = QFrame()
        self.centerFrameLayout = QVBoxLayout(self.centerFrame)
        self.centerFrameLayout.addWidget(self.drawWindow)
        self.centerFrameLayout.addWidget(self.resultWindow)
        self.resultWindow.hide()

        content.addWidget(self.centerFrame, 3)
        self.layout.addLayout(content)

        # load style
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        try:
            with open(qss_path, "r", encoding="utf8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def _open_settings(self):
        self.settingsWindow.show()

    def _on_settings_changed(self):
        # reload animation manager config if needed
        self.am.load()

    def _start_draw(self):
        # hide result, show draw area
        self.resultWindow.hide()
        self.drawWindow.show()
        self.drawWindow.start_draw()

    def _on_draw_finished(self, prize):
        # hide draw window and show result
        self.drawWindow.hide()
        self.resultWindow.set_result(prize)
        self.resultWindow.show()

    def _on_retry(self):
        self.resultWindow.hide()
        self.drawWindow.show()
        # ensure engine resets flags
        self.engine.calculated = False
        self.engine.result = None
        self.drawWindow.start_draw()

    def _on_back(self):
        self.resultWindow.hide()
        self.settingsWindow.show()

    def toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
