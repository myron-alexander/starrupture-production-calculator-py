"""
Production capacity calculator.

Not complete, only implemented a vary naive approach.
Missing:

1. Calculating difference between wanted rate and supplied rate. This would be shown for the inputs
   to blocks.
2. Taking into consideration transport rate limits.
3. Loading targets from map data and calculating the production rates for all the targets.
4. Support for multi-type storage.
5. Allow for setting a target amount alongside the rate, and calculating the time to reach the
   target amount at the current supply rate.
"""

#---------------------------------------------------------------------------------------------------

__all__ = [
]

#---------------------------------------------------------------------------------------------------

import json
import math
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, cast

from application_data import GameData, load_game_data
import map_data as mmapd

#---------------------------------------------------------------------------------------------------

class NodePullRequest:
    """
    """
    def __init__(self, request_node:"Ledger", request_ipm:int = 0) -> None:
        self.request_node = request_node
        self.request_ipm:int = request_ipm
        # Since I have removed support for nodes to supply more than one item type, the pull
        # request doesn't need to specify the pulled item.

#---------------------------------------------------------------------------------------------------


"""
Types of nodes in the production chain:

1. Resource                 - Provides the raw materials for production.
                              Necessary to start the chain.
                              No inputs.
2. Crafter                  - Transforms one or more input materials/items into items.
                              Necessary for production.
                              Needs inputs.
3. Single-type Intermediary - Accepts inputs of a specified item or material.
                              Delivers the same item or material as output.
                              Example: dispatcher, single type storage.
4. Multi-type Intermediary  - Accepts inputs of multiple item or material types.
                              Delivers a specified item or material as output on request.
                              Example: receiver, multi-type storage.
"""



class Ledger(ABC):

    #---------------------------------------------------------------------------

    @abstractmethod
    def get_owner_id(self) -> str:
        """
        Get the owner node's id.
        """
        pass


    #---------------------------------------------------------------------------

    @abstractmethod
    def supply_rate_ipm(self, request_item:str|None = None) -> int:
        """
        The amount actually supplied by this node for the requested item.

        Parameters
        ----------
        request_item : str|None
            The name of the item being requested. This is necessary for multi-type suppliers to
            determine which item is being requested. For single-type suppliers, this parameter is
            ignored and can be passed as None.
        """
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def clear_requests(self) -> None:
        """
        Clear the requests from the input nodes. This is intended to be used when recalculating
        the production rates for a factory, to clear the existing requests before recalculating and
        approving new requests.

        Doesn't propagate the clear to the suppliers.
        """
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def request_supplies(self, requestor:"Ledger", request_item:str, request_ipm:int) -> int:
        """
        Request delivery of supplies from the suppliers at the rate of request_ipm.
        Passing in zero to request_ipm will revoke the request from all the suppliers.

        Parameters
        ----------
        request_item : str
            The name of the item being requested. This is necessary for multi-type suppliers to
            determine which item is being requested.

        request_ipm : int
            The amount of the item being requested per minute.

        Returns
        -------
        int:
            The approved request rate which will be less than or equal to request_ipm.
        """
        pass

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class SingleItemLedger(Ledger):
    """
    Ledger for nodes that only supply one type of item.
    """

    def __init__(self) -> None:

        self._supply_rate_ipm:int = 0
        """
        The amount actually supplied by this node to its consumers.
        """

        self._approved_pull_requests:list[NodePullRequest] = []
        """
        The list of requestors that are consuming the item produced, and the amounts they are
        approved to consume.
        """

    #---------------------------------------------------------------------------

    def supply_rate_ipm(self, request_item:str|None = None) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests.clear()
        self._supply_rate_ipm = 0

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class ResourceLedger(SingleItemLedger):
    """
    Ledger for resource nodes that are primary providers of items.
    """
    #---------------------------------------------------------------------------

    def __init__(self, owner: mmapd.MapResourceNode) -> None:
        super().__init__()
        self._owner = owner

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_global_id()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:

        assert requestor is not None, "Requestor cannot be None."

        assert request_item == self._owner.supplied_item_name, \
            f"Requested item '{request_item}' does not match the supplied item"\
            f" '{self._owner.supplied_item_name}' for single storage node '{self._owner.get_global_id()}'."

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        idx, existing_request = next(
            (r for r in enumerate(self._approved_pull_requests) if r[1].request_node == requestor)
            , (-1, None)
        )

        approved_request_ipm = 0

        if 0 == request_ipm:
            # A zero request means that the requestor wishes to revoke their request.
            if existing_request is not None:
                del self._approved_pull_requests[idx]
        else:
            capacity = self._owner.max_production_ipm - self._supply_rate_ipm - request_ipm
            if existing_request is not None:
                capacity += existing_request.request_ipm

            if 0 <= capacity:
                approved_request_ipm = request_ipm
            else:
                over_capacity = abs(capacity)
                approved_request_ipm = request_ipm - over_capacity
                capacity = 0

            if 0 == approved_request_ipm:
                if existing_request is not None:
                    # No additional resources approved.
                    approved_request_ipm = existing_request.request_ipm

            elif 0 < approved_request_ipm:
                if existing_request is None:
                    self._approved_pull_requests.append(NodePullRequest(requestor, approved_request_ipm))
                else:
                    existing_request.request_ipm = approved_request_ipm

            else:
                raise ValueError(
                    "Error in request approval amount calculation. Approved request is negative"
                    f" thus invalid. Result ({approved_request_ipm}).")

        self._supply_rate_ipm = sum([r.request_ipm for r in self._approved_pull_requests])

        return approved_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class CrafterLedger(SingleItemLedger):
    """
    Ledger for crafter nodes that are producers of items that require inputs.
    """
    #---------------------------------------------------------------------------

    def __init__(self, owner: mmapd.MapCrafterNode) -> None:
        super().__init__()
        self._owner = owner

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_global_id()

    #---------------------------------------------------------------------------

    def _request_supplies_for_deliverable(
            self, recipe_item:mmapd.RecipeItem, rate_ratio:float) -> tuple[int,int]:

        adjusted_required_ipm = math.ceil(recipe_item.required_ipm * rate_ratio)
        remaining_request_ipm = adjusted_required_ipm

        for supplier in recipe_item.get_suppliers(recipe_item.recipe_item_name):
            # Iterating through all the suppliers even when the remaining is
            # reduced to zero so that those suppliers that are not longer
            # being used will have their request revoked.
            node = cast(mmapd.MapNode, supplier)
            ledger = cast(Ledger, node.ledger)
            remaining_request_ipm \
                -= ledger.request_supplies(
                    self, recipe_item.recipe_item_name, remaining_request_ipm)
            assert 0 <= remaining_request_ipm

        approved_request_ipm = adjusted_required_ipm - remaining_request_ipm

        return adjusted_required_ipm, approved_request_ipm

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:

        assert requestor is not None, "Requestor cannot be None."

        assert request_item == self._owner.supplied_item_name, \
            f"Requested item '{request_item}' does not match the supplied item"\
            f" '{self._owner.supplied_item_name}' for single storage node '{self._owner.get_global_id()}'."

        #print(f"request_supplies: {self.key} --> {requestor.key}")

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        idx, existing_request = next(
            (r for r in enumerate(self._approved_pull_requests) if r[1].request_node == requestor)
            , (-1, None)
        )

        # By design, all the requests within pull_requests are already approved, meaning the
        # suppliers are able to supply the desired amounts so any request rate of the existing
        # supply rate or lower, when requesting supplies from suppliers, will be expected to be
        # approved.

        other_requests_ipm = self._supply_rate_ipm
        if existing_request is not None:
            other_requests_ipm -= existing_request.request_ipm

        assert other_requests_ipm <= self._owner.max_production_ipm

        if other_requests_ipm == self._owner.max_production_ipm:
            # No capacity for any more requests, so the request will be rejected.
            assert existing_request is None
            return 0

        required_ipm = min(other_requests_ipm + request_ipm, self._owner.max_production_ipm)

        #
        # Request the suppliers for the recipe input items.
        # When this is a revokation request, the request to suppliers should always return with
        # full approval.
        #

        assert True if 0 < request_ipm else other_requests_ipm == required_ipm

        assert self._owner.max_production_ipm > 0\
            , f"Max production ipm for node '{self._owner.get_global_id()}' must be greater than zero"\
               " to calculate rate ratio."

        rate_ratio:float = required_ipm / self._owner.max_production_ipm

        available_inputs:list[tuple[str,int,int]] = []
        for recipe_item in self._owner.get_recipe_items():
            supply_request_ipm, supply_approved_ipm \
                = self._request_supplies_for_deliverable(recipe_item, rate_ratio)
            available_inputs.append(
                (recipe_item.recipe_item_name, supply_request_ipm, supply_approved_ipm))

        #
        # When the request is to revoke, just remove the request from pull requests as the
        # suppliers have already been adjusted.
        #

        if 0 == request_ipm:
            if existing_request is not None:
                del self._approved_pull_requests[idx]
            self._supply_rate_ipm = other_requests_ipm
            assert other_requests_ipm == required_ipm
            return 0

        #
        # When at least one of the suppliers cannot supply any of the required items, then the
        # request cannot be fulfilled at all so revert back to the previous rate.
        #

        lowest_supply = min(r[2] for r in available_inputs)
        if 0 == lowest_supply:
            rate_ratio:float = self._supply_rate_ipm / self._owner.max_production_ipm
            # No supply available, undo requests to suppliers.
            for recipe_item in self._owner.get_recipe_items():
                self._request_supplies_for_deliverable(recipe_item, rate_ratio)
            if existing_request is not None:
                return existing_request.request_ipm
            else:
                return 0

        #
        # When there is insufficient supply for one or more of the inputs, then reduce the request
        # to the lowest supply available by using the ratio of wanted:available.
        #

        adjusted_required_ipm = required_ipm
        all_supplies_available = all(r[1] <= r[2] for r in available_inputs)
        if not all_supplies_available:
            availability_ratios = [(ai[0], ai[2]/ai[1]) for ai in available_inputs]
            lowest_ratio = min([ar[1] for ar in availability_ratios])
            adjusted_required_ipm = math.floor(required_ipm * lowest_ratio)
            for recipe_item in self._owner.get_recipe_items():
                self._request_supplies_for_deliverable(recipe_item, lowest_ratio)

        self._supply_rate_ipm = adjusted_required_ipm

        approved_request_ipm = self._supply_rate_ipm - other_requests_ipm

        assert 0 < approved_request_ipm <= adjusted_required_ipm

        if existing_request is not None:
            existing_request.request_ipm = approved_request_ipm
        else:
            self._approved_pull_requests.append(NodePullRequest(requestor, approved_request_ipm))

        return approved_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class SingleStorageLedger(SingleItemLedger):
    """
    Ledger for single item storage nodes that are suppliers of items that require inputs.
    """
    #---------------------------------------------------------------------------

    def __init__(self, owner:mmapd.MapSingleStorageNode) -> None:
        super().__init__()
        self._owner = owner

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_global_id()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:
        """
        Since storage doesn't produce items, pass on the request to the inputs.
        """

        assert requestor is not None, "Requestor cannot be None."

        assert request_item == self._owner.supplied_item_name, \
            f"Requested item '{request_item}' does not match the supplied item"\
            f" '{self._owner.supplied_item_name}' for single storage node '{self._owner.get_global_id()}'."

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        idx, existing_request = next(
            (r for r in enumerate(self._approved_pull_requests) if r[1].request_node == requestor)
            , (-1, None)
        )

        # By design, all the requests within pull_requests are already approved, meaning the
        # suppliers are able to supply the desired amounts so any request rate of the existing
        # supply rate or lower, when requesting supplies from suppliers, will be expected to be
        # approved.

        other_requests_ipm = self._supply_rate_ipm
        if existing_request is not None:
            other_requests_ipm -= existing_request.request_ipm

        required_ipm = other_requests_ipm + request_ipm

        assert True if 0 < request_ipm else other_requests_ipm == required_ipm

        remaining_request_ipm = required_ipm

        for supplier in self._owner.get_suppliers(request_item):
            node = cast(mmapd.MapNode, supplier)
            ledger = cast(Ledger, node.ledger)
            remaining_request_ipm \
                -= ledger.request_supplies(self, request_item, remaining_request_ipm)

        self._supply_rate_ipm = required_ipm - remaining_request_ipm

        if 0 == request_ipm:
            if existing_request is not None:
                del self._approved_pull_requests[idx]
            return 0

        else:
            approved_request_ipm = self._supply_rate_ipm - other_requests_ipm

            if existing_request is not None:
                # When an approved request exists, there will be at least the capacity of the
                # existing request so approved_request_ipm will be greater than 1.
                existing_request.request_ipm = approved_request_ipm
            else:
                # When no existing request, might have insufficient capacity, in which case
                # approved_request_ipm will less than request_ipm, even zero, but never negative.
                if 0 < approved_request_ipm:
                    self._approved_pull_requests.append(
                        NodePullRequest(requestor, approved_request_ipm))

                elif approved_request_ipm < 0:
                    raise ValueError(
                        "Error in request approval amount calculation. Approved request is negative"
                        f" thus invalid. Result ({approved_request_ipm}).")

        return approved_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class DispatcherLedger(SingleItemLedger):
    #---------------------------------------------------------------------------

    def __init__(self, owner:mmapd.MapDispatcherNode) -> None:
        super().__init__()
        self._owner = owner

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_global_id()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:
        """
        Since dispatcher doesn't produce items, pass on the request to the inputs.
        """

        assert requestor is not None, "Requestor cannot be None."

        assert request_item == self._owner.supplied_item_name, \
            f"Requested item '{request_item}' does not match the supplied item"\
            f" '{self._owner.supplied_item_name}' for dispatcher node '{self._owner.get_global_id()}'."

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        existing_request:NodePullRequest|None = None

        if self._approved_pull_requests:
            existing_request = self._approved_pull_requests[0]

        if existing_request is not None:
            if requestor != existing_request.request_node:
                raise ValueError(
                    "Dispatcher nodes can only have one requestor, which is the corresponding"
                    " receiver. Existing requestor: "
                    f"{existing_request.request_node.get_owner_id()},"
                    f" new requestor: {requestor.get_owner_id()}.")

        remaining_request_ipm = request_ipm

        for supplier in self._owner.get_suppliers(request_item):
            node = cast(mmapd.MapNode, supplier)
            ledger = cast(Ledger, node.ledger)
            remaining_request_ipm \
                -= ledger.request_supplies(self, request_item, remaining_request_ipm)

        self._supply_rate_ipm = request_ipm - remaining_request_ipm

        if 0 == request_ipm:
            self._approved_pull_requests.clear()
            return 0
        else:
            if existing_request is not None:
                existing_request.request_ipm = self._supply_rate_ipm
            else:
                self._approved_pull_requests.append(
                    NodePullRequest(requestor, self._supply_rate_ipm))

        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MultiItemLedger(Ledger):
    """
    Ledger for nodes that supply multiple types of items.
    """
    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._supplied_items:dict[str,SingleItemLedger] = {}

    #---------------------------------------------------------------------------

    def supply_rate_ipm(self, request_item:str|None = None) -> int:
        if request_item is None:
            raise ValueError(
                f"Request item must be specified for multi-item ledger of '{self.get_owner_id()}'.")
        ledger = self._supplied_items.get(request_item)
        if ledger is None:
            return 0
        else:
            return ledger.supply_rate_ipm()

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        for l in self._supplied_items.values():
            l.clear_requests()

    #---------------------------------------------------------------------------

    @property
    def supplied_items(self) -> tuple[SingleItemLedger, ...]:
        return tuple(self._supplied_items.values())

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class ReceiverItemLedger(SingleItemLedger):
    """
    Ledger for a single item supplied from a receiver node. A receiver node can have multiple
    of these ledgers, one for each item type that it supplies.
    """
    #---------------------------------------------------------------------------

    def __init__(self, owner:mmapd.MapReceiverNode, connector:mmapd.MapSupplyConnector) -> None:
        super().__init__()
        self._owner = owner
        self._item_name = connector.supplied_item_name
        self._connector = connector

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_id()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:
        assert requestor is not None, "Requestor cannot be None."

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        if request_item != self._connector.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item}' does not match the supplied item"
                f" '{self._connector.supplied_item_name}' for this ledger of receiver node"
                f" '{self._owner.get_id()}'.")

        idx, existing_request = next(
            (r for r in enumerate(self._approved_pull_requests) if r[1].request_node == requestor)
            , (-1, None)
        )

        # By design, all the requests within pull_requests are already approved, meaning the
        # suppliers are able to supply the desired amounts so any request rate of the existing
        # supply rate or lower, when requesting supplies from suppliers, will be expected to be
        # approved.

        other_requests_ipm = self._supply_rate_ipm
        if existing_request is not None:
            other_requests_ipm -= existing_request.request_ipm

        required_ipm = other_requests_ipm + request_ipm

        assert True if 0 < request_ipm else other_requests_ipm == required_ipm

        remaining_request_ipm = required_ipm

        for supplier in self._connector.get_suppliers(request_item):
            node = cast(mmapd.MapNode, supplier)
            ledger = cast(Ledger, node.ledger)
            remaining_request_ipm \
                -= ledger.request_supplies(self, request_item, remaining_request_ipm)

        self._supply_rate_ipm = required_ipm - remaining_request_ipm

        if 0 == request_ipm:
            if existing_request is not None:
                del self._approved_pull_requests[idx]
            return 0

        else:
            approved_request_ipm = self._supply_rate_ipm - other_requests_ipm

            if existing_request is not None:
                # When an approved request exists, there will be at least the capacity of the
                # existing request so approved_request_ipm will be greater than 1.
                existing_request.request_ipm = approved_request_ipm
            else:
                # When no existing request, might have insufficient capacity, in which case
                # approved_request_ipm will less than request_ipm, even zero, but never negative.
                if 0 < approved_request_ipm:
                    self._approved_pull_requests.append(
                        NodePullRequest(requestor, approved_request_ipm))

                elif approved_request_ipm < 0:
                    raise ValueError(
                        "Error in request approval amount calculation. Approved request is negative"
                        f" thus invalid. Result ({approved_request_ipm}).")

        return approved_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class ReceiverLedger(MultiItemLedger):
    #---------------------------------------------------------------------------

    def __init__(self, owner:mmapd.MapReceiverNode) -> None:
        super().__init__()
        self._owner = owner
        for connector in self._owner.supplied_items:
            ledger = ReceiverItemLedger(owner, connector)
            connector.ledger = ledger
            self._supplied_items[connector.supplied_item_name] = ledger

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_id()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:
        ledger = self._supplied_items.get(request_item)
        if ledger is None:
            raise ValueError(
                f"Requested item '{request_item}' is not supplied by receiver node"
                f" '{self._owner.get_id()}'.")
        return ledger.request_supplies(requestor, request_item, request_ipm)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class TargetLedger(Ledger):
    """
    Ledger for target nodes that represent the demand for items being produced by the factory.
    """
    #---------------------------------------------------------------------------

    def __init__(self, owner:mmapd.MapTargetNode) -> None:
        super().__init__()
        self._owner = owner
        self._target_ipm:int = 0
        self._supply_rate_ipm:int = 0
        """
        The actual rate of supply from all the suppliers attempting to provide the target rate.
        """

    #---------------------------------------------------------------------------

    def get_owner_id(self) -> str:
        return self._owner.get_global_id()

    #---------------------------------------------------------------------------

    def supply_rate_ipm(self, request_item:str|None = None) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._supply_rate_ipm = 0

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:Ledger, request_item:str, request_ipm:int) -> int:
        if self != requestor:
            raise ValueError(
                "Target nodes can only be requested by themselves.")

        if request_ipm != self._target_ipm:
            raise ValueError(
                "Target nodes can only be requested at their target rate. Requested rate: "
                f"{request_ipm}, target rate: {self._target_ipm}.")

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        if request_item != self._owner.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item}' does not match the supplied item"
                f" '{self._owner.supplied_item_name}' for this ledger of target node"
                f" '{self._owner.get_global_id()}'.")

        remaining_request_ipm = request_ipm
        for supplier in self._owner.get_suppliers(request_item):
            node = cast(mmapd.MapNode, supplier)
            ledger = cast(Ledger, node.ledger)
            remaining_request_ipm \
                -= ledger.request_supplies(self, request_item, remaining_request_ipm)

        self._supply_rate_ipm = request_ipm - remaining_request_ipm

        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def set_target(self, target_ipm:int) -> None:
        """
        Set the target rate and perform the supply chain production calculation.
        This can only be called once the network has been fully built.
        """
        self._target_ipm = target_ipm
        self.request_supplies(self, self._owner.supplied_item_name, target_ipm)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

def set_map_data_ledgers(map_data:mmapd.MapData) -> None:
    for site in map_data.sites.values():
        for resource_node in site.resource_nodes.values():
            resource_node.ledger = ResourceLedger(resource_node)
        for factory in site.factories.values():
            for crafter_node in factory.crafters.values():
                crafter_node.ledger = CrafterLedger(crafter_node)
            for single_storage_node in factory.storages.values():
                single_storage_node.ledger = SingleStorageLedger(single_storage_node)
            for dispatcher_node in factory.dispatchers.values():
                dispatcher_node.ledger = DispatcherLedger(dispatcher_node)
            for receiver_node in factory.receivers.values():
                receiver_node.ledger = ReceiverLedger(receiver_node)
            for target_node in factory.targets.values():
                target_node.ledger = TargetLedger(target_node)

#---------------------------------------------------------------------------------------------------




def spike_calc_factory_resource_usage2(
        site_id:str,
        factory_id:str,
        map_data:mmapd.MapData) -> None:

    factory = map_data.sites[site_id].factories[factory_id]

    factory_nodes:list[mmapd.MapNode] = list(factory.crafters.values())
    factory_nodes.extend(list(factory.storages.values()))
    factory_nodes.extend(list(factory.site.resource_nodes.values()))
    factory_nodes.extend(i for r in factory.receivers.values() for i in r.supplied_items)

    factory_nodes.sort(key=lambda n:n.global_id)

    for n in factory_nodes:
        id = n.global_id
        max_production_ipm = 0
        if isinstance(n, mmapd.MapProductionSupplyNode):
            max_production_ipm = n.max_production_ipm
        if isinstance(n, mmapd.MapSupplyConnector):
            id = f"{n.global_id} ({n.supplied_item_name})"
        ledger = cast(SingleItemLedger,n.ledger)
        print(f"{id}  {max_production_ipm}  {ledger.supply_rate_ipm()}")

#---------------------------------------------------------------------------------------------------

def main():
    game_data = load_game_data()
    map_data = mmapd.load_map_data(game_data)

    target_node = mmapd.MapTargetNode("test-site", "factory", "target1", "glass")
    map_data.sites["test-site"].factories["factory"].add_target(target_node)
    target_node.add_supplier(map_data.sites["test-site"].factories["factory"].storages["s-glass-1"])

    set_map_data_ledgers(map_data)

    target_node.ledger.set_target(100)

    spike_calc_factory_resource_usage2("test-site", "factory", map_data)

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------