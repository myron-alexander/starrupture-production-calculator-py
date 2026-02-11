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
Data classes for elements of a factory that, when connected, define the constituents of one or
more production chains. Consists of:

Site - A collection of factories that are located very near each other. The position of the site is
       indicated by proximity to a teleporter.

Factory - A collection of connected machines that produce items. A factory can both dispatch and
          receive items from other factories.

FactoryMachine - A machine that produces an item either from other items, or by extracting raw
                 materials from the ground.

FactoryStorage - A building that stores items. Most types of storage buildings can store only a
                 single type of item but there are buildings that allow for multiple item types
                 to be stored.

FactoryOutput - Defines an egress point for items to be dispatched to another factory.

FactoryInput - Defines an ingress point for items from another factory.
"""

#---------------------------------------------------------------------------------------------------

__all__ = [
    'Site',
    'Factory',
    'FactoryMachine',
    'FactoryMachineInput',
    'FactoryStorage',
    'FactoryInput',
    'FactoryOutput',
    'FactoryOutputSource',
    'make_factory_output_key'
]

#---------------------------------------------------------------------------------------------------

from dataclasses import dataclass, field

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryMachineInput:
    """
    Sources of items consumed by the machine.

    A factory storage is also a type of machine but differs from a factory machine in that is
    doesn't craft items but it does have the same kinds of sources so FactoryMachineInput is
    also used by FactoryStorage as the input definition.
    """
    from_machine_ids: list[str] | None
    from_factory_input_ids: list[str] | None
    # A factory storage may not specify itself as an input, only other storages.
    from_storage_ids: list[str] | None
    rate_limit_ipm: int

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryMachine:
    """
    A machine within a factory that produces an item. The machine can be one of two types:

    1. Crafts items
    2. Extracts raw items

    When the machine crafts items, attribute 'input' will be populated with the list of inputs and
    'variant' will be set to None.

    When the machine extracts raw items, 'variant' will be populated with the resource variant and
    'input' will be set to None.
    """

    factory: "Factory"
    """
    Link to the factory that contains the machine.
    """

    machine_id: str
    item_name: str
    variant: str | None
    """
    When the machine extracts raw items from a resource node, 'variant' is set to the purity of the
    resource node, otherwise it is set to None.
    """
    inputs: list[FactoryMachineInput] | None
    """
    When the machine crafts an item from other items, 'inputs' is set to the list of item suppliers,
    otherwise it is set to None.
    """

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryStorage:
    """
    A factory storage is different from a machine as it can never be a source of items into a
    production chain. This is because storage is a finite, non-renewable source. Within a factory,
    storage can only be connected as a buffer or final destination.
    """

    factory: "Factory"
    """
    Link to the factory that contains the machine.
    """

    storage_id: str
    item_names: list[str]
    num_stacks: int
    inputs: list[FactoryMachineInput]

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

#---------------------------------------------------------------------------------------------------

def make_factory_output_key(site_id:str, factory_id:str, factory_output_id:str) -> str:
    """
    Generate a key that identifies a single factory output.

    :param site_id: Site of the factory.
    :type site_id: str
    :param factory_id: Factory providing the output.
    :type factory_id: str
    :param factory_output_id: Provided output.
    :type factory_output_id: str
    :return: A key that can be used to lookup a factory output.
    :rtype: str
    """
    return "%s;%s;%s" % (site_id, factory_id, factory_output_id)

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryInput:
    factory_input_id: str
    site_id: str
    factory_id: str
    factory_output_id: str

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

    def get_output_key(self) -> str:
        return make_factory_output_key(self.site_id, self.factory_id, self.factory_output_id)

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryOutputSource:
    from_machine_ids: list[str] | None
    from_storage_ids: list[str] | None
    rate_limit_ipm: int

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryOutput:
    factory: "Factory"
    """
    Link to the factory that contains the machine.
    """

    dispatched_item_name: str
    factory_output_id: str
    rate_limit_ipm: int
    sources: list[FactoryOutputSource]

    json_path:list[str]
    """
    Path to this data in the JSON file.
    """

#---------------------------------------------------------------------------------------------------

class Factory:

    def __init__(self, site:"Site", factory_id: str, purpose: str, json_path:list[str]) -> None:
        self.site: "Site" = site
        """
        Link to site that contains this factory.
        """

        self.factory_id: str = factory_id
        self.purpose: str = purpose
        self.json_path = json_path

        self.factory_machines: list[FactoryMachine] = list()
        self.factory_inputs: list[FactoryInput] = list()
        self.factory_outputs: list[FactoryOutput] = list()
        self.factory_storage: list[FactoryStorage] = list()


    def add_machine(self, machine: FactoryMachine) -> None:
        self.factory_machines.append(machine)

    def add_input(self, factory_input: FactoryInput) -> None:
        self.factory_inputs.append(factory_input)

    def add_output(self, factory_output: FactoryOutput) -> None:
        self.factory_outputs.append(factory_output)

    def add_storage(self, storage: FactoryStorage) -> None:
        self.factory_storage.append(storage)

#---------------------------------------------------------------------------------------------------

@dataclass
class Site:
    site_id: str
    teleporter: str
    heat_limit: int
    heat_current: int
    json_path:list[str]
    """
    Path to this data in the JSON file.
    """
    factories: list[Factory] = field(default_factory=list)

    def add_factory(self, factory: Factory) -> None:
        self.factories.append(factory)

#---------------------------------------------------------------------------------------------------
