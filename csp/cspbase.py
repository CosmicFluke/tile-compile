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


class GridVariableIterator:
    def __init__(self, collection):
        self.collection = sorted(
            collection,
            key=lambda gv:
                (0 if len(gv.get_exit_points()) > 0 else
                 1 if 0 in gv.get_coords() else 2) + gv.get_cur_domain_size(),
            reverse=True)

    def __iter__(self):
        return self

    def __next__(self):
        for var in self.collection:
            if len(var.get_exit_points()) > 0 or 0 in var.get_coords():
                self.collection.remove(var)
                return var
        if self.collection:
            return self.collection.pop()
        raise StopIteration

    def __len__(self):
        return len(self.collection)

    def pop(self):
        return self.collection.pop()


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
        self.cur_domain_flag = True
        self.cur_domain_cache = self.get_cur_domain()

    def add_domain_values(self, values):
        """
        Add additional domain values to the domain
        Removals not supported

        :type values: list
        """
        for val in values:
            self.domain.add(val)
            self.cur_domain[val] = True
        self.cur_domain_flag = True

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
        if self.is_assigned() and self.get_assigned_value() is value:
            self.unassign()
        self.cur_domain[value] = False
        self.cur_domain_flag = True

    def unprune_value(self, value):
        """Restore value to CURRENT domain"""
        self.cur_domain[value] = True
        self.cur_domain_flag = True

    def get_cur_domain(self):
        """
        :return: List of values in CURRENT domain (if assigned,
            only assigned value is viewed as being in current domain)
        :rtype: set
        """
        if self.is_assigned():
            return [self.get_assigned_value()]
        if self.cur_domain_flag:
            self.cur_domain_cache = \
                list(filter(self.cur_domain.get, self.cur_domain.keys()))
            self.cur_domain_flag = False
        return self.cur_domain_cache

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
        return 1 if self.is_assigned() else len(self.cur_domain_cache) if not \
            self.cur_domain_flag else len(self.get_cur_domain())

    def restore_cur_domain(self):
        """
        return all values back into CURRENT domain
        """
        for val in self.domain:
            self.cur_domain[val] = True
        self.cur_domain_flag = True

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
        self.cur_domain_flag = True

    def unassign(self):
        """
        Used by bt_search. Un-assign and restore old curdom
        """
        if not self.is_assigned():
            msg = "ERROR: trying to un-assign, variable {} not yet assigned"
            print(msg.format(self), file=sys.stderr)
            return

        self.assignedValue = None
        self.cur_domain_flag = True

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

        Constraints are implemented as functions

        :param name: Constraint Name
        :type name: str
        :param scope: An ORDERED list of variable objects
        :type scope: iterable[Variable]
        :return: None
        """
        self.scope = set(scope)
        self.name = name
        self.constraint_function = function
        self.sat_mappings = set()
        self.unsat_mappings = set()

    def get_scope(self):
        """
        :return: all variables that the constraint is over
        :rtype: set[Variable]
        """
        return GridVariableIterator(self.scope)

    def check(self):
        """
        Check if the current assignments to the variables in this constraint's
        scope satisfy the constraint function

        :rtype: bool
        """
        return self.constraint_function(
            {var: var.get_assigned_value() for var in self.scope})

    def get_num_unassigned(self):
        """
        return the number of unassigned variables in the constraint's scope
        """
        return len(list(filter(lambda v: not v.is_assigned(),
                               self.scope)))

    def get_unassigned_vars(self):
        """
        :return: All unassigned variables in constraint's scope. Note that it is
           more expensive to get the list than to then number
        :rtype: set[Variable]
        """
        return GridVariableIterator(filter(lambda v: not v.is_assigned(),
                                           self.scope))

    def check_mapping(self, mapping):
        frozen_mapping = frozenset(mapping)
        if frozen_mapping in self.sat_mappings and \
                frozen_mapping not in self.unsat_mappings:
            return True
        if self.constraint_function(dict(mapping)):
            self.sat_mappings.add(frozen_mapping)
            return True
        self.unsat_mappings.add(frozen_mapping)
        return False

    def has_support(self, var, val):
        """
        Test if a variable value pair has a supporting set of assignments
        satisfying the constraint where each value is still in the
        corresponding variables current domain.

        :rtype: bool
        """

        # print("Var: {}\t\tVal: {}".format(var, val))
        if var not in self.scope:
            return True

        if len(self.scope) == 1:
            return self.constraint_function({var: val})

        # Sequence of 2-tuples with variables and respective current domains
        var_to_cur_domain = ((variable, variable.get_cur_domain()) for
                             variable in self.scope)

        variables, cur_domains = zip(*var_to_cur_domain)

        return any(map(
            # Calls to constraint function given var-value mappings for each
            # assignment
            lambda assignment:
                self.check_mapping(frozenset(zip(variables, assignment))),
            # Product of all possible assignments given current domains
            itertools.product(*cur_domains)
        ))

    def __str__(self):
        return "{}({})".format(self.name, [var.name for var in self.scope])


class CSP:
    """Class for packing up a set of variables into a CSP problem.
       Contains various utility routines for accessing the problem.
       The variables of the CSP can be added later or on initialization.
       The constraints must be added later"""

    def __init__(self, name, variables=set()):
        """
        Create a CSP object. Specify a name (a string) and optionally a set
        of variables

        :param name: Name of CSP
        :type name: str
        :param variables:
        :type variables: iterable[Variable]
        :return:
        """

        self.name = name
        self.vars = set()
        self.cons = set()
        self.vars_to_cons = dict()
        for v in variables:
            self.add_var(v)

    def add_var(self, v):
        """Add variable object to CSP while setting up an index
           to obtain the constraints over this variable"""
        if v in self.vars_to_cons:
            print("Trying to add variable", v,
                  "to CSP object that already has it", file=sys.stderr)
            return
        self.vars.add(v)
        self.vars_to_cons[v] = set()

    def add_constraint(self, c):
        """Add constraint to CSP. Note that all variables in the
           constraints scope must already have been added to the CSP"""
        if not type(c) is Constraint:
            raise TypeError(
                "Trying to add non constraint {} to CSP object".format(c))
        if any((v not in self.vars_to_cons for v in c.scope)):
            print("Trying to add constraint", c,
                  "with unknown variables to CSP object", file=sys.stderr)
            return

        for v in c.scope:
            self.vars_to_cons[v].add(c)
        self.cons.add(c)

    def get_all_cons(self):
        """
        return list of all constraints in the CSP

        :rtype: set[Constraint]
        """
        return set(self.cons)

    def get_cons_with_var(self, var):
        """
        return list of constraints that include var in their scope

        :rtype: set[Constraint]
        """
        return set(self.vars_to_cons[var])

    def get_all_vars(self):
        """
        Get all the variables in the CSP

        :return: List of variables in the CSP
        :rtype: list[Variable]
        """

        return list(self.vars)

    def __str__(self):
        return "CSP {}\n".format(self.name) + \
               "   Variables = {}\n".format(self.vars) + \
               "   Constraints = {}".format(self.cons)

    def solution_str(self):
        return "CSP {}\n".format(self.name) + \
               "    Assignments: \n" + \
               "\n".join(
                   ("{} = {}".format(v, v.get_assigned_value()) for
                    v in self.vars))
