# ui/draw_window.py
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer, Qt, Signal

class DrawWindow(QWidget):
    finished = Signal(str)  # emits prize name when done

    def __init__(self, draw_engine, parent=None):
        super().__init__(parent)
        self.engine = draw_engine
        self.setup_ui()
        self._anim_playing = False
        self._anim_file = None

        # poll for calculation done
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self._poll)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.videoWidget = QVideoWidget()
        self.layout.addWidget(self.videoWidget)

        # controls
        h = QHBoxLayout()
        self.skipBtn = QPushButton(">| 跳过动画")
        self.skipBtn.setObjectName("skipBtn")
        self.skipBtn.setEnabled(False)
        h.addStretch()
        h.addWidget(self.skipBtn)
        self.layout.addLayout(h)

        # media player
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.videoWidget)

        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)

        self.skipBtn.clicked.connect(self._on_skip)

    def start_draw(self):
        # get selected animation
        item = self.engine.am.get_weighted_animation()
        if item is None:
            # no animation configured
            self._anim_file = None
            # start compute immediately
            self.engine.start_draw(lambda f: None, lambda: None)
            self.timer.start()
            return

        anim_type, anim_file = item
        self._anim_file = anim_file

        # play animation
        if os.path.exists(anim_file):
            url = QUrl.fromLocalFile(anim_file)
            self.player.setSource(url)
            self.player.play()
        else:
            # file missing — fallback to no animation
            self.player.stop()

        # start computing in engine thread (engine will compute in background)
        self.engine.start_draw(lambda f: None, lambda: None)
        self.timer.start()

    def _on_playback_state_changed(self, state):
        # if stopped and calculation done -> show result
        if state == QMediaPlayer.PlaybackState.Stopped:
            # if calculated, emit result
            if self.engine.calculated:
                self.finish_with_result()
            else:
                # if video ended but calc not done, wait (timer already running)
                pass

    def _on_media_status_changed(self, status):
        # when media loaded, we want to not enable skip until calculation is done
        pass

    def _poll(self):
        # enable skip when calculation finished
        if self.engine.calculated:
            self.skipBtn.setEnabled(True)
        # if calculation finished and media is not playing, finish
        if self.engine.calculated and self.player.playbackState() != QMediaPlayer.PlaybackState.Playing:
            self.finish_with_result()

    def _on_skip(self):
        # user chooses to skip — stop video and finish
        try:
            self.player.stop()
        except:
            pass
        self.finish_with_result()

    def finish_with_result(self):
        self.timer.stop()
        prize = self.engine.result
        if prize is None:
            # if engine hasn't set result for some reason, compute synchronously
            prize = self.engine.pm.draw_prize()
        self.finished.emit(prize)
