"""
TerraDesk – Building Type Definitions
Data-driven building catalogue.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple
from src.core.constants import BUILDING_COSTS


@dataclass
class BuildingDef:
    name: str
    btype: str
    width: int = 1
    height: int = 1
    description: str = ""
    icon: str = "🏠"
    # What resources/workers it provides
    provides_jobs: int = 0
    provides_housing: int = 0
    food_production: float = 0.0
    service_radius: int = 5
    happiness_bonus: float = 0.0
    # Build requirements
    requires_road: bool = False
    # Category for toolbar
    category: str = "buildings"


BUILDING_CATALOGUE: Dict[str, BuildingDef] = {
    "house": BuildingDef(
        name="House", btype="house",
        width=1, height=1,
        description="A cosy home for 4 citizens.",
        icon="🏠", provides_housing=4, category="buildings"
    ),
    "farm": BuildingDef(
        name="Farm", btype="farm",
        width=2, height=2,
        description="Produces food for the village.",
        icon="🌾", provides_jobs=2, food_production=20.0, category="production"
    ),
    "market": BuildingDef(
        name="Market", btype="market",
        width=2, height=2,
        description="Citizens buy and sell goods here.",
        icon="🏪", provides_jobs=3, happiness_bonus=0.05, category="commerce"
    ),
    "school": BuildingDef(
        name="School", btype="school",
        width=2, height=2,
        description="Educates children, boosts village growth.",
        icon="🏫", provides_jobs=4, happiness_bonus=0.08, service_radius=8, category="services"
    ),
    "hospital": BuildingDef(
        name="Hospital", btype="hospital",
        width=2, height=2,
        description="Keeps citizens healthy.",
        icon="🏥", provides_jobs=5, happiness_bonus=0.10, service_radius=10, category="services"
    ),
    "church": BuildingDef(
        name="Church", btype="church",
        width=2, height=2,
        description="A place of worship. Boosts happiness greatly.",
        icon="⛪", provides_jobs=2, happiness_bonus=0.15, service_radius=12, category="services"
    ),
    "tavern": BuildingDef(
        name="Tavern", btype="tavern",
        width=1, height=1,
        description="Citizens relax here. Boosts social happiness.",
        icon="🍺", provides_jobs=2, happiness_bonus=0.08, category="commerce"
    ),
    "well": BuildingDef(
        name="Well", btype="well",
        width=1, height=1,
        description="Provides fresh water to nearby houses.",
        icon="💧", happiness_bonus=0.03, service_radius=4, category="infrastructure"
    ),
    "mill": BuildingDef(
        name="Windmill", btype="mill",
        width=1, height=1,
        description="Grinds grain into flour.",
        icon="⚙️", provides_jobs=1, food_production=10.0, category="production"
    ),
    "blacksmith": BuildingDef(
        name="Blacksmith", btype="blacksmith",
        width=1, height=1,
        description="Crafts tools and weapons.",
        icon="⚒️", provides_jobs=2, category="production"
    ),
    "warehouse": BuildingDef(
        name="Warehouse", btype="warehouse",
        width=2, height=1,
        description="Stores resources for the village.",
        icon="🏭", provides_jobs=1, category="infrastructure"
    ),
    "road": BuildingDef(
        name="Road", btype="road",
        width=1, height=1,
        description="Connects buildings. Citizens move faster.",
        icon="🛣️", category="infrastructure"
    ),
    "tree": BuildingDef(
        name="Tree", btype="tree",
        width=1, height=1,
        description="Decorative tree. Boosts happiness slightly.",
        icon="🌲", happiness_bonus=0.01, category="nature"
    ),
    "bridge": BuildingDef(
        name="Bridge", btype="bridge",
        width=1, height=1,
        description="Allows crossing rivers.",
        icon="🌉", category="infrastructure"
    ),
}


def get_building_def(btype: str) -> BuildingDef:
    return BUILDING_CATALOGUE.get(btype, BUILDING_CATALOGUE["house"])


def get_cost(btype: str) -> dict:
    return BUILDING_COSTS.get(btype, {"money": 100})


def get_all_by_category(category: str):
    return [(k, v) for k, v in BUILDING_CATALOGUE.items() if v.category == category]


CATEGORIES = ["buildings", "production", "commerce", "services", "infrastructure", "nature"]
CATEGORY_ICONS = {
    "buildings": "🏠",
    "production": "⚙️",
    "commerce": "💰",
    "services": "🏥",
    "infrastructure": "🛣️",
    "nature": "🌲",
}