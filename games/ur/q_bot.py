import numpy as np
import ur_game
import math
# search with threads very important because it'll give an idea of what moves are best
# for each possible move, send 30 threads that play at random until a point is scored?
# or maybe until game is won. or maybe 3 points? large #'s of threads => will follow most likely paths
# will essentially give a distribution

# add learning aspect which is a conv-net (follow connect4 thing)

# or try learning aspect of q-table? approx. 2^20 * 36 * 2 = 10^8 = 100 million

# could try HTM (good first application of it)

# could try q-learning with heuristics (get extra value if have square on the hill, for double moves, for captures, for increasing score)
# would help reduce the state space a lot most likely (good approach) + simulation, get updated values based on simulation? or
# based on outcome? review connect 4 to see whether simulation or outcome mattered more
# heur_eval(board_state) - our turn = better (goes for 2x squares), tile on hill = better, more_score = better, more_tiles=better,
#   fewer_enemy_tiles = better
# i think it was use heur eval to search the state space, then use the simulation results and the outcome to update heur eval

TURN_BONUS = 25
HILL_BONUS = 25
SCORE_MUL = 4
TILES_MUL = 4
HILL = 7

class Urbot():
    def __init__(self, c):
        self.Q = {}
        self.N = {}
        self.visited = set()
        self.c = c

    def hval(self, state):      # this will seed the value for the Q table?
        score = 0
        if state.last_turn == state.w_turn:
            score += TURN_BONUS     # possibly remove this and make it implicit
        if state.board[state.w_turn, HILL]:
            score += HILL_BONUS
        score += float(state.score[state.w_turn] - state.score[1-state.w_turn]) * SCORE_MUL
        score += float(state.remain[state.w_turn] - state.remain[1-state.w_turn]) * TILES_MUL
        return score


    def get_heuristic_scores(self, state, legals):
        t_state = ur_game.board()
        vals = np.zeros(len(legals))
        for i, l in enumerate(legals):
            t_state.reset_to(state)
            t_state.move(l)
            vals[i] = self.hval(t_state)
        return vals


    def search(self, state):
        h_game = state.hash()
        if h_game not in self.visited:
            self.visited.add(h_game)
            moves = state.valid_moves()
            potential = self.get_heuristic_scores(state, moves)
            self.Q[h_game] = potential
            self.N[h_game] = np.zeros(len(moves))
            return np.random.choice(moves, softmax(potential))
        else:
            max_score = -float("inf")
            b_move = -1.212
            sum_sqrt = math.sqrt(sum(self.N[h_game]))
            for m_idx,move in enumerate(state.valid_moves()):
                ucb = self.Q[h_game][m_idx] + self.c * math.log(1+sum_sqrt/(1+self.N[h_game][m_idx]))
                if ucb >= max_score:
                    max_score = ucb
                    b_move = move
            return b_move, h_game


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()
