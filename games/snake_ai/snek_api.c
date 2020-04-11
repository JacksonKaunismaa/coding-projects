#include "snek_api.h"
#include <string.h>
#include <time.h>
#include "ai_consts.h"


int CURR_FRAME = 0;
int SCORE = 0;
int MOOGLE_FLAG = 0;
int MOOGLES_EATEN = 0;
int TIME_OUT = ((BOARD_SIZE * 4) - 4) * CYCLE_ALLOWANCE;

GameBoard* init_board(){
	srand(time(0));
	GameBoard* gameBoard = (GameBoard*)(malloc(sizeof(GameBoard)));

	for (int i = 0; i < BOARD_SIZE; i++){
		for (int j = 0; j < BOARD_SIZE; j++){
			gameBoard->cell_value[i][j] = 0;
			gameBoard->occupancy[i][j] = 0;
		}
	}
	gameBoard->occupancy[0][0] = 1; //snake initialized
	gameBoard->snek = init_snek(0, 0);
	return gameBoard;
}

Snek* init_snek(int a, int b){
	Snek* snek = (Snek *)(malloc(sizeof(Snek)));

	snek->head = (SnekBlock *)malloc(sizeof(SnekBlock));
	snek->head->coord[x] = a;
	snek->head->coord[y] = b;

	snek->tail = (SnekBlock *)malloc(sizeof(SnekBlock));
	snek->tail->coord[x] = a;
	snek->tail->coord[y] = b;

	snek->tail->next = NULL;
	snek->head->next = snek->tail;
	
	snek->length = 1;

	return snek;
}

//updated
int hits_edge(int axis, int direction, GameBoard* gameBoard){
	if (((axis == AXIS_Y) && ((direction == UP && gameBoard->snek->head->coord[y] + UP < 0) || (direction == DOWN && gameBoard->snek->head->coord[y] + DOWN > BOARD_SIZE - 1)))
	   || (axis == AXIS_X && ((direction == LEFT && gameBoard->snek->head->coord[x] + LEFT < 0) || (direction == RIGHT && gameBoard->snek->head->coord[x] + RIGHT > BOARD_SIZE-1))))
	{
		return 1;
	} else {
		return 0;
	}

}

//updated
int hits_self(int axis, int direction, GameBoard *gameBoard){
	int new_x, new_y;
	if (axis == AXIS_X){
		new_x = gameBoard->snek->head->coord[x] + direction;
		new_y = gameBoard->snek->head->coord[y];
	} else if (axis == AXIS_Y){
		new_x = gameBoard->snek->head->coord[x];
		new_y = gameBoard->snek->head->coord[y] + direction;
	}
	if ((gameBoard->snek->length != 1) && 
		(new_y == gameBoard->snek->tail->coord[y] && new_x == gameBoard->snek->tail->coord[x]))
	{
		return 0; //not hit self, this is the tail which will shortly be moving out of the way
	} else {
		return gameBoard->occupancy[new_y][new_x]; //1 if occupied
	}
}

int time_out(){
	return (MOOGLE_FLAG == 1 && CURR_FRAME > TIME_OUT);

}

int is_failure_state(int axis, int direction, GameBoard *gameBoard){
	return (hits_edge(axis, direction, gameBoard) || time_out() || hits_self(axis, direction, gameBoard));   // switched order of functions because memory leaks leads to very obvious error
}

void populate_moogles(GameBoard *gameBoard){
	if (MOOGLE_FLAG == 0){
		int r1 = rand() % BOARD_SIZE;
		int r2 = rand() % BOARD_SIZE;
		
		/// ADDED TO MAKE CODE LESS SHIT AND ILLOGICAL
		int fails=100000; // assuming worst case scenario (eg. BOARD_SIZE=50, length=2499) the probablity this results in a bad spot is 4.2*10^-16
		while (gameBoard->occupancy[r1][r2] && fails > 0){
			r1 = rand() % BOARD_SIZE;
			r2 = rand() % BOARD_SIZE;
			fails--;
		}
		/// ADDED TO MAKE CODE LESS SHIT AND ILLOGICAL
		
		int r3 = rand() % (BOARD_SIZE * 10);
		if (r3 == 0){
			gameBoard->cell_value[r1][r2] = MOOGLE_POINT * HARRY_MULTIPLIER;
			MOOGLE_FLAG = 1;
		} else if (r3 < BOARD_SIZE){
			gameBoard->cell_value[r1][r2] = MOOGLE_POINT;
			MOOGLE_FLAG = 1;
		}
	}
}

void eat_moogle(GameBoard* gameBoard, int head_x, int head_y) {
	SCORE = SCORE + gameBoard->cell_value[head_y][head_x];
	gameBoard->cell_value[head_y][head_x] = 0;

	gameBoard->snek->length ++;
	MOOGLES_EATEN ++;
	MOOGLE_FLAG = 0;
	CURR_FRAME = 0;
}

int advance_frame(int axis, int direction, GameBoard *gameBoard){
	if (is_failure_state(axis, direction, gameBoard)){
		return 0;
	} else {
		// update the occupancy grid and the snake coordinates
		int head_x, head_y;
		// figure out where the head should now be
		if (axis == AXIS_X) {
			head_x = gameBoard->snek->head->coord[x] + direction;
			head_y = gameBoard->snek->head->coord[y];
		} else if (axis == AXIS_Y){
			head_x = gameBoard->snek->head->coord[x];
			head_y = gameBoard->snek->head->coord[y] + direction;
		}
		
		int tail_x = gameBoard->snek->tail->coord[x];
		int tail_y = gameBoard->snek->tail->coord[y];

		// update the occupancy grid for the head
		gameBoard->occupancy[head_y][head_x] = 1;

		if (gameBoard->snek->length > 1) { //make new head
			SnekBlock *newBlock = (SnekBlock *)malloc(sizeof(SnekBlock));
			newBlock->coord[x] = gameBoard->snek->head->coord[x];
			newBlock->coord[y] = gameBoard->snek->head->coord[y];
			newBlock->next = gameBoard->snek->head->next;

			gameBoard->snek->head->coord[x] = head_x;
			gameBoard->snek->head->coord[y] = head_y;
			gameBoard->snek->head->next = newBlock;
	
			if (gameBoard->cell_value[head_y][head_x] > 0){  //eat something
				eat_moogle(gameBoard, head_x, head_y);
			} else { //did not eat
				//delete the tail
				gameBoard->occupancy[tail_y][tail_x] = 0;	
				gameBoard->occupancy[head_y][head_x] = 1; ///////////////////////////////////////////////////// reset the head just in case 
				SnekBlock *currBlock = gameBoard->snek->head;
				while (currBlock->next != gameBoard->snek->tail){
					currBlock = currBlock->next;
				} //currBlock->next points to tail

				currBlock->next = NULL;
				free(gameBoard->snek->tail);
				gameBoard->snek->tail = currBlock;
			}

		} else if ((gameBoard->snek->length == 1) && gameBoard->cell_value[head_y][head_x] == 0){ // change both head and tail coords, head is tail
			gameBoard->occupancy[tail_y][tail_x] = 0;
			gameBoard->snek->head->coord[x] = head_x;
			gameBoard->snek->head->coord[y] = head_y;
			gameBoard->snek->tail->coord[x] = head_x;
			gameBoard->snek->tail->coord[y] = head_y;
			
		} else { //snake is length 1 and eats something
			eat_moogle(gameBoard, head_x, head_y);
			gameBoard->snek->head->coord[x] = head_x;
			gameBoard->snek->head->coord[y] = head_y;
		}

		// update the score and board
		SCORE = SCORE + LIFE_SCORE;
		if (MOOGLE_FLAG == 1){
			CURR_FRAME ++;
		}

		// populate moogles
		populate_moogles(gameBoard);
		return 1;
	} 
}

void show_board(GameBoard* gameBoard) {
	fprintf(stdout, "\033[2J"); // clear terminal ANSI code
	fprintf(stdout, "\033[0;0H"); // reset cursor position
	
	char blank = 	'-';   // >using number to represent chars... (changed value)
	char snek = 	'S';  
	char moogle = 	'X';
	char border_block = '|';     //// added
	char head_block = 'H';			//// added
	char tail_block = 'T';		/////added

	char border[BOARD_SIZE*2+4];    ///// added 
	memset(border, '*', BOARD_SIZE*2+4-1);   ////added
	border[BOARD_SIZE*2+4-1] = '\0';

	int head_x = gameBoard->snek->head->coord[x];
	int head_y = gameBoard->snek->head->coord[y];
	int tail_x = gameBoard->snek->tail->coord[x];
	int tail_y = gameBoard->snek->tail->coord[y];

	fprintf(stdout, "%s\n", border);    ////  addded
	for (int i = 0; i < BOARD_SIZE; i++){
		fprintf(stdout, "%c", border_block);   ///adeded 
		for (int j = 0; j < BOARD_SIZE; j++){
			fprintf(stdout, " ");		 /////// spaces added
			if (gameBoard->occupancy[i][j] == 1){
				//snake is here
				if (i == head_y && j == head_x) fprintf(stdout, "%c", head_block);    ///// all modified and changed to make better
				else if (i == tail_y && j == tail_x ) fprintf(stdout, "%c", tail_block);	///// all modified and changed to make better
				else fprintf(stdout, "%c", snek);			///// all modified and changed to make better
			} else if (gameBoard->cell_value[i][j] > 0) {
				//there be a moogle
				fprintf(stdout, "%c", moogle);
			} else {
				//nothing to see here
				fprintf(stdout, "%c", blank);
			}
		} //new line
		fprintf(stdout, " %c", border_block);     ///// addded
		fprintf(stdout, "\n");	
	}
	fprintf(stdout, "%s", border);			////// added

	fprintf(stdout, "\n\n");
	
	if (MOOGLE_FLAG == 1){
		fprintf(stdout, "!..ALERT, MOOGLE IN VICINITY..!\n\n");
	}
	fprintf(stdout, "SCORE: %d\n", SCORE);
	fprintf(stdout, "YOU HAVE EATEN %d MOOGLES\n\n", MOOGLES_EATEN);

	fprintf(stdout, "SNEK HEAD\t(%d, %d)\n", gameBoard->snek->head->coord[x], gameBoard->snek->head->coord[y]);
	fprintf(stdout, "SNEK TAIL\t(%d, %d)\n", gameBoard->snek->tail->coord[x], gameBoard->snek->tail->coord[y]);
	fprintf(stdout, "LENGTH \t%d\n", gameBoard->snek->length);
	fprintf(stdout, "CURR FRAME %d vs TIME OUT %d\n", CURR_FRAME, TIME_OUT);


	fflush(stdout);
}

int get_score() {
	return SCORE;
}

void end_game(GameBoard **board){
	//fprintf(stdout, "\033[2J");
	//fprintf(stdout, "\033[0;0H"); 
	if (PRINT) fprintf(stdout, "\n\n\n--!!---GAME OVER---!!--\n\nYour score: %d\n\n\n\n", SCORE);
	if (PRINT) fflush(stdout);
	// need to free all allocated memory
	// first snek
	SnekBlock **snekHead = &((*board)->snek->head);
	SnekBlock *curr;
	SnekBlock *prev;
	while ((*snekHead)->next != NULL) {
		curr = *snekHead;
		while (curr->next != NULL){
			prev = curr;
			curr = curr->next;
		}
		prev->next = NULL;
		free(curr);
	}
	free(*snekHead);
	free((*board)->snek);
	free(*board);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void clean_gamex(GameBoardX **board){
	SnexBlock* iter = (*board)->snex->tail; 
	SnexBlock* back;
	while (iter != NULL){
		back = iter;
		iter = iter->prev;
		free(back);
	}
	free((*board)->snex);
	free(*board);
}

//	GameBoardX* gboard2 = (GameBoardX*)(malloc(sizeof(GameBoardX)));
//
//	for (int i = 0; i < BOARD_SIZE; i++){
//		for (int j = 0; j < BOARD_SIZE; j++){
//			gboard2->cell_value[i][j] = gboard->cell_value[i][j];
//			gboard2->occupancy[i][j]  = gboard->occupancy[i][j];
//		}
//	}
//
//	Snex* snex2 = (Snex*)malloc(sizeof(Snex));
//	SnexBlock* forward;
//	SnexBlock* backward = (SnexBlock*)malloc(sizeof(SnexBlock));
//	snex2->head = backward;
//
//	SnekBlock* curr = gboard->snek->head;   //iterate through current snake
//	backward->coord[x] = curr->coord[x];
//	backward->coord[y] = curr->coord[y];
//	curr = curr->next;
//
//	while (curr != NULL){
//			forward = (SnexBlock*)malloc(sizeof(SnexBlock));
//			forward->coord[x] = curr->coord[x];
//			forward->coord[y] = curr->coord[y];
//			
//			backward->next = forward;
//			forward->prev = backward;
//			//forward->next = NULL;
//			
//			curr = curr->next;
//			backward = forward;
//	}
//	snex2->length = gboard->snek->length;
//	snex2->tail = forward;
//	snex2->tail->next = NULL;
//	snex2->head->prev = NULL;
//	gboard2->snex = snex2;
//	return gboard2;
int advance_framex(int axis, int direction, GameBoardX* gboard) {
	/// only takes legal moves so no need to check for collisions, eating moogles, or creating a new SnexBlock
		// update the occupancy grid and the snake coordinates
		int head_x, head_y;
		// figure out where the head should now be
		if (axis == AXIS_X) {
			head_x = gboard->snex->head->coord[x] + direction;
			head_y = gboard->snex->head->coord[y];
		} 
		else {//(axis == AXIS_Y)
			head_x = gboard->snex->head->coord[x];
			head_y = gboard->snex->head->coord[y] + direction;
		}
		
		int tail_x = gboard->snex->tail->coord[x];
		int tail_y = gboard->snex->tail->coord[y];


		// update the occupancy grid for the head and tail 
		gboard->occupancy[tail_y][tail_x] = 0;
		gboard->occupancy[head_y][head_x] = 1;

		if (gboard->snex->length > 1) { //make new head	
			SnexBlock* new_block = (SnexBlock*)malloc(sizeof(SnexBlock));			// its a tradeoff between two things. Moving pointers around to their 'prev' attribute means we have to delete one block
			new_block->coord[x] = gboard->snex->head->coord[x];				// and therefore create another one (O(1)), or if we want to not delete any nodes and teleport them, we have to copy 2n ints
			new_block->coord[y] = gboard->snex->head->coord[y];				// we'll empirically test both to see what happens TODO.
			new_block->next = gboard->snex->head->next;
			new_block->prev = gboard->snex->head;   //gboard->snex->head->prev;
			new_block->next->prev = new_block;

			gboard->snex->head->coord[x] = head_x;
			gboard->snex->head->coord[y] = head_y;
			gboard->snex->head->next = new_block;
			//SnexBlock* temp = gboard->snex->tail;
			
			
			if (gboard->cell_value[head_y][head_x] == 0){
				gboard->snex->tail = gboard->snex->tail->prev;
				free(gboard->snex->tail->next);
				gboard->snex->tail->next = NULL;
			}
			else {
				(gboard->snex->length)++; 
				gboard->occupancy[tail_y][tail_x] = 1;
				// dont change cell_value so that unmove can detect it for later
			}
			
			
			
			/*SnexBlock* iter = gboard->snex->head;
			while (iter != NULL){
				iter->next->coord[x] = iter->coord[x];
				iter->next->coord[y] = iter->coord[y];
				iter = iter->next;
			}
			gboard->snex->head->coord[x] = head_x;
			gboard->snex->head->coord[y] = head_y;*/
		}
		else if (gboard->snex->length == 1) {
			gboard->snex->head->coord[x] = head_x;
			gboard->snex->head->coord[y] = head_y;
			gboard->snex->tail->coord[x] = head_x;
			gboard->snex->tail->coord[y] = head_y;
		} 
		return 1;
}

int unmove(int old_tail_x, int old_tail_y, GameBoardX* gboard){
		int head_x, head_y;
		
		head_y = gboard->snex->head->coord[y];
		head_x = gboard->snex->head->coord[x];
		
		// update the occupancy grid for the head and tail 
		gboard->occupancy[old_tail_y][old_tail_x] = 1;
		gboard->occupancy[head_y][head_x] = 0;

		if (gboard->snex->length > 1) { //make new tail	
			
			if (gboard->cell_value[head_y][head_x] == 0){			
				SnexBlock *new_block = (SnexBlock *)malloc(sizeof(SnexBlock));			// its a tradeoff between two things. Moving pointers around to their 'prev' attribute means we have to delete one block
				new_block->coord[x] = gboard->snex->tail->coord[x];				// and therefore create another one (O(1)), or if we want to not delete any nodes and teleport them, we have to copy 2n ints
				new_block->coord[y] = gboard->snex->tail->coord[y];				// we'll empirically test both to see what happens TODO.
				new_block->next = gboard->snex->tail;
				new_block->prev = gboard->snex->tail->prev; 
				new_block->prev->next = new_block;

				gboard->snex->tail->coord[x] = old_tail_x;
				gboard->snex->tail->coord[y] = old_tail_y;
				gboard->snex->tail->prev = new_block;
			//SnexBlock* temp = gboard->snex->head;
			}
			else { 
				(gboard->snex->length)--;
			}
			gboard->snex->head = gboard->snex->head->next;
			free(gboard->snex->head->prev);
			gboard->snex->head->prev = NULL;
			
			
			/*SnexBlock* iter = gboard->snex->tail;
			while (iter != NULL){
				iter->prev->coord[x] = iter->coord[x];
				iter->prev->coord[y] = iter->coord[y];
				iter = iter->prev;
			}
			gboard->snex->tail->coord[x] = old_tail_x;
			gboard->snex->tail->coord[y] = old_tail_y;*/
		}
		else if (gboard->snex->length == 1) {
			gboard->snex->head->coord[x] = old_tail_x;
			gboard->snex->head->coord[y] = old_tail_y;
			gboard->snex->tail->coord[x] = old_tail_x;
			gboard->snex->tail->coord[y] = old_tail_y;
		} 
		return 1;

}

int move(int dir, GameBoardX* gboard){
	int ret = 1;
	switch (dir) {
		case NORTH:
					ret = advance_framex(AXIS_Y, UP, gboard);
					break;
		case EAST:
					ret = advance_framex(AXIS_X, RIGHT, gboard);
					break;
		case SOUTH:
					ret = advance_framex(AXIS_Y, DOWN, gboard);
					break;
		case WEST:
					ret = advance_framex(AXIS_X, LEFT, gboard);
					break;
	}
	return ret;
}

int move_inf(int dir, GameBoardX* gboard){
	int head_x = gboard->snex->head->coord[x];
	int head_y = gboard->snex->head->coord[y];
	switch(dir){
		case NORTH:
			head_y += UP;
			break;
		case SOUTH:
			head_y += DOWN;
			break;
		case WEST:
			head_x += LEFT;
			break;
		case EAST:
			head_x += RIGHT;
			break;
	}
	//if (gboard->snex->length > 15){
	//	show_boardx(gboard, stderr);
	//	fprintf(stderr, "length = %d\n", gboard->snex->length);
	//	fprintf(stderr, "moving, dir = %d\n################################\n###########################3\n#############################\n", dir);
	//}
	gboard->cell_value[head_y][head_x] += 1; 
	switch (dir) {
		case NORTH:
					return advance_framex(AXIS_Y, UP, gboard);
		case EAST:
					return advance_framex(AXIS_X, RIGHT, gboard);
		case SOUTH:
					return advance_framex(AXIS_Y, DOWN, gboard);
		case WEST:
					return advance_framex(AXIS_X, LEFT, gboard);
	}
	return -1;
}

int unmove_inf(int old_tail_x, int old_tail_y, GameBoardX* gboard){
	int head_x = gboard->snex->head->coord[x];
	int head_y = gboard->snex->head->coord[y];
	int res = unmove(old_tail_x, old_tail_y, gboard);
	if (gboard->cell_value[head_y][head_x] > 0) gboard->cell_value[head_y][head_x] -= 1; 
	//if (gboard->snex->length > 15){
	//	show_boardx(gboard, stderr);
	//	fprintf(stderr, "length = %d\n", gboard->snex->length);
	//	fprintf(stderr, "unmoving, oldp = %d,%d\n################################\n#################################\n########################\n",old_tail_x, old_tail_y);
	//}
	return res;
}


GameBoardX* copy_to_boardx(GameBoard* gboard){	
	GameBoardX* gboard2 = (GameBoardX*)(malloc(sizeof(GameBoardX)));

	for (int i=0; i < BOARD_SIZE; i++){
		for (int j=0; j < BOARD_SIZE; j++){
			gboard2->cell_value[i][j] = gboard->cell_value[i][j];
			gboard2->occupancy[i][j]  = gboard->occupancy[i][j];
		}
	}

	Snex* snex2 = (Snex*)malloc(sizeof(Snex));
	SnexBlock* forward = NULL;
	SnexBlock* backward = (SnexBlock*)malloc(sizeof(SnexBlock));
	snex2->head = backward;

	SnekBlock* curr = gboard->snek->head;   //iterate through current snake
	backward->coord[x] = curr->coord[x];
	backward->coord[y] = curr->coord[y];
	curr = curr->next;

	while (curr != NULL){
			forward = (SnexBlock*)malloc(sizeof(SnexBlock));
			forward->coord[x] = curr->coord[x];
			forward->coord[y] = curr->coord[y];
			
			backward->next = forward;
			forward->prev = backward;
			//forward->next = NULL;
			
			curr = curr->next;
			backward = forward;
	}
	snex2->length = gboard->snek->length;
	if (forward != NULL) snex2->tail = forward;
	else snex2->tail = backward;
	snex2->tail->next = NULL;
	snex2->head->prev = NULL;
	gboard2->snex = snex2;
	return gboard2;
}

int hits_edgex(int axis, int direction, GameBoardX* gboard){
	if (((axis == AXIS_Y) && ((direction == UP && gboard->snex->head->coord[y] + UP < 0) || (direction == DOWN && gboard->snex->head->coord[y] + DOWN > BOARD_SIZE - 1)))
	   || (axis == AXIS_X && ((direction == LEFT && gboard->snex->head->coord[x] + LEFT < 0) || (direction == RIGHT && gboard->snex->head->coord[x] + RIGHT > BOARD_SIZE-1))))
	{
		return 1;
	} else {
		return 0;
	}

}

//updated
int hits_selfx(int axis, int direction, GameBoardX* gboard){
	int new_x, new_y;
	if (axis == AXIS_X){
		new_x = gboard->snex->head->coord[x] + direction;
		new_y = gboard->snex->head->coord[y];
	} else if (axis == AXIS_Y){
		new_x = gboard->snex->head->coord[x];
		new_y = gboard->snex->head->coord[y] + direction;
	}
	if ((gboard->snex->length != 1) && 
		(new_y == gboard->snex->tail->coord[y] && new_x == gboard->snex->tail->coord[x]))
	{
		return 0; //not hit self, this is the tail which will shortly be moving out of the way
	} else {
		return gboard->occupancy[new_y][new_x]; //1 if occupied
	}
}

int is_failure_statex(int axis, int direction, GameBoardX* gboard){
	return (hits_edgex(axis, direction, gboard) || hits_selfx(axis, direction, gboard)); 
}


void valid_dirs(GameBoard* gboard, int dirs[]){
	dirs[NORTH] = 1-is_failure_state(AXIS_Y, UP, gboard);
	dirs[SOUTH] = 1-is_failure_state(AXIS_Y, DOWN, gboard);
	dirs[WEST] =  1-is_failure_state(AXIS_X, LEFT, gboard);
	dirs[EAST] =  1-is_failure_state(AXIS_X, RIGHT, gboard);
}


void valid_dirsx(GameBoardX* gboard, int dirs[]){
	dirs[NORTH] = 1-is_failure_statex(AXIS_Y, UP, gboard);
	dirs[SOUTH] = 1-is_failure_statex(AXIS_Y, DOWN, gboard);
	dirs[WEST] =  1-is_failure_statex(AXIS_X, LEFT, gboard);
	dirs[EAST] =  1-is_failure_statex(AXIS_X, RIGHT, gboard);
}

void show_boardx(GameBoardX* gameBoard, FILE* loc) {
	//fprintf(stdout, "\033[2J"); // clear terminal ANSI code
	//fprintf(stdout, "\033[0;0H"); // reset cursor position
	
	char blank = 	'.';   // >using number to represent chars... (changed value)
	char snek = 	'S';  
	char moogle = 	'M';
	char border_block = '|';     //// added
	char head_block = 'H';			//// added
	char tail_block = 'T';		/////added

	char border[BOARD_SIZE*2+4];    ///// added 
	memset(border, '*', BOARD_SIZE*2+4-1);   ////added
	border[BOARD_SIZE*2+4-1] = '\0';

	int head_x = gameBoard->snex->head->coord[x];
	int head_y = gameBoard->snex->head->coord[y];
	int tail_x = gameBoard->snex->tail->coord[x];
	int tail_y = gameBoard->snex->tail->coord[y];

	fprintf(loc, "%s\n", border);    ////  addded
	for (int i = 0; i < BOARD_SIZE; i++){
		fprintf(loc, "%c", border_block);   ///adeded 
		for (int j = 0; j < BOARD_SIZE; j++){
			fprintf(loc, " ");		 /////// spaces added
			if (gameBoard->occupancy[i][j] == 1){
				//snake is here
				if (i == head_y && j == head_x) fprintf(loc, "%c", head_block);    ///// all modified and changed to make better
				else if (i == tail_y && j == tail_x ) fprintf(loc, "%c", tail_block);	///// all modified and changed to make better
				else fprintf(loc, "%c", snek);			///// all modified and changed to make better
			} else if (gameBoard->cell_value[i][j] > 0) {
				//there be a moogle
				fprintf(loc, "%c", moogle);
			} else {
				//nothing to see here
				fprintf(loc, "%c", blank);
			}
		} //new line
		fprintf(loc, " %c", border_block);     ///// addded
		fprintf(loc, "\n");	
	}
	fprintf(loc, "%s", border);			////// added

	fprintf(loc, "\n\n");
}
