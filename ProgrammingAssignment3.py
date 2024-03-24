import numpy as np

NSides = 2
LTarget = 6
UTarget = 7
NDice = 3
M = 100
NGames = 10000


def define_game():
    # input of the setting of the game
    global NSides, LTarget, UTarget, NDice, M, NGames
    NSides = int(input('NSides= '))
    LTarget = int(input('LTarget= '))
    UTarget = int(input('UTarget= '))
    NDice = int(input('NDice= '))
    M = int(input('M= '))
    NGames = int(input('NGames= '))


class GameEngine:
    def __init__(self):
        self.player1 = None
        self.player2 = None  # two AI players
        self.n_game = NGames
        self.n_dice = NDice
        self.l_target = LTarget
        self.u_target = UTarget
        self.win_count = np.zeros((self.l_target, self.l_target, 1 + self.n_dice), int)
        self.lose_count = np.zeros((self.l_target, self.l_target, 1 + self.n_dice), int)
        self.best_nums = np.zeros((self.l_target, self.l_target), int)  # the answer PLAY
        self.prob = np.zeros((self.l_target, self.l_target))  # the answer PROB

    def opponent_player(self, player):
        # given player 1 or 2, return its opponent
        return self.player1 if player == self.player2 else self.player2

    def initialize(self):
        # after each game, player 1 and 2 need to be initialized
        self.player1 = BlackJackAI(self.win_count, self.lose_count)
        self.player2 = BlackJackAI(self.win_count, self.lose_count)

    def update_counts(self, winner):
        # called when a game ends
        # update win_count and lose_count
        for x, y, n in winner.cache:
            self.win_count[x, y, n] += 1
        for x, y, n in self.opponent_player(winner).cache:
            self.lose_count[x, y, n] += 1

    def game_ends(self, player, delta):
        # given a number of a player's outcome of rolling dices, judge whether the game ends and the winner
        if player.score + delta > self.u_target:
            return True, self.opponent_player(player)
        elif player.score + delta >= self.l_target:
            return True, player

        # if the game doesn't end, add the player's score
        player.score += delta
        return False, None

    def play_one_round(self, p1, p2):
        # one player roll dices base on the current state
        p1.opp_score = p2.score
        delta = p1.one_move()
        ends, winner = self.game_ends(p1, delta)
        if ends:
            self.update_counts(winner)
        return ends

    def play_one_game(self):
        # play one game, iterate until there is a winner
        while True:
            if self.play_one_round(self.player1, self.player2):
                break
            if self.play_one_round(self.player2, self.player1):
                break

    def repeat_games(self):
        # repeat a game for NGame times
        for _ in range(self.n_game):
            self.initialize()
            self.play_one_game()
        self.extract_answer()

    def extract_answer(self):
        # when NGame games ends, extract the final answer

        def cal_answer(x, y):
            # given the win_count and lose_count, the AI should calculate the best move and prob of winning
            answer_ai.score = x
            answer_ai.opp_score = y
            best_num = answer_ai.choose_best_k()[0]
            p = answer_ai.f(best_num, 0)
            return best_num, p

        answer_ai = BlackJackAI(self.win_count, self.lose_count)
        for i in range(self.l_target):
            for j in range(self.l_target):
                self.best_nums[i, j], self.prob[i, j] = cal_answer(i, j)


class BlackJackAI:
    def __init__(self, win_count, lose_count):
        self.n_sides = NSides
        self.n_dice = NDice
        self.m = M
        self.win_count = win_count
        self.lose_count = lose_count
        self.score = 0
        self.opp_score = 0
        self.cache = []  # store when a decision is made, the current state of 2 players' scores

    def roll_dices(self, num):
        # roll dices for num times, return the score
        return np.sum(np.random.randint(1, self.n_sides + 1, size=num))

    def choose_num_with_probability(self, probabilities):
        # choose the num of the dice to roll given probabilities
        return np.random.choice(np.arange(1, self.n_dice + 1), p=probabilities)

    def choose_best_k(self):
        # decide the best number of dices to row, given f(k)
        f_values = np.array([self.f(k) for k in range(1, self.n_dice + 1)])
        return np.argmax(f_values) + 1, f_values

    def choose_dice_num(self):
        # choose the number of dices to roll, with explore/exploit trade-off
        best_k, f_values = self.choose_best_k()
        s = np.sum(f_values) - f_values[best_k - 1]
        T = self.cal_T()
        p_best_k = self.p_best_k(T, best_k)
        prob = [p_best_k if k == best_k else self.p_k(k, p_best_k, T, s) for k in range(1, self.n_dice + 1)]
        return self.choose_num_with_probability(prob)

    def cal_T(self):
        # calculate T
        return np.sum(self.win_count[self.score, self.opp_score, 1:self.n_dice + 1] +
                      self.lose_count[self.score, self.opp_score, 1:self.n_dice + 1])

    def p_best_k(self, T, best_k):
        # calculate the probability to "exploit"
        return 1 + self.m * (1 - self.n_dice) / (T * self.f(best_k) + self.n_dice * self.m)

    def p_k(self, k, p_best_k, T, s):
        # calculate the probability to "explore"
        return (1 - p_best_k) * (T * self.f(k) + self.m) / (s * T + (self.n_dice - 1) * self.m)

    def f(self, k, default=0.5):
        # calculate f(k)
        base = self.win_count[self.score, self.opp_score, k] + self.lose_count[self.score, self.opp_score, k]
        if base == 0:
            return default  # when extracting answer, it should return 0 if no winning prob, not 0.5
        return self.win_count[self.score, self.opp_score, k] / base

    def one_move(self):
        # the score it attains in a move
        best_n_dice = self.choose_dice_num()
        self.cache.append((self.score, self.opp_score, best_n_dice))
        return self.roll_dices(best_n_dice)


if __name__ == '__main__':
    define_game()
    game = GameEngine()
    game.repeat_games()
    print('PLAY=\n', game.best_nums)
    print('PROB=\n', game.prob)
