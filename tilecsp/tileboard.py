from .cspbase import *


class TileBoard(CSP):
    """
    Attributes:

<<<<<<< HEAD
        tiles:          list of Tiles, (initial domain for each variable in the board)
        dimensions:     tuple of (int, int)
        tile_positions  list of Variables, n x n sized array (n = dimensions)
=======
        dimensions:     tuple of (int, int)
        tiles:          list of Variable (of size 4)
                        each Variable, one side of tile
>>>>>>> efd6b75bc14bbb49b2051110ae871df86a3c4f50


        (Optional)
        border_goals:   list of Variables
                        each Variable corresponds to some position on the border
                        of the board
                        e.g. goal on border : house, for a puzzle game where there exists
                         one tile whose edge contains a path that leads to the house
                         i.e. the tile's edge should align with the goal

<<<<<<< HEAD
    """

    def __init__(self, name, tiles, dim=3):
        self.name = name
        self.tiles = tiles
        self.dimensions = dim
        tile_positions = create_board(self.dimensions, self.tiles)
        CSP.__init__(self, name, tile_positions)
=======
    ==> make note of limited number of tiles

    Solution:
    Each tile is a variable, with locations and orientations,
    prune locations once placed. 

    """

    def __init__(self, name, tiles):
        self.name = name
        self.tiles = tiles
        self.num_tiles = len(tiles)
>>>>>>> efd6b75bc14bbb49b2051110ae871df86a3c4f50

    def set_tile_position(self, tile):
        pass

    def get_tile_position(self, tile):
        pass

<<<<<<< HEAD
    def get_total_num_tiles(self):
        return len(self.tiles)

    def get_num_tiles_left(self):
=======
    def get_num_tiles(self):
>>>>>>> efd6b75bc14bbb49b2051110ae871df86a3c4f50
        pass


class Tile:

<<<<<<< HEAD
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
=======
    def __init__(self, id):
        self.id = id

        
>>>>>>> efd6b75bc14bbb49b2051110ae871df86a3c4f50
