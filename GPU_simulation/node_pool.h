#ifndef NODE_POOL_H
#define NODE_POOL_H
#include "sharedonGPU.h"

class NodePool{     //nodeָ��������lane��
public:
	int Node_ID[LaneSize];
	int current_buffer[LaneSize];
	int buffer_counts[LaneSize];
	int up_lane_num[LaneSize];
	int up_lane_index[LaneSize][Maxuplane];
};
#endif