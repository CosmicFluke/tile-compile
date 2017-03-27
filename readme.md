# tile-compile

CREATED BY
* Asher Minden-Webb
* Kathy Ge
* Amit Kadan

Creates a Constraint Satisfaction Problem model of a children's tile-placing game, and runs a backtracking search algorithm to attempt to solve it.  Works for most 3x3 puzzles using a forward checking propagation algorithm. GAC propagation is too slow on puzzles larger than 2x2 due to massive branching (requires further optimization).

Uses elements of source code from CSC384 Assignment 2 Starter Code (University of Toronto, Department of Computer Science), which formed the basis for the `btsearch` module.

Dependencies (not currently utilized):
 - numpy
 - matplotlib

 To run:
 ```
 python3 ./tilecompile.py
 ```
