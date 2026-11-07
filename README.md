# Frostpunk Trainer Development Workspace

## Architecture & Overview
- **Target Process**: `Frostpunk.exe` (x86_64 PE)
- **Target Installation Path**: `D:\SteamLibrary\steamapps\common\Frostpunk` (Strictly Read-Only, no modifications permitted)
- **Trainer Implementation**: Python (PySide6 / CustomTkinter UI, `ctypes` Win32 Memory Engine)

## Directory Structure
- `src/` - Trainer source code
  - `core/` - Memory reading/writing, pattern scanning, process attachment
  - `cheats/` - Resource managers, game feature hooks, pointer definitions
  - `gui/` - User interface (Modern UI via PySide6 or CustomTkinter)
- `tests/` - Unit and integration tests
- `research/` - Static analysis logs, pattern signatures, pointer offsets

## Core Safety Rules
1. **Never modify files in the game installation directory (`D:\SteamLibrary\steamapps\common\Frostpunk`)**.
2. All game memory manipulations occur at runtime via Windows API (`OpenProcess`, `ReadProcessMemory`, `WriteProcessMemory`, `VirtualProtectEx`).
