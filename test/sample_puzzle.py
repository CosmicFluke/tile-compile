import traceback

from tilecsp.tileboard import *
from search.btsearch import *
from csp.propagators import *
import time
import matplotlib.pyplot as plt
import numpy as np


def puzzle_test(num_tiles, terminal_nodes={}, dim=3):
    tiles = create_tiles(num_tiles)

    tileboard_BT = TileBoard('Simple Path Puzzle', tiles, terminal_nodes,
                             dim)
    tileboard_FC = TileBoard('Simple Path Puzzle', tiles, terminal_nodes,
                             dim)
    tileboard_GAC = TileBoard('Simple Path Puzzle', tiles, terminal_nodes,
                              dim)

    start_BT = time.time()
    solver_BT = BacktrackingSearch(tileboard_BT, 20)
    # solver_BT.bt_search(prop_BT)
    print(tileboard_BT.solution_str())
    time_BT = time.time() - start_BT

    start_FC = time.time()
    solver_FC = BacktrackingSearch(tileboard_FC, 20)
    solver_FC.bt_search(prop_fc)
    print(tileboard_FC.solution_str())
    time_FC = time.time() - start_FC
    #
    start_GAC = time.time()
    solver_GAC = BacktrackingSearch(tileboard_GAC, 20)
    solver_GAC.bt_search(prop_gac)
    print(tileboard_GAC.solution_str())
    time_GAC = time.time() - start_GAC

    print('Time to solve with backtracking: {}\n'.format(time_BT))
    print('Time to solve with forward checking: {}\n'.format(time_FC))
    print('Time to solve with GAC: {}\n'.format(time_GAC))

    ind = np.arange(3)
    width = 0.5
    time_data = [time_BT, time_FC, time_GAC]
    fig, ax = plt.subplots()
    ax.bar(ind, time_data)
    ax.set_xlabel('Backtracking algorithm')
    ax.set_title(
        'Performance of backtracking search algorithms for 3x3 Puzzle')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(('BT', 'FC', 'GAC'))
    plt.show()

    print("Finished trying to solve puzzle: Simple path\n")


def test_1_puzzle():
    print('Beginning puzzle 1: 2x2 puzzle, no terminal nodes')
    try:
        num_tiles = {CornerTile: 4}
        terminal_nodes = set()

        puzzle_test(num_tiles, terminal_nodes, 2)

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())

def test_2_puzzle():
    print('Beginning puzzle 2: 3x3 with 2 terminal nodes')

    num_tiles = {CornerTile: 4, TTile: 4, CrossTile: 1}
    # terminal_nodes = {((0, 2), W), ((2, 0), N)}
    terminal_nodes = set()
    try:
        puzzle_test(num_tiles, terminal_nodes, 3)
    except Exception:
        print("Error occurred: %r" % traceback.print_exc())


def test_3_puzzle():
    print('Beginning puzzle 3: 4x4 with four terminal nodes')
    try:

        num_tiles = {EmptyTile: 9} #For 3-3 case
        terminal_nodes = frozenset()

        puzzle_test(num_tiles, terminal_nodes, 3)

    except Exception:
        print("Error occurred: %r" % traceback.print_exc())

def test_4_puzzle():
    print('Beginning puzzle 1: 4x4 puzzle, with no terminal nodes')
    try:
        num_tiles = {CornerTile: 8, LineTile: 8}
        terminal_nodes = set()

        puzzle_test(num_tiles, terminal_nodes, 4)
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

    # test_1_puzzle()
    # test_2_puzzle()
    # test_3_puzzle()
    test_4_puzzle()
    # test_trivial_puzzle()

if __name__ == "__main__":

    main()

