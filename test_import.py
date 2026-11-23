import sys, traceback
sys.path.insert(0, '.')

modules = [
    ('constants','src.core.constants'),
    ('camera','src.core.camera'),
    ('grid','src.core.grid'),
    ('renderer','src.core.renderer'),
    ('time_manager','src.world.time_manager'),
    ('weather','src.world.weather'),
    ('environment','src.world.environment'),
    ('building_types','src.buildings.building_types'),
    ('building','src.buildings.building'),
    ('building_manager','src.buildings.building_manager'),
    ('pathfinding','src.citizens.pathfinding'),
    ('citizen','src.citizens.citizen'),
    ('citizen_manager','src.citizens.citizen_manager'),
    ('economy','src.economy.economy'),
    ('ui_base','src.ui.ui_base'),
    ('toolbar','src.ui.toolbar'),
    ('sidebar','src.ui.sidebar'),
    ('hud','src.ui.hud'),
    ('save_manager','src.save.save_manager'),
    ('game','src.core.game'),
]

for name, mod in modules:
    try:
        __import__(mod, fromlist=[''])
        print(f'  OK  {name}')
    except Exception as e:
        print(f'\nFAIL  {name}:')
        traceback.print_exc()
        print()
