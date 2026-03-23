
#---------------------------------------------------------------------------------------------------

__all__ = [
    'MapNode',
    'MapSite',
    'MapFactory',
    'MapSiteNode',
    'MapFactoryNode',
    'MapSingleSupplyNode',
    'MapSupplyConnector',
    'MapMultiSupplyNode',
    'MapProductionSupplyNode',
    'MapResourceNode',
    'RecipeItem',
    'MapCrafterNode',
    'MapSingleStorageNode',
    'MapDispatcherNode',
    'MapReceiverNode',
    'MapData',
    'load_map_data_dict_from_file',
    'load_map_data',
]

#---------------------------------------------------------------------------------------------------

debug_mode = False

#---------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
import json
import math
from typing import Any, cast
from application_data import GameData, load_game_data

#---------------------------------------------------------------------------------------------------

class MapNode(ABC):

    #--------------------------------------------------------------------------

    def __init__(self, global_node_id:str) -> None:
        self.global_id = global_node_id
        self.ledger:Any = None
        self.graph:Any = None
        # A node is assumed to be terminal until it is added as a supplier to another node.
        self._is_terminal = True
        self._uses_receiver = False

    #--------------------------------------------------------------------------

    def __eq__(self, value: object) -> bool:
        if isinstance(value, MapNode):
            return self.global_id == value.global_id
        return False

    #--------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self.global_id)

    #--------------------------------------------------------------------------

    def get_global_id(self) -> str:
        """
        Get the ID of this node this is globally unique.
        """
        return self.global_id

    #--------------------------------------------------------------------------

    @property
    def is_terminal(self) -> bool:
        """
        Get whether this node is a terminal node. Terminal nodes are nodes that are not inputs to
        any other nodes in the factory. This is used for determining which nodes to start from when
        calculating production.
        """
        return self._is_terminal

    #--------------------------------------------------------------------------

    def flag_not_terminal(self) -> None:
        """
        When this node is added as a supplier to another node, it is no longer a terminal node.
        """
        self._is_terminal = False

    #--------------------------------------------------------------------------

    @property
    def uses_receiver(self) -> bool:
        """
        Get whether this node uses a receiver. This is used when calculating max available
        capacity.
        """
        return self._uses_receiver

    #--------------------------------------------------------------------------

    def flag_uses_receiver(self, uses_receiver:bool) -> None:
        """
        Sets the node's uses_receiver property. If this property is already true, it remains true
        regardless of parameter value.
        """
        self._uses_receiver |= uses_receiver

    #--------------------------------------------------------------------------

    @abstractmethod
    def get_node_id(self) -> str:
        """
        Get the ID of this node that is locally unique.
        """
        pass

    #--------------------------------------------------------------------------


    @staticmethod
    def id_for_site(site_id:str) -> str:
        return MapNode._create_id(site_id, None, None)

    @staticmethod
    def id_for_site_node(site_id:str, node_id:str) -> str:
        return MapNode._create_id(site_id, None, node_id)

    @staticmethod
    def id_for_factory(site_id:str, factory_id:str) -> str:
        return MapNode._create_id(site_id, factory_id, None)

    @staticmethod
    def id_for_factory_node(site_id:str, factory_id:str, node_id:str) -> str:
        return MapNode._create_id(site_id, factory_id, node_id)

    @staticmethod
    def _create_id(site_id:str, factory_id:str|None, node_id:str|None = None) -> str:
        return f"{site_id} ┇ {factory_id or ""} ┇ {node_id or ""}"

#---------------------------------------------------------------------------------------------------

class MapSite(MapNode):
    """
    A site on the map. A site contains resource nodes and factories.
    """
    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, x:int, y:int, teleporter:str, description:str) -> None:
        super().__init__(MapNode.id_for_site(site_id))
        self.site_id = site_id
        self.x = x
        self.y = y
        self.teleporter = teleporter
        self.description = description
        self.resource_nodes:dict[str,MapResourceNode] = {}
        self.factories:dict[str,MapFactory] = {}

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.site_id

    #---------------------------------------------------------------------------

    def add_resource_node(self, resource_node:"MapResourceNode") -> None:
        assert resource_node.resource_id not in self.resource_nodes, \
            f"Resource node with ID '{resource_node.resource_id}' already exists in site '{self.site_id}'"
        self.resource_nodes[resource_node.resource_id] = resource_node

    #---------------------------------------------------------------------------

    def add_factory(self, factory:"MapFactory") -> None:
        assert factory.factory_id not in self.factories, \
            f"Factory with ID '{factory.factory_id}' already exists in site '{self.site_id}'"
        self.factories[factory.factory_id] = factory

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapFactory(MapNode):
    """
    A factory on the map. A factory contains crafters, storages, dispatchers, receivers, and
    targets.
    """
    #---------------------------------------------------------------------------

    def __init__(self, site:MapSite, factory_id:str) -> None:
        super().__init__(MapNode.id_for_factory(site.site_id, factory_id))
        self.site = site
        self.factory_id = factory_id
        self.crafters:dict[str,MapCrafterNode] = {}
        self.storages:dict[str,MapSingleStorageNode] = {}
        self.dispatchers:dict[str,MapDispatcherNode] = {}
        self.receivers:dict[str,MapReceiverNode] = {}
        self.targets:dict[str,MapTargetNode] = {}

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.factory_id

    #---------------------------------------------------------------------------

    @property
    def is_empty(self) -> bool:
        # Targets are not considered as part of the production chain thus a factory with only
        # targets is still considered empty.
        return not (   self.crafters
                    or self.storages
                    or self.dispatchers
                    or self.receivers
                   )

    #---------------------------------------------------------------------------

    def get_terminal_nodes(self) -> tuple[MapNode, ...]:
        """
        Get the terminal nodes of this factory. Terminal nodes are nodes that are not inputs
        to any other nodes in the factory.
        """
        # Build list of components that are inputs.
        is_input = set()
        for v in self.dispatchers.values():
            is_input |= set(v.get_all_supplier_node_ids())
        for v in self.crafters.values():
            is_input |= set(v.get_all_supplier_node_ids())
        for v in self.storages.values():
            is_input |= set(v.get_all_supplier_node_ids())

        # Dispatchers are always terminal within the factory.
        terminals = [v for v in self.dispatchers.values()]
        terminals += [v for v in self.crafters.values() if v.get_node_id() not in is_input]
        terminals += [v for v in self.storages.values() if v.get_node_id() not in is_input]

        return tuple(terminals)

    #---------------------------------------------------------------------------

    def add_crafter(self, crafter:"MapCrafterNode") -> None:
        assert crafter.crafter_id not in self.crafters, \
            f"Crafter with ID '{crafter.crafter_id}' already exists in factory '{self.factory_id}'"
        self.crafters[crafter.crafter_id] = crafter

    #---------------------------------------------------------------------------

    def add_storage(self, storage:"MapSingleStorageNode") -> None:
        assert storage.storage_id not in self.storages, \
            f"Storage with ID '{storage.storage_id}' already exists in factory '{self.factory_id}'"
        self.storages[storage.storage_id] = storage

    #---------------------------------------------------------------------------

    def add_dispatcher(self, dispatcher:"MapDispatcherNode") -> None:
        assert dispatcher.dispatcher_id not in self.dispatchers, \
            f"Dispatcher with ID '{dispatcher.dispatcher_id}' already exists in factory '{self.factory_id}'"
        self.dispatchers[dispatcher.dispatcher_id] = dispatcher

    #---------------------------------------------------------------------------

    def add_receiver(self, receiver:"MapReceiverNode") -> None:
        assert receiver.receiver_id not in self.receivers, \
            f"Receiver with ID '{receiver.receiver_id}' already exists in factory '{self.factory_id}'"
        self.receivers[receiver.receiver_id] = receiver

    #---------------------------------------------------------------------------

    def add_target(self, target:"MapTargetNode") -> None:
        assert target.target_id not in self.targets, \
            f"Target with ID '{target.target_id}' already exists in factory '{self.factory_id}'"
        self.targets[target.target_id] = target

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapSiteNode:
    """
    A node that is part of a site. This is used as a base class for nodes that are part of a site
    but are not part of a factory, such as resource nodes.
    """
    #---------------------------------------------------------------------------

    def __init__(self, site_id:str) -> None:
        self.site_id = site_id
        self.site:MapSite|None = None

    #---------------------------------------------------------------------------

    def set_site(self, site:MapSite) -> None:
        assert site.site_id == self.site_id, \
            f"Site ID '{site.site_id}' does not match expected site ID '{self.site_id}'"
        self.site = site

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapFactoryNode(MapSiteNode):
    """
    A node that is part of a factory. This is used as a base class for nodes that are part of a
    factory, such as crafters, storages, dispatchers, receivers, and targets.
    """
    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str) -> None:
        super().__init__(site_id)
        self.factory_id = factory_id
        self.factory:MapFactory|None = None

    #---------------------------------------------------------------------------

    def set_factory(self, factory:MapFactory) -> None:
        assert factory.factory_id == self.factory_id, \
            f"Factory ID '{factory.factory_id}' does not match expected factory ID '{self.factory_id}'"
        self.factory = factory
        self.set_site(factory.site)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapConsumerNode(MapNode):
    """
    A node that consumes items from suppliers.
    """

    @abstractmethod
    def get_max_recipe_item_request_ipm(
            self, request_item_name:str) -> list[tuple["MapConsumerNode", int]]:
        """
        Used by a supplier to get this consumer's max request rate, as per recipe, for the supplied
        item. This gets complicated for nodes that don't work to a recipe/defined rate so the
        request has to be passed on up the chain to a node that has a defined rate (eg crafter or
        target).

        Parameters
        ----------
        request_item_name : str
            The name of the item being requested. This is used to determine which recipe item is
            being requested when the consumer has a recipe with multiple items.

        Returns
        -------
        list[tuple[MapConsumerNode, int]]
            A list of consumers and their requested IPM for the requested item. The list is
            intended for pass-through nodes to return the requesting consumers so that the
            total request IPM is calculated from the source values and also only once per consumer.
        """

    @abstractmethod
    def set_max_available_rate_ipm(
            self,
            supplier:"MapSingleSupplyNode",
            request_item_name:str,
            available_rate_ipm:int) -> None:
        """
        Used by the supplier to inform the consumer of the max rate that it can supply the
        requested item.

        Parameters
        ----------
        supplier : MapSingleSupplyNode
            The supplier that is providing the available rate information. This is used to determine
            which supplier is providing the available rate information when the consumer has
            multiple suppliers of the same item.
        request_item_name : str
            The name of the item being requested. This is used to determine which recipe item is
            being requested when the consumer has a recipe with multiple items.
        available_rate_ipm : int
            The max rate in items per minute that the supplier can provide for the requested item.
        """

#---------------------------------------------------------------------------------------------------

class MapSingleSupplyNode(MapNode):
    """
    A node that supplies a single type of item.
    """
    #---------------------------------------------------------------------------

    def __init__(self, supplied_item_name:str) -> None:
        self.supplied_item_name = supplied_item_name
        self._parent_consumers:list[MapConsumerNode] = []

    #---------------------------------------------------------------------------

    @abstractmethod
    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        """
        Get this node's suppliers of items. The request_item_name parameter is used to determine
        which suppliers to return in the case of a multi-item supplier.

        Parameters
        ----------
        request_item_name : str | None, optional
            The name of the item being requested. This is used to determine which suppliers to
            return in the case of a multi-item supplier. If None, then all suppliers are returned.
        """
        pass

    #---------------------------------------------------------------------------

    def get_parent_consumers(self) -> tuple[MapConsumerNode, ...]:
        """
        Get this node's consumers of items that are directly connected to this node.
        """
        return tuple(self._parent_consumers)

    #---------------------------------------------------------------------------

    def add_parent_consumer(self, consumer:MapConsumerNode) -> None:
        """
        Add a consumer that is directly connected to this node.
        """
        self._parent_consumers.append(consumer)

    #---------------------------------------------------------------------------

    def register_demand(self, consumer:MapConsumerNode, request_item_name:str, request_ipm:int) -> None:
        """
        Register a consumer's demand for this node's supplied item. This is used to calculate the
        rate that this node can supply to each of its consumers.

        Parameters
        ----------
        consumer : MapConsumerNode
            The consumer that is requesting the item.
        request_item_name : str
            The name of the item being requested. This is used to determine which recipe item is
            being requested when the consumer has a recipe with multiple items.
        request_ipm : int
            The requested IPM of the consumer.
        """

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapSupplyConnector(MapSingleSupplyNode):
    """
    A supply connector is a node that connects a multi-item supplier to a consumer. It is used to
    provide access to only one of the possible items from a multi-item supplier.

    This is not a MapConsumerNode, even though it has suppliers, because it exists as a part of
    the owner node which is the consumer that has been added to the supplier as the consumer.
    This is done as only the owner is aware of the multiple items being supplied so only the
    owner can provide the entire context.
    """
    def __init__(self, owner:"MapMultiSupplyNode", supplied_item_name:str) -> None:
        MapSingleSupplyNode.__init__(self, supplied_item_name)
        if isinstance(owner, MapNode):
            MapNode.__init__(self, owner.global_id)
        else:
            raise ValueError(
                f"Owner of MapSupplyConnector must be a MapNode, got {type(owner).__name__}")
        self.owner = owner
        self.suppliers:list[MapSingleSupplyNode] = []

    #---------------------------------------------------------------------------

    def get_owner(self) -> "MapMultiSupplyNode":
        """
        Gets the supply node.
        """
        return self.owner

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" supply connector item name '{self.supplied_item_name}'"
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_global_id(self) -> str:
        return MapNode.get_global_id(self)

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.owner.get_node_id()

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        if request_item_name is not None and request_item_name != self.supplied_item_name:
            return tuple()
        return tuple(self.suppliers)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapMultiSupplyNode(MapNode):
    """
    A node that supplies more than one type of item to consumers.
    """
    #---------------------------------------------------------------------------

    def __init__(self, supplied_item_names:list[str]|None) -> None:
        self._supplied_items:dict[str,MapSupplyConnector] = {}
        if supplied_item_names is not None:
            for item_name in supplied_item_names:
                self._supplied_items[item_name] = MapSupplyConnector(self, item_name)

    #---------------------------------------------------------------------------

    @property
    def supplied_items(self) -> tuple[MapSupplyConnector, ...]:
        return tuple(self._supplied_items.values())

    #---------------------------------------------------------------------------

    def add_supplied_item(self, item_name:str) -> MapSupplyConnector:
        return self._supplied_items.setdefault(item_name, MapSupplyConnector(self, item_name))

    #---------------------------------------------------------------------------

    def get_item_connector(self, item_name:str) -> MapSupplyConnector:
        connector = self._supplied_items.get(item_name)
        if connector:
            return connector
        raise ValueError(f"Supplied item '{item_name}' not found in multi-supply node.")

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        """
        Get this node's suppliers of items. The request_item_name parameter is used to determine
        which suppliers to return.

        Parameters
        ----------
        request_item_name : str | None, optional
            The name of the item being requested. This is used to determine which suppliers to
            return. If None, then all suppliers of all items are returned.
        """
        if request_item_name is None:
            # If no item name is provided, return all suppliers for all items.
            suppliers = []
            for connector in self._supplied_items.values():
                suppliers.extend(connector.get_suppliers())
            return tuple(suppliers)
        connector = self._supplied_items.get(request_item_name)
        if connector:
            return connector.get_suppliers(request_item_name)
        return tuple()

    #---------------------------------------------------------------------------

    def get_parent_consumers(self, supplied_item_name:str|None = None) -> tuple[MapConsumerNode, ...]:
        """
        Get this node's consumers of items that are directly connected to this node. When
        supplied_item_name is provided, only consumers that consume the specified item are returned.
        """
        if supplied_item_name is not None:
            return self.get_item_connector(supplied_item_name).get_parent_consumers()
        else:
            consumers = []
            for connector in self._supplied_items.values():
                consumers.extend(connector.get_parent_consumers())
            return tuple(consumers)

    #---------------------------------------------------------------------------

    def add_parent_consumer(self, consumer:MapConsumerNode, supplied_item_name:str) -> None:
        """
        Add a consumer of supplied item that is directly connected to this node.
        """
        self.get_item_connector(supplied_item_name).add_parent_consumer(consumer)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapProductionSupplyNode(MapSingleSupplyNode):
    def __init__(self, produced_item_name:str, recipe_production_ipm:int) -> None:
        super().__init__(produced_item_name)
        self.max_production_ipm = recipe_production_ipm

#---------------------------------------------------------------------------------------------------

def round_half_up(n:float) -> int:
    """
    Round a number to the nearest integer, rounding halves up.

    Parameters
    ----------
    n : float
        The number to round.

    Returns
    -------
    int
        The rounded number.
    """
    return math.floor(n + 0.5)

#---------------------------------------------------------------------------------------------------

class SupplierConsumerMatrix:
    """
    Allows for calculating the rate delivered to each of a supplier's direct consumer taking into
    consideration:

    * A supplier delivers to multiple consumers.
    * Only producer consumers request supplies.
    * All other consumers are pass-through consumers in that requests from producer consumers are
      passed through to producer suppliers and the deliveries from the suppliers pass through to
      the producer consumers.
    * Producer supplier and consumers are MapProductionSupplyNode instances.
    * Not all producer consumers will request at the same rate.
    * When a pass-through consumer is between a producer supplier and producer consumer, there may
      be many levels as well as routes from supplier to ultimate consumer and that more than one
      route may lead to the same producer consumer, however the rate delivered from the supplier to
      that producer consumer is the same regardless of the route taken and the rate could be
      fragmented across multiple routes to converge at the producer consumer with the intended rate.
    """

    # The matrix results in:
    #   for each direct consumer, for each item supplied, ratio of available item rate.
    #
    # Using the ratio, when the available item rate is changed, notify each direct consumer of the
    # new available item rate by multiplying the ratio by the new available item rate.

    #---------------------------------------------------------------------------

    def __init__(self) -> None:

        self._requestors:dict[str, dict[MapConsumerNode, int]] = {}
        """
        item name -> requestor -> defined rate.
        """

        self._routes:dict[tuple[str,MapConsumerNode], list[MapConsumerNode]] = {}
        """
        request key -> connectors that route to requestor.
        """

        self._ratios:dict[MapConsumerNode, dict[str, float]] = {}
        """
        direct consumer -> item name -> ratio of available item rate to deliver to direct consumer.
        """

    #---------------------------------------------------------------------------

    def add_consumer_request_ipm(
            self,
            connector:MapConsumerNode,
            requested_item_name:str,
            requestor:MapConsumerNode,
            request_ipm:int) -> None:
        """
        Add a consumer's requested IPM to the matrix. This is used to calculate the ratio of the
        available item rate that should be delivered to each direct consumer.

        Parameters
        ----------
        connector : MapConsumerNode
            This node's direct consumer that routes to the requestor.
        requested_item_name:str
            The item being requested.
        requestor : MapConsumerNode
            A producer consumer that is requesting the item.
        request_ipm : int
            The requested IPM of the consumer.
        """

        item_map = self._requestors.setdefault(requested_item_name, {})
        existing_request_ipm = item_map.get(requestor, None)
        if existing_request_ipm is None:
            item_map[requestor] = request_ipm
        elif existing_request_ipm != request_ipm:
            raise ValueError(
                f"Requestor '{requestor.get_global_id()}' has multiple different requested IPM"
                f" values for item '{requested_item_name}': {existing_request_ipm} and"
                f" {request_ipm}")

        self._routes.setdefault((requested_item_name, requestor), []).append(connector)

    #---------------------------------------------------------------------------

    def compute_connector_ratios(self) -> None:
        """
        Compute the ratio of the available item rate that should be delivered to each direct
        consumer. This must be called only after all consumer request IPM values have been added
        to the matrix.
        """

        for item_name, requests in self._requestors.items():
            total_request_ipm = sum(requests.values())
            connector_ipm_totals:dict[MapConsumerNode, float] = {}
            """
            connector -> total adjusted IPM routed through connector.
            """
            for requestor, request_ipm in requests.items():
                connectors = self._routes[(item_name, requestor)]
                num_connectors = len(connectors)
                proportial_rate = request_ipm / num_connectors
                for connector in connectors:
                    connector_ipm_totals[connector] \
                        = connector_ipm_totals.get(connector, 0) + proportial_rate
            for connector, ipm_total in connector_ipm_totals.items():
                ratio = ipm_total / total_request_ipm if total_request_ipm > 0 else 0
                self._ratios.setdefault(connector, {})[item_name] = ratio

    #---------------------------------------------------------------------------

    def get_ratio(self, connector:MapConsumerNode, item_name:str) -> float:
        """
        Get the ratio of the available item rate that should be delivered to the direct consumer
        via the connector for the specified item.

        Parameters
        ----------
        connector : MapConsumerNode
            The direct consumer connector for which to get the ratio.
        item_name : str
            The name of the item for which to get the ratio.

        Returns
        -------
        float
            The ratio of the available item rate that should be delivered to the direct consumer.
            This will be a value between 0 and 1 inclusive.
        """
        # It is possible that ratios have not been set if the pass-through nodes do not connect
        # with a producer consumer.
        return self._ratios.get(connector, {}).get(item_name, 0)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapResourceNode(MapSiteNode, MapProductionSupplyNode):

    def __init__(self,
                 site_id:str,
                 resource_id:str,
                 resource_item_name:str,
                 variant:str,
                 recipe_production_ipm:int,
                 building_id:str) -> None:

        MapNode.__init__(self, MapNode.id_for_site_node(site_id, resource_id))
        MapSiteNode.__init__(self, site_id)
        MapProductionSupplyNode.__init__(self, resource_item_name, recipe_production_ipm)
        self.resource_id = resource_id
        self.variant = variant
        self.building_id = building_id

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.resource_id

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        return tuple()

    #---------------------------------------------------------------------------

    def get_max_game_definition_requested_ipm(self) -> int:
        """
        Get the total requested IPM by consumers when the consumers are requesting at the game
        defined rate.
        """
        total_request_ipm = 0
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            consumer_requests += consumer.get_max_recipe_item_request_ipm(self.supplied_item_name)
        visited_consumers = set()
        for consumer, request_ipm in consumer_requests:
            if consumer.get_global_id() not in visited_consumers:
                total_request_ipm += request_ipm
                visited_consumers.add(consumer.get_global_id())
        return total_request_ipm

    #---------------------------------------------------------------------------

    def calculate_and_set_max_suppliable_rate_ipm(self) -> None:
        """
        Get the max recipe item request ipm from consumers and determine at what rate this
        resource node can supply the item if every consumer requests at the game defined rate.
        The transport rate is not taken into consideration for this calculation.
        """

        consumer_remote_mapping:dict[str, set[str]] = {}
        """
        When a consumer is a pass-through node, the actual consumer is not attached to this node
        so to calculate the rate delivered to a direct consumer, it is necessary to know which
        direct consumer routes to the remote consumer.

        requestor -> connector
        """

        remote_consumer_requests:dict[str, tuple[MapConsumerNode,int]] = {}
        """
        The same remote consumer may be returned from multiple direct consumers. Ensure that the
        remote consumer is represented exactly once. This is only an issue for when the direct
        consumer is a pass-through node.

        requestor -> requestor
        """

        remote_consumer_rate:dict[str, int] = {}
        """
        key = remote consumer id.

        requestor -> rate
        """

        direct_consumer_rate:dict[str, int] = {}
        """
        key = direct consumer id.

        connector -> rate
        """

        #
        # Get the request rates from nearest production consumers. The production consumer may
        # be directly linked to this node, or indirectly linked via one or more pass-through
        # nodes that are direct consumers of this node.
        #

        for consumer in self.get_parent_consumers():
            direct_consumer_rate[consumer.get_global_id()] = 0
            for cr in consumer.get_max_recipe_item_request_ipm(self.supplied_item_name):
                id = cr[0].get_global_id()
                consumer_remote_mapping.setdefault(id, set()).add(consumer.get_global_id())
                existing = remote_consumer_requests.get(id, None)
                if existing is None:
                    remote_consumer_requests[id] = cr
                elif existing[1] != cr[1]:
                    raise ValueError(
                        f"Consumer '{id}' has multiple different requested IPM values"
                        f" for item '{self.supplied_item_name}': {existing[1]} and {cr[1]}")

        total_request_ipm = sum(cr[1] for cr in remote_consumer_requests.values())

        available_ipm = min(self.max_production_ipm, total_request_ipm)

        #
        # Calculate the rate for each of the production consumers, whether they be a direct
        # consumer or a remote (indirect) consumer routed via pass-through node(s).
        #

        low_to_high_requests = sorted(remote_consumer_requests.values(), key=lambda cr: cr[1])
        num_requests = len(low_to_high_requests)
        for remote_consumer, request_ipm in low_to_high_requests:
            fair_ipm = available_ipm // num_requests
            if fair_ipm < request_ipm:
                remote_consumer_rate[remote_consumer.get_global_id()] = fair_ipm
                #remote_consumer.set_max_available_rate_ipm(self, self.supplied_item_name, fair_ipm)
                available_ipm -= fair_ipm
            else:
                remote_consumer_rate[remote_consumer.get_global_id()] = request_ipm
                #remote_consumer.set_max_available_rate_ipm(self, self.supplied_item_name, request_ipm)
                available_ipm -= request_ipm
            num_requests -= 1

        #
        # Calculate the rate for each of the direct consumers.
        #

        # A remote consumer may be reachable through multiple direct consumers when there are
        # pass-through nodes. The remote consumer rate is thus apportioned to those direct consumers
        # that route to it.
        for remote_consumer_id, rate in remote_consumer_rate.items():
            direct_consumer_ids = consumer_remote_mapping[remote_consumer_id]
            num_direct_consumers = len(direct_consumer_ids)
            if 1 == num_direct_consumers:
                # This will handle the case where a production consumer is either routed through
                # only one of the direct consumers, or when it is the direct consumer.
                #
                # Case 1: where the production consumer is the direct consumer
                #
                # ┌───────┐    ┌────────┐
                # │Source │    │Producer│
                # │Node   ├───►│Consumer│
                # └───────┘    │Node    │
                #              └────────┘
                #
                # Case 2: where the production consumer is linked via one direct consumer that is
                #         a pass-through node.
                #
                # ┌───────┐    ┌────────┐    ┌────────┐
                # │Source │    │Consumer│    │Producer│
                # │Node   ├───►│Node    ├───►│Consumer│
                # └───────┘    └────────┘    │Node    │
                #                            └────────┘
                #
                direct_consumer_rate[direct_consumer_ids.pop()] += rate
            else:
                # When there are multiple direct consumers routing to the same remote consumer,
                # then at least one of the direct consumers is always a pass-through node. The
                # rate is split evenly across the direct consumers.
                #
                # Case 3: where the production consumer is only linked to this node via
                #         pass-through nodes.
                #
                #               ┌────────┐
                # ┌───────┐┌───►│Consumer├─┐    ┌────────┐
                # │Source ││    │Node    │ │    │Producer│
                # │Node   ├┤    └────────┘ ├───►│Consumer│
                # └───────┘│    ┌────────┐ │    │Node    │
                #          │    │Consumer│ │    └────────┘
                #          └───►│Node    ├─┘
                #               └────────┘
                #
                # Case 4: where the production consumer is both directly linked to this node and
                #         linked via a pass-through node.
                #
                #                           ┌────────┐
                #                           │Producer│
                # ┌───────┐                 │Consumer│
                # │Source ├────────────────►│Node    │
                # │Node   ├┐                └────────┘
                # └───────┘│    ┌────────┐     ▲
                #          │    │Consumer│     │
                #          └───►│Node    ├─────┘
                #               └────────┘
                #
                remaining_rate = rate
                dc_rate = round_half_up(rate / num_direct_consumers)
                for idx, direct_consumer_id in enumerate(direct_consumer_ids):
                    if idx == num_direct_consumers - 1:
                        dc_rate = remaining_rate
                    direct_consumer_rate[direct_consumer_id] += dc_rate
                    remaining_rate -= dc_rate

        #
        # Set the rates.
        #

        for consumer in self.get_parent_consumers():
            rate = direct_consumer_rate[consumer.get_global_id()]
            consumer.set_max_available_rate_ipm(self, self.supplied_item_name, rate)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class RecipeItem:

    #---------------------------------------------------------------------------

    def __init__(self, recipe_item_name:str, required_ipm:int) -> None:
        self.recipe_item_name = recipe_item_name
        """
        Name of the item required by this recipe to craft the crafted item.
        """
        self.required_ipm = required_ipm
        """
        Amount required per minute of this recipe item to craft the crafted item.
        """
        self.suppliers:list[MapSingleSupplyNode] = []

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        """
        Get this recipe item's suppliers. The request_item_name parameter is used to
        check if this recipe item is the one requested, and if it doesn't match the recipe
        item name, then an empty tuple is returned.

        Parameters
        ----------
        request_item_name : str | None, optional
            The name of the item being requested. If None, then all suppliers are returned.
        """
        if request_item_name is not None and request_item_name != self.recipe_item_name:
            return tuple()
        return tuple(self.suppliers)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapCrafterNode(MapFactoryNode, MapProductionSupplyNode, MapConsumerNode):

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 crafter_id:str,
                 crafted_item:str,
                 recipe_production_ipm:int,
                 craft_recipe:list[tuple[str, int, int]],
                 building_id:str) -> None:

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, crafter_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        MapProductionSupplyNode.__init__(self, crafted_item, recipe_production_ipm)
        self.crafter_id = crafter_id
        self.recipe:tuple[RecipeItem, ...] = tuple(
            RecipeItem(recipe_item, required_ipm) for recipe_item, _, required_ipm in craft_recipe
        )
        self.building_id = building_id
        # Not sure if the dict should be keyed on the id or the actual MapSingleSupplyNode
        # reference. Not 100% sure how I will be using this so to keep it simple, just using the
        # id.
        self._max_available_recipe_item_ipm:dict[str, dict[str, int]] = {
            recipe_item.recipe_item_name: {} for recipe_item in self.recipe
        }
        """
        A dictionary of recipe item names mapped to a dictionary of supplier global IDs and the
        max available IPM that the supplier can provide for that recipe item.
        """

    #---------------------------------------------------------------------------

    def add_recipe_item_supplier(self, recipe_item_name:str, supplier:MapSingleSupplyNode) -> None:
        cast(MapNode, supplier).flag_not_terminal()
        for recipe_item in self.recipe:
            if recipe_item.recipe_item_name == recipe_item_name:
                recipe_item.add_supplier(supplier)
                break

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.crafter_id

    #---------------------------------------------------------------------------

    def get_recipe_items(self) -> tuple[RecipeItem, ...]:
        return self.recipe

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        """
        Get the suppliers for the given recipe item name. If the request_item_name is None, then all
        suppliers for all recipe items are returned. If the request_item_name does not match any of
        the recipe item names, then an empty tuple is returned.

        Parameters
        ----------
        request_item_name : str | None, optional
            The name of the recipe item being requested. This is used to determine which suppliers to
            return. If None, then all suppliers for all recipe items are returned. The
            crafted item name may not be used and will raise an error if passed in.
        """
        if request_item_name is None:
            suppliers = []
            for recipe_item in self.recipe:
                suppliers.extend(recipe_item.get_suppliers())
            return tuple(suppliers)
        else:
            if request_item_name == self.supplied_item_name:
                raise ValueError(
                    "For a crafter, the suppliers will never supply the crafted item itself, so"
                    " the requested item must be one of the recipe items. Call get_recipe_items()"
                    " to get the recipe items.")
            for recipe_item in self.recipe:
                if recipe_item.recipe_item_name == request_item_name:
                    return recipe_item.get_suppliers()
        return tuple()

    #---------------------------------------------------------------------------

    def get_all_supplier_node_ids(self) -> set[str]:
        """
        Get the set of all supplier node IDs that are supplying items to this crafter.
        This was added for finding terminal nodes.
        """
        supplier_node_ids = set()
        for recipe_item in self.recipe:
            for supplier in recipe_item.suppliers:
                supplier_node_ids.add(supplier.get_node_id())
        return supplier_node_ids

    #---------------------------------------------------------------------------

    def get_max_recipe_item_request_ipm(
            self, request_item_name: str) -> list[tuple[MapConsumerNode, int]]:
        for recipe_item in self.recipe:
            if recipe_item.recipe_item_name == request_item_name:
                return [(self, recipe_item.required_ipm)]
        raise ValueError(
            f"Requested item '{request_item_name}' is not one of the recipe items for this"
             " crafter.")

    #---------------------------------------------------------------------------

    def set_max_available_rate_ipm(
            self,
            supplier:MapSingleSupplyNode,
            request_item_name:str,
            available_rate_ipm:int) -> None:
        # It is assumed that the recipe items has been populated so an unknown request_item_name
        # will result in a KeyError.
        self._max_available_recipe_item_ipm[request_item_name][supplier.get_global_id()] \
            = available_rate_ipm

    #---------------------------------------------------------------------------

    def get_max_game_definition_requested_ipm(self) -> int:
        """
        Get the total requested IPM by consumers when the consumers are requesting at the game
        defined rate.
        """
        total_request_ipm = 0
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            consumer_requests += consumer.get_max_recipe_item_request_ipm(self.supplied_item_name)
        visited_consumers = set()
        for consumer, request_ipm in consumer_requests:
            if consumer.get_global_id() not in visited_consumers:
                total_request_ipm += request_ipm
                visited_consumers.add(consumer.get_global_id())
        return total_request_ipm

    #---------------------------------------------------------------------------

    def _calculate_max_production_rate_from_max_suppliers(self) -> int:
        """
        Calculate how much of max_production_ipm is available to be delivered to consumers
        based on the max available IPM from suppliers.
        """
        total_available_ipm_per_supplied_item:dict[str, int] = {}
        for item_name, supplier_maxes in self._max_available_recipe_item_ipm.items():
            total_available_ipm_per_supplied_item[item_name] = sum(supplier_maxes.values())
        lowest_ratio:float = min(
            total_available_ipm_per_supplied_item[r.recipe_item_name] / r.required_ipm
            for r in self.recipe
        )
        # Not concerned about precision issues,
        if lowest_ratio < 1:
            return math.floor(self.max_production_ipm * lowest_ratio)
        else:
            return self.max_production_ipm

    #---------------------------------------------------------------------------

    def calculate_and_set_max_suppliable_rate_ipm(self) -> None:
        """
        Get the max recipe item request ipm from consumers and determine at what rate this
        crafter node can supply the item if every consumer requests at the game defined rate.
        The transport rate is not taken into consideration for this calculation.
        """
        adjusted_max_production_ipm = self._calculate_max_production_rate_from_max_suppliers()
        if 0 == adjusted_max_production_ipm:
            # If the adjusted max production IPM is 0, then there is no need to calculate the
            # available IPM for consumers as it will be 0 regardless of the consumer requests.
            for consumer in self.get_parent_consumers():
                consumer.set_max_available_rate_ipm(self, self.supplied_item_name, 0)
            return

        consumer_remote_mapping:dict[str, set[str]] = {}
        """
        When a consumer is a pass-through node, the actual consumer is not attached to this node
        so to calculate the rate delivered to a direct consumer, it is necessary to know which
        direct consumer routes to the remote consumer.

        requestor -> connector
        """

        remote_consumer_requests:dict[str, tuple[MapConsumerNode,int]] = {}
        """
        The same remote consumer may be returned from multiple direct consumers. Ensure that the
        remote consumer is represented exactly once. This is only an issue for when the direct
        consumer is a pass-through node.

        requestor -> requestor
        """

        remote_consumer_rate:dict[str, int] = {}
        """
        key = remote consumer id.

        requestor -> rate
        """

        direct_consumer_rate:dict[str, int] = {}
        """
        key = direct consumer id.

        connector -> rate
        """

        #
        # Get the request rates from nearest production consumers. The production consumer may
        # be directly linked to this node, or indirectly linked via one or more pass-through
        # nodes that are direct consumers of this node.
        #

        for consumer in self.get_parent_consumers():
            direct_consumer_rate[consumer.get_global_id()] = 0
            for cr in consumer.get_max_recipe_item_request_ipm(self.supplied_item_name):
                id = cr[0].get_global_id()
                consumer_remote_mapping.setdefault(id, set()).add(consumer.get_global_id())
                existing = remote_consumer_requests.get(id, None)
                if existing is None:
                    remote_consumer_requests[id] = cr
                elif existing[1] != cr[1]:
                    raise ValueError(
                        f"Consumer '{id}' has multiple different requested IPM values"
                        f" for item '{self.supplied_item_name}': {existing[1]} and {cr[1]}")

        total_request_ipm = sum(cr[1] for cr in remote_consumer_requests.values())

        available_ipm = min(adjusted_max_production_ipm, total_request_ipm)

        #
        # Calculate the rate for each of the production consumers, whether they be a direct
        # consumer or a remote (indirect) consumer routed via pass-through node(s).
        #

        low_to_high_requests = sorted(remote_consumer_requests.values(), key=lambda cr: cr[1])
        num_requests = len(low_to_high_requests)
        for remote_consumer, request_ipm in low_to_high_requests:
            fair_ipm = available_ipm // num_requests
            if fair_ipm < request_ipm:
                remote_consumer_rate[remote_consumer.get_global_id()] = fair_ipm
                #remote_consumer.set_max_available_rate_ipm(self, self.supplied_item_name, fair_ipm)
                available_ipm -= fair_ipm
            else:
                remote_consumer_rate[remote_consumer.get_global_id()] = request_ipm
                #remote_consumer.set_max_available_rate_ipm(self, self.supplied_item_name, request_ipm)
                available_ipm -= request_ipm
            num_requests -= 1

        #
        # Calculate the rate for each of the direct consumers.
        #

        # A remote consumer may be reachable through multiple direct consumers when there are
        # pass-through nodes. The remote consumer rate is thus apportioned to those direct consumers
        # that route to it.
        for remote_consumer_id, rate in remote_consumer_rate.items():
            direct_consumer_ids = consumer_remote_mapping[remote_consumer_id]
            num_direct_consumers = len(direct_consumer_ids)
            if 1 == num_direct_consumers:
                # This will handle the case where a production consumer is either routed through
                # only one of the direct consumers, or when it is the direct consumer.
                #
                # Case 1: where the production consumer is the direct consumer
                #
                # ┌───────┐    ┌────────┐
                # │Source │    │Producer│
                # │Node   ├───►│Consumer│
                # └───────┘    │Node    │
                #              └────────┘
                #
                # Case 2: where the production consumer is linked via one direct consumer that is
                #         a pass-through node.
                #
                # ┌───────┐    ┌────────┐    ┌────────┐
                # │Source │    │Consumer│    │Producer│
                # │Node   ├───►│Node    ├───►│Consumer│
                # └───────┘    └────────┘    │Node    │
                #                            └────────┘
                #
                direct_consumer_rate[direct_consumer_ids.pop()] += rate
            else:
                # When there are multiple direct consumers routing to the same remote consumer,
                # then at least one of the direct consumers is always a pass-through node. The
                # rate is split evenly across the direct consumers.
                #
                # Case 3: where the production consumer is only linked to this node via
                #         pass-through nodes.
                #
                #               ┌────────┐
                # ┌───────┐┌───►│Consumer├─┐    ┌────────┐
                # │Source ││    │Node    │ │    │Producer│
                # │Node   ├┤    └────────┘ ├───►│Consumer│
                # └───────┘│    ┌────────┐ │    │Node    │
                #          │    │Consumer│ │    └────────┘
                #          └───►│Node    ├─┘
                #               └────────┘
                #
                # Case 4: where the production consumer is both directly linked to this node and
                #         linked via a pass-through node.
                #
                #                           ┌────────┐
                #                           │Producer│
                # ┌───────┐                 │Consumer│
                # │Source ├────────────────►│Node    │
                # │Node   ├┐                └────────┘
                # └───────┘│    ┌────────┐     ▲
                #          │    │Consumer│     │
                #          └───►│Node    ├─────┘
                #               └────────┘
                #
                remaining_rate = rate
                dc_rate = round_half_up(rate / num_direct_consumers)
                for idx, direct_consumer_id in enumerate(direct_consumer_ids):
                    if idx == num_direct_consumers - 1:
                        dc_rate = remaining_rate
                    direct_consumer_rate[direct_consumer_id] += dc_rate
                    remaining_rate -= dc_rate

        #
        # Set the rates.
        #

        for consumer in self.get_parent_consumers():
            rate = direct_consumer_rate[consumer.get_global_id()]
            consumer.set_max_available_rate_ipm(self, self.supplied_item_name, rate)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

# There is a multi-item storage building in the game. Will add support for that later when I
# have unlocked it and can see how it works.

# TODO: Handle number of stacks.
#       For now, since we are not implementing buffering, the number of stacks is not relevant.

class MapSingleStorageNode(MapFactoryNode, MapSingleSupplyNode, MapConsumerNode):

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 storage_id:str,
                 stored_item_name:str,
                 building_id:str) -> None:

        if "*" == stored_item_name:
            raise ValueError("MapSingleStorageNode does not support multi-item storage")

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, storage_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        MapSingleSupplyNode.__init__(self, stored_item_name)
        self.storage_id = storage_id
        self.building_id = building_id
        self.suppliers:list[MapSingleSupplyNode] = []
        self._max_available_recipe_item_ipm:dict[str,int] = {}
        """
        A dictionary of supplier global IDs and the max available IPM that the supplier can
        provide.
        """
        self.supplier_consumer_matrix:SupplierConsumerMatrix|None = None

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" storage item name '{self.supplied_item_name}'"
        cast(MapNode, supplier).flag_not_terminal()
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.storage_id

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        if request_item_name is not None and request_item_name != self.supplied_item_name:
            return tuple()
        return tuple(self.suppliers)

    #---------------------------------------------------------------------------

    def get_all_supplier_node_ids(self) -> set[str]:
        """
        Get the set of all supplier node IDs that are supplying items to this crafter.
        This was added for finding terminal nodes.
        """
        supplier_node_ids = set()
        for supplier in self.suppliers:
            supplier_node_ids.add(supplier.get_node_id())
        return supplier_node_ids

    #---------------------------------------------------------------------------

    def get_max_recipe_item_request_ipm(
            self, request_item_name: str) -> list[tuple[MapConsumerNode, int]]:
        if request_item_name != self.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item_name}' does not match stored item"
                 f" '{self.supplied_item_name}' for this storage.")
        # TODO: This should take into consideration the transport rate limits.
        self.supplier_consumer_matrix = SupplierConsumerMatrix()
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            requests = consumer.get_max_recipe_item_request_ipm(request_item_name)
            consumer_requests += requests
            for cn, r in requests:
                self.supplier_consumer_matrix.add_consumer_request_ipm(
                    consumer, request_item_name, cn, r)
        self.supplier_consumer_matrix.compute_connector_ratios()
        return consumer_requests

    #---------------------------------------------------------------------------

    def set_max_available_rate_ipm(
            self,
            supplier: MapSingleSupplyNode,
            request_item_name: str,
            available_rate_ipm: int) -> None:

        if request_item_name != self.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item_name}' does not match stored item"
                 f" '{self.supplied_item_name}' for this storage.")

        self._max_available_recipe_item_ipm[supplier.get_global_id()] = available_rate_ipm

        max_rate_ipm = sum(self._max_available_recipe_item_ipm.values())
        for consumer in self.get_parent_consumers():
            ratio = 0
            # It is very possible that the matrix has not been initialized if the supplier
            # production rate is zero.
            if self.supplier_consumer_matrix is not None:
                ratio = self.supplier_consumer_matrix.get_ratio(consumer, request_item_name)
            consumer.set_max_available_rate_ipm(
                self, request_item_name, math.floor(max_rate_ipm * ratio))

    #---------------------------------------------------------------------------

    def get_max_game_definition_requested_ipm(self) -> int:
        """
        Get the total requested IPM by consumers when the consumers are requesting at the game
        defined rate.
        """
        total_request_ipm = 0
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            consumer_requests += consumer.get_max_recipe_item_request_ipm(self.supplied_item_name)
        visited_consumers = set()
        for consumer, request_ipm in consumer_requests:
            if consumer.get_global_id() not in visited_consumers:
                total_request_ipm += request_ipm
                visited_consumers.add(consumer.get_global_id())
        return total_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapDispatcherNode(MapFactoryNode, MapSingleSupplyNode, MapConsumerNode):

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 dispatcher_id:str,
                 dispatched_item_name:str,
                 output_rate_limit_ipm:int,
                 input_rate_limit_ipm:int,
                 building_id:str) -> None:

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, dispatcher_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        MapSingleSupplyNode.__init__(self, dispatched_item_name)
        self.dispatcher_id = dispatcher_id
        self.output_rate_limit_ipm = output_rate_limit_ipm
        self.input_rate_limit_ipm = input_rate_limit_ipm
        self.building_id = building_id
        self.suppliers:list[MapSingleSupplyNode] = []
        self._max_available_recipe_item_ipm:dict[str,int] = {}
        """
        A dictionary of supplier global IDs and the max available IPM that the supplier can
        provide.
        """

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" dispatcher item name '{self.supplied_item_name}'"
        cast(MapNode, supplier).flag_not_terminal()
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def add_parent_consumer(self, consumer:MapConsumerNode) -> None:
        if self._parent_consumers is not None and 0 < len(self._parent_consumers):
            raise ValueError(
                "A dispatcher may only have one consumer, the receiver.")
        super().add_parent_consumer(consumer)

    #---------------------------------------------------------------------------

    def flag_not_terminal(self) -> None:
        print(
            f"Dispatcher {self.global_id} remains terminal as dispatchers are always terminal"
             " within the factory.")
        return

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.dispatcher_id

    #---------------------------------------------------------------------------

    def get_suppliers(self, request_item_name:str|None = None) -> tuple["MapSingleSupplyNode", ...]:
        if request_item_name is not None and request_item_name != self.supplied_item_name:
            return tuple()
        return tuple(self.suppliers)

    #---------------------------------------------------------------------------

    def get_all_supplier_node_ids(self) -> set[str]:
        """
        Get the set of all supplier node IDs that are supplying items to this crafter.
        This was added for finding terminal nodes.
        """
        supplier_node_ids = set()
        for supplier in self.suppliers:
            supplier_node_ids.add(supplier.get_node_id())
        return supplier_node_ids

    #---------------------------------------------------------------------------

    def get_max_recipe_item_request_ipm(
            self, request_item_name: str) -> list[tuple[MapConsumerNode, int]]:
        if request_item_name != self.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item_name}' does not match dispatched item"
                 f" '{self.supplied_item_name}' for this dispatcher.")
        # TODO: This should take into consideration the transport rate limits.
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            consumer_requests += consumer.get_max_recipe_item_request_ipm(request_item_name)
        return consumer_requests

    #---------------------------------------------------------------------------

    def set_max_available_rate_ipm(
            self,
            supplier: MapSingleSupplyNode,
            request_item_name: str,
            available_rate_ipm: int) -> None:
        if request_item_name != self.supplied_item_name:
            raise ValueError(
                f"Requested item '{request_item_name}' does not match dispatched item"
                 f" '{self.supplied_item_name}' for this dispatcher.")
        self._max_available_recipe_item_ipm[supplier.get_global_id()] = available_rate_ipm

    #---------------------------------------------------------------------------

    def get_max_game_definition_requested_ipm(self) -> int:
        """
        Get the total requested IPM by consumers when the consumers are requesting at the game
        defined rate.
        """
        total_request_ipm = 0
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers():
            consumer_requests += consumer.get_max_recipe_item_request_ipm(self.supplied_item_name)
        visited_consumers = set()
        for consumer, request_ipm in consumer_requests:
            if consumer.get_global_id() not in visited_consumers:
                total_request_ipm += request_ipm
                visited_consumers.add(consumer.get_global_id())
        return total_request_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapReceiverNode(MapFactoryNode, MapMultiSupplyNode, MapConsumerNode):

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 receiver_id:str,
                 building_id:str) -> None:

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, receiver_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        MapMultiSupplyNode.__init__(self, None)
        self.receiver_id = receiver_id
        self.building_id = building_id
        self._max_available_recipe_item_ipm:dict[str, dict[str, int]] = {}
        """
        A dictionary of dispatched item names mapped to a dictionary of supplier global IDs and the
        max available IPM that the supplier can provide for that item.
        """

    #---------------------------------------------------------------------------

    def add_dispatcher(self, dispatcher:MapDispatcherNode) -> None:
        # Dispatchers are always terminal within the factory, so we don't need to flag them as not
        # terminal here.
        connector = self.add_supplied_item(dispatcher.supplied_item_name)
        connector.add_supplier(dispatcher)

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.receiver_id

    #---------------------------------------------------------------------------

    def get_max_recipe_item_request_ipm(
            self, request_item_name: str) -> list[tuple[MapConsumerNode, int]]:
        # TODO: This should take into consideration the transport rate limits.
        consumer_requests:list[tuple[MapConsumerNode,int]] = []
        for consumer in self.get_parent_consumers(request_item_name):
            consumer_requests += consumer.get_max_recipe_item_request_ipm(request_item_name)
        return consumer_requests

    #---------------------------------------------------------------------------

    def get_max_game_definition_requested_ipm(self) -> tuple[tuple[str,int]]:
        """
        Get the total requested IPM by consumers when the consumers are requesting at the game
        defined rate.
        """
        rates = []
        for connector in self.supplied_items:
            total_request_ipm = 0
            consumer_requests:list[tuple[MapConsumerNode,int]] = []
            for consumer in connector.get_parent_consumers():
                consumer_requests \
                    += consumer.get_max_recipe_item_request_ipm(connector.supplied_item_name)
            visited_consumers = set()
            for consumer, request_ipm in consumer_requests:
                if consumer.get_global_id() not in visited_consumers:
                    total_request_ipm += request_ipm
                    visited_consumers.add(consumer.get_global_id())
            rates.append((connector.supplied_item_name, total_request_ipm))
        return tuple(rates)

    #---------------------------------------------------------------------------

    def set_max_available_rate_ipm(
            self,
            supplier:MapSingleSupplyNode,
            request_item_name:str,
            available_rate_ipm:int) -> None:
        # Check that the request item name is one of the supplied items for this receiver.
        self.get_item_connector(request_item_name)
        self._max_available_recipe_item_ipm \
            .setdefault(request_item_name, {})[supplier.get_global_id()] = available_rate_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

# MapTargetNode does not supply items and is not part of the production chain so doesn't implement
# a *SupplyNode interface.
class MapTargetNode(MapFactoryNode, MapConsumerNode):
    """
    A target node represents a desired output from the factory. It is not an actual node in the
    factory but is used to represent the demand for an item that is being produced by the factory.
    """

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 target_id:str,
                 target_rate_ipm:int,
                 target_amount:int) -> None:

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, target_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        self.target_id = target_id
        self.suppliers:list[MapSingleSupplyNode] = []
        self.target_rate_ipm:int = target_rate_ipm
        """
        Target production rate in items per minute. If set to zero, then target is disabled and
        shouldn't be used for production calculations.
        """
        self.target_amount:int = target_amount
        """
        Optional amount of the target item to produce. When not provided, will be zero.
        """
        self._max_available_recipe_item_ipm:dict[str,int] = {}
        """
        A dictionary of supplier global IDs and the max available IPM that the supplier can
        provide.
        """

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        if self.suppliers and self.suppliers[0].supplied_item_name != supplier.supplied_item_name:
            raise ValueError(
                f"Supplier '{supplier.get_global_id()}' item name '{supplier.supplied_item_name}'"
                 " does not match existing"
                f" supplier item name '{self.suppliers[0].supplied_item_name}' for target node"
                f" '{self.global_id}'. All suppliers for a target node must supply the same item.")
        # Target nodes are not part of the production chain and are only used to represent demand,
        # so they do not affect terminal status of their suppliers.
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_global_id(self) -> str:
        return MapNode.get_global_id(self)

    #---------------------------------------------------------------------------

    def get_node_id(self) -> str:
        return self.target_id

    #---------------------------------------------------------------------------

    def get_suppliers(self) -> tuple["MapSingleSupplyNode", ...]:
        return tuple(self.suppliers)

    #---------------------------------------------------------------------------

    def get_max_recipe_item_request_ipm(
            self, request_item_name: str) -> list[tuple[MapConsumerNode, int]]:
        """
        A target node has no game defined recipe ipm so must always return 0.
        """
        return [(self, 0)]

    #---------------------------------------------------------------------------

    def set_max_available_rate_ipm(
            self,
            supplier: MapSingleSupplyNode,
            request_item_name: str,
            available_rate_ipm: int) -> None:
        self._max_available_recipe_item_ipm[supplier.get_global_id()] = available_rate_ipm

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapData:
    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        self.sites:dict[str,MapSite] = {}
        self.map_nodes:list[MapNode] = []

    #---------------------------------------------------------------------------

    def _add_site(self, site:MapSite) -> None:
        assert site.site_id not in self.sites, \
            f"Site with ID '{site.site_id}' already exists in map data"
        self.sites[site.site_id] = site

    #---------------------------------------------------------------------------

    def delete_all_ledgers(self) -> None:
        for node in self.map_nodes:
            node.ledger = None

    #---------------------------------------------------------------------------

    def delete_all_graphs(self) -> None:
        for node in self.map_nodes:
            node.graph = None

    #---------------------------------------------------------------------------

    def _add_node(self, node:MapNode) -> None:
        if isinstance(node, MapSite):
            self._add_site(node)
        elif isinstance(node, MapFactory):
            node.site.add_factory(node)
        elif isinstance(node, MapSiteNode):
            if node.site is None:
                raise ValueError(f"Site node '{node.global_id}' does not have an associated site")
            if isinstance(node, MapResourceNode):
                node.site.add_resource_node(node)
            elif isinstance(node, MapFactoryNode):
                if node.factory is None:
                    raise ValueError(f"Factory node '{node.global_id}' does not have an associated factory")
                if isinstance(node, MapCrafterNode):
                    node.factory.add_crafter(node)
                elif isinstance(node, MapSingleStorageNode):
                    node.factory.add_storage(node)
                elif isinstance(node, MapDispatcherNode):
                    node.factory.add_dispatcher(node)
                elif isinstance(node, MapReceiverNode):
                    node.factory.add_receiver(node)
                elif isinstance(node, MapTargetNode):
                    node.factory.add_target(node)
                else:
                    raise ValueError(f"Unsupported factory node type: {type(node).__name__}")
            else:
                raise ValueError(f"Unsupported site node type: {type(node).__name__}")
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
        self.map_nodes.append(node)

    #---------------------------------------------------------------------------

    def _get_node_by_id(self, site_id:str, node_id:str, factory_id:str|None = None) -> MapNode:
        if factory_id is None:
            # Look for resource nodes.
            map_node_id = MapNode.id_for_site_node(site_id, node_id)
            for node in self.map_nodes:
                if node.global_id == map_node_id:
                    return node
        else:
            # Look for both resource nodes and factory nodes. This is necessary as the caller
            # won't know the type of node when looking up a from_id reference.
            map_factory_node_id = MapNode.id_for_factory_node(site_id, factory_id, node_id)
            map_site_node_id = MapNode.id_for_site_node(site_id, node_id)
            for node in self.map_nodes:
                if node.global_id in (map_factory_node_id, map_site_node_id):
                    return node
        raise ValueError(
            f"Node site '{site_id}', factory '{factory_id}', id '{node_id}' not found in map data.")

    #---------------------------------------------------------------------------

    def get_supplier_node(
            self,
            supplied_item_name:str,
            site_id:str,
            node_id:str,
            factory_id:str|None = None) -> MapSingleSupplyNode:
        """
        Get the supplier node for the given item and node reference. The node reference is given
        by the site ID, node ID, and optionally factory ID. If the factory ID is not provided, it
        will look for a resource node with the given site ID and node ID. If the factory ID is
        provided, it will look for both resource nodes and factory nodes with the given site ID,
        node ID, and factory ID. This is necessary because the caller won't know the type of node
        when looking up a from_id reference.

        Parameters
        ----------
        supplied_item_name : str
            The name of the item being supplied. This is used to determine which supplier to return
            in the case of a multi-item supplier.

        site_id : str
            The ID of the site where the supplier node is located.

        node_id : str
            The ID of the node being referenced. This is the resource ID for resource nodes and the
            crafter/storage/dispatcher/receiver ID for factory nodes.

        factory_id : str | None, optional
            The ID of the factory where the supplier node is located. This is only needed when
            looking up factory nodes, but it is optional to allow looking up resource nodes without
            needing to provide a factory ID.

        Returns
        -------

        MapSingleSupplyNode
            The supplier node for the given item and node reference. If the node is not found,
            or the node is not one of MapSingleSupplyNode, MapMultiSupplyNode, then a ValueError
            is raised.
        """
        node = self._get_node_by_id(site_id, node_id, factory_id)
        if isinstance(node, MapSingleSupplyNode):
            return node
        if isinstance(node, MapMultiSupplyNode):
            return node.get_item_connector(supplied_item_name)
        raise ValueError(f"Node with ID '{node.global_id}' is not a supply node.")

    #---------------------------------------------------------------------------

    def set_map_data(self, map_data:dict[str, Any], game_data:GameData) -> "MapData":
        """
        Build the map data from the given map data dictionary.
        """
        for site_id, site_data in map_data.items():
            site = MapSite( site_id,
                            int(site_data['x']),
                            int(site_data['y']),
                            site_data['teleporter'],
                            site_data.get('description', ''))
            self._add_node(site)
            #print("-" * 40)
            #print(f"Site ID    : {site.site_id}")
            #print(f"Latitude   : {site.x}")
            #print(f"Longitude  : {site.y}")
            #print(f"Teleporter : {site.teleporter}")
            #print(f"Description: {site.description}")
            for resource_id, resource_data in site_data.get('resource_nodes', {}).items():
                item_name = resource_data["resource_item"]
                variant = resource_data["variant"]
                recipe_production_ipm = game_data.get_production_rate_ipm(item_name, variant)
                building_id = game_data.get_item_building(item_name)
                node = MapResourceNode( site_id,
                                        resource_id,
                                        item_name,
                                        variant,
                                        recipe_production_ipm,
                                        building_id)
                node.set_site(site)
                self._add_node(node)
                #print("-" * 40)
                #print(f"resource id       : {node.resource_id}")
                #print(f"item name         : {node.supplied_item_name}")
                #print(f"variant           : {node.variant}")
                #print(f"max production ipm: {node.max_production_ipm}")

            for factory_id, factory_values in site_data.get("factories", {}).items():
                factory = MapFactory(site, factory_id)
                self._add_node(factory)

                machines = factory_values.get("machines", {})
                for crafter_id, crafter_values in machines.get("crafters", {}).items():
                    item_name = crafter_values["crafted_item"]
                    recipe_production_ipm = game_data.get_production_rate_ipm(item_name)
                    recipe = game_data.get_craft_recipe(item_name)
                    building_id = game_data.get_item_building(item_name)
                    node = MapCrafterNode(  site_id,
                                            factory_id,
                                            crafter_id,
                                            item_name,
                                            recipe_production_ipm,
                                            recipe,
                                            building_id)
                    node.set_factory(factory)
                    self._add_node(node)
                    #print("-" * 40)
                    #print(f"factory id        : {node.factory_id}")
                    #print(f"crafter id        : {node.crafter_id}")
                    #print(f"crafted item name : {node.supplied_item_name}")
                    #print(f"production ipm    : {node.max_production_ipm}")
                    #for recipe_item, _, required_ipm in recipe:
                    #    print(f"  - {recipe_item:<20}: {required_ipm} ipm")
                    #    from_ids = [
                    #        ids for x in crafter_values["inputs"]
                    #            if x["input_item"] == recipe_item
                    #            for ids in x["from_ids"]
                    #    ]
                    #    print(f"    from ids: {", ".join(from_ids)}")

                for storage_id, storage_values in machines.get("storage", {}).items():
                    item_name = storage_values["stored_item"]
                    building_id = storage_values.get("building_id", "")
                    node = MapSingleStorageNode(
                        site_id, factory_id, storage_id, item_name, building_id)
                    node.set_factory(factory)
                    self._add_node(node)
                    #print("-" * 40)
                    #print(f"factory id       : {node.factory_id}")
                    #print(f"storage id       : {node.storage_id}")
                    #print(f"stored item name : {node.supplied_item_name}")
                    #print(f"building id      : {node.building_id}")
                    #for input_data in storage_values.get("inputs", []):
                    #    from_ids = input_data["from_ids"]
                    #    print(f"  - from ids: {', '.join(from_ids)}")

                for dispatcher_id, dispatcher_values \
                        in factory_values.get("dispatchers", {}).items():
                    item_name = dispatcher_values["dispatched_item"]
                    building_id = dispatcher_values.get("building_id", "")
                    from_ids = dispatcher_values["from_ids"]
                    output_rate_limit_ipm = int(dispatcher_values["output_rate_limit_ipm"])
                    input_rate_limit_ipm = int(dispatcher_values["input_rate_limit_ipm"])
                    node = MapDispatcherNode(site_id,
                                             factory_id,
                                             dispatcher_id,
                                             item_name,
                                             output_rate_limit_ipm,
                                             input_rate_limit_ipm,
                                             building_id)
                    node.set_factory(factory)
                    self._add_node(node)
                    #print("-" * 40)
                    #print(f"factory id        : {node.factory_id}")
                    #print(f"dispatcher id     : {node.dispatcher_id}")
                    #print(f"dispatched item   : {node.supplied_item_name}")
                    #print(f"building id       : {node.building_id}")
                    #print(f"output rate limit : {node.output_rate_limit_ipm} ipm")
                    #print(f"input rate limit  : {node.input_rate_limit_ipm} ipm")
                    #print(f"from ids          : {', '.join(from_ids)}")

                for receiver_id, receiver_values in factory_values.get("receivers", {}).items():
                    building_id = receiver_values.get("building_id", "")
                    dispatchers = [
                        (d["site_id"], d["factory_id"], d["dispatcher_id"])
                        for d in receiver_values["dispatchers"]
                    ]
                    node = MapReceiverNode(site_id, factory_id, receiver_id, building_id)
                    node.set_factory(factory)
                    self._add_node(node)
                    #print("-" * 40)
                    #print(f"factory id  : {node.factory_id}")
                    #print(f"receiver id : {node.receiver_id}")
                    #print(f"building id : {node.building_id}")
                    #print( "dispatchers :")
                    #for s, f, d in dispatchers:
                    #    print(f"  - {s} / {f} / {d}")

                for target_id, target_values in factory_values.get("targets", {}).items():
                    target_rate_ipm = int(target_values["target_rate_ipm"])
                    target_amount = int(target_values["target_amount"])
                    node = MapTargetNode(site_id,
                                         factory_id,
                                         target_id,
                                         target_rate_ipm,
                                         target_amount)
                    node.set_factory(factory)
                    self._add_node(node)
                    #print("-" * 40)
                    #print(f"factory id      : {node.factory_id}")
                    #print(f"target id       : {node.target_id}")
                    #print(f"target rate ipm : {node.target_rate_ipm}")
                    #print(f"target amount   : {node.target_amount}")
                    #print("suppliers  :")
                    #for supplier in target_values.get("from_ids", []):
                    #    print(f"  - {supplier}")


        #
        # Link nodes. This has to happen after all nodes have been created.
        #

        for site_id, site_data in map_data.items():
            for factory_id, factory_values in site_data.get("factories", {}).items():

                # The receivers have to be linked first as they are multi-item suppliers and their
                # supply connectors must be initialized before use. If this wasn't done, when
                # calling _get_supplier_node, an error would be raised.
                for receiver_id, receiver_values in factory_values.get("receivers", {}).items():
                    node = self._get_node_by_id(site_id, receiver_id, factory_id)
                    if not isinstance(node, MapReceiverNode):
                        raise ValueError(f"Node with ID '{node.global_id}' is not a MapReceiverNode.")
                    dispatchers = receiver_values["dispatchers"]
                    for dispatcher in dispatchers:
                        dispatcher_node = self._get_node_by_id(
                            dispatcher["site_id"],
                            dispatcher["dispatcher_id"],
                            dispatcher["factory_id"])
                        if not isinstance(dispatcher_node, MapDispatcherNode):
                            raise ValueError(
                                f"Dispatcher node '{dispatcher_node.global_id}' is not a"
                                 " MapDispatcherNode.")
                        node.add_dispatcher(dispatcher_node)
                        dispatcher_node.add_parent_consumer(node)

                # NOTE: When multi-storage is implemented, it must be linked here after receivers.

                machines = factory_values.get("machines", {})

                for crafter_id, crafter_values in machines.get("crafters", {}).items():
                    node = self._get_node_by_id(site_id, crafter_id, factory_id)
                    if not isinstance(node, MapCrafterNode):
                        raise ValueError(f"Node with ID '{node.global_id}' is not a MapCrafterNode.")
                    for input_data in crafter_values.get("inputs", []):
                        recipe_item_name = input_data["input_item"]
                        from_ids = input_data["from_ids"]
                        for from_id in from_ids:
                            #print(f"{crafter_id} / {recipe_item_name} from {from_id}")
                            supplier_node = self.get_supplier_node(
                                recipe_item_name, site_id, from_id, factory_id)
                            node.add_recipe_item_supplier(recipe_item_name, supplier_node)
                            supplier_node.add_parent_consumer(node)

                for storage_id, storage_values in machines.get("storage", {}).items():
                    node = self._get_node_by_id(site_id, storage_id, factory_id)
                    if not isinstance(node, MapSingleStorageNode):
                        raise ValueError(f"Node with ID '{node.global_id}' is not a MapSingleStorageNode.")
                    for input_data in storage_values.get("inputs", []):
                        from_ids = input_data["from_ids"]
                        for from_id in from_ids:
                            supplier_node = self.get_supplier_node(
                                node.supplied_item_name, site_id, from_id, factory_id)
                            node.add_supplier(supplier_node)
                            supplier_node.add_parent_consumer(node)

                for dispatcher_id, dispatcher_values \
                        in factory_values.get("dispatchers", {}).items():
                    node = self._get_node_by_id(site_id, dispatcher_id, factory_id)
                    if not isinstance(node, MapDispatcherNode):
                        raise ValueError(f"Node with ID '{node.global_id}' is not a MapDispatcherNode.")
                    from_ids = dispatcher_values["from_ids"]
                    for from_id in from_ids:
                        supplier_node = self.get_supplier_node(
                            node.supplied_item_name, site_id, from_id, factory_id)
                        node.add_supplier(supplier_node)
                        supplier_node.add_parent_consumer(node)

                for target_id, target_values in factory_values.get("targets", {}).items():
                    node = self._get_node_by_id(site_id, target_id, factory_id)
                    if not isinstance(node, MapTargetNode):
                        raise ValueError(f"Node with ID '{node.global_id}' is not a MapTargetNode.")
                    for from_id in target_values.get("from_ids", []):
                        supplier_map_node = self._get_node_by_id(site_id, from_id, factory_id)
                        # The plan is that even when multi-item storage is implemented, the
                        # target node will only allow crafter and single item storage.
                        supplier_node = cast(MapSingleSupplyNode, supplier_map_node)
                        node.add_supplier(supplier_node)
                        supplier_node.add_parent_consumer(node)

        #
        # Set max available recipe item IPM for all nodes. This has to happen after all nodes
        # have been linked.
        #

        # TODO: Implement this by walking the graph starting with nodes that are terminal and
        #       don't use receiver. That should populate all the pass-through nodes as well as
        #       dispatcher so the next step is to walk the graph of terminal nodes that use
        #       receiver and stop when reaching a node that has already been populated.

        # This implementation is for testing only.
        for site_id, site in self.sites.items():
            for resource_id, resource_node in site.resource_nodes.items():
                resource_node.calculate_and_set_max_suppliable_rate_ipm()
            for factory_id, factory in site.factories.items():
                for crafter_id, crafter_node in factory.crafters.items():
                    crafter_node.calculate_and_set_max_suppliable_rate_ipm()

        return self

    #---------------------------------------------------------------------------

    def populate_uses_receiver_flags(self) -> None:
        """
        Populate the uses_receiver flag for all nodes in the map data. This is used to determine
        whether a node is using a receiver in its supply chain.
        """
        def walk_node(input:MapSingleSupplyNode) -> bool:
            #print(f"walk_node: {input.get_global_id()}")
            if isinstance(input, MapSupplyConnector) \
                    and isinstance(input.get_owner(), MapReceiverNode):
                return True
            uses_receiver = False
            for supplier in input.get_suppliers():
                uses_receiver |= walk_node(supplier)
            cast(MapNode,input).flag_uses_receiver(uses_receiver)
            return uses_receiver

        terminals = [node for node in self.map_nodes if node.is_terminal]

        #for terminal in terminals:
        #    print(f"Terminal node: {terminal.global_id} ({type(terminal).__name__})")

        for terminal in terminals:
            if isinstance(terminal, MapSingleSupplyNode):
                walk_node(terminal)
            else:
                if debug_mode:
                    print(
                        f"Terminal node '{terminal.global_id}' is not a MapSingleSupplyNode but"
                        f" '{type(terminal)}'. Skipping uses_receiver flag population for this"
                         " node.")

    #---------------------------------------------------------------------------

    def debug_dump_nodes(self) -> None:
        for site in self.sites.values():
            print("-" * 40)
            print(f"Site ID    : {site.site_id}")
            print(f"Latitude   : {site.x}")
            print(f"Longitude  : {site.y}")
            print(f"Teleporter : {site.teleporter}")
            print(f"Description: {site.description}")
            for resource_node in site.resource_nodes.values():
                print("-" * 40)
                print(f"resource id       : {resource_node.resource_id}")
                print(f"item name         : {resource_node.supplied_item_name}")
                print(f"variant           : {resource_node.variant}")
                print(f"max production ipm: {resource_node.max_production_ipm}")
                print(f"is terminal       : {resource_node.is_terminal}")
                print(f"uses receiver     : {resource_node.uses_receiver}")
                print(f"max recipe item request ipm: {resource_node.get_max_game_definition_requested_ipm()}")
                print( "consumers:")
                for consumer in resource_node.get_parent_consumers():
                    print(f"  - {consumer.get_global_id()}")

            for factory in site.factories.values():
                for crafter in factory.crafters.values():
                    print("-" * 40)
                    print(f"factory id        : {crafter.factory_id}")
                    print(f"crafter id        : {crafter.crafter_id}")
                    print(f"crafted item name : {crafter.supplied_item_name}")
                    print(f"max production ipm: {crafter.max_production_ipm}")
                    print(f"is terminal       : {crafter.is_terminal}")
                    print(f"uses receiver     : {crafter.uses_receiver}")
                    print(f"max recipe item request ipm: {crafter.get_max_game_definition_requested_ipm()}")
                    print( "recipe:")
                    for recipe_item in crafter.recipe:
                        print(f"  - {recipe_item.recipe_item_name:<20}:"
                              f" {recipe_item.required_ipm} ipm")
                        for supplier in recipe_item.suppliers:
                            print(f"      - {supplier.get_global_id()}  max available ipm: {crafter._max_available_recipe_item_ipm.get(recipe_item.recipe_item_name, {}).get(supplier.get_global_id(), 'N/A')}")
                    print( "consumers:")
                    for consumer in crafter.get_parent_consumers():
                        print(f"  - {consumer.get_global_id()}")

                for storage in factory.storages.values():
                    print("-" * 40)
                    print(f"factory id      : {storage.factory_id}")
                    print(f"storage id      : {storage.storage_id}")
                    print(f"stored item name: {storage.supplied_item_name}")
                    print(f"building id     : {storage.building_id}")
                    print(f"is terminal     : {storage.is_terminal}")
                    print(f"uses receiver   : {storage.uses_receiver}")
                    print(f"max recipe item request ipm: {storage.get_max_game_definition_requested_ipm()}")
                    print( "suppliers:")
                    for supplier in storage.suppliers:
                        print(f"  - {supplier.get_global_id()}  max available ipm: {storage._max_available_recipe_item_ipm.get(supplier.get_global_id(), 'N/A')}")
                    print( "consumers:")
                    for consumer in storage.get_parent_consumers():
                        print(f"  - {consumer.get_global_id()}")

                for dispatcher in factory.dispatchers.values():
                    print("-" * 40)
                    print(f"factory id       : {dispatcher.factory_id}")
                    print(f"dispatcher id    : {dispatcher.dispatcher_id}")
                    print(f"dispatched item  : {dispatcher.supplied_item_name}")
                    print(f"building id      : {dispatcher.building_id}")
                    print(f"output rate limit: {dispatcher.output_rate_limit_ipm} ipm")
                    print(f"input rate limit : {dispatcher.input_rate_limit_ipm} ipm")
                    print(f"is terminal      : {dispatcher.is_terminal}")
                    print(f"uses receiver    : {dispatcher.uses_receiver}")
                    print(f"max recipe item request ipm: {dispatcher.get_max_game_definition_requested_ipm()}")
                    print( "suppliers:")
                    for supplier in dispatcher.suppliers:
                        print(f"  - {supplier.get_global_id()}  max available ipm: {dispatcher._max_available_recipe_item_ipm.get(supplier.get_global_id(), 'N/A')}")
                    print( "consumers:")
                    for consumer in dispatcher.get_parent_consumers():
                        print(f"  - {consumer.get_global_id()}")

                for receiver in factory.receivers.values():
                    print("-" * 40)
                    print(f"factory id   : {receiver.factory_id}")
                    print(f"receiver id  : {receiver.receiver_id}")
                    print(f"building id  : {receiver.building_id}")
                    print(f"is terminal  : {receiver.is_terminal}")
                    print(f"uses receiver: {receiver.uses_receiver}")
                    print(f"max recipe item request ipm: {receiver.get_max_game_definition_requested_ipm()}")
                    print( "dispatched items:")
                    for dispatched_item in receiver.supplied_items:
                        print(f"  - {dispatched_item.supplied_item_name} from dispatcher(s):")
                        for supplier in dispatched_item.suppliers:
                            print(f"    - {supplier.get_global_id()}  max available ipm: {receiver._max_available_recipe_item_ipm.get(dispatched_item.supplied_item_name, {}).get(supplier.get_global_id(), 'N/A')}")
                    print( "consumers:")
                    for consumer in receiver.get_parent_consumers():
                        print(f"  - {consumer.get_global_id()}")

                for target in factory.targets.values():
                    print("-" * 40)
                    print(f"factory id     : {target.factory_id}")
                    print(f"target id      : {target.target_id}")
                    print(f"target item    : {target.suppliers[0].supplied_item_name if target.suppliers else 'N/A'}")
                    print(f"target rate ipm: {target.target_rate_ipm}")
                    print(f"target amount  : {target.target_amount}")
                    print( "suppliers:")
                    for supplier in target.suppliers:
                        print(f"  - {supplier.get_global_id()}  max available ipm: {target._max_available_recipe_item_ipm.get(supplier.get_global_id(), 'N/A')}")

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

def load_map_data_dict_from_file(file_path:str = 'pins_data.json') -> dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

#---------------------------------------------------------------------------------------------------

def load_map_data(game_data:GameData, file_path:str = 'pins_data.json') -> MapData:
    map_dict_data = load_map_data_dict_from_file(file_path)
    return MapData().set_map_data(map_dict_data, game_data)

#---------------------------------------------------------------------------------------------------

def main():
    global debug_mode
    debug_mode = True

    game_data = load_game_data()
    #with open('pins_data.json', 'r', encoding='utf-8') as f:
    #    map_dict_data = json.load(f)
    #map_data = MapData().set_map_data(map_dict_data, game_data)

    map_data = load_map_data(game_data)

    #target_node = MapTargetNode("test-site", "factory", "target1", "glass")
    #map_data.sites["test-site"].factories["factory"].add_target(target_node)
    #target_node.add_supplier(map_data.get_supplier_node("glass", "test-site", "s-glass-1", "factory"))

    map_data.populate_uses_receiver_flags()
    print()
    print()
    print()
    print()
    print()
    print()
    map_data.debug_dump_nodes()

    print()
    print()
    print()
    print()
    print()
    print()

    def walk_tree(node:MapSingleSupplyNode, depth:int = 0) -> None:
        indent = "  " * depth
        print(f"{indent}- {node.get_global_id()} ({type(node).__name__})")
        if isinstance(node, MapCrafterNode):
            for recipe_item in node.get_recipe_items():
                print(f"{indent}  - Recipe item: {recipe_item.recipe_item_name}")
                for supplier in recipe_item.get_suppliers(recipe_item.recipe_item_name):
                    walk_tree(supplier, depth + 2)
        elif isinstance(node, MapSingleSupplyNode):
            for supplier in node.get_suppliers(node.supplied_item_name):
                walk_tree(supplier, depth + 1)

    node = map_data._get_node_by_id("test-site", "s-glass-1", "factory")
    if isinstance(node, MapSingleSupplyNode):
        walk_tree(node)




#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------