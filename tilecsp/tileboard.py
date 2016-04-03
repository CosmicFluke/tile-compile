from csp.cspbase import *


class TileBoard(CSP):
    """
    Attributes:

        tiles:          list of Tiles, (initial domain for each variable in the board)
        dimensions:     tuple of (int, int)
        vars:           list of Variables, n x n sized array (n = dimensions)


        (Optional)
        border_goals:   list of Variables
                        each Variable corresponds to some position on the border
                        of the board
                        e.g. goal on border : house, for a puzzle game where there exists
                         one tile whose edge contains a path that leads to the house
                         i.e. the tile's edge should align with the goal
    """

    def __init__(self, name, tiles, dim=3):
        self.name = name
        self.tiles = tiles
        self.dimensions = dim
        tile_positions = create_board(self.dimensions, self.tiles)
        CSP.__init__(self, name, tile_positions)

    def set_tile_position(self, tile):
        pass

    def get_tile_position(self, tile):
        pass

    def get_total_num_tiles(self):
        return len(self.tiles)

    def get_num_tiles_left(self):
        pass


class Tile:

    def __init__(self, id):
        self.id = id


class TTile(Tile):

    EDGES = (1, 2, 3, 4)
    ORIENTATIONS = ("n", "e", "s", "w")
    _EDGE_VALUES = (False, True, True, True), \
                   (True, False, True, True), \
                   (True, True, False, True), \
                   (True, True, True, False)

    MAPPINGS = dict(
        zip(
            EDGES,
            map(
                lambda tup: dict(zip(TTile.ORIENTATIONS, tup)),
                _EDGE_VALUES)
        )
    )

    def __init__(self, id, orientation):
        Tile.__init__(id)
        self.edges = TTile.MAPPINGS[orientation]


class CrossTile(Tile):

    EDGES = (1)
    ORIENTATIONS = ("n", "e", "s", "w")
    _EDGE_VALUES = (True, True, True, True)

    MAPPINGS = dict(
        zip(
            EDGES,
            map(
                lambda tup: dict(zip(TTile.ORIENTATIONS, tup)),
                _EDGE_VALUES)
        )
    )

    def __init__(self, id, orientation):
        Tile.__init__(id)
        self.edges = CrossTile.MAPPINGS[orientation]

class CornerTile(Tile):
    EDGES = (1, 2, 3, 4)
    ORIENTATIONS = ("n", "e", "s", "w")
    _EDGE_VALUES = (True, True, False, False), \
                   (False, True, True, False), \
                   (False, False, True, True), \
                   (True, False, False, True)
    MAPPINGS = dict(
        zip(
            EDGES,
            map(
                lambda tup: dict(zip(TTile.ORIENTATIONS, tup)),
                _EDGE_VALUES)
        )
    )

    def __init__(self, id, orientation):
        Tile.__init__(id)
        self.edges = CornerTile.MAPPINGS[orientation]


class LineTile(Tile):
    EDGES = (1, 2)
    ORIENTATIONS = ("n", "e", "s", "w")
    _EDGE_VALUES = (False, True, False, True), \
                   (True, False, True, False)
    MAPPINGS = dict(
        zip(
            EDGES,
            map(
                lambda tup: dict(zip(TTile.ORIENTATIONS, tup)),
                _EDGE_VALUES)
        )
    )

    def __init__(self, id, orientation):
        Tile.__init__(id)
        self.edges = LineTile.MAPPINGS[orientation]


def create_tiles(num_tiles):
    '''
    IN:
        num_tiles: dictionary { Subclass of Tile : number of said tiles}

    OUT:
        list of Tiles
    '''
    tiles = []

    count = 0
    for tile in num_tiles.keys():
        for i in range(num_tiles[tile]):
            id = 'id' + '-' + str(count)
            for orientation in tile.ORIENTATIONS:

                value = tile(id, orientation)
                tiles.append(value)
            count += 1

    return tiles


def create_board(dim, tiles):
    '''
    IN:
        dim: dimensions of board
        tiles:  list of Tiles (initial domain for each variable in board

    OUT:
        n x n matrix, each element is a Variable with initial domain
        being the tiles array
    '''

    return [Variable('V' + str((i, j)), tiles) for i in range(dim) for j in range(dim)]

