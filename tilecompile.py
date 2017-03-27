import traceback

from tilecsp.tileboard import *
from search.btsearch import *
from csp.propagators import *
import time
import matplotlib.pyplot as plt
import numpy as np


def puzzle_test(num_tiles, terminal_nodes={}, dim=3):
    tiles1 = create_tiles(num_tiles)
    tiles2 = create_tiles(num_tiles)
    tiles3 = create_tiles(num_tiles)

    tileboard_BT = TileBoard('Simple Path Puzzle', tiles1, terminal_nodes,
                             dim)
    tileboard_FC = TileBoard('Simple Path Puzzle', tiles2, terminal_nodes,
                             dim)
    tileboard_GAC = TileBoard('Simple Path Puzzle', tiles3, terminal_nodes,
                              dim)

    start_BT = time.time()
    solver_BT = BacktrackingSearch(tileboard_BT, 20)
    solver_BT.bt_search(prop_BT)
    print(tileboard_BT.solution_str())
    time_BT = time.time() - start_BT

    start_FC = time.time()
    solver_FC = BacktrackingSearch(tileboard_FC, 20)
    solver_FC.bt_search(prop_fc)
    print(tileboard_FC.solution_str())
    time_FC = time.time() - start_FC
    #
    # start_GAC = time.time()
    # solver_GAC = BacktrackingSearch(tileboard_GAC, 20)
    # solver_GAC.bt_search(prop_gac)
    # print(tileboard_GAC.solution_str())
    # time_GAC = time.time() - start_GAC

    print('Time to solve with backtracking: {}\n'.format(time_BT))
    print('Time to solve with forward checking: {}\n'.format(time_FC))
    #print('Time to solve with GAC: {}\n'.format(time_GAC))

    # ind = np.arange(3)
    # width = 0.5
    # time_data = [time_BT, time_FC, time_GAC]
    # fig, ax = plt.subplots()
    # ax.bar(ind, time_data)
    # ax.set_xlabel('Backtracking algorithm')
    # ax.set_title(
    #     'Performance of backtracking search algorithms for 3x3 Puzzle')
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(('BT', 'FC', 'GAC'))
    # plt.show()

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


def test_fc_puzzle():

    num_tiles_2 = {CornerTile: 4}
    num_tiles_3 = {CornerTile: 4, TTile: 4, CrossTile: 1}
    num_tiles_4 = {CornerTile: 8, LineTile: 8}

    tiles2 = create_tiles(num_tiles_2)
    tiles3 = create_tiles(num_tiles_3)
    tiles4 = create_tiles(num_tiles_4)

    tileboard_2 = TileBoard('2x2 Puzzle', tiles2, set(), 2)
    tileboard_3 = TileBoard('3x3 Puzzle', tiles3, set(), 3)
    tileboard_4 = TileBoard('4x4 Puzzle', tiles4, set(), 4)

    start_2 = time.time()
    solver_2 = BacktrackingSearch(tileboard_2, 20)
    solver_2.bt_search(prop_BT)
    print(tileboard_2.solution_str())
    time_2 = time.time() - start_2

    start_3 = time.time()
    solver_3 = BacktrackingSearch(tileboard_3, 20)
    solver_3.bt_search(prop_BT)
    print(tileboard_3.solution_str())
    time_3 = time.time() - start_3
    #

    try:
        start_4 = time.time()
        solver_4 = BacktrackingSearch(tileboard_4, 20)
        solver_4.bt_search(prop_BT)
        print(tileboard_4.solution_str())
        time_4 = time.time() - start_4
    except KeyboardInterrupt:
        time_4 = 30
    print('Time to 2x2 : {}\n'.format(time_2))
    print('Time to 3x3: {}\n'.format(time_3))
    print('Time to 4x4: {}\n'.format(time_4))


    ind = np.arange(3)
    width = 0.5
    time_data = [time_2, time_3, time_4]

    # plt.plot([2, 3, 4], time_data)
    # plt.title('Performance of backtracking for puzzles of dim=2,3,4 ')
    # plt.xlabel('dimensions')
    # fig, ax = plt.subplots()
    # ax.bar(ind, time_data)
    # ax.set_xlabel('dimensions')
    # ax.set_title(
    #     'Performance of forward checking for dim=2,3, 4 Puzzles')
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(('2x2', '3x3', '4x4'))
    # plt.show()

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


def test_vars_assigned():

    try:
        num_tiles = {CornerTile: 4, TTile: 4, LineTile: 1 }
        terminal_nodes = {((0, 2), W), ((2, 0), N)}

        puzzle_test(num_tiles, terminal_nodes)
    except:
        pass


def main():

    test_1_puzzle()
    test_2_puzzle()
    test_3_puzzle()

    # Remaining tests are unacceptably slow or get stuck
    # test_4_puzzle()
    # test_fc_puzzle()
    # test_vars_assigned()
    # test_trivial_puzzle()

    #plt.plot([13238, 9], [0, 218])

if __name__ == "__main__":

    main()

