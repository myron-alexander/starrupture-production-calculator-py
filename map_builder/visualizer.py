"""
Provides capability to visualize factory layout.
"""

#---------------------------------------------------------------------------------------------------

__all__ = [
    "visualize_factory_on_a_grid"
]

#---------------------------------------------------------------------------------------------------

import json
import heapq
import math
import os
from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable

#---------------------------------------------------------------------------------------------------

class NodeType(Enum):
    Resource = 1
    Receiver = 2
    Crafter = 3
    Storage = 4
    Dispatcher = 5

#---------------------------------------------------------------------------------------------------

@dataclass
class NodeBox:
    x0: int
    y0: int
    x1: int
    y1: int
    col: int
    row: int
    type: str

#---------------------------------------------------------------------------------------------------

@dataclass
class NodeAnchors:
    north: list[tuple[int, int]]
    south: list[tuple[int, int]]
    west: list[tuple[int, int]]
    east: list[tuple[int, int]]

    def get_side(self, side:str):
        match side:
            case "north": return self.north
            case "south": return self.south
            case "east": return self.east
            case "west": return self.west
            case _: raise ValueError(f"Unknown side '{side}' for anchors.")

#---------------------------------------------------------------------------------------------------

@dataclass
class ConnectorRoute:
    source_id: str
    consumer_id: str
    supplied_item: str
    group_key: str
    source_side: str
    consumer_side: str
    start_candidates: list[tuple[int, int]]
    goal_candidates: list[tuple[int, int]]

#---------------------------------------------------------------------------------------------------

@dataclass
class RoutedConnection:
    source_id: str
    consumer_id: str
    supplied_item: str
    group_key: str
    style_idx: int
    path: list[tuple[int, int]]|None
    """
    List of (x,y) cell co-ordinates in the occupancy grid.
    """
    path_found: bool
    path_length: int

#---------------------------------------------------------------------------------------------------

class FactoryNode:
    def __init__(
            self,
            type:NodeType,
            id:str,
            definition:dict[str,Any],
            depth:int,
            terminal_idx:int) -> None:

        self.type:NodeType = type
        self.id = id
        self.definition = definition
        self.depths = [depth]
        self.terminal_idxs = [terminal_idx]
        self.inputs:list["FactoryNode"] = []
        self.owner_terminal_idx:int|None = None
        """
        When the node is used in the production chain leading up to multiple terminals, then
        a single terminal must be chosen to take ownership for display in the grid.
        """
        self.use_depth:int|None = None
        """
        When the node exists at multiple depths in the production chain, a single depth must be
        chosen for display in the grid.
        """

    @property
    def is_ingress(self) -> bool:
        return self.type == NodeType.Resource or self.type == NodeType.Receiver

    def add_child(self, child:"FactoryNode") -> None:
        if child not in self.inputs:
            self.inputs.append(child)

    def add_depth(self, depth:int) -> None:
        if depth not in self.depths:
            self.depths.append(depth)
            self.depths.sort()

    def add_terminal_idx(self, terminal_idx:int) -> None:
        if terminal_idx not in self.terminal_idxs:
            self.terminal_idxs.append(terminal_idx)
            self.terminal_idxs.sort()

    def finalize(self) -> None:
        # The depth that this node is to be displayed must always be the highest depth.
        # The list of depths is assumed to be sorted in ascending order.
        self.use_depth = self.depths[-1]

        # Take the middle value of the terminal_idxs list as the index into the terminals list
        # where the owning terminal node is located. The middle is chosen as that would distribute
        # routing of the connector lines up and down reducing overlap.
        i = 0
        num_terminals = len(self.terminal_idxs)
        if 1 < num_terminals:
            i = (num_terminals // 2) - 1
        self.owner_terminal_idx = self.terminal_idxs[i]

    def __str__(self) -> str:
        return f"({self.id}, {self.type.name}, {self.depths} ({self.use_depth}), {self.terminal_idxs} ({self.owner_terminal_idx}))"

    def __repr__(self) -> str:
        return self.__str__()

#---------------------------------------------------------------------------------------------------

class SiteData:
    def __init__(self, data:dict[str,Any], site_id:str, factory_id:str) -> None:
        self.site = data[site_id]
        self.factory = self.site["factories"][factory_id]
        self.dispatchers = self.factory.get("dispatchers", {})
        self.crafters = self.factory.get("machines", {}).get("crafters", {})
        self.storage = self.factory.get("machines", {}).get("storage", {})
        self.resources = self.site.get("resource_nodes",{})
        self.receivers = self.factory.get("receivers", {})


    @property
    def is_empty(self) -> bool:
        """
        Does the factory have no nodes on the grid?

        Returns
        -------
        bool:
            True when no nodes on the grid.

        """
        return 0 == (
            len(self.dispatchers) + len(self.crafters) + len(self.storage) + len(self.receivers)
        )


    def walk_inputs(
            self,
            terminal_idx:int,
            id:str,
            inputs:list[dict[str,Any]],
            func:Callable[[int, str, NodeType, str, dict[str, Any], int], None],
            depth:int = 1):

        for ii in inputs:
            for i in ii["from_ids"]:
                crafter = self.crafters.get(i)
                if crafter:
                    #print(f"crafter: {i}")
                    func(terminal_idx, id, NodeType.Crafter, i, crafter, depth)
                    self.walk_inputs(terminal_idx, i, crafter["inputs"], func, depth + 1)
                storage = self.storage.get(i)
                if storage:
                    #print(f"storage: {i}")
                    func(terminal_idx, id, NodeType.Storage, i, storage, depth)
                    self.walk_inputs(terminal_idx, i, storage["inputs"], func, depth + 1)
                resource = self.resources.get(i)
                if resource:
                    #print(f"resource: {i}")
                    func(terminal_idx, id, NodeType.Resource, i, resource, depth)
                receiver = self.receivers.get(i)
                if receiver:
                    #print(f"receiver: {i}")
                    func(terminal_idx, id, NodeType.Receiver, i, receiver, depth)

#---------------------------------------------------------------------------------------------------

def print_terminal_tree(
        node:FactoryNode, depth_limit:int = 101, indent:str = "", current_depth:int = 0) -> None:

    if 100 < current_depth:
        raise ValueError(f"Hit recurse limit, possible reference loop around node '{node.id}'.")
    if depth_limit < current_depth:
        return

    boxed_name = f"│ {node.id} /{node.owner_terminal_idx},{node.use_depth}/ {node.depths} {node.terminal_idxs} │"
    box_size = len(boxed_name)
    print(f"{indent}┌{'─'*(box_size-2)}┐")
    print(indent+boxed_name)
    print(f"{indent}└{'─'*(box_size-2)}┘")

    for i in node.inputs:
        print_terminal_tree(i, depth_limit, "|   " + indent, current_depth + 1)

#---------------------------------------------------------------------------------------------------

class DisplayGrid:
    """
    A sparse grid of factory nodes organized by layer where the first column in the grid is layer 0.
    Layer 0 is the outputs from the factory. Layer 1 onwards are the inputs into the prior layers
    as specified by the tree of factory nodes. The highest layer will be the inputs into the
    factory and are the starting point for the production flow.
    """

    def __init__(self) -> None:

        self.grid:list[list[FactoryNode|None]] = []
        """
        Columns of rows.

        For adding the nodes to the grid, the columns of rows layout is easier.
        For displaying the grid, the grid has to be pivoted into a rows of columns layout.
        """

        self.max_num_rows = 0
        """
        When adding a column to the grid which has had a terminal previously added, the column
        must start with empty rows to match the number of rows added by the previous terminal.
        This value is set after the terminal is added.
        """

        self.ingress_col_idx = 0
        """
        All nodes that supply items into the factory must be set at the furtherest depth. Thus
        resource and receiver nodes must all appear in a single column with no other node types.
        """


    def __get_column(self, column_idx:int) -> list[FactoryNode|None]:
        count_columns = len(self.grid)
        while count_columns < column_idx + 1:
            self.grid.append([None]*self.max_num_rows)
            count_columns = len(self.grid)
        return self.grid[column_idx]


    def __walk_terminal_tree_and_add_nodes(
            self, terminal_idx:int, node:FactoryNode, current_depth:int = 0) -> None:
        """
        Walk the tree nodes of a terminal and add them to the correct row, column.
        """
        if node.owner_terminal_idx == terminal_idx:
            if node.use_depth is not None:
                if node.is_ingress:
                    if self.ingress_col_idx < node.use_depth:
                        self.ingress_col_idx = node.use_depth
                # Not immediately moving the ingress node to the ingress column intentionally.
                # The node is currently directly adjacent the one which consumes so when moving
                # the ingress node, it will be possible to shift all the other column rows
                # down to open a clear visual path from the ingress node to the consumer.
                column = self.__get_column(node.use_depth)
                if node not in column:
                    column.append(node)
            else:
                raise ValueError(
                    f"The use_depth of node '{node.id}' should have been set by finalize.")
        for i in node.inputs:
            self.__walk_terminal_tree_and_add_nodes(terminal_idx, i, current_depth+1)


    def __ensure_columns_have_same_number_of_rows(self) -> None:
        """
        When adding a terminal to the grid, the terminal nodes must be inserted into rows below
        the nodes of existing terminals. To ensure this, all columns in the grid must have
        the same number of rows after a terminal has been added.
        """
        self.max_num_rows = max(len(c) for c in self.grid)
        for c in self.grid:
            num_rows = len(c)
            #print(f"{max_num_rows} :: {num_rows} :: {max_num_rows - num_rows}")
            if num_rows < self.max_num_rows:
                ar = [None]*(self.max_num_rows - num_rows)
                #print(ar)
                c.extend(ar)


    def __move_ingress_sources_to_last_column(self):
        """
        When multiple terminals are added to the grid, it is possible that the depth for ingress
        nodes (resources, receivers) are at different depths. Any ingress nodes that are not
        in the ingress column, must be moved to the ingress column for the same row.
        Must be run after __ensure_columns_have_same_number_of_rows.
        """
        cells_to_move = []
        if 0 < self.ingress_col_idx:
            for col_num in range(len(self.grid)):
                if col_num != self.ingress_col_idx:
                    c = self.grid[col_num]
                    for row_num in range(len(c)):
                        node = c[row_num]
                        if node is not None and node.is_ingress:
                            cells_to_move.append((col_num, row_num))

        if 0 < len(cells_to_move):
            for ctm in cells_to_move:
                node = self.grid[ctm[0]][ctm[1]]
                self.grid[self.ingress_col_idx][ctm[1]] = node
                self.grid[ctm[0]][ctm[1]] = None
                # Shift every row of columns between this one and ingress down.
                for c in range(ctm[0]+1, self.ingress_col_idx):
                    self.grid[c].insert(ctm[1], None)

            #print(f"boom: {self.max_num_rows-1}")
            #print([c for c in self.grid if c[-1] is not None])
            #print()

            # Find max populated row so that the grid can be squared off.
            max_populated_row = -1
            for c in self.grid:
                for row_num in range(len(c)-1, -1, -1):
                    if c[row_num] is not None:
                        max_populated_row = max(max_populated_row, row_num)
                        break

            self.max_num_rows = max_populated_row + 1

            # Square up the rows by ensuring that every column matches the longest populated
            # column.
            for c in self.grid:
                c[:] = c[0:self.max_num_rows]
                if len(c) < self.max_num_rows:
                    c.extend([None]*(self.max_num_rows - len(c)))


    def add_terminal_tree(self, terminals:list[FactoryNode], terminal_idx:int) -> None:
        node = terminals[terminal_idx]
        self.__walk_terminal_tree_and_add_nodes(terminal_idx, node)
        self.__ensure_columns_have_same_number_of_rows()
        self.__move_ingress_sources_to_last_column()


    def print_raw_grid(self) -> None:
        """
        Print the grid in column/row format for debugging.
        """
        print([len(c) for c in self.grid])


    def pivot_grid(self) -> list[list[FactoryNode|None]]:
        """
        Pivot the grid from columns of rows, to rows of columns.
        """
        pivoted_grid:list[list[FactoryNode|None]] = [
            [column[i] for column in self.grid] for i in range(self.max_num_rows)
        ]
        return pivoted_grid


    def print_grid(self) -> None:
        """
        Printing the grid requires pivoting the matrix from column/row to row/column matrix.
        """
        pivoted_grid = self.pivot_grid()

        display_grid:list[list[str]] = [
          ["" if n is None else n.id for n in row] for row in pivoted_grid
        ]

        column_widths = [max([1]+[len(r.id) for r in c if r is not None]) for c in self.grid]

        for r in display_grid:
            for idx, c in enumerate(r):
                print(f"| {c:<{column_widths[idx]}} ", end="")
            print("|")

#---------------------------------------------------------------------------------------------------

@dataclass
class RoutedConnections:
    connections: list[RoutedConnection]
    channel_usage: dict[tuple[int, int], int]
    channel_group_usage: dict[tuple[int, int], dict[str, int]]
    group_style_map: dict[str, int]
    overlap_penalty: int
    same_group_discount: float
    trunk_fraction: float
    num_failed: int
    num_succeeded: int

#---------------------------------------------------------------------------------------------------

class RoutingOccupancyGrid:
    """
    A grid that is made up of a subdivision of DisplayGrid for the purpose of determining
    graphical connections between nodes that are easy to follow.

    The occupancy grid size is calculated from the following values:

    - node_size_cells:         The number of cells across that are occupied by a factory node.
                               Also the number of cells down.
    - channel_size_cells:      The number of channels for use by routes. The channels occupy the
                               space between nodes and are the cells that can be populated with a
                               connection.
    - channel_padding_cells:   Margin around the node that cannot be used as a channel.
    """

    def __init__(
            self,
            node_size_cells:int,
            channel_size_cells:int,
            channel_padding_cells:int,
            dispatcher_item_map:dict[str,str]) -> None:
        """
        :param node_size_cells: The number of cells across that are occupied by a factory node.
        :type node_size_cells: int

        :param channel_size_cells: The number of channels for use by routes.
                                   Must be <= node_size_cells.
        :type channel_size_cells: int

        :param channel_padding_cells: Margin around the node that cannot be used as a channel.
        :type channel_padding_cells: int

        :param dispatcher_item_map: Provides the dispatched items for a dispatcher.
        :type dispatcher_item_map: dict[str,str]
        """

        self.node_size_cells = node_size_cells
        """
        The number of cells across that are occupied by a factory node.
        """
        self.channel_size_cells = channel_size_cells
        """
        The number of cells across that can be occupied by channels.
        """
        if self.node_size_cells < self.channel_size_cells:
            raise ValueError(
                f"channel_size_cells ({self.channel_size_cells}) must be <= node_size_cells"
                f" ({self.node_size_cells}).")

        self.channel_padding_cells = channel_padding_cells
        """
        Margin around the node that cannot be used as a channel.
        """
        self.num_cells_between_nodes = self.channel_size_cells + self.channel_padding_cells
        """
        Total number of cells between nodes including channels and padding.
        """
        self._dispatcher_item_map = dispatcher_item_map
        self.distance_to_start_of_next_node = 0
        """
        Full column width in occupancy grid cells. Includes:
          node size
          padding
          channels
        """
        self.occupancy_grid:list[list[int]] = []
        """
        Rows of columns.
        """
        self.node_boxes:dict[str, NodeBox] = {}
        self.node_anchors:dict[str, NodeAnchors] = {}
        self.node_output_items:dict[str, str] = {}
        self.node_input_items:dict[str,list[str]] = {}
        self.edges:list[tuple[str, str]] = []
        """
        List of connections from source to destination nodes.
        """
        self.routes:list[ConnectorRoute] = []

    #---------------------------------------------------------------------------

    def from_display_grid(self, display_grid:DisplayGrid) -> None:
        """
        Create an occupancy grid from the provided display grid.

        :param display_grid: Source display grid.
        :type display_grid: DisplayGrid
        """

        num_node_layers = len(display_grid.grid)
        num_node_rows = display_grid.max_num_rows

        if num_node_layers < 1:
            raise ValueError("Expected num_node_layers to be at least 1.")

        if num_node_rows < 1:
            raise ValueError("Expected num_node_rows to be at least 1.")

        # Full column width in occupancy grid cells.
        self.distance_to_start_of_next_node = \
            self.node_size_cells \
                + self.channel_padding_cells \
                + self.channel_size_cells \
                + self.channel_padding_cells

        # Width is: |node size|ch.padding|ch.size|ch.padding| * num cols-1 then |node size|
        width = (
            # Make space for every layer except the last as that one doesn't have padding.
            (num_node_layers - 1) * self.distance_to_start_of_next_node
            # Make space for the last layer.
                + self.node_size_cells
        )

        # Height is: |node size|ch.padding|ch.size|ch.padding| * num_rows-1 then |node size|
        height = (
            # Make space for every row except the last as that one doesn't have padding.
            (num_node_rows - 1) * self.distance_to_start_of_next_node
            # Make space for the last layer.
                + self.node_size_cells
        )

        # Instantiate occupancy grid with all cells set to 0 meaning unoccupied.
        self.occupancy_grid:list[list[int]] = [[0 for _ in range(width)] for _ in range(height)]

        self.__populate_node_occupancy(display_grid)
        self.__populate_edges(display_grid)
        self.__populate_routes()
        self.__populate_anchor_occupancy()

    #---------------------------------------------------------------------------

    def __populate_anchor_occupancy(self):
        """
        Anchor positions in the occupancy grid must be marked for the routing algorithm. The
        marked anchor positions will be allowed as walkable for connectors start/end points
        but not traversable.
        """
        if 0 == len(self.node_anchors):
            raise ValueError(
                "node_anchors is empty. Was __populate_node_occupancy run before "
                "__populate_anchor_occupancy?")

        for anchors in self.node_anchors.values():
            for x,y in anchors.north:
                self.occupancy_grid[y][x] = 2
            for x,y in anchors.south:
                self.occupancy_grid[y][x] = 2
            for x,y in anchors.east:
                self.occupancy_grid[y][x] = 2
            for x,y in anchors.west:
                self.occupancy_grid[y][x] = 2

    #---------------------------------------------------------------------------

    def __get_connector_pattern(self):
        """
        Generates a middle out connector pattern.

        For example with 8 connector slots left to right:
            [ 0, 1, 2, 3, 4, 5, 6, 7 ]

        middle-out looks like:
            [ 4, 3, 5, 2, 6, 1, 7, 0 ]
        """
        mid_point = int(math.ceil(self.channel_size_cells / 2.0))
        connector_pattern = [mid_point]
        for i in range(mid_point-1, -1, -1):
            connector_pattern.append(i)
            opposite = (mid_point - i) + mid_point
            if opposite < self.channel_size_cells:
                connector_pattern.append(opposite)
        return connector_pattern

    #---------------------------------------------------------------------------

    def __populate_node_occupancy(self, display_grid:DisplayGrid):

        connector_pattern = self.__get_connector_pattern()
        #print(connector_pattern)

        self.node_boxes:dict[str, NodeBox] = {}
        self.node_anchors:dict[str, NodeAnchors] = {}
        self.node_output_items:dict[str, str] = {}
        self.node_input_items:dict[str,list[str]] = {}

        # The last column and rows don't having padding cells to the right, below them.
        last_column = len(display_grid.grid) - 1
        last_row = display_grid.max_num_rows - 1

        width = len(self.occupancy_grid[0])
        height = len(self.occupancy_grid)

        for col_idx, column in enumerate(display_grid.grid):
            for row_idx, node in enumerate(column):
                if node is None:
                    continue

                # |node|pad|channels|pad|...|node|

                x0 = col_idx * self.distance_to_start_of_next_node
                y0 = row_idx * self.distance_to_start_of_next_node
                x1 = x0 + self.node_size_cells - 1
                y1 = y0 + self.node_size_cells - 1

                #print(f"{x0},{y0}->{x1+pad_x},{y1+pad_y}    {pad_x},{pad_y} {self.distance_to_start_of_next_node}")

                #
                # Mark the blocks occupied by the node and padding in the occupancy grid.
                #

                start_x = None
                start_y = None

                if 1 == len(self.occupancy_grid):
                    # Only 1 row so no padding needed.
                    start_y = 0
                    pad_y = 0

                if 1 == len(self.occupancy_grid[0]):
                    # Only 1 column so no padding needed.
                    start_x = 0
                    pad_x = 0

                if start_x is None:
                    if 0 == col_idx:
                        # Occupy padding on the right side when first column.
                        start_x = 0
                        pad_x = self.channel_padding_cells
                    elif 0 < col_idx < last_column:
                        # Occupy padding on the left and right side.
                        start_x = self.channel_padding_cells
                        pad_x = self.channel_padding_cells*2
                    else:
                        # Occupy padding on the left side when last column.
                        start_x = self.channel_padding_cells
                        pad_x = self.channel_padding_cells

                if start_y is None:
                    if 0 == row_idx:
                        # Occupy padding on the bottom side when first row.
                        start_y = 0
                        pad_y = self.channel_padding_cells
                    elif 0 < row_idx < last_row:
                        # Occupy padding on the top and bottom side.
                        start_y = self.channel_padding_cells
                        pad_y = self.channel_padding_cells*2
                    else:
                        # Occupy padding on the top side when last row.
                        start_y = self.channel_padding_cells
                        pad_y = self.channel_padding_cells

                last_x = -1
                last_y = -1
                try:
                    # Mark the node and padding cells as occupied.
                    for y in range(y0 - start_y, y0 + self.node_size_cells + pad_y - start_y ):
                        last_y = y
                        for x in range(x0 - start_x, x0 + self.node_size_cells + pad_x - start_x):
                            last_x = x
                            self.occupancy_grid[y][x] = 1
                except:
                    print(f"{last_x},{last_y} {row_idx},{col_idx} {node.id} {len(self.occupancy_grid[0]) if 0 < len(self.occupancy_grid) else "x"} {len(self.occupancy_grid)}")

                #
                # Save the occupancy grid coordinates, and output item, for the node.
                #

                self.node_boxes[node.id] = NodeBox(
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    col=col_idx,
                    row=row_idx,
                    type=node.type.name,
                )

                self.node_output_items[node.id] = self.__get_node_output_item(node)

                # Set the list of input items for each node so that the router can ensure a
                # connector on a consumer node is only receiving one item type.
                self.node_input_items[node.id] = [
                    self.__get_node_output_item(fn) for fn in node.inputs
                ]

                #
                # Create the connection points for the node.
                #
                # The anchor points must terminate in an unoccupied cell otherwise the routing
                # algorithm will assume that all anchors are occupied.
                #

                # Calculate the start position of the connector points.
                # Python integer division is a floor operation.
                connector_start_offset = (self.node_size_cells - self.channel_size_cells) // 2

                north_y = y0 - 1 - self.channel_padding_cells
                south_y = y1 + 1 + self.channel_padding_cells

                north = [
                    (x0+connector_start_offset+connector_pattern[i], north_y)
                        for i in range(0, self.channel_size_cells)
                            if 0 <= y0 - 1
                ]
                south = [
                    (x0+connector_start_offset+connector_pattern[i], south_y)
                        for i in range(0, self.channel_size_cells)
                            if (y1 + 1) < height
                ]

                west_x = x0 - 1 - self.channel_padding_cells
                east_x = x1 + 1 + self.channel_padding_cells

                west = [
                    (west_x, y0+connector_start_offset+connector_pattern[i])
                        for i in range(0, self.channel_size_cells)
                            if 0 <= x0 - 1
                ]
                east = [
                    (east_x, y0+connector_start_offset+connector_pattern[i])
                        for i in range(0, self.channel_size_cells)
                            if (x1 + 1) < width
                ]

                self.node_anchors[node.id] = NodeAnchors(
                    north=north,
                    south=south,
                    west=west,
                    east=east,
                )

    #---------------------------------------------------------------------------

    def __populate_edges(self, display_grid:DisplayGrid):
        edges:set[tuple[str, str]] = set()
        for column in display_grid.grid:
            for node in column:
                if node is None:
                    continue
                for source in node.inputs:
                    if source.id in self.node_boxes:
                        edges.add((source.id, node.id))
        self.edges = sorted(edges)

    #---------------------------------------------------------------------------

    def __populate_routes(self):

        def choose_sides(src_id:str, dst_id:str) -> tuple[str, str]:
            src_box = self.node_boxes[src_id]
            dst_box = self.node_boxes[dst_id]
            src_col = src_box.col
            dst_col = dst_box.col
            src_row = src_box.row
            dst_row = dst_box.row

            if src_col > dst_col:
                return ("west", "east")
            if src_col < dst_col:
                return ("east", "west")
            if src_row > dst_row:
                return ("north", "south")
            return ("south", "north")

        routes:list[ConnectorRoute] = []
        for source_id, consumer_id in self.edges:
            source_side, consumer_side = choose_sides(source_id, consumer_id)
            supplied_item = self.node_output_items[source_id]
            group_key = f"{source_id}::{supplied_item}"
            #group_key = f"{consumer_id}::{supplied_item}"
            #group_key = f"{supplied_item}"
            #group_key = f"{self.node_boxes[source_id].col}::{supplied_item}"
            routes.append(ConnectorRoute(
                source_id=source_id,
                consumer_id=consumer_id,
                supplied_item=supplied_item,
                group_key=group_key,
                source_side=source_side,
                consumer_side=consumer_side,
                start_candidates=self.node_anchors[source_id].get_side(source_side),
                goal_candidates=self.node_anchors[consumer_id].get_side(consumer_side),
            ))

        self.routes = routes

    #---------------------------------------------------------------------------

    def __get_node_output_item(self, node:FactoryNode) -> str:
        match node.type:
            case NodeType.Resource:
                return str(node.definition["resource_item"])
            case NodeType.Crafter:
                return str(node.definition["crafted_item"])
            case NodeType.Storage:
                return str(node.definition["stored_item"])
            case NodeType.Dispatcher:
                return str(node.definition["dipatched_item"])
            case NodeType.Receiver:
                key = f"{node.definition["site_id"]}"\
                        f";{node.definition["factory_id"]}"\
                        f";{node.definition["dispatcher_id"]}"
                dispatched_item = self._dispatcher_item_map[key]
                return dispatched_item
        return "*"

    #---------------------------------------------------------------------------

    def route_connections_a_star(
            self,
            overlap_penalty:int = 6,
            same_group_discount:float = 0.98,
            trunk_fraction:float = 0.70,
            turn_penalty:float = 2.0,
            converge_overlap_discount:float = 1.0) -> RoutedConnections:
        """
        Route all producer->consumer connections using A*.

          High-level behavior:
          1) Build route groups (same source + supplied item).
          2) Route longer links first (usually gives better global layout).
          3) For each route, run A* where movement cost is:
                    step_cost(1)
                 + overlap penalty for cells already used by other routes
                 + discounted overlap cost for routes in the same group
          4) If a group already has a "trunk" from an earlier route, try to start from that
              trunk first so related routes can bundle naturally.
          5) If trunk-start fails, retry from the original source anchors.
          6) Prefer straighter orthogonal paths by adding cost when movement direction changes.
          7) Routes converging on the same locked (consumer,item) anchor can overlap more freely.
        """
        occgrid = self.occupancy_grid
        routes = self.routes
        channel_usage:dict[tuple[int, int], int] = {}
        channel_group_usage:dict[tuple[int, int], dict[str, int]] = {}
        channel_consumer_item_usage:dict[tuple[int, int], dict[str, int]] = {}
        group_trunk_starts:dict[str, list[tuple[int, int]]] = {}
        # consumer_item_goal_anchor[(consumer_id, item)] = goal anchor (x,y)
        # Is used to lock an item to a specific anchor on the node.
        # Also used to ensure that an input endpoint will only take one item type.
        consumer_item_goal_anchor:dict[tuple[str, str], tuple[int, int]] = {}
        routed_connections:list[RoutedConnection] = []
        route_groups:dict[str, list[ConnectorRoute]] = {}

        def a_star_find_path(
                start_candidates:list[tuple[int, int]],
                goal_candidates:list[tuple[int, int]],
                usage_counts:dict[tuple[int, int], int]|None = None,
                group_usage:dict[tuple[int, int], dict[str, int]]|None = None,
            route_group_key:str|None = None,
            consumer_item_usage:dict[tuple[int, int], dict[str, int]]|None = None,
            route_consumer_item_key:str|None = None) -> list[tuple[int, int]]|None:
                # Multi-start / multi-goal A*:
                # - Any walkable start candidate can seed the search.
                # - Any walkable goal candidate can terminate it.
                # This allows anchors on node sides to act as interchangeable endpoints.
            if len(occgrid) == 0:
                return None

            usage = usage_counts or {}
            per_group_usage = group_usage or {}
            per_consumer_item_usage = consumer_item_usage or {}
            height = len(occgrid)
            width = len(occgrid[0])

            def is_walkable(point:tuple[int, int], expected:int = 0) -> bool:
                """
                Expected can be set to 2 for evaluating anchor points.
                """
                x, y = point
                if x < 0 or y < 0 or width <= x or height <= y:
                    return False
                return occgrid[y][x] == expected

            # Anchors may be invalid (outside bounds or blocked), so filter first.
            starts = [p for p in start_candidates if is_walkable(p,2)]
            goals = [p for p in goal_candidates if is_walkable(p,2)]
            if len(starts) == 0 or len(goals) == 0:
                return None

            goal_set = set(goals)

            def heuristic(point:tuple[int, int]) -> int:
                x, y = point
                # Manhattan distance to the nearest goal.
                # Admissible for 4-way movement (no diagonals), so A* remains optimal
                # for the configured movement cost model.
                return min(abs(x - gx) + abs(y - gy) for gx, gy in goal_set)

            # Direction-aware A* state: (x, y, dx, dy), where dx,dy is movement used
            # to enter this state from its parent. (0,0) means a start state.
            open_heap:list[tuple[float, int, float, int, int, int, int]] = []
            came_from:dict[tuple[int, int, int, int], tuple[int, int, int, int]] = {}
            g_score:dict[tuple[int, int, int, int], float] = {}
            turn_count:dict[tuple[int, int, int, int], int] = {}
            # g_score[state] = best known true cost from start -> state so far.
            # "Better" means LOWER cost, because cost accumulates per step and overlap.

            # Seed the frontier with all start candidates.
            for sx, sy in starts:
                start_state = (sx, sy, 0, 0)
                g_score[start_state] = 0
                turn_count[start_state] = 0
                f0 = heuristic((sx, sy))
                # f_score = g_score + heuristic estimate to goal.
                # For starts, g=0 so f starts as just the heuristic.
                heapq.heappush(open_heap, (f0, 0, 0, sx, sy, 0, 0))

            while len(open_heap) > 0:
                _, current_turns, current_g, cx, cy, cdx, cdy = heapq.heappop(open_heap)
                current_state = (cx, cy, cdx, cdy)
                current = (cx, cy)

                # First goal popped from heap is the selected path endpoint.
                if current in goal_set:
                    # Reconstruct path by walking parent pointers back to the start.
                    path = [current]
                    trace_state = current_state
                    while trace_state in came_from:
                        trace_state = came_from[trace_state]
                        path.append((trace_state[0], trace_state[1]))
                    path.reverse()
                    return path

                # Ignore stale heap entries that were superseded by a better g-score.
                if current_g != g_score.get(current_state):
                    continue
                if current_turns != turn_count.get(current_state):
                    continue

                # Expand 4-neighbor cells (left, right, up, down).
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    neighbor = (nx, ny)
                    if neighbor not in goal_set and not is_walkable(neighbor):
                        continue

                    # Existing occupancy is used as soft cost, not a hard block.
                    # This lets routes share channels when needed, but encourages
                    # A* to prefer cleaner, less congested corridors.
                    total_neighbor_usage = usage.get(neighbor, 0)
                    same_group_usage = 0
                    if route_group_key is not None:
                        same_group_usage = per_group_usage.get(neighbor, {}).get(route_group_key, 0)
                    same_consumer_item_usage = 0
                    if route_consumer_item_key is not None:
                        same_consumer_item_usage = per_consumer_item_usage.get(neighbor, {}).get(route_consumer_item_key, 0)
                    same_consumer_item_usage = max(0, same_consumer_item_usage - same_group_usage)
                    other_group_usage = max(0, total_neighbor_usage - same_group_usage - same_consumer_item_usage)

                    # Overlap from different groups is expensive.
                    # Overlap in the same group can be discounted to encourage trunk sharing.
                    same_group_cost = same_group_usage * overlap_penalty * (1.0 - same_group_discount)
                    same_consumer_item_cost = same_consumer_item_usage * overlap_penalty * (1.0 - converge_overlap_discount)
                    overlap_cost = (other_group_usage * overlap_penalty) + same_group_cost + same_consumer_item_cost

                    ndx = nx - cx
                    ndy = ny - cy
                    is_turn = (cdx, cdy) != (0, 0) and (ndx, ndy) != (cdx, cdy)
                    turn_cost = turn_penalty if is_turn else 0
                    tentative_turns = current_turns + (1 if is_turn else 0)

                    # Base step cost is 1 per move; overlap cost is additive.
                    tentative_g = current_g + 1 + overlap_cost + turn_cost
                    neighbor_state = (nx, ny, ndx, ndy)
                    known_g = g_score.get(neighbor_state)
                    known_turns = turn_count.get(neighbor_state)
                    # If this route reaches neighbor_state with a lower g_score than previously
                    # recorded, it is a better path and replaces the older parent/cost.
                    if (
                        known_g is None
                        or tentative_g < known_g
                        or (
                            tentative_g == known_g
                            and known_turns is not None
                            and tentative_turns < known_turns
                        )
                    ):
                        came_from[neighbor_state] = current_state
                        g_score[neighbor_state] = tentative_g
                        turn_count[neighbor_state] = tentative_turns
                        # A* prioritizes by lowest f_score where:
                        #   f_score = g_score (known cost so far)
                        #           + heuristic (estimated cost remaining)
                        # So the search balances "cheap so far" and "looks close to goal".
                        f_score = tentative_g + heuristic(neighbor)
                        heapq.heappush(open_heap, (f_score, tentative_turns, tentative_g, nx, ny, ndx, ndy))

            return None

        for route in routes:
            group_key = route.group_key
            route_groups.setdefault(group_key, []).append(route)

        # Deterministic style assignment per group.
        sorted_group_keys = sorted(route_groups.keys())
        group_style_map = {
            group_key: (idx % 8)
            for idx, group_key in enumerate(sorted_group_keys)
        }

        ordered_routes:list[ConnectorRoute] = []
        for group_key in sorted_group_keys:
            grouped = route_groups[group_key]

            def route_priority(route:ConnectorRoute) -> int:
                # Approximate route length using midpoint-to-midpoint Manhattan distance.
                # Longer paths routed first usually reduce dead-ends for later routes.
                start = route.start_candidates[len(route.start_candidates) // 2]
                goal = route.goal_candidates[len(route.goal_candidates) // 2]
                return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

            grouped.sort(key=route_priority, reverse=True)
            ordered_routes.extend(grouped)

        for route in ordered_routes:
            group_key = route.group_key
            has_group_trunk = group_key in group_trunk_starts
            consumer_item_key = (route.consumer_id, route.supplied_item)
            consumer_item_key_str = f"{route.consumer_id}::{route.supplied_item}"
            locked_goal_anchor = consumer_item_goal_anchor.get(consumer_item_key)
            selected_goals = [locked_goal_anchor] if locked_goal_anchor is not None else route.goal_candidates

            # MA: Check if any goal anchors are receiving an item and remove that goal if the item
            #     is not the same as the one supplied by the route.
            if locked_goal_anchor is None:
                # When locked_goal_anchor is None, it *must* mean that an anchor on the consumer
                # has not been assighed to the supplied item.
                for ii in self.node_input_items[route.consumer_id]:
                    item_anchor = \
                        consumer_item_goal_anchor.get((route.consumer_id, ii)) 
                    if item_anchor is not None:
                        if ii == route.supplied_item:
                            raise ValueError(
                                "locked_goal_anchor is None but consumer_item_goal_anchor"
                                " returned an anchor for the supplied item."
                                f" Consumer ({route.consumer_id}) supplied item ({ii}).")
                        # Remove anchor taking a different item from the selected goals.
                        selected_goals = [sg for sg in selected_goals if sg != item_anchor]

            # Path selection strategy:
            # - First route in a group uses source anchors.
            # - Later routes in the same group first try to start from the existing
            #   trunk cells (prefix of an earlier successful path) to promote bundling.
            selected_starts = group_trunk_starts[group_key] if has_group_trunk else route.start_candidates

            path = a_star_find_path(
                selected_starts,
                selected_goals,
                channel_usage,
                channel_group_usage,
                group_key,
                channel_consumer_item_usage,
                consumer_item_key_str,
            )

            # Fallback: if trunk-based search fails, retry from raw source anchors.
            if path is None and has_group_trunk:
                path = a_star_find_path(
                    route.start_candidates,
                    selected_goals,
                    channel_usage,
                    channel_group_usage,
                    group_key,
                    channel_consumer_item_usage,
                    consumer_item_key_str,
                )

            if path is not None:
                if not has_group_trunk:
                    # Store only an initial fraction of the first successful path as a
                    # reusable trunk for the group.
                    trunk_len = max(2, math.floor(len(path) * trunk_fraction))
                    group_trunk_starts[group_key] = list(dict.fromkeys(path[:trunk_len]))

                if locked_goal_anchor is None:
                    consumer_item_goal_anchor[consumer_item_key] = path[-1]

                for idx, cell in enumerate(path):
                    # Do not count route endpoints as occupied channels; only interior cells
                    # contribute congestion costs for future routes.
                    if idx != 0 and idx != len(path) - 1:
                        channel_usage[cell] = channel_usage.get(cell, 0) + 1
                        group_counts = channel_group_usage.setdefault(cell, {})
                        group_counts[group_key] = group_counts.get(group_key, 0) + 1
                        consumer_item_counts = channel_consumer_item_usage.setdefault(cell, {})
                        consumer_item_counts[consumer_item_key_str] = consumer_item_counts.get(consumer_item_key_str, 0) + 1

            routed_connections.append(RoutedConnection(
                source_id=route.source_id,
                consumer_id=route.consumer_id,
                supplied_item=route.supplied_item,
                group_key=group_key,
                style_idx=group_style_map[group_key],
                path=path,
                path_found=path is not None,
                path_length=0 if path is None else len(path)
            ))

        return RoutedConnections(
            connections=routed_connections,
            channel_usage=channel_usage,
            channel_group_usage=channel_group_usage,
            group_style_map=group_style_map,
            overlap_penalty=overlap_penalty,
            same_group_discount=same_group_discount,
            trunk_fraction=trunk_fraction,
            num_failed=len([c for c in routed_connections if c.path is None]),
            num_succeeded=len([c for c in routed_connections if c.path is not None]),
        )

    #---------------------------------------------------------------------------

    def __simplify_path(self, points:list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(points) <= 2:
            return points

        simplified = [points[0]]
        for i in range(1, len(points)-1):
            ax, ay = points[i-1]
            bx, by = points[i]
            cx, cy = points[i+1]
            if (bx - ax, by - ay) == (cx - bx, cy - by):
                continue
            simplified.append((bx, by))
        simplified.append(points[-1])
        return simplified

    #---------------------------------------------------------------------------

    def debug_print_occgrid(self, routes:list[RoutedConnection]|None = None):

        copy = [row[:] for row in self.occupancy_grid]
        #for anchors in self.node_anchors.values():
        #    keep_x = 0
        #    keep_y = 0
        #    try:
        #        for x,y in anchors.north:
        #            keep_x = x
        #            keep_y = y
        #            copy[y][x] = 2
        #        for x,y in anchors.south:
        #            keep_x = x
        #            keep_y = y
        #            copy[y][x] = 2
        #        for x,y in anchors.east:
        #            keep_x = x
        #            keep_y = y
        #            copy[y][x] = 2
        #        for x,y in anchors.west:
        #            keep_x = x
        #            keep_y = y
        #            copy[y][x] = 2
        #    except:
        #        print(f"{keep_x}, {keep_y}  {len(copy[1])}, {len(copy)} ")
        #        raise

        if routes is not None:
            for rnum, conn in enumerate(routes):
                print(f"{conn.source_id} ==> {conn.consumer_id}")
                if conn.path is not None:
                    print(f"#paths {len(conn.path)}")
                    #p = self.__simplify_path(conn.path)
                    #p = self.__simplify_path2(conn.path)
                    p = conn.path
                    for x,y in p:
                        copy[y][x] = 100+rnum
                        if conn.source_id in ['calcium-ore-4', 'r-calcium-1']:
                            print(f"{x},{y}   {copy[y][x]}")
                print(rnum)

        for row in copy:
            for value in row:
                # ◼  ◻
                s = ""
                match value:
                    case 1: s = "◼"
                    case 2: s = "●"
                    case 3: s = "◄"
                    case _:
                        if 100 <= value:
                            v = (value - 100) % 16
                            s = hex(v)[2:]
                        else:
                            s = "◻"
                print(s, end="")
            print()

    #---------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

class SvgVisualizer:

    svg_styles = """
svg {
    display: block;
}
.block-rect {
    stroke-width: 2;
}
.block-text {
    font-family: monospace;
    font-size: 11px;
    fill: #e0e0e0;
}
.block-text-title {
    font-family: monospace;
    font-size: 12px;
    font-weight: bold;
}
.connection-line-1 {
    stroke: #8c9dff;
    stroke-width: 2;
    fill: none;
}
.connection-line-2 {
    stroke: #00f5dd;
    /* stroke: #66ef84; */
    stroke-width: 2;
    fill: none;
}
.connection-line-3 {
    stroke: #efea66;
    stroke-width: 2;
    fill: none;
}
.connection-line-4 {
    stroke: #e69595;
    stroke-width: 2;
    fill: none;
}
.connection-line-5 {
    stroke: #6071d2;
    stroke-width: 2;
    fill: none;
}
.connection-line-6 {
    stroke: #37b1a5;
    stroke-width: 2;
    fill: none;
}
.connection-line-7 {
    stroke: #969331;
    stroke-width: 2;
    fill: none;
}
.connection-line-8 {
    stroke: #841818;
    stroke-width: 2;
    fill: none;
}
.connection-arrow {
    fill: #8c9dff;
}
"""

    html_styles = """
body {
    font-family: monospace;
    background: #1e1e1e;
    color: #e0e0e0;
    padding: 20px;
    margin: 0;
}
.container {
    max-width: 100%;
    margin: 0 auto;
}
.factory-header {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #4fc3f7;
}
.factory-purpose {
    font-size: 14px;
    color: #90caf9;
    margin-bottom: 30px;
    font-style: italic;
}
.visualization-wrapper {
    /*overflow: auto;*/    /* OR limit the viewable SVG width and scroll the SVG within the wrapper. */
    display: inline-block; /* OR fit the wrapper to the svg. */
    border: 1px solid #3a3a4a;
    border-radius: 4px;
    background: #2a2a2a;
}
"""

    color_map = {
        NodeType.Resource: { "bg": '#1b5e20', "border": '#4caf50', "text": '#4caf50' },
        NodeType.Receiver: { "bg": '#1a237e', "border": '#3f51b5', "text": '#3f51b5' },
        NodeType.Crafter: { "bg": '#bf360c', "border": '#ff6e40', "text": '#ff6e40' },
        NodeType.Storage: { "bg": '#455a64', "border": '#78909c', "text": '#78909c' },
        NodeType.Dispatcher: { "bg": '#663399', "border": '#ba68c8', "text": '#ba68c8' }
    }

    route_styles = [
        ("connection-line-1", "#8c9dff"),
        ("connection-line-2", "#00f5dd"),
        ("connection-line-3", "#efea66"),
        ("connection-line-4", "#e69595"),
        ("connection-line-5", "#6071d2"),
        ("connection-line-6", "#37b1a5"),
        ("connection-line-7", "#969331"),
        ("connection-line-8", "#841818")
    ]

    marker_defs = ""
    for idx, (_, color) in enumerate(route_styles):
        marker_defs += (
            f'<marker id="arrow-{idx}" markerWidth="6" markerHeight="4" '
            f'refX="0" refY="2" orient="180deg" markerUnits="strokeWidth">'
            f'<polygon points="0,0 6,2 0,4" fill="{color}"/></marker>'
        )
        marker_defs += (
            f'<marker id="starting-{idx}" markerWidth="5" markerHeight="5" '
            f'refX="2.5" refY="2.5" orient="auto" markerUnits="strokeWidth">'
            f'<circle cx="2.5" cy="2.5" r="2.5" fill="{color}"/></marker>'
        )

    # Node block dimensions.
    block_width_px = 180
    """
    Width, in pixels, to draw the factory node block.
    """
    block_height_px = 90
    """
    Height, in pixels, to draw the factory node block.
    """

    column_gap_x_px = 60
    """
    The width of the gap between node blocks in a row. The gap is where the connection lines are
    drawn.
    """
    row_gap_y_px = 60
    """
    The height of the gap between node blocks in a column. The gap is where the connection lines
    are drawn.
    """

    column_width_px:int = block_width_px + column_gap_x_px
    row_height_px:int = block_height_px + row_gap_y_px

    drawing_start_x_px = 20
    """
    Pixel co-ordinate where the start of drawing happens within the SVG viewport. The value is the
    left margin for the visualization.
    """

    drawing_start_y_px = 20
    """
    Pixel co-ordinate where the start of drawing happens within the SVG viewport. The value is the
    top margin for the visualization.
    """

    text_line_height = 14
    text_baseline_offset = 2

    #---------------------------------------------------------------------------

    def __map_cell_to_svg(
            self,
            cell_x:int,
            cell_y:int,
            occgrid:RoutingOccupancyGrid) -> tuple[float,float]:
        """
        """

        # On screen, the layout is as follows:
        #
        #            (node width)
        #         |- block width -->v
        # (node) -┌─────────────────┬─────┐ -
        # block  |│                 │     │ |
        # height |│  Factory Node   │  1  │ | row height
        #        |│                 │     │ | distance_to_start_of_next_node
        #        v│        0        │     │ |
        #        >├─────────────────┘┄┄┄┄┄│ |
        #         │                 ┊     │ |
        #         │     2           ┊  3  │ |
        #         └───────────────────────┘ v
        #
        #
        # Before determining the cell:px ratio, need to determine which rectangle the cell
        # is in. We need to do this separately for the different areas as the area of the factory
        # node block in pixels has a different ratio to the overall grid (row x column) area than
        # the one in the occupancy grid so a simple 1:n scaling cannot be done.
        #
        # I made an incorrect assumption. I believed that the routing algorithm created by the AI
        # would only select points in areas 1,2,3 but that is incorrect for the case where
        # a display grid position is not occupied by a factory node. I need to allow for points
        # in area 0 and trust in the routing algorithm to avoid populated nodes.

        cell_width_px:float = 0
        cell_height_px:float = 0

        #
        # Determine the quadrant of the cell.
        #

        column = cell_x // occgrid.distance_to_start_of_next_node
        offset_cx =  cell_x % occgrid.distance_to_start_of_next_node
        row = cell_y // occgrid.distance_to_start_of_next_node
        offset_cy = cell_y % occgrid.distance_to_start_of_next_node

        # offset + 1 for change from 0-based to 1-based to match the sizes.
        beside_block = occgrid.node_size_cells + occgrid.channel_padding_cells < (offset_cx + 1)
        below_block = occgrid.node_size_cells + occgrid.channel_padding_cells < (offset_cy + 1)

        #print(f"cell_x:{cell_x}  cell_y:{cell_y}")
        #print(f"offset_cx:{offset_cx}  offset_cy:{offset_cy}")
        #print(f"beside_block:{beside_block}  below_block:{below_block}")

        def beside_block_x() -> float:
            # The column gap includes the padding cells so the pixel size must take that into consideration.
            cell_width_px = round(self.column_gap_x_px / (occgrid.channel_size_cells + occgrid.channel_padding_cells), 1)
            channel_x = offset_cx - occgrid.node_size_cells
            point_x_px = \
                (column * self.column_width_px) + self.block_width_px + (channel_x * cell_width_px)
            return point_x_px

        def below_block_x() -> float:
            # The width of area 2 doesn't include the padding.
            cell_width_px = round(self.block_width_px / occgrid.node_size_cells, 1)
            channel_x = offset_cx
            point_x_px = \
                (column * self.column_width_px) + (channel_x * cell_width_px)
            return point_x_px

        def beside_block_y() -> float:
            # The height of area 1 doesn't include the padding.
            cell_height_px = round(self.block_height_px / occgrid.node_size_cells, 1)
            channel_y = offset_cy
            point_y_px = \
                (row * self.row_height_px) + (channel_y * cell_height_px)
            return point_y_px

        def below_block_y() -> float:
            # The row gap includes the padding cells so the pixel size must take that into consideration.
            cell_height_px = round(self.row_gap_y_px / (occgrid.channel_size_cells + occgrid.channel_padding_cells), 1)
            channel_y = offset_cy - occgrid.node_size_cells
            point_y_px = \
                (row * self.row_height_px) + self.block_height_px + (channel_y * cell_height_px)
            return point_y_px


        if beside_block and below_block:
            # Area 3
            point_x_px = beside_block_x()
            point_y_px = below_block_y()

        elif beside_block:
            # Area 1
            point_x_px = beside_block_x()
            point_y_px = beside_block_y()

        elif below_block:
            # Area 2
            point_x_px = below_block_x()
            point_y_px = below_block_y()

        else:
            # Area 0
            point_x_px = below_block_x()
            point_y_px = beside_block_y()

        #print(f"cell_width_px {cell_width_px} cell_height_px {cell_height_px}")

        return self.drawing_start_x_px + point_x_px, self.drawing_start_y_px + point_y_px


    #---------------------------------------------------------------------------

    def __simplify_path(self, points:list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        For any straight line of points, remove the points in between so only the start and
        end points of the line remain.
        """
        if len(points) <= 2:
            return points

        simplified = [points[0]]
        for i in range(1, len(points)-1):
            ax, ay = points[i-1]
            bx, by = points[i]
            cx, cy = points[i+1]
            if (bx - ax, by - ay) == (cx - bx, cy - by):
                continue
            simplified.append((bx, by))
        simplified.append(points[-1])
        return simplified

    #---------------------------------------------------------------------------

    def __convert_path_from_cells_to_pixels(
            self,
            routes:list[RoutedConnection],
            occgrid:RoutingOccupancyGrid) -> list[tuple[int,list[tuple[float,float]]]]:

        pixel_paths:list[tuple[int,list[tuple[float,float]]]] = []
        for rnum, conn in enumerate(routes):
            if conn.path is not None:
                pp = self.__simplify_path(conn.path)
                #pp = conn.path
                try:
                    pixel_paths.append(
                        (   conn.style_idx,
                            [self.__map_cell_to_svg(p[0], p[1], occgrid) for p in pp]
                        ))
                except ValueError as e:
                    print(f"Failed for node {conn.source_id}, {conn.consumer_id}")
                    print(f"{pp}")
                    print(f"{e}")
        return pixel_paths

    #---------------------------------------------------------------------------

    def __draw_connections(
            self, routes:list[RoutedConnection], occgrid:RoutingOccupancyGrid) -> str:
        """
        """
        pixel_paths = self.__convert_path_from_cells_to_pixels(routes, occgrid)

        svg_content = ""

        for pp in pixel_paths:
            points_attr = " ".join((f"{x:.1f},{y:.1f}" for x, y in pp[1]))

            style_idx = pp[0]
            css_class = self.route_styles[style_idx][0]
            marker_id = f"arrow-{style_idx}"
            starting_id = f"starting-{style_idx}"
            svg_content += (
                f'<polyline points="{points_attr}" class="{css_class}"'
                f' marker-end="url(#{marker_id})"'
                f' marker-start="url(#{starting_id})"'
                '/>'
            )

        return svg_content

    #---------------------------------------------------------------------------

    def __draw_node_details(self, text_x, text_y, row:FactoryNode) -> str:
        """
        """
        svg_content = ""

        match row.type:
            case NodeType.Resource:
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Item: {row.definition["resource_item"]}</text>'
                text_y += self.text_line_height
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Rate: {row.definition["rate_ipm"]} ipm</text>'

            case NodeType.Crafter:
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Crafts: {row.definition["crafted_item"]}</text>'
                text_y += self.text_line_height
                if 0 < len(row.inputs):
                    svg_content += \
                        f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                        f'Inputs:</text>'
                    text_y += self.text_line_height
                    for input_node in row.inputs:
                        truncated = input_node.id[:18]+"..." if 20 < len(input_node.id) else input_node.id
                        svg_content += \
                            f'<text x="{text_x + 10}" y="{text_y}" class="block-text"'\
                            f' fill="#b3e5fc">• {truncated}</text>'
                        text_y += self.text_line_height

            case NodeType.Storage:
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Stores: {row.definition["stored_item"] or "*"}</text>'

            case NodeType.Dispatcher:
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Dispatches: {row.definition["dipatched_item"]}</text>'
                text_y += self.text_line_height
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'Rate: {row.definition["output_rate_limit_ipm"]} ipm</text>'

            case NodeType.Receiver:
                site = row.definition["site_id"]
                factory = row.definition["factory_id"]
                dispatcher = row.definition["dispatcher_id"]
                from_text = f'From: {site}/{factory}'
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'{from_text}</text>'
                text_y += self.text_line_height
                svg_content += \
                    f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#b3e5fc">'\
                    f'    /{dispatcher}</text>'

        return svg_content

    #---------------------------------------------------------------------------

    def __draw_node_block(self, row_idx:int, col_idx:int, row:FactoryNode) -> str:
        """
        """
        column_start_x = col_idx * self.column_width_px + self.drawing_start_x_px
        column_start_y = row_idx * self.row_height_px + self.drawing_start_y_px
        colors = self.color_map[row.type]

        svg_content = ""

        # Draw block rectangle
        svg_content += \
            f'<rect x="{column_start_x}" y="{column_start_y}"'\
            f' width="{self.block_width_px}" height="{self.block_height_px}"'\
            f' fill="{colors["bg"]}" stroke="{colors["border"]}" class="block-rect" rx="4"/>'

        # Draw block text content
        text_x = column_start_x + 10
        text_y = column_start_y + 20

        # Block ID (title)
        svg_content += \
            f'<text x="{text_x}" y="{text_y}" class="block-text-title" fill="{colors["text"]}">'\
            f'{row.id}</text>'

        text_y += self.text_line_height

        # Type
        svg_content += \
            f'<text x="{text_x}" y="{text_y}" class="block-text" fill="#90caf9">'\
            f'{row.type.name}</text>'

        text_y += self.text_line_height

        svg_content += self.__draw_node_details(text_x, text_y, row)

        return svg_content


    #---------------------------------------------------------------------------

    def __draw_node_blocks_from_displaygrid(self, display_grid:DisplayGrid) -> str:
        """
        """
        svg_content = ""

        for col_idx, column in enumerate(display_grid.grid):
            for row_idx, row in enumerate(column):
                if row is not None:
                    svg_content += self.__draw_node_block(row_idx, col_idx, row)
        return svg_content

    #---------------------------------------------------------------------------

    def __write_html(self, svg_width:int, svg_height:int, svg_content:str):
        """
        """
        factory_id = "EYEDEE"
        purpose = ""

        sw = str(svg_width)
        sh = str(svg_height)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{factory_id} Visualization</title>
    <style>
    {self.html_styles}
    {self.svg_styles}
    </style>
</head>
<body>
    <div class="container">
        <div class="factory-header">{factory_id}</div>
        <div class="factory-purpose">{purpose}</div>
        <div class="visualization-wrapper">
            <svg width="{sw}" height="{sh}">
                <defs>{self.marker_defs}</defs>
                {svg_content}
            </svg>
        </div>
    </div>
</body>
</html>
"""
        with open("svg.html", "w") as f:
            f.write(html)

    #---------------------------------------------------------------------------

    def visualize(
            self,
            display_grid:DisplayGrid,
            routedConnections:RoutedConnections,
            routingOccupancyGrid:RoutingOccupancyGrid) -> tuple[int, int, str, str]:
        """
        Generate a SVG visualization of the display grid.

        Returns:
            - SVG width in pixels
            - SVG height in pixels
            - SVG definition
            - Styles needed by the SVG
        """

        columns = len(display_grid.grid)
        rows = display_grid.max_num_rows

        # drawing_start * 2 for both margins.
        svg_width = columns * self.column_width_px + (self.drawing_start_x_px * 2) - self.column_gap_x_px
        svg_height = rows * self.row_height_px + (self.drawing_start_y_px * 2) - self.row_gap_y_px

        svg_content = self.__draw_node_blocks_from_displaygrid(display_grid)

        svg_content += self.__draw_connections(routedConnections.connections, routingOccupancyGrid)

        #self.__write_html(svg_width, svg_height, svg_content)

        html_svg_block = f"""
<svg width="{svg_width}" height="{svg_height}">
    <defs>{self.marker_defs}</defs>
    {svg_content}
</svg>
"""
        return (svg_width, svg_height, html_svg_block, self.svg_styles)


    #---------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------

def extract_all_dispatched_items(data:dict[str, Any]):
    """
    For all the dispatchers in the loaded JSON data, get the dispatched items.
    """
    dispatcher_item_map:dict[str, str] = dict()
    for site_id, site_def in data.items():
        factories = site_def.get("factories", dict())
        for factory_id, factory_def in factories.items():
            dispatchers = factory_def.get("dispatchers", dict())
            for dispatcher_id, dispatcher_def in dispatchers.items():
                key = f"{site_id};{factory_id};{dispatcher_id}"
                dispatcher_item_map[key] = dispatcher_def["dipatched_item"]
    return dispatcher_item_map

#---------------------------------------------------------------------------------------------------

def visualize_factory_on_a_grid(
        data:dict[str, Any], site_id:str, factory_id:str) -> tuple[int, int, str, str]|None:
    """
    Generate a SVG diagram of the requested site and factory as a grid of connected factory nodes.

    Parameters
    ----------
    data : dict[str, Any]
        The data structure generated by the factory management website.

    site_id : str
        The site of the factory to visualize.

    factory_id : str
        The factory to visualize.
    
    Returns
    -------
    tuple[int, int, str, str] | None
        Generated visualization and related values as a tuple of:
            - SVG width in pixels
            - SVG height in pixels
            - SVG block
            - CSS styles needed by the SVG
        
        or None when the factory has no nodes on the grid.
    """
    dispatcher_item_map = extract_all_dispatched_items(data)

    sd = SiteData(data, site_id, factory_id)

    if sd.is_empty:
        return None

    #
    # Build terminal trees
    #

    # Build list of components that are inputs.
    is_input = set([from_ids for kv in sd.dispatchers.items() for from_ids in kv[1]["from_ids"]])
    is_input |= set([i for c in sd.crafters.items() for ii in c[1]["inputs"] for i in ii["from_ids"]])
    is_input |= set([i for c in sd.storage.items() for ii in c[1]["inputs"] for i in ii["from_ids"]])

    terminals:list[FactoryNode] = []
    nodes:list[FactoryNode] = []

    def find_node(id:str) -> FactoryNode|None:
        return next((n for n in nodes if n.id == id), None)

    def add_node_func(
            terminal_idx:int,
            current_id:str,
            input_type:NodeType,
            input_id:str,
            input_def:dict[str, Any],
            depth:int) -> None:
        # 1. Find current node
        # 2. Find input node
        # 3. Create input node if not exists and add to nodes.
        # 4. Link current nod to input node.
        current_node = find_node(current_id)
        if current_node is None:
            raise ValueError(f"Current node '{current_id}' not found.")
        input_node = find_node(input_id)
        if input_node is None:
            input_node = FactoryNode(
                input_type, input_id, input_def, depth, terminal_idx)
            nodes.append(input_node)
        else:
            input_node.add_depth(depth)
            input_node.add_terminal_idx(terminal_idx)

        current_node.add_child(input_node)

    # Sort terminals in alphabetic order within their type so that the displayed grid will show
    # them as such.

    definitions = list(sd.dispatchers.items())
    definitions.sort(key=lambda t:t[0])
    for k,v in definitions:
        #print(f"\n\nWalking dispatcher {k}:")
        terminal_idx = len(terminals)
        node = FactoryNode(NodeType.Dispatcher, k, v, 0, terminal_idx)
        terminals.append(node)
        nodes.append(node)
        sd.walk_inputs(terminal_idx, k, [v], add_node_func)

    definitions = [(k,v) for k,v in sd.crafters.items() if k not in is_input]
    definitions.sort(key=lambda t:t[0])
    for k,v in definitions:
        #print(f"\n\nWalking crafter {k}:")
        terminal_idx = len(terminals)
        node = FactoryNode(NodeType.Crafter, k, v, 0, terminal_idx)
        terminals.append(node)
        nodes.append(node)
        sd.walk_inputs(terminal_idx,k, v["inputs"], add_node_func)

    definitions = [(k,v) for k,v in sd.storage.items() if k not in is_input]
    definitions.sort(key=lambda t:t[0])
    for k,v in definitions:
        #print(f"\n\nWalking storage {k}:")
        terminal_idx = len(terminals)
        node = FactoryNode(NodeType.Storage, k, v, 0, terminal_idx)
        terminals.append(node)
        nodes.append(node)
        sd.walk_inputs(terminal_idx, k, v["inputs"], add_node_func)

    for n in nodes:
        n.finalize()

    #
    # Create display grid of factory nodes.
    #

    display_grid = DisplayGrid()
    for i in range(len(terminals)):
        display_grid.add_terminal_tree(terminals, i)

    #
    # Create connection lines between factory nodes.
    #

    # Routing presets:
    #
    # Clean separation (least overlap):
    #   overlap_penalty = 12
    #   same_group_discount = 0.75
    #   trunk_fraction = 0.45
    #   Effect: routes spread out, minimal sharing, more detours.
    #
    # Balanced (good default):
    #   overlap_penalty = 6
    #   same_group_discount = 0.90
    #   trunk_fraction = 0.65
    #   Effect: moderate bundling for related flows, still avoids heavy congestion.
    #
    # Aggressive bundling (shared trunks):
    #   overlap_penalty = 3
    #   same_group_discount = 0.98
    #   trunk_fraction = 0.80
    #   Effect: same-item routes heavily reuse corridors, compact but more overlap.
    #
    # Very shortest-path biased:
    #   overlap_penalty = 1
    #   same_group_discount = 1.00
    #   trunk_fraction = 0.90
    #   Effect: most direct paths, lots of line stacking.
    #
    # Tip: same_group_discount = 1 makes same-group overlap effectively free.
    # If you want clearer separation, lower same_group_discount first (for example 0.9)
    # before raising overlap_penalty a lot.

    overlap_penalty = 3
    same_group_discount = 1
    trunk_fraction = 0.8
    turn_penalty = 3.0
    converge_overlap_discount = 1.0

    rog = RoutingOccupancyGrid(12, 10, 2, dispatcher_item_map)
    rog.from_display_grid(display_grid)

    result = rog.route_connections_a_star(
        overlap_penalty,
        same_group_discount,
        trunk_fraction,
        turn_penalty,
        converge_overlap_discount,
    )

    print()
    print(f"A* routed {result.num_succeeded} / {len(result.connections)} connections.")
    print(
        "Routing params: "
        f"overlap_penalty={overlap_penalty}, "
        f"same_group_discount={same_group_discount}, "
        f"trunk_fraction={trunk_fraction}, "
        f"turn_penalty={turn_penalty}, "
        f"converge_overlap_discount={converge_overlap_discount}"
    )
    if 0 < result.num_failed:
        failed = [
            f"{c.source_id} -> {c.consumer_id}"
            for c in result.connections
            if not c.path_found
        ]
        print("Failed routes:")
        print("\n".join(f"  {f}" for f in failed))

    #
    # Generate visualization of the factory node display grid and connector lines as a SVG image.
    #

    svg_visualizer = SvgVisualizer()
    svg_content = svg_visualizer.visualize(display_grid, result, rog)

    return svg_content

#---------------------------------------------------------------------------------------------------

def __write_html(svg_content:str, svg_styles:str):
    """
    """
    factory_id = "EYEDEE"
    purpose = ""

    html_styles = """
body {
    font-family: monospace;
    background: #1e1e1e;
    color: #e0e0e0;
    padding: 20px;
    margin: 0;
}
.container {
    max-width: 100%;
    margin: 0 auto;
}
.factory-header {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #4fc3f7;
}
.factory-purpose {
    font-size: 14px;
    color: #90caf9;
    margin-bottom: 30px;
    font-style: italic;
}
.visualization-wrapper {
    /*overflow: auto;*/    /* OR limit the viewable SVG width and scroll the SVG within the wrapper. */
    display: inline-block; /* OR fit the wrapper to the svg. */
    border: 1px solid #3a3a4a;
    border-radius: 4px;
    background: #2a2a2a;
}
"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{factory_id} Visualization</title>
    <style>
    {html_styles}
    {svg_styles}
    </style>
</head>
<body>
    <div class="container">
        <div class="factory-header">{factory_id}</div>
        <div class="factory-purpose">{purpose}</div>
        <div class="visualization-wrapper">
            {svg_content}
        </div>
    </div>
</body>
</html>
"""
    with open("svg.html", "w") as f:
        f.write(html)


#---------------------------------------------------------------------------------------------------

def main():
    with open(f"{os.path.dirname(__file__)}/pins_data.json") as f:
        data = json.load(f)

    viz = visualize_factory_on_a_grid(data, "site-1", "inductor")

    __write_html(viz[2], viz[3])

    #print(viz)

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------------------------
