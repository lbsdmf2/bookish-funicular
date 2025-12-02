# ui/result_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal

class ResultWindow(QWidget):
    retryRequested = Signal()
    backRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.resultLabel = QLabel("抽奖结果：")
        self.resultLabel.setObjectName("resultLabel")
        self.layout.addWidget(self.resultLabel)

        h = QHBoxLayout()
        self.btnBack = QPushButton("返回设置")
        self.btnRetry = QPushButton("再来一次")
        h.addWidget(self.btnBack)
        h.addWidget(self.btnRetry)
        self.layout.addLayout(h)

        self.btnBack.clicked.connect(self.backRequested.emit)
        self.btnRetry.clicked.connect(self.retryRequested.emit)

    def set_result(self, text):
        self.resultLabel.setText(f"抽奖结果：{text}")
