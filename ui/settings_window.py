# ui/settings_window.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                               QPushButton, QFileDialog, QHBoxLayout, QListWidgetItem)
from PySide6.QtCore import Signal

class SettingsWindow(QWidget):
    settingsChanged = Signal()  # emitted when enabled list or slots changed

    def __init__(self, animation_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 - 自定义动画")
        self.am = animation_manager
        self.setup_ui()
        self.refresh_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("自定义动画设置")
        title.setObjectName("title")
        hint = QLabel("slot1/slot2 为抽奖组(rare+normal)。slot3~slot5 为普通单视频。")
        hint.setObjectName("hint")
        self.layout.addWidget(title)
        self.layout.addWidget(hint)

        # list of slots
        self.slotList = QListWidget()
        self.layout.addWidget(self.slotList)

        btnLayout = QHBoxLayout()
        self.btnAdd = QPushButton("添加/替换 槽位文件")
        self.btnToggle = QPushButton("启用/禁用 选中项")
        self.btnSave = QPushButton("保存")
        btnLayout.addWidget(self.btnAdd)
        btnLayout.addWidget(self.btnToggle)
        btnLayout.addWidget(self.btnSave)
        self.layout.addLayout(btnLayout)

        self.btnAdd.clicked.connect(self.add_replace)
        self.btnToggle.clicked.connect(self.toggle_enabled)
        self.btnSave.clicked.connect(self.save_and_emit)

    def refresh_ui(self):
        self.slotList.clear()
        # Show all 5 slots: slot1..slot5 and the files currently set
        for s in ["slot1", "slot2", "slot3", "slot4", "slot5"]:
            desc = s
            if s in self.am.rare and s in self.am.normal:
                desc += f"  (group) rare={self.am.rare.get(s)} normal={self.am.normal.get(s)}"
            elif s in self.am.single:
                desc += f"  (single) file={self.am.single.get(s)}"
            else:
                desc += "  (empty)"
            item = QListWidgetItem(desc)
            if s in self.am.enabled:
                item.setSelected(True)
            self.slotList.addItem(item)

    def add_replace(self):
        # user picks a slot to replace
        items = self.slotList.selectedItems()
        if not items:
            return
        idx = self.slotList.row(items[0])
        slot = f"slot{idx+1}"

        # Depending on slot, pick file(s)
        if slot in ("slot1", "slot2"):
            # Need two files: rare and normal
            rare_path, _ = QFileDialog.getOpenFileName(self, "选择 稀有动画 (10%)", "", "视频文件 (*.mp4 *.avi *.mov)")
            if not rare_path:
                return
            normal_path, _ = QFileDialog.getOpenFileName(self, "选择 常规动画 (90%)", "", "视频文件 (*.mp4 *.avi *.mov)")
            if not normal_path:
                return
            self.am.rare[slot] = rare_path
            self.am.normal[slot] = normal_path
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择 动画文件", "", "视频文件 (*.mp4 *.avi *.mov)")
            if not file_path:
                return
            self.am.single[slot] = file_path

        self.refresh_ui()

    def toggle_enabled(self):
        items = self.slotList.selectedItems()
        if not items:
            return
        idx = self.slotList.row(items[0])
        slot = f"slot{idx+1}"
        if slot in self.am.enabled:
            self.am.enabled.remove(slot)
        else:
            self.am.enabled.append(slot)
        self.refresh_ui()

    def save_and_emit(self):
        self.am.save()
        self.settingsChanged.emit()
