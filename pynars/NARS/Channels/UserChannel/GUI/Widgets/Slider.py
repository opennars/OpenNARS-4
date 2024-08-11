from PySide6.QtWidgets import QSlider, QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout

class Slider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, min=0, max=100, default=50, text="", parent=None):
        super().__init__(orientation, parent)
        self.setRange(min, max)
        self.setSingleStep(1)
        self.setValue(default)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 30px;
                background: rgba(255, 255, 255, 0);
            }
            QSlider::sub-page:horizontal {
                height: 30px;
                background: rgba(255, 255, 255, 0.3);
            }
            QSlider::add-page:horizontal {
                height: 30px;
                background: rgba(0, 0, 0, 0.5);
            }
            QSlider::handle:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        layout = QStackedLayout(self)
        self.setLayout(layout)
        self.text = text
        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.label)
        self._on_value_chagned(default)
        self.valueChanged.connect(self._on_value_chagned)

    def _on_value_chagned(self, value):
        self.label.setText(f"{self.text}{value}")

    def value_changed_connect(self, func):
        def _func(value):
            self._on_value_chagned(value)
            func(value)
        self.valueChanged.connect(_func)
        _func(self.value())
