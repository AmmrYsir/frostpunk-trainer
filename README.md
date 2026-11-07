# Frostpunk Ultimate Trainer

A high-performance runtime memory trainer and research framework for **Frostpunk** (x86_64, Liquid Engine), featuring real-time telemetry, native developer engine cheat flag control, morale manipulation, climate modulation, and an intuitive PySide6 user interface.

---

## Reverse Engineering & Architecture Discoveries

During deep analysis of `Frostpunk.exe` (`0x140000000` Image Base):

1. **Engine Architecture**:
   - Liquid Engine utilizes an Entity Component System (ECS) alongside polymorphic singleton managers registered via RTTI `PropertyManager` and MSVC `CompleteObjectLocator`.
   - The root engine instance is **`FrostpunkGame`** located at a static module relative address: **`mem.base_address + 0x2b8cfa0`**.

2. **System Layout (via `FrostpunkGame`)**:
   - `+0x560` -> `FrostpunkCheatSystem`: Native developer cheat controller with bitmask flags.
   - `+0x1060` -> `FrostpunkTemperatureSystem`: Weather and ambient temperature level (`+0x21a0`).
   - `+0x19c0` -> `FrostpunkCitizenDiscontentSystem`: City discontent float metric (`+0x21e8`).
   - `+0x19e0` -> `FrostpunkCitizenHopeSystem`: City hope float metric (`+0x2164`) and population (`+0x2168`).
   - `+0x418` -> `FrostpunkGameStateGameplay`: Gameplay state and UI controller (`+0x18` -> `FrostpunkUIGameplayController`).

3. **Native Developer Engine Cheats (`FrostpunkCheatSystem`)**:
   - `0x00000002`: **Infinite Resources** (Coal, Wood, Steel, Steam Cores, Food Rations, Raw Food)
   - `0x00000004`: **Instant Construction** (Buildings finish immediately upon placement)
   - `0x00000010`: **Freeze Citizen Statistics** (Hunger, Cold, Sickness conditions do not deteriorate)
   - `0x00000040`: **Immortal Citizens** (Citizens will not die)
   - `0x00000080`: **No Critical Need Breakdown** (Prevents critical strikes, illness crises)
   - `0x00000100`: **Valid Placement Everywhere** (Build anywhere without terrain restrictions)
   - `0x00000200`: **Instant Research** (Workshop technologies finish immediately)
   - `0x00000400`: **Resource Boost** (High-yield extraction multiplier)
   - `0x00000800`: **Freeze Alignments**
   - `0x00001000`: **Reset Sociotech Cooldown** (Instant Book of Laws signing without cooldown)
   - `0x00002000`: **Instant Expedition Travel** (Scouts traverse the Frostland immediately)
   - `0x00004000`: **Unlock All Technologies**
   - `0x00008000`: **Unlock All Buildings**
   - `0x00010000`: **Unlock All Sociotech (Laws)**
   - `0x00020000`: **Unlock All Unlocks**
   - `0x00080000`: **Research All Tech (Complete Tree)**

---

## Trainer Features

### 📦 1. Resources & Economy
- **Infinite Resources**: Toggles native unlimited storage & construction consumption.
- **Resource Production Boost**: Increases resource yields.
- **Valid Placement Everywhere**: Allows buildings and streets to be built regardless of collision/slope limits.
- **Unlock All Buildings**: Makes every structure immediately buildable.

### ⚖️ 2. City Morale & Citizens
- **Live Morale Meters**: Real-time hope percentage bar and discontent status readout.
- **Max Hope (100%)**: Fills the hope bar to maximum city capacity.
- **Zero Discontent (0%)**: Resets discontent to absolute zero.
- **Instant Full Recovery**: Simultaneously maxes Hope and zeroes Discontent.
- **Immortal Citizens**: Prevents all citizen fatalities.
- **Freeze Citizen Needs**: Freezes hunger, health, and warmth levels.
- **No Critical Statistic Levels**: Eliminates crisis events from unfulfilled needs.

### ⚡ 3. Climate & Temperature
- **Live Temperature Indicator**: Displays current weather level and Celsius approximation.
- **Warmest Weather (-20°C / Level 1)**: Modulates ambient temperature to the warmest possible setting, lowering generator coal consumption.
- **Custom Climate Steps**: Set weather to Level 1, 2, or standard scenario progression.

### 🚀 4. Gameplay & Technology
- **Instant Construction**: Buildings are constructed instantaneously.
- **Instant Research**: Active Workshop research completes in 1 frame.
- **Instant Book of Laws**: Eliminates waiting cooldowns between law enactments.
- **Instant Expedition Travel**: Scouts travel instantaneously across Frostland map nodes.
- **Research All Tech**: Immediately researches the entire technology tree.
- **Unlock All Laws**: Unlocks every law branch in the Book of Laws.
- **Master Unlock**: Executes complete technology, building, and sociotech unlocks.

---

## Quick Start

### Prerequisites
- Python 3.10+ (x86_64)
- Installed dependencies: `PySide6`

### Running the Trainer
Launch the trainer from the repository root:
```powershell
python main.py
```
The trainer automatically detects and attaches to `Frostpunk.exe` whether launched before or after starting the game.
