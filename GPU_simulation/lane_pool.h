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
	int queue_length[LaneSize];     //�Ŷӳ�����
	int lane_length[LaneSize];
	int max_vehicles[LaneSize];       //�������
	int output_capacity[LaneSize];    //��ͨ����������������
	int empty_space[LaneSize];      //ʣ������

	float alpha[LaneSize];
	float beta[LaneSize];
	float max_density[LaneSize];
	float max_speed[LaneSize];
	float min_speed[LaneSize];

	int vehicle_counts[LaneSize];         //��ǰ������
	int vehicle_start_index[LaneSize];
	int vehicle_end_index[LaneSize];
	int buffer_counts[LaneSize];
	int buffered_vehicle_start_index[LaneSize];
	int buffered_vehicle_end_index[LaneSize];

	bool vehicle_passed[LaneSize];   //�����Ƿ����
	//bool locked[kLaneSize];

	int signal[LaneSize];          //�Ƿ��ſ�
	int greenstart_time[LaneSize];     //�̵ƿ�ʼʱ��
	int green[LaneSize];           //�̵�ʱ��
	int cycle_offset[LaneSize];    //�����´��̵ƿ�ʼʱ���ʱ��

	int complete_num[LaneSize];
	int begin_num[LaneSize];

};

#endif
