"""
Constraint Satisfaction Routines
   A) class Variable

      This class allows one to define CSP variables.

      On initialization the variable object can be given a name, and
      an original domain of values. This list of domain values can be
      added but NOT deleted from.
      
      To support constraint propagation, the class also maintains a
      set of flags to indicate if a value is still in its current domain.
      So one can remove values, add them back, and query if they are 
      still current. 

    B) class constraint

      This class allows one to define constraints specified by tables
      of satisfying assignments.

      On initialization the variables the constraint is over is
      specified (i.e. the scope of the constraint). This must be an
      ORDERED list of variables. This list of variables cannot be
      changed once the constraint object is created.

      Once initialized the constraint can be incrementally initialized
      with a list of satisfying tuples. Each tuple specifies a value
      for each variable in the constraint (in the same ORDER as the
      variables of the constraint were specified).

    C) Backtracking routine---takes propagator and CSP as arguments
       so that basic backtracking, forward-checking or GAC can be 
       executed depending on the propagator used.

"""
import itertools

import sys


class Variable:
    """
    Class for defining CSP variables.  On initialization the
    variable object should be given a name, and optionally a list of
    domain values. Later on more domain values an be added...but
    domain values can never be removed.

    The variable object offers two types of functionality to support
    search.

    (a) It has a current domain, implemented as a set of flags
       determining which domain values are "current", i.e., un-pruned.
       - you can prune a value, and restore it.
       - you can obtain a list of values in the current domain, or count
         how many are still there

    (b) You can assign and un-assign a value to the variable.
       The assigned value must be from the variable domain, and
       you cannot assign to an already assigned variable.

       You can get the assigned value e.g., to find the solution after
       search.

       Assignments and current domain interact at the external interface
       level. Assignments do not affect the internal state of the current domain
       so as not to interact with value pruning and restoring during search.

       But conceptually when a variable is assigned it only has
       the assigned value in its current domain (viewing it this
       way makes implementing the propagators easier). Hence, when
       the variable is assigned, the 'cur_domain' returns the
       assigned value as the sole member of the current domain,
       and 'in_cur_domain' returns True only for the assigned
       value. However, the internal state of the current domain
       flags are not changed so that pruning and un-pruning can
       work independently of assignment and un-assignment.
    """

    #
    # set up and info methods
    #
    def __init__(self, name, domain=set()):
        """
        Create a variable object, specifying its name (a string).
        Optionally specify the initial domain.

        :param name: Variable name
        :type name: str
        :param domain: Optional domain of CSP
        :type domain: set
        :return: None
        """
        self.name = name  # text name for variable
        self.domain = set(domain)  # Make a copy of passed domain
        self.cur_domain = {val: True for val in self.domain}  # using list
        self.assignedValue = None

    def add_domain_values(self, values):
        """
        Add additional domain values to the domain
        Removals not supported

        :type values: list
        """
        for val in values:
            self.domain.add(val)
            self.cur_domain[val] = True

    def domain_size(self):
        """
        :return: The size of the (permanent) domain
        :rtype: int
        """
        return len(self.domain)

    def domain(self):
        """
        :return: the variable's (permanent) domain
        :rtype: set
        """
        return set(self.domain)

    #
    # methods for current domain (pruning and unpruning)
    #
    def prune_value(self, value):
        """Remove value from CURRENT domain"""
        self.cur_domain[value] = False

    def unprune_value(self, value):
        """Restore value to CURRENT domain"""
        self.cur_domain[value] = True

    def get_cur_domain(self):
        """
        :return: List of values in CURRENT domain (if assigned,
            only assigned value is viewed as being in current domain)
        :rtype: set
        """
        return set(filter(self.cur_domain.get, self.cur_domain.keys())) \
            if not self.is_assigned() else {self.get_assigned_value()}

    def in_cur_domain(self, value):
        """
        Check if value is in CURRENT domain (without constructing list).
        If assigned, only assigned value is viewed as being in current
        domain.

        :return: True iff value is in current domain
        :rtype: bool
        """
        return self.cur_domain[value] if not self.is_assigned() else \
            value == self.get_assigned_value()

    def get_cur_domain_size(self):
        """
        Return the size of the variables domain (without constructing list)

        :rtype: int
        """
        return sum(filter(self.cur_domain.get, self.cur_domain.keys())) \
            if not self.is_assigned() else 1

    def restore_cur_domain(self):
        """
        return all values back into CURRENT domain
        """
        for val in self.domain:
            self.cur_domain[val] = True

    #
    # methods for assigning and un-assigning
    #
    def is_assigned(self):
        return self.assignedValue is not None

    def assign(self, value):
        """
        Used by bt_search. When we assign we remove all other values
        values from curdom. We save this information so that we can
        reverse it on unassign
        """

        if self.is_assigned() or not self.in_cur_domain(value):
            msg = "ERROR: trying to assign variable that is already " \
                  "assigned or illegal value (not in current domain)"
            print(msg, file=sys.stderr)
            return

        self.assignedValue = value

    def unassign(self):
        """
        Used by bt_search. Un-assign and restore old curdom
        """
        if not self.is_assigned():
            msg = "ERROR: trying to un-assign, variable {} not yet assigned"
            print(msg.format(self), file=sys.stderr)
            return

        self.assignedValue = None

    def get_assigned_value(self):
        """return assigned value...returns None if is unassigned"""
        return self.assignedValue

    #
    # internal methods
    #
    def __repr__(self):
        return "Var--\"{}\": Dom = {}, CurDom = {}".format(self.name,
                                                           self.domain,
                                                           self.cur_domain)

    def __str__(self):
        return "Var--{}".format(self.name)


class Constraint:
    """
    Class for defining constraints variable objects specifies an
    ordering over variables.  This ordering is used when calling
    the satisfied function which tests if an assignment to the
    variables in the constraint's scope satisfies the constraint
    """

    def __init__(self, name, scope, function):
        """
        Create a constraint object, specify the constraint name (a
        string) and its scope (an ORDERED list of variable objects).
        The order of the variables in the scope is critical to the
        functioning of the constraint.

        Constraints are implemented as storing a set of satisfying
        tuples (i.e., each tuple specifies a value for each variable
        in the scope such that this sequence of values satisfies the
        constraints).

        NOTE: This is a very space expensive representation...a proper
        constraint object would allow for representing the constraint
        with a function.

        :param name: Constraint Name
        :type name: str
        :param scope: An ORDERED list of variable objects
        :type scope: iterable[Variable]
        :return: None
        """
        self.scope = set(scope)
        self.name = name
        self.constraint_function = function
        self.satisfying_cache = dict()

    def get_scope(self):
        """
        :return: all variables that the constraint is over
        :rtype: set[Variable]
        """
        return set(self.scope)

    def check(self, vals):
        """
        Check if the current assignments to the variables in this constraint's
        scope satisfy the constraint function

        :rtype: bool
        """
        return self.constraint_function(self.scope)

    def get_num_unassigned(self):
        """
        return the number of unassigned variables in the constraint's scope
        """
        n = 0
        for v in self.scope:
            if not v.is_assigned():
                n = n + 1
        return n

    def get_unassigned_vars(self):
        """return list of unassigned variables in constraint's scope. Note
           more expensive to get the list than to then number"""
        vs = []
        for v in self.scope:
            if not v.is_assigned():
                vs.append(v)
        return vs

    def has_support(self, var, val):
        """Test if a variable value pair has a supporting tuple (a set
           of assignments satisfying the constraint where each value is
           still in the corresponding variables current domain
        """
        if (var, val) in self.sup_tuples:
            for t in self.sup_tuples[(var, val)]:
                if self.tuple_is_valid(t):
                    return True
        return False

    def tuple_is_valid(self, t):
        """
        Internal routine. Check if every value in tuple is still in
        corresponding variable domains

        :rtype: boolean
        """
        for i, var in enumerate(self.scope):
            if not var.in_cur_domain(t[i]):
                return False
        return True

    def __str__(self):
        return "{}({})".format(self.name, [var.name for var in self.scope])


class CSP:
    """Class for packing up a set of variables into a CSP problem.
       Contains various utility routines for accessing the problem.
       The variables of the CSP can be added later or on initialization.
       The constraints must be added later"""

    def __init__(self, name, vars=[]):
        """
        Create a CSP object. Specify a name (a string) and optionally a set
        of variables

        :param name: Name of CSP
        :type name: str
        :param vars:
        :type vars: iterable[Variable]
        :return:
        """

        self.name = name
        self.vars = []
        self.cons = []
        self.vars_to_cons = dict()
        for v in vars:
            self.add_var(v)

    def add_var(self, v):
        """Add variable object to CSP while setting up an index
           to obtain the constraints over this variable"""
        if not type(v) is Variable:
            print("Trying to add non variable ", v, " to CSP object")
        elif v in self.vars_to_cons:
            print("Trying to add variable ", v,
                  " to CSP object that already has it")
        else:
            self.vars.append(v)
            self.vars_to_cons[v] = []

    def add_constraint(self, c):
        """Add constraint to CSP. Note that all variables in the
           constraints scope must already have been added to the CSP"""
        if not type(c) is Constraint:
            print("Trying to add non constraint ", c, " to CSP object")
        else:
            for v in c.scope:
                if v not in self.vars_to_cons:
                    print("Trying to add constraint ", c,
                          " with unknown variables to CSP object")
                    return
                self.vars_to_cons[v].append(c)
            self.cons.append(c)

    def get_all_cons(self):
        """
        return list of all constraints in the CSP

        :rtype: list[Constraint]
        """
        return self.cons

    def get_cons_with_var(self, var):
        """
        return list of constraints that include var in their scope

        :rtype: list[Constraint]
        """
        return list(self.vars_to_cons[var])

    def get_all_vars(self):
        """
        Get all the variables in the CSP

        :return: List of variables in the CSP
        :rtype: list[Variable]
        """

        return list(self.vars)

    def print_all(self):
        print("CSP", self.name)
        print("   Variables = ", self.vars)
        print("   Constraints = ", self.cons)

    def print_soln(self):
        print("CSP", self.name, " Assignments = ")
        for v in self.vars:
            print(v, " = ", v.get_assigned_value(), "    ", end='')
        print("")
