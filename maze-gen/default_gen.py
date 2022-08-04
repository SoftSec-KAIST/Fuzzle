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
        for idx in range(self.size):
            numb_edges = len(self.edges[idx])
            conds = []
            if numb_edges == 1:
                conds = [1]
            elif numb_edges == 2:
                conds = ["c < 0", "c >= 0"]
            elif numb_edges == 3:
                conds = ["c < -43", "c < 42", "c >= 42"]
            elif numb_edges == 4:
                conds = ["c < -64", "c < 0", "c < 64", "c >= 64"]
            guard.append(conds)
        return guard

    def get_total_bytes(self):
        return sum(self.get_numb_bytes())

    def get_bug(self):
        return "abort();"