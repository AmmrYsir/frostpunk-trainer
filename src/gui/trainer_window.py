"""Modern Frostpunk Trainer User Interface using PySide6.

Features real-time memory monitoring, tabbed cheat management,
responsive toggles, and live Hope/Discontent and Climate status gauges.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QGridLayout, QStatusBar,
    QTabWidget, QCheckBox, QProgressBar, QSpinBox, QFrame, QMessageBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QColor

from core.memory import MemoryManager
from cheats import FrostpunkTrainerEngine, CheatFlag


MODERN_DARK_STYLE = """
QMainWindow {
    background-color: #0f141a;
    color: #e0e6ed;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QTabWidget::pane {
    border: 1px solid #1f2937;
    background-color: #151b22;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f141a;
    color: #9ca3af;
    padding: 10px 18px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: bold;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #151b22;
    color: #00e5ff;
    border-bottom: 2px solid #00e5ff;
}

QTabBar::tab:hover {
    color: #ffffff;
    background-color: #1b232c;
}

QGroupBox {
    border: 1px solid #253041;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: bold;
    font-size: 13px;
    color: #00e5ff;
    background-color: #121820;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px 0 6px;
}

QCheckBox {
    color: #d1d5db;
    font-size: 13px;
    spacing: 8px;
    padding: 4px;
}

QCheckBox:hover {
    color: #ffffff;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #374151;
    background-color: #1a222d;
}

QCheckBox::indicator:checked {
    background-color: #00e5ff;
    border-color: #00bcd4;
}

QPushButton {
    background-color: #1e293b;
    color: #f3f4f6;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2e3e53;
    border-color: #00e5ff;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #0e7490;
}

QPushButton.primary {
    background-color: #0284c7;
    border-color: #38bdf8;
}

QPushButton.primary:hover {
    background-color: #0369a1;
}

QPushButton.warn {
    background-color: #b45309;
    border-color: #f59e0b;
}

QPushButton.warn:hover {
    background-color: #92400e;
}

QProgressBar {
    border: 1px solid #2d3748;
    border-radius: 6px;
    text-align: center;
    background-color: #111827;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #00e5ff;
    border-radius: 5px;
}

QStatusBar {
    background-color: #0b0f14;
    color: #9ca3af;
    font-size: 12px;
}
"""


class TrainerWindow(QMainWindow):
    """Main Trainer window with real-time UI controls."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frostpunk Ultimate Trainer")
        self.resize(600, 520)
        self.setStyleSheet(MODERN_DARK_STYLE)

        self.mem = MemoryManager("Frostpunk.exe")
        self.engine = FrostpunkTrainerEngine(self.mem)

        self.init_ui()

        # Polling timer for process attachment and live metrics
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status_and_metrics)
        self.timer.start(800)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # Header Status Bar
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("FROSTPUNK TRAINER")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #00e5ff; letter-spacing: 2px;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.status_pill = QLabel("SEARCHING PROCESS...")
        self.status_pill.setStyleSheet(
            "background-color: #374151; color: #f59e0b; padding: 4px 10px; "
            "border-radius: 12px; font-weight: bold; font-size: 11px;"
        )
        header_layout.addWidget(self.status_pill)
        main_layout.addWidget(header_frame)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_resources_tab(), "Resources")
        self.tabs.addTab(self.create_morale_tab(), "City Morale")
        self.tabs.addTab(self.create_climate_tab(), "Climate & Weather")
        self.tabs.addTab(self.create_gameplay_tab(), "Gameplay & Tech")
        main_layout.addWidget(self.tabs)

        # Bottom Quick Action Bar
        quick_frame = QFrame()
        quick_layout = QHBoxLayout(quick_frame)
        quick_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_heal_city = QPushButton("Instant Full Recovery (Hope + Discontent)")
        self.btn_heal_city.setStyleSheet("background-color: #065f46; border-color: #10b981; color: white;")
        self.btn_heal_city.clicked.connect(self.action_instant_full_recovery)
        quick_layout.addWidget(self.btn_heal_city)

        self.btn_reset_cheats = QPushButton("Reset All Cheats")
        self.btn_reset_cheats.clicked.connect(self.action_reset_all_cheats)
        quick_layout.addWidget(self.btn_reset_cheats)

        main_layout.addWidget(quick_frame)

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Trainer ready. Run Frostpunk or start a scenario.")

    # -------------------------------------------------------------
    # Tabs Construction
    # -------------------------------------------------------------
    def create_resources_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)

        box = QGroupBox("Resource & Construction Logistics")
        box_layout = QVBoxLayout()

        self.chk_inf_resources = QCheckBox("Infinite Resources (Coal, Wood, Steel, Steam Cores, Food)")
        self.chk_inf_resources.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.INFINITE_RESOURCES, chk))
        box_layout.addWidget(self.chk_inf_resources)

        self.chk_res_boost = QCheckBox("Resource Production Boost (Multiplier)")
        self.chk_res_boost.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.RESOURCES_BOOST, chk))
        box_layout.addWidget(self.chk_res_boost)

        self.chk_free_placement = QCheckBox("Valid Placement Everywhere (Free Street & Building Area)")
        self.chk_free_placement.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.VALID_PLACEMENT_EVERYWHERE, chk))
        box_layout.addWidget(self.chk_free_placement)

        self.chk_unlock_buildings = QCheckBox("Unlock All Buildings Instantly")
        self.chk_unlock_buildings.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.UNLOCK_ALL_BUILDINGS, chk))
        box_layout.addWidget(self.chk_unlock_buildings)

        box.setLayout(box_layout)
        layout.addWidget(box)
        layout.addStretch()
        return widget

    def create_morale_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)

        # Morale Indicators
        stats_group = QGroupBox("Live Morale Meters")
        stats_layout = QVBoxLayout()

        hope_layout = QHBoxLayout()
        hope_layout.addWidget(QLabel("Hope Level:"))
        self.hope_bar = QProgressBar()
        self.hope_bar.setRange(0, 100)
        self.hope_bar.setValue(0)
        self.hope_bar.setStyleSheet("QProgressBar::chunk { background-color: #38bdf8; }")
        hope_layout.addWidget(self.hope_bar)
        self.hope_label = QLabel("0 / 0 (0%)")
        self.hope_label.setFixedWidth(110)
        hope_layout.addWidget(self.hope_label)
        stats_layout.addLayout(hope_layout)

        disc_layout = QHBoxLayout()
        disc_layout.addWidget(QLabel("Discontent:"))
        self.disc_bar = QProgressBar()
        self.disc_bar.setRange(0, 100)
        self.disc_bar.setValue(0)
        self.disc_bar.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")
        disc_layout.addWidget(self.disc_bar)
        self.disc_label = QLabel("0.0")
        self.disc_label.setFixedWidth(110)
        disc_layout.addWidget(self.disc_label)
        stats_layout.addLayout(disc_layout)

        btns_layout = QHBoxLayout()
        self.btn_max_hope = QPushButton("Max Hope (100%)")
        self.btn_max_hope.clicked.connect(self.action_max_hope)
        btns_layout.addWidget(self.btn_max_hope)

        self.btn_zero_disc = QPushButton("Zero Discontent (0%)")
        self.btn_zero_disc.clicked.connect(self.action_zero_discontent)
        btns_layout.addWidget(self.btn_zero_disc)
        stats_layout.addLayout(btns_layout)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Citizen Protections
        protect_group = QGroupBox("Citizen Health & Conditions")
        protect_layout = QVBoxLayout()

        self.chk_immortal = QCheckBox("Immortal Citizens (Never Die from Cold, Starvation or Sickness)")
        self.chk_immortal.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.IMMORTAL_CITIZENS, chk))
        protect_layout.addWidget(self.chk_immortal)

        self.chk_freeze_stats = QCheckBox("Freeze Citizen Needs & Statistics (No Deterioration)")
        self.chk_freeze_stats.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.FREEZE_CITIZEN_STATISTICS, chk))
        protect_layout.addWidget(self.chk_freeze_stats)

        self.chk_no_critical = QCheckBox("No Critical Need Breakdown (Prevent Riots & Sickness Outbreaks)")
        self.chk_no_critical.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.NO_CRITICAL_STATISTIC_LEVELS, chk))
        protect_layout.addWidget(self.chk_no_critical)

        self.chk_freeze_alignments = QCheckBox("Freeze Alignments (Prevent Discontent Polarization)")
        self.chk_freeze_alignments.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.FREEZE_ALIGNMENTS, chk))
        protect_layout.addWidget(self.chk_freeze_alignments)

        protect_group.setLayout(protect_layout)
        layout.addWidget(protect_group)
        layout.addStretch()
        return widget

    def create_climate_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)

        climate_group = QGroupBox("City Temperature & Weather Control")
        climate_layout = QVBoxLayout()

        self.temp_status_label = QLabel("Current Level: Normal")
        self.temp_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00e5ff;")
        climate_layout.addWidget(self.temp_status_label)

        temp_btn_layout = QHBoxLayout()
        self.btn_warm_weather = QPushButton("Set Warmest Weather (-20°C / Level 1)")
        self.btn_warm_weather.clicked.connect(self.action_set_warmest_weather)
        temp_btn_layout.addWidget(self.btn_warm_weather)

        self.btn_mild_weather = QPushButton("Set Level 2 (-30°C)")
        self.btn_mild_weather.clicked.connect(lambda: self.engine.set_temperature_level(2))
        temp_btn_layout.addWidget(self.btn_mild_weather)

        climate_layout.addLayout(temp_btn_layout)

        desc_label = QLabel(
            "Note: Modifying the temperature level alters ambient weather for the entire city, "
            "drastically reducing generator coal consumption and preventing cold sickness."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #9ca3af; font-size: 12px; margin-top: 6px;")
        climate_layout.addWidget(desc_label)

        climate_group.setLayout(climate_layout)
        layout.addWidget(climate_group)
        layout.addStretch()
        return widget

    def create_gameplay_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)

        gameplay_group = QGroupBox("Fast Research, Build & Exploration")
        g_layout = QVBoxLayout()

        self.chk_instant_build = QCheckBox("Instant Construction (Buildings finished instantly)")
        self.chk_instant_build.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.INSTANT_CONSTRUCTION, chk))
        g_layout.addWidget(self.chk_instant_build)

        self.chk_instant_research = QCheckBox("Instant Research (Workshop technologies finish instantly)")
        self.chk_instant_research.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.INSTANT_RESEARCH, chk))
        g_layout.addWidget(self.chk_instant_research)

        self.chk_instant_laws = QCheckBox("Instant Book of Laws (No Cooldown Between Signings)")
        self.chk_instant_laws.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.RESET_SOCIOTECH_COOLDOWN, chk))
        g_layout.addWidget(self.chk_instant_laws)

        self.chk_instant_expedition = QCheckBox("Instant Expedition Travel (Scouts move immediately)")
        self.chk_instant_expedition.toggled.connect(lambda chk: self.toggle_cheat(CheatFlag.INSTANT_EXPEDITION_TRAVEL, chk))
        g_layout.addWidget(self.chk_instant_expedition)

        g_layout.addSpacing(6)
        btn_grid = QGridLayout()

        self.btn_unlock_all_tech = QPushButton("Unlock All Technologies")
        self.btn_unlock_all_tech.clicked.connect(lambda: self.engine.trigger_one_shot_cheat(CheatFlag.UNLOCK_ALL_TECHNOLOGIES))
        btn_grid.addWidget(self.btn_unlock_all_tech, 0, 0)

        self.btn_research_all_tech = QPushButton("Research All Tech (Complete Tree)")
        self.btn_research_all_tech.clicked.connect(lambda: self.engine.trigger_one_shot_cheat(CheatFlag.RESEARCH_ALL_TECH))
        btn_grid.addWidget(self.btn_research_all_tech, 0, 1)

        self.btn_unlock_all_laws = QPushButton("Unlock All Laws (Sociotech)")
        self.btn_unlock_all_laws.clicked.connect(lambda: self.engine.trigger_one_shot_cheat(CheatFlag.UNLOCK_ALL_SOCIOTECH))
        btn_grid.addWidget(self.btn_unlock_all_laws, 1, 0)

        self.btn_master_unlock = QPushButton("Master Unlock (Everything)")
        self.btn_master_unlock.clicked.connect(lambda: self.engine.trigger_one_shot_cheat(CheatFlag.UNLOCK_ALL_UNLOCKS))
        btn_grid.addWidget(self.btn_master_unlock, 1, 1)

        g_layout.addLayout(btn_grid)
        gameplay_group.setLayout(g_layout)
        layout.addWidget(gameplay_group)
        layout.addStretch()
        return widget

    # -------------------------------------------------------------
    # Cheat Action Handlers
    # -------------------------------------------------------------
    def toggle_cheat(self, flag: CheatFlag, enable: bool):
        if not self.engine.is_connected:
            return
        self.engine.set_cheat_flag(flag, enable)

    def action_max_hope(self):
        if not self.engine.is_connected:
            return
        self.engine.set_max_hope()
        self.statusBar.showMessage("Max Hope applied (100%).")

    def action_zero_discontent(self):
        if not self.engine.is_connected:
            return
        self.engine.set_zero_discontent()
        self.statusBar.showMessage("Zero Discontent applied (0%).")

    def action_instant_full_recovery(self):
        if not self.engine.is_connected:
            return
        self.engine.set_max_hope()
        self.engine.set_zero_discontent()
        self.statusBar.showMessage("Full City Recovery applied: 100% Hope, 0% Discontent.")

    def action_set_warmest_weather(self):
        if not self.engine.is_connected:
            return
        self.engine.set_warmest_weather()
        self.statusBar.showMessage("Temperature set to Level 1 (-20°C).")

    def action_reset_all_cheats(self):
        if not self.engine.is_connected:
            return
        # Reset to base default 0x8 (Debug events)
        cheat_sys = self.engine.get_system_address(self.engine.OFFSET_CHEAT_SYSTEM)
        if cheat_sys:
            self.mem.write_int32(cheat_sys + self.engine.OFFSET_CHEAT_FLAGS, 0x8)
            ver = self.mem.read_int32(cheat_sys + self.engine.OFFSET_CHEAT_VERSION) or 0
            self.mem.write_int32(cheat_sys + self.engine.OFFSET_CHEAT_VERSION, ver + 1)
        self.sync_checkboxes_with_game()
        self.statusBar.showMessage("All cheats reset to standard default.")

    def sync_checkboxes_with_game(self):
        flags = self.engine.get_cheat_flags()
        self.chk_inf_resources.blockSignals(True)
        self.chk_res_boost.blockSignals(True)
        self.chk_free_placement.blockSignals(True)
        self.chk_unlock_buildings.blockSignals(True)
        self.chk_immortal.blockSignals(True)
        self.chk_freeze_stats.blockSignals(True)
        self.chk_no_critical.blockSignals(True)
        self.chk_freeze_alignments.blockSignals(True)
        self.chk_instant_build.blockSignals(True)
        self.chk_instant_research.blockSignals(True)
        self.chk_instant_laws.blockSignals(True)
        self.chk_instant_expedition.blockSignals(True)

        self.chk_inf_resources.setChecked(bool(flags & CheatFlag.INFINITE_RESOURCES))
        self.chk_res_boost.setChecked(bool(flags & CheatFlag.RESOURCES_BOOST))
        self.chk_free_placement.setChecked(bool(flags & CheatFlag.VALID_PLACEMENT_EVERYWHERE))
        self.chk_unlock_buildings.setChecked(bool(flags & CheatFlag.UNLOCK_ALL_BUILDINGS))
        self.chk_immortal.setChecked(bool(flags & CheatFlag.IMMORTAL_CITIZENS))
        self.chk_freeze_stats.setChecked(bool(flags & CheatFlag.FREEZE_CITIZEN_STATISTICS))
        self.chk_no_critical.setChecked(bool(flags & CheatFlag.NO_CRITICAL_STATISTIC_LEVELS))
        self.chk_freeze_alignments.setChecked(bool(flags & CheatFlag.FREEZE_ALIGNMENTS))
        self.chk_instant_build.setChecked(bool(flags & CheatFlag.INSTANT_CONSTRUCTION))
        self.chk_instant_research.setChecked(bool(flags & CheatFlag.INSTANT_RESEARCH))
        self.chk_instant_laws.setChecked(bool(flags & CheatFlag.RESET_SOCIOTECH_COOLDOWN))
        self.chk_instant_expedition.setChecked(bool(flags & CheatFlag.INSTANT_EXPEDITION_TRAVEL))

        self.chk_inf_resources.blockSignals(False)
        self.chk_res_boost.blockSignals(False)
        self.chk_free_placement.blockSignals(False)
        self.chk_unlock_buildings.blockSignals(False)
        self.chk_immortal.blockSignals(False)
        self.chk_freeze_stats.blockSignals(False)
        self.chk_no_critical.blockSignals(False)
        self.chk_freeze_alignments.blockSignals(False)
        self.chk_instant_build.blockSignals(False)
        self.chk_instant_research.blockSignals(False)
        self.chk_instant_laws.blockSignals(False)
        self.chk_instant_expedition.blockSignals(False)

    # -------------------------------------------------------------
    # Live Polling & Updates
    # -------------------------------------------------------------
    def update_status_and_metrics(self):
        if not self.engine.is_connected:
            if self.mem.attach():
                self.status_pill.setText(f"CONNECTED (PID {self.mem.process_id})")
                self.status_pill.setStyleSheet(
                    "background-color: #064e3b; color: #34d399; padding: 4px 10px; "
                    "border-radius: 12px; font-weight: bold; font-size: 11px;"
                )
                self.statusBar.showMessage(f"Attached to Frostpunk (Base: 0x{self.mem.base_address:x})")
                self.sync_checkboxes_with_game()
        else:
            # Check if alive
            if not self.mem.read_bytes(self.mem.base_address, 1):
                self.mem.detach()
                self.status_pill.setText("DISCONNECTED")
                self.status_pill.setStyleSheet(
                    "background-color: #7f1d1d; color: #f87171; padding: 4px 10px; "
                    "border-radius: 12px; font-weight: bold; font-size: 11px;"
                )
                self.statusBar.showMessage("Frostpunk closed. Waiting for game...")
                return

            # Read live Morale stats
            hope_val, citizens, hope_pct, discontent = self.engine.get_morale_stats()
            self.hope_bar.setValue(int(hope_pct))
            self.hope_label.setText(f"{hope_val:.1f} / {citizens} ({hope_pct:.0f}%)")

            disc_pct = min(100.0, max(0.0, discontent * 100.0))
            self.disc_bar.setValue(int(disc_pct))
            self.disc_label.setText(f"{discontent:.2f} ({disc_pct:.0f}%)")

            # Read Temperature Level
            temp_level = self.engine.get_temperature_level()
            temp_celsius = -20 - max(0, temp_level - 1) * 10
            self.temp_status_label.setText(f"Current Level: {temp_level} (~{temp_celsius}°C)")

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
