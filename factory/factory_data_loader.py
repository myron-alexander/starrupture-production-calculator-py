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
Provides functions to read and verify a factory layout definition JSON file.
"""

#---------------------------------------------------------------------------------------------------

import argparse
import json
import sys
import weakref
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from factories_data import *
from functools import reduce

sys.path.append("..")

from starrupture.sr_game_data import *

#---------------------------------------------------------------------------------------------------

def missing_string(s:str | None) -> bool:
    return s is None or len(s.strip()) < 1

#---------------------------------------------------------------------------------------------------

class GameDataDefinitions:
    def __init__(self,
                 items: list[Item],
                 recipe_inputs: list[RecipeInput],
                 raw_items: list[RawItem],
                 buildings: list[Building]) -> None:
        # Data read from data files.
        self.items:list[Item] = items
        self.recipe_inputs:list[RecipeInput] = recipe_inputs
        self.raw_items:list[RawItem] = raw_items
        self.buildings:list[Building] = buildings

        # Calculated collections.
        self.inputs_per_item:dict[str,list[str]] = dict()
        """ Map an item name, to the list of input item names required to craft it.
        Doesn't include raw items in the keys. """
        self.valid_items:set[str] = set()
        """ A set containing all known item names. """

        self.update()


    def update(self) -> None:
        # Intentionally not replacing the instances and rather replacing the contents of the
        # existing instance.

        self.inputs_per_item.clear()
        self.inputs_per_item |= {
                ri.item_name: [r.input_name
                                    for r in self.recipe_inputs
                                    if r.item_name == ri.item_name
                              ]
                for ri in self.recipe_inputs
            }
        self.valid_items.clear()
        self.valid_items |= set([ii.item_name for ii in self.items])
        self.valid_items |= set([ii.item_name for ii in self.raw_items])

#---------------------------------------------------------------------------------------------------

def load_data_definitions() -> GameDataDefinitions:
    return GameDataDefinitions(*load_definitions(
            '../starrupture_recipe_items.csv',
            '../starrupture_recipe_input.csv',
            '../starrupture_recipe_raw.csv',
            '../starrupture_recipe_buildings.csv'
    ))

#---------------------------------------------------------------------------------------------------

# Type hint for json_path in quotes as the class has not been defined so the quotes allow for a
# forward reference. The return type hint for method set_next quotes the JsonPathNode class name
# for the same reason.

class JsonPathNode:
    def __init__(self, json_path:"JsonPath", path_id: str) -> None:
        self._json_path_ref = weakref.ref(json_path)
        self.path_id:str = path_id
        self.next:JsonPathNode | None = None


    def set_next(self, path_id:str) -> "JsonPathNode":
        """
        Replace the link to next node with a new node for path_id. This is effectively the
        equivalent of a truncate and then add node.

        :param path_id: JSON path id to be added to the path.
        :type path_id: str
        :return: The new path node.
        :rtype: JsonPathNode
        """
        jp = self._json_path_ref()
        if jp is not None:
            node = JsonPathNode(jp, path_id)
            self.next = node
            return node
        else:
            raise ValueError(
                "JsonPathNode is being used when the containing JsonPath has been garbage" \
                " collected. This is a fatal error and suggests a programming mistake.")


    def truncate(self) -> "JsonPathNode":
        """
        Disconnect the path nodes following this one from the list.

        :return: self
        :rtype: JsonPathNode
        """
        self.next = None
        return self


    def get_path_str(self) -> str:
        """
        Calls the containing JsonPath.get_path() to get the path string.

        :return: Get all the path IDs as a string. May return an empty string if the containing
                 JsonPath has been garbage collected.
        :rtype: str
        """
        jp = self._json_path_ref()
        if jp is not None:
            return jp.get_path_str()
        else:
            return ""


    def get_path_array(self) -> list[str]:
        jp = self._json_path_ref()
        if jp is not None:
            return jp.get_path_array()
        else:
            return []

#---------------------------------------------------------------------------------------------------

# Removed the building of JsonPath from the validation functions to simplify the means of reporting
# JSON file position. By centralising the path building to the JSON data loader, it removes
# duplicate effort. Setting the json path in the data objects makes it available wherever the
# object is used without needing to know the JSON file structure.
#
# Another thought is that the json_path can be used to write a new JSON data file from the loaded
# objects.

#---------------------------------------------------------------------------------------------------

class JsonPath:
    def __init__(self, path_id: str) -> None:
        self._path:JsonPathNode = JsonPathNode(self, path_id)


    def get_path_head(self) -> JsonPathNode:
        return self._path

    def set_next(self, path_id: str) -> JsonPathNode:
        node = JsonPathNode(self, path_id)
        self._path.next = node
        return node


    def get_path_array(self) -> list[str]:
        """
        Get the list of path names.

        :return: The full JSON path as a list of the key names.
        :rtype: list[str]
        """
        path_array:list[str] = []
        current = self._path
        while current is not None:
            path_array.append(current.path_id)
            current = current.next
        return path_array


    def get_path_str(self) -> str:
        """
        Get all the path names as a string.

        :return: The full JSON path represented as a string.
        :rtype: str
        """
        return "▹".join(self.get_path_array())

#---------------------------------------------------------------------------------------------------

class FactoriesJsonError(Exception):
    def __init__(self, message, json_path_node:JsonPathNode|list[str]|None = None) -> None:
        if type(json_path_node) is list:
            self.message = message + f'\nJSON path: {"▹".join(json_path_node)}'
        elif type(json_path_node) is JsonPathNode:
            self.message = message + f'\nJSON path: {json_path_node.get_path_str()}'
        else:
            self.message = message
        super().__init__(self.message)

#---------------------------------------------------------------------------------------------------

def validate_source_list(path_node:JsonPathNode, description:str, source:str, value):
    """
    For an optional list of input IDs that point to a source of items, when the list is provided,
    validate that the list is not empty and that the IDs are populated strings.

    :param path_node: Path to the JSON element.
    :type path_node: JsonPathNode
    :param description: Description of the connector destination
    :type description: str
    :param source: JSON key providing value.
    :type source: str
    :param value: Value to be tested.
    """

    if value is not None:
        if type(value) is not list \
            or len(value) < 1 \
            or not reduce(lambda x,y: x and type(y) is str and 0 < len(y.strip()), value, True):
            raise FactoriesJsonError(
                f"When '{source}' is specified by a {description}, it must be a"
                " list of strings.", path_node)


#---------------------------------------------------------------------------------------------------

def new_factory_machine_input(
        path_node:JsonPathNode, input_spec:dict) -> FactoryMachineInput:
    from_machine_id = input_spec.get("from_machine_id")
    from_factory_input_id = input_spec.get("from_factory_input_id")
    from_storage_id = input_spec.get("from_storage_id")
    rate_limit_ipm = input_spec.get("rate_limit_ipm")

    if from_machine_id is None and from_factory_input_id is None and from_storage_id is None:
        raise FactoriesJsonError(
            "A factory machine input must specify at least one of"
            " 'from_machine_id', 'from_factory_input_id', 'from_storage_id'.", path_node)
    if type(rate_limit_ipm) is not int or rate_limit_ipm < 1:
        raise FactoriesJsonError(
            "A factory machine input must specify the 'rate_limit_ipm' with an integer value"
            " of at least 1.",
            path_node)
    d = "factory machine input"
    validate_source_list(path_node, d, "from_machine_id", from_machine_id)
    validate_source_list(path_node, d, "from_factory_input_id", from_factory_input_id)
    validate_source_list(path_node, d, "from_storage_id", from_storage_id)

    return FactoryMachineInput(
        from_machine_id,
        from_factory_input_id,
        from_storage_id,
        int(rate_limit_ipm),
        path_node.get_path_array())

#---------------------------------------------------------------------------------------------------

def new_factory_machine(
        path_node:JsonPathNode,
        factory:"Factory",
        machine_id:str,
        machine_spec:dict) -> FactoryMachine:

    item = machine_spec.get("item")
    variant = machine_spec.get("variant")
    inputs = machine_spec.get("inputs")

    if type(item) is not str or missing_string(item):
        raise FactoriesJsonError(
            "A factory machine must define an 'item' with a non-empty string value.", path_node)
    if variant is not None and inputs is not None:
        raise FactoriesJsonError(
            "A factory machine may only define either 'variant' or 'inputs' but not both.",
            path_node)
    if variant is None and inputs is None:
        raise FactoriesJsonError(
            "A factory machine must define at least one of 'variant' or 'inputs'.", path_node)
    if variant is not None:
        return FactoryMachine(factory, machine_id, item, variant, None, path_node.get_path_array())
    else:
        if type(inputs) is not list or len(inputs) < 1:
            raise FactoriesJsonError(
                "When 'inputs' is specified for a factory machine, is must be a non-empty list.",
                path_node)
        inputs_path_node = path_node.set_next("inputs")
        inputs = [new_factory_machine_input(inputs_path_node, ii) for ii in inputs]
        path_node.truncate()
        return FactoryMachine(
            factory,
            machine_id,
            item,
            None,
            inputs,
            path_node.get_path_array()
        )

#---------------------------------------------------------------------------------------------------

def new_factory_storage(
        path_node:JsonPathNode,
        factory:"Factory",
        storage_id:str,
        storage_spec:dict) -> FactoryStorage:

    items = storage_spec.get("items")
    num_stacks = storage_spec.get("num_stacks")
    inputs = storage_spec.get("inputs")

    if type(items) is not list or len(items) < 1:
        raise FactoriesJsonError(
            "A factory storage must define 'items' as a non-empty list.",
            path_node)
    if 0 < len([ii for ii in items if type(ii) is not str or missing_string(ii)]):
        raise FactoriesJsonError(
            "A factory storage must define 'items' as a list of non-empty strings.",
            path_node)
    if type(num_stacks) is not int or num_stacks < 1:
        raise FactoriesJsonError(
            "A factory storage must specify the 'num_stacks' with an integer value"
            " of at least 1.",
            path_node)
    if type(inputs) is not list or len(inputs) < 1:
        raise FactoriesJsonError(
            "A factory storage must define 'inputs' as a non-empty list.",
            path_node)
    inputs_path_node = path_node.set_next("inputs")
    factory_machine_inputs = [new_factory_machine_input(inputs_path_node, ii) for ii in inputs]
    for fmi in factory_machine_inputs:
        if fmi.from_storage_id is not None and storage_id in fmi.from_storage_id:
            raise FactoriesJsonError(
                "A factory storage may not define itself as an input.",
                path_node)
    inputs_path_node.truncate()

    return FactoryStorage(
        factory,
        storage_id,
        items,
        num_stacks,
        factory_machine_inputs,
        path_node.get_path_array()
    )

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

def new_factory_input(path_node:JsonPathNode, factory_input_id:str, input_spec:dict) -> FactoryInput:
    site_id = input_spec.get("site_id")
    factory_id = input_spec.get("factory_id")
    factory_output_id = input_spec.get("factory_output_id")

    if type(site_id) is not str or missing_string(site_id):
        raise FactoriesJsonError(
            "A factory input must define a 'site_id' with a non-empty string value.", path_node)
    if type(factory_id) is not str or missing_string(factory_id):
        raise FactoriesJsonError(
            "A factory input must define a 'factory_id' with a non-empty string value.", path_node)
    if type(factory_output_id) is not str or missing_string(factory_output_id):
        raise FactoriesJsonError(
            "A factory input must define a 'factory_output_id' with a non-empty string value.",
            path_node)
    return FactoryInput(
        factory_input_id, site_id, factory_id, factory_output_id, path_node.get_path_array())

#---------------------------------------------------------------------------------------------------

def new_factory_output_source(path_node:JsonPathNode, source_spec:dict) -> FactoryOutputSource:
    from_machine_id = source_spec.get("from_machine_id")
    from_storage_id = source_spec.get("from_storage_id")
    rate_limit_ipm = source_spec.get("rate_limit_ipm")

    if from_machine_id is None and from_storage_id is None:
        raise FactoriesJsonError(
            "A factory output source must specify at least one of"
            " 'from_machine_id', 'from_storage_id'.", path_node)

    if type(rate_limit_ipm) is not int or rate_limit_ipm < 1:
        raise FactoriesJsonError(
            "A factory output source must define 'rate_limit_ipm' with an integer value of at"
            " least 1.",
            path_node)

    validate_source_list(path_node, "factory output source", "from_machine_id", from_machine_id)
    validate_source_list(path_node, "factory output source", "from_storage_id", from_storage_id)

    return FactoryOutputSource(
        from_machine_id, from_storage_id, rate_limit_ipm, path_node.get_path_array())

#---------------------------------------------------------------------------------------------------

def new_factory_output(
        path_node:JsonPathNode,
        factory:"Factory",
        factory_output_id:str,
        output_spec:dict) -> FactoryOutput:

    dispatched_item = output_spec.get("dispatched_item")
    rate_limit_ipm = output_spec.get("rate_limit_ipm")
    sources = output_spec.get("sources")

    if type(dispatched_item) is not str or missing_string(dispatched_item):
        raise FactoriesJsonError(
            "A factory output must define a 'dispatched_item' with a non-empty string value.",
            path_node)
    if type(rate_limit_ipm) is not int or rate_limit_ipm < 1:
        raise FactoriesJsonError(
            "A factory output must define a 'rate_limit_ipm' with an integer value of at least 1.",
            path_node)
    if type(sources) is not list or len(sources) < 1:
        raise FactoriesJsonError(
            "A factory output must define 'sources' as a non-empty list.", path_node)
    source_path_node = path_node.set_next("sources")
    sources = [new_factory_output_source(source_path_node, ss) for ss in sources]
    source_path_node.truncate()
    return FactoryOutput(
        factory,
        dispatched_item,
        factory_output_id,
        rate_limit_ipm,
        sources,
        path_node.get_path_array()
    )

#---------------------------------------------------------------------------------------------------

def new_factory(
        path_node:JsonPathNode,
        site:"Site",
        factory_id:str,
        factory_values:dict) -> Factory:

    purpose = factory_values.get("purpose")

    if type(purpose) is not str or missing_string(purpose):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a populated string,"
            f" for value of entry 'purpose'.", path_node)

    factory = Factory(site, factory_id, purpose, path_node.get_path_array())

    machines = factory_values.get("machines")
    if not isinstance(machines, dict):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid dict,"
            " for value of entry 'machines'.", path_node)

    machines_path_node = path_node.set_next("machines")

    for k,v in machines.items():
        if missing_string(k):
            raise FactoriesJsonError(
                f'JSON mandatory machine ID entry "{k}" invalid.', machines_path_node)
        machine = new_factory_machine(machines_path_node.set_next(k), factory, k, v)
        machines_path_node.truncate()
        factory.add_machine(machine)

    # Finished with machines node so remove it from the path.
    path_node.truncate()

    factory_inputs = factory_values.get("inputs")
    # Factory inputs are optional.
    if factory_inputs is not None:
        if not isinstance(factory_inputs, dict):
            raise FactoriesJsonError(
                "JSON optional entry value isn't a valid dict, for value of entry 'inputs'.",
                path_node)
        factory_input_path_node = path_node.set_next("inputs")
        for k,v in factory_inputs.items():
            if missing_string(k):
                raise FactoriesJsonError(
                    f'JSON mandatory factory input ID entry "{k}" invalid.',
                    factory_input_path_node)
            factory_input = new_factory_input(factory_input_path_node.set_next(k), k, v)
            if factory.factory_id == factory_input.factory_id \
                    and factory.site.site_id == factory_input.site_id:
                raise FactoriesJsonError(
                    f"Factory input '{factory_input.factory_input_id}' specifies a connection to"
                    f" an output within it's own factory. Only links to other factories are"
                    " allowed.", factory_input_path_node)
            factory_input_path_node.truncate()
            factory.add_input(factory_input)

    factory_outputs = factory_values.get("outputs")
    # Factory outputs are optional.
    if factory_outputs is not None:
        if not isinstance(factory_outputs, dict):
            raise FactoriesJsonError(
                "JSON optional entry value isn't a valid dict, for value of entry 'outputs'.",
                path_node)
        factory_output_path_node = path_node.set_next("outputs")
        for k,v in factory_outputs.items():
            if missing_string(k):
                raise FactoriesJsonError(
                    f'JSON mandatory factory output ID entry "{k}" invalid.',
                    factory_output_path_node)
            factory_output = new_factory_output(factory_output_path_node.set_next(k), factory, k, v)
            factory_output_path_node.truncate()
            factory.add_output(factory_output)

    factory_storage = factory_values.get("storage")
    # Factory storage is optional
    if factory_storage is not None:
        if not isinstance(factory_storage, dict):
            raise FactoriesJsonError(
                "JSON optional entry value isn't a valid dict, for value of entry 'storage'.",
                path_node)
        factory_storage_path_node = path_node.set_next("storage")
        for k,v in factory_storage.items():
            if missing_string(k):
                raise FactoriesJsonError(
                    f'JSON mandatory factory storage ID entry "{k}" invalid.',
                    factory_storage_path_node)
            fs = new_factory_storage(factory_storage_path_node.set_next(k), factory, k, v)
            factory_storage_path_node.truncate()
            factory.add_storage(fs)

    return factory

#---------------------------------------------------------------------------------------------------

def new_site(path_node:JsonPathNode, site_id:str, site_values:dict) -> Site:
    teleporter = site_values.get("teleporter")
    heat_limit = site_values.get("heat_limit")
    heat_current = site_values.get("heat_current")

    # Teleporter may be empty.
    if type(teleporter) is not str:
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a populated string,"
            " for value of entry 'teleporter'.", path_node)
    if type(heat_limit) is not int or heat_limit < 1000:
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid int,"
            " for value of entry 'heat_limit'.", path_node)
    if type(heat_current) is not int or heat_current < 1:
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid int,"
            " for value of entry 'heat_current'.", path_node)

    # Stripping teleporter as an empty string indicates no teleporter and white space is the
    # visual equivalent of nothing entered.
    site = Site(site_id, teleporter.strip(), heat_limit, heat_current, path_node.get_path_array())

    factories = site_values.get("factories")

    if not isinstance(factories, dict):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid dict,"
            " for value of entry 'factories'.", path_node)

    factory_path_node = path_node.set_next("factories")

    for k,v in factories.items():
        if missing_string(k):
            raise FactoriesJsonError(
                f'JSON mandatory factory ID entry "{k}" invalid.', factory_path_node)
        site.add_factory(new_factory(factory_path_node.set_next(k), site, k, v))

    return site

#---------------------------------------------------------------------------------------------------

class FactoryDefinitions:
    """
    All the factories, their sites and linkages.
    """

    def __init__(self) -> None:
        self.sites: list[Site] = list()

        self.all_factory_outputs:dict[str,FactoryOutput] = dict()
        """Index all factory outputs by key 'site_id;factory_id;factory_output_id'. """


    def add_site(self, site: Site) -> None:
        self.sites.append(site)


    def load(self, factories_dict:dict) -> None:
        """
        Extract site data from factories data file. Once this method has finished, the factory
        data is loaded and ready for use.

        :param factories_dict: Dictionary representing the structure of the factories JSON.
        :type factories_dict: dict
        """
        root_path = "sites"
        json_path = JsonPath(root_path)
        current_path_node:JsonPathNode = json_path.get_path_head()
        sites = factories_dict.get(root_path)
        if sites is None:
            raise FactoriesJsonError(
                "JSON missing root level 'sites' entry.", current_path_node)
        for k,v in sites.items():
            if missing_string(k):
                raise FactoriesJsonError(
                    f'JSON mandatory site ID entry "{k}" invalid.', current_path_node)
            self.add_site(new_site(current_path_node.set_next(k), k, v))

        self.__index_factory_outputs()


    def __index_factory_outputs(self) -> None:
        for site in self.sites:
            for factory in site.factories:
                for factory_output in factory.factory_outputs:
                    key = make_factory_output_key(
                        site.site_id, factory.factory_id, factory_output.factory_output_id)
                    # This check isn't necessary but is included as defense in depth.
                    if key in self.all_factory_outputs:
                        raise FactoriesJsonError(
                            f"Factory output ID '{factory_output.factory_output_id}' is duplicate"
                            f" within factory '{factory.factory_id}' and site '{site.site_id}'.")
                    self.all_factory_outputs[key] = factory_output

#---------------------------------------------------------------------------------------------------

def visit_all_machines(
        factory_definitions: FactoryDefinitions,
        machine_visitor: Callable[[FactoryMachine], None]) -> None:
    """
    Call method machine_visitor for every machine in the definitions.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    """

    for site in factory_definitions.sites:
        for factory in site.factories:
            for machine in factory.factory_machines:
                machine_visitor(machine)

#---------------------------------------------------------------------------------------------------

def visit_all_factory_outputs(
        factory_definitions: FactoryDefinitions,
        factory_output_visitor: Callable[[FactoryOutput], None]) -> None:
    """
    Call method factory_output_visitor for every factory output in the definitions.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    """
    for site in factory_definitions.sites:
        for factory in site.factories:
            for factory_output in factory.factory_outputs:
                factory_output_visitor(factory_output)

#---------------------------------------------------------------------------------------------------

def visit_all_factory_storage(
        factory_definitions: FactoryDefinitions,
        factory_storage_visitor: Callable[[FactoryStorage], None]) -> None:
    """
    Call method factory_storage_visitor for every factory storage in the definitions.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    """
    for site in factory_definitions.sites:
        for factory in site.factories:
            for factory_storage in factory.factory_storage:
                factory_storage_visitor(factory_storage)

#---------------------------------------------------------------------------------------------------

def validate_item_exists(
        factory_definitions: FactoryDefinitions, data_definitions: GameDataDefinitions) -> None:
    """
    Ensure that every mentioned item and variant exists in the data definitions.

    This validation is run first.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    :param data_definitions: Definitions for game items and buildings.
    :type data_definitions: DataDefinitions
    """

    raw_items = set([f"{ri.item_name};{ri.variant}" for ri in data_definitions.raw_items])
    items = set([i.item_name for i in data_definitions.items])

    def validator(machine:FactoryMachine) -> None:
        if machine.variant is not None:
            # Raw item
            raw_item = f"{machine.item};{machine.variant}"
            if raw_item not in raw_items:
                raise FactoriesJsonError(
                    f"Machine '{machine.machine_id}'"
                    f" specifies raw item '{machine.item}' with variant '{machine.variant}'"
                    " that does not exist in the data definitions.", machine.json_path)
        else:
            # Crafted item
            if machine.item not in items:
                raise FactoriesJsonError(
                    f"Machine '{machine.machine_id}'"
                    f" specifies item '{machine.item}' that does not exist in the data"
                    " definitions.", machine.json_path)

    visit_all_machines(factory_definitions, validator)

#---------------------------------------------------------------------------------------------------

def validate_connections_exist(factory_definitions: FactoryDefinitions) -> None:
    """
    Validate that all connections between factory machines, factory inputs, factory outputs and
    storage are valid. For example, a factory machine input that specifies a from_machine_id must
    specify an ID that exists in the same factory.

    Run validate_item_exists before this.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    """

    def validate_machine_inputs(
            machine_ids:set[str],
            input_ids:set[str],
            storage_ids:set[str],
            input:FactoryMachineInput|FactoryOutputSource) -> None:
        if input.from_machine_id is not None:
            for from_machine_id in input.from_machine_id:
                if from_machine_id not in machine_ids:
                    raise FactoriesJsonError(
                        f"Connection specified by from_machine_id '{from_machine_id}'"
                        " references a machine that doesn't exist within the same"
                        " factory.", input.json_path)
        if input.from_storage_id is not None:
            for storage_id in input.from_storage_id:
                if storage_id not in storage_ids:
                    raise FactoriesJsonError(
                        f"Connection specified by from_storage_id '{storage_id}'"
                        " references a storage that does not exist within the"
                        " same factory.", input.json_path)
        if type(input) is FactoryMachineInput:
            if input.from_factory_input_id is not None:
                for from_factory_input_id in input.from_factory_input_id:
                    if from_factory_input_id not in input_ids:
                        raise FactoriesJsonError(
                            "Connection specified by from_factory_input_id"
                            f" '{from_factory_input_id}' references a factory input"
                            " that does not exist within the same factory.", input.json_path)

    # "site id;factory id;factory output id" is the key for a factory output.
    # This is used to validate that factory inputs are linked to an existing factory output.
    existing_factory_outputs = set()

    for site in factory_definitions.sites:
        for factory in site.factories:
            machine_ids = set([m.machine_id for m in factory.factory_machines])
            input_ids = set([i.factory_input_id for i in factory.factory_inputs])
            storage_ids = set([s.storage_id for s in factory.factory_storage])
            for machine in factory.factory_machines:
                #
                # Validate that linked machines exist within the same factory.
                #
                if machine.inputs is not None:
                    for mi in machine.inputs:
                        validate_machine_inputs(machine_ids, input_ids, storage_ids, mi)

            for storage in factory.factory_storage:
                for ss in storage.inputs:
                    validate_machine_inputs(machine_ids, input_ids, storage_ids, ss)

            for factory_output in factory.factory_outputs:
                #
                # Validate that linked machines exist within the same factory.
                #
                for source in factory_output.sources:
                    validate_machine_inputs(machine_ids, input_ids, storage_ids, source)
                key = make_factory_output_key(
                        site.site_id,
                        factory.factory_id,
                        factory_output.factory_output_id
                )
                existing_factory_outputs.add(key)

    #
    # Validate that factory inputs are linked to an existing factory output.
    #
    for site in factory_definitions.sites:
        for factory in site.factories:
            for factory_input in factory.factory_inputs:
                key = make_factory_output_key(
                        factory_input.site_id,
                        factory_input.factory_id,
                        factory_input.factory_output_id
                )
                if key not in existing_factory_outputs:
                    raise FactoriesJsonError(
                        f"Factory '{factory.factory_id}' factory input"
                        f" '{factory_input.factory_input_id}' references a factory output that"
                        " doesn't exist.", factory_input.json_path)

#---------------------------------------------------------------------------------------------------

def validation_correct_item_for_input(
        factory_definitions: FactoryDefinitions, data_definitions: GameDataDefinitions) -> None:
    """
    Ensure inputs into a machine, storage or factory output are actually supplying an items that can
    be consumed by the machine, storage or factory output.

    Both validate_item_exists and validate_connections_exist must be run before this.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    :param data_definitions: Definitions for game items and buildings.
    :type data_definitions: DataDefinitions
    """

    def inputs_validator(
            factory:Factory,
            input:FactoryMachineInput|FactoryOutputSource,
            required_input_items:list[str],
            consumer_desc:str) -> None:

        if input.from_machine_id is not None:
            #
            # Validate that the source input can be consumed by the machine.
            #
            for from_machine_id in input.from_machine_id:
                from_machine = next(
                    (m for m in factory.factory_machines
                        if m.machine_id == from_machine_id)
                )
                if from_machine.item not in required_input_items:
                    raise FactoriesJsonError(
                        f"The item produced by machine '{from_machine_id}' cannot"
                        f" be used by {consumer_desc}."
                        f"\nExpecting one of {required_input_items} but delivering"
                        f" '{from_machine.item}'."
                        , input.json_path)

        if input.from_storage_id is not None:
            #
            # Validate that the item provided from storage can be consumed by the
            # machine.
            #
            for from_storage_id in input.from_storage_id:
                storage = next(
                    (m for m in factory.factory_storage
                        if m.storage_id == from_storage_id)
                )
                if set(storage.items).isdisjoint(required_input_items):
                    raise FactoriesJsonError(
                        f"The item supplied by storage '{from_storage_id}' cannot"
                        f" be used by {consumer_desc}."
                        f"\nExpecting one of {required_input_items} but delivering"
                        f" '{storage.items}'."
                        , input.json_path)

        if type(input) is FactoryMachineInput:
            if input.from_factory_input_id is not None:
                #
                # Validate that item sent from the remote factory can be consumed by
                # the machine.
                #
                for from_factory_input_id in input.from_factory_input_id:
                    output_key = next(
                        (i for i in factory.factory_inputs
                            if i.factory_input_id == from_factory_input_id)) \
                        .get_output_key()
                    factory_output = \
                        factory_definitions.all_factory_outputs[output_key]
                    # Don't check from_factory_output for None as that should never
                    # happen if the validation have been run in the correct order.
                    # Allow a reference exception if not set.
                    if factory_output.dispatched_item not in required_input_items:
                        raise FactoriesJsonError(
                            "The item dispatched by output"
                            f" '{output_key}' cannot"
                            f" be used by {consumer_desc}."
                            f"\nExpecting one of {required_input_items} but delivering"
                            f" '{factory_output.dispatched_item}'."
                            , input.json_path)

    def machines_validator(machine:FactoryMachine) -> None:
        if machine.inputs is not None:
            required_input_items = \
                data_definitions.inputs_per_item[machine.item]
            consumer_desc = f"machine '{machine.machine_id}'"
            for mi in machine.inputs:
                inputs_validator(machine.factory, mi, required_input_items, consumer_desc)

    def factory_outputs_validator(output:FactoryOutput) -> None:
        required_input_items = [output.dispatched_item]
        consumer_desc = f"factory output '{output.factory_output_id}'"
        for ss in output.sources:
            inputs_validator(output.factory, ss, required_input_items, consumer_desc)

    def storage_validator(storage:FactoryStorage) -> None:
        required_input_items = storage.items
        consumer_desc = f"factory storage '{storage.storage_id}'"
        for si in storage.inputs:
            inputs_validator(storage.factory, si, required_input_items, consumer_desc)

    visit_all_machines(factory_definitions, machines_validator)
    visit_all_factory_outputs(factory_definitions, factory_outputs_validator)
    visit_all_factory_storage(factory_definitions, storage_validator)

#---------------------------------------------------------------------------------------------------

# The function assigned to object_pairs_hook will be called with every JSON object. The processing
# order of nested objects is inner most object first IE ascending up the hierarchy.
# The JSON object will be converted into an array of key,value tuples.
#
# For example:
#   {
#       "item": "titanium ore",
#       "variant": "normal"
#   }
#
# is converted to:
#   [("item", "titanium ore"), ("variant", "normal")]
#
# The return from the function is used as the input into the parent node.

class FailOnDuplicateDict(dict):
    """
    Instantiates a dict from an array of key,value tuples of the form [(k,v), (k2,v2), ...]. The
    keys are checked for duplicates and a KeyError is raised if a key occurs in a JSON object
    more than once.

    A JSON object is specified with curly braces within the JSON message.
    For example: {"a":1, "b":"c"} is a JSON object with 2 keys: "a", "b".
    Nested example with no duplicate keys: {"a":1, "b":{"a":"not dup", "b":2}}.

    Example with duplicate keys: {"a":1, "a":2, "b":3, "c":{"b":4}} where key "a" is the key with
    duplicates, and "b" is not duplicate because it occurs on different levels.

    A new class will be instantiated by json.load for every JSON object read in the JSON message.
    For nested JSON objects, the order of processing is from the innermost object up to the topmost
    object so the resultant dictionary retains the message hierarchy.

    For example {"a":1, "b":{"a":"not dup", "b":2}}, the object {"a":"not dup", "b":2} is processed
    first and results in a FailOnDuplicateDict with key=value of ["a"="not dup"), "b"=2]. That
    instance is then passed up the chain when {"a":1, "b":{}} object is passed into the constructor
    as [("a", 1), ("b", FailOnDuplicateDict)] where the FailOnDuplicateDict linked to "b" is the
    result from the previous call.
    """
    def __init__(self, ordered_pairs):
        duplicates = [d for d,i in Counter([pair[0] for pair in ordered_pairs]).items() if i > 1]
        if duplicates:
            raise FactoriesJsonError(
                f"Duplicate keys are not allowed in a JSON message. Duplicates: {duplicates}")
        self.update(ordered_pairs)

#---------------------------------------------------------------------------------------------------

def read_factories_json(factories_filename: str) -> FactoryDefinitions:
    with open(factories_filename) as jsf:
        factories_dict = json.load(jsf, object_pairs_hook=FailOnDuplicateDict)
    factory_definitions = FactoryDefinitions()
    factory_definitions.load(factories_dict)
    return factory_definitions

#---------------------------------------------------------------------------------------------------

def indent_lines(multi_line_str:str, indent:int) -> str:
    indent_str = " "*indent
    return multi_line_str.replace("\n", "\n"+indent_str)

#---------------------------------------------------------------------------------------------------

def load_factories_json(
        game_data_definitions:GameDataDefinitions, filename:str) -> FactoryDefinitions:

    factory_definitions = read_factories_json(filename)
    # Order of validations is important as the validation functions make assumptions about
    # valid data based on known correctness.
    validate_item_exists(factory_definitions, game_data_definitions)
    validate_connections_exist(factory_definitions)
    validation_correct_item_for_input(factory_definitions, game_data_definitions)
    return factory_definitions

#---------------------------------------------------------------------------------------------------

def main():
    data_definitions = load_data_definitions()

    aparser = argparse.ArgumentParser(
        description="Verifies factory management definition JSON file is valid."
    )

    aparser.add_argument(
        "filename",
        help="Name of factory management definition JSON file to validate."
    )

    args = aparser.parse_args()

    filename = args.filename
    try:
        load_factories_json(data_definitions, filename)
        print(f"Successfully loaded and validated factories from '{filename}'.")
    except FactoriesJsonError as e:
        print(f"\n\nERROR in '{filename}':")
        print(f"    {indent_lines(e.message, 4)}")
        print()
        print()

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------
