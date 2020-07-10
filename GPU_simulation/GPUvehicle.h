#ifndef GPUVEHICLE_H
#define GPUVEHICLE_H 

//#include "sharedonGPU.h"

class GPUvehicle {
public:
	int vehicle_ID;
	int current_lane_ID;
	int current_road_ID;
	int entry_time;
	int start_time;
	int com_time;
	float distant;
	int next_lane;
	int next_road;
	int path_road[Maxpath];
	int path_directions[Maxpath];
	int path_num;
	int whole_num;
};

#endif