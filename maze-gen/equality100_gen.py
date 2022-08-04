import random

class Generator:
    def __init__(self, size, edges, sln, smt_file):
        self.size = size
        self.edges = edges
        self.sln = sln

    def get_logic_def(self):
        logic_def = "char read_input(char *input, int index){ return input[index]; }\n\n"
        return logic_def

    def get_logic_c(self):
        logic_c = list()
        for idx in range(self.size):
            logic_c.append("\t\tchar c = read_input(copy, 0);")
        return logic_c

    def get_numb_bytes(self):
        numb_bytes = list()
        for idx in range(self.size):
            numb_bytes.append(1)
        return numb_bytes

    def get_guard(self):
        guard = list()
        default = [["0"], ["1"],
            ["c < 0", "c >= 0"],
            ["c < -43", "c < 42", "c >= 42"],
            ["c < -64", "c < 0", "c < 64", "c >= 64"]]
        equality = [["0"], ["c == 1"],
            ["c == -64", "c == 64"],
            ["c == -85", "c == 1", "c == 87"],
            ["c == -96", "c == -32", "c == 32", "c == 96"]]
        proportion_eq, total_edges = 1, 0
        for idx in range(self.size):
            total_edges = total_edges + len(self.edges[idx])
        eq_edges = int(total_edges*proportion_eq)
        eq_nodes = set()
        random.seed(0)
        while eq_edges > 0:
            idx = random.randrange(0, self.size)
            if not idx in eq_nodes:
                eq_nodes.add(idx)
                eq_edges = eq_edges - len(self.edges[idx])
        for idx in range(self.size):
            numb_edges = len(self.edges[idx])
            if idx in eq_nodes:
                guard.append(equality[numb_edges])
            else:
                guard.append(default[numb_edges])
        return guard

    def get_total_bytes(self):
        return sum(self.get_numb_bytes())

    def get_bug(self):
        return "abort();"
