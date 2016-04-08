import traceback

from tilecsp.tileboard import *
from search.btsearch import *
from csp.propagators import *


def test_1_puzzle():
    print('Beginning puzzle 1: 2x2 puzzle, no terminal nodes')
    try:
        num_tiles = {CornerTile: 4}
        tiles = create_tiles(num_tiles)

        terminal_nodes = set()
        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 2)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_GAC)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())


def test_2_puzzle():

    print('Beginning puzzle 2: 3x3 no terminal nodes')
    try:
        num_tiles = {CornerTile : 4, LineTile : 3, TTile : 2}
        tiles = create_tiles(num_tiles)

        terminal_nodes = []

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 3)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_fc)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())


def test_3_puzzle():
    print('Beginning puzzle 3: 4x4 with four terminal nodes')
    try:
        num_tiles = {CornerTile: 10, LineTile: 1, TTile: 4, CrossTile: 1}
        tiles = create_tiles(num_tiles)

        terminal_nodes = frozenset({((0, 1), W), ((3, 0), N), ((0, 3), S), ((3, 2), E)})

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 4)
        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_fc)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")
    except Exception:
        print("Error occurred: %r" % traceback.print_exc())

def test_4_puzzle():
    print('Beginning puzzle 1: Simple path 2x2, with one terminal node')
    try:
        num_tiles = {CornerTile: 3, TTile: 1}
        tiles = create_tiles(num_tiles)

        terminal_nodes = {((0, 0), N)}

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 2)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_gac)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())


def test_trivial_puzzle():

    try:
        num_tiles = {CrossTile: 1}
        tiles = create_tiles(num_tiles)

        terminal_nodes = {((0, 0), N), ((0, 0), S), ((0, 0), E), ((0, 0), W)}

        tileboard = TileBoard("Simple path puzzle", tiles, terminal_nodes, 1)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_gac)
        print(tileboard.solution_str())
        print("Finished")
    except Exception:
        print("Error occurred: %r" % traceback.print_exc())

def main():

    test_1_puzzle()
    # test_2_puzzle()
    # test_3_puzzle()
    # test_4_puzzle()
    # test_trivial_puzzle()
    pass

if __name__ == "__main__":

    main()

