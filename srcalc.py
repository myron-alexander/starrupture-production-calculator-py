import argparse
import csv
import json
import math
from dataclasses import dataclass, field

#--------------------------------------------------------------------------------------------------

# [item name, requested ipm]
requesting = None

#--------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------

@dataclass
class RequiredItem:
    machine_name: str = None
    provided_ipm: int = 0
    required_ipm: float = 0.0

    def set_machine_name(self, machine_name: str):
        if self.machine_name is None:
            self.machine_name = machine_name
        return self

    def add_provided(self, provided_per_minute: int):
        #self.provided_ipm += provided_per_minute
        # In order to calculate the number of machines, we need to save the
        # amount provided by 1 machine.
        self.provided_ipm = provided_per_minute
        return self

    def add_required(self, required_per_minute: float):
        self.required_ipm += required_per_minute
        return self

#--------------------------------------------------------------------------------------------------

@dataclass
class Machine:
    machine_name: str
    item_name: str
    provided_ipm: int
    required_ipm: float
    inputs: list = field(default_factory=list)
    # When true, this is not a machine, but a stand-in for some external source that will provide
    # the items. When this is true, inputs must be empty and required_ipm must be zero.
    is_existing_provider: bool = False

    def add_input(self, machine):
        self.inputs.append(machine)

    def get_ratio(self) -> float:
        return self.required_ipm / self.provided_ipm


def new_existing_provider_machine(item_name: str, provided_ipm: int) -> Machine:
    return Machine("INPUT", item_name, provided_ipm, 0, is_existing_provider=True)

#--------------------------------------------------------------------------------------------------


# Every item in the chain that is necessary for crafting the output item.
# Key is item_name
crafting_items: dict[str, RequiredItem] = dict()


# Set of raw item names to match against the input item list so that we don't try to look for a
# raw item in the input list.
raw_item_names = set()


# The list of already produced items, keyed on the position in the production chain. The key
# is made of all the elements (item name) in the chain starting from the requested item
# and working back, separated by the semicolon charactor. For example, if "valve" is
# requested, and "heat resistant sheet" of "nozzle" is provided, the key is "valve;nozzle".
# 
# The value dict is keyed on the input name, and has the available items per minute as the value.
available_inputs: dict[str, dict[str, int]] = dict()

#--------------------------------------------------------------------------------------------------

def main():
    #
    # Load item and machine data.
    #

    items, recipe_inputs, raw_items, buildings = load_data()
    initialize_raw_items(raw_items)

    #
    # Initialize command line parser. This is done after the data is loaded as it needs the
    # list of items for argument error checking.
    #

    aparser = argparse.ArgumentParser(
        prog="StarRupture Calculator",
        description=
            "Calculates the machines and intermediate items required to craft requested item.")

    me_group = aparser.add_mutually_exclusive_group(required=True)
    me_group.add_argument(
        "-i", "--item", choices=[item.item_name for item in items], metavar="ITEM NAME",
        help="Requested item. Mutually exclusive with option 'spec'.")
    me_group.add_argument(
        "-s", "--spec", metavar="FILENAME",
        help="Item specifier as a JSON file. Mutually exclusive with option 'item'."
                " JSON comments aren't supported.")
    me_group.add_argument(
        "--dump_items", action='store_true',
        help="Output the available items and exit.")

    count_group = aparser.add_mutually_exclusive_group()
    count_group.add_argument(
        "-c", "--count", type=int,
        help="Requested number of items." +
            " When no number is specified either here or within the JSON spec, the output of"
            " a single machine is requested."
            " Mututally exclusive with option 'machines'.")
    count_group.add_argument(
        "-m", "--machines", type=int, metavar="NUM MACHINES",
        help="Calculate for the number of machines producing the requested item."
            " Mututally exclusive with option 'count'.")

    aparser.add_argument(
        "-d", "--depth", type=int, default=0,
        help="Limit production chain printing depth. Valid values are 0 to maxint."
            " When less than 1, no limit." +
            " When 1, prints out the request machine and immediate inputs."
            " When 2, prints out the request machine, it's inputs, and their inputs. Etc.")

    spec_group = aparser.add_argument_group(
        "Generate spec file", "Generate a template item specification file for an item.")

    spec_group.add_argument(
        "--genspec", metavar="FILENAME",
        help="Instead of performing a calculation, write out a spec file for requested item."
                " The provided parameter is the spec file name."
                " The parameter '--item' sets the item in the spec file."
                " The parameter '--count' sets the request per minute."
                " If count not provided, the ipm of a single machine is set.")

    spec_group.add_argument(
        "-u", "--use_input", action='store_true',
        help="When specified, the written template file will include an inputs section.")

    args = aparser.parse_args()
    #print(args)

    # found_item = find_item(requesting[0], items)
    # print(found_item)
    # found_inputs = find_items(requesting[0], recipe_inputs)
    # print(found_inputs)

    if args.dump_items:
        dump_items(items)
        return

    if args.genspec is not None:
        generate_spec_file(aparser, args, items)
        return

    requested_item = None
    requested_count = None

    if args.item is not None:
        requested_item = args.item

    if args.spec is not None:
        global available_inputs
        requested_item, requested_count, available_inputs = parse_request_spec(args.spec)

    #print(available_inputs)

    if args.count is not None:
        requested_count = args.count

    if args.machines is not None:
        requested_count = \
            get_count_item_produced_from_one_machine(requested_item, items) * args.machines

    if requested_count is None:
        requested_count = get_count_item_produced_from_one_machine(requested_item, items)

    if requested_count < 1:
        requested_count = 1

    global requesting
    requesting = [requested_item, requested_count]
    #print(requesting)

    if requesting is None:
        raise ValueError("The requested item must be specified.")

    #
    # Do calculation
    #

    # Tree of machines used to produce the requested item.
    # required_ipm is passed in with the amount to set on the root machine.
    machine_nodes = walk_item_chain(requesting[0], items, recipe_inputs, raw_items, requesting[1])

    #
    # Print results
    #

    banner = f"REQUESTING: {requesting[1]} ipm of {requesting[0]}"
    print()
    """
    ┌─┐└─┘│ ┄┆╔╗╚╝═║  ╭╮╯╰
    """

    print(f"╔{'═'*(len(banner)+2)}╗")
    print(f"║ {' '*len(banner)} ║")
    print(f"║ {banner} ║")
    print(f"║ {' '*len(banner)} ║")
    print(f"╚{'═'*(len(banner)+2)}╝")

    #print(crafting_items)
    print()
    print_crafting_items(buildings)

    print()
    print_machine_tree(machine_nodes, buildings, args.depth)

#--------------------------------------------------------------------------------------------------

def dump_items(items: list[Item]):
    item_names = [item.item_name for item in items]
    item_names.sort()
    for ii in item_names:
        print(f"{ii:<20}")


#--------------------------------------------------------------------------------------------------

def get_count_item_produced_from_one_machine(item_name: str, items: list[Item]) -> int:
    item = find_item(item_name, items)
    return item.items_per_minute

#--------------------------------------------------------------------------------------------------

def find_building_cost(building_name: str, num_buildings: int, buildings: list[Building]) -> tuple[int, str]:
    """
    Returns the costs associated with the building.

    :param building_name: Key into building list.
    :type building_name: str
    :param num_buildings: For calculating total cost, the number of buildings to be calculated.
                          Must be a whole number rounded up.
    :type num_buildings: int
    :param buildings: List of building details from which the costs will be calculated.
    :type buildings: list[Building]
    :return: Tuple of heat cost and building cost. The building cost string includes the building
             material type.
    :rtype: tuple[int, str]
    """
    for b in buildings:
        if(b.building_name == building_name):
            return \
                b.heat_cost * num_buildings, \
                f"{b.building_cost * num_buildings} {b.building_material_type}"
    raise ValueError(f"Building '{building_name}' not found")

#--------------------------------------------------------------------------------------------------

def print_crafting_items(buildings: list[Building]):
    crafted_keys = list(crafting_items)
    crafted_keys.sort(key = str.lower)
    print("%-20s %-10s %-10s %-15s" % ("", "Provided", "Required", "Num"))
    print("%-20s %-10s %-10s %-15s %-20s %-4s %-10s" \
          % ("Item", "IPM", "IPM", "Machines", "Machine", "Heat", "Cost"))
    print("-"*(20+10+10+10+44+5))
    for k in crafted_keys:
        i = crafting_items[k]
        num_machines = i.required_ipm/i.provided_ipm
        num_machines_rounded = max(1, math.ceil(num_machines))
        heat_cost, building_cost = find_building_cost(i.machine_name, num_machines_rounded, buildings)
        print(
            f"{k:<20} {i.provided_ipm:10d} {i.required_ipm:10.2f}" +
            f" {num_machines:10.2f} ({num_machines_rounded:2d}) {i.machine_name:<20}" +
            f" {heat_cost:4} {building_cost:>10}")

#--------------------------------------------------------------------------------------------------

"""
┌─┐└─┘│
"""

def print_machine_tree(machine: Machine,
                       buildings: list[Building],
                       depth_limit:int,
                       indent: str = "",
                       current_depth:int = 0):
    if 0 < depth_limit and depth_limit < current_depth:
        return

    indent_str = indent
    if machine.is_existing_provider:
        num_machines = 0
        heat_cost, building_cost = 0, 0
        machine_display_name = machine.machine_name
    else:
        num_machines = max(1, math.ceil(machine.required_ipm / machine.provided_ipm))
        heat_cost, building_cost = find_building_cost(machine.machine_name, num_machines, buildings)
        machine_display_name = \
            f"{machine.machine_name} (x{num_machines})  [heat {heat_cost}] [{building_cost}]"

    box_size = 46
    print(f"{indent_str}┌{'─'*(box_size+2)}┐")
    print("%s│ %-*s │" % (indent_str, box_size, machine_display_name))
    print("%s│ %-*s │" % (indent_str, box_size, machine.item_name))
    if machine.is_existing_provider:
        print("%s│ %-*s │" % (indent_str, box_size, f"prov: {machine.provided_ipm}"))
    else:
        total_provided = num_machines*machine.provided_ipm
        per_machine = machine.provided_ipm
        print("%s│ %-*s │" % (indent_str, box_size, f"prov: {total_provided}    ({per_machine}/machine)"))
        print("%s│ %-*s │" % (
            indent_str,
            box_size,
            f"req:  {machine.required_ipm:.2f} ({machine.get_ratio():.3f} machines)"))
    print(f"{indent_str}└{'─'*(box_size+2)}┘")
    for i in machine.inputs:
        print_machine_tree(i, buildings, depth_limit, "|   " + indent, current_depth + 1)

#--------------------------------------------------------------------------------------------------

# Recurse limit to prevent infinite recursion.
MAX_WALK_DEPTH = 100

# Node types
NODE_ITEM = 0
NODE_INPUT = 1
NODE_RAW = 2

#:param source_list: Which list to search: 0 = items, 1 = input, 2 = raw

def walk_item_chain(    item_name: str,
                        items: list[Item],
                        recipe_inputs: list[RecipeInput],
                        raw_items: list[RawItem],
                        required_ipm: float,
                        source_list: int = 0,
                        walk_depth: int = 0,
                        current_machine: Machine = None,
                        production_chain_key: str = None) -> Machine:

    #print(f"S:{source_list}, I:{item_name}, PCK:{production_chain_key}")

    global crafting_items
    walk_depth += 1
    if MAX_WALK_DEPTH < walk_depth:
        raise ValueError("Exceeded walk item chain recursion depth.")

    match source_list:
        case 0: # NODE_ITEM
            found_item = find_item(item_name, items)
            #print(walk_depth, found_item)
            ci = crafting_items \
                .get(found_item.item_name, RequiredItem()) \
                .add_provided(found_item.items_per_minute) \
                .set_machine_name(found_item.factory)
            crafting_items[found_item.item_name] = ci
            if(item_name == requesting[0]):
                ci.add_required(requesting[1])
            machine = Machine(found_item.factory, found_item.item_name, found_item.items_per_minute, required_ipm)
            if current_machine is not None:
                current_machine.add_input(machine)
            # Move to process the inputs, doesn't descend to next node thus the production_chain_key is not altered.
            walk_item_chain(item_name, items, recipe_inputs, raw_items, 0, NODE_INPUT, walk_depth, machine, production_chain_key)
            # The very first machine is the root of the tree and is the one that produces the
            # requested item. Will result in the root machine being returned.
            return machine
        case 1: # NODE_INPUT
            found_items = find_inputs(item_name, recipe_inputs)
            for fi in found_items:
                #print(walk_depth, fi)
                #
                # Get the required input ipm to produce the item at the required rate.
                #
                required_input_ipm = fi.required_per_minute * current_machine.get_ratio()
                #
                # Modify the input rate based on available inputs.
                #
                existing_inputs = available_inputs.get(production_chain_key or item_name)
                #print(f"IN:{fi.input_name} EI:{existing_inputs}")
                if existing_inputs is not None:
                    existing_ipm = existing_inputs.get(fi.input_name, 0)
                    if 0 < existing_ipm:
                        # Add the existing input provided as a special machine.
                        existing_provider = new_existing_provider_machine(fi.input_name, existing_ipm)
                        current_machine.add_input(existing_provider)
                        #print(existing_ipm)
                        required_input_ipm -= existing_ipm
                        # When all required items are provided by the existing input, no further
                        # processing down this branch is needed. However, it is possible that the
                        # existing input doesn't cover the requirement, in that case, the remaining
                        # amount must be calculated.
                        if required_input_ipm <= 0:
                            #print(f"Don't need to continue this chain, already provided. {required_input_ipm}")
                            continue
                #
                #
                #
                crafting_items[fi.input_name] = crafting_items \
                    .get(fi.input_name, RequiredItem()) \
                    .add_required(required_input_ipm)
                if production_chain_key is None:
                    pckey = ";".join([item_name, fi.input_name])
                else:
                    pckey = ";".join([production_chain_key, fi.input_name])
                if is_raw(fi.input_name):
                    walk_item_chain(fi.input_name, items, recipe_inputs, raw_items, required_input_ipm, NODE_RAW, walk_depth, current_machine, pckey)
                else:
                    walk_item_chain(fi.input_name, items, recipe_inputs, raw_items, required_input_ipm, NODE_ITEM, walk_depth, current_machine, pckey)
        case 2: # NODE_RAW
            fi = find_raw(item_name, "normal", raw_items)
            #print(walk_depth, fi)
            crafting_items[fi.item_name] = crafting_items \
                .get(fi.item_name, RequiredItem()) \
                .add_provided(fi.items_per_minute) \
                .set_machine_name(fi.factory)
            machine = Machine(fi.factory, fi.item_name, fi.items_per_minute, required_ipm)
            current_machine.add_input(machine)

#--------------------------------------------------------------------------------------------------

def is_raw(item_name: str) -> bool:
    """
    Will return True when the item is the start of the production chain. These items are not
    crafted, they are extracted from a resource and thus don't have any inputs.

    :param item_name: Item to check.
    :type item_name: str
    :return: True when is a raw item, or False when not.
    :rtype: bool
    """
    return item_name in raw_item_names

#--------------------------------------------------------------------------------------------------

def initialize_raw_items(raw_items: list[RawItem]):
    global raw_item_names
    for ri in raw_items:
        raw_item_names.add(ri.item_name)

#--------------------------------------------------------------------------------------------------

def find_item(item_name: str, items: list[Item]):
    for i in items:
        if item_name == i.item_name:
            return i
    raise ValueError("Cannot find item '%s' in items." % item_name)

#--------------------------------------------------------------------------------------------------

def find_inputs(item_name: str, recipe_inputs: list[RecipeInput]) -> list[RecipeInput]:
    found = []
    for i in recipe_inputs:
        if item_name == i.item_name:
            found.append(i)
    if 0 == len(found):
        raise ValueError("Cannot find item '%s' in recipe_inputs." % item_name)
    return found

#--------------------------------------------------------------------------------------------------

def find_raw(item_name: str, variant: str, raw_items: list[RawItem]) -> RawItem:
    for i in raw_items:
        if item_name == i.item_name and variant == i.variant:
            return i
    raise ValueError("Cannot find item '%s' in raw_items." % item_name)

#--------------------------------------------------------------------------------------------------

def load_data() -> tuple[list[Item], list[RecipeInput], list[RawItem], list[Building]]:
    def item_conv(row):
        o = Item(row[0], int(row[1]), float(row[2]), row[3], int(row[4]))
        #print(o.item_name, o.num_produced, o.period_seconds, o.factory, o.items_per_minute)
        return o

    def input_conv(row):
        o = RecipeInput(row[0], row[1], int(row[2]), float(row[3]), int(row[4]))
        #print(o.item_name, o.input_name, o.num_required)
        return o

    def raw_conv(row):
        o = RawItem(row[0], row[1], int(row[2]), int(row[3]), row[4], int(row[5]))
        #print(o.item_name, o.variant, o.num_produced)
        return o

    def building_conv(row):
        mat_type: str = None
        build_cost: int = None
        if 0 < len(str.strip(row[2])):
            mat_type = "bbm"
            build_cost = int(row[2])
        elif 0 < len(str.strip(row[3])):
            mat_type = "ibm"
            build_cost = int(row[3])
        elif 0 < len(str.strip(row[4])):
            mat_type = "qbm"
            build_cost = int(row[4])
        if mat_type is None:
            raise ValueError(f"No building cost defined for machine '{row[0]}'.")
        o = Building(row[0], int(row[1]), mat_type, build_cost)
        #print(o.building_name, o.heat_cost, o.building_cost, o.building_material_type)
        return o


    items = load_file('starrupture_recipe_items.csv', item_conv)
    recipe_inputs = load_file('starrupture_recipe_input.csv', input_conv)
    raw_items = load_file('starrupture_recipe_raw.csv', raw_conv)
    buildings = load_file('starrupture_recipe_buildings.csv', building_conv)

    return (items, recipe_inputs, raw_items, buildings)


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

"""
{
    "request": {
        // Name of item to be crafted.
        "item": "",

        // Number of items to craft per minute. This can be overridden by the value specified on
        // the program command line. When set to a value less than 1, the default is to use
        // the number of items that can be produced by a single machine per minute.
        "items_per_minute": 0
    },

    // Optional list of available items that can be fed into the production chain.
    "inputs": [
        {
            // Provided items are intended to be used as an input for crafting a specific item.
            // The array is the names starting at the machine producing the requested item, and
            // working backwards down the manufacturing chain.
            //
            // For example, when crafting 'electronics' and existing supply of inductors is
            // available, then for_item will be: ["electronics"]. However, if a certain amount of
            // calcite sheets are available to produce ceramics for synthetic silicon, then
            // for_item will be: ["electronics", "synthetic silicon", "ceramics"]
            "for_item": [""],
            // The item that is provided from an existing manifacturing site.
            "provided_item": "",
            // The items per minute that can be provided.
            "provided_ipm": 0
        }
    ]
}
"""

SPEC_INPUTS_TEMPLATE = """,

    "inputs": [
        {
            "for_item": [""],
            "provided_item": "",
            "provided_ipm": 0
        }
    ]"""

#---------------------------------------------------------------------------------------------------

def generate_spec_file(aparser:argparse.ArgumentParser, args:argparse.Namespace, items:list[Item]):
    item_name = args.item
    if item_name is None:
        aparser.exit(1, "Must specify item name with '--item' when generating spec file.\n\n")
    ipm = args.count \
        if args.count is not None else get_count_item_produced_from_one_machine(item_name, items)
    write_out_spec_template(args.genspec, item_name, ipm, args.use_input)

#---------------------------------------------------------------------------------------------------

def write_out_spec_template(spec_filename:str, item_name:str, ipm:int, include_inputs:bool):

    inputs = SPEC_INPUTS_TEMPLATE if include_inputs else ""

    spec_content = f"""{{
    "request": {{
        "item": "{item_name}",
        "items_per_minute": {ipm}
    }}{inputs}
}}
"""

    with open(spec_filename, "w") as f:
        f.write(spec_content)

    print(f"Written spec file '{spec_filename}'.")

#---------------------------------------------------------------------------------------------------

def parse_request_spec(spec_filename: str) -> tuple[str, int, dict[str, tuple[str, int]]]:
    with open(spec_filename) as jsf:
        spec = json.load(jsf)
    return get_spec_request(spec)

#---------------------------------------------------------------------------------------------------

def get_spec_request(spec: dict) -> tuple[str, int, dict[str, dict[str, int]]]:
    """
    Extract the item request from the specification.

    :param spec: JSON specification containing the request as well as other parameters.
    :type spec: dict
    :return: A tuple of the requested item name, the number of items to be crafted per minute,
             and available existing inputs.
             If items_per_minute is not provided in the spec, then None is returned for the
             number.
    :rtype: tuple[str, int, dict[str, dict[str, int]]]
    """
    requested_item_name = spec["request"]["item"]
    requested_ipm = \
        spec["request"].get("items_per_minute")
    return requested_item_name, requested_ipm, get_spec_inputs(spec)

#---------------------------------------------------------------------------------------------------

def get_spec_inputs(spec: dict) -> dict[str, dict[str, int]]:
    """
    Extract the list of available items that can be provided as inputs into the production
    chain.

    :param spec: JSON specification containing the request as well as other parameters.
    :type spec: dict
    :return: The list of available items keyed on the position in the production chain. The key
             is made of all the elements (item name) in the chain starting from the requested item
             and working back, separated by the semicolon charactor. For example, if "valve" is
             requested, and "heat resistant sheet" is provided as an input to nozzle, the key is
             "valve;nozzle".
             The value is a dictionary keyed on the name of an input item of that machine giving
             the IPM available for that input into the item. The value is a dictionary as machines
             can required multiple items as inputs.
    :rtype: dict[str, dict[str, int]]
    """
    existing_inputs: dict[str, dict[str, int]] = dict()
    inputs = spec.get("inputs", [])
    for ii in inputs:
        key = ";".join(ii["for_item"])
        ei = existing_inputs.get(key)
        if ei is None:
            existing_inputs[key] = ei = dict()
        ei[ii["provided_item"]] = ii["provided_ipm"]
    return existing_inputs

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------
