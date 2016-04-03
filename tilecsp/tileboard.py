from csp.cspbase import *


class TileBoard(CSP):
    """
    Attributes:

        tiles:          list of Tiles, (initial domain for each variable in the board)
        dimensions:     tuple of (int, int)
        tile_positions  list of Variables, n x n sized array (n = dimensions)


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

    def __init__(self, id, orientation):
        self.id = id
        self.orientation = orientation


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
