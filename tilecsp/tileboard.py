from .cspbase import *


class TileBoard(CSP):
    """
    Attributes:

        dimensions:     tuple of (int, int)
        tiles:          list of Variable (of size 4)
                        each Variable, one side of tile


        (Optional)
        border_goals:   list of Variables
                        each Variable corresponds to some position on the border
                        of the board
                        e.g. goal on border : house, for a puzzle game where there exists
                         one tile whose edge contains a path that leads to the house
                         i.e. the tile's edge should align with the goal

    ==> make note of limited number of tiles

    Solution:
    Each tile is a variable, with locations and orientations,
    prune locations once placed.

    """

    def __init__(self, name, tiles):
        self.name = name
        self.tiles = tiles
        self.num_tiles = len(tiles)

    def set_tile_position(self, tile):
        pass

    def get_tile_position(self, tile):
        pass

    def get_num_tiles(self):
        pass


class Tile:

    def __init__(self, id):
        self.id = id

        