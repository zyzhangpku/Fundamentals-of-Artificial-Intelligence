def get_input():
    ans, key, x = [], [], 0
    with open('./data/back_end_input.txt', 'r') as f:
        lines = f.readlines()
    while True:
        try:
            i, s = map(str, lines[x].rstrip().split())
            x += 1
            ans.append((i, s))
        except ValueError:
            x += 1
            break
    while True:
        try:
            i, s = map(str, lines[x].rstrip().split())
            x += 1
            key.append((i, s))
        except IndexError:
            break
    moves = [s[-1] + '\n' for s in key if ans[int(s[0]) - 1][1] == 'T' and s[-1][0] == 'J']
    return sorted(moves, key=process)


def process(s):
    # Jump(*,*,*,t)
    i = len(s) - 1
    t = 0
    while s[i] != ',':
        i -= 1
    i += 1
    while s[i] != ')':
        t = t * 10 + int(s[i])
        i += 1
    return t


def output(move):
    with open('./data/back_end_output.txt', 'w') as f:
        if move:
            f.writelines(move)
        else:
            f.write('NO SOLUTION')
    print('Output successfully')


move = get_input()
output(move)
