"""Modern UI for Frostpunk Trainer built with PySide6."""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QGridLayout, QStatusBar
)
from PySide6.QtCore import QTimer, Qt
from core.memory import MemoryManager


class TrainerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frostpunk Trainer")
        self.setFixedSize(520, 480)

        self.mem = MemoryManager("Frostpunk.exe")
        self.init_ui()

        # Attachment polling timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_game_connection)
        self.timer.start(1000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status Banner
        self.status_label = QLabel("Searching for Frostpunk.exe...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff9800;")
        main_layout.addWidget(self.status_label)

        # Cheats Panel
        resources_group = QGroupBox("Resources & Economy")
        grid = QGridLayout()

        self.btn_coal = QPushButton("Add 5,000 Coal")
        self.btn_wood = QPushButton("Add 2,500 Wood")
        self.btn_steel = QPushButton("Add 2,500 Steel")
        self.btn_food = QPushButton("Add 2,500 Rations")
        self.btn_cores = QPushButton("Add 10 Steam Cores")

        grid.addWidget(self.btn_coal, 0, 0)
        grid.addWidget(self.btn_wood, 0, 1)
        grid.addWidget(self.btn_steel, 1, 0)
        grid.addWidget(self.btn_food, 1, 1)
        grid.addWidget(self.btn_cores, 2, 0, 1, 2)
        resources_group.setLayout(grid)
        main_layout.addWidget(resources_group)

        # City Morale Panel
        morale_group = QGroupBox("City Conditions & Morale")
        morale_layout = QVBoxLayout()
        self.btn_max_hope = QPushButton("Max Hope")
        self.btn_zero_discontent = QPushButton("Zero Discontent")
        self.btn_no_generator_stress = QPushButton("Reset Generator Stress")

        morale_layout.addWidget(self.btn_max_hope)
        morale_layout.addWidget(self.btn_zero_discontent)
        morale_layout.addWidget(self.btn_no_generator_stress)
        morale_group.setLayout(morale_layout)
        main_layout.addWidget(morale_group)

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Trainer initialized.")

    def check_game_connection(self):
        if not self.mem.handle:
            if self.mem.attach():
                self.status_label.setText(f"Connected to Frostpunk (PID: {self.mem.process_id})")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4caf50;")
                self.statusBar.showMessage(f"Attached at base 0x{self.mem.base_address:x}")
        else:
            # Verify if process is still alive by reading 1 byte
            if not self.mem.read_bytes(self.mem.base_address, 1):
                self.mem.detach()
                self.status_label.setText("Frostpunk disconnected. Waiting for process...")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f44336;")
                self.statusBar.showMessage("Disconnected.")

    def closeEvent(self, event):
        self.mem.detach()
        event.accept()


def run_gui():
    app = QApplication(sys.argv)
    window = TrainerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_gui())
