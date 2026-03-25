
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
from enum import StrEnum
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

class DemandRequest:
    """
    Represents a consumer's demand for a specific item at a specific rate.

    Parameters
    ----------
    consumer : MapConsumerNode
        The consumer that is requesting the item.

    request_item_name : str
        The name of the item being requested. This is used to determine which recipe item is being
        requested when the consumer has a recipe with multiple items.

    request_ipm : int
        The requested rate in items per minute for the requested item.
    """

    #---------------------------------------------------------------------------

    def __init__(self, consumer:"MapConsumerNode", request_item_name:str, request_ipm:int) -> None:
        self.consumer = consumer
        self.request_item_name = request_item_name
        self.request_ipm = request_ipm

    #---------------------------------------------------------------------------

    # Two demand requests are considered equal if they are from the same consumer and for the same
    # item regardless of the requested IPM.
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DemandRequest):
            return (self.consumer == value.consumer
                    and self.request_item_name == value.request_item_name)
        return False

    #---------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash((self.consumer, self.request_item_name))

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class DemandSupply:
    """
    Represents a supply of demanded items for a specific item at a specific rate.

    Parameters
    ----------
    from_supplier : MapSingleSupplyNode
        The supplier that is providing the item.

    for_consumer : MapConsumerNode
        The consumer that demanded the supply of item.

    supplied_ipm : int
        The rate in items per minute that the requested item can be supplied.
    """

    #---------------------------------------------------------------------------

    def __init__(
            self,
            from_supplier:"MapSingleSupplyNode",
            for_consumer:"MapConsumerNode",
            supplied_ipm:int) -> None:

        self.from_supplier = from_supplier
        self.for_consumer = for_consumer
        self.supplied_ipm = supplied_ipm

    #---------------------------------------------------------------------------

    @property
    def request_item_name(self) -> str:
        return self.from_supplier.supplied_item_name

    #---------------------------------------------------------------------------

    # Two demand supplies are considered equal if they are from the same supplier and for the same
    # consumer regardless of the supplied IPM.
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DemandSupply):
            return (self.from_supplier == value.from_supplier
                    and self.for_consumer == value.for_consumer)
        return False

    #---------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash((self.from_supplier, self.for_consumer))

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

class DemandCategory(StrEnum):
    """
    An enumeration of demand categories. This is used to separate different types of demand for the
    same item. For example, to differenciate between the calculation for max available rate when all
    requestors are requesting at the game defined rate vs when requestors are requesting at a target
    rate.
    """
    GAME_DEFINITION = "game_definition"
    TARGET_RATE = "target_rate"

#---------------------------------------------------------------------------------------------------

class MapConsumerNode(MapNode):
    """
    A node that consumes items from suppliers.
    """

    @abstractmethod
    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:
        """
        Register supplier availability rates all the way up the chain. Used by the supplier to
        inform the consumer of the max rate that it can supply the requested item.

        Parameters
        ----------
        demand_category : str
            The demand category for which to set the available rate IPM. This is used to separate
            different types of demand for the same item. For example, to differenciate between the
            calculation for max available rate when all requestors are requesting at the game
            defined rate vs when requestors are requesting at a target rate.

        child_supplier : MapSingleSupplyNode
            A supplier that is directly connected to this consumer.

        demand_suppliers : list[DemandSupply]
            A list of supplies for the requested item from the child supplier. This is used to
            determine the total supplied IPM for the requested item from the child supplier.
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

        self._demand_parent:dict[str, dict[MapConsumerNode,set[MapConsumerNode]]] = {}
        """
        Links the demand consumer to the parent consumer so that the amount of demand can be
        apportioned to the parent.

        demand category
            -> parent consumer
                -> list of demand consumers that are linked to the parent consumer.
        """

        self._demand:dict[str, dict[MapConsumerNode, int]] = {}
        """
        demand category -> consumer -> request ipm.
        """

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

    def _register_demand_ipm(
            self,
            demand_category:str,
            parent_consumer:MapConsumerNode,
            requestors:list[DemandRequest]) -> None:
        """
        Register a consumer's demand for this node's supplied item. This is used to calculate the
        rate that this node can supply to each of its consumers.

        Parameters
        ----------
        demand_category : str
            To allow for multiple different demand calculations, the category separates the demands.
            For example, to differenciate between the calculation for max available rate when all
            requestors are requesting at the game defined rate vs when requestors are requesting at
            a target rate.

        parent_consumer : MapConsumerNode
            The consumer that is directly connected to this node.

        requestors : list[DemandRequest]
            A list of demand requests from requesting consumers. When the parent consumers is a
            producer, then the list will have exactly one demand request that is the parent
            consumer. When the parent consumer is a pass-through node, the list will contain the
            requests from  one or more requestors linked to the pass-through node.
        """
        #
        # Verify that this method is being called only after the parent structure is in place.
        #

        if 0 == len(self._parent_consumers):
            raise ValueError(
                f"Attempting to register demand for node '{self.get_global_id()}' before any parent"
                f" consumers have been added."
            )

        if parent_consumer not in self._parent_consumers:
            raise ValueError(
                 "Attempting to register demand for parent consumer"
                f" '{parent_consumer.get_global_id()}' that is not a direct consumer of node"
                f" '{self.get_global_id()}'."
            )

        #
        #
        #

        parent_demand_consumers = self._demand_parent \
            .setdefault(demand_category, {}) \
                .setdefault(parent_consumer, set())

        category_map = self._demand.setdefault(demand_category, {})

        for request in requestors:
            if request.request_item_name != self.supplied_item_name:
                raise ValueError(
                    f"Requested item name '{request.request_item_name}' does not match supplied"
                    f" item name '{self.supplied_item_name}' for demand category '{demand_category}'"
                    f" from consumer '{request.consumer.get_global_id()}'")
            parent_demand_consumers.add(request.consumer)
            existing_request_ipm = category_map.get(request.consumer, None)
            category_map[request.consumer] = request.request_ipm
            if existing_request_ipm is not None and existing_request_ipm != request.request_ipm:
                # When a producer has demand from multiple consumers, the order that demand is
                # registered is not guaranteed so demand may increase as consumers are registered.
                print(
                    f"Consumer '{request.consumer.get_global_id()}' rate change for item"
                    f" '{self.supplied_item_name}' in demand category '{demand_category}':"
                    f" {existing_request_ipm} -> {request.request_ipm}"
                )

    #---------------------------------------------------------------------------

    def _total_demand_ipm(self, demand_category:str) -> int:
        """
        Get the total demand IPM for the specified demand category.

        Parameters
        ----------
        demand_category : str
            The demand category for which to get the total demand IPM.
        """
        category_map = self._demand.get(demand_category, {})
        return sum(category_map.values())

    #---------------------------------------------------------------------------

    def _get_demands(self, demand_category:str) -> list[tuple[MapConsumerNode, int]]:
        """
        Get the demands for the specified demand category.

        Parameters
        ----------
        demand_category : str
            The demand category for which to get the demands.
        """
        category_map = self._demand.get(demand_category, {})
        return [(consumer, ipm) for consumer, ipm in category_map.items()]

    #---------------------------------------------------------------------------

    def _get_parent_demands(
            self,
            demand_category:str,
            parent_consumer:MapConsumerNode) -> tuple[MapConsumerNode, ...]:
        """
        Get the demand consumers that are linked to the parent consumer for the specified demand
        category.
        """
        return tuple(self._demand_parent.get(demand_category, {}).get(parent_consumer, set()))

    #---------------------------------------------------------------------------

    @abstractmethod
    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:
        """
        Register this consumer's demand with its suppliers all the way down the production chain.

        Parameters
        ----------
        demand_category : str
            To allow for multiple different demand calculations, the category separates the demands.
            For example, to differenciate between the calculation for max available rate when all
            requestors are requesting at the game defined rate vs when requestors are requesting at
            a target rate.
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

                 ┌────────────────────────────┐
                 │OWNER                       │
    ┌──────┐   ┌─┴────────────────────────────┴─┐   ┌────────┐
    │Source│   │                                │   │Consumer│
    │Nodes ├──►│   MapSupplyConnector (Item 1)  ├──►│Nodes   │
    └──────┘   │                                │   └────────┘
               └─┬────────────────────────────┬─┘
    ┌──────┐   ┌─┴────────────────────────────┴─┐   ┌────────┐
    │Source│   │                                │   │Consumer│
    │Nodes ├──►│   MapSupplyConnector (Item 2)  ├──►│Nodes   │
    └──────┘   │                                │   └────────┘
               └─┬────────────────────────────┬─┘
                 └────────────────────────────┘
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

        self._supplier_availablity_ipm:dict[str, set[DemandSupply]] = {}
        """
        Registration of the max available rate of supply for this item in a demand category.

        demand category -> supplies
        """

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

    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:

        self._register_demand_ipm(demand_category, parent_consumer, requestors)

        demands = [
            DemandRequest(d[0], self.supplied_item_name, d[1])
                for d in self._demand[demand_category].items()
        ]

        # If an owner has suppliers, then it will be a MapConsumerNode.
        for supplier in self.get_suppliers():
            supplier.register_demand_with_suppliers(
                demand_category, cast(MapConsumerNode, self.owner), demands)

    #---------------------------------------------------------------------------

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        if demand_category not in self._demand:
             raise ValueError(
                 "Attempting to register_suppliable_rate_ipm for demand category"
                f" '{demand_category}' before any demand has been registered for resource node"
                f" '{self.get_global_id()}'."
            )

        if child_supplier not in self.suppliers:
            raise ValueError(
                f"child_supplier '{child_supplier.get_global_id()}' not registered as a direct"
                f" supplier for this storage node '{self.get_global_id()}'.")

        # Register the supplies with this node for the demand category.

        supplier_availability_set \
            = self._supplier_availablity_ipm.setdefault(demand_category, set())

        for ds in demand_suppliers:
            if ds.from_supplier.supplied_item_name != self.supplied_item_name:
                raise ValueError(
                    f"Supplied item '{ds.from_supplier.supplied_item_name}' does not match"
                    f" storage item '{self.supplied_item_name}'; from supplier"
                    f" '{ds.from_supplier.get_global_id()}'.")
            supplier_availability_set.add(ds)

        # A supply connector is a pass-though node so send the DemandSupply objects on to the
        # applicable parent consumers without alteration.

        for parent in self.get_parent_consumers():
            supplies:list[DemandSupply] = []
            for demander in self._get_parent_demands(demand_category, parent):
                for_demander = [
                    ds for ds in supplier_availability_set if ds.for_consumer == demander]
                supplies.extend(for_demander)
            if supplies:
                parent.register_suppliable_rate_ipm(demand_category, self, supplies)

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
        """
        The max production rate in items per minute that this node can produce as defined by
        the recipe.
        """

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

    def calculate_and_set_max_suppliable_rate_ipm(self, demand_category:str) -> None:
        """
        Calculate the max suppliable rate in items per minute for this resource node based on the
        registered demand.

        Can only be called once all consumers have been registered with this resource node
        via register_demand_with_suppliers() for the demand_category.
        """

        if demand_category not in self._demand:
             raise ValueError(
                 "Attempting to calculate max suppliable rate for demand category"
                f" '{demand_category}' before any demand has been registered for resource node"
                f" '{self.get_global_id()}'."
            )

        total_request_ipm = self._total_demand_ipm(demand_category)
        available_ipm = min(self.max_production_ipm, total_request_ipm)

        provided_consumer_rate:dict[str, int] = {}
        """
        key = demanding consumer id.

        requestor -> rate
        """

        # Apportion the available rate to the demanding consumers. The available rate is shared
        # fairly among the demanding consumers using a moving average. A consumer won't be supplied
        # more than their demand.

        demands = self._get_demands(demand_category)
        # The requests are sorted so that consumers with lower requested rate get their demand
        # fulfilled first and the nature of the moving average means that consumers with higher
        # requests have a better chance of getting their demand fulfilled.
        low_to_high_requests = sorted(demands, key=lambda cr: cr[1])
        num_requests = len(low_to_high_requests)
        for demanding_consumer, request_ipm in low_to_high_requests:
            fair_ipm = available_ipm // num_requests
            if fair_ipm < request_ipm:
                provided_consumer_rate[demanding_consumer.get_global_id()] = fair_ipm
                available_ipm -= fair_ipm
            else:
                provided_consumer_rate[demanding_consumer.get_global_id()] = request_ipm
                available_ipm -= request_ipm
            num_requests -= 1

        # Register the available rates for demanding consumers with the direct consumers.

        for parent in self.get_parent_consumers():
            supplies:list[DemandSupply] = []
            for demander in self._get_parent_demands(demand_category, parent):
                demand_supply = DemandSupply(
                    self, demander, provided_consumer_rate[demander.get_global_id()])
                supplies.append(demand_supply)
            if supplies:
                parent.register_suppliable_rate_ipm(demand_category, self, supplies)

    #---------------------------------------------------------------------------

    def register_demand_with_suppliers(
            self,
            demand_category: str,
            parent_consumer: MapConsumerNode,
            requestors: list[DemandRequest]) -> None:

        self._register_demand_ipm(demand_category, parent_consumer, requestors)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class RecipeItem:

    #---------------------------------------------------------------------------

    def __init__(self, owner:"MapCrafterNode", recipe_item_name:str, required_ipm:int) -> None:

        self.owner = owner

        self.recipe_item_name = recipe_item_name
        """
        Name of the item required by this recipe to craft the crafted item.
        """

        self.required_ipm = required_ipm
        """
        Amount required per minute of this recipe item to craft the crafted item.
        """

        self.suppliers:list[MapSingleSupplyNode] = []

        self._supplier_availablity_ipm:dict[str, dict[MapSingleSupplyNode, int]] = {}
        """
        Registration of the max available rate of supply for this recipe item in a demand category.

        demand category -> supplier -> available rate in items per minute.
        """

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

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        if child_supplier not in self.suppliers:
            raise ValueError(
                f"child_supplier '{child_supplier.get_global_id()}' not registered as a direct"
                f" supplier for this recipe item '{self.recipe_item_name}' of "
                f" '{self.owner.get_global_id()}'.")

        supplier_availability_map = self._supplier_availablity_ipm.setdefault(demand_category, {})
        for ds in demand_suppliers:
            if ds.from_supplier.supplied_item_name != self.recipe_item_name:
                raise ValueError(
                    f"Supplied item '{ds.from_supplier.supplied_item_name}' does not match"
                    f" recipe item '{self.recipe_item_name}'; from supplier"
                    f" '{ds.from_supplier.get_global_id()}'.")
            if ds.for_consumer != self.owner:
                raise ValueError(
                    f"Demand supply for consumer '{ds.for_consumer.get_global_id()}' does not match"
                    f" recipe item owner '{self.owner.get_global_id()}'; from supplier"
                    f" '{ds.from_supplier.get_global_id()}'.")
            supplier_availability_map[ds.from_supplier] = ds.supplied_ipm

    #---------------------------------------------------------------------------

    def get_available_rate_ipm(self, demand_category:str) -> int:
        """
        Get the total available rate in items per minute for this recipe item based on the
        registered supplier rates.

        Parameters
        ----------
        demand_category : str
            The demand category for which to get the available rate IPM.
        """
        supplier_availability_map = self._supplier_availablity_ipm.get(demand_category, {})
        return sum(supplier_availability_map.values())

    #---------------------------------------------------------------------------

    def get_available_rate_ratio(self, demand_category:str) -> float:
        """
        Get the ratio of the available rate to the required rate for this recipe item based on the
        registered supplier rates.

        Parameters
        ----------
        demand_category : str
            The demand category for which to get the available rate ratio.

        Returns
        -------
        float
            The ratio of the available rate to the required rate for this recipe item. This will
            be a value between 0 and 1 inclusive.
        """
        available_ipm = self.get_available_rate_ipm(demand_category)
        if self.required_ipm <= available_ipm:
            return 1
        else:
            return available_ipm / self.required_ipm if self.required_ipm > 0 else 0

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
            RecipeItem(self, recipe_item, required_ipm)
                for recipe_item, _, required_ipm in craft_recipe
        )
        self.building_id = building_id

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

    def register_recipe_demand_with_suppliers(self) -> None:
        """
        Register this consumer's demand with its suppliers based on the recipe. This should be
        called after the suppliers have been added and the recipe items have been populated.
        """
        for recipe_item in self.recipe:
            for supplier in recipe_item.suppliers:
                supplier.register_demand_with_suppliers(
                    DemandCategory.GAME_DEFINITION,
                    self,
                    [DemandRequest(self, recipe_item.recipe_item_name, recipe_item.required_ipm)])

    #---------------------------------------------------------------------------

    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:

        self._register_demand_ipm(demand_category, parent_consumer, requestors)

        # Only demand from the suppliers a rate that is necessary to meet the demand of the
        # consumers.

        total_demand_ipm = self._total_demand_ipm(demand_category)
        request_ratio:float = 1.0
        if total_demand_ipm < self.max_production_ipm:
            request_ratio = total_demand_ipm / self.max_production_ipm

        for recipe_item in self.recipe:
            for supplier in recipe_item.suppliers:
                supplier.register_demand_with_suppliers(
                    demand_category,
                    self,
                    [DemandRequest(
                        self,
                        recipe_item.recipe_item_name,
                        math.ceil(recipe_item.required_ipm * request_ratio)
                            if total_demand_ipm > 0 else 0
                    )])

    #---------------------------------------------------------------------------

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        if demand_category not in self._demand:
             raise ValueError(
                 "Attempting to register_suppliable_rate_ipm for demand category"
                f" '{demand_category}' before any demand has been registered for resource node"
                f" '{self.get_global_id()}'."
            )

        # Register the supplies with this node for the demand category.

        for recipe_item in self.recipe:
            if child_supplier in recipe_item.suppliers:
                recipe_item.register_suppliable_rate_ipm(
                    demand_category, child_supplier, demand_suppliers)
            break

        # Based on the available supplies, calculate and register the production rate with the
        # registered parent consumers.

        supply_availability_ratio = min(
            r.get_available_rate_ratio(demand_category) for r in self.recipe)

        production_ipm = math.floor(self.max_production_ipm * supply_availability_ratio)

        total_request_ipm = self._total_demand_ipm(demand_category)
        available_ipm = min(production_ipm, total_request_ipm)

        provided_consumer_rate:dict[str, int] = {}
        """
        key = demanding consumer id.

        requestor -> rate
        """

        # Apportion the available rate to the demanding consumers. The available rate is shared
        # fairly among the demanding consumers using a moving average. A consumer won't be supplied
        # more than their demand.

        demands = self._get_demands(demand_category)
        # The requests are sorted so that consumers with lower requested rate get their demand
        # fulfilled first and the nature of the moving average means that consumers with higher
        # requests have a better chance of getting their demand fulfilled.
        low_to_high_requests = sorted(demands, key=lambda cr: cr[1])
        num_requests = len(low_to_high_requests)
        for demanding_consumer, request_ipm in low_to_high_requests:
            fair_ipm = available_ipm // num_requests
            if fair_ipm < request_ipm:
                provided_consumer_rate[demanding_consumer.get_global_id()] = fair_ipm
                available_ipm -= fair_ipm
            else:
                provided_consumer_rate[demanding_consumer.get_global_id()] = request_ipm
                available_ipm -= request_ipm
            num_requests -= 1

        # Register the available rates for demanding consumers with the direct consumers.

        for parent in self.get_parent_consumers():
            supplies:list[DemandSupply] = []
            for demander in self._get_parent_demands(demand_category, parent):
                demand_supply = DemandSupply(
                    self, demander, provided_consumer_rate[demander.get_global_id()])
                supplies.append(demand_supply)
            if supplies:
                parent.register_suppliable_rate_ipm(demand_category, self, supplies)

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

        self._supplier_availablity_ipm:dict[str, set[DemandSupply]] = {}
        """
        Registration of the max available rate of supply for this item in a demand category.

        demand category -> supplies
        """

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

    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:

        self._register_demand_ipm(demand_category, parent_consumer, requestors)

        demands = [
            DemandRequest(d[0], self.supplied_item_name, d[1])
                for d in self._demand[demand_category].items()
        ]

        for supplier in self.get_suppliers():
            supplier.register_demand_with_suppliers(demand_category, self, demands)

    #---------------------------------------------------------------------------

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        if demand_category not in self._demand:
             raise ValueError(
                 "Attempting to register_suppliable_rate_ipm for demand category"
                f" '{demand_category}' before any demand has been registered for resource node"
                f" '{self.get_global_id()}'."
            )

        if child_supplier not in self.suppliers:
            raise ValueError(
                f"child_supplier '{child_supplier.get_global_id()}' not registered as a direct"
                f" supplier for this storage node '{self.get_global_id()}'.")

        # Register the supplies with this node for the demand category.

        supplier_availability_set \
            = self._supplier_availablity_ipm.setdefault(demand_category, set())

        for ds in demand_suppliers:
            if ds.from_supplier.supplied_item_name != self.supplied_item_name:
                raise ValueError(
                    f"Supplied item '{ds.from_supplier.supplied_item_name}' does not match"
                    f" storage item '{self.supplied_item_name}'; from supplier"
                    f" '{ds.from_supplier.get_global_id()}'.")
            supplier_availability_set.add(ds)

        # A storage node is a pass-though node so send the DemandSupply objects on to the
        # applicable parent consumers without alteration.

        for parent in self.get_parent_consumers():
            supplies:list[DemandSupply] = []
            for demander in self._get_parent_demands(demand_category, parent):
                for_demander = [
                    ds for ds in supplier_availability_set if ds.for_consumer == demander]
                supplies.extend(for_demander)
            if supplies:
                parent.register_suppliable_rate_ipm(demand_category, self, supplies)

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

        self._supplier_availablity_ipm:dict[str, set[DemandSupply]] = {}
        """
        Registration of the max available rate of supply for this item in a demand category.

        demand category -> supplies
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

    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:

        self._register_demand_ipm(demand_category, parent_consumer, requestors)

        demands = [
            DemandRequest(d[0], self.supplied_item_name, d[1])
                for d in self._demand[demand_category].items()
        ]

        for supplier in self.get_suppliers():
            supplier.register_demand_with_suppliers(demand_category, self, demands)

    #---------------------------------------------------------------------------

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        if demand_category not in self._demand:
             raise ValueError(
                 "Attempting to register_suppliable_rate_ipm for demand category"
                f" '{demand_category}' before any demand has been registered for resource node"
                f" '{self.get_global_id()}'."
            )

        if child_supplier not in self.suppliers:
            raise ValueError(
                f"child_supplier '{child_supplier.get_global_id()}' not registered as a direct"
                f" supplier for this storage node '{self.get_global_id()}'.")

        # Register the supplies with this node for the demand category.

        supplier_availability_set \
            = self._supplier_availablity_ipm.setdefault(demand_category, set())

        for ds in demand_suppliers:
            if ds.from_supplier.supplied_item_name != self.supplied_item_name:
                raise ValueError(
                    f"Supplied item '{ds.from_supplier.supplied_item_name}' does not match"
                    f" storage item '{self.supplied_item_name}'; from supplier"
                    f" '{ds.from_supplier.get_global_id()}'.")
            supplier_availability_set.add(ds)

        # A dispatch node is a pass-though node so send the DemandSupply objects on to the
        # receiver node.

        for parent in self.get_parent_consumers():
            supplies:list[DemandSupply] = []
            for demander in self._get_parent_demands(demand_category, parent):
                for_demander = [
                    ds for ds in supplier_availability_set if ds.for_consumer == demander]
                supplies.extend(for_demander)
            if supplies:
                parent.register_suppliable_rate_ipm(demand_category, self, supplies)

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

    def register_demand_with_suppliers(
        self,
        demand_category:str,
        parent_consumer:"MapConsumerNode",
        requestors:list[DemandRequest]) -> None:

        for connector in self.supplied_items:
            item_requestors = [
                r for r in requestors if r.request_item_name == connector.supplied_item_name
            ]
            if item_requestors:
                connector.register_demand_with_suppliers(
                    demand_category, parent_consumer, item_requestors)

    #---------------------------------------------------------------------------

    def register_suppliable_rate_ipm(
            self,
            demand_category:str,
            child_supplier:"MapSingleSupplyNode",
            demand_suppliers:list[DemandSupply]) -> None:

        for connector in self.supplied_items:
            if connector.supplied_item_name == child_supplier.supplied_item_name:
                connector.register_suppliable_rate_ipm(
                    demand_category, child_supplier, demand_suppliers)
                break

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

    def set_max_available_rate_ipm(
            self,
            supplier: MapSingleSupplyNode,
            request_item_name: str,
            available_rate_ipm: int) -> None:
        self._max_available_recipe_item_ipm[supplier.get_global_id()] = available_rate_ipm

    #---------------------------------------------------------------------------

    def register_target_demand_with_suppliers(self, demand_category:str) -> None:
        """
        Register this target's demand with its suppliers based on the target production rate.
        This should be called after the suppliers have been added.
        """
        for supplier in self.suppliers:
            supplier.register_demand_with_suppliers(
                demand_category,
                self,
                [DemandRequest(self, supplier.supplied_item_name, self.target_rate_ipm)])

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