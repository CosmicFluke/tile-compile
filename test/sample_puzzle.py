from tilecsp.tileboard import *
from search.btsearch import *
from csp.propagators import *


def test_1_puzzle():

    print('Beginning puzzle 1: Simple path, with two terminal nodes')
    try:
        num_tiles = {CornerTile : 2, LineTile : 3, Tile : 4}
        tiles = create_tiles(num_tiles)

        # TODO: terminal node representation
        terminal_nodes = []

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 3)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_BT)

        print(tileboard.solution_str())
    except Exception:
        print("Error occurred: %r" % traceback.print_exc())
    finally:
        print("Finished solving puzzle: Simple path\n")


def test_2_puzzle():

    print('Beginning puzzle 1: Simple path, with two terminal nodes')
    try:
        num_tiles = {CornerTile : 4, LineTile : 3, TTile : 2}
        tiles = create_tiles(num_tiles)

        # TODO: terminal node representation
        terminal_nodes = []

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 3)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_fc)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())


def test_3_puzzle():
    print('Beginning puzzle 1: Simple path, with no terminal nodes')
    try:
        num_tiles = {CornerTile: 2, LineTile: 4, TTile: 2, EmptyTile: 1}
        tiles = create_tiles(num_tiles)

        # TODO: terminal node representation
        terminal_nodes = frozenset({((2, 2), S), ((0, 2), S)})

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 3)
        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_fc)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")
    except Exception:
        print("Error occurred: %r" % traceback.print_exc())

def test_4_puzzle():
    print('Beginning puzzle 1: Simple path, with no terminal nodes')
    try:
        num_tiles = {CornerTile: 3, TTile: 1}
        tiles = create_tiles(num_tiles)

        # TODO: terminal node representation
        terminal_nodes = {(frozenset({1, 1}), N)}

        tileboard = TileBoard('Simple Path Puzzle', tiles, terminal_nodes, 2)

        solver = BacktrackingSearch(tileboard, 20)
        solver.bt_search(prop_fc)

        print(tileboard.solution_str())
        print("Finished trying to solve puzzle: Simple path\n")

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())



def main():

    #test_1_puzzle()
    #test_2_puzzle()
    test_3_puzzle()
    # test_4_puzzle()

if __name__ == "__main__":

    main()

