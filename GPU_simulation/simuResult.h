#ifndef SIMURESULT_H
#define SIMURESULT_H 
#include "sharedonGPU.h"

class simuResult
{
public:
	int flow[static_num][LaneSize];  //ͳ�Ƽ����������
	//int density[kLaneSize];
	float speed[static_num][LaneSize]; //ͳ�Ƽ�������ٶ�
	//int road_ID[kRoadSize];
	//int density[kRoadSize];
	//int speed[kRoadSize];
	int count[static_num][LaneSize];  //ͳ�Ƽ������������
	int avg_travel[static_num][LaneSize];  //ͳ�Ƽ������ƽ���г�ʱ��
	int complete[static_num][LaneSize];   //ͳ�Ƽ��������ɳ�����
	//int signal[static_num][LaneSize];     
	int travel[LaneSize];        
	int comlete_num[LaneSize];
	int begin_num[LaneSize];
	int total_complete[LaneSize];
};

#endif
