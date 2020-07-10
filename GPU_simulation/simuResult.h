#ifndef SIMURESULT_H
#define SIMURESULT_H 
#include "sharedonGPU.h"

class simuResult
{
public:
	int flow[static_num][LaneSize];  //统计间隔车道流量
	//int density[kLaneSize];
	float speed[static_num][LaneSize]; //统计间隔车道速度
	//int road_ID[kRoadSize];
	//int density[kRoadSize];
	//int speed[kRoadSize];
	int count[static_num][LaneSize];  //统计间隔车道车辆数
	int avg_travel[static_num][LaneSize];  //统计间隔车道平均行程时间
	int complete[static_num][LaneSize];   //统计间隔车道完成车辆数
	//int signal[static_num][LaneSize];     
	int travel[LaneSize];        
	int comlete_num[LaneSize];
	int begin_num[LaneSize];
	int total_complete[LaneSize];
};

#endif
