#---------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
import json
from typing import Any
from application_data import GameData, load_game_data

#---------------------------------------------------------------------------------------------------

class MapNode:
    def __init__(self, global_node_id:str) -> None:
        self.id = global_node_id

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

    def add_resource_node(self, resource_node:"MapResourceNode") -> None:
        assert resource_node.id not in self.resource_nodes, \
            f"Resource node with ID '{resource_node.id}' already exists in site '{self.id}'"
        self.resource_nodes[resource_node.id] = resource_node

    #---------------------------------------------------------------------------

    def add_factory(self, factory:"MapFactory") -> None:
        assert factory.id not in self.factories, \
            f"Factory with ID '{factory.id}' already exists in site '{self.id}'"
        self.factories[factory.id] = factory

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapFactory(MapNode):
    #---------------------------------------------------------------------------

    def __init__(self, site:MapSite, factory_id:str) -> None:
        super().__init__(MapNode.id_for_factory(site.site_id, factory_id))
        self.site = site
        self.factory_id = factory_id
        self.crafters:dict[str,MapCrafterNode] = {}
        self.storages:dict[str,MapSingleStorageNode] = {}
        self.dispatchers:dict[str,MapDispatcherNode] = {}
        self.receivers:dict[str,MapReceiverNode] = {}

    #---------------------------------------------------------------------------

    def add_crafter(self, crafter:"MapCrafterNode") -> None:
        assert crafter.id not in self.crafters, \
            f"Crafter with ID '{crafter.id}' already exists in factory '{self.id}'"
        self.crafters[crafter.id] = crafter

    #---------------------------------------------------------------------------

    def add_storage(self, storage:"MapSingleStorageNode") -> None:
        assert storage.id not in self.storages, \
            f"Storage with ID '{storage.id}' already exists in factory '{self.id}'"
        self.storages[storage.id] = storage

    #---------------------------------------------------------------------------

    def add_dispatcher(self, dispatcher:"MapDispatcherNode") -> None:
        assert dispatcher.id not in self.dispatchers, \
            f"Dispatcher with ID '{dispatcher.id}' already exists in factory '{self.id}'"
        self.dispatchers[dispatcher.id] = dispatcher

    #---------------------------------------------------------------------------

    def add_receiver(self, receiver:"MapReceiverNode") -> None:
        assert receiver.id not in self.receivers, \
            f"Receiver with ID '{receiver.id}' already exists in factory '{self.id}'"
        self.receivers[receiver.id] = receiver

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapSiteNode:
    #---------------------------------------------------------------------------

    def __init__(self, site_id:str) -> None:
        self.site_id = site_id
        self.site:MapSite|None = None

    #---------------------------------------------------------------------------

    def set_site(self, site:MapSite) -> None:
        assert site.site_id == self.site_id, \
            f"Site ID '{site.id}' does not match expected site ID '{self.site_id}'"
        self.site = site

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapFactoryNode(MapSiteNode):
    #---------------------------------------------------------------------------

    def __init__(self, site_id:str, factory_id:str) -> None:
        super().__init__(site_id)
        self.factory_id = factory_id
        self.factory:MapFactory|None = None

    #---------------------------------------------------------------------------

    def set_factory(self, factory:MapFactory) -> None:
        assert factory.factory_id == self.factory_id, \
            f"Factory ID '{factory.id}' does not match expected factory ID '{self.factory_id}'"
        self.factory = factory
        self.set_site(factory.site)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapSingleSupplyNode(ABC):
    #---------------------------------------------------------------------------

    def __init__(self, supplied_item_name:str) -> None:
        self.supplied_item_name = supplied_item_name
        self.supply_ipm = 0

    #---------------------------------------------------------------------------

    @abstractmethod
    def get_id(self) -> str:
        pass

    #---------------------------------------------------------------------------

    # TODO: Add abtract method request_supplies(self, request_ipm:int) -> int:

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

class MapSupplyConnector(MapSingleSupplyNode, MapNode):
    """
    A supply connector is a node that connects a multi-item supplier to a consumer. It is used to
    provide access to only one of the possible items from a multi-item supplier.
    """
    def __init__(self, owner:"MapMultiSupplyNode", supplied_item_name:str) -> None:
        MapSingleSupplyNode.__init__(self, supplied_item_name)
        if isinstance(owner, MapNode):
            MapNode.__init__(self, owner.id)
        else:
            raise ValueError(
                f"Owner of MapSupplyConnector must be a MapNode, got {type(owner).__name__}")
        self.owner = owner
        self.suppliers:list[MapSingleSupplyNode] = []

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" supply connector item name '{self.supplied_item_name}'"
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapMultiSupplyNode:
    #---------------------------------------------------------------------------

    def __init__(self, supplied_item_names:list[str]|None) -> None:
        self.supplied_items:list[MapSupplyConnector] = []
        if supplied_item_names is not None:
            for item_name in supplied_item_names:
                self.supplied_items.append(MapSupplyConnector(self, item_name))

    #---------------------------------------------------------------------------

    def add_supplied_item(self, item_name:str) -> MapSupplyConnector:
        connector = next(
            (ii for ii in self.supplied_items if ii.supplied_item_name == item_name), None)
        if connector is None:
            connector = MapSupplyConnector(self, item_name)
            self.supplied_items.append(connector)
        return connector

    #---------------------------------------------------------------------------

    def get_item_connector(self, item_name:str) -> MapSupplyConnector:
        for supplied_item in self.supplied_items:
            if supplied_item.supplied_item_name == item_name:
                return supplied_item
        raise ValueError(f"Supplied item '{item_name}' not found in multi-supply node.")

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapProductionSupplyNode(MapSingleSupplyNode):
    def __init__(self, produced_item_name:str, recipe_production_ipm:int) -> None:
        super().__init__(produced_item_name)
        self.max_production_ipm = recipe_production_ipm

#---------------------------------------------------------------------------------------------------

class MapResourceNode(MapNode, MapSiteNode, MapProductionSupplyNode):
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

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class RecipeItem:

    #---------------------------------------------------------------------------

    def __init__(self, recipe_item_name:str, required_ipm:int) -> None:
        self.recipe_item_name = recipe_item_name
        self.required_ipm = required_ipm
        self.suppliers:list[MapSingleSupplyNode] = []

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapCrafterNode(MapNode, MapFactoryNode, MapProductionSupplyNode):

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
        self.recipe = (
            RecipeItem(recipe_item, required_ipm) for recipe_item, _, required_ipm in craft_recipe
        )
        self.building_id = building_id

    #---------------------------------------------------------------------------

    def add_recipe_item_supplier(self, recipe_item_name:str, supplier:MapSingleSupplyNode) -> None:
        for recipe_item in self.recipe:
            if recipe_item.recipe_item_name == recipe_item_name:
                recipe_item.add_supplier(supplier)
                break

    #---------------------------------------------------------------------------

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

# There is a multi-item storage building in the game. Will add support for that later when I
# have unlocked it and can see how it works.

# TODO: Handle number of stacks.
#       For now, since we are not implementing buffering, the number of stacks is not relevant.

class MapSingleStorageNode(MapNode, MapFactoryNode, MapSingleSupplyNode):

    #---------------------------------------------------------------------------

    def __init__(self,
                 site_id:str,
                 factory_id:str,
                 storage_id:str,
                 stored_item_name:str,
                 building_id:str) -> None:

        MapNode.__init__(self, MapNode.id_for_factory_node(site_id, factory_id, storage_id))
        MapFactoryNode.__init__(self, site_id, factory_id)
        MapSingleSupplyNode.__init__(self, stored_item_name)
        self.storage_id = storage_id
        self.building_id = building_id
        self.suppliers:list[MapSingleSupplyNode] = []

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" storage item name '{self.supplied_item_name}'"
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapDispatcherNode(MapNode, MapFactoryNode, MapSingleSupplyNode):

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

    #---------------------------------------------------------------------------

    def add_supplier(self, supplier:MapSingleSupplyNode) -> None:
        assert supplier.supplied_item_name == self.supplied_item_name, \
            f"Supplier item name '{supplier.supplied_item_name}' does not match" \
            f" dispatcher item name '{self.supplied_item_name}'"
        self.suppliers.append(supplier)

    #---------------------------------------------------------------------------

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapReceiverNode(MapNode, MapFactoryNode, MapMultiSupplyNode):

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
        connector = self.add_supplied_item(dispatcher.supplied_item_name)
        connector.add_supplier(dispatcher)

    #---------------------------------------------------------------------------

    def get_id(self) -> str:
        return self.id

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class MapData:
    #---------------------------------------------------------------------------

    def __init__(self) -> None:
        self.sites:dict[str,MapSite] = {}
        self.map_nodes:list[MapNode] = []

    #---------------------------------------------------------------------------

    def _add_site(self, site:MapSite) -> None:
        assert site.id not in self.sites, \
            f"Site with ID '{site.id}' already exists in map data"
        self.sites[site.id] = site

    #---------------------------------------------------------------------------

    def _add_node(self, node:MapNode) -> None:
        if isinstance(node, MapSite):
            self._add_site(node)
        elif isinstance(node, MapFactory):
            node.site.add_factory(node)
        elif isinstance(node, MapSiteNode):
            if node.site is None:
                raise ValueError(f"Site node '{node.id}' does not have an associated site")
            if isinstance(node, MapResourceNode):
                node.site.add_resource_node(node)
            elif isinstance(node, MapFactoryNode):
                if node.factory is None:
                    raise ValueError(f"Factory node '{node.id}' does not have an associated factory")
                if isinstance(node, MapCrafterNode):
                    node.factory.add_crafter(node)
                elif isinstance(node, MapSingleStorageNode):
                    node.factory.add_storage(node)
                elif isinstance(node, MapDispatcherNode):
                    node.factory.add_dispatcher(node)
                elif isinstance(node, MapReceiverNode):
                    node.factory.add_receiver(node)
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
                if node.id == map_node_id:
                    return node
        else:
            # Look for both resource nodes and factory nodes. This is necessary as the caller
            # won't know the type of node when looking up a from_id reference.
            map_factory_node_id = MapNode.id_for_factory_node(site_id, factory_id, node_id)
            map_site_node_id = MapNode.id_for_site_node(site_id, node_id)
            for node in self.map_nodes:
                if node.id in (map_factory_node_id, map_site_node_id):
                    return node
        raise ValueError(
            f"Node site '{site_id}', factory '{factory_id}', id '{node_id}' not found in map data.")

    #---------------------------------------------------------------------------

    def _get_supplier_node(
            self,
            supplied_item_name:str,
            site_id:str,
            node_id:str,
            factory_id:str|None = None) -> MapSingleSupplyNode:

        node = self._get_node_by_id(site_id, node_id, factory_id)
        if isinstance(node, MapSingleSupplyNode):
            return node
        if isinstance(node, MapMultiSupplyNode):
            return node.get_item_connector(supplied_item_name)
        raise ValueError(f"Node with ID '{node.id}' is not a supply node.")

    #---------------------------------------------------------------------------

    def set_map_data(self, map_data:dict[str, Any], game_data:GameData) -> "MapData":
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
                        raise ValueError(f"Node with ID '{node.id}' is not a MapReceiverNode.")
                    dispatchers = receiver_values["dispatchers"]
                    for dispatcher in dispatchers:
                        dispatcher_node = self._get_node_by_id(
                            dispatcher["site_id"],
                            dispatcher["dispatcher_id"],
                            dispatcher["factory_id"])
                        if not isinstance(dispatcher_node, MapDispatcherNode):
                            raise ValueError(
                                f"Dispatcher node '{dispatcher_node.id}' is not a"
                                 " MapDispatcherNode.")
                        node.add_dispatcher(dispatcher_node)

                # NOTE: When multi-storage is implemented, it must be linked here after receivers.

                machines = factory_values.get("machines", {})

                for crafter_id, crafter_values in machines.get("crafters", {}).items():
                    node = self._get_node_by_id(site_id, crafter_id, factory_id)
                    if not isinstance(node, MapCrafterNode):
                        raise ValueError(f"Node with ID '{node.id}' is not a MapCrafterNode.")
                    for input_data in crafter_values.get("inputs", []):
                        recipe_item_name = input_data["input_item"]
                        from_ids = input_data["from_ids"]
                        for from_id in from_ids:
                            #print(f"{crafter_id} / {recipe_item_name} from {from_id}")
                            supplier_node = self._get_supplier_node(
                                recipe_item_name, site_id, from_id, factory_id)
                            node.add_recipe_item_supplier(recipe_item_name, supplier_node)

                for storage_id, storage_values in machines.get("storage", {}).items():
                    node = self._get_node_by_id(site_id, storage_id, factory_id)
                    if not isinstance(node, MapSingleStorageNode):
                        raise ValueError(f"Node with ID '{node.id}' is not a MapSingleStorageNode.")
                    for input_data in storage_values.get("inputs", []):
                        from_ids = input_data["from_ids"]
                        for from_id in from_ids:
                            supplier_node = self._get_supplier_node(
                                node.supplied_item_name, site_id, from_id, factory_id)
                            node.add_supplier(supplier_node)

                for dispatcher_id, dispatcher_values \
                        in factory_values.get("dispatchers", {}).items():
                    node = self._get_node_by_id(site_id, dispatcher_id, factory_id)
                    if not isinstance(node, MapDispatcherNode):
                        raise ValueError(f"Node with ID '{node.id}' is not a MapDispatcherNode.")
                    from_ids = dispatcher_values["from_ids"]
                    for from_id in from_ids:
                        supplier_node = self._get_supplier_node(
                            node.supplied_item_name, site_id, from_id, factory_id)
                        node.add_supplier(supplier_node)

        return self

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

            for factory in site.factories.values():
                for crafter in factory.crafters.values():
                    print("-" * 40)
                    print(f"factory id        : {crafter.factory_id}")
                    print(f"crafter id        : {crafter.crafter_id}")
                    print(f"crafted item name : {crafter.supplied_item_name}")
                    print(f"production ipm    : {crafter.max_production_ipm}")
                    for recipe_item in crafter.recipe:
                        print(f"  - {recipe_item.recipe_item_name:<20}:"
                              f" {recipe_item.required_ipm} ipm")
                        for supplier in recipe_item.suppliers:
                            print(f"    from supplier: {supplier.get_id()}")

                for storage in factory.storages.values():
                    print("-" * 40)
                    print(f"factory id       : {storage.factory_id}")
                    print(f"storage id       : {storage.storage_id}")
                    print(f"stored item name : {storage.supplied_item_name}")
                    print(f"building id      : {storage.building_id}")
                    for supplier in storage.suppliers:
                        print(f"  from supplier: {supplier.get_id()}")

                for dispatched_item in factory.dispatchers.values():
                    print("-" * 40)
                    print(f"factory id        : {dispatched_item.factory_id}")
                    print(f"dispatcher id     : {dispatched_item.dispatcher_id}")
                    print(f"dispatched item   : {dispatched_item.supplied_item_name}")
                    print(f"building id       : {dispatched_item.building_id}")
                    print(f"output rate limit : {dispatched_item.output_rate_limit_ipm} ipm")
                    print(f"input rate limit  : {dispatched_item.input_rate_limit_ipm} ipm")
                    for supplier in dispatched_item.suppliers:
                        print(f"  from supplier: {supplier.get_id()}")
                
                for receiver in factory.receivers.values():
                    print("-" * 40)
                    print(f"factory id  : {receiver.factory_id}")
                    print(f"receiver id : {receiver.receiver_id}")
                    print(f"building id : {receiver.building_id}")
                    print( "dispatched items :")
                    for dispatched_item in receiver.supplied_items:
                        print(f"  - {dispatched_item.supplied_item_name} from dispatcher(s):")
                        for supplier in dispatched_item.suppliers:
                            print(f"    - {supplier.get_id()}")

    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

def main():
    with open('pins_data.json', 'r', encoding='utf-8') as f:
        map_dict_data = json.load(f)

    game_data = load_game_data()

    map_data = MapData().set_map_data(map_dict_data, game_data)

    print()
    print()
    print()
    print()
    print()
    print()
    map_data.debug_dump_nodes()


#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------