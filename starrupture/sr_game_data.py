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
    'ItemRecord',
    'RecipeInputRecord',
    'RawItemRecord',
    'BuildingRecord',
    'load_definitions'
]

#---------------------------------------------------------------------------------------------------

import csv
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar

#---------------------------------------------------------------------------------------------------

# Stack size and num stacks were added to support factory management, with the thought of dealing
# with item buffering on lines with incomplete consumption, as well as calculating amounts stored
# within the chain. This will never be accurate but can provide an approximate picture in time.
# Can also be used to show amount stored in storage (non-buffering) buildings to support querying
# items for collection by the player, answering the question: where can I grab n of item.
# These ideas are aspirational and not implemented.

#---------------------------------------------------------------------------------------------------

@dataclass
class ItemRecord:
    item_name: str
    num_produced: int
    period_seconds: float
    stack_size: int
    factory: str
    items_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class RecipeInputRecord:
    item_name: str
    input_name: str
    num_required: int
    period_seconds: float
    required_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class RawItemRecord:
    item_name: str
    variant: str
    num_produced: int
    period_seconds: int
    stack_size: int
    factory: str
    items_per_minute: int

#--------------------------------------------------------------------------------------------------

@dataclass
class BuildingRecord:
    building_name: str
    heat_cost: int
    building_material_type: str
    building_cost: int
    num_stacks: int

#---------------------------------------------------------------------------------------------------

T = TypeVar('T', bound=ItemRecord|RecipeInputRecord|RawItemRecord|BuildingRecord)

class CsvRowConverter(ABC):
    def __init__(self) -> None:
        self._header_lookup:dict[str,int] = dict()


    def set_headers(self, row:list[str]) -> None:
        """
        Set the column name to column number mapping from the read header row.
        Columns names are converted to all uppercase.

        :param row: CSV file header row.
        :type row: list[str]
        """
        self._header_lookup.clear()
        self._header_lookup.update(zip([v.upper() for v in row], range(0,len(row))))


    @abstractmethod
    def convert_row(self, row:list[str]) -> T:
        """
        Extract the data from the row into a data class.

        :param row: CSV file data row.
        :type row: list[str]
        """
        pass


    def get_column_value(self, column_name:str, row:list[str]) -> str:
        """
        Get the row value from the specified named column. If the column doesn't exist, an
        error is raised.

        :param column_name: Column name of the row which contains the data to return.
        :type column_name: str
        :param row: Row data.
        :type row: list[str]
        :return: Data read from the row column.
        :rtype: str
        """
        return row[self._header_lookup[column_name.upper()]]

#---------------------------------------------------------------------------------------------------

class ItemRowConverter(CsvRowConverter):
    """
    For version 1.0 records, expecting headers:
        Item;NumProduced;PeriodSeconds;Factory;ItemsPerMinute

    For version 1.1 records, expecting headers:
        Item;NumProduced;PeriodSeconds;StackSize;Factory;ItemsPerMinute

    When converting 1.0 records, the stack_size on Item is set to 0.
    """

    def __init__(self) -> None:
        super().__init__()
        self.has_stacksize = False

    def set_headers(self, row:list[str]) -> None:
        super().set_headers(row)
        self.has_stacksize = "STACKSIZE" in self._header_lookup

    def convert_row(self, row:list[str]) -> ItemRecord:
        return ItemRecord(
            self.get_column_value("Item", row),
            int(self.get_column_value("NumProduced", row)),
            float(self.get_column_value("PeriodSeconds", row)),
            int(self.get_column_value("StackSize", row)) if self.has_stacksize else 0,
            self.get_column_value("Factory", row),
            int(self.get_column_value("ItemsPerMinute", row))
        )

#---------------------------------------------------------------------------------------------------

class RecipeInputRowConverter(CsvRowConverter):
    """
    Item;Input;NumRequired;PeriodSeconds;RequiredPerMinute
    """

    def __init__(self) -> None:
        super().__init__()

    def convert_row(self, row:list[str]) -> RecipeInputRecord:
        return RecipeInputRecord(
            self.get_column_value("Item", row),
            self.get_column_value("Input", row),
            int(self.get_column_value("NumRequired", row)),
            float(self.get_column_value("PeriodSeconds", row)),
            int(self.get_column_value("RequiredPerMinute", row))
        )

#---------------------------------------------------------------------------------------------------

class RawItemRowConverter(CsvRowConverter):
    """
    For version 1.0 records, expecting headers:
        Item;Variant;NumProduced;PeriodSeconds;Factory;ItemsPerMinute

    For version 1.1 records, expecting headers:
        Item;Variant;NumProduced;PeriodSeconds;StackSize;Factory;ItemsPerMinute

    When converting 1.0 records, the stack_size on RawItem is set to 0.
    """

    def __init__(self) -> None:
        super().__init__()
        self.has_stacksize = False

    def set_headers(self, row:list[str]) -> None:
        super().set_headers(row)
        self.has_stacksize = "STACKSIZE" in self._header_lookup

    def convert_row(self, row:list[str]) -> RawItemRecord:
        return RawItemRecord(
            self.get_column_value("Item", row),
            self.get_column_value("Variant", row),
            int(self.get_column_value("NumProduced", row)),
            int(self.get_column_value("PeriodSeconds", row)),
            int(self.get_column_value("StackSize", row)) if self.has_stacksize else 0,
            self.get_column_value("Factory", row),
            int(self.get_column_value("ItemsPerMinute", row))
        )

#---------------------------------------------------------------------------------------------------

class BuildingRowConverter(CsvRowConverter):
    """
    For version 1.0 records, expecting headers:
        building;heat;bbm cost;ibm cost;qbm cost

    For version 1.1 records, expecting headers:
        Building;Heat;BbmCost;IbmCost;QbmCost;NumStacks

    When converting 1.0 records, the num_stacks on Building is set to 0.
    """

    def __init__(self) -> None:
        super().__init__()
        self.has_numstacks = False

    def set_headers(self, row:list[str]) -> None:
        super().set_headers(row)
        self.has_numstacks = "NUMSTACKS" in self._header_lookup

    def convert_row(self, row:list[str]) -> BuildingRecord:
        building = self.get_column_value("Building", row)
        heat = int(self.get_column_value("Heat", row))
        num_stacks = 0
        if self.has_numstacks:
            bbm_cost = self.get_column_value("BbmCost", row)
            ibm_cost = self.get_column_value("IbmCost", row)
            qbm_cost = self.get_column_value("QbmCost", row)
            num_stacks = int(self.get_column_value("NumStacks", row))
        else:
            bbm_cost = self.get_column_value("bbm cost", row)
            ibm_cost = self.get_column_value("ibm cost", row)
            qbm_cost = self.get_column_value("qbm cost", row)

        bbm_cost = None if 0 == len(bbm_cost.strip()) else ("bbm", int(bbm_cost))
        ibm_cost = None if 0 == len(ibm_cost.strip()) else ("ibm", int(ibm_cost))
        qbm_cost = None if 0 == len(qbm_cost.strip()) else ("qbm", int(qbm_cost))

        build_cost = next((c for c in (bbm_cost,ibm_cost,qbm_cost) if c is not None), None)
        if build_cost is None:
            raise ValueError(f"No building cost defined for machine '{building}'.")

        return BuildingRecord(building, heat, build_cost[0], build_cost[1], num_stacks)


#---------------------------------------------------------------------------------------------------

def load_definitions(
        items_filename:str,
        input_filename:str,
        raw_filename:str,
        buildings_filename:str
    ) -> tuple[list[ItemRecord], list[RecipeInputRecord], list[RawItemRecord], list[BuildingRecord]]:
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

    items = load_file(items_filename, ItemRowConverter())
    recipe_inputs = load_file(input_filename, RecipeInputRowConverter())
    raw_items = load_file(raw_filename, RawItemRowConverter())
    buildings = load_file(buildings_filename, BuildingRowConverter())

    return (items, recipe_inputs, raw_items, buildings)

#---------------------------------------------------------------------------------------------------

def load_file(fname:str, converter:CsvRowConverter) -> list[T]:
    ar:list[T] = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        read_header = True
        for row in reader:
            if read_header:
                converter.set_headers(row)
                read_header = False
                continue
            ar.append(converter.convert_row(row))
    return ar

#---------------------------------------------------------------------------------------------------
