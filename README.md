# 🏡 TerraDesk — Desktop Village Simulation

A complete, open-source **isometric village simulation** that runs as a desktop overlay on Windows.
Build a thriving medieval village, manage citizens, economy, resources and weather — all in a beautiful pixel-art isometric world.

![TerraDesk Screenshot](docs/screenshot.png)

## ✨ Features

| Category | Details |
|---|---|
| 🏗 **14 Building Types** | Houses, Farms, Markets, Schools, Hospitals, Churches, Taverns, Wells, Mills, Blacksmiths, Warehouses, Roads, Bridges, Trees |
| 👥 **Autonomous Citizens** | Each citizen has hunger, energy, social & happiness needs. They find homes, jobs, eat, sleep, socialise and wander. |
| 💰 **Full Economy** | Tax collection, salaries, resource production (food/wood/stone), market trading |
| 🌤 **Day/Night & Seasons** | Dynamic sky colour, window glow at night, seasonal tree/crop colours, 4 seasons |
| 🌧 **Weather System** | Clear, cloudy, rain, heavy rain, snow, storm, fog — with particle effects |
| ⚡ **God Mode** | 12 direct-intervention tools: spawn citizens, add resources, meteor strike, instant-build |
| 🖥 **Desktop Integration** | Always-on-top, wallpaper mode (behind windows), click-through (Windows) |
| 💾 **Save / Load** | JSON saves in `~/.terradesk/saves/`, autosave every 5 min |
| 📦 **Single EXE** | Packaged with PyInstaller — no Python install needed |

## 🚀 Quick Start

### Option A — Download the EXE (Windows)
1. Go to [Releases](../../releases/latest)
2. Download `TerraDesk.exe`
3. Double-click to run

### Option B — Run from Source

```bash
# Python 3.11+ required (3.14 works with pygame-ce)
git clone https://github.com/YOUR_USERNAME/terradesk.git
cd terradesk
pip install -r requirements.txt
python main.py
```

## 🕹 Controls

| Key / Action | Effect |
|---|---|
| **Left click** (build mode) | Place selected building |
| **Right click / drag** | Pan camera |
| **Scroll wheel** | Zoom in / out |
| **Space** | Pause / resume |
| **1–4** | Set simulation speed |
| **R** | Reset camera |
| **Escape** | Cancel build / deselect |
| **F5** | Save game |
| **F9** | Load game |

## 🏗 Building

```bash
python scripts/build_exe.py
# Output: dist/TerraDesk.exe
```

## 📁 Project Structure

```
terradesk/
├── main.py                  # Entry point
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── constants.py     # All game constants & colours
│   │   ├── camera.py        # Isometric camera (pan, zoom)
│   │   ├── grid.py          # 60×60 tile world
│   │   ├── renderer.py      # Procedural isometric drawing
│   │   └── game.py          # Main game loop
│   ├── world/
│   │   ├── time_manager.py  # Day/night/seasons
│   │   ├── weather.py       # Particle weather system
│   │   └── environment.py   # Weather coordinator
│   ├── buildings/
│   │   ├── building_types.py # 14-type catalogue
│   │   ├── building.py      # Building state & construction
│   │   └── building_manager.py
│   ├── citizens/
│   │   ├── citizen.py       # AI with needs state machine
│   │   ├── citizen_manager.py
│   │   └── pathfinding.py   # A* pathfinding
│   ├── economy/
│   │   └── economy.py       # Tax, salaries, resources
│   ├── ui/
│   │   ├── toolbar.py       # Top bar
│   │   ├── sidebar.py       # Right panel (7 modes)
│   │   ├── hud.py           # Notifications, tooltips, build ghost
│   │   └── ui_base.py       # Shared drawing primitives
│   └── save/
│       └── save_manager.py  # JSON save/load
└── scripts/
    └── build_exe.py         # EXE builder
```

## 📋 Requirements

- Python 3.11+ (3.14 supported via `pygame-ce`)
- `pygame-ce >= 2.5.0`
- `pywin32 >= 305` (Windows desktop integration)
- `pyinstaller >= 6.0` (build only)

## 📄 License

MIT — see [LICENSE](LICENSE)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)