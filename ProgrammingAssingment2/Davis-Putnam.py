def dpll(clauses, assignment):

    # Unit Propagation
    unit_clauses = [c for c in clauses if len(c) == 1]
    while unit_clauses:
        unit = unit_clauses[0]
        clauses = propagate_unit(clauses, unit[0])
        assignment[abs(unit[0])] = unit[0] > 0
        unit_clauses = [c for c in clauses if len(c) == 1]

    # Pure Literal Elimination
    for pure_literal in find_pure_literals(clauses):
        clauses = eliminate_pure_literal(clauses, pure_literal)
        assignment[abs(pure_literal)] = pure_literal > 0

    # Check if all clauses are satisfied
    if not clauses:
        return assignment, True

    # Check for empty clause (conflict)
    if [] in clauses:
        return None, False

    # Choose a literal to assign
    chosen_literal = clauses[0][0]

    # Recur with chosen literal assigned true
    new_assignment = assignment.copy()
    result, success = dpll(clauses + [[-chosen_literal]], new_assignment)
    if success:
        return result, True

    # Recur with chosen literal assigned false
    new_assignment = assignment.copy()
    return dpll(clauses + [[chosen_literal]], new_assignment)


def propagate_unit(clauses, literal):
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue
        new_clause = [x for x in clause if x != -literal]
        new_clauses.append(new_clause)
    return new_clauses


def find_pure_literals(clauses):
    literals = set([literal for clause in clauses for literal in clause])
    return [l for l in literals if -l not in literals]


def eliminate_pure_literal(clauses, pure_literal):
    return [clause for clause in clauses if pure_literal not in clause]


def get_input(filepath='./data/DP_input.txt'):
    ans, n, end, x = [], 0, '', 0
    with open(filepath, 'r') as f:
        lines = f.readlines()
    while True:
        s = list(map(int, lines[x].rstrip().split()))
        x += 1
        for i in s:
            n = max(n, i)
        if s[0] == 0:
            break
        ans.append(s)
    while True:
        try:
            end += lines[x]
            x += 1
        except IndexError:
            return ans, n, end


def output(solution, flag, filepath='./data/DP_output.txt'):
    lines = []
    if flag:
        for i in range(1, n + 1):
            s = 'T' if i in solution.keys() and solution[i] else 'F'
            lines.append(f'{i} {s}\n')
    lines.append('0\n')
    lines.append(end.rstrip('\n'))
    with open(filepath, 'w', newline='\n') as f:
        f.writelines(lines)
    print('Output Successfully')


clauses, n, end = get_input(filepath='./data/front_end_output.txt')
assignment = {}
solution, success = dpll(clauses, assignment)
output(solution, success, filepath='./data/back_end_input.txt')
