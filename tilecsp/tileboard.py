import functools

from csp.cspbase import *

ABOVE, RIGHT, BELOW, LEFT = 1, 2, 3, 4

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
        CSP.__init__(self, name, variable_grid)
        self._add_all_diff_constraint()
        self._add_adjacency_constraints(variable_grid)
        # self._add_terminal_point_constraints(terminal_points)
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
            vars = []
            for var in var_map:
                vars.append(var)
            relation = var[0].get_relation_to_neighbor(var[1])
            if relation == ABOVE:
                return var_map[var[0]].has_edge(Tile.S) == var_map[var[1]].has_edge(Tile.N)
            elif relation == RIGHT:
                return var_map[var[0]].has_edge(Tile.W) == var_map[var[1]].has_edge(Tile.E)
            elif relation == LEFT:
                return var_map[var[0]].has_edge(Tile.E) == var_map[var[1]].has_edge(Tile.W)
            else:
                return var_map[var[0]].has_edge(Tile.N) == var_map[var[1]].has_edge(Tile.S)

        var_grid_2d = self.make_2d_grid()
        for i in range(self.dimensions):
            for j in (self.dimensions - 1):
                pair_vert = set(var_grid_2d[i][j], var_grid_2d[i][j + 1])
                pair_horiz = set(var_grid_2d[j][i], var_grid_2d[j + 1][i])
                self.add_constraint(Constraint("Pair {}".format(pair_vert), pair_vert, adjacency_constraint))
                self.add_constraint(Constraint("Pair {}".format(pair_horiz), pair_horiz, adjacency_constraint))

    def _add_all_diff_constraint(self):
        # Inner function
        def all_diff(var_map):
            """
            :param var_map: Dictionary of variables mapped to assigned values
            :type var_map: dict[Variable, Tile]
            :return: True iff all tiles have unique IDs
            :rtype: bool
            """
            seen = set()
            # Uses early exit
            return not any(
                t_id in seen or seen.add(t_id)
                for t_id in map(lambda tile: tile.id, var_map.values())
            )
        self.add_constraint(
            Constraint("All-diff", self.get_all_vars(), all_diff))

    def _add_terminal_point_constraints(self, terminal_points):
        #TODO: write constraint function for perimeters
        # TODO: replace "None" arg below with correct constraint function ref

        self.add_constraint(
            Constraint('Terminal points', None)
        )

    def _add_border_constraints(self, var_grid, exit_points):
        """
        Set border constraints for all border variables.

        :param var_map: Dictionary of variables mapped to assigned values
        :type var_map: dict[Variable, Tile]
        """
        def border_constraint(var_map):
            """
            Checks whether var in var_map satisfies border constraint.

            :param var_map: Dictionary of variables mapped to assigned values
            :type var_map: dict[Variable, Tile]
            :return: True if tile doesn't have edge where it meets the outside of the board.
            :rtype: bool
            """
            dim = self.dimensions
            tile = None
            var = None
            edge_bool = [True] * 4
            # Dictionary only has one variable
            for v in var_map:
                var = v
                tile = var_map[v]
            x, y = var.get_coords
            if x == 0:
                edge_bool[0] = not tile.has_edge(Tile.W)
            if y == 0:
                edge_bool[1] = not tile.has_edge(Tile.N)
            if x == dim:
                edge_bool[2] = not tile.has_edge(Tile.E)
            if y == dim:
                edge_bool[3] = not tile.has_edge(Tile.S)
            return edge_bool[0] and edge_bool[1] and edge_bool[2] and edge_bool[3]

        def special_border_constraint(var_map):
            """
            Checks whether var in var_map satisfies special border constraint.

            :param var_map: Dictionary of variables mapped to assigned values
            :type var_map: dict[Variable, Tile]
            :return: True if tile has edge at specified exit point.
            :rtype: bool
            """
            tile = None
            var = None
            # Dictionary only has one variable
            for v in var_map:
                var = v
                tile = var_map[v]
            return tile.has_edge(var.get_exit_point())

        var_grid_2d = self.make_2d_grid()
        for i in range(self.dimensions):
            for j in range(self.dimensions):
                if i == 0 or i == self.dimensions - 1 or j == 0 or j == self.dimensions - 1:
                    self.add_constraint(Constraint("Border {}".format(var_grid_2d[i][j]), var_grid_2d[i][j],
                                                   border_constraint))
                    if (i, j) in exit_points:
                        var_grid_2d[i][j].set_exit_point(exit_points[(i, j)])
                        self.add_constraint(Constraint("Special Border {}".format(var_grid_2d[i][j]),
                                                       var_grid_2d[i][j], special_border_constraint))

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
        return [GridVariable('V' + str((i, j)), tiles, i, j, dim) for i in range(dim) for j in
                range(dim)]

    @staticmethod
    def get_adjacent_pairs(grid):
        # top-left to bottom-right BFS adjacent-pair-finding algorithm
        pairs = set()
        q = [(0, 0)]  # list of (x, y) tuples
        max_y, max_x = len(grid), len(grid[0])
        while q:
            x, y = q.pop(0)
            current_cell = grid[y][x]
            # Get successor pairs (0, 1, or 2)
            # TODO verify
            adjacent = {{current_cell, s} for s in TileBoard.get_grid_successors(x, y, max_x, max_y)}
            q.extend((pair for pair in adjacent if pair not in pairs))
            pairs.update(adjacent)
        return pairs

    @staticmethod
    def get_grid_successors(x, y, max_x, max_y):
        s = [(x + 1, y) if x < max_x else None,
             (x, y + 1) if y < max_y else None]
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
    N, E, S, W = "n", "e", "s", "w"
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
        edge_chars = map(lambda e: d[e] if e else " ",
                         map(lambda e: e in self.edges_with_roads,
                             Tile.EDGES))
        return " {}\n{}-{}\n {}".format(*edge_chars)

    @staticmethod
    def get_orientations_with_edges(tile_class, edges):
        """
        Return a tuple containing all orientations which support the given
        set of edges (specified by constants Tile.N/E/S/W).

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
        of paths (specified by pairs of the constants Tile.N/E/S/W).

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
    CONFIGURATIONS = {1: {Tile.E, Tile.S, Tile.W},
                      2: {Tile.N, Tile.S, Tile.W},
                      3: {Tile.N, Tile.E, Tile.W},
                      4: {Tile.N, Tile.E, Tile.S}}

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
    CONFIGURATIONS = {1: {Tile.N, Tile.E},
                      2: {Tile.E, Tile.S},
                      3: {Tile.S, Tile.W},
                      4: {Tile.W, Tile.N}}
    ORIENTATIONS = CONFIGURATIONS.keys()

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id, CornerTile.CONFIGURATIONS[orientation])


class LineTile(Tile):
    """
    Represents a tile with one road between opposite sides
    """
    CONFIGURATIONS = {1: {Tile.N, Tile.S},
                      2: {Tile.E, Tile.W}}
    ORIENTATIONS = CONFIGURATIONS.keys()

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id, LineTile.CONFIGURATIONS[orientation])


class BridgeCrossTile(Tile):
    CONFIGURATIONS = CrossTile.CONFIGURATIONS
    PATHS = tuple(({Tile.N, Tile.S}, {Tile.E, Tile.W}))

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id,
                         CrossTile.CONFIGURATIONS[orientation],
                         BridgeCrossTile.PATHS)


class OppositeCornersTile(Tile):
    CONFIGURATIONS = {1: set(Tile.EDGES),
                      2: set(Tile.EDGES)}
    ORIENTATIONS = CONFIGURATIONS.keys()

    PATHS = {1: tuple(({Tile.N, Tile.E}, {Tile.S, Tile.W})),
             2: tuple(({Tile.N, Tile.W}, {Tile.S, Tile.E}))}

    def __init__(self, tile_id, orientation):
        Tile.__init__(self, tile_id,
                         CrossTile.CONFIGURATIONS[orientation],
                         OppositeCornersTile.PATHS[orientation])


class GridVariable(Variable):

    def __init__(self, name, domain, x, y, bound):
        Variable.__init__(self, name, domain)
        self.x_pos = x
        self.y_pos = y
        self.exit_point = 0
        neighbors = dict()
        if y > 0:
            neighbors[ABOVE] = (x, y - 1)
        if y < bound - 1:
            neighbors[BELOW] = (x, y + 1)
        if x > 0:
            neighbors[LEFT] = (x - 1, y)
        if x < bound - 1:
            neighbors[RIGHT] = (x + 1, y)
        self.neighbors = neighbors

    def get_coords(self):
        return (self.x_pos, self.y_pos)

    def set_path_ids(self, path_ids):
        """
        TODO: write function
        """

    def get_path_id(self, dir):
        """
        Return the neighbor in the direction desired.

        :type dir: int
        """
        if dir in self.path_ids:
            return self.path_ids[dir]

    def set_exit_point(self, dir):
        self.exit_point = dir

    def get_exit_point(self):
        return self.exit_point

    def relation_to_neighbor(self, neighbor):
        """
        Return a constant representing the relation of the tile to a given neighbor tile.
        i.e. if

        :type neighbor: GridVariable
        :rtype: int
        """
        x, y = self.x_pos, self.y_pos
        n_x, n_y = neighbor.x_pos, neighbor.y_pos
        if n_x - x == 1 and n_y - y == 0:
            return RIGHT
        elif n_x - x == - 1 and n_y - y == 0:
            return LEFT
        elif n_x - x == 0 and n_y - y == 1:
            return ABOVE
        elif n_x - x == 0 and n_y - y == -1:
            return BELOW
        else:
            return None


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
