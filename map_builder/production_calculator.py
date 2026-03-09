
#---------------------------------------------------------------------------------------------------

__all__ = [
]

#---------------------------------------------------------------------------------------------------

import json
import math
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any

from application_data import GameData, load_game_data

#---------------------------------------------------------------------------------------------------

def make_map_node_key(id:str, site_id:str, factory_id:str|None) -> str:
    return f"{site_id};{factory_id or ""};{id}"

def make_map_node_factory_partial_key(site_id:str, factory_id:str) -> str:
    """
    Make a partial key of just the site and factory portion which can be used to get all the nodes
    of a factory from the network.
    """
    return f"{site_id};{factory_id};"

def make_map_node_site_partial_key(site_id:str) -> str:
    """
    Make a partial key of just the site portion which can be used to get all the resource nodes
    of a site from the network.
    """
    return f"{site_id};;"

#---------------------------------------------------------------------------------------------------

class MapNodeSuppliers:
    """
    Wrap an input MapNodes to allow for request calculation.
    """

    def __init__(self, owner:"MapNode", supplied_item_name:str) -> None:

        self._owner = owner
        """
        The map node that is supplied from the inputs.
        """
        self.supplies = supplied_item_name
        self._input_nodes:list["MapNode"] = []

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        """
        Clear the requests from the input nodes. This is intended to be used when recalculating
        the production rates for a factory, to clear the existing requests before recalculating and
        approving new requests.
        """
        for n in self._input_nodes:
            n.clear_requests()

    #---------------------------------------------------------------------------

    def request_supplies(self, request_ipm:int) -> int:
        """
        Request delivery of supplies from the suppliers at the rate of request_ipm.
        Passing in zero to request_ipm will revoke the request from all the suppliers.

        Returns
        -------
        int:
            The approved request rate which will be less than or equal to request_ipm.
        """

        if request_ipm < 0:
            raise ValueError("Request ipm cannot be negative.")

        remaining_request_ipm = request_ipm
        for n in self._input_nodes:
            # Iterating through all the suppliers even when the remaining is
            # reduced to zero so that those suppliers that are not longer
            # being used will have their request revoked.
            remaining_request_ipm \
                -= n.request_supplies(self._owner, remaining_request_ipm)
            assert 0 <= remaining_request_ipm

        approved_request_ipm = request_ipm - remaining_request_ipm

        return approved_request_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:"MapNode") -> None:
        if supplier.key in [n.key for n in self._input_nodes]:
            raise ValueError(
                f"Supplier {supplier.key} is already a supplier for {self._owner.key}.")
        self._input_nodes.append(supplier)

    # There isn't a means to remove the supplier as the current design assumes that the whole
    # network is rebuilt after the network structure is changed.

    #---------------------------------------------------------------------------

    @property
    def input_nodes(self) -> tuple["MapNode", ...]:
        """
        This is a property so that the membership is not accidently added or deleted. It is very
        important that the references are identical to those in _input_nodes as the reference
        id is used for comparisons.
        """
        return tuple(self._input_nodes)

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

class MapNodeRecipeSuppliers(MapNodeSuppliers):
    """
    Wrap an input MapNode that is intended to be used by a crafter for a recipe. This class
    provides the recipe elements needed for input item request values.
    """

    def __init__(self, owner: "MapNode", supplied_item_name: str) -> None:

        #
        # Initialize inherited.
        #
        super().__init__(owner, supplied_item_name)

        #
        # Initialize class specific.
        #

        self.crafted_baseline_delivery_ipm:int = 0
        """
        The amount of the crafted item that is delivered by the owner per minute as per game
        definition. This value is used to calculate the required input request rate from the
        crafted item production rate.
        """

        self.baseline_required_ipm:int = 0
        """
        The required number of items per minute that is required to craft the craftable as per
        game definition. This value is used to calculate the required input request rate from the
        crafted item production rate.
        """
        self._actually_supplied_ipm:int = 0
        """
        The amount actually supplied by the input nodes. This value is not related to
        baseline_required_ipm and will often be greater than it.
        """

    #---------------------------------------------------------------------------

    def get_recipe_ipm(self, delivery_ipm:int) -> int:
        """
        Get the required input supply rate for a given delivery rate of the crafted item.

        Parameters
        ----------
        delivery_ipm : int
            The amount of crafted items that need to be delivered by the owner per minute.
            The required supply rate for this recipe item, asked of suppliers, will be calculated
            from this value.

        Returns
        -------
        int:
            The required supply rate for this recipe item. This may be zero if the delivery_ipm is
            zero or if the baseline_required_ipm is zero.
        """

        if delivery_ipm < 0:
            raise ValueError("Delivery ipm cannot be negative.")

        required_ipm = math.ceil(
            (delivery_ipm / self.crafted_baseline_delivery_ipm) * self.baseline_required_ipm)
        return required_ipm

    #---------------------------------------------------------------------------

    def request_supplies_for_deliverable(self, delivery_ipm:int) -> tuple[int,int]:
        """
        In order for the owner to make deliveries, a certain number of supplies of this
        recipe item are necessary. Calculate the rate of supplies necessary and make the request
        of suppliers.

        Parameters
        ----------
        delivery_ipm : int
            The amount of crafted items that need to be delivered by the owner per minute.
            The request rate for the recipe item, asked of suppliers, will be calculated from
            this value.

        Returns
        -------
        tuple[int,int]:
            First value is the requested supply rate for this recipe item.
            Second value is the approved supply rate for this recipe item. This may be zero if the
            suppliers have no capacity.
        """
        supply_request_ipm = self.get_recipe_ipm(delivery_ipm)
        self._actually_supplied_ipm = self.request_supplies(supply_request_ipm)
        return supply_request_ipm, self._actually_supplied_ipm

    #---------------------------------------------------------------------------

    @property
    def actually_supplied_ipm(self) -> int:
        """
        The amount actually supplied by the input nodes. This value is not related to
        baseline_required_ipm and will often be greater than it.
        """
        return self._actually_supplied_ipm

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

class NodePullRequest:
    """
    """
    def __init__(self, request_node:"MapNode", request_ipm:int = 0) -> None:
        self.request_node = request_node
        self.request_ipm:int = request_ipm
        # Since I have removed support for nodes to supply more than one item type, the pull
        # request doesn't need to specify the pulled item.

#---------------------------------------------------------------------------------------------------

class MapNode(ABC):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, id:str, site_id:str, factory_id:str|None) -> None:
        self.key:str = make_map_node_key(id, site_id, factory_id)
        self.site_id = site_id
        self.factory_id = factory_id or ""
        self.node_id = id
        # Supplies was an array to support future addition of multi-storage but I have decided
        # to simplify and handle multi-storage separately.
        self.supplies = ""
        """
        List of nodes that have pull requests as well as the amount requested.
        """
        # Presume not part of any input until otherwise known.
        self._terminal = True

    #---------------------------------------------------------------------------

    @property
    @abstractmethod
    def baseline_production_rate_ipm(self) -> int:
        pass

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    @abstractmethod
    def baseline_production_rate_ipm(self, value:int) -> None:
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def add_supplier(self, supplier:"MapNode") -> None:
        """
        Add the provider of item to this node as an item supplier.
        """
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def get_suppliers(self) -> tuple["MapNode", ...]:
        """
        Get this node's suppliers of items. This is intended to be used for traversing the
        tree and is not intended to be used for request calculation as the suppliers may be
        wrapped in a MapNodeSuppliers or MapNodeRecipeSuppliers which should be used for request
        calculation instead.
        """
        pass

    #---------------------------------------------------------------------------

    @property
    @abstractmethod
    def supply_rate_ipm(self) -> int:
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def request_supplies(self, requestor:"MapNode", request_ipm:int) -> int:
        """
        Ask for an amount of items per minute. If the producer has sufficient production capacity,
        the request will be added to the list of requestors and request_ipm is returned. If there
        is no capacity, the request is not added to the list and zero ipm is returned. If there
        is insufficient capacity, the request_ipm will be reduced to available capacity, added
        to the list of requestors and returned.

        If the request_ipm is zero, and the requestor has an existing approved request, remove the
        existing request.

        Returns
        -------
        int:
            The approved request rate.
        """
        pass

    #---------------------------------------------------------------------------

    @abstractmethod
    def clear_requests(self) -> None:
        """
        Clear all the requests from the requestors. This is intended to be used when recalculating
        the production rates for a factory, to clear the existing requests before recalculating
        and approving new requests.
        """
        pass

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
            f"   key                         : {self.key}\n"\
            f"   supplies                    : {self.supplies}\n"\
            f"   terminal                    : {self._terminal}\n"\
            f"   boundary                    : {self.is_boundary}\n"\
            f"   baseline production rate ipm: {self.baseline_production_rate_ipm}\n"\
            f"   supply rate ipm             : {self.supply_rate_ipm}\n"\
            f"   inputs                      : {[n.key for n in self.get_suppliers()]}\n"\
             "]\n"

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapProducerNode(MapNode):

    def __init__(self, id: str, site_id: str, factory_id: str|None) -> None:

        #
        # Initialize inherited.
        #

        super().__init__(id, site_id, factory_id)

        #
        # Initialize class specific.
        #

        self._baseline_production_rate_ipm:int = 0
        """
        Production rate as per game definition.
        """
        self._approved_pull_requests:list[NodePullRequest] = []
        """
        The list of requestors that are consuming the item produced, and the amounts they are
        approved to consume.
        """
        self._suppliers:dict[str, MapNodeRecipeSuppliers] = {}
        """
        Suppliers of items into this node.
        """
        self._supply_rate_ipm:int = 0
        """
        Same as sum([r.request_ipm for r in self._approved_pull_requests]).
        Will always be less than or equal to baseline_production_rate_ipm.
        """

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        return self._baseline_production_rate_ipm

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        self._baseline_production_rate_ipm = value

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        item_name = supplier.supplies
        suppliers = self._suppliers.setdefault(
            item_name, MapNodeRecipeSuppliers(self, item_name))
        suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        suppliers = []
        for s in self._suppliers.values():
            suppliers.extend(s.input_nodes)
        return tuple(suppliers)

    #---------------------------------------------------------------------------

    def set_recipe(self, recipe:tuple[tuple[str, int, int], ...]) -> None:
        """
        Set the recipe for this producer node. This will ensure that every input into the recipe
        has an entry in the _suppliers mapping and that the baseline_required_ipm is set for each
        of the recipe items.

        Parameters
        ----------
        recipe : tuple[tuple[str, int, int], ...]
            List of items in the recipe. Each item is specified as:
              1. The input item name as per game definition
              2. The amount required by the game definition
              3. The cacluated required amount per minute
        """
        for item_name, _, baseline_required_ipm in recipe:
            #print(f"{self.key}   {item_name}   {baseline_required_ipm}")
            supplier = self._suppliers.setdefault(
                item_name, MapNodeRecipeSuppliers(self, item_name))
            assert 0 < self._baseline_production_rate_ipm
            supplier.crafted_baseline_delivery_ipm = self._baseline_production_rate_ipm
            supplier.baseline_required_ipm = baseline_required_ipm

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests.clear()
        self._supply_rate_ipm = 0
        for suppliers in self._suppliers.values():
            suppliers.clear_requests()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:

        assert requestor is not None, "Requestor cannot be None."

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

        assert other_requests_ipm <= self._baseline_production_rate_ipm

        if other_requests_ipm == self._baseline_production_rate_ipm:
            # No capacity for any more requests, so the request will be rejected.
            assert existing_request is None
            return 0

        required_ipm = min(other_requests_ipm + request_ipm, self._baseline_production_rate_ipm)

        #
        # Request the suppliers for the recipe input items.
        # When this is a revokation request, the request to suppliers should always return with
        # full approval.
        #

        assert True if 0 < request_ipm else other_requests_ipm == required_ipm

        available_inputs:list[tuple[str,int,int]] = []
        for recipe_item, suppliers in self._suppliers.items():
            supply_request_ipm, supply_approved_ipm \
                = suppliers.request_supplies_for_deliverable(required_ipm)
            available_inputs.append((recipe_item, supply_request_ipm, supply_approved_ipm))

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
            # No supply available, undo requests to suppliers.
            for suppliers in self._suppliers.values():
                suppliers.request_supplies_for_deliverable(self._supply_rate_ipm)
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
            for suppliers in self._suppliers.values():
                suppliers.request_supplies_for_deliverable(adjusted_required_ipm)

        self._supply_rate_ipm = adjusted_required_ipm

        approved_request_ipm = self._supply_rate_ipm - other_requests_ipm

        assert 0 < approved_request_ipm <= adjusted_required_ipm

        if existing_request is not None:
            existing_request.request_ipm = approved_request_ipm
        else:
            self._approved_pull_requests.append(NodePullRequest(requestor, approved_request_ipm))

        return approved_request_ipm

    #---------------------------------------------------------------------------

    def __repr__(self) -> str:
        requestors = ""
        for pr in self._approved_pull_requests:
            requestors \
                += f"                                 {pr.request_node.key} : {pr.request_ipm}\n"

        return \
            f"{type(self).__name__} [\n"\
            f"   key                         : {self.key}\n"\
            f"   supplies                    : {self.supplies}\n"\
            f"   terminal                    : {self._terminal}\n"\
            f"   boundary                    : {self.is_boundary}\n"\
            f"   baseline production rate ipm: {self.baseline_production_rate_ipm}\n"\
            f"   supply rate ipm             : {self.supply_rate_ipm}\n"\
            f"   pull requests               :\n{requestors}"\
            f"   inputs                      : {[n.key for n in self.get_suppliers()]}\n"\
             "]\n"

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapResourceNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, resource_id:str, item_name:str) -> None:

        #
        # Initialize inherited.
        #

        super().__init__(resource_id, site_id, None)
        # A resource cannot be a terminal, only dispatcher, storage and crafter.
        # This is because a resource that is not an input to a node within the factory isn't
        # actually bringing items into the production chain.
        self._terminal = False
        self.supplies = item_name

        #
        # Initialize class specific.
        #

        self._baseline_production_rate_ipm:int = 0
        """
        Production rate as per game definition.
        """
        self._approved_pull_requests:list[NodePullRequest] = []
        """
        The list of requestors that are consuming the item produced, and the amounts they are
        approved to consume.
        """
        self._supply_rate_ipm:int = 0
        """
        Same as sum([r.request_ipm for r in self._approved_pull_requests])
        """

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        return self._baseline_production_rate_ipm

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        self._baseline_production_rate_ipm = value

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return False

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        raise ValueError(
            "Resource nodes cannot have suppliers as they are primary sources of items.")

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        return tuple()

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests.clear()
        self._supply_rate_ipm = 0

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:

        assert requestor is not None, "Requestor cannot be None."

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
            capacity = self._baseline_production_rate_ipm - self._supply_rate_ipm - request_ipm
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

class MapCrafterNode(MapProducerNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, crafter_id:str, item_name:str) -> None:
        super().__init__(crafter_id, site_id, factory_id)
        self.supplies = item_name

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

    def __init__(self, site_id:str, factory_id:str, storage_id:str, item_name:str) -> None:

        #
        # Initialize inherited.
        #

        super().__init__(storage_id, site_id, factory_id)
        self.supplies = item_name

        #
        # Initialize class specific.
        #

        self._suppliers:MapNodeSuppliers = MapNodeSuppliers(self, item_name)
        """
        Suppliers of items into this node.
        """
        self._approved_pull_requests:list[NodePullRequest] = []
        """
        The list of requestors that are consuming the item, and the amounts they are
        approved to consume.
        """
        self._supply_rate_ipm:int = 0
        """
        Same as sum([r.request_ipm for r in self._approved_pull_requests])
        """

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return False

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        """
        Storage doesn't produce items, so it doesn't have a baseline production rate.
        """
        return 0

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        return

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        self._suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        return self._suppliers.input_nodes

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests.clear()
        self._supply_rate_ipm = 0
        self._suppliers.clear_requests()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        Since storage doesn't produce items, pass on the request to the inputs.
        """

        assert requestor is not None, "Requestor cannot be None."

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

        self._supply_rate_ipm = self._suppliers.request_supplies(required_ipm)

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

class MapDispatcherNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, dispatcher_id:str, item_name:str) -> None:

        #
        # Initialize inherited.
        #

        super().__init__(dispatcher_id, site_id, factory_id)
        self.supplies = item_name

        #
        # Initialize class specific.
        #

        self._suppliers:MapNodeSuppliers = MapNodeSuppliers(self, item_name)
        """
        Suppliers of items into this node.
        """
        self._approved_pull_request:NodePullRequest|None = None
        """
        The receiver consuming the item and the amount it is approved to consume.
        """
        self._supply_rate_ipm:int = 0
        """
        Same as sum([r.request_ipm for r in self._approved_pull_requests])
        """

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return True

    #---------------------------------------------------------------------------

    def set_not_terminal(self) -> None:
        # A dispatcher is always terminal within the factory.
        return

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        """
        A dispatcher doesn't have a baseline production rate as it doesn't produce anything
        and acts purely as a bridge between factories.
        """
        return 0

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        """
        A dispatcher doesn't have a baseline production rate as it doesn't produce anything
        and acts purely as a bridge between factories.
        """
        return

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        """
        Add the provider of item to this node as an item supplier.
        """
        self._suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        return self._suppliers.input_nodes

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests = None
        self._supply_rate_ipm = 0
        self._suppliers.clear_requests()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        TODO: I'm planning on allowing priority targets for a factory. This means that when a
        factory has insufficient capacity to meet the demand of all the dispatchers, it will
        prioritise the dispatchers with priority targets over those without. Not just dispatchers,
        but any terminal nodes in the factory that are intended to be outputs of the production
        chain like orbital launchers, and specific designated storage. The only way this works
        is if the factory calculation are done for each factory separately. Thus the calculation
        process may not cross a factory boundary.

        Thus when a receiver requests supplies, the dispatcher can only provide from the known
        available capacity without cascading the request to it's suppliers.

        I'm thinking of allowing for a queued command mechanism where instead of cascading the
        request, the receiver can send a command to the factory and request it to recalculate
        the pull rates based on the updated demand from the consumers linked to the receiver.
        By doing this, we can still perform demand based capacity allocation which will trigger
        a factory recalculation if the demand increases or decreases. A recalculation for a
        factory would not be necessary if the demand exceeds the total production capability of
        the factory.
        """

        assert requestor is not None, "Requestor cannot be None."

        existing_request = self._approved_pull_request

        if existing_request is not None:
            if requestor != existing_request.request_node:
                raise ValueError(
                    "Dispatcher nodes can only have one requestor, which is the corresponding"
                    " receiver. Existing requestor: "
                    f"{existing_request.request_node.key}, new requestor: {requestor.key}.")

        required_ipm = request_ipm

        self._supply_rate_ipm = self._suppliers.request_supplies(required_ipm)

        if 0 == request_ipm:
            self._approved_pull_request = None
            return 0
        else:
            if existing_request is not None:
                existing_request.request_ipm = self._supply_rate_ipm
            else:
                self._approved_pull_request = NodePullRequest(requestor, self._supply_rate_ipm)

        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapReceiverNode(MapNode):
    """
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, receiver_id:str, item_name:str) -> None:
        super().__init__(receiver_id, site_id, factory_id)
        # A receiver cannot be a terminal, only dispatcher, storage and crafter.
        # This is because a receiver that is not an input to a node within the factory isn't
        # actually bringing items into the production chain.
        self._terminal = False
        self.supplies = item_name

        self._supplier:MapNode|None = None

        self._approved_pull_requests:list[NodePullRequest] = []
        """
        The list of requestors that are consuming the item produced, and the amounts they are
        approved to consume.
        """
        self._supply_rate_ipm:int = 0
        """
        Same as sum([r.request_ipm for r in self._approved_pull_requests])
        """

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return True

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        return 0

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        return

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        """
        Add the provider of item to this node as an item supplier.
        """
        if self._supplier is not None and self._supplier != supplier:
            raise ValueError(
                "Receiver nodes can only have one supplier. Existing supplier: "
                f"{self._supplier.key}, new supplier: {supplier.key}.")
        self._supplier = supplier

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        if self._supplier is not None:
            return (self._supplier,)
        else:
            return tuple()

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._approved_pull_requests.clear()
        self._supply_rate_ipm = 0

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        For now, until I implement the factory calculator, the receiver will just approve the
        request without checking with the supplier.
        """
        # TODO: Implement.

        assert requestor is not None, "Requestor cannot be None."

        idx, existing_request = next(
            (r for r in enumerate(self._approved_pull_requests) if r[1].request_node == requestor)
            , (-1, None)
        )

        if 0 == request_ipm:
            if existing_request is not None:
                del self._approved_pull_requests[idx]
        else:
            if existing_request is not None:
                existing_request.request_ipm = request_ipm
            else:
                self._approved_pull_requests.append(NodePullRequest(requestor, request_ipm))

        self._supply_rate_ipm = sum([r.request_ipm for r in self._approved_pull_requests])

        return request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapTargetNode(MapNode):
    """
    A target node represents a desired output from the factory. It is not an actual node in the
    factory but is used to represent the demand for an item that is being produced by the factory.
    """

    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str, target_id:str, item_name:str) -> None:

        #
        # Initialize inherited.
        #

        super().__init__(target_id, site_id, factory_id)
        self.supplies = item_name
        self._terminal = True

        #
        # Initialize class specific.
        #

        self._target_ipm:int = 0

        self._suppliers:MapNodeSuppliers = MapNodeSuppliers(self, item_name)
        """
        Suppliers of items into this node.
        """
        self._supply_rate_ipm:int = 0
        """
        The actual rate of supply from all the suppliers attempting to provide the target rate.
        """

    #---------------------------------------------------------------------------

    @property
    def is_boundary(self) -> bool:
        return True

    #---------------------------------------------------------------------------

    def set_not_terminal(self) -> None:
        # A target is always terminal within the factory.
        return

    #---------------------------------------------------------------------------

    @property
    def baseline_production_rate_ipm(self) -> int:
        """
        The target rate for this target node.
        """
        return self._target_ipm

    #---------------------------------------------------------------------------

    @baseline_production_rate_ipm.setter
    def baseline_production_rate_ipm(self, value:int) -> None:
        """
        Set the target rate for this target node.
        """
        self._target_ipm = value
        return

    #---------------------------------------------------------------------------

    @property
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        """
        Add the provider of item to this node as an item supplier.
        """
        self._suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple[MapNode, ...]:
        return self._suppliers.input_nodes

    #---------------------------------------------------------------------------

    def clear_requests(self) -> None:
        self._supply_rate_ipm = 0
        self._suppliers.clear_requests()

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        """

        if self != requestor:
            raise ValueError(
                "Target nodes can only be requested by themselves.")

        if request_ipm != self._target_ipm:
            raise ValueError(
                "Target nodes can only be requested at their target rate. Requested rate: "
                f"{request_ipm}, target rate: {self._target_ipm}.")

        self._supply_rate_ipm = self._suppliers.request_supplies(request_ipm)

        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def set_target(self, target_ipm:int) -> None:
        """
        Set the target rate and perform the supply chain production calculation.
        This can only be called once the network has been fully built.
        """
        self._target_ipm = target_ipm
        self.request_supplies(self, target_ipm)

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

    def get_all_factory_nodes(self, site_id:str, factory_id:str) -> list[MapNode]:
        pkey = make_map_node_factory_partial_key(site_id, factory_id)
        factory_nodes = [
            n for n in self.map_nodes.values() if n.key.startswith(pkey)
        ]
        return factory_nodes

    #---------------------------------------------------------------------------

    def get_all_resource_nodes(self, site_id:str) -> list[MapNode]:
        pkey = make_map_node_site_partial_key(site_id)
        resource_nodes = [
            n for n in self.map_nodes.values() if n.key.startswith(pkey)
        ]
        return resource_nodes

    #---------------------------------------------------------------------------

    def get_factory_terminals(self, site_id:str, factory_id:str) -> list[MapNode]:
        """
        Get all the nodes within the factory that are not inputs into the production chain
        within the factory.
        """
        pkey = make_map_node_factory_partial_key(site_id, factory_id)
        terminals = [
            n for n in self.map_nodes.values() if n.key.startswith(pkey) and n.is_terminal
        ]
        return terminals

    #---------------------------------------------------------------------------

    def __walk_inputs_get_production_terminals(self, non_productive_node:MapStorageNode|MapDispatcherNode) -> set[MapNode]:
        # Using set as children in the tree may be referenced by multiple parents.
        non_storage = set()
        for n in non_productive_node.get_suppliers():
            if type(n) in (MapStorageNode, MapDispatcherNode):
                non_storage |= self.__walk_inputs_get_production_terminals(n) # type: ignore
            else:
                non_storage.add(n)
        return non_storage

    #---------------------------------------------------------------------------

    def get_factory_terminal_producers(self, site_id:str, factory_id:str) -> list[MapNode]:
        """
        Get the terminal nodes in the production chain for this factory that produce items.
        This will return the list of nodes that are contributing to the production chain so it
        excludes the storage and dispatcher nodes. Instead, the first linked non-storage,
        non-dispatcher feeds are included. When a storage/dispatcher is a terminal supplied by a
        receiver or resource, then the receiver/resource will be included in the terminal list
        since it is bringing items into the factory.
        """
        pkey = make_map_node_factory_partial_key(site_id, factory_id)
        terminals = [
            n for n in self.map_nodes.values() if n.key.startswith(pkey) and n.is_terminal
        ]
        # Neither storage nor dispatcher nodes produce items so defer to the first input
        # that are producers.
        non_storage = set()
        for n in terminals:
            if type(n) in (MapStorageNode, MapDispatcherNode):
                non_storage |= self.__walk_inputs_get_production_terminals(n) # type: ignore
            else:
                non_storage.add(n)
        return list(non_storage)

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

def spike_calc_factory_resource_usage(
        site_id:str,
        factory_id:str,
        map_network:MapNetwork) -> None:

    factory_nodes = map_network.get_all_factory_nodes(site_id, factory_id)

    factory_nodes.extend(map_network.get_all_resource_nodes(site_id))

    #x = Counter([ii for x in factory_nodes for ii in x.get_suppliers() if type(ii) is MapResourceNode])
    #print(x)

    for n in factory_nodes:
        print(n)

    # Find all the resources being used.

def spike_calc_factory_resource_usage2(
        site_id:str,
        factory_id:str,
        map_network:MapNetwork) -> None:

    factory_nodes = map_network.get_all_factory_nodes(site_id, factory_id)

    factory_nodes.extend(map_network.get_all_resource_nodes(site_id))

    #x = Counter([ii for x in factory_nodes for ii in x.get_suppliers() if type(ii) is MapResourceNode])
    #print(x)

    factory_nodes.sort(key=lambda n:n.key)

    for n in factory_nodes:
        print(f"{n.node_id}  {n.baseline_production_rate_ipm}  {n.supply_rate_ipm}")

    # Find all the resources being used.


#---------------------------------------------------------------------------------------------------

def build_map_network(map_data:dict[str,Any], game_data:GameData) -> MapNetwork:

    map_network = MapNetwork()

    #
    # Create the nodes in the network.
    #

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
            node = MapResourceNode(site_id, resource_id, item_name)
            node.baseline_production_rate_ipm = definition.items_per_minute
            map_network.add_node(node)

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
                recipe = game_data.item_recipes.get(item_name, None)
                if recipe is None:
                    raise ValueError(
                        f"Game recipe definition for item ({item_name}) of node"
                        f" ({site_id}, {factory_id}, {crafter_id}) not found.")
                node = MapCrafterNode(site_id, factory_id, crafter_id, item_name)
                node.baseline_production_rate_ipm = definition.items_per_minute
                node.set_recipe(tuple(recipe))
                map_network.add_node(node)

            for storage_id, storage_values in machines.get("storage", {}).items():
                item_name = storage_values["stored_item"]
                map_network.add_node(MapStorageNode(site_id, factory_id, storage_id, item_name))

            for displatcher_id, dispatcher_values in factory_values.get("dispatchers", {}).items():
                item_name = dispatcher_values["dispatched_item"]
                map_network.add_node(
                    MapDispatcherNode(site_id, factory_id, displatcher_id, item_name))

            for receiver_id, receiver_values in factory_values.get("receivers", {}).items():
                # A receiver will always reference an existing dispatcher.
                other_site_id = receiver_values["site_id"]
                other_factory_id = receiver_values["factory_id"]
                other_dispatcher_id = receiver_values["dispatcher_id"]
                item_name = \
                    map_data\
                        [other_site_id]\
                            ["factories"]\
                                [other_factory_id]\
                                    ["dispatchers"]\
                                        [other_dispatcher_id]\
                                            ["dispatched_item"]
                map_network.add_node(MapReceiverNode(site_id, factory_id, receiver_id, item_name))

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
                        crafter_node.add_supplier(
                            get_input_node(site_id, factory_id, input_id, resource_ids))

            for storage_id, storage_values in machines.get("storage", {}).items():
                storage_node = map_network.get_factory_node(site_id, factory_id, storage_id)
                for ii in storage_values["inputs"]:
                    for input_id in ii["from_ids"]:
                        storage_node.add_supplier(
                            get_input_node(site_id, factory_id, input_id, resource_ids))

            for displatcher_id, dispatcher_values in factory_values.get("dispatchers", {}).items():
                dispatcher_node = map_network.get_factory_node(site_id, factory_id, displatcher_id)
                for input_id in dispatcher_values["from_ids"]:
                    dispatcher_node.add_supplier(
                        get_input_node(site_id, factory_id, input_id, resource_ids))

            for receiver_id, receiver_values in factory_values.get("receivers", {}).items():
                receiver_node = map_network.get_factory_node(site_id, factory_id, receiver_id)
                other_site_id = receiver_values["site_id"]
                other_factory_id = receiver_values["factory_id"]
                other_dispatcher_id = receiver_values["dispatcher_id"]
                receiver_node.add_supplier(
                    get_input_node(
                        other_site_id, other_factory_id, other_dispatcher_id, resource_ids))

    return map_network


#---------------------------------------------------------------------------------------------------

def main():
    game_data = load_game_data()

    with open('pins_data.json', 'r', encoding='utf-8') as f:
        map_data = json.load(f)

    map_network = build_map_network(map_data, game_data)
    #print(map_network)

    #print()
    #print()
    #print()
    #xxx = map_network.get_factory_terminal_producers("wolfram 2", "stabilizer")
    #print(xxx)

    #print()
    #print()
    #print()
    #xxx = map_network.get_factory_terminal_producers("starter", "inductor")
    #print(xxx)

    #target1_node = MapTargetNode("starter", "tube and applicator", "target1", "tube")
    #supplier_node = map_network.get_factory_node("starter", "tube and applicator", "d-tube-1")
    #target1_node.add_supplier(supplier_node)
    #map_network.add_node(target1_node)

    #target2_node = MapTargetNode("starter", "tube and applicator", "target2", "applicator")
    #supplier_node = map_network.get_factory_node("starter", "tube and applicator", "s-applicator-1")
    #target2_node.add_supplier(supplier_node)
    #map_network.add_node(target2_node)



    #target1_node.set_target(1000)
    #target2_node.set_target(1000)

    print()
    print()
    print()
    print()
    print()
    print()
    #spike_calc_factory_resource_usage("starter", "inductor", map_network)
    #spike_calc_factory_resource_usage("starter", "wolfram wire", map_network)
    #spike_calc_factory_resource_usage("starter", "tube and applicator", map_network)


    target1_node = MapTargetNode("test-site", "factory", "target1", "glass")
    target1_node.add_supplier(
        map_network.get_factory_node("test-site", "factory", "s-glass-1")
    )

    target1_node.set_target(1000)
    spike_calc_factory_resource_usage2("test-site", "factory", map_network)

    cp = map_network.get_factory_node("test-site", "factory", "calcium-powder-1")
    print(cp)

    #key = make_map_node_key("stabilizer-5", "wolfram 2", "stabilizer")
    #node = map_network.map_nodes[key]
    #print(node)

    #supplied_items = set([s for n in node.inputs for s in n.supplies])
    #xxx = [(s, [n.key for n in node.inputs if s in n.supplies]) for s in supplied_items]
    #print(xxx)


#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------