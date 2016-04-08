from csp.cspbase import *
import logging, time


class BacktrackingSearch:
    """
    Encapsulates statistics and bookkeeping for backtracking search.
    """

    def __init__(self, csp, logLevel):
        '''
        csp == CSP object specifying the CSP to be solved
        '''

        self.csp = csp

        # the number of variable assignments made during search
        self.num_decisions = 0

        # the number of value prunings during search
        self.num_prunings = 0

        # Tracks unassigned variables
        unassigned_vars = list()
        self.logger = logging.getLogger('btLogger')
        self.logger.setLevel(logLevel)
        self.TRACE = False
        self.runtime = 0

    def trace_on(self):
        '''Turn search trace on'''
        self.TRACE = True

    def trace_off(self):
        '''Turn search trace off'''
        self.TRACE = False

    def clear_stats(self):
        '''Initialize counters'''
        self.num_decisions = 0
        self.num_prunings = 0
        self.runtime = 0

    def print_stats(self):
        print("Search made {} variable assignments and pruned {} variable values".format(
            self.num_decisions, self.num_prunings))

    def restoreValues(self,prunings):
        '''Restore list of values to variable domains
           each item in prunings is a pair (var, val)'''
        for var, val in prunings:
            var.unprune_value(val)

    def restore_all_variable_domains(self):
        '''Reinitialize all variable domains'''
        for var in self.csp.vars:
            if var.is_assigned():
                var.unassign()
            var.restore_cur_domain()

    def extract_mr_var(self):
        """
        Remove variable with minimum sized cur domain from list of
        unassigned vars. Would be faster to use heap...but this is
        not production code.
        """
        md = -1
        mv = None
        for v in self.unasgn_vars:
            if md < 0:
                md = v.get_cur_domain_size()
                mv = v
            elif v.get_cur_domain_size() < md:
                md = v.get_cur_domain_size()
                mv = v
        self.unasgn_vars.remove(mv)
        return mv

    def restoreUnasgnVar(self, var):
        '''Add variable back to list of unassigned vars'''
        self.unasgn_vars.append(var)

    def bt_search(self, propagator):
        """
        Try to solve the CSP using specified propagator routine

        propagator == a function with the following template
        propagator(csp, newly_instantiated_variable=None)
        ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

        csp is a CSP object---the propagator can use this to get access
        to the variables and constraints of the problem.

        newly_instaniated_variable is an optional argument.
        if newly_instantiated_variable is not None:
           then newly_instantiated_variable is the most
           recently assigned variable of the search.
        else:
           propagator is called before any assignments are made
           in which case it must decide what processing to do
           prior to any variables being assigned.

        The propagator returns True/False and a list of (Variable, Value) pairs.
        Return is False if a deadend has been detected by the propagator.
         in this case bt_search will backtrack
        return is true if we can continue.

        The list of variable values pairs are all of the values
        the propagator pruned (using the variable's prune_value method).
        bt_search NEEDS to know this in order to correctly restore these
        values when it undoes a variable assignment.

        NOTE propagator SHOULD NOT prune a value that has already been
        pruned! Nor should it prune a value twice
        """

        # TODO: Re-implement

        self.clear_stats()
        stime = time.process_time()

        self.restore_all_variable_domains()

        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        status, prunings = propagator(self.csp)  # initial propagate no assigned variables.
        self.num_prunings = self.num_prunings + len(prunings)

        self.logger.info(len(self.unasgn_vars), " unassigned variables at start of search")
        self.logger.info("Root Prunings: ", prunings)

        if status == False:
            self.logger.info("CSP{} detected contradiction at root".format(
                self.csp.name))
        else:
            status = self.bt_recurse(propagator, 1)   # now do recursive search


        self.restoreValues(prunings)
        if status == False:
            print("CSP{} unsolved. Has no solutions".format(self.csp.name))
        if status == True:
            self.logger.info("CSP {} solved. CPU Time used = {}".format(self.csp.name,
                                                             time.process_time() - stime))
            self.csp.solution_str()

        print("bt_search finished")
        self.print_stats()

    def bt_recurse(self, propagator, level):
        """
        Return true if found solution. False if still need to search.
        If top level returns false--> no solution
        """

        # TODO: Re-implement

        print('  ' * level, "bt_recurse level ", level)

        if not self.unasgn_vars:
            # all variables assigned
            return True
        else:
            var = self.extract_mr_var()

            print('  ' * level, "bt_recurse var = ", var)

            for val in var.get_cur_domain():
                print('  ' * level, "bt_recurse trying", var, "=", val)

                var.assign(val)
                self.num_decisions = self.num_decisions + 1

                status, prunings = propagator(self.csp, var)
                self.num_prunings = self.num_prunings + len(prunings)

                print('  ' * level, "bt_recurse prop status = ", status)
                print('  ' * level, "bt_recurse prop pruned = ", prunings)

                if status:
                    if self.bt_recurse(propagator, level+1):
                        return True

                print('  ' * level, "bt_recurse restoring ", prunings)
                self.restoreValues(prunings)
                var.unassign()

            self.restoreUnasgnVar(var)
            return False

