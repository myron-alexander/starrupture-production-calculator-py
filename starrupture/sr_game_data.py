# Copyright (C) 2026  Myron Alexander
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
StarRupture game data for item and building definitions.
"""

#---------------------------------------------------------------------------------------------------

__all__ = [
    'Item',
    'RecipeInput',
    'RawItem',
    'Building',
    'load_definitions'
]

#---------------------------------------------------------------------------------------------------

import csv
from dataclasses import dataclass

#---------------------------------------------------------------------------------------------------

@dataclass
class Item:
    item_name: str
    num_produced: int
    period_seconds: float
    factory: str
    items_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class RecipeInput:
    item_name: str
    input_name: str
    num_required: int
    period_seconds: float
    required_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class RawItem:
    item_name: str
    variant: str
    num_produced: int
    period_seconds: int
    factory: str
    items_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class Building:
    building_name: str
    heat_cost: int
    building_material_type: str
    building_cost: int

#---------------------------------------------------------------------------------------------------

def load_definitions(
        items_filename:str,
        input_filename:str,
        raw_filename:str,
        buildings_filename:str
    ) -> tuple[list[Item], list[RecipeInput], list[RawItem], list[Building]]:
    """
    Load the definitions for StarRupture items and buildings.

    :param items_filename: Path to 'starrupture_recipe_items.csv' file.
    :type items_filename: str
    :param input_filename: Path to 'starrupture_recipe_input.csv' file.
    :type input_filename: str
    :param raw_filename: Path to 'starrupture_recipe_raw.csv' file.
    :type raw_filename: str
    :param buildings_filename: Path to 'starrupture_recipe_buildings.csv' file.
    :type buildings_filename: str
    :return: Definitions for items and buildings.
    :rtype: tuple[list[Item], list[RecipeInput], list[RawItem], list[Building]]
    """

    def item_conv(row):
        o = Item(row[0], int(row[1]), float(row[2]), row[3], int(row[4]))
        return o

    def input_conv(row):
        o = RecipeInput(row[0], row[1], int(row[2]), float(row[3]), int(row[4]))
        return o

    def raw_conv(row):
        o = RawItem(row[0], row[1], int(row[2]), int(row[3]), row[4], int(row[5]))
        return o

    def building_conv(row):
        mat_type: str|None = None
        build_cost: int|None = None
        if 0 < len(str.strip(row[2])):
            mat_type = "bbm"
            build_cost = int(row[2])
        elif 0 < len(str.strip(row[3])):
            mat_type = "ibm"
            build_cost = int(row[3])
        elif 0 < len(str.strip(row[4])):
            mat_type = "qbm"
            build_cost = int(row[4])
        if mat_type is None or build_cost is None:
            raise ValueError(f"No building cost defined for machine '{row[0]}'.")
        o = Building(row[0], int(row[1]), mat_type, build_cost)
        return o


    items = load_file(items_filename, item_conv)
    recipe_inputs = load_file(input_filename, input_conv)
    raw_items = load_file(raw_filename, raw_conv)
    buildings = load_file(buildings_filename, building_conv)

    return (items, recipe_inputs, raw_items, buildings)

#---------------------------------------------------------------------------------------------------

def load_file(fname, conv_func):
    ar = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        skip_header = True
        for row in reader:
            if skip_header:
                skip_header = False
                continue
            ar.append(conv_func(row))
    return ar

#---------------------------------------------------------------------------------------------------
