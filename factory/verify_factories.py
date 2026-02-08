import argparse
import csv
import json
import weakref
from dataclasses import dataclass, field
from functools import reduce
from collections import Counter

#---------------------------------------------------------------------------------------------------

def missing_string(s:str | None) -> bool:
    return s is None or len(s.strip()) < 1

#---------------------------------------------------------------------------------------------------

@dataclass
class Item:
    item_name: str
    factory: str

#---------------------------------------------------------------------------------------------------

@dataclass
class RecipeInput:
    item_name: str
    input_name: str

#---------------------------------------------------------------------------------------------------

@dataclass
class RawItem:
    item_name: str
    variant: str
    factory: str

#---------------------------------------------------------------------------------------------------

@dataclass
class Building:
    building_name: str

#---------------------------------------------------------------------------------------------------

class DataDefinitions:
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

def load_data_definition_file(fname, conv_func):
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

def load_data_definitions() -> DataDefinitions:
    def item_conv(row):
        o = Item(row[0], row[3])
        #print(o.item_name, o.num_produced, o.period_seconds, o.factory, o.items_per_minute)
        return o

    def input_conv(row):
        o = RecipeInput(row[0], row[1])
        #print(o.item_name, o.input_name, o.num_required)
        return o

    def raw_conv(row):
        o = RawItem(row[0], row[1], row[4])
        #print(o.item_name, o.variant, o.num_produced)
        return o

    def building_conv(row):
        o = Building(row[0])
        return o

    items = load_data_definition_file('../starrupture_recipe_items.csv', item_conv)
    recipe_inputs = load_data_definition_file('../starrupture_recipe_input.csv', input_conv)
    raw_items = load_data_definition_file('../starrupture_recipe_raw.csv', raw_conv)
    buildings = load_data_definition_file('../starrupture_recipe_buildings.csv', building_conv)

    return DataDefinitions(items, recipe_inputs, raw_items, buildings)

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

    def add_path(self, path_id: str) -> JsonPathNode:
        node = JsonPathNode(self, path_id)
        self.__find_last_node().next = node
        return node

    def __find_last_node(self) -> JsonPathNode:
        current = self._path
        while True:
            if current.next is None:
                break
            current = current.next
        return current


    def get_path_str(self) -> str:
        """
        Get all the path IDs as a string.

        :return: The full path represented as a string.
        :rtype: str
        """
        path = None
        current = self._path
        while current is not None:
            if path is None:
                path = '"' + current.path_id + '"'
            else:
                path = path + "▹" + '"' + current.path_id + '"'
            current = current.next
        return path or ""

#---------------------------------------------------------------------------------------------------

class FactoriesJsonError(Exception):
    def __init__(self, message, json_path_node:JsonPathNode|None = None) -> None:
        if json_path_node is not None:
            self.message = message + f'\nJSON path: {json_path_node.get_path_str()}'
        else:
            self.message = message
        super().__init__(self.message)

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryMachineInput:
    from_machine_id: list[str]
    from_factory_input_id: list[str]
    rate_limit_ipm: int

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
    machine_id: str
    item: str
    variant: str | None   # Set to None when machine has inputs.
    inputs: list[FactoryMachineInput] | None # Set to None when machine is raw extractor.

#---------------------------------------------------------------------------------------------------

def validate_machine_input_source(path_node:JsonPathNode, source:str, value):
    if value is not None:
        if type(value) is not list \
            or len(value) < 1 \
            or not reduce(lambda x,y: x and type(y) is str and 0 < len(y.strip()), value, True):
            raise FactoriesJsonError(
                f"When '{source}' is specified by a factory machine input, it must be a"
                " list of strings.", path_node)


#---------------------------------------------------------------------------------------------------

def new_factory_machine_input(
        path_node:JsonPathNode, input_spec:dict) -> FactoryMachineInput:
    from_machine_id = input_spec.get("from_machine_id")
    from_factory_input_id = input_spec.get("from_factory_input_id")
    rate_limit_ipm = input_spec.get("rate_limit_ipm")

    if from_machine_id is None and from_factory_input_id is None:
        raise FactoriesJsonError(
            "A factory machine input must specify either one or both of"
            " 'from_machine_id', 'from_factory_input_id'.", path_node)
    if type(rate_limit_ipm) is not int or rate_limit_ipm < 1:
        raise FactoriesJsonError(
            "A factory machine input must specify the 'rate_limit_ipm' with an integer value"
            " of at least 1.",
            path_node)
    validate_machine_input_source(path_node, "from_machine_id", from_machine_id)
    validate_machine_input_source(path_node, "from_factory_input_id", from_factory_input_id)

    return FactoryMachineInput(from_machine_id, from_factory_input_id, int(rate_limit_ipm)) # type: ignore

#---------------------------------------------------------------------------------------------------

def new_factory_machine(
        path_node:JsonPathNode, machine_id:str, machine_spec:dict) -> FactoryMachine:
    item = machine_spec.get("item")
    variant = machine_spec.get("variant")
    inputs = machine_spec.get("inputs")

    #print(f"              item: {item}")

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
        return FactoryMachine(machine_id, item, variant, None)
    else:
        if type(inputs) is not list or len(inputs) < 1:
            raise FactoriesJsonError(
                "When 'inputs' is specified for a factory machine, is must be a non-empty list.",
                path_node)
        inputs_path_node = path_node.set_next("inputs")
        return FactoryMachine(
            machine_id,
            item,
            None,
            [new_factory_machine_input(inputs_path_node, ii) for ii in inputs]
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

@dataclass
class FactoryInput:
    factory_input_id: str
    site_id: str
    factory_id: str
    factory_output_id: str


    def get_output_key(self) -> str:
        return make_factory_output_key(self.site_id, self.factory_id, self.factory_output_id)

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
    return FactoryInput(factory_input_id, site_id, factory_id, factory_output_id)

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryOutputSource:
    from_machine_id: list[str]
    rate_limit_ipm: int

#---------------------------------------------------------------------------------------------------

@dataclass
class FactoryOutput:
    dispatched_item: str
    factory_output_id: str
    rate_limit_ipm: int
    sources: list[FactoryOutputSource]


#---------------------------------------------------------------------------------------------------

def new_factory_output_source(path_node:JsonPathNode, source_spec:dict) -> FactoryOutputSource:
    from_machine_id = source_spec.get("from_machine_id")
    rate_limit_ipm = source_spec.get("rate_limit_ipm")

    if type(from_machine_id) is not list \
        or len(from_machine_id) < 1 \
        or not reduce(lambda x,y: x and type(y) is str and 0 < len(y.strip()), from_machine_id, True):
        raise FactoriesJsonError(
            "A factory output source must define 'from_machine_id' as a non-empty list of strings.",
            path_node)
    if type(rate_limit_ipm) is not int or rate_limit_ipm < 1:
        raise FactoriesJsonError(
            "A factory output source must define 'rate_limit_ipm' with an integer value of at"
            " least 1.",
            path_node)
    return FactoryOutputSource(from_machine_id, rate_limit_ipm)

#---------------------------------------------------------------------------------------------------

def new_factory_output(
        path_node:JsonPathNode, factory_output_id:str, output_spec:dict) -> FactoryOutput:
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
    return FactoryOutput(
        dispatched_item,
        factory_output_id,
        rate_limit_ipm,
        [new_factory_output_source(source_path_node, ss) for ss in sources]
    )

#---------------------------------------------------------------------------------------------------

class Factory:

    def __init__(self, site_id: str, factory_id: str, purpose: str ) -> None:
        self.site_id: str = site_id
        self.factory_id: str = factory_id
        self.purpose: str = purpose
        self.factory_machines: list[FactoryMachine] = list()
        self.factory_inputs: list[FactoryInput] = list()
        self.factory_outputs: list[FactoryOutput] = list()

        # Duplication check lists
        self.__machine_ids: list[str] = list()
        self.__input_ids: list[str] = list()
        self.__output_ids: list[str] = list()


    def add_machine(self, path_node:JsonPathNode, machine: FactoryMachine) -> None:
        is_unique: bool = Factory.__validate_unique_name(self.__machine_ids, machine.machine_id)
        if is_unique:
            self.factory_machines.append(machine)
            self.__machine_ids.append(machine.machine_id)
        else:
            raise FactoriesJsonError(
                f"Machine ID '{machine.machine_id}' is duplicate within"
                f" factory '{self.factory_id}'.", path_node)


    def add_input(self, path_node:JsonPathNode, factory_input: FactoryInput) -> None:
        is_unique: bool = Factory.__validate_unique_name(
            self.__input_ids, factory_input.factory_input_id)
        if is_unique:
            self.factory_inputs.append(factory_input)
            self.__input_ids.append(factory_input.factory_input_id)
        else:
            raise FactoriesJsonError(
                f"Factory input ID '{factory_input.factory_input_id}' is duplicate within"
                f" factory '{self.factory_id}'.", path_node)


    def add_output(self, path_node:JsonPathNode, factory_output: FactoryOutput) -> None:
        is_unique: bool = Factory.__validate_unique_name(
            self.__output_ids, factory_output.factory_output_id)
        if is_unique:
            self.factory_outputs.append(factory_output)
            self.__output_ids.append(factory_output.factory_output_id)
        else:
            raise FactoriesJsonError(
                f"Factory output ID '{factory_output.factory_output_id}' is duplicate within"
                f" factory '{self.factory_id}'.", path_node)


    @staticmethod
    def __validate_unique_name(names: list[str], check_name: str) -> bool:
        """
        Check if provided name is unique in names. JSON spec actually allows for duplicate keys
        but most parsers either fail on the duplicate, ignore the duplicate or the duplicate
        replaces the one in the collection. The current JSON parser in Python3 defaults to
        replacement so only the last duplicate in the list is kept. There is a mechanism that
        can be used to handle this case but it requires implementation of a handler function.

        This function exists in case the code is modified in such a way that duplicates could be
        added to the list.

        :param names: List of known names.
        :type names: list[str]
        :param check_name: Name to test if already exists in names list.
        :type check_name: str
        :return: True when check_name is unique.
        :rtype: bool
        """
        return check_name not in names

#---------------------------------------------------------------------------------------------------

def new_factory(path_node:JsonPathNode, site_id:str, factory_id:str, factory_values:dict) -> Factory:
    purpose = factory_values.get("purpose")

    if type(purpose) is not str or missing_string(purpose):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a populated string,"
            f" for value of entry 'purpose'.", path_node)

    factory = Factory(site_id, factory_id, purpose)

    machines = factory_values.get("machines")
    if not isinstance(machines, dict):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid dict,"
            " for value of entry 'machines'.", path_node)

    machines_path_node = path_node.set_next("machines")

    for k,v in machines.items():
        #print(f"machine: {k}")
        if missing_string(k):
            raise FactoriesJsonError(
                f'JSON mandatory machine ID entry "{k}" invalid.', machines_path_node)
        machine = new_factory_machine(machines_path_node.set_next(k) , k, v)
        factory.add_machine(machines_path_node.truncate(), machine)

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
                    and factory.site_id == factory_input.site_id:
                raise FactoriesJsonError(
                    f"Factory input '{factory_input.factory_input_id}' specifies a connection to"
                    f" an output within it's own factory. Only links to other factories are"
                    " allowed.", factory_input_path_node)
            factory.add_input(factory_input_path_node.truncate(), factory_input)

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
            factory_output = new_factory_output(factory_output_path_node.set_next(k), k, v)
            factory.add_output(factory_output_path_node.truncate(), factory_output)

    return factory

#---------------------------------------------------------------------------------------------------

@dataclass
class Site:
    site_id: str
    teleporter: str
    heat_limit: int
    heat_current: int
    factories: list[Factory] = field(default_factory=list)

    def add_factory(self, factory: Factory) -> None:
        self.factories.append(factory)

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
    site = Site(site_id, teleporter.strip(), heat_limit, heat_current)

    factories = site_values.get("factories")

    if not isinstance(factories, dict):
        raise FactoriesJsonError(
            "JSON mandatory entry is either missing, or value isn't a valid dict,"
            " for value of entry 'factories'.", path_node)

    factory_path_node = path_node.set_next("factories")

    for k,v in factories.items():
        #print(f"factory: {k}")
        if missing_string(k):
            raise FactoriesJsonError(
                f'JSON mandatory factory ID entry "{k}" invalid.', factory_path_node)
        site.add_factory(new_factory(factory_path_node.set_next(k), site.site_id, k, v))

    return site

#---------------------------------------------------------------------------------------------------

#class DispatchedItem:

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
            #print(f"site: {k}")
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

def validate_item_exists(
        factory_definitions: FactoryDefinitions, data_definitions: DataDefinitions) -> None:
    """
    Ensure that every mentioned item and variant exists in the data definitions.

    This validation is run first.

    :param factory_definitions: Description
    :type factory_definitions: FactoryDefinitions
    :param data_definitions: Description
    :type data_definitions: DataDefinitions
    """

    raw_items = set([f"{ri.item_name};{ri.variant}" for ri in data_definitions.raw_items])
    items = set([i.item_name for i in data_definitions.items])

    for site in factory_definitions.sites:
        for factory in site.factories:
            for machine in factory.factory_machines:
                if machine.variant is not None:
                    # Raw item
                    raw_item = f"{machine.item};{machine.variant}"
                    if raw_item not in raw_items:
                        raise FactoriesJsonError(
                            f"Site '{site.site_id}'"
                            f" Factory '{factory.factory_id}' machine '{machine.machine_id}'"
                            f" specifies item '{machine.item}' with variant '{machine.variant}'"
                            " that does not exist in the data definitions.")
                else:
                    # Crafted item
                    if machine.item not in items:
                        raise FactoriesJsonError(
                            f"Site '{site.site_id}'"
                            f" Factory '{factory.factory_id}' machine '{machine.machine_id}'"
                            f" specifies item '{machine.item}' that does not exist in the data"
                            " definitions.")

#---------------------------------------------------------------------------------------------------

def validate_connections_exist(factory_definitions: FactoryDefinitions) -> None:
    """
    Validate that all connections between factory machines, factory inputs and factory outputs are
    valid. For example, a factory machine input that specifies a from_machine_id must specify an
    ID that exists in the same factory.

    Run validate_item_exists before this.

    :param factory_definitions: Factory definitions to validate.
    :type factory_definitions: FactoryDefinitions
    """

    # "site id;factory id;factory output id" is the key for a factory output.
    # This is used to validate that factory inputs that specify a factory output id are linked to
    # an actual factory output.
    existing_factory_outputs = set()

    for site in factory_definitions.sites:
        for factory in site.factories:
            machine_ids = set([m.machine_id for m in factory.factory_machines])
            input_ids = set([i.factory_input_id for i in factory.factory_inputs])
            for machine in factory.factory_machines:
                #
                # Validate that linked machines exist within the same factory.
                #
                if machine.inputs is not None:
                    for mi in machine.inputs:
                        if mi.from_machine_id is not None:
                            for from_machine_id in mi.from_machine_id:
                                if from_machine_id not in machine_ids:
                                    raise FactoriesJsonError(
                                        f"Factory '{factory.factory_id}' machine"
                                        f" '{machine.machine_id}' input specifies"
                                        f" from_machine_id '{from_machine_id}'"
                                        " that does not exist within the same factory.")
                        if mi.from_factory_input_id is not None:
                            for from_factory_input_id in mi.from_factory_input_id:
                                if from_factory_input_id not in input_ids:
                                    raise FactoriesJsonError(
                                        f"Factory '{factory.factory_id}' machine"
                                        f" '{machine.machine_id}' input specifies"
                                        f" from_factory_input_id '{from_factory_input_id}'"
                                        " that does not exist within the same factory.")
            for factory_output in factory.factory_outputs:
                #
                # Validate that linked machines exist within the same factory.
                #
                for source in factory_output.sources:
                    for from_machine_id in source.from_machine_id:
                        if from_machine_id not in machine_ids:
                            raise FactoriesJsonError(
                                f"Factory '{factory.factory_id}' output source"
                                f" '{factory_output.factory_output_id}' specifies"
                                f" from_machine_id '{from_machine_id}'"
                                " that does not exist within the same factory.")
                        key = make_factory_output_key(
                                site.site_id,
                                factory.factory_id,
                                factory_output.factory_output_id
                        )
                        existing_factory_outputs.add(key)

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
                        " doesn't exist.")

#---------------------------------------------------------------------------------------------------

def validation_correct_item_for_machine_input(
        factory_definitions: FactoryDefinitions, data_definitions: DataDefinitions) -> None:
    """
    Ensure that the item specified for a machine input is actually an item that is produced by a
    machine output or factory output that is linked to the machine input.

    Both validate_item_exists and validate_connections_exist must be run before this.

    :param factory_definitions: Description
    :type factory_definitions: FactoryDefinitions
    """

    # The first draft of this method was suggested by copilot but it got only about 30% of the
    # implementation correct. The rest was implemented by me. The main thing that copilot got wrong
    # was that is misunderstood the intention of the validation and assumed that the input items
    # into the machine must match the one crafted by the machine. That is not the intent,
    # the intent is to get the input items from the recipe and match those to the input machines.
    #
    # CoPilot also got confused about the relationship between factory inputs and factory outputs
    # and thought that those inputs defined for the factory were linked to the outputs within the
    # same factory. That might have been cause by me as I found a bug in the program error messages
    # that stated the input must reference the output of the same factory.

    path = JsonPath("sites")
    for site in factory_definitions.sites:
        factories_path = path.set_next(site.site_id).set_next("factories")
        for factory in site.factories:
            machines_path = factories_path.set_next(factory.factory_id).set_next("machines")
            for machine in factory.factory_machines:
                machine_path = machines_path.set_next(machine.machine_id)
                if machine.inputs is not None:
                    machine_path.set_next("inputs")
                    for mi in machine.inputs:
                        required_input_items = \
                            data_definitions.inputs_per_item[machine.item]

                        if mi.from_machine_id is not None:
                            #
                            # Validate that the source input can be consumed by the machine.
                            #
                            for from_machine_id in mi.from_machine_id:
                                from_machine = next(
                                    (m for m in factory.factory_machines
                                        if m.machine_id == from_machine_id)
                                )
                                if from_machine.item not in required_input_items:
                                    raise FactoriesJsonError(
                                        f"The item produced by machine '{from_machine_id}' cannot"
                                        f" be used by machine '{machine.machine_id}'."
                                        f"\nExpecting one of {required_input_items} but delivering"
                                        f" '{from_machine.item}'."
                                        , machine_path)

                        if mi.from_factory_input_id is not None:
                            #
                            # Validate that item sent from the remote factory can be consumed by
                            # the machine.
                            #
                            for from_factory_input_id in mi.from_factory_input_id:
                                from_factory_input = next(
                                    (i for i in factory.factory_inputs
                                       if i.factory_input_id == from_factory_input_id))
                                from_factory_output = \
                                    factory_definitions.all_factory_outputs[
                                        from_factory_input.get_output_key()]
                                # Don't check from_factory_output for None as that should never
                                # happen if the validation have been run in the correct order.
                                # Allow a reference exception if not set.
                                if from_factory_output.dispatched_item not in required_input_items:
                                    raise FactoriesJsonError(
                                        "The item dispatched by output"
                                        f" '{from_factory_input.get_output_key()}' cannot"
                                        f" be used by machine '{machine.machine_id}'."
                                        f"\nExpecting one of {required_input_items} but delivering"
                                        f" '{from_factory_output.dispatched_item}'."
                                        , machine_path)

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

def main():
    data_definitions = load_data_definitions()

    filename = "factories_test.json"
    #filename = "factories.json"
    try:
        factory_definitions = read_factories_json(filename)
        # Order of validations is important as the validation functions make assumptions about
        # valid data based on known correctness.
        validate_item_exists(factory_definitions, data_definitions)
        validate_connections_exist(factory_definitions)
        validation_correct_item_for_machine_input(factory_definitions, data_definitions)
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