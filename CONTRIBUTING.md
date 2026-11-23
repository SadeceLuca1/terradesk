# Contributing to TerraDesk

Thank you for your interest in contributing to TerraDesk!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/terradesk.git
   cd terradesk
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate # Linux/macOS
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the game:
   ```bash
   python main.py
   ```

## Project Structure

```
terradesk/
├── main.py                  # Entry point
├── src/
│   ├── core/                # Engine: camera, grid, renderer, constants
│   ├── world/               # Time, weather, environment
│   ├── buildings/           # Building types, placement, management
│   ├── citizens/            # Citizen AI, pathfinding, needs
│   ├── economy/             # Currency, taxes, resources, trade
│   ├── ui/                  # Toolbar, sidebar, HUD, tooltips
│   └── save/                # Save/load manager
├── assets/                  # Sprites, fonts, sounds (future)
├── data/                    # JSON data files (future)
└── scripts/                 # Build / release scripts
```

## Ways to Contribute

- **Bug fixes** – Check open issues and submit PRs
- **New building types** – Add to `src/buildings/building_types.py`
- **Citizen behaviours** – Extend `src/citizens/citizen.py`
- **Weather effects** – Improve `src/world/weather.py`
- **Asset creation** – Pixel art tiles and sprites
- **Performance** – Profiling and optimisation
- **Documentation** – README, code comments, wiki

## Code Style

- Follow PEP 8
- Add docstrings to all public classes and methods
- Keep modules under 400 lines where possible
- No hardcoded magic numbers – use `src/core/constants.py`

## Submitting a PR

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Write your code and add tests if applicable
3. Run `python main.py --test-engine` to check basic functionality
4. Commit with a descriptive message
5. Push and open a PR against `main`

## Code of Conduct

Be respectful, constructive, and welcoming to all contributors.
