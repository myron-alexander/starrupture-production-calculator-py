
#---------------------------------------------------------------------------------------------------

__all__ = [
]

#---------------------------------------------------------------------------------------------------

import json
from typing import Any

from application_data import GameData, load_game_data

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
        self.capacity_ipm:int = 0
        """
        The total amount able to be supplied. If consumers attempt to pull more then the
        baseline_production_rate_ipm, capacity_ipm will be negative for the amount over
        baseline_production_rate_ipm.
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

def calculate_factory_usage_rates(site_id:str, factory_id:str):
    """

    """

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

def main():
    game_data = load_game_data()

    with open('pins_data.json', 'r', encoding='utf-8') as f:
        map_data = json.load(f)
    
    ledger = NodeLedger()
    populate_defined_production_rates(map_data, game_data, ledger)

    print(ledger.ledger)


#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------