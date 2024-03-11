class PropositionalEncoding:
    """
    rules to code the CNFs' indexes:

        First, the input has m possible moves: Jump(a,b,c,t), together with Jump(c,b,a,t),
        we have 2*m moves in total. From t=1 to t=n-2, there are 2*m*(n-2) CNFs,
        denoted as Jump(*,*,*,t).

        Second, there are n holes, from t=1 to t=n-1, so there are n*(n-1) CNFs, denoted as Peg(i,t).
    """

    def __init__(self):
        self.n = None  # number of holes
        self.empty = None  # the index of the empty hole at t=1
        self.rows = None  # all holes that are in a row
        self.m = None  # =len(rows)

    def peg_integer(self, i, t):
        # the CNF index Peg(i,t)
        return 2 * self.m * (self.n - 2) + (i - 1) * (self.n - 1) + t

    def initialize(self):
        # read from file
        with open('./data/front_end_input.txt', 'r') as f:
            lines = f.readlines()
        self.n, self.empty = map(int, lines[0].rstrip().split())
        rows, i = [], 1
        while True:
            try:
                row = tuple(map(int, lines[i].rstrip().split()))
                rows.append(row)
                i += 1
            except IndexError:
                break
        self.rows = rows
        self.m = len(self.rows)

    def precondition_and_causal_axioms(self):
        clauses = []
        for i in range(self.m):
            row = self.rows[i]
            for t in range(1, self.n - 2 + 1):
                a, b, c = row
                jump = (self.n - 2) * i * 2 + t
                reversed_jump = (self.n - 2) * (2 * i + 1) + t
                clauses += [
                    # Precondition axioms
                    [-jump, self.peg_integer(a, t)],
                    [-jump, self.peg_integer(b, t)],
                    [-jump, -self.peg_integer(c, t)],
                    [-reversed_jump, self.peg_integer(c, t)],
                    [-reversed_jump, self.peg_integer(b, t)],
                    [-reversed_jump, -self.peg_integer(a, t)],

                    # Causal axioms
                    [-jump, -self.peg_integer(a, t + 1)],
                    [-jump, -self.peg_integer(b, t + 1)],
                    [-jump, self.peg_integer(c, t + 1)],
                    [-reversed_jump, -self.peg_integer(c, t + 1)],
                    [-reversed_jump, -self.peg_integer(b, t + 1)],
                    [-reversed_jump, self.peg_integer(a, t + 1)]
                ]
        return clauses

    def starting_state(self):
        return [[self.peg_integer(i, 1)] if i != self.empty else [-self.peg_integer(i, 1)] for i in
                range(1, self.n + 1)]

    def ending_state(self):
        # At least one peg remains at time N-1
        clauses = [[self.peg_integer(i, self.n - 1) for i in range(1, self.n + 1)]]

        # No two holes have a peg
        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                clauses.append([-self.peg_integer(i, self.n - 1), -self.peg_integer(j, self.n - 1)])
        return clauses

    def one_action_at_a_time(self):
        clauses = []
        for t in range(1, self.n - 2 + 1):
            rows = [t + i * (self.n - 2) for i in range(2 * self.m)]
            for i in range(len(rows) - 1):
                for j in range(i + 1, len(rows)):
                    clauses.append([-rows[i], -rows[j]])
        return clauses

    def frame_axioms(self):
        clauses = []
        for t in range(1, self.n - 2 + 1):
            for j in range(1, self.n + 1):
                now1 = [-self.peg_integer(j, t), self.peg_integer(j, t + 1)]
                now2 = [self.peg_integer(j, t), -self.peg_integer(j, t + 1)]
                for i in range(self.m):
                    row = self.rows[i]
                    a, b, c = row
                    jump = (self.n - 2) * i * 2 + t
                    reversed_jump = (self.n - 2) * (2 * i + 1) + t
                    if a == j:
                        now1.append(jump)
                        now2.append(reversed_jump)
                    if b == j:
                        now1 += [jump, reversed_jump]
                    if c == j:
                        now1.append(reversed_jump)
                        now2.append(jump)
                clauses += [now1, now2]
        return clauses

    def all_clauses(self):
        return self.precondition_and_causal_axioms() + \
               self.frame_axioms() + \
               self.one_action_at_a_time() + \
               self.starting_state() + self.ending_state()

    def save_output(self):
        lines = []
        for i in test.all_clauses():
            s = ''
            for j in i:
                s += str(j) + ' '
            lines.append(s.rstrip() + '\n')
        lines.append('0\n')
        for i in range(self.m):
            row = self.rows[i]
            a, b, c = row
            for t in range(1, self.n - 2 + 1):
                jump = (self.n - 2) * i * 2 + t
                lines.append(f'{jump} Jump({a},{b},{c},{t})\n')
            for t in range(1, self.n - 2 + 1):
                reversed_jump = (self.n - 2) * (2 * i + 1) + t
                lines.append(f'{reversed_jump} Jump({c},{b},{a},{t})\n')
        for i in range(1, self.n + 1):
            for t in range(1, self.n):
                lines.append(f'{self.peg_integer(i, t)} Peg({i},{t})\n')
        with open('./data/front_end_output.txt', 'w') as f:
            f.writelines(lines)
        print('Output Successfully')


test = PropositionalEncoding()
test.initialize()
test.save_output()
