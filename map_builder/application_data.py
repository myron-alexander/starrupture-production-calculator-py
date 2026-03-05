"""
Provides data to the application.
"""

#---------------------------------------------------------------------------------------------------

__all__ = [
    "GameData",
    "load_game_data"
]

#---------------------------------------------------------------------------------------------------

# The module path containing starrupture is added in the virtual environment using file:
#    .venv/lib/pythonV.VV/site-packages/starrupture.pth
# where the "V"s are the python version number. The path to add is the absolute path to the
# parent folder of "starrupture" and "srcalc.py".

from starrupture.sr_game_data import *

#---------------------------------------------------------------------------------------------------

class GameData:
    def __init__(
            self,
            items:list[ItemRecord],
            inputs:list[RecipeInputRecord],
            raw_items:list[RawItemRecord],
            buildings:list[BuildingRecord]) -> None:

        self.item_definitions = items
        self.item_input_definitions = inputs
        self.raw_item_definitions = raw_items
        self.building_definitions = buildings

        self.item_definitions.sort(key=lambda i: i.item_name.lower())
        self.item_input_definitions.sort(key=lambda i: f"{i.item_name};{i.input_name}".lower())
        self.raw_item_definitions.sort(key=lambda i: f"{i.item_name};{i.variant}".lower())
        self.building_definitions.sort(key=lambda i: i.building_name)

        self.craftable_items = list(set([i.item_name for i in self.item_input_definitions]))
        self.craftable_items.sort()
        self.valid_items = self._make_valid_items()
        self.valid_raw_items = list(set([i.item_name for i in self.raw_item_definitions]))
        self.valid_raw_items.sort()
        self.valid_raw_variations = list(set(i.variant for i in self.raw_item_definitions))
        self.valid_raw_variations.sort()
        self.crafting_buildings = list(set([i.factory for i in self.item_definitions]))
        self.crafting_buildings.sort()
        self.excavator_buildings = list(set([i.factory for i in self.raw_item_definitions]))
        self.excavator_buildings.sort()
        self.generator_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "generator"
        ]
        self.generator_buildings.sort()
        self.dispatcher_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "dispatcher"
        ]
        self.dispatcher_buildings.sort()
        self.receiving_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "receiver"
        ]
        self.receiving_buildings.sort()
        self.storage_buildings = [
            b.building_name for b in self.building_definitions if b.building_type == "storage"
        ]
        self.storage_buildings.sort()

        production_buildings = set()
        production_buildings |= set([b for b in self.crafting_buildings])
        production_buildings |= set([b for b in self.excavator_buildings])
        production_buildings |= set([b for b in self.dispatcher_buildings])
        production_buildings |= set([b for b in self.receiving_buildings])

        self.non_production_buildings = [
            b.building_name for b in self.building_definitions
                if b.building_name not in production_buildings
        ]

        self.item_recipes:dict[str,list[tuple[str, int, int]]] = {
            ri.item_name: [(r.input_name, r.num_required, r.required_per_minute)
                                for r in self.item_input_definitions
                                    if r.item_name == ri.item_name
                          ]
            for ri in self.item_input_definitions
        }
        """
        Crafting recipe for every craftable item. The key is the craftable item name and the
        value is a list of input items needed to craft the items, as well as the number required to
        craft. The value tuple is (input item name, amount required, amount required per minute).
        """

    #---------------------------------------------------------------------------

    def _make_valid_items(self) -> list[str]:
        valid_items = set()
        valid_items |= set([i.item_name for i in self.item_definitions])
        valid_items |= set([i.item_name for i in self.raw_item_definitions])
        l = list(valid_items)
        l.sort()
        return l

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

def dump_game_data(game_data:GameData):
    print(game_data.craftable_items)

#---------------------------------------------------------------------------------------------------

def load_game_data() -> GameData:

    items, inputs, raws, buildings = load_definitions(
            '../starrupture_recipe_items.csv',
            '../starrupture_recipe_input.csv',
            '../starrupture_recipe_raw.csv',
            '../starrupture_recipe_buildings.csv'
    )

    game_data = GameData(items, inputs, raws, buildings)

    #dump_game_data(game_data)

    return game_data

#---------------------------------------------------------------------------------------------------
