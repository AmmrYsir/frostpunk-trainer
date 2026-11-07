"""Frostpunk Trainer Core Engine and Cheats Implementation.

Interfaces directly with the Liquid Engine runtime structures inside Frostpunk.exe:
- FrostpunkGame root singleton (Fixed RVA: 0x2b8cfa0)
- FrostpunkCheatSystem (Offset +0x560): Native developer engine flags
- FrostpunkCitizenHopeSystem (Offset +0x19e0): TotalHope (+0x2164), Citizens (+0x2168)
- FrostpunkCitizenDiscontentSystem (Offset +0x19c0): TotalDiscontent (+0x21e8)
- FrostpunkTemperatureSystem (Offset +0x1060): CurrentTemperature (+0x21a0)
"""

from enum import IntFlag
from typing import Optional, Tuple, Dict
from core.memory import MemoryManager


class CheatFlag(IntFlag):
    """Native developer engine cheat flags in FrostpunkCheatSystem."""
    NONE = 0x0
    INFINITE_RESOURCES = 0x2
    INSTANT_CONSTRUCTION = 0x4
    DEBUG_EVENTS = 0x8
    FREEZE_CITIZEN_STATISTICS = 0x10
    DEBUG_BARS = 0x20
    IMMORTAL_CITIZENS = 0x40
    NO_CRITICAL_STATISTIC_LEVELS = 0x80
    VALID_PLACEMENT_EVERYWHERE = 0x100
    INSTANT_RESEARCH = 0x200
    RESOURCES_BOOST = 0x400
    FREEZE_ALIGNMENTS = 0x800
    RESET_SOCIOTECH_COOLDOWN = 0x1000
    INSTANT_EXPEDITION_TRAVEL = 0x2000
    UNLOCK_ALL_TECHNOLOGIES = 0x4000
    UNLOCK_ALL_BUILDINGS = 0x8000
    UNLOCK_ALL_SOCIOTECH = 0x10000
    UNLOCK_ALL_UNLOCKS = 0x20000
    ENABLE_TIME_IN_FROSTLAND = 0x40000
    RESEARCH_ALL_TECH = 0x80000
    RESEARCH_CUSTOM_TECH = 0x100000


class FrostpunkTrainerEngine:
    """Trainer engine that interfaces with running Frostpunk memory."""

    FROSTPUNK_GAME_RVA = 0x2b8cfa0

    # Offsets inside FrostpunkGame singleton
    OFFSET_CHEAT_SYSTEM = 0x560
    OFFSET_TEMPERATURE_SYSTEM = 0x1060
    OFFSET_DISCONTENT_SYSTEM = 0x19c0
    OFFSET_HOPE_SYSTEM = 0x19e0

    # Offsets inside specific systems
    OFFSET_CHEAT_VERSION = 0x30
    OFFSET_CHEAT_FLAGS = 0x68
    OFFSET_HOPE_VALUE = 0x2164
    OFFSET_HOPE_CITIZENS = 0x2168
    OFFSET_DISCONTENT_VALUE = 0x21e8
    OFFSET_TEMPERATURE_LEVEL = 0x21a0

    def __init__(self, mem: Optional[MemoryManager] = None):
        self.mem = mem or MemoryManager("Frostpunk.exe")

    @property
    def is_connected(self) -> bool:
        return self.mem.handle is not None and self.mem.base_address != 0

    def get_game_address(self) -> int:
        if not self.is_connected:
            return 0
        return self.mem.base_address + self.FROSTPUNK_GAME_RVA

    def get_system_address(self, offset: int) -> int:
        game_addr = self.get_game_address()
        if not game_addr:
            return 0
        sys_ptr = self.mem.read_int64(game_addr + offset)
        return sys_ptr or 0

    # -------------------------------------------------------------
    # Native Cheat Flags
    # -------------------------------------------------------------
    def get_cheat_flags(self) -> int:
        cheat_sys = self.get_system_address(self.OFFSET_CHEAT_SYSTEM)
        if not cheat_sys:
            return 0
        val = self.mem.read_int32(cheat_sys + self.OFFSET_CHEAT_FLAGS)
        return val if val is not None else 0

    def set_cheat_flag(self, flag: CheatFlag, enable: bool) -> bool:
        cheat_sys = self.get_system_address(self.OFFSET_CHEAT_SYSTEM)
        if not cheat_sys:
            return False

        current = self.get_cheat_flags()
        new_flags = (current | flag) if enable else (current & ~flag)

        success = self.mem.write_int32(cheat_sys + self.OFFSET_CHEAT_FLAGS, new_flags)
        if success:
            # Increment sequence version so subsystems update immediately
            ver = self.mem.read_int32(cheat_sys + self.OFFSET_CHEAT_VERSION) or 0
            self.mem.write_int32(cheat_sys + self.OFFSET_CHEAT_VERSION, ver + 1)
        return success

    def is_cheat_enabled(self, flag: CheatFlag) -> bool:
        current = self.get_cheat_flags()
        return bool(current & flag)

    def trigger_one_shot_cheat(self, flag: CheatFlag) -> bool:
        """Enables a one-shot cheat, bumps version, then clears the flag."""
        self.set_cheat_flag(flag, True)
        return self.set_cheat_flag(flag, False)

    # -------------------------------------------------------------
    # Morale & City Statistics
    # -------------------------------------------------------------
    def get_morale_stats(self) -> Tuple[float, int, float, float]:
        """Returns (hope_val, citizen_count, hope_percent, discontent_val)."""
        hope_sys = self.get_system_address(self.OFFSET_HOPE_SYSTEM)
        disc_sys = self.get_system_address(self.OFFSET_DISCONTENT_SYSTEM)

        hope_val = self.mem.read_float(hope_sys + self.OFFSET_HOPE_VALUE) if hope_sys else 0.0
        citizens = self.mem.read_int32(hope_sys + self.OFFSET_HOPE_CITIZENS) if hope_sys else 0
        discontent = self.mem.read_float(disc_sys + self.OFFSET_DISCONTENT_VALUE) if disc_sys else 0.0

        hope_percent = 0.0
        if citizens and citizens > 0 and hope_val is not None:
            hope_percent = min(100.0, max(0.0, (hope_val / citizens) * 100.0))

        return (hope_val or 0.0, citizens or 0, hope_percent, discontent or 0.0)

    def set_max_hope(self) -> bool:
        hope_sys = self.get_system_address(self.OFFSET_HOPE_SYSTEM)
        if not hope_sys:
            return False
        citizens = self.mem.read_int32(hope_sys + self.OFFSET_HOPE_CITIZENS) or 45
        return self.mem.write_float(hope_sys + self.OFFSET_HOPE_VALUE, float(citizens))

    def set_zero_discontent(self) -> bool:
        disc_sys = self.get_system_address(self.OFFSET_DISCONTENT_SYSTEM)
        if not disc_sys:
            return False
        return self.mem.write_float(disc_sys + self.OFFSET_DISCONTENT_VALUE, 0.0)

    # -------------------------------------------------------------
    # Climate & Temperature
    # -------------------------------------------------------------
    def get_temperature_level(self) -> int:
        temp_sys = self.get_system_address(self.OFFSET_TEMPERATURE_SYSTEM)
        if not temp_sys:
            return 0
        val = self.mem.read_int32(temp_sys + self.OFFSET_TEMPERATURE_LEVEL)
        return val if val is not None else 0

    def set_temperature_level(self, level: int) -> bool:
        temp_sys = self.get_system_address(self.OFFSET_TEMPERATURE_SYSTEM)
        if not temp_sys:
            return False
        return self.mem.write_int32(temp_sys + self.OFFSET_TEMPERATURE_LEVEL, level)

    def set_warmest_weather(self) -> bool:
        """Sets temperature level to 1 (-20°C / baseline pleasant)."""
        return self.set_temperature_level(1)
