"""
API given by CSC384 Assignment 2 (Winter 2016), University of Toronto

All functions except prop_BT were implemented by Asher Minden-Webb, (C) 2016

This file will contain different constraint propagators to be used within
bt_search.

propagator == a function with the following template
    propagator(csp, newly_instantiated_variable=None)
        ==> returns (True/False, [(Variable, Value), (Variable, Value) ...])

    csp is a CSP object---the propagator can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    newly_instantiated_variable is an optional argument.
    if newly_instantiated_variable is not None:
        then newly_instantiated_variable is the most
        recently assigned variable of the search.
    else:
        propagator is called before any assignments are made
        in which case it must decide what processing to do
        prior to any variables being assigned. SEE BELOW

    The propagator returns True/False and a list of (Variable, Value) pairs.

    Returns False if a deadend has been detected by the propagator.
        in this case bt_search will backtrack
    Returns True if we can continue.

    The list of variable values pairs are all of the values
    the propagator pruned (using the variable's prune_value method).
    bt_search NEEDS to know this in order to correctly restore these
    values when it undoes a variable assignment.

    NOTE propagator SHOULD NOT prune a value that has already been
    pruned! Nor should it prune a value twice

    PROPAGATOR called with newly_instantiated_variable = None
        PROCESSING REQUIRED:
            for plain backtracking (where we only check fully instantiated
            constraints) we do nothing...return (true, [])

            for forward checking (where we only check constraints with one
            remaining variable) we look for unary constraints of the csp
            (constraints whose scope contains only one variable) and we
            forward_check these constraints.

            for gac we establish initial GAC by initializing the GAC queue with
            all constraints of the csp

    PROPAGATOR called with newly_instantiated_variable = a variable V
        PROCESSING REQUIRED:
            for plain backtracking we check all constraints with V (see csp
            method get_cons_with_var) that are fully assigned.

            for forward checking we forward check all constraints with V that
            have one unassigned variable left

            for gac we initialize the GAC queue with all constraints containing
            V.
"""

# Used for type contracts in reStructuredText docstrings
from collections.abc import Iterable, Sequence

# A2 CSP API
from csp.cspbase import *


def prop_BT(csp, new_var=None):
    """
    (Description from CSC384 A2 Starter Code)

    Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints

    :param csp: CSP instance
    :type csp: CSP
    :param new_var: Optional new variable
    :type new_var: Variable
    :return: Dead-end and list of pruned values
    :rtype: bool, list[(Variable, object)]
    """

    if not new_var:
        return True, []
    for c in csp.get_cons_with_var(new_var):
        if c.get_num_unassigned() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check():
                return False, []

    return True, []


def prop_fc(csp, new_var=None):
    """
    (Description from CSC384 A2 Starter Code)

    Do forward checking.  That is, check constraints with only one
    uninstantiated variable, and prune appropriately.  (i.e., do not prune a
    value that has already been pruned; do not prune the same value twice.)
    Return if a deadend has been detected, and return the variable/value pairs
    that have been pruned.  See beginning of this file for complete description
    of what propagator functions should take as input and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to
        access the variables and constraints.

        newVar is an optional argument.
        if newVar is not None:
            then newVar is the most recently assigned variable of the search.
            run FC on all constraints that contain newVar.
        else:
            propagator is called before any assignments are made in which case
            it must decide what processing to do prior to any variable
            assignment.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

        boolean is False if a deadend has been detected, and True otherwise.

        list is a set of variable/value pairs that are all of the values the
        propagator pruned.

    :param csp: CSP Instance
    :type csp: CSP
    :param new_var: Optional new variable
    :type new_var: Variable
    :return: False if a dead end has been detected and
        True otherwise; List of variable/value pairs which were pruned
    :rtype: bool, list[(Variable, object)]
    """
    pruned = []
    dwo = False
    constraints = \
        csp.get_cons_with_var(new_var) if new_var else csp.get_all_cons()

    # Filter accepts constraints with 1 un-instantiated variable
    # Sort constraints in increasing order of the current domain size of the
    # un-instantiated variable
    filtered_constraints = \
        sorted(
            filter(
                lambda c: c.get_num_unassigned() == 1,
                constraints),
            key=lambda c: list(c.get_unassigned_vars())[0].get_cur_domain_size()
        )
    """ :type: filter[Constraint] """

    for constraint in filtered_constraints:
        var = constraint.get_unassigned_vars().pop()
        ''' :type: Variable '''
        for value in var.get_cur_domain():
            var.assign(value)
            # Begin FCCheck
            if not constraint.check():
            # if not constraint.check(map(
            #         lambda v: v.get_assigned_value(),
            #         constraint.get_scope())):
                var.prune_value(value)
                pruned.append((var, value))
            # End FCCheck
            var.unassign()
        if var.get_cur_domain_size() == 0:
            # Domain wipe out
            return False, pruned
    return True, list(set(pruned))


class LLNode:
    """
    A node in a Linked List

    :type val: object
    :type next: LLNode
    """
    def __init__(self, val, child=None):
        self.value, self.next = val, child


class GACQueue:
    """ A GAC Queue """
    def __init__(self, init=None):
        """
        Initializes a GACQueue instance

        :param init: (Optional) An initial sequence to enqueue
        :type init: Sequence
        """
        # Initialize linked List implementation
        self._front = None
        self._end = None
        self._size = 0
        for i in (init if init else []):
            self.enqueue(i)

    def enqueue(self, constraint):
        """
        Add a Constraint to the end of the Queue

        :param constraint: Constraint to enqueue
        :type constraint: Constraint
        """
        # Append to LL
        if not self._front:
            self._front = LLNode(constraint)
            self._end = self._front
        else:
            self._end.next = LLNode(constraint)
            self._end = self._end.next
        self._size += 1

    def enqueue_all(self, constraint_sequence):
        """
        Enqueue a sequence (iterable) of Constraints, in order

        :param constraint_sequence: Ordered sequence of Constraints to enqueue
        :type constraint_sequence: Iterable[Constraint]
        """
        for c in constraint_sequence:
            self.enqueue(c)

    def dequeue(self):
        """
        Remove and return the Constraint at the front of the GACQueue

        :return: Dequeued constraint
        :rtype: Constraint
        """
        if self.is_empty():
            raise Exception("Queue is empty")
        # Remove from front of LL
        constraint = self._front.value
        self._front = self._front.next
        if self._front is None:
            self._end = None
        self._size -= 1
        return constraint

    def is_empty(self) -> bool:
        """ True iff the GACQueue is empty """
        return self._front is None

    def clear(self):
        """ Empty the contents of the GACQueue """
        del self._front, self._end
        self._front, self._end = None, None
        self._size = 0

    def __len__(self):
        return self._size

    def __bool__(self):
        return len(self) > 0

    def __contains__(self, constraint):
        cur_node = self._front
        ''' :type: LLNode '''
        while cur_node:
            if cur_node.value is constraint:
                return True
            cur_node = cur_node.next
        return False


def prop_gac(csp, new_var=None):
    """
    (Description from CSC384 A2 Starter Code)

    Do GAC propagation, as described in lecture. See beginning of this file
    for complete description of what propagator functions should take as input
    and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to access the variables
        and constraints.

        newVar is an optional argument.
        if newVar is not None:
            do GAC enforce with constraints containing newVar on the GAC queue.
        else:
            Do initial GAC enforce, processing all constraints.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

    boolean is False if a deadend has been detected, and True otherwise.

    list is a set of variable/value pairs that are all of the values the
    propagator pruned.

    :param csp: CSP Instance
    :type csp: CSP
    :param new_var: Optional new variable
    :type new_var: Variable
    :return: False if a dead end has been detected and
        True otherwise; List of variable/value pairs which were pruned
    :rtype: bool, list[(Variable, object)]
    """
    pruned = []
    constraints = \
        csp.get_cons_with_var(new_var) if new_var else csp.get_all_cons()

    # Enqueue all constraints to the GAC Queue
    # Sort constraints by number of unassigned variables (increasing)
    gac_queue = GACQueue(sorted(constraints, key=lambda c: c.get_num_unassigned()))
    # GAC Enforce
    while gac_queue:
        constraint = gac_queue.dequeue()
        # Iterate through variables, sorted by current domain size (increasing)
        for variable in sorted(constraint.get_scope(),
                               key=lambda v: v.get_cur_domain_size()):
            for value in variable.get_cur_domain():
                # Check this variable/value pair for a valid assignment for all
                # other variables in constraint's scope
                if not constraint.has_support(variable, value):
                    # No valid assignment -> Prune variable
                    variable.prune_value(value)
                    pruned.append((variable, value))
                    # Check for DWO
                    if variable.get_cur_domain_size() == 0:
                        gac_queue.clear()
                        return False, pruned
                    else:
                        # Get remaining constraints, filter out the constraints
                        # which are already in GAC Queue
                        gac_queue.enqueue_all(
                            filter(
                                lambda c: c not in gac_queue,
                                csp.get_cons_with_var(variable)
                                )
                            )
    return True, pruned


prop_GAC = prop_gac  # Aliased to comply with A2 API
prop_FC = prop_fc  # Aliased to comply with A2 API
