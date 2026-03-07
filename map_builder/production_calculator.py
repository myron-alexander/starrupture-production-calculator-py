
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
        if supplier not in self._input_nodes:
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

        required_ipm = math.ceil(delivery_ipm / 60 * self.baseline_required_ipm)
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
            f"   supplies: {self.supplies}\n"\
            f"   terminal: {self._terminal}\n"\
            f"   inputs  : {[n.key for n in self.inputs]}\n"\
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
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        item_name = supplier.supplies
        suppliers = self._suppliers.setdefault(
            item_name, MapNodeRecipeSuppliers(self, item_name))
        suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def set_recipe(self, recipe:tuple[tuple[str, int], ...]) -> None:
        """
        Set the recipe for this producer node. This will ensure that every input into the recipe
        has an entry in the _suppliers mapping and that the baseline_required_ipm is set for each
        of the recipe items.
        """
        for item_name, baseline_required_ipm in recipe:
            self._suppliers \
                .setdefault(item_name, MapNodeRecipeSuppliers(self, item_name)) \
                    .baseline_required_ipm = baseline_required_ipm

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:

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

        required_ipm = min(other_requests_ipm + request_ipm, self._baseline_production_rate_ipm)

        #
        # Request the suppliers for the recipe input items.
        # When this is a revokation request, the request to suppliers should always return with
        # full approval.
        #

        assert True if 0 < request_ipm else other_requests_ipm == required_ipm

        available_inputs = []
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

        all_supplies_available = all(r[1] <= r[2] for r in available_inputs)
        if not all_supplies_available:
            availability_ratios = [(ai[0], ai[2]/ai[1]) for ai in available_inputs]
            lowest_ratio = min([ar[1] for ar in availability_ratios])
            request_ipm = math.floor(request_ipm * lowest_ratio)
            for suppliers in self._suppliers.values():
                suppliers.request_supplies_for_deliverable(request_ipm)

        self._supply_rate_ipm = request_ipm

        approved_request_ipm = request_ipm - other_requests_ipm

        assert 0 < approved_request_ipm < request_ipm

        if existing_request is not None:
            existing_request.request_ipm = approved_request_ipm
        else:
            self._approved_pull_requests.append(NodePullRequest(requestor, approved_request_ipm))

        return approved_request_ipm

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

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:

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
    def supply_rate_ipm(self) -> int:
        return self._supply_rate_ipm

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapNode) -> None:
        self._suppliers.add_supplier(supplier)

    #---------------------------------------------------------------------------

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        Since storage doesn't produce items, pass on the request to the inputs.
        """
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

        self.suppliers:MapNodeSuppliers = MapNodeSuppliers(self, item_name)
        """
        Suppliers of items into this node.
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
        self.suppliers.add_supplier(supplier)

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

        return 0

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

    def request_supplies(self, requestor:MapNode, request_ipm:int) -> int:
        """
        For now, until I implement the factory calculator, the receiver will just approve the
        request without checking with the supplier.
        """
        # TODO: Implement.

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
        for n in non_productive_node.inputs:
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
        self.required_production_ipm:int = 0
        """
        The supply rate required to match consumer demands.
        """
        self.production_capacity_ipm:int = 0
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
        item to target rate ipm. When a target production rate is set, the calculation will
        ignore the remote factory receiver pull rates attached to factory dispatchers of the item.
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

    def get_factory_target_rates(self, site_id:str, factory_id:str) -> list[tuple[str,int]]:
        key = f"{site_id};{factory_id}"
        return list(self.factory_production_target_ipm.get(key, {}).items())

    #---------------------------------------------------------------------------

    @staticmethod
    def __make_factory_ledger_key(site_id:str, factory_id:str, node_id:str):
        return make_map_node_key(node_id, site_id, factory_id)

    #---------------------------------------------------------------------------

    @staticmethod
    def __make_resource_ledger_key(site_id:str, node_id:str):
        return make_map_node_key(node_id, site_id, None)

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
        site_id:str,
        factory_id:str,
        map_data:dict[str,Any],
        ledger:NodeLedger,
        map_network:MapNetwork) -> None:
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

    terminals = map_network.get_factory_terminal_producers(site_id, factory_id)

    # NOTE: Have not implemented using dispatcher pull rates instead of factory target rates.
    #       That will be implemented later.

    # It is important that only the item producers are returned as terminals so that the distribution
    # of target rates can be calculated with the correct number of production nodes.

    if 0 < len(terminals):
        target_rates = ledger.get_factory_target_rates(site_id, factory_id)
        print(f"target_rates {target_rates}")
        for item, rate in target_rates:
            item_terminals = [t for t in terminals if item == t.supplies]
            num_item_producers = len(item_terminals)
            print(f"rate: {rate} num_item_producers: {num_item_producers}")
            if 0 < num_item_producers:
                # Rounding up to ensure that the combined producers will match or exceed the
                # required rate.
                distributed_rate = math.ceil(rate / num_item_producers)
                print(f"distributed_rate {distributed_rate}")
                for t in item_terminals:
                    ledger\
                        .get_factory_entry(t.site_id, t.factory_id, t.node_id)\
                        .required_production_ipm = distributed_rate

    print(terminals)

    terminals.sort(key=lambda n:n.node_id)

    for t in terminals:
        fe = ledger.get_factory_entry(t.site_id, t.factory_id, t.node_id)
        print(f"{t.node_id}   base: {fe.baseline_production_rate_ipm} req: {fe.required_production_ipm}  act: {fe.actual_production_rate_ipm} cap: {fe.production_capacity_ipm}")





#---------------------------------------------------------------------------------------------------

def spike_calc_factory_resource_usage(
        site_id:str,
        factory_id:str,
        map_network:MapNetwork) -> None:

    factory_nodes = map_network.get_all_factory_nodes(site_id, factory_id)

    x = Counter([ii for x in factory_nodes for ii in x.inputs if type(ii) is MapResourceNode])
    print(x)

    # Find all the resources being used.


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
        for resource_id, resource_values in site_values.get("resource_nodes", {}).items():
            item_name = resource_values["resource_item"]
            map_network.add_node(MapResourceNode(site_id, resource_id, item_name))
        for factory_id, factory_values in site_values.get("factories", {}).items():
            machines = factory_values.get("machines", {})
            for crafter_id, crafter_values in machines.get("crafters", {}).items():
                item_name = crafter_values["crafted_item"]
                map_network.add_node(MapCrafterNode(site_id, factory_id, crafter_id, item_name))
            for storage_id, storage_values in machines.get("storage", {}).items():
                item_name = storage_values["stored_item"]
                map_network.add_node(MapStorageNode(site_id, factory_id, storage_id, item_name))
            for displatcher_id, dispatcher_values in factory_values.get("dispatchers", {}).items():
                item_name = dispatcher_values["dipatched_item"]
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
                                            ["dipatched_item"]
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

    ledger = NodeLedger()
    populate_defined_production_rates(map_data, game_data, ledger)
    print(ledger.ledger)

    map_network = build_map_network(map_data)
    #print(map_network)

    print()
    print()
    print()
    xxx = map_network.get_factory_terminal_producers("wolfram 2", "stabilizer")
    print(xxx)

    print()
    print()
    print()
    xxx = map_network.get_factory_terminal_producers("starter", "inductor")
    print(xxx)

    ledger.set_factory_target_rate("starter", "inductor", "inductor", 100)

    #calculate_factory_production_and_pull_rates(
    #    "starter", "inductor", map_data, ledger, map_network)

    print()
    print()
    print()
    print()
    print()
    print()
    #spike_calc_factory_resource_usage("starter", "inductor", map_network)
    #spike_calc_factory_resource_usage("starter", "wolfram wire", map_network)
    spike_calc_factory_resource_usage("starter", "tube and applicator", map_network)

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