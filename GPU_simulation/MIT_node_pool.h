#ifndef MIT_NODEPOOL_H
#define MIT_NODEPOOL_H
#include "sharedonGPU.h"

class MIT_NodePool {     //node指的是上游lane和
public:
	int down_road_ID[RoadSize];
	int down_lane_start[RoadSize];
	int down_lane_end[RoadSize];
	int up_lane_num[RoadSize];
	int up_lane_index[RoadSize][Maxuplane];
};
#endif
