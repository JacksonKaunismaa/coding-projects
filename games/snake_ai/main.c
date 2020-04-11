
#include <time.h>
#include "snek_api.h"
#include <unistd.h>
#include "ai_consts.h"
#include <string.h>
#include <limits.h>


#define MAX_TIME 1.0

int find_moggle(GameBoard* gboard, int coords[]){
	for (int i=0; i < BOARD_SIZE; i++){
		for (int j=0; j < BOARD_SIZE; j++){
			if ((gboard->cell_value)[i][j] > 0) {
				coords[y] = i;
				coords[x] = j;
				return 1;
			}
		}
	}
	return 0;
}

int in_bounds(int val){
	return val >= 0 && val < BOARD_SIZE;
}

void print_snek(GameBoard* gboard){
	printf("[");
	SnekBlock* iter = gboard->snek->head;
	while (iter != NULL){
					printf("(%d %d), ", iter->coord[x], iter->coord[y]);
					iter = iter->next;
	}
	printf("\b\b]\n");
}

void print_path(MovePath* mp){
	printf("[");
	MoveCell* iter = mp->tail;
	while (iter != NULL){
					printf("%d, ", iter->move);
					iter = iter->prev;
	}
	printf("\b\b]\n");
}

void print_snex(GameBoardX* gboard){
	printf("[");
	SnexBlock* iter = gboard->snex->head;
	while (iter != NULL){
					printf("(%d %d), ", iter->coord[x], iter->coord[y]);
					iter = iter->next;
	}
	printf("\b\b]\n");
}

void print_2dlist(int gay[BOARD_SIZE][BOARD_SIZE]){
	for (int i=0; i<BOARD_SIZE; i++){
		for (int j=0; j<BOARD_SIZE; j++){
		printf("%d", gay[i][j]);
		}
		printf("\n");
	}
	printf("################################################################################\n");
}

void print_list(int gay[], int len){
	for (int i=0; i<len; i++){
		printf("%d ", gay[i]);
	}
	printf("\n");
}


void clean_move_path(MovePath** mp){
	MoveCell* iter = (*mp)->head;
	MoveCell* temp;
	while (iter != NULL){
		temp = iter;
		iter = iter->next;
		free(temp);
	}
	free(*mp);
}

MovePath* init_move_path(){
	MovePath* temp = (MovePath*)malloc(sizeof(MovePath));
	temp->length = 0;
	temp->head = NULL;
	temp->tail = NULL;
	return temp;
}

void replace(MovePath* mp, int new_move, int idx){
	//printf("asked for replace of %d at %d\n", new_move, idx);
	if (idx >= 0 && idx <= mp->length-1){
		MoveCell* start = mp->tail;
		for (int i=0; i < idx; i++) if (start->prev != NULL) start = start->prev; 
		start->move = new_move;
	}
	else {
		if (PRINT) printf("Invalid idx(=%d) for list of size(=%d)", idx, mp->length);
	}
}

void append(MovePath* mp, int new_move){
	//printf("asked for append of %d\n", new_move);
	MoveCell* new_cell = (MoveCell*)malloc(sizeof(MoveCell));
	new_cell->move = new_move;
	new_cell->next = NULL;
	new_cell->prev = NULL;
	if (mp->head == NULL){
		mp->head = new_cell;
		mp->tail = new_cell;
	}	
	else {
		new_cell->next = NULL;
		new_cell->prev = mp->tail;
		mp->tail->next = new_cell;
		mp->tail = new_cell;
	}
	mp->length++;
}

void insert(MovePath* mp, int new_move, int idx){
	//printf("asked for insert of %d at %d\n", new_move, idx);
	// idx[0] = head, idx[-1] = tail
	//printf("len=(%d,%d)\n", mp->length, idx);
	MoveCell* new_cell = (MoveCell*)malloc(sizeof(MoveCell));
	new_cell->move = new_move;
	new_cell->next = NULL;
	new_cell->prev = NULL;
	if (mp->head == NULL){
		mp->head = new_cell;
		mp->tail = new_cell;
	}	
	else {
		if (idx > 0 && idx <= mp->length-1){
			MoveCell* start = mp->tail;
			for (int i=0; i < idx; i++){
				//printf("%d", i);
				if (start != NULL) start = start->prev;
				else break;
			}
			//printf("\n");
			//printf("n");
			new_cell->next = start->next;
			//printf("i");
			new_cell->prev = start;
			//printf("g");
			if (new_cell->next != NULL) new_cell->next->prev = new_cell;
			//printf("g");
			if (new_cell->prev != NULL) new_cell->prev->next = new_cell;
			//printf("e");
		}
		else if (idx == 0){
			append(mp, new_move);
			free(new_cell);
		}
		else if (idx == mp->length){
			//printf("nigger asked for an actual append\n");
			new_cell->next = mp->head;
			new_cell->prev = NULL;
			mp->head->prev = new_cell;
			mp->head = new_cell;
		}
		else {
			free(new_cell);
			if (PRINT) printf("Invalid idx(=%d) for list of size(=%d)", idx, mp->length);
		}
	}
	(mp->length)++;
}

int fill_area(GameBoardX* gx, int reachable[BOARD_SIZE][BOARD_SIZE]){
	int old_reachable = -1;
	int reachable_cnt = 0;
	while (reachable_cnt > old_reachable){
		old_reachable = reachable_cnt;
		for (int i=0; i<BOARD_SIZE; i++){
			for (int j=0; j<BOARD_SIZE; j++){
				if (reachable[j][i]==1){
					if (in_bounds(j+1) && gx->occupancy[j+1][i] == 0 && reachable[j+1][i] == 0)
						{reachable[j+1][i]=1; reachable_cnt++;}
					if (in_bounds(j-1) && gx->occupancy[j-1][i] == 0 && reachable[j-1][i] == 0)
						{reachable[j-1][i]=1; reachable_cnt++;}
					if (in_bounds(i+1) && gx->occupancy[j][i+1] == 0 && reachable[j][i+1] == 0)
						{reachable[j][i+1]=1; reachable_cnt++;}
					if (in_bounds(i-1) && gx->occupancy[j][i-1] == 0 && reachable[j][i-1] == 0)
						{reachable[j][i-1]=1; reachable_cnt++;}
				}
			}
		}	
	}
	return reachable_cnt;
}

int valid_cell(GameBoardX* gx, int xc, int yc){
	return in_bounds(xc) && in_bounds(yc) && gx->occupancy[yc][xc] == 0;
}

int path_back(GameBoardX* gx, int reachable[BOARD_SIZE][BOARD_SIZE], int xc, int yc, int dir){
	int xs1[3];
	int ys1[3];
	int xs2[3];
	int ys2[3];
	switch (dir){
		case NORTH:
			xs1[0] = xc;	ys1[0] = yc;
			xs1[1] = xc+1;	ys1[1] = yc;
			xs1[2] = xc+1;	ys1[2] = yc+1;
			
			xs2[0] = xc;	ys2[0] = yc;
			xs2[1] = xc-1;	ys2[1] = yc;
			xs2[2] = xc-1;	ys2[2] = yc+1;
			break;	
		case SOUTH:
			xs1[0] = xc;	ys1[0] = yc;
			xs1[1] = xc+1;	ys1[1] = yc;
			xs1[2] = xc+1;	ys1[2] = yc-1;
			
			xs2[0] = xc;	ys2[0] = yc;
			xs2[1] = xc-1;	ys2[1] = yc;
			xs2[2] = xc-1;	ys2[2] = yc-1;
			break;	
		case EAST:
			xs1[0] = xc;	ys1[0] = yc;
			xs1[1] = xc;	ys1[1] = yc-1;
			xs1[2] = xc-1;	ys1[2] = yc-1;
			
			xs2[0] = xc;	ys2[0] = yc;
			xs2[1] = xc;	ys2[1] = yc+1;
			xs2[2] = xc-1;	ys2[2] = yc+1;
			break;	
		case WEST:
			xs1[0] = xc;	ys1[0] = yc;
			xs1[1] = xc;	ys1[1] = yc-1;
			xs1[2] = xc+1;	ys1[2] = yc-1;
			
			xs2[0] = xc;	ys2[0] = yc;
			xs2[1] = xc;	ys2[1] = yc+1;
			xs2[2] = xc+1;	ys2[2] = yc+1;
			break;	
	}
	if (valid_cell(gx, xs1[0], ys1[0]) && valid_cell(gx, xs1[1], ys1[1]) && valid_cell(gx, xs1[2], ys1[2]) && reachable[ys1[2]][xs1[2]]) return 1;
	if (valid_cell(gx, xs2[0], ys2[0]) && valid_cell(gx, xs2[1], ys2[1]) && valid_cell(gx, xs2[2], ys2[2]) && reachable[ys2[2]][xs2[2]]) return 1;	
	return 0;
}

int reduced_delay_areas(GameBoardX* gx, int reachable[BOARD_SIZE][BOARD_SIZE], int sx, int sy){
	reachable[sy][sx] = 1;
	int old_reachable = -1;
	int reachable_cnt = 0;
	if (in_bounds(sy+1) && gx->occupancy[sy+1][sx] == 0 && reachable[sy+1][sx] == 0)
		{reachable[sy+1][sx]=1; reachable_cnt++;}
	if (in_bounds(sy-1) && gx->occupancy[sy-1][sx] == 0 && reachable[sy-1][sx] == 0) 
		{reachable[sy-1][sx]=1; reachable_cnt++;}
	if (in_bounds(sx+1) && gx->occupancy[sy][sx+1] == 0 && reachable[sy][sx+1] == 0)
		{reachable[sy][sx+1]=1; reachable_cnt++;}
	if (in_bounds(sx-1) && gx->occupancy[sy][sx-1] == 0 && reachable[sy][sx-1] == 0)
		{reachable[sy][sx-1]=1; reachable_cnt++;}
	while (reachable_cnt > old_reachable){
		old_reachable = reachable_cnt;
		for (int i=0; i<BOARD_SIZE; i++){
			for (int j=0; j<BOARD_SIZE; j++){
				if (reachable[j][i]==1){
					if (in_bounds(j+1) && gx->occupancy[j+1][i] == 0 && reachable[j+1][i] == 0 && path_back(gx, reachable, i, j+1, SOUTH))
						{reachable[j+1][i]=1; reachable_cnt++;}
					if (in_bounds(j-1) && gx->occupancy[j-1][i] == 0 && reachable[j-1][i] == 0 && path_back(gx, reachable, i, j-1, NORTH))
						{reachable[j-1][i]=1; reachable_cnt++;}
					if (in_bounds(i+1) && gx->occupancy[j][i+1] == 0 && reachable[j][i+1] == 0 && path_back(gx, reachable, i+1, j, EAST))
						{reachable[j][i+1]=1; reachable_cnt++;}
					if (in_bounds(i-1) && gx->occupancy[j][i-1] == 0 && reachable[j][i-1] == 0 && path_back(gx, reachable, i-1, j, WEST))
						{reachable[j][i-1]=1; reachable_cnt++;}
				}
			}
		}	
	}
	return reachable_cnt;
}


int red_delay_areas(GameBoardX* gx, int dir, int dx, int dy, int tout){
	int start_x = gx->snex->head->coord[x];
	int start_y = gx->snex->head->coord[y];
	switch(dir){
		case NORTH:
			start_y += UP;
			break;
		case SOUTH:
			start_y += DOWN;
			break;
		case EAST:
			start_x += RIGHT;
			break;
		case WEST:
			start_x += LEFT;
			break;
	}
	int tail_x = gx->snex->tail->coord[x];
	int tail_y = gx->snex->tail->coord[y];
	int save_val = gx->occupancy[start_y][start_x];
	//int COUNT_1 = count2d_list(gx->occupancy);	
	gx->occupancy[start_y][start_x] = 0;
	gx->occupancy[tail_y][tail_x] = 0;
	int head_reach[BOARD_SIZE][BOARD_SIZE];
	memset(head_reach, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	head_reach[start_y][start_x] = 1;
	int max_time = fill_area(gx, head_reach);
	max_time = max_time > tout ? tout : max_time;

	SnexBlock* iter = gx->snex->tail;
	for (int i=0; i<max_time; i++){
		gx->occupancy[iter->coord[y]][iter->coord[x]] = 0;
		if (iter->prev != NULL && i != max_time) iter = iter->prev;
	}
	int food_reach[BOARD_SIZE][BOARD_SIZE];
	memset(food_reach, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	reduced_delay_areas(gx, food_reach, dx, dy);	
	
	iter = gx->snex->tail;
	for (int i=0; i<max_time; i++){
		gx->occupancy[iter->coord[y]][iter->coord[x]] = 1;
		if (iter->prev != NULL && i != max_time-1 && i != max_time-2) iter = iter->prev;
	}
	gx->occupancy[start_y][start_x] = save_val;
	gx->occupancy[tail_y][tail_x] = 1;
	if (PRINT) fprintf(stderr, "chekcing reddelay loc (%d, %d)\n", iter->coord[x], iter->coord[y]);
	return food_reach[iter->coord[y]][iter->coord[x]];	
}

int delay_area(GameBoardX* gx, int dir, int dest_x, int dest_y, int timing){
	// fast way to check if there is there even a path to the goal (assuming snake stays fixed)
	int start_x = gx->snex->head->coord[x];
	int start_y = gx->snex->head->coord[y];
	switch(dir){
		case NORTH:
			start_y += UP;
			break;
		case SOUTH:
			start_y += DOWN;
			break;
		case EAST:
			start_x += RIGHT;
			break;
		case WEST:
			start_x += LEFT;
			break;
	}
	int tail_x = gx->snex->tail->coord[x];
	int tail_y = gx->snex->tail->coord[y];
	int save_val = gx->occupancy[start_y][start_x];
	//int COUNT_1 = count2d_list(gx->occupancy);	
	gx->occupancy[start_y][start_x] = 0;
	gx->occupancy[tail_y][tail_x] = 0;
	int reachable[BOARD_SIZE][BOARD_SIZE];
	memset(reachable, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	reachable[start_y][start_x] = 1;
	
	int delay_time = fill_area(gx, reachable)+2;
	delay_time = delay_time > gx->snex->length-2 ? gx->snex->length-2 : delay_time;
	delay_time = delay_time < 0 ? 0 : delay_time;
	if (timing != -1)
		delay_time = delay_time > timing ? timing : delay_time;

	SnexBlock* iter = gx->snex->tail;
	for (int i=0; i<delay_time; i++){
		gx->occupancy[iter->coord[y]][iter->coord[x]] = 0;
		if (iter->prev != NULL && i != delay_time) iter = iter->prev;
	}

	fill_area(gx, reachable);	
	iter = gx->snex->tail;
	for (int i=0; i<delay_time; i++){
		gx->occupancy[iter->coord[y]][iter->coord[x]] = 1;
		if (iter->prev != NULL && i != delay_time-1) iter = iter->prev;
	}
	gx->occupancy[start_y][start_x] = save_val;
	gx->occupancy[tail_y][tail_x] = 1;
	if (PRINT) fprintf(stderr, "checking loc (%d,%d)\n", iter->coord[x], iter->coord[y]);
	//fprintf(stderr, "also to verify the before(=%d) after(=%d) thing", COUNT_1, count2d_list(gx->occupancy));
	//if (count2d_list(gx->occupancy) != COUNT_1) fprintf(stderr, "nigger: start=%d, end=%d", COUNT_1, count2d_list(gx->occupancy));
	if (dest_x != -1 && dest_y != -1) return reachable[dest_y][dest_x];
	return reachable[iter->coord[y]][iter->coord[x]];
}				

int valid_area(GameBoardX* gx, int dir, int dest_x, int dest_y){
	// fast way to check if there is there even a path to the goal (assuming snake stays fixed)
	int start_x = gx->snex->head->coord[x];
	int start_y = gx->snex->head->coord[y];
	switch(dir){
		case NORTH:
			start_y += UP;
			break;
		case SOUTH:
			start_y += DOWN;
			break;
		case EAST:
			start_x += RIGHT;
			break;
		case WEST:
			start_x += LEFT;
			break;
	}
	if (start_x == dest_x && start_y == dest_y) return 1;
	int tail_x = gx->snex->tail->coord[x];
	int tail_y = gx->snex->tail->coord[y];
	gx->occupancy[start_y][start_x] += 1;
	gx->occupancy[tail_y][tail_x] = 0;
	int reachable[BOARD_SIZE][BOARD_SIZE];
	memset(reachable, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	reachable[start_y][start_x] = 1;
	fill_area(gx, reachable);
	gx->occupancy[start_y][start_x] -= 1;
	gx->occupancy[tail_y][tail_x] = 1;
	return reachable[dest_y][dest_x];
}				

int man_dist(int dest_x, int dest_y, int start_x, int start_y){
	return abs(dest_x-start_x) + abs(dest_y-start_y);
}

int man_dist_directional(int direction, int dest_x, int dest_y, int start_x, int start_y){
	switch(direction){
		case NORTH:
			return man_dist(dest_x, dest_y, start_x, start_y-1);
			break;
		case EAST:
			return man_dist(dest_x, dest_y, start_x+1, start_y);
			break;
		case SOUTH:
			return man_dist(dest_x, dest_y, start_x, start_y+1);
			break;
		case WEST:
			return man_dist(dest_x, dest_y, start_x-1, start_y);
			break;
	}
	return -1;
}

void sort_indices(int keys[], int values[], int len){
	int temp;
	int cont = 1;
	while (cont==1){
		cont=0;
		for (int i=0; i<len-1; i++){
			if (values[i+1] < values[i]){
				temp=values[i];
				values[i] = values[i+1];
				values[i+1]=temp;
				temp=keys[i];
				keys[i] = keys[i+1];
				keys[i+1]=temp;
				cont=1;
			}
		}
		len--;
	}
}

int* predict_tail_position(GameBoardX* gx, int head_x, int head_y, int hdist_flag){
	int tail_x = gx->snex->tail->coord[x];
	int tail_y = gx->snex->tail->coord[y];
	int hdist = man_dist(tail_x, tail_y, head_x, head_y)-1;
	hdist = hdist > 10 ? 10 : hdist;   // h can only be as big as 10
	hdist = hdist > gx->snex->length ? gx->snex->length-3 : hdist; // h cant be as big as snex-length
	hdist = hdist < 0 ? 0 : hdist;	// h cant be negative
	if (hdist == 0 || (hdist == 1 && hdist_flag <= 1)) return (int*)NULL;
	SnexBlock* iter = gx->snex->tail;
	for (int i=0; i<hdist; i++){
		if (iter->prev != NULL) iter = iter->prev;
	}
	//show_boardx(gx, stderr);
	if (PRINT) fprintf(stderr, "predicting loc (h=%d)as %d %d", hdist, iter->coord[x], iter->coord[y]);
	int* res = (int*)malloc(sizeof(int)*3);
	res[0] = iter->coord[x];
	res[1] = iter->coord[y];
	res[2] = hdist;
	return res;
}
								
int find_shortest_path_checker(GameBoardX* gx);




int shortest_path(int dest_x, int dest_y, GameBoardX* gboard, MovePath* mp, int tout, int ret_flag, int hdist_flag, time_t start,  
								int (*mv_f)(int, GameBoardX*), int (*unmv_f)(int, int, GameBoardX*)){
	// ret_flag = 0: just find the food(or tail in fixed location)
	// ret_flag = 1: find a path to the food such that you can make it back to the tail (inf_path or fixed position)
	// ret_flag = 2: using special inf functions (tail stays fixed) and valid_areas
	// ret_flag = 3: using normal functions (dyanmic tail location) and delay_areas and tail position predictions
	if (PRINT){
		show_boardx(gboard, stderr);
		fprintf(stderr, "retf=%d,d=%d,%d,t=%d,hd=%d\n", ret_flag, dest_x,dest_y, tout, hdist_flag);
	}
	int x_now = gboard->snex->head->coord[x];
	int y_now = gboard->snex->head->coord[y];
	if (ret_flag == 3){
		int* pred = predict_tail_position(gboard, x_now, y_now, hdist_flag);
		if (pred != NULL){
			dest_x = pred[x];
			dest_y = pred[y];
			if (pred[2] == 1) hdist_flag--;
			else hdist_flag = 8;
			free(pred);
		}
		else {
			dest_x = gboard->snex->tail->coord[x];
			dest_y = gboard->snex->tail->coord[y];
			ret_flag = 0;
		}
	}
	if (dest_x == x_now && y_now == dest_y){ 
		if (ret_flag == 1){			
			if (find_shortest_path_checker(gboard)) return 0;
			else return INT_MAX;
		}
		else return 0;   // if we at the destination
	}		
	if (tout - man_dist(dest_x, dest_y, x_now, y_now) <= 0) return INT_MAX;
	if (difftime(time(NULL), start) > MAX_TIME) return INT_MAX;
	else{	
		int old_tail_x = gboard->snex->tail->coord[x];  // for unmove purposes
		int old_tail_y = gboard->snex->tail->coord[y];
		int ways[4];   // load with the valid ways we can go at the current step
		int hdists[4]; // heuristic distances (uses manhattan distance)
		valid_dirsx(gboard, ways);  // actual figure out which ways we can go
		int dirs[4] = {0, 1, 2, 3};  // use as keys for direction to go in heurisitic search
		int valid_spot=0; 	// is there a single direction we can go from this spot?

		for (int i=0; i<4; i++){   // compute all heurisitc distances
			if (ways[i] == 1){
				hdists[i] = man_dist_directional(i, dest_x, dest_y, x_now, y_now);
				valid_spot=1;
			}
			else hdists[i] = INT_MAX;
		}
			
		if (valid_spot == 0) return INT_MAX; // no directions were valid, we cant go this direction
		sort_indices(dirs, hdists, 4);  // figure out heurisitc best direction
		int shortest_dist = INT_MAX;
		int actual_dist;

		for (int i=0; i<4; i++){
			if (hdists[i] < INT_MAX){
				if (ret_flag == 2){
					if (!valid_area(gboard,dirs[i],dest_x,dest_y))	continue;
				}
				else if (ret_flag == 3){
					if (!delay_area(gboard, dirs[i], -1, -1, -1)) continue;
				}
				else if (ret_flag == 1){
					if (!delay_area(gboard, dirs[i], dest_x, dest_y, tout)) continue;
				}
				else if (ret_flag == 0){
					if (!delay_area(gboard, dirs[i], dest_x, dest_y, tout)) continue;
				}
				(*mv_f)(dirs[i], gboard);
				actual_dist = shortest_path(dest_x, dest_y, gboard, mp, tout-1, ret_flag, hdist_flag, start, mv_f, unmv_f);
				(*unmv_f)(old_tail_x, old_tail_y, gboard);
				if (actual_dist < tout-1 && actual_dist != INT_MAX) { // weird way of saying actual_dist+1<time && actual_dist != INT_MAX
					append(mp, dirs[i]);
					return actual_dist + 1;
				}
			}
		}
		return shortest_dist;
	}
}


int find_shortest_path_checker(GameBoardX* gx){
	int dest_x = gx->snex->tail->coord[x];
	int dest_y = gx->snex->tail->coord[y];
	int timeout = BOARD_SIZE*BOARD_SIZE+BOARD_SIZE;
	MovePath* mp = init_move_path();
	int result;
	if (gx->snex->head->coord[x] == dest_x && gx->snex->head->coord[y] == dest_y) return 1;
	else {
		shortest_path(dest_x, dest_y, gx, mp, timeout, 2, -1, time(NULL), &move_inf, &unmove_inf);
		//shortest_path(dest_x, dest_y, gx, mp, timeout, 0, &move, &unmove);
		result = mp->length;
		clean_move_path(&mp);	
		if (result > 0) return 1;
	
		mp = init_move_path();
		shortest_path(dest_x, dest_y, gx, mp, timeout, 3, 8, time(NULL), &move, &unmove);
		result = mp->length;
		clean_move_path(&mp);
		if (result > 0) return 1;

		mp = init_move_path();
		shortest_path(dest_x, dest_y, gx, mp, timeout, 0, -1, time(NULL), &move, &unmove);
		result = mp->length;
		clean_move_path(&mp);	
		if (result > 0) return 1;
		
		else return 0;
	}
}


MovePath* _path_to_tail(GameBoardX* gx){
	int dest_x = gx->snex->tail->coord[x];
	int dest_y = gx->snex->tail->coord[y];
	int timeout = BOARD_SIZE*BOARD_SIZE+BOARD_SIZE;
	int result;
	
	if (PRINT) printf("Trying auto path_to_tail...\n");
	MovePath* mp = init_move_path();
	if (gx->snex->head->coord[x] == dest_x && gx->snex->head->coord[y] == dest_y) {clean_gamex(&gx); return mp;}
	
	if (PRINT) printf("Trying inf path_to_tail...\n");
	shortest_path(dest_x, dest_y, gx, mp, timeout, 2, -1, time(NULL), &move_inf, &unmove_inf);
	result = mp->length;
	if (result > 0) {clean_gamex(&gx); return mp;}
	clean_move_path(&mp);	
	
	if (PRINT) printf("Trying dynamic path_to_tail...\n");
	mp = init_move_path();
	shortest_path(dest_x, dest_y, gx, mp, timeout, 3, 8, time(NULL), &move, &unmove);
	result = mp->length;
	if (result > 0) {clean_gamex(&gx); return mp;}
	clean_move_path(&mp);	

	if (PRINT) printf("Trying fixed path_to_tail...\n");
	mp = init_move_path();
	shortest_path(dest_x, dest_y, gx, mp, timeout, 0, -1, time(NULL), &move, &unmove);
	result = mp->length;
	if (result > 0) {clean_gamex(&gx); return mp;}
	clean_move_path(&mp);	

	mp = init_move_path();
	return mp;
}

MovePath* path_to_tail(GameBoard* gb){
	GameBoardX* gx = copy_to_boardx(gb);
	MovePath* mp = _path_to_tail(gx); // since the _path_to_tail function cleans it?
	return mp;
}


MovePath* find_shortest_path(int dest_x, int dest_y, GameBoard* gboard, int ret_flag, int timeout){
	GameBoardX* gboardx = copy_to_boardx(gboard);
	MovePath* mp = init_move_path();
	shortest_path(dest_x, dest_y, gboardx, mp, timeout, ret_flag, -1, time(NULL), &move, &unmove);
	clean_gamex(&gboardx);
	return mp;
}


int still_path_exists(int dest_x, int dest_y, GameBoard* gboard, int ret_flag, int timeout, int move_dir){
	GameBoardX* gboardx = copy_to_boardx(gboard);
	MovePath* mp = init_move_path();
	move(move_dir, gboardx); 
	shortest_path(dest_x, dest_y, gboardx, mp, timeout, ret_flag, -1, time(NULL), &move, &unmove);
	int res = 0;
	if (mp->length > 0) res = 1;
	clean_move_path(&mp);
	clean_gamex(&gboardx);
	return res;
}

void show_valids(GameBoard* gb){
	GameBoardX* gx = copy_to_boardx(gb);
	int ways[4];
	valid_dirsx(gx, ways);
	print_list(ways, 4);
	//sleep(5000);	
	clean_gamex(&gx);
}

int move_board(GameBoard* gboard, int our_dir){
	//getchar();
	if (PRINT) printf("making move %d ,len is %d\n", our_dir, gboard->snek->length);
	switch (our_dir){
		case NORTH:
			return advance_frame(AXIS_Y, UP, gboard);
			break;
		case SOUTH:
			return advance_frame(AXIS_Y, DOWN, gboard);
			break;
		case WEST:
			return advance_frame(AXIS_X, LEFT, gboard);
			break;
		default:  // case: EAST
			return advance_frame(AXIS_X, RIGHT, gboard);
			break;	
	}
}

int heuristic_move(GameBoard* gboard){
	int ways[4];
	valid_dirs(gboard, ways);
	for (int i=0; i<4; i++){
		if (PRINT) printf("5th\n");
		if (ways[i]) return i;
	}
	return 0;
}

void translate(int* x_pos, int* y_pos, int move){
	switch(move){
		case NORTH:
			*y_pos += UP;
			break;
		case SOUTH:
			*y_pos += DOWN;
			break;
		case WEST:
			*x_pos += LEFT;
			break;
		case EAST:
			*x_pos += RIGHT;
			break;
	}
}

void utranslate(int* x_pos, int* y_pos, int move){
	switch(move){
		case NORTH:
			*y_pos -= UP;
			break;
		case SOUTH:
			*y_pos -= DOWN;
			break;
		case WEST:
			*x_pos -= LEFT;
			break;
		case EAST:
			*x_pos -= RIGHT;
			break;
	}
}

int extend_path_maybe(MovePath* mp, int i, int mv, int used[BOARD_SIZE][BOARD_SIZE], int alt_mv, int x_now, int y_now, GameBoardX* gx){
	translate(&x_now, &y_now, alt_mv);
	//printf("checking new coords (%d, %d)\n", x_now, y_now);
	if (in_bounds(x_now) && in_bounds(y_now) && !used[y_now][x_now] && gx->occupancy[y_now][x_now] == 0){
		translate(&x_now, &y_now, mv);
		//printf("passed first check, checking new coords (%d, %d)\n", x_now, y_now);
		if (in_bounds(x_now) && in_bounds(y_now) && !used[y_now][x_now] && gx->occupancy[y_now][x_now] == 0){   // therefore its valid extension
			//printf("passed both checks!\n");
			used[y_now][x_now] = 1;
			utranslate(&x_now, &y_now, mv);
			used[y_now][x_now] = 1;
			replace(mp, alt_mv, i);
			//print_path(mp);
			insert(mp, mv, i+1);
			//print_path(mp);
			insert(mp, (alt_mv+2)%4, i+2);
			//print_path(mp);
			//printf("new used list\n");
			//print_2dlist(used);
			//print_path(mp);
			return 1;
		}
	}	
	return 0;
}
void extend_food_path(MovePath* mp, GameBoard* gb){		// assume its the path to food we are extending
	GameBoardX* gx = copy_to_boardx(gb);
	MoveCell* iter = mp->tail;
	int used[BOARD_SIZE][BOARD_SIZE];
	memset(used, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	//printf("init path: ");
	//print_path(mp);
	while (iter != NULL){
		//printf("%d, %d\n", gx->snex->head->coord[x], gx->snex->head->coord[y]);
		used[gx->snex->head->coord[y]][gx->snex->head->coord[x]] = 1;
		move(iter->move, gx);
		iter = iter->prev;	
	}  // move snex to food to compute path back to tail
	MovePath* ftt = _path_to_tail(gx);
	gx = copy_to_boardx(gb);
	iter = mp->tail;	
	while (iter != NULL){
		used[gx->snex->head->coord[y]][gx->snex->head->coord[x]] = 1;
		move(iter->move, gx);
		iter = iter->prev;	
	}  // move snex to food to compute path back to tail
	iter = ftt->tail;	
	while (iter != NULL){		// highlight all squares that snex needs after eating to get back to the tail, and move snex to tail
		//printf("%d, %d\n", gx->snex->head->coord[x], gx->snex->head->coord[y]);
		used[gx->snex->head->coord[y]][gx->snex->head->coord[x]] = 1;
		move(iter->move, gx);
		iter = iter->prev;
	}
	
	clean_gamex(&gx); // reset snex back to initial posion should already be cleaned
	gx = copy_to_boardx(gb); // reset snex back to initial posion
	//printf("mmmkay so here is our used grid for now\n");
	//print_2dlist(used);
	iter = mp->tail;			// eg. iter = move 2, after = move 3
	int i=0; // corresponds to the idx of iter move

	int mv;
	int alt_mv1;
	int alt_mv2;
	int x_now = gx->snex->head->coord[x];
	int y_now = gx->snex->head->coord[y];
	while (iter != NULL && mp->length + 2 + CURR_FRAME < TIME_OUT){  // because length increases in increments of 2
		mv = iter->move;
		alt_mv1 = (mv + 1+16)%4;
		alt_mv2 = (mv - 1+16)%4;
		//printf("looking to extend path, mv=%d, i=%d, alt1=%d, alt2=%d, x=%d, y=%d\n", mv, i, alt_mv1, alt_mv2, x_now, y_now);
		//print_path(mp);	
		if (extend_path_maybe(mp, i, mv, used, alt_mv1, x_now, y_now, gx)){
			i=0;
			iter = mp->tail;
			x_now = gx->snex->head->coord[x];
			y_now = gx->snex->head->coord[y];
			continue;
		}
		if (extend_path_maybe(mp, i, mv, used, alt_mv2, x_now, y_now, gx)){
			i=0;
			iter = mp->tail;
			x_now = gx->snex->head->coord[x];
			y_now = gx->snex->head->coord[y];
			continue;
		}
		i++;
		translate(&x_now, &y_now, iter->move);
		iter = iter->prev;
	}
	clean_move_path(&ftt);
	clean_gamex(&gx);
}


void ai_play() {
	long long delay = 40000;
	//board initialized, struct has pointer to snek
	GameBoard* board = init_board();
	if (PRINT)
		show_board(board);
	GameBoardX* bcopy;

	int play_on = 1;
	int coord[2];
	
	int floc[2];
	int ffound;
	
	MovePath* mp;
	MoveCell* mc;

	int screwed = 0;
	int food_path = 0;
	while (play_on){
		if (board->snek->length >= BOARD_SIZE*BOARD_SIZE) break;
		coord[x] = board->snek->head->coord[x];
		coord[y] = board->snek->head->coord[y];
		
		
		if (PRINT){
			show_board(board);
			printf("HEADLOC: (%d, %d)\n", coord[x], coord[y]);
			print_snek(board);
		}

		ffound = find_moggle(board, floc);
		if (ffound){
			bcopy = copy_to_boardx(board);
			if (valid_area(bcopy,-1,floc[x],floc[y])){
				if (PRINT){
					printf("FOODLOC: (%d, %d)\n", floc[x], floc[y]);
					show_valids(board);
				}
				food_path = 1;
				if (board->snek->length >= 3) mp = find_shortest_path(floc[x], floc[y], board, 1, TIME_OUT - CURR_FRAME);
				else mp = find_shortest_path(floc[x], floc[y], board, 0, TIME_OUT - CURR_FRAME);
				
				mc = mp->tail;
				if (mp->length == 0) {ffound = 0; food_path = 0;}
				
				if (PRINT) print_path(mp);
				extend_food_path(mp, board);
				//getchar();
				
				if (PRINT) print_path(mp);
				while (mc != NULL && play_on && food_path){
					play_on = move_board(board, mc->move);
					if (PRINT) show_board(board);
					mc = mc->prev;	
					if (PRINT) usleep(delay);
				}
				if (play_on) clean_move_path(&mp);
			}
			else ffound = 0;
			clean_gamex(&bcopy);
		}
		if (board->snek->length < 3 || screwed == 1){
			play_on = move_board(board, heuristic_move(board));
			if (PRINT) usleep(delay);
		}
		else{
			mp = path_to_tail(board);
			mc = mp->tail;
			if (PRINT) print_path(mp);
			if (mp->length == 0 && food_path == 0) screwed = 1;
			while (mc != NULL && play_on && !ffound && !screwed){
				if (PRINT) printf("Pathing back to tail, move buf is %d\n", mc->move);
				
				play_on = move_board(board, mc->move);
				
				if (PRINT) show_board(board);
				mc = mc->prev;
				ffound = find_moggle(board, floc);
				if (PRINT) usleep(delay);
				if (food_path == 0 && CURR_FRAME > 40 && ffound && mc != NULL){    // last ditch effort to pick up last moggle if life is no longer possible (if no path from food to tail exists)
					if (still_path_exists(floc[x], floc[y], board, 0, TIME_OUT - CURR_FRAME, -1) && // if path exists right now
													!still_path_exists(floc[x], floc[y], board, 0, TIME_OUT - CURR_FRAME-1, mc->move)){   // if path wont exist after this move
						clean_move_path(&mp);
						mp = find_shortest_path(floc[x], floc[y], board, 0, TIME_OUT - CURR_FRAME);
						mc = mp->tail;
						if (PRINT){
							printf("Going for last ditch effort!\n");
							print_path(mp);
						}
						while (mc != NULL && play_on){
							play_on = move_board(board, mc->move);
							if (PRINT) show_board(board);
							mc = mc->prev;
							if (PRINT) usleep(delay);
						}
						clean_move_path(&mp);
						screwed = 1;
					}
				}
			}
			if (!screwed) clean_move_path(&mp);
		}
	}
	if (board->snek->length < 4){
		show_board(board);	
	}
	printf("%d\t%d\n", SCORE, board->snek->length);
	end_game(&board);
}

int main(){
	ai_play();
	return 0;
}
