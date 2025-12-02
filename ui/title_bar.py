# ui/title_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint

class TitleBar(QWidget):
    minimizeRequested = Signal()
    maximizeRequested = Signal()
    closeRequested = Signal()

    def __init__(self, title="LotteryApp", parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self._mouse_pos = None
        self._dragging = False

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(6, 4, 6, 4)
        self.titleLabel = QLabel(title)
        self.titleLabel.setObjectName("titleLabel")

        self.btnMin = QPushButton("-")
        self.btnMax = QPushButton("□")
        self.btnClose = QPushButton("×")

        for b in (self.btnMin, self.btnMax, self.btnClose):
            b.setFixedSize(28, 24)
            b.setObjectName("ghost")

        self.layout.addWidget(self.titleLabel)
        self.layout.addStretch()
        self.layout.addWidget(self.btnMin)
        self.layout.addWidget(self.btnMax)
        self.layout.addWidget(self.btnClose)

        self.btnMin.clicked.connect(self.minimizeRequested.emit)
        self.btnMax.clicked.connect(self.maximizeRequested.emit)
        self.btnClose.clicked.connect(self.closeRequested.emit)

        # styling done via qss

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.globalPosition().toPoint()
            self._dragging = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self.parent():
            delta = event.globalPosition().toPoint() - self._mouse_pos
            self.parent().move(self.parent().pos() + delta)
            self._mouse_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)
