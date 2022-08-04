import smt2_parser

class Generator:
    def __init__(self, size, edges, sln, smt_file):
        self.size = size
        self.edges = edges
        self.sln = sln
        self.constraints, self.vars_all = smt2_parser.parse(smt_file, check_neg = False)
        self.groups, self.vars = smt2_parser.independent_formulas(self.constraints, self.vars_all)
        self.insert = list()
        for idx in range(self.size):
            self.insert.append(0)
        while sum(self.insert) < len(self.groups):
            for func in self.sln:
                self.insert[func] += 1
                if sum(self.insert) >= len(self.groups):
                    break
    def get_logic_def(self):
        logic_def = "char read_input(char *input, int index){ return input[index]; }\n"
        return logic_def

    def get_logic_c(self):
        logic_c = list()
        group_idx = 0
        for idx in range(self.size):
            if self.insert[idx] == 0:
                logic_c.append("\t\tchar c = read_input(copy, 0);")
            else:
                copy_idx, tab_cnt = 0, 0
                constraints, vars = set(), set()
                for cnt in range(self.insert[idx]):
                    constraints = constraints.union(self.groups[group_idx + cnt])
                    vars = vars.union(self.vars[group_idx + cnt])
                buggy_constraints = ""
                for var in vars:
                    buggy_constraints += "\t\tchar {} = read_input(copy, {});\n".format(var, copy_idx)
                    copy_idx += 1
                buggy_constraints += "\t\tchar c = read_input(copy, {});\n".format(len(vars))
                buggy_constraints += "\t\tint flag = 0;\n"
                for constraint in constraints:
                    buggy_constraints += "\t"*tab_cnt + "\t\tif{}{{\n".format(constraint)
                    tab_cnt += 1
                buggy_constraints += "\t"*tab_cnt + "\t\tflag = 1;\n"
                for k in range(len(constraints)-1, -1, -1):
                    buggy_constraints += "\t"*k + "\t\t}\n"
                logic_c.append(buggy_constraints)
                group_idx += self.insert[idx]
        return logic_c

    def get_numb_bytes(self):
        numb_bytes = list()
        group_idx = 0
        for idx in range(self.size):
            if self.insert[idx] == 0:
                numb_bytes.append(1)
            else:
                used_bytes = 0
                for cnt in range(self.insert[idx]):
                    used_bytes += len(self.vars[group_idx + cnt])
                numb_bytes.append(used_bytes + 1)
                group_idx += self.insert[idx]
        return numb_bytes

    def get_guard(self):
        guard = list()
        group_idx = 0
        for idx in range(self.size):
            conds_default = [["0"], ["1"],
            ["c < 0", "c >= 0"],
            ["c < -43", "c < 42", "c >= 42"],
            ["c < -64", "c < 0", "c < 64", "c >= 64"]]
            numb_edges = len(self.edges[idx])
            if self.insert[idx] == 0:
                guard.append(conds_default[numb_edges])
            else:
                next, bug_edge, m = 0, 0, 0
                conds = []
                for i in range(len(self.sln)):
                    if self.sln[i] == idx:
                        if i == len(self.sln) - 1:
                            next = 'bug'
                        else:
                            next = self.sln[i+1]
                for n in range(numb_edges):
                    if self.edges[idx][n] == next:
                        bug_edge = n
                for n in range(numb_edges):
                    if n == bug_edge:
                        conds.append("flag == 1")
                    else:
                        conds.append(conds_default[numb_edges-1][m] + " && flag == 0")
                        m += 1
                group_idx += 1
                guard.append(conds)
        return guard

    def get_total_bytes(self):
        return sum(self.get_numb_bytes())

    def get_bug(self):
        return "abort();"