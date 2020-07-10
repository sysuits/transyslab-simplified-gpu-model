#ifndef LANE_POOL_H
#define LANE_POOL_H
//#include "GPUvehicle.h"
#include "sharedonGPU.h"

class LanePool {
	
public:
	int lane_ID[LaneSize];
	int road_ID[LaneSize];
	int direction[LaneSize];
	
	int flow[LaneSize];
	float density[LaneSize];
	float speed[LaneSize];
	int queue_length[LaneSize];     //排队车辆数
	int lane_length[LaneSize];
	int max_vehicles[LaneSize];       //最大容量
	int output_capacity[LaneSize];    //即通行能力、饱和流率
	int empty_space[LaneSize];      //剩余容量

	float alpha[LaneSize];
	float beta[LaneSize];
	float max_density[LaneSize];
	float max_speed[LaneSize];
	float min_speed[LaneSize];

	int vehicle_counts[LaneSize];         //当前车辆数
	int vehicle_start_index[LaneSize];
	int vehicle_end_index[LaneSize];
	int buffer_counts[LaneSize];
	int buffered_vehicle_start_index[LaneSize];
	int buffered_vehicle_end_index[LaneSize];

	bool vehicle_passed[LaneSize];   //车道是否放行
	//bool locked[kLaneSize];

	int signal[LaneSize];          //是否信控
	int greenstart_time[LaneSize];     //绿灯开始时间
	int green[LaneSize];           //绿灯时长
	int cycle_offset[LaneSize];    //距离下次绿灯开始时间的时差

	int complete_num[LaneSize];
	int begin_num[LaneSize];

};

#endif
