import functools

from csp.cspbase import *

# Tile edge constants
N, E, S, W = "n", "e", "s", "w"

# Tile relations (a ABOVE b, ...)
ABOVE, RIGHT, BELOW, LEFT = 1, 2, 3, 4

# Mapping of tile relations to corresponding edges
CORRESPONDING_EDGES = {ABOVE: (S, N),
                       RIGHT: (W, E),
                       BELOW: (N, S),
                       LEFT: (E, W)}


class TileBoard(CSP):
    """
    Attributes:

        tiles:          list of Tiles, (initial domain for each variable in the
                        board)
        dimensions:     tuple of (int, int)
        vars:           list of Variables, n x n sized array (n = dimensions)


        (Optional)
        border_goals:   list of Variables
                        each Variable corresponds to some position on the border
                        of the board
                        e.g. goal on border : house, for a puzzle game where
                        there exists one tile whose edge contains a path that
                        leads to the house
                        i.e. the tile's edge should align with the goal
    """

    def __init__(self, name, tiles, exit_points, dim=3):
        self.name = name
        self.tiles = tiles
        self.dimensions = dim
        variable_grid = TileBoard.create_board(self.dimensions, self.tiles)
        CSP.__init__(self, name, itertools.chain(*variable_grid))
        self._add_all_diff_constraint()
        self._add_adjacency_constraints(variable_grid)
        self._add_border_constraints(variable_grid, exit_points)

    def _add_adjacency_constraints(self, var_grid):
        """
        Adds all adjacency constraints over variables in var_grid

        :param var_map: Dictionary of variables mapped to assigned values
        :type var_map: dict[Variable, Tile]
        """        
        def adjacency_constraint(var_map):
            """
            Adds adjacency constraint between variables in var_map

            :param var_map: Dictionary of variables mapped to assigned values
            :type var_map: dict[Variable, Tile]
            :return: True if both variables have edges that connect to each other
            :rtype: bool
            """
            # If var_map has > 2 entries, something is wrong with the constraint
            assert len(var_map) == 2
            var1, var2 = var_map.items()
            edges = CORRESPONDING_EDGES[var1[0].relation_to_neighbor(var2[0])]
            return var1[1].has_edge(edges[0]) == var2[1].has_edge(edges[1])

        for pair in TileBoard.get_adjacent_pairs(var_grid):
            self.add_constraint(
                Constraint("Pair {}".format(pair), 
                           pair, 
                           adjacency_constraint))

    def _add_all_diff_constraint(self):
        """ Adds the all-diff constraint over all variables """
        # Inner function
        def all_diff(var_map):
            """ True iff all tiles have unique IDs """
            seen = set()
            # Uses early exit (lazy eval)
            return not any(
                t_id in seen or seen.add(t_id)
                for t_id in map(lambda tile: tile.id, var_map.values())
            )

        self.add_constraint(
            Constraint("All-diff", self.get_all_vars(), all_diff))

    def _add_border_constraints(self, var_grid, exit_points):
        """
        Set border constraints for all border variables.

        :param var_map: Dictionary of variables mapped to assigned values
        :type var_map: dict[Variable, Tile]
        """
        def border_constraint_fn(var_map, border_edge, terminal=False):
            """
            Checks whether var in var_map satisfies border constraint.

            :param var_map: Dictionary of variables mapped to assigned values
            :type var_map: dict[Variable, Tile]
            :param border_edge: The edge that touches the border
            :param terminal: True iff this constraint is a terminal variable
            :return: True iff tile doesn't have edge where it meets the outside
                of the board.
            :rtype: bool
            """
            var, tile = list(var_map.items())[0]
            has_edge = tile.has_edge(border_edge)
            return not has_edge if terminal else has_edge

        def make_constraint(var, edge, is_terminal):
            return Constraint(
                "Border {}".format(var),
                frozenset({var}),
                functools.partial(border_constraint_fn,
                                  border_edge=edge,
                                  terminal=is_terminal))

        top_row = var_grid[0]
        bottom_row = var_grid[-1]
        left_column = (row[0] for row in var_grid)
        right_column = (row[-1] for row in var_grid)
        border_vars = itertools.chain(
            map(lambda v: (v, N, N in v.terminal_edges), top_row),
            map(lambda v: (v, W, W in v.terminal_edges), left_column),
            map(lambda v: (v, E, E in v.terminal_edges), right_column),
            map(lambda v: (v, S, S in v.terminal_edges), bottom_row))
        for v_data in border_vars:
            self.add_constraint(make_constraint(*v_data))

    def set_tile_position(self, tile):
        pass

    def get_tile_position(self, tile):
        pass

    def get_total_num_tiles(self):
        return len(self.tiles)

    def get_num_tiles_left(self):
        pass

    @staticmethod
    def create_board(dim, tiles):
        """
        :param dim: dimensions of board
        :type dim: int
        :param tiles:  list of Tiles (initial domain for each variable in
            board)
        :type tiles: list[Tile]

        :return: n x n matrix, each element is a Variable with initial domain
            being the tiles array
        :rtype: list[list[Variable]]
        """
        tiles = set(tiles)

        def make_grid_variable(m, n, size):
            return GridVariable('V{}'.format((m, n)), tiles, m, n, size)

        return [[make_grid_variable(i, j, dim) for i in range(dim)] for j in
                range(dim)]

    @staticmethod
    def get_adjacent_pairs(grid):
        # top-left to bottom-right BFS adjacent-pair-finding algorithm
        pairs = set()
        q = [(0, 0)]  # list of (x, y) tuples
        max_y, max_x = len(grid), len(grid[0])
        while q:

            x, y = q.pop(0)
            current_cell = grid[x][y]
            # Get successor pairs (0, 1, or 2)
            # TODO verify

            adjacent = [tuple((current_cell, s)) for s in TileBoard.get_grid_successors(x, y, max_x, max_y) if s is not None]
            q.extend((pair[1] for pair in adjacent if pair not in pairs))
            adjacent = {tuple((current_cell, grid[s[0]][s[1]])) for current_cell, s in adjacent}
            pairs.update(adjacent)
        pairs = {frozenset((pair)) for pair in pairs}
        return pairs
        #     adjacent = {tuple((current_cell, s)) for s in TileBoard.get_grid_successors(x, y, max_x, max_y) if s is not None}
        #     q.extend((pair[1] for pair in adjacent if pair not in pairs))
        #     pairs.update(adjacent)
        # new_pairs = set()
        # for pair in pairs:
        #     new_pairs.add(frozenset((pair[0], grid[pair[1][0]][pair[1][1]])))
        # return new_pairs

    @staticmethod
    def get_grid_successors(x, y, max_x, max_y):
        s = [(x + 1, y) if x + 1 < max_x else None,
             (x, y + 1) if y + 1 < max_y else None]
        return s

    def make_2d_grid(self, var_grid):
        var_grid_2d = [[] for i in range(self.dimensions)]
        for i in range(self.dimensions):
            for j in range(self.dimensions):
                var_grid_2d[i].append(var_grid[i * self.dimensions + j])
        return var_grid_2d



class Tile:
    """
    Class representing a game tile (tile_board variable domain value)
    """
    # Edge constants
    EDGES = (N, E, S, W)
    # Generic configurations
    CONFIGURATIONS = {1: set()}
    ORIENTATIONS = CONFIGURATIONS.keys()
    PATHS = None

    def __init__(self, tile_id, edges=set(), paths=None):
        self.id = tile_id
        self.edges_with_roads = edges
        # Default to paths between all edges unless otherwise specified
        self.paths = paths if paths is not None else \
            set(itertools.combinations(edges, 2))

    def get_edges(self):
        """
        :return: Set containing all road-edges on this tile
        :rtype: set[str]
        """
        return set(self.edges_with_roads)

    def has_edge(self, e):
        """
        :param e: Edge to check on this tile
        :return: True iff this tile has a road on edge e.
        :rtype: bool
        """
        return e in self.edges_with_roads

    def paths_from(self, e):
        """
        :param e: Starting edge
        :return: All edges on this tile that can be reached from edge e.
        :rtype: set[str]
        """
        return set(
            itertools.chain(
                *map(
                    lambda p: p.difference({e}),
                    {p for p in self.paths if e in p}
                )
            )
        )

    def has_path(self, e1, e2):
        """
        Check for a path on this tile between edge e1 and edge e2
        :type e1: str
        :type e2: str
        :return: True iff this tile has a road between edges e1 and e2.
        :rtype: bool
        """
        return {e1, e2} in self.paths

    def __str__(self):
        d = dict(zip(Tile.EDGES, ("|", "-", "|", "-")))
        # edge_chars = map(lambda e: d[e] if e else " ",
        #                  map(lambda e: e in self.edges_with_roads,
        #                      Tile.EDGES))
        # return " {}\n{}-{}\n {}".format(*edge_chars)
        return self.id

    @staticmethod
    def get_orientations_with_edges(tile_class, edges):
        """
        Return a tuple containing all orientations which support the given
        set of edges (specified by constants N/E/S/W).

        :type tile_class: Tile
        :type edges: set[str]
        :rtype: set[int]
        """
        return {o for o in tile_class.CONFIGURATIONS
                if all((e in tile_class.CONFIGURATIONS[o] for e in edges))}

    @staticmethod
    def get_orientations_with_paths(tile_class, paths):
        """
        Return a tuple containing all orientations which support the given set
        of paths (specified by pairs of the constants N/E/S/W).

        :type tile_class: Tile
        :type paths: set[str]
        :rtype: set[int]
        """
        if not tile_class.PATHS:
            return Tile.get_orientations_with_edges(
                tile_class, set(itertools.chain(*paths)))
        return {o for o in tile_class.PATHS
                if all((p in tile_class.PATHS[o] for p in paths))}


class TTile(Tile):
    """
    Represents a tile with a T-shaped road connecting 3 edges
    """
    CONFIGURATIONS = {1: {E, S, W},
                      2: {N, S, W},
                      3: {N, E, W},
                      4: {N, E, S}}

    ORIENTATIONS = CONFIGURATIONS.keys()

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id, TTile.CONFIGURATIONS[orientation])


class CrossTile(Tile):
    """
    Represents a tile with crossroads connecting all four edges
    """
    CONFIGURATIONS = {1: set(Tile.EDGES)}

    def __init__(self, tile_id, orientation=1):
        Tile.__init__(self, tile_id, set(Tile.EDGES))

    # staticmethod get_orientations_for_edges(edges) is same as superclass


class CornerTile(Tile):
    """
    Represents a tile with one road between adjacent edges
    """
    CONFIGURATIONS = {1: {N, E},
                      2: {E, S},
                      3: {S, W},
                      4: {W, N}}
    ORIENTATIONS = CONFIGURATIONS.keys()

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id, CornerTile.CONFIGURATIONS[orientation])


class LineTile(Tile):
    """
    Represents a tile with one road between opposite sides
    """
    CONFIGURATIONS = {1: {N, S},
                      2: {E, W}}
    ORIENTATIONS = CONFIGURATIONS.keys()

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id, LineTile.CONFIGURATIONS[orientation])


class BridgeCrossTile(Tile):
    CONFIGURATIONS = CrossTile.CONFIGURATIONS

    PATHS = {frozenset({N, S}), frozenset({E, W})}

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id,
                         CrossTile.CONFIGURATIONS[orientation],
                         BridgeCrossTile.PATHS)


class OppositeCornersTile(Tile):
    CONFIGURATIONS = {1: set(Tile.EDGES),
                      2: set(Tile.EDGES)}
    ORIENTATIONS = CONFIGURATIONS.keys()

    PATHS = {1: {frozenset({N, E}), frozenset({S, W})},
             2: {frozenset({N, W}), frozenset({S, E})}}

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id,
                         CrossTile.CONFIGURATIONS[orientation],
                         OppositeCornersTile.PATHS[orientation])


class GridVariable(Variable):

    def __init__(self, name, domain, x, y, bound):
        Variable.__init__(self, name, domain)
        self.x_pos = x
        self.y_pos = y
        self.terminal_edges = frozenset()

    def get_coords(self):
        return self.x_pos, self.y_pos

    def set_path_ids(self, path_ids):
        """
        (What does it do?)
        """
        # TODO: Implement
        raise NotImplementedError

    def get_path_id(self, dir):
        """
        Return the neighbor in the direction desired.

        :type dir: int
        """
        # TODO: where is path_ids defined?
        if dir in self.path_ids:
            return self.path_ids[dir]

    def get_exit_point(self):
        return self.terminal_edges

    def relation_to_neighbor(self, neighbor):
        """
        Return a constant representing the relation of the tile to a given neighbor tile.
        i.e. if
        Precondition: neighbour *must* be a neighbour of self

        :type neighbor: GridVariable
        :rtype: int
        """
        x, y = self.x_pos, self.y_pos
        n_x, n_y = neighbor.x_pos, neighbor.y_pos
        diff_to_relation = {(1, 0): RIGHT,
                            (-1, 0): LEFT,
                            (0, 1): ABOVE,
                            (0, -1): BELOW}
        return diff_to_relation[(n_x - x, n_y - y)]


def create_tiles(num_tiles):
    """
    IN:
        num_tiles: dictionary { Subclass of Tile : number of said tiles}

    OUT:
        list of Tiles
    """
    tiles = []

    count = 0
    for tile_type in num_tiles:
        for i in range(num_tiles[tile_type]):
            id_name = 'id' + '-' + str(count)
            for orientation in tile_type.ORIENTATIONS:
                value = tile_type(id_name, orientation)
                tiles.append(value)
            count += 1

    return tiles
