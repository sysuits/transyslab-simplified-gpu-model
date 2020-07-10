#ifndef ROAD_POOL_H
#define ROAD_POOL_H
#include "sharedonGPU.h"

class RoadPool {
public:
	int Road_ID[RoadSize];
	int lane_count[RoadSize];
	float density[RoadSize];
	float speed[RoadSize];
	int count[RoadSize];
	int complete_num[RoadSize];
	int begin_num[RoadSize];
	int length[RoadSize];
	int park[RoadSize][park_cap];
	int park_num[RoadSize];
	int park_output[RoadSize];
	int lane_start_index[RoadSize];
	int lane_end_index[RoadSize];

	int up_node_index[RoadSize];
	int down_node_index[RoadSize];

};
#endif
