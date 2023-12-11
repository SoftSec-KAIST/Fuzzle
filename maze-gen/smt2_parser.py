import sys, random
from pysmt.smtlib.parser import SmtLibParser
from collections import defaultdict
from pysmt.shortcuts import is_sat, Not

def error(flag):
    if flag == 0:
        print("ERROR: node type not recognized")
    elif flag == 1:
        print("ERROR: type not supported")

def cast_to_signed(l, r):
    cast = ""
    extend_step = 0
    if l.is_bv_constant():
        cast = "(int" + str(l.bv_width()) + "_t) "
    elif r.is_bv_constant():
        cast = "(int" + str(r.bv_width()) + "_t) "
    elif l.is_bv_sext() or l.is_bv_zext():
        extend_step = l.bv_extend_step()
    elif r.is_bv_sext() or r.is_bv_zext():
        extend_step = r.bv_extend_step()
    else:
        error(1)
    if extend_step == 8:
        cast = "(int16_t) "
    elif extend_step == 16 or extend_step == 24:
        cast = "(int32_t) "
    elif extend_step == 32 or extend_step == 48 or extend_step == 56:
        cast = "(int64_t) "
    return cast

def cast_to_unsigned(l, r):
    cast = ""
    extend_step = 0
    if l.is_bv_constant():
        cast = "(uint" + str(l.bv_width()) + "_t) "
    elif r.is_bv_constant():
        cast = "(uint" + str(r.bv_width()) + "_t) "
    elif l.is_bv_sext() or l.is_bv_zext():
        extend_step = l.bv_extend_step()
    elif r.is_bv_sext() or r.is_bv_zext():
        extend_step = r.bv_extend_step()
    else:
        error(1)
    if extend_step == 8:
        cast = "(uint16_t) "
    elif extend_step == 16 or extend_step == 24:
        cast = "(uint32_t) "
    elif extend_step == 32 or extend_step == 48 or extend_step == 56:
        cast = "(uint64_t) "
    return cast

def convert_helper(node, cons, op):
    (l, r) = node.args()
    cons = convert(l, cons + "(")
    cons += op
    cons = convert(r, cons) + ")"
    return cons

def convert(node, cons):
    if node.is_iff():
            (l, r) = node.args()
            if l.is_false():
                cons += "(!"
                cons = convert(r, cons)
                cons += ")"
            else:
                error(1)
    elif node.is_equals():
        cons = convert_helper(node, cons, " == ")
    elif node.is_bv_sle():
        (l, r) = node.args()
        cast = cast_to_signed(l, r)
        cons = convert(l, cons + "(" + cast)
        cons += " <= "
        cons = convert(r, cons + cast) + ")"
    elif node.is_bv_ule():
        (l, r) = node.args()
        cast = cast_to_unsigned(l, r)
        cons = convert(l, cons + "(" + cast)
        cons += " <= "
        cons = convert(r, cons + cast) + ")"
    elif node.is_bv_slt():
        (l, r) = node.args()
        cast = cast_to_signed(l, r)
        cons = convert(l, cons + "(" + cast)
        cons += " < "
        cons = convert(r, cons + cast) + ")"
    elif node.is_bv_ult():
        (l, r) = node.args()
        cast = cast_to_unsigned(l, r)
        cons = convert(l, cons + "(" + cast)
        cons += " < "
        cons = convert(r, cons + cast) + ")"
    elif node.is_bv_add():
        cons = convert_helper(node, cons, " + ")
    elif node.is_bv_sub():
        cons = convert_helper(node, cons, " - ")
    elif node.is_bv_mul():
        cons = convert_helper(node, cons, " * ")
    elif node.is_bv_udiv() or node.is_bv_sdiv():
        cons = convert_helper(node, cons, " / ")
    elif node.is_bv_urem() or node.is_bv_srem():
        cons = convert_helper(node, cons, " % ")
    elif node.is_bv_sext():
        extend_step = node.bv_extend_step()
        (l, ) = node.args()
        if extend_step == 8:
            cons += "(int16_t) "
        if extend_step == 16 or extend_step == 24:
            cons += "(int32_t) "
        elif extend_step == 32 or extend_step == 48 or extend_step == 56:
            cons += "(int64_t) "
        cons = convert(l, cons)
    elif node.is_bv_zext():
        extend_step = node.bv_extend_step()
        (l, ) = node.args()
        if extend_step == 8:
            cons += "(uint16_t) "
        if extend_step == 16 or extend_step == 24:
            cons += "(uint32_t) "
        elif extend_step == 32 or extend_step == 48 or extend_step == 56:
            cons += "(uint64_t) "
        cons = convert(l, cons)
    elif node.is_bv_concat():
        cons += "model_version"
    elif node.is_bv_extract():
        ext_start = node.bv_extract_start()
        ext_end = node.bv_extract_end()
        (l, ) = node.args()
        extract = ""
        if ext_start == 0 and ext_end == 7:
            extract = "(uint8_t) "
        elif ext_start == 0 and ext_end == 15:
            extract = "(uint16_t) "
        elif ext_start == 0 and ext_end == 31:
            extract = "(uint32_t) "
        else:
            error(1)
        cons = convert(l, cons + extract + "(")
        cons += ")"
    elif node.is_select():
        (l, r) = node.args()
        if l.is_symbol() and r.is_bv_constant():
            array = str(l) + "_" + str(r.constant_value())
            cons += array
        else:
            error(1)
    elif node.is_bv_constant():
        constant =  "(uint" + str(node.bv_width()) + "_t) " + str(node.constant_value())
        cons += constant
    else:
        error(0)
    return cons

def is_neg_sat(c, clauses):
    form_neg = Not(c)
    for n in clauses:
        if n is not c:
            form_neg = form_neg.And(n)
    sat = is_sat(form_neg, solver_name = "z3")
    return sat

def parse(file_path, check_neg):
    parser = SmtLibParser()
    script = parser.get_script_fname(file_path)
    decl_arr = list()
    variables = set()
    decls = script.filter_by_command_name("declare-fun")
    for d in decls:
        for arg in d.args:
            if (str)(arg) != "model_version":
                decl_arr.append(arg)
    formula = script.get_strict_formula()
    res = is_sat(formula, solver_name="z3")
    assert(res == True)
    parsed_cons = dict()
    x = formula
    clauses = set()
    while len(x.get_atoms()) > 1:
        (x, y) = x.args()
        clauses.add(y)
    clauses.add(x)
    for clause in clauses:
        cons_in_c = convert(clause, "")
        if "model_version" not in cons_in_c:
            if check_neg == True:
                neg_sat = is_neg_sat(clause, clauses)
                parsed_cons[cons_in_c] = neg_sat
            else:
                parsed_cons[cons_in_c] = ""
            for declared in decl_arr:
                for idx in range(0,100):
                    var_idx = str(declared) + "_" + str(idx)
                    if var_idx + " " in cons_in_c or var_idx + ")" in cons_in_c:
                        variables.add(str(declared) + "_" + str(idx))
    return parsed_cons, variables

def extract_vars(cond, variables):
    vars = set()
    for var in variables:
        if var + " " in cond or var + ")" in cond:
            vars.add(var)
    return vars

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, node, neighbour):
        self.graph[node].append(neighbour)

    def get_edges(self, node):
        return self.graph[node]

    def separate_helper(self, node, visited, group):
        if node not in visited:
            group.add(node)
            visited.add(node)
        for neighbour in self.graph[node]:
            if neighbour not in visited:
                self.separate_helper(neighbour, visited, group)
        return group

    def separate(self):
        visited = set()
        groups = list()
        for node in self.graph:
            group = self.separate_helper(node, visited, set())
            if len(group) > 0:
                groups.append(group)
        return groups

def independent_formulas(conds, variables):
    formula = Graph()
    for cond in conds:
        vars = extract_vars(cond, variables)
        for other in conds:
            if len(vars.intersection(extract_vars(other, variables))) > 0:
                formula.add_edge(cond, other)
    groups = formula.separate()
    vars_by_groups = list()
    for group in groups:
        used_vars = set()
        for cond in group:
            used_vars = used_vars.union(extract_vars(cond, variables))
        vars_by_groups.append(sorted(used_vars))
    return groups, vars_by_groups

def get_negated(conds, group, vars, numb):
    negated_groups = list()
    new_vars = list()
    n = 0
    for cond in group:
        if conds[cond] == True:
            n = n + 1
    if n >= numb:
        negated = set()
        for i in range(numb):
            negated_group = set()
            for cond in group:
                if conds[cond] == True and len(negated) <= i and cond not in negated:
                        negated_group.add("(!" + cond + ")")
                        negated.add(cond)
                else:
                    negated_group.add(cond)
            negated_groups.append(negated_group)
    else:
        for i in range(numb):
            new_group = set()
            new_var = "c" + str(i)
            # negate one of the original and add same conds for new var
            for cond in group:
                if conds[cond] == True:
                    cond_neg = "(!" + cond + ")"
                    break
            new_group.add(cond_neg)
            for cond in group:
                cond_vars = extract_vars(cond, vars)
                for v in cond_vars:
                    cond_new = cond.replace(v, new_var)
                new_group.add(cond_new)
            negated_groups.append(new_group)
            new_vars.append(new_var)
    return negated_groups, new_vars

def get_subgroup(groups, vars_by_groups, seed):
    # get a subset of a randomly selected independent group
    random.seed(seed)
    rand = random.randint(0, len(groups)-1)
    vars = set()
    subgroup = groups[rand]
    for cond in subgroup:
        vars = vars.union(extract_vars(cond, vars_by_groups[rand]))
    return subgroup, vars

def main(file_path):
    conds, variables = parse(file_path, True)
    for cond in conds:
        vars = extract_vars(cond, variables)
        print(cond)
        print(vars, "\n")
    print("-"*100)
    groups, vars_by_groups = independent_formulas(conds, variables)
    for idx in range(len(groups)):
        print(vars_by_groups[idx], "\n")
        for cond in groups[idx]:
            print(cond)
            print("Can be negated:", conds[cond], "\n")
        print("*"*100)

if __name__ == '__main__':
    file_path = sys.argv[1]
    main(file_path)
