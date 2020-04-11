
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
#include "snek_api.h"
#include <string.h>
#include "ai_consts.h"
//void sort_indices(int keys[], int values[], int len){
//	int temp;
//	int cont = 1;
//	while (cont==1){
//		cont=0;
//		for (int i=0; i<len-1; i++){
//			if (values[i+1] < values[i]){
//				temp=values[i];
//				values[i] = values[i+1];
//				values[i+1]=temp;
//				temp=keys[i];
//				keys[i] = keys[i+1];
//				keys[i+1]=temp;
//				cont=1;
//			}
//		}
//		len--;
//	}
//}
//
void print_list(int gay[], int len){
	for (int i=0; i<len; i++){
		printf("%d ", gay[i]);
	}
	puts("\n");
}

void print_2dlist(int gay[][10], int len, int len2){
	for (int i=0; i<len; i++){
		for (int j=0; j<len2; j++){
		printf("%d", gay[i][j]);
		}
		printf("\n");
	}
	printf("################################################################################\n");
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


void print_path2(MovePath* mp){
	printf("[");
	MoveCell* iter = mp->tail;
	while (iter != NULL){
					printf("%d, ", iter->move);
					iter = iter->prev;
	}
	printf("\b\b]\n");
}

void print_path(MovePath* mp){
	printf("[");
	MoveCell* iter = mp->head;
	while (iter != NULL){
					printf("%d, ", iter->move);
					iter = iter->next;
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

void print_snek(GameBoard* gboard){
	printf("[");
	SnekBlock* iter = gboard->snek->head;
	while (iter != NULL){
					printf("(%d %d), ", iter->coord[x], iter->coord[y]);
					iter = iter->next;
	}
	printf("\b\b]\n");
}

void replace(MovePath* mp, int new_move, int idx){
	printf("asked for replace of %d at %d\n", new_move, idx);
	if (idx >= 0 && idx <= mp->length-1){
		MoveCell* start = mp->tail;
		for (int i=0; i < idx; i++) if (start->prev != NULL) start = start->prev; 
		start->move = new_move;
	}
	else {
		printf("Invalid idx(=%d) for list of size(=%d)", idx, mp->length);
	}
}

void append(MovePath* mp, int new_move){
	printf("asked for append of %d\n", new_move);
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
	printf("asked for insert of %d at %d\n", new_move, idx);
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
				printf("%d", i);
				if (start != NULL) start = start->prev;
				else break;
			}
			printf("\n");
			printf("n");
			new_cell->next = start->next;
			printf("i");
			new_cell->prev = start;
			printf("g");
			if (new_cell->next != NULL) new_cell->next->prev = new_cell;
			printf("g");
			if (new_cell->prev != NULL) new_cell->prev->next = new_cell;
			printf("e");
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
			printf("Invalid idx(=%d) for list of size(=%d)", idx, mp->length);
		}
	}
	(mp->length)++;
}

int in_bounds(int val){
	return val >= 0 && val < BOARD_SIZE;
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
	//if (gx->snex->length > 10)
	//	print_2dlist(reachable, 10, 10);
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
	printf("heres head_reach\n");
	print_2dlist(head_reach, 10, 10);
	printf("heres food_reach\n");
	print_2dlist(food_reach, 10, 10);
	gx->occupancy[start_y][start_x] = save_val;
	gx->occupancy[tail_y][tail_x] = 1;
	printf("chekcing loc (%d, %d)\n", iter->coord[x], iter->coord[y]);
	return food_reach[iter->coord[y]][iter->coord[x]];	
}

int delay_area(GameBoardX* gx, int dir){
	// fast way to check if there is there even a path to the goal (assuming snake stays fixed)
	int start_x = gx->snex->head->coord[x];
	int start_y = gx->snex->head->coord[y];
	if (start_y -1 < 0) return -1;
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
	gx->occupancy[start_y][start_x] += 1;
	gx->occupancy[tail_y][tail_x] = 0;
	int reachable[BOARD_SIZE][BOARD_SIZE];
	memset(reachable, 0, sizeof(int)*BOARD_SIZE*BOARD_SIZE);
	reachable[start_y][start_x] = 1;
	
	int delay_time = fill_area(gx, reachable)+2;
	delay_time = delay_time > gx->snex->length-2 ? gx->snex->length-2 : delay_time;
	delay_time = delay_time < 0 ? 0 : delay_time;

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
	gx->occupancy[start_y][start_x] -= 1;
	gx->occupancy[tail_y][tail_x] = 1;
	printf("checking loc (%d,%d)\n", iter->coord[x], iter->coord[y]);
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
	return reachable[dest_y][dest_x];
}				


int main(){
	//int ks[6] = {0,1,2,3,4,5};
	//int vs[6] = {100, 88, 77, 66, 55, 111};
	//print_list(ks, 6);
	//print_list(vs, 6);
	//sort_indices(ks, vs, 6);
	//print_list(ks, 6);
	//print_list(vs, 6);
	//int contig[3][3] = {{1,2,3,},{4,5,6},{7,8,9}};
	//print_2dlist(contig, 3, 3);
	//memset(contig, -1, sizeof(int)*3*3);
	//print_2dlist(contig, 3, 3);
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////				
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////				
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////				
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////				
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////				
	//MovePath* test = (MovePath*)malloc(sizeof(MovePath));
	//test->head = NULL;
	//test->tail = NULL;
	//test->length = 0;
	//append(test, 12);
	////print_path(test);
	//print_path2(test);
	//append(test, 5);
	//append(test, 7);
	//append(test, 39);
	////print_path(test);
	//print_path2(test);
	//printf("insert(40, 2)");
	//insert(test, 40, 2);
	//print_path2(test);
	//printf("insert(41, 4)");
	//insert(test, 41, 4);
	//print_path2(test);
	//printf("insert(-40, 0)");
	//insert(test, -40, 0);
	//print_path2(test);
	//printf("insert(45, test->legnth-1)");
	//insert(test, 45, test->length-1);
	//print_path2(test);
	//printf("insert(46, test->length)");
	//insert(test, 46, test->length);
	//print_path2(test);
	//printf("replace(7, 3)");
	//replace(test, 7, 3);
	//print_path2(test);
	//printf("reaplace(77, 0)");
	//replace(test, 77, 0);
	//print_path2(test);
	//printf("reaplace(777, test->length-1)");
	//replace(test, 777, test->length-1);
	//print_path2(test);
	//printf("reaplace(7777, test->length)");
	//replace(test, 7777, test->length);
	//print_path2(test);
	//printf("replace(77777, -1)");
	//replace(test, 77777, -1);
	//print_path2(test);
	//clean_move_path(&test);
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
	GameBoard* gb = init_board();
	GameBoardX* gx;
	int mv=-1;
	//int ways[4];
	//int waysx[4];
	
	//int old_tail_x[3];
	//int old_tail_y[3];
	
	//int resp='n';	
	while (mv!=4){
		show_board(gb);
		print_snek(gb);
	//	if (gb->snek->length >15){
	//		printf("do the check (y/n)? ");
	//		resp = getchar();
	//	}
  //  while ((getchar()) != '\n'); 
	//	if (resp == 'y'){
	//		valid_dirs(gb, ways);	
	//		gx = copy_to_boardx(gb);
	//		valid_dirsx(gx, waysx);
	//		
	//		show_boardx(gx, stdout);
	//					
	//		old_tail_x[0] = gx->snex->tail->coord[x];
	//		old_tail_y[0] = gx->snex->tail->coord[y];
	//		move_inf(NORTH, gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);
	//		old_tail_x[1] = gx->snex->tail->coord[x];
	//		old_tail_y[1] = gx->snex->tail->coord[y];
	//		move_inf(NORTH, gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);
	//		old_tail_x[2] = gx->snex->tail->coord[x];
	//		old_tail_y[2] = gx->snex->tail->coord[y];
	//		move_inf(NORTH, gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);
	//	
	//		unmove_inf(old_tail_x[2], old_tail_y[2], gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);
	//		unmove_inf(old_tail_x[1], old_tail_y[1], gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);
	//		unmove_inf(old_tail_x[0], old_tail_y[0], gx);
	//		show_boardx(gx, stdout);
	//		print_snex(gx);

	//		clean_gamex(&gx);
	//		print_list(ways, 4);
	//		print_list(waysx, 4);
	//	}
		
		gx = copy_to_boardx(gb);
		//printf("%d", valid_area(gx, NORTH, gx->snex->tail->coord[x], gx->snex->tail->coord[y]));
		if (gx->snex->length > 3 && gx->snex->head->coord[y] != 0){
			printf("%d", red_delay_areas(gx, NORTH, 1, 1, 10));
		}
		clean_gamex(&gx);
		printf("\n0=up, 1=right, 2=down, 3=left, 4=quit");
		mv = getchar() - '0';
    while ((getchar()) != '\n'); 
		switch(mv){
			case 0:
				advance_frame(AXIS_Y, UP, gb);
				break;
			case 1:
				advance_frame(AXIS_X, RIGHT, gb);
				break;
			case 2:
				advance_frame(AXIS_Y, DOWN, gb);
				break;
			case 3:
				advance_frame(AXIS_X, LEFT, gb);
				break;
			case 4:
				break;
		}
	}	
	gx = copy_to_boardx(gb);
	int old_x = gx->snex->tail->coord[x];
	int old_y = gx->snex->tail->coord[y];
	move(NORTH, gx);
	unmove(old_x, old_y, gx);
	clean_gamex(&gx);
	end_game(&gb);
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//	MovePath* test = (MovePath*)malloc(sizeof(MovePath));
//	test->head = NULL;
//	test->tail = NULL;
//	test->length = 0;
//	insert(test, 1, 0);
//	insert(test, 2, 1);
//	insert(test, 3, 2);
//	insert(test, 2, 3);
//	insert(test, 1, 4);
//	print_path2(test);
//	replace(test, 3, 3);
//	print_path2(test);
//	insert(test, 2, 4);
//	print_path2(test);
//	insert(test, 1, 5);
//	print_path2(test);
//	//insert(test, -1, 2);
//	//print_path2(test);
//	
//	clean_move_path(&test);	
	
	return 0;
}
