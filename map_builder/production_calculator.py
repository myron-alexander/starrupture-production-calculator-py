
#---------------------------------------------------------------------------------------------------

__all__ = [
]

#---------------------------------------------------------------------------------------------------

import json
from typing import Any
from abc import ABC, abstractmethod

from application_data import GameData, load_game_data

#---------------------------------------------------------------------------------------------------

def make_map_node_key(id:str, site_id:str, factory_id:str|None) -> str:
    return f"{site_id};{factory_id or ""};{id}"

#---------------------------------------------------------------------------------------------------

class MapNode(ABC):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, id:str, site_id:str, factory_id:str|None = None) -> None:
        self.key:str = make_map_node_key(id, site_id, factory_id)
        self.site_id = site_id
        self.factory_id = factory_id or ""
        self.node_id = id
        self.inputs:list["MapNode"] = []
        # Presume not part of any input until otherwise known.
        self._terminal = True

    #---------------------------------------------------------------------------

    @property
    @abstractmethod
    def is_boundary(self) -> bool:
        """
        True when node is an entry point into the factory, or out of the factory. This is
        intended to be used when traversing the tree, to detect the crossing point from one
        factory to another without having to check the node type.
        """
        pass

    #---------------------------------------------------------------------------

    @property
    def is_terminal(self) -> bool:
        """
        A node that is at the end of a production chain is called a terminal.
        Only crafters, storage and dispatchers can be at the end of a production chain so only
        they can be terminal. All such nodes are considered terminal until they supply items
        to a consumer, in which case they are not terminal.
        """
        return self._terminal

    #---------------------------------------------------------------------------

    def set_not_terminal(self) -> None:
        self._terminal = False

    #---------------------------------------------------------------------------

    def __str__(self) -> str:
        return self.__repr__()

    #---------------------------------------------------------------------------

    def __repr__(self) -> str:
        return \
            f"{type(self).__name__} [\n"\
            f"   key     : {self.key}\n"\
            f"   terminal: {self._terminal}\n"\
            f"   inputs  : {[n.key for n in self.inputs]}\n"\
             "]\n"

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapResourceNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, resource_id:str) -> None:
        super().__init__(resource_id, site_id)
        # A resource cannot be a terminal, only dispatcher, storage and crafter.
        self._terminal = False

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return False

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapCrafterNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, crafter_id:str) -> None:
        super().__init__(crafter_id, site_id, factory_id)

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return False

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapStorageNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, storage_id:str) -> None:
        super().__init__(storage_id, site_id, factory_id)

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return False

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapDispatcherNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, dispatcher_id:str) -> None:
        super().__init__(dispatcher_id, site_id, factory_id)

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return True

    #---------------------------------------------------------------------------

    def set_not_terminal(self) -> None:
        # A dispatcher is always terminal within the factory.
        return

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapReceiverNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, receiver_id:str) -> None:
        super().__init__(receiver_id, site_id, factory_id)
        # A receiver cannot be a terminal, only dispatcher, storage and crafter.
        self._terminal = False

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return True

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapNetwork:
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        self.map_nodes:dict[str,MapNode] = {}

    #---------------------------------------------------------------------------

    def add_node(self, node:MapNode) -> None:
        self.map_nodes[node.key] = node

    #---------------------------------------------------------------------------

    def get_factory_node(self, site_id:str, factory_id:str, id:str) -> MapNode:
        key = make_map_node_key(id, site_id, factory_id)
        return self.map_nodes[key]

    #---------------------------------------------------------------------------

    def get_site_node(self, site_id:str, id:str) -> MapNode:
        key = make_map_node_key(id, site_id, None)
        return self.map_nodes[key]

    #---------------------------------------------------------------------------

    def __str__(self) -> str:
        return self.__repr__()

    #---------------------------------------------------------------------------

    def __repr__(self) -> str:
        nodes = [n for n in self.map_nodes.values()]
        nodes.sort(key=lambda n:n.key)
        return "\n".join([str(n) for n in nodes])

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class NodeLedgerEntry:
    """
    Provides the production crafting rates as well as pull rates. Buffer nodes (storage) are not
    catered for.
    """

    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        self.baseline_production_rate_ipm:int = 0
        """
        Production rate as per game definition.
        """
        self.baseline_pull_rate_ipm:dict[str, int] = {}
        """
        Pull rates as per game definition.
        """
        self.actual_production_rate_ipm:int = 0
        """
        Production rate modified for any limitations or according the the needs of the consumers
        that this node is supplying. Will always be a number <= than baseline_pull_rate_ipm.
        """
        self.actual_pull_rate_ipm:dict[str, int] = {}
        """
        Pull rates modified for the actual needs of the production rate. Thus if the
        actual_production_rate_ipm is less than baseline_production_rate_ipm, then these
        values will be reduced to scale.
        """
        self.required_ipm:dict[str, int] = {}
        """
        """
        self.capacity_ipm:int = 0
        """
        The total amount able to be supplied. If consumers attempt to pull more then the
        actual_production_rate_ipm, capacity_ipm will be negative for the amount over
        actual_production_rate_ipm.
        """

    #---------------------------------------------------------------------------

    def initalize_for_resource(self, baseline_production_rate_ipm:int) -> None:
        self.baseline_production_rate_ipm = baseline_production_rate_ipm
        self.capacity_ipm = baseline_production_rate_ipm

    #---------------------------------------------------------------------------

    def initialize_for_crafter(
            self,
            baseline_production_rate_ipm:int,
            baseline_pull_rates:list[tuple[str,int]]|tuple[tuple[str,int]]
        ) -> None:
        self.baseline_production_rate_ipm = baseline_production_rate_ipm
        self.capacity_ipm = baseline_production_rate_ipm
        self.baseline_pull_rate_ipm = dict(baseline_pull_rates)
        self.actual_pull_rate_ipm = dict((k, 0) for k in self.baseline_pull_rate_ipm.keys())

    #---------------------------------------------------------------------------

    def initialize_for_dispatcher(
            self, dispatched_item:str, dispatched_ipm:int, input_ipm:int) -> None:
        self.baseline_production_rate_ipm = dispatched_ipm
        self.capacity_ipm = dispatched_ipm
        self.baseline_pull_rate_ipm[dispatched_item] = input_ipm
        self.actual_pull_rate_ipm = dict((k, 0) for k in self.baseline_pull_rate_ipm.keys())

    #---------------------------------------------------------------------------

    def initialize_for_receiver(self, dispatched_item:str, dispatched_ipm:int) -> None:
        self.baseline_production_rate_ipm = dispatched_ipm
        self.capacity_ipm = dispatched_ipm
        self.baseline_pull_rate_ipm[dispatched_item] = 0
        self.actual_pull_rate_ipm = dict((k, 0) for k in self.baseline_pull_rate_ipm.keys())

    #---------------------------------------------------------------------------

    @property
    def is_raw(self) -> bool:
        """
        When the entry is for an extracted resource, will return True.
        """
        return 0 == len(self.baseline_pull_rate_ipm)

    #---------------------------------------------------------------------------

    def __str__(self) -> str:
        return self.__repr__()

    #---------------------------------------------------------------------------

    def __repr__(self) -> str:
        return \
            "NodeLedgerEntry: [\n"\
           f"   baseline_production_rate_ipm: {self.baseline_production_rate_ipm}\n"\
           f"   baseline_pull_rate_ipm      : {self.baseline_pull_rate_ipm.items()}\n"\
           f"   capacity_ipm                : {self.capacity_ipm}\n"\
           f"   actual_production_rate_ipm  : {self.actual_production_rate_ipm}\n"\
           f"   actual_pull_rate_ipm        : {self.actual_pull_rate_ipm.items()}\n"\
           f"   is_raw                      : {self.is_raw}\n"\
            "]\n"


#---------------------------------------------------------------------------------------------------

class NodeLedger:
    """
    Buffer nodes (storage) are not catered for.
    """
    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        self.ledger:dict[str, NodeLedgerEntry] = {}
        self.factory_production_target_ipm:dict[str, dict[str,int]] = {}
        """
        In order to calculate usage rates, it must be possible to set a target production rate
        for an item of a factory. The key is "site_id;factory_id" and the value is a mapping from
        item to target rate ipm.
        """

    #---------------------------------------------------------------------------

    def set_factory_target_rate(
            self, site_id:str, factory_id:str, item_id:str, target_rate_ipm:int) -> None:
        """
        Set the target rate for an item produced in a factory.

        Parameters
        ---------
        site_id : str
            Identifies the site.

        factory_id : str
            Identifies the factory.

        item_id : str
            Identifies the item which must be produced at the target rate.

        target_rate_ipm : int
            The rate, in items per minute, at which the factory must produce the item.
        """
        key = f"{site_id};{factory_id}"
        target_ipms = self.factory_production_target_ipm.setdefault(key, {})
        target_ipms[item_id] = target_rate_ipm

    #---------------------------------------------------------------------------

    def remove_factory_target_rate(
            self, site_id:str, factory_id:str, item_id:str|None = None) -> None:
        """
        Remove the target rate for an item, or all items, of a factory.

        Parameters
        ---------
        site_id : str
            Identifies the site.

        factory_id : str
            Identifies the factory.

        item_id : str|None
            When provided, identifies the item whose target rate is to be removed. If not provided,
            the entire factory is removed from the factory target rate collection.
        """
        key = f"{site_id};{factory_id}"
        if key in self.factory_production_target_ipm:
            if item_id is not None:
                target_ipms = self.factory_production_target_ipm[key]
                if item_id in target_ipms:
                    del target_ipms[item_id]
            else:
                del self.factory_production_target_ipm[key]

    #---------------------------------------------------------------------------

    @staticmethod
    def __make_factory_ledger_key(site_id:str, factory_id:str, node_id:str):
        return f"fac:{site_id};{factory_id};{node_id}"

    #---------------------------------------------------------------------------


    @staticmethod
    def __make_resource_ledger_key(site_id:str, node_id:str):
        return f"res:{site_id};{node_id}"

    #---------------------------------------------------------------------------

    def add_resource_entry(self, site_id:str, node_id:str, ledger_entry:NodeLedgerEntry) -> None:
        """
        Add a resource node ledger entry to the ledger.
        """
        key = NodeLedger.__make_resource_ledger_key(site_id, node_id)
        if key in self.ledger:
            raise ValueError(f"Ledger entry for node ({site_id}, {node_id}) exists.")
        self.ledger[key] = ledger_entry

    #---------------------------------------------------------------------------

    def add_factory_entry(self, site_id:str, factory_id:str, node_id:str, ledger_entry:NodeLedgerEntry) -> None:
        """
        Add a factory node ledger entry to the ledger.
        """
        key = NodeLedger.__make_factory_ledger_key(site_id, factory_id, node_id)
        if key in self.ledger:
            raise ValueError(f"Ledger entry for node ({site_id}, {factory_id}, {node_id}) exists.")
        self.ledger[key] = ledger_entry

    #---------------------------------------------------------------------------

    def get_factory_entry(self, site_id:str, factory_id:str, node_id:str) -> NodeLedgerEntry:
        key = NodeLedger.__make_factory_ledger_key(site_id, factory_id, node_id)
        return self.ledger[key]

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

def populate_defined_production_rates(
        map_data:dict[str,Any], game_data:GameData, ledger:NodeLedger) -> None:
    """
    Set all the extraction/production rates as per the game definitions. This provides the baseline
    for calculating input, usage and output rates.
    """

    for site_id, site_values in map_data.items():
        for resource_id, resource_values in site_values.get("resource_nodes", {}).items():
            item_name = resource_values["resource_item"]
            variant = resource_values["variant"]
            definition = next(
                (r for r in game_data.raw_item_definitions
                    if r.item_name == item_name and r.variant == variant)
                , None
            )
            if definition is None:
                raise ValueError(
                    f"Game definition for resource ({item_name}, {variant}) of node"
                    f" ({site_id}, {resource_id}) not found.")
            # Resources don't pull items, they are a primary source of items.
            entry = NodeLedgerEntry()
            entry.initalize_for_resource(definition.items_per_minute)
            ledger.add_resource_entry(site_id, resource_id, entry)

        for factory_id, factory_values in site_values.get("factories", {}).items():
            machines = factory_values.get("machines", {})
            for crafter_id, crafter_values in machines.get("crafters", {}).items():
                item_name = crafter_values["crafted_item"]
                definition = next(
                    (d for d in game_data.item_definitions if d.item_name == item_name)
                    , None
                )
                if definition is None:
                    raise ValueError(
                        f"Game definition for item ({item_name}) of node"
                        f" ({site_id}, {factory_id}, {crafter_id}) not found.")
                entry = NodeLedgerEntry()
                recipe = game_data.item_recipes.get(item_name, None)
                if recipe is None:
                    raise ValueError(
                        f"Game recipe definition for item ({item_name}) of node"
                        f" ({site_id}, {factory_id}, {crafter_id}) not found.")
                entry.initialize_for_crafter(
                    definition.items_per_minute, [(r[0], r[2]) for r in recipe])
                ledger.add_factory_entry(site_id, factory_id, crafter_id, entry)

            for displatcher_id, dispatcher_value in factory_values.get("dispatchers", {}).items():
                item_name = dispatcher_value["dipatched_item"]
                output_ipm = int(dispatcher_value["output_rate_limit_ipm"])
                input_ipm = int(dispatcher_value["input_rate_limit_ipm"])
                entry = NodeLedgerEntry()
                entry.initialize_for_dispatcher(item_name, output_ipm, input_ipm)
                ledger.add_factory_entry(site_id, factory_id, displatcher_id, entry)

    # Must process the receivers after all the dispatcher have been added to the ledger.
    for site_id, site_values in map_data.items():
        for factory_id, factory_values in site_values.get("factories", {}).items():
            for receiver_id, receiver_value in factory_values.get("receivers", {}).items():
                dispatcher_site_id = receiver_value["site_id"]
                dispatcher_factory_id = receiver_value["factory_id"]
                dispatcher_id = receiver_value["dispatcher_id"]
                dispatcher_entry = ledger.get_factory_entry(
                    dispatcher_site_id, dispatcher_factory_id, dispatcher_id)
                dispatched_item = next(k for k in dispatcher_entry.baseline_pull_rate_ipm.keys())
                # The baseline production rate for a receiver is the same as that for the
                # corresponding dispatcher. The baseline pull rate is 0 as the receiver is a
                # bridge between the dispatcher and nodes within the factory so it doesn't
                # pull unless requested to do so.
                entry = NodeLedgerEntry()
                entry.initialize_for_receiver(
                    dispatched_item, dispatcher_entry.baseline_production_rate_ipm)
                ledger.add_factory_entry(site_id, factory_id, receiver_id, entry)

#---------------------------------------------------------------------------------------------------

def calculate_factory_production_and_pull_rates(
        site_id:str, factory_id:str,map_data:dict[str,Any], ledger:NodeLedger) -> None:
    """
    Calculate the actual production and pull rates for nodes in the factory based on the
    set target rates, or pull request from another factory depending on which is greater.

    If the factory has neither a set target rate, nor a dispatcher for a terminal item producer,
    then the actual production rate and pull rates for that terminal item producer will be zero.
    A terminal item producer is one that produces an item and is not an input into either another
    producer, or storage.
    """

    # 1. Find all the terminal producers.
    # 2. For each terminal producer, set the required_ipm from either the factory target or
    #    the dispatcher.
    # 3. Iterate through the production tree setting the required ipm.
    # 4. Once all the required ipm values have been set, calculate the


#---------------------------------------------------------------------------------------------------

def calculate_factory_input_rates(site_id:str, factory_id:str):
    """
    Determine the input rates for each source into the factory.
    When the input is from an extractor, then the limitation is the lesser of:
      1. extraction rate
      2. transport rate
      3. remaining extraction rate after deducting the total usage of extractor resource
         across all other factories using the resource
      4. usage rate within the factory

    When the input rate is from an receiver, the limitation is the lesser of
    calculated dispatch rate, which includes the calculated input rate into the dispatcher,
    and transport rate from the receiver.

    This calculation can only be performed when all the input elements are known. This means, for
    inputs that are receivers, then the factory output rates of the other factory must have been
    calculated.
    """

#---------------------------------------------------------------------------------------------------

def build_map_network(map_data:dict[str,Any]) -> MapNetwork:

    map_network = MapNetwork()

    #
    # Create the nodes in the network.
    #

    for site_id, site_values in map_data.items():
        for resource_id in site_values.get("resource_nodes", {}).keys():
            map_network.add_node(MapResourceNode(site_id, resource_id))
        for factory_id, factory_values in site_values.get("factories", {}).items():
            machines = factory_values.get("machines", {})
            for crafter_id in machines.get("crafters", {}).keys():
                map_network.add_node(MapCrafterNode(site_id, factory_id, crafter_id))
            for storage_id in machines.get("storage", {}).keys():
                map_network.add_node(MapStorageNode(site_id, factory_id, storage_id))
            for displatcher_id in factory_values.get("dispatchers", {}).keys():
                map_network.add_node(MapDispatcherNode(site_id, factory_id, displatcher_id))
            for receiver_id in factory_values.get("receivers", {}).keys():
                map_network.add_node(MapReceiverNode(site_id, factory_id, receiver_id))

    print(map_network)

    #
    # Link the nodes.
    #

    def get_input_node(site_id, factory_id, input_id, resource_ids) -> MapNode:
        if input_id in resource_ids:
            node = map_network.get_site_node(site_id, input_id)
        else:
            node = map_network.get_factory_node(site_id, factory_id, input_id)
        # Node is now known as an input.
        node.set_not_terminal()
        return node

    for site_id, site_values in map_data.items():
        resource_ids = [k for k in site_values.get("resource_nodes", {})]
        
        for factory_id, factory_values in site_values.get("factories", {}).items():
            machines = factory_values.get("machines", {})

            for crafter_id, crafter_values in machines.get("crafters", {}).items():
                crafter_node = map_network.get_factory_node(site_id, factory_id, crafter_id)
                for ii in crafter_values["inputs"]:
                    for input_id in ii["from_ids"]:
                        crafter_node.inputs.append(
                            get_input_node(site_id, factory_id, input_id, resource_ids))

            for storage_id, storage_values in machines.get("storage", {}).items():
                storage_node = map_network.get_factory_node(site_id, factory_id, storage_id)
                for ii in storage_values["inputs"]:
                    for input_id in ii["from_ids"]:
                        storage_node.inputs.append(
                            get_input_node(site_id, factory_id, input_id, resource_ids))

            for displatcher_id, dispatcher_values in factory_values.get("dispatchers", {}).items():
                dispatcher_node = map_network.get_factory_node(site_id, factory_id, displatcher_id)
                for input_id in dispatcher_values["from_ids"]:
                    dispatcher_node.inputs.append(
                        get_input_node(site_id, factory_id, input_id, resource_ids))
            
            for receiver_id, receiver_values in factory_values.get("receivers", {}).items():
                receiver_node = map_network.get_factory_node(site_id, factory_id, receiver_id)
                other_site_id = receiver_values["site_id"]
                other_factory_id = receiver_values["factory_id"]
                other_dispatcher_id = receiver_values["dispatcher_id"]
                receiver_node.inputs.append(
                    get_input_node(
                        other_site_id, other_factory_id, other_dispatcher_id, resource_ids))
            
    return map_network


#---------------------------------------------------------------------------------------------------

def main():
    game_data = load_game_data()

    with open('pins_data.json', 'r', encoding='utf-8') as f:
        map_data = json.load(f)

    # ledger = NodeLedger()
    # populate_defined_production_rates(map_data, game_data, ledger)
    # print(ledger.ledger)

    map_network = build_map_network(map_data)
    print(map_network)


#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------