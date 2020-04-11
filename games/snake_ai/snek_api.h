/**
AUTHOR: SAIMA ALI
LATEST WORKING VERSION 
FEBRUARY 2ND, 2020
ESC190H1S PROJECT
SNAKE API
 **/

#include <stdlib.h>
#include <stdio.h>

#define CYCLE_ALLOWANCE 1.5
#define BOARD_SIZE 10
#define PRINT 1

#define LIFE_SCORE 1 //score awarded for simply staying alive one frame

#define AXIS_X -1
#define AXIS_Y 1

#define UP -1
#define DOWN 1
#define LEFT -1
#define RIGHT 1

#define AXIS_INIT AXIS_Y
#define DIR_INIT DOWN

#define x 0
#define y 1

#define MOOGLE_POINT 20
#define HARRY_MULTIPLIER 3

extern int CURR_FRAME;
extern int SCORE;
extern int MOOGLE_FLAG;
extern int TIME_OUT;

typedef struct SnekBlock{
	int coord[2];
	struct SnekBlock* next;
} SnekBlock;

typedef struct Snek{
	struct SnekBlock* head;
	struct SnekBlock* tail;
	int length;
} Snek;

typedef struct GameBoard {
	int cell_value[BOARD_SIZE][BOARD_SIZE];
	int occupancy[BOARD_SIZE][BOARD_SIZE];
	struct Snek* snek;
} GameBoard;


GameBoard *init_board();
Snek *init_snek(int a, int b);
int hits_edge(int axis, int direction,  GameBoard *gameBoard);
int hits_self(int axis, int direction,  GameBoard *gameBoard);
int is_failure_state(int axis, int direction,  GameBoard *gameBoard);
int advance_frame(int axis, int direction,  GameBoard *gameBoard);
void end_game(GameBoard **board);
void show_board(GameBoard* gameBoard);
int get_score();

///////////////////////////////////////////////////////////////////////////////////////////

typedef struct SnexBlock{   // x => two-way cuz k and x are sort of similar letters but x has 2 lines on the left where k has 1
	int coord[2];
	struct SnexBlock* next;
	struct SnexBlock* prev;
} SnexBlock;

typedef struct Snex{
	struct SnexBlock* head;
	struct SnexBlock* tail;
	int length;
} Snex;

typedef struct GameBoardX {  // again x for two-way
	int cell_value[BOARD_SIZE][BOARD_SIZE];
	int occupancy[BOARD_SIZE][BOARD_SIZE];
	struct Snex* snex;
} GameBoardX;

int move(int dir, GameBoardX* gboard);
int unmove(int tail_x, int tail_y, GameBoardX* gboard);
GameBoardX* copy_to_boardx(GameBoard* gboard);
void clean_gamex(GameBoardX** gboard);
void valid_dirs(GameBoard* gboard, int dirs[]);
void valid_dirsx(GameBoardX* gboard, int dirs[]);
int hits_edgex(int axis, int direction,  GameBoardX* gboard);
int hits_selfx(int axis, int direction,  GameBoardX* gboard);
int is_failure_statex(int axis, int direction,  GameBoardX* gboard);

void show_boardx(GameBoardX* gx, FILE* loc);
int unmove_inf(int old_tail_x, int old_tail_y, GameBoardX* gx);
int move_inf(int dir, GameBoardX* gx);

typedef struct MoveCell{
	struct MoveCell* next;
	struct MoveCell* prev;
	int move;
} MoveCell;

typedef struct MovePath{
	struct MoveCell* head;
	struct MoveCell* tail;
	int length;
}	MovePath;


