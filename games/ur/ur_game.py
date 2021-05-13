import numpy as np
#   —————————————
#   | D |   | D |
#   |———|———|———|
#   |   |   |   |
#   |———|———|———|
#   |   |   |   |
#   |———|———|———|
#   | S | D | S |
#   ————|———|————
#       |   |
#   ————|———|————
#   | E |   | E |
#   |———|———|———|
#   | D |   | D |
#   |———|———|———|
#   |   |   |   |
#   —————————————
HILL = 7  # hill is the location of the best square in the game
LENGTH = 14
PIECES = 7
DICE_SIZE = 4
BATTLE_LOWER = 4
BATTLE_UPPER = 11
AGAIN_SQUARES = [3, HILL, 13]
PROBS = [1/16, 4/16, 6/16, 4/16, 1/16]
PIECE_TYPE = np.int8

class Board():
    def __init__(self, board=None, remain=None, score=None, white_turn=1):
        if remain is None:
            self.remain = np.ones(2).astype(PIECE_TYPE)*PIECES
        else:
            self.remain = remain.copy()

        if score is None:
            self.score = np.zeros(2).astype(PIECE_TYPE)
        else:
            self.score = score.copy()

        if board is None:
            self.board = np.zeros((2, LENGTH)).astype(PIECE_TYPE)
        else:
            self.board = board.copy()
        self.w_turn = white_turn    # black's board is board[0,:], whites is board[1,:] so if whites turn is 1 it'll index that
        self.last_turn = 1 - white_turn

        self.roll = self.roll_one()
        while not self.roll:
            print("got a 0, moving turns")
            self.w_turn = 1 - self.w_turn
            self.roll = self.roll_one()

    def is_valid(self,new_pos):
        return (new_pos == LENGTH) or (new_pos < LENGTH and not self.board[self.w_turn, new_pos] and not (new_pos == HILL and self.board[1-self.w_turn, HILL]))

    def valid_moves(self):
        moves = []
        if self.roll != 0 and self.is_valid(-1+self.roll) and self.remain[self.w_turn] > 0:
            moves.append(-1)
        for pos in range(LENGTH):
            if self.board[self.w_turn,pos]:
                if self.is_valid(pos+self.roll):
                    moves.append(pos)  # can move this idx
        return moves

    def move(self, pos):
        new_pos = pos + self.roll
        # updates board
        if pos != -1:   # normal move
            self.board[self.w_turn, pos] = 0
        else:           # putting a new piece on
            self.remain[self.w_turn] -= 1

        if new_pos != LENGTH: # normal move
            self.board[self.w_turn, new_pos] = 1
        else:                   # scoring a point
            self.score[self.w_turn] += 1

        if (BATTLE_LOWER <= new_pos <= BATTLE_UPPER) and self.board[1-self.w_turn, new_pos]:  # capturing
            self.board[1-self.w_turn, new_pos] = 0
            self.remain[1-self.w_turn] += 1

        self.last_turn = self.w_turn
        if new_pos not in AGAIN_SQUARES:
            self.w_turn = 1 - self.w_turn

        self.roll = self.roll_one()
        while not self.roll:
            print("got a 0, moving turns")
            self.last_turn = self.w_turn
            self.w_turn = 1 - self.w_turn
            self.roll = self.roll_one()

    def reset_to(self, other):
        self.board = other.board.copy()
        self.score = other.score.copy()
        self.remain = other.score.copy()
        self.w_turn = other.w_turn
        self.roll = other.roll
        self.last_turn = other.last_turn

    def roll_one(self):
        return np.random.choice(DICE_SIZE+1, p=PROBS)

    def win_check(self):
        return self.score[self.last_turn] == PIECES  # checks if the last move was a winning one

    def hash(self):
        return hash(str(self.board) + str(self.remain) + str(self.w_turn) + str(self.roll))

"""save_board = np.array([[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]]).astype(PIECE_TYPE)

print(save_board.shape)
save_remain = np.array([2,0]).astype(PIECE_TYPE)
save_score = np.array([2,2]).astype(PIECE_TYPE)
save_turn = 0

game = Board(board=save_board, remain=save_remain, score=save_score, white_turn=save_turn)
bot = q_bot.Urbot(2)
"""
game = Board()
while True:
    print(game.board)
    #print("EVAL:", bot.hval(game))
    print("SCORE:", game.score)
    print("REMAIN:", game.remain)
    print("ROLL:", game.roll)
    print("WHITE'S TURN:", game.w_turn)
    curr_moves = game.valid_moves()
    print("MOVES:", curr_moves)
    print("MOVE HERE (idx): ", end="", flush=True)

    try:
        our_move = int(input())
    except ValueError:
        our_move = 9999

    if 0 <= our_move <= len(curr_moves):
        game.move(curr_moves[our_move])


