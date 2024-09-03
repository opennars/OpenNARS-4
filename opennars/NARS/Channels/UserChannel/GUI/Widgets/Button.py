from PySide6.QtWidgets import QPushButton


class Button(QPushButton):
    def __init__(self, icon, text="", parent=None):
        super().__init__(icon, text, parent)
        self.setFixedSize(30, 30)
        self.setIcon(icon)
        self.setFlat(True)