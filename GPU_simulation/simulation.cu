
#include <cmath>
#include <stdint.h>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <string>
#include <map>
#include "GPUmemory.h"
#include "simuResult.h"
#include <cuda_runtime.h>
#include <iostream>
#include <cstring>
#include <vector>
#include "GPUvehicle.h"
//#include "GPU_kernel.cuh"
#include "device_functions.h"
#include "demand.h"
//#include <windows.h>
#include<time.h>
#include <assert.h>

using namespace std;

GPUmemory* gpu_data;
GPUvehicle *CPU_veh;
GPUvehicle *GPU_veh;
Demand *gpu_demand;
int memory_space_for_vehicles = TotalVehNum * sizeof(GPUvehicle);

simuResult* GPUResult;
simuResult* CPUResult=NULL;

bool InitilizeGPU(string road_file, string lane_file, string veh_file, string node_file);     
bool InitGPUData(GPUmemory* cpu_data,Demand* cpu_demand,string road_file, string lane_file, string veh_file, string node_file);            //��ʼ�� GPUmemory
bool StartSimulation();

vector<string> &split(const std::string &s, char delim, std::vector<std::string> &elems)
{
	std::stringstream ss(s);
	std::string item;
	while (std::getline(ss, item, delim)) {
		elems.push_back(item);
	}
	return elems;
}
vector<string> split_str(string str, string pattern)
{
	string::size_type pos;
	vector<string> result;
	str += pattern;
	size_t size = str.size();
	for (size_t i = 0; i < size; i++)
	{
		pos = str.find(pattern, i);
		if (pos < size)
		{
			string s = str.substr(i, pos - i);
			result.push_back(s);
			i = pos + pattern.size() - 1;
		}
	}
	return result;
}

//���������
int main(int argc, char** argv) {
	printf("argc ->%d\n", argc);
	for (int i = 0; i < argc; i++)
	{
		std::cout << "argument[" << i << "] is: " << argv[i] << endl;
	}
	string road_file = argv[1];
	string lane_file = argv[2];
	string veh_file = argv[3];
	string node_file = argv[4];
	//string output_file= argv[5];
	//string MIT_node_file= argv[6];
	InitilizeGPU(road_file, lane_file, veh_file, node_file); //��ʼ��CPU��GPU���ݲ�����
	std::cout << "Initlition Complete" << std::endl;
	StartSimulation();   //���л�����
	std::cout << "Simulation Succeed!" << endl;
	//cudaDeviceReset();   //����GPU��Ϣ
}

bool InitilizeGPU(string road_file, string lane_file, string veh_file, string node_file) {
	gpu_data = NULL;
	GPUmemory* cpu_data = new GPUmemory();
	Demand* cpu_demand = new Demand();
	InitGPUData(cpu_data, cpu_demand, road_file, lane_file, veh_file, node_file); //��ʼ����������
	//���ݴ���
	if (cudaMalloc((void**)&GPU_veh, memory_space_for_vehicles) != cudaSuccess) {
		cerr << "cudaMalloc((void**)&GPU_veh, memory_space_for_vehicles" << endl;
	}
	if (cudaMalloc((void**)&gpu_demand, sizeof(NewVehicle)*TotalTimeSteps) != cudaSuccess) {
		cerr<<"cudaMalloc((void**)&gpu_demand, sizeof(NewVehicle)*TotalTimeSteps) failed"<< endl;
	}
	if (cudaMalloc((void**)&gpu_data, (cpu_data->total_size())) != cudaSuccess) {
		cerr << "cudaMalloc((void**)&gpu_data, 2 * (cpu_data->total_size()) failed" << endl;
	}
	if (cudaMalloc((void**)&GPUResult, sizeof(simuResult)) != cudaSuccess){
		cerr << "cudaMalloc((void**)&GPUResult, memory_space_outputs) failed" << endl;
	}
	if (cudaMallocHost((void **)&CPUResult, sizeof(simuResult)) != cudaSuccess){
		cerr <<"cudaMallocHost((void **)&CPUResult, sizeof(simuResult)) failed"<< endl;
	}
	//cudaMemcpy(GPUResult, CPUResult, memory_space_outputs, cudaMemcpyHostToDevice);
	if (cudaMemcpy(GPU_veh, CPU_veh, memory_space_for_vehicles, cudaMemcpyHostToDevice) != cudaSuccess) {
		cerr << "cudaMemcpy(GPU_veh, CPU_veh, memory_space_for_vehicles, cudaMemcpyHostToDevice failed" << endl;
	}
	if (cudaMemcpy(gpu_data, cpu_data, (cpu_data->total_size()), cudaMemcpyHostToDevice)!= cudaSuccess) {
		cerr << "cudaMemcpy(gpu_data, cpu_data, (cpu_data->total_size()), cudaMemcpyHostToDevice); failed" << endl;
	}
	if (cudaMemcpy(gpu_demand, cpu_demand, sizeof(NewVehicle)*TotalTimeSteps, cudaMemcpyHostToDevice) != cudaSuccess) {
		cerr << "cudaMemcpy(gpu_demand, cpu_demand, sizeof(NewVehicle)*TotalTimeSteps, cudaMemcpyHostToDevice) failed" << endl;
	}
	return true;
}

//��ʼ����������
bool InitGPUData(GPUmemory* cpu_data, Demand* cpu_demand,string road_file, string lane_file, string veh_file, string node_file) {
	
	int veh_start = 0;
	int veh_index = 0;
	//���������ļ�
	for (int q = 0; q < TotalTimeSteps; q++) {
		for (int p = 0; p < RoadSize; p++) {
			cpu_demand->new_vehicle_everystep[q].Lane_ID[p] = p;
			cpu_demand->new_vehicle_everystep[q].new_vehicle_size[p] = 0;
		}
	}
	for (int i = 0; i < NetworkMaxNum; i++) {
		cpu_data->lane_vehicle_space.vehicle_space[i] = -1;
		cpu_data->buffer_vehicle_space.buffer_space[i] = -1;
	}
	std::cout << "new_vehicle_everystep initial complete" << endl;
	//����·���ļ�
	std::string line;
	std::ifstream myfile(road_file.c_str());
	vector<int> road_len;
	if (myfile.is_open()) {
		int index = 0;
		while (getline(myfile, line)) {
			vector<string> res;
			split(line, ':', res);
			cpu_data->road_pool.Road_ID[index] = atoi(res[0].c_str());
			cpu_data->road_pool.up_node_index[index] = atoi(res[1].c_str());
			cpu_data->road_pool.down_node_index[index] = atoi(res[2].c_str());
			cpu_data->road_pool.length[index] = atoi(res[3].c_str());
			cpu_data->road_pool.lane_start_index[index] = atoi(res[4].c_str());
			cpu_data->road_pool.lane_end_index[index] = atoi(res[5].c_str());
			cpu_data->road_pool.lane_count[index] = atoi(res[5].c_str()) - atoi(res[4].c_str());
			cpu_data->road_pool.park_num[index]=0;
			cpu_data->road_pool.park_output[index] = 2;
			road_len.push_back(atoi(res[3].c_str()));
			index++;
		}
		myfile.close();
	}
	std::cout << "road data input complete" << endl;
	//���س����ļ�
	std::string line2;
	std::ifstream myfile2(lane_file.c_str());
	int lane_num = 0;
	if (myfile2.is_open()) {
		int lane_index = 0;
		int lane_ID = 0;
		while (getline(myfile2, line2)) {
			vector<string> res;
			split(line2, ':', res);
			cpu_data->lane_pool.lane_ID[lane_index] = atoi(res[0].c_str());
			cpu_data->lane_pool.direction[lane_index] = atoi(res[1].c_str());
			cpu_data->lane_pool.road_ID[lane_index] = atoi(res[9].c_str());
			//std::cout << cpu_data->lane_pool.lane_ID[lane_index] << '-' << cpu_data->lane_pool.road_ID[lane_index] << endl;
			cpu_data->lane_pool.flow[lane_index] = 0;
			cpu_data->lane_pool.density[lane_index] = 0;
			cpu_data->lane_pool.speed[lane_index] = 0;
			cpu_data->lane_pool.queue_length[lane_index] = 0;
			cpu_data->lane_pool.lane_length[lane_index] = atoi(res[6].c_str());
			cpu_data->lane_pool.alpha[lane_index] = 1;
			cpu_data->lane_pool.beta[lane_index] = 1;
			cpu_data->lane_pool.max_density[lane_index] = 178.6;
			cpu_data->lane_pool.max_speed[lane_index] = 60;
			cpu_data->lane_pool.min_speed[lane_index] = 10.8;
			cpu_data->lane_pool.vehicle_counts[lane_index] = 0;
			cpu_data->lane_pool.vehicle_start_index[lane_index] = atoi(res[7].c_str());
			cpu_data->lane_pool.vehicle_end_index[lane_index] = atoi(res[8].c_str());
			int max_veh = cpu_data->lane_pool.vehicle_end_index[lane_index];
			int min_veh= cpu_data->lane_pool.vehicle_start_index[lane_index];
			cpu_data->lane_pool.max_vehicles[lane_index] = max_veh-min_veh;
			cpu_data->lane_pool.output_capacity[lane_index] = 2;
			cpu_data->lane_pool.empty_space[lane_index] = max_veh - min_veh;
			//printf("empty: %d \n", cpu_data->lane_pool.empty_space[lane_index]);
			cpu_data->lane_pool.buffer_counts[lane_index] = 0;
			cpu_data->lane_pool.buffered_vehicle_start_index[lane_index] = atoi(res[7].c_str());
			cpu_data->lane_pool.buffered_vehicle_end_index[lane_index] = atoi(res[8].c_str());
			cpu_data->lane_pool.vehicle_passed[lane_index] = false;
			cpu_data->lane_pool.signal[lane_index] = atoi(res[2].c_str());
			cpu_data->lane_pool.greenstart_time[lane_index] = atoi(res[3].c_str());
			cpu_data->lane_pool.green[lane_index] = atoi(res[4].c_str());
			cpu_data->lane_pool.cycle_offset[lane_index] = atoi(res[5].c_str());
			cpu_data->lane_pool.complete_num[lane_index] = 0;
			cpu_data->lane_pool.begin_num[lane_index] = 0;
			//cpu_data->lane_pool.locked[lane_index] = false;
			lane_index++;
			lane_ID++;
			lane_num++;
		}
		myfile2.close();
	}
	std::cout << "lane data input complete" << endl;
	//���س����ļ�
	std::string line3;
	std::ifstream myfile3(veh_file.c_str());
	CPU_veh = (GPUvehicle*)malloc(memory_space_for_vehicles);
	//memset(CPU_veh, 0, memory_space_for_vehicles);
	int veh_num = 0;
	if (myfile3.is_open()) {
		int veh_index = 0;
		int veh_ID =0;
		while (getline(myfile3, line3)) {
			veh_num += 1;
			vector<string> res;
			split(line3, ':', res);
			CPU_veh[veh_index].vehicle_ID = veh_ID;
			int entry_time = atoi(res[1].c_str());
			CPU_veh[veh_index].entry_time = atoi(res[1].c_str());
			string::size_type idx;
			idx = res[2].find('-');
			if (idx == string::npos) {
				CPU_veh[veh_index].path_road[0] = atoi(res[2].c_str());
				CPU_veh[veh_index].path_directions[0] = atoi(res[3].c_str());
				CPU_veh[veh_index].whole_num = 1;
			}
			else {
				vector<string> road_path = split_str(res[2], "-");
				vector<string> fx_path = split_str(res[3], "-");
				for (int j = 0; j < road_path.size(); j++) {
					CPU_veh[veh_index].path_road[j] = atoi(road_path[j].c_str());
					CPU_veh[veh_index].path_directions[j] = atoi(fx_path[j].c_str());
				}
				CPU_veh[veh_index].whole_num = road_path.size();
			}
			CPU_veh[veh_index].path_num = 0;
			int st = CPU_veh[veh_index].path_road[0];
			CPU_veh[veh_index].current_road_ID = st;
			CPU_veh[veh_index].current_lane_ID = -1;
			CPU_veh[veh_index].distant = 100;
			CPU_veh[veh_index].next_lane = -1;
			CPU_veh[veh_index].next_road = -1;
			int road_index = CPU_veh[veh_index].path_road[0];
			if (cpu_demand->new_vehicle_everystep[entry_time].new_vehicle_size[road_index] < LaneInputCapacity) {
				int insert_index = cpu_demand->new_vehicle_everystep[entry_time].new_vehicle_size[road_index];
				cpu_demand->new_vehicle_everystep[entry_time].new_vehicles[road_index][insert_index] = veh_index;
				cpu_demand->new_vehicle_everystep[entry_time].new_vehicle_size[road_index]++;
			}
			veh_index++;
			veh_ID++;
		}
		myfile3.close();
	}
	std::cout << "vehicle/demand data input complete" << endl;
	std::cout << "total vehicle num:"<<veh_num << endl;
	//���ؽڵ��ļ�
	std::string line4;
	std::ifstream myfile4(node_file.c_str());
	if (myfile4.is_open()) {
		while (getline(myfile4, line4)) {
			vector<string> res;
			split(line4, ':', res);
			//int index = 0;
			int index = atoi(res[0].c_str());
			cpu_data->node_pool.Node_ID[index] = index;
			cpu_data->node_pool.current_buffer[index] = index;
			cpu_data->node_pool.buffer_counts[index] = 0;
			string::size_type idx;
			idx = res[1].find('-');
			if (idx == string::npos) {
				if (res[1] == "null") {
					cpu_data->node_pool.up_lane_num[index] = 0;
				}
				else {
					int up = atoi(res[1].c_str());
					cpu_data->node_pool.up_lane_num[index] = 1;
					cpu_data->node_pool.up_lane_index[index][0] = up;
				}
			}
			else {
				vector<string> up_lane = split_str(res[1], "-");
				cpu_data->node_pool.up_lane_num[index] = up_lane.size();
				for (int j = 0; j < up_lane.size(); j++) {
					cpu_data->node_pool.up_lane_index[index][j] = atoi(up_lane[j].c_str());
				}
			}
		}
		myfile4.close();
	}
	std::cout << "node data input complete" << endl;
	return true;
}

//�˺���������Ѱ��Ŀ�공��
__device__ int Vehicle_getnextlane(GPUmemory* gpu_data, int road_index, int direction) {
	int lane_ID = -1;
	int lane_queue = -1;
	for (int i = gpu_data->road_pool.lane_start_index[road_index]; i < gpu_data->road_pool.lane_end_index[road_index]; i++) {
		int dir1 = gpu_data->lane_pool.direction[i];
		int dir2 = direction;
		if (gpu_data->lane_pool.empty_space[i] > 0) {  //�����Ƿ���ʣ������
			//ѡ��ת�򳵵�
		    if (dir1 == dir2 || (dir2 == 0 && (dir1 == 3 || dir1 == 5 || dir1 == 6)) || (dir2 == 1 && (dir1 == 4 || dir1 == 5 || dir1 == 6)) || (dir2 == 2 && (dir1 == 4 || dir1 == 3 || dir1 == 6))) {
				if (lane_queue < 0 ||((lane_queue >= 0) && (gpu_data->lane_pool.queue_length[i] < lane_queue))) {
					lane_ID = i;
					lane_queue = gpu_data->lane_pool.queue_length[i];
				}
			}
		}
	}
	if (lane_queue == -1 || lane_ID == -1) {
		return -1;
	}
	else {
		return lane_ID; //���Ŀ�공��
	}
}

//�˺�������·��Ϊ���е�Ԫ�����ء�����������
__global__ void load_demand(GPUmemory*gpu_data, Demand* gpu_demand, int time_step, int Roadsize, GPUvehicle * GPU_veh) {
	unsigned road_index = blockIdx.x * blockDim.x + threadIdx.x;
	if (road_index >= Roadsize)
		return;
	int flow = 0;
	//int length = gpu_data->road_pool.length[road_index];
	for (int i = gpu_data->road_pool.lane_start_index[road_index]; i < gpu_data->road_pool.lane_end_index[road_index]; i++) {
		flow+=gpu_data->lane_pool.flow[i];
	}
	//·���ܶȸ���
	float density = flow /((gpu_data->road_pool.lane_count[road_index] * gpu_data->road_pool.length[road_index]) / 1000);
	gpu_data->road_pool.density[road_index] =density;
	//·���ٶȸ���
	float speed = 10.8 + (60 -10.8)*(1 - (density /178.6));
	gpu_data->road_pool.speed[road_index] = speed / 3.6;
	//����������
	for (int i = 0; i < gpu_demand->new_vehicle_everystep[time_step].new_vehicle_size[road_index]; i++) {
		int veh = gpu_demand->new_vehicle_everystep[time_step].new_vehicles[road_index][i];
		int obj_lane = Vehicle_getnextlane(gpu_data,road_index, GPU_veh[veh].path_directions[0]); //�����󳵵�ѡ��
		if ( obj_lane!=-1) {
			//��������״̬��Ϣ����
			GPU_veh[veh].current_lane_ID = obj_lane;
			GPU_veh[veh].start_time = time_step;
			GPU_veh[veh].distant = gpu_data->lane_pool.lane_length[obj_lane];
			gpu_data->lane_pool.flow[obj_lane] += 1;
			gpu_data->lane_pool.empty_space[obj_lane] -= 1;
			//���س���
			int load_point = gpu_data->lane_pool.vehicle_start_index[obj_lane] + gpu_data->lane_pool.vehicle_counts[obj_lane];
			gpu_data->lane_vehicle_space.vehicle_space[load_point] = veh;
			gpu_data->lane_pool.vehicle_counts[obj_lane] += 1;
			gpu_data->lane_pool.begin_num[obj_lane] += 1;
			//printf("%d new---------------------obj:%d,veh:%d,road:%d,where:%d\n", time_step, obj_lane, veh, road_index,p);
		}
		else {
			//���������������ת����·��ͣ����
			//printf("transfer to park--------------------obj:%d,veh:%d,road:%d\n", obj_lane, veh, road_index);
			int n = gpu_data->road_pool.park_num[road_index];
			gpu_data->road_pool.park[road_index][n] = veh;
			gpu_data->road_pool.park_num[road_index]++;
		}
	}
	//·��ͣ�����ŷ�ʱ�����
	if (gpu_data->road_pool.park_output[road_index]>0) {
		gpu_data->road_pool.park_output[road_index]--;
	}
	if (gpu_data->road_pool.park_num[road_index] > 0) {
		if (gpu_data->road_pool.park_output[road_index]==0) {
			int veh = gpu_data->road_pool.park[road_index][0];//ͣ����������
			int obj_lane = Vehicle_getnextlane(gpu_data, road_index, GPU_veh[veh].path_directions[0]);
			//GPU_veh[veh].next_lane = obj_lane;
			if (obj_lane != -1) {
				//ͣ�����ŷų���
				GPU_veh[veh].current_lane_ID = gpu_data->lane_pool.lane_ID[obj_lane];
				GPU_veh[veh].start_time = time_step;
				GPU_veh[veh].distant == gpu_data->lane_pool.lane_length[obj_lane];
				//printf("%d park out ---------------------obj:%d,veh:%d,road:%d\n", time_step, obj_lane, veh, road_index);
				gpu_data->lane_pool.flow[obj_lane] += 1;
				gpu_data->lane_pool.empty_space[obj_lane] -= 1;
				int p = gpu_data->lane_pool.vehicle_start_index[obj_lane] + gpu_data->lane_pool.vehicle_counts[obj_lane];
				gpu_data->lane_vehicle_space.vehicle_space[p] = veh;
				gpu_data->lane_pool.vehicle_counts[obj_lane] += 1;
				for (int j = 0; j < gpu_data->road_pool.park_num[road_index];j++) {
					gpu_data->road_pool.park[road_index][j] = gpu_data->road_pool.park[road_index][j+1];
				}
				gpu_data->road_pool.park[road_index][gpu_data->road_pool.park_num[road_index]] = 0;
				gpu_data->road_pool.park_num[road_index] -= 1;
				gpu_data->road_pool.park_output[road_index] = 2;
				gpu_data->lane_pool.begin_num[obj_lane] += 1;
				gpu_data->road_pool.begin_num[road_index] += 1;
			}
		}
	}
	return;
}

//�˺������Գ���Ϊ���е�Ԫ�������ӻ������·ţ�����������״̬����
__global__ void simulateVehicle_pass(GPUmemory*gpu_data, int time_step, int LaneSize, GPUvehicle * GPU_veh, simuResult* GPUResult) {
	unsigned lane_index = blockIdx.x * blockDim.x + threadIdx.x;
	if (lane_index >= LaneSize)
		return;
	//�����ٶȸ��£�=����·���ٶȣ�
	float speed = gpu_data->road_pool.speed[gpu_data->lane_pool.road_ID[lane_index]];  
	//�����ӳ����������·�����ʵ����
	for (int i = 0; i < gpu_data->node_pool.buffer_counts[lane_index]; i++) {
		//����״̬����
		int veh_id = gpu_data->buffer_vehicle_space.buffer_space[gpu_data->lane_pool.buffered_vehicle_start_index[lane_index] + i];
		//printf("load in real lane,veh:%d,lane:%d,where:%d\n", veh_id, lane_index, gpu_data->lane_pool.buffered_vehicle_start_index[lane_index] + i);
		GPU_veh[veh_id].current_lane_ID = lane_index;
		GPU_veh[veh_id].entry_time = time_step;
		GPU_veh[veh_id].distant = gpu_data->lane_pool.lane_length[lane_index];
		GPU_veh[veh_id].path_num += 1;
		gpu_data->lane_vehicle_space.vehicle_space[gpu_data->lane_pool.vehicle_counts[lane_index] + gpu_data->lane_pool.vehicle_start_index[lane_index]] = veh_id;
		gpu_data->lane_pool.vehicle_counts[lane_index] += 1;
		gpu_data->lane_pool.flow[lane_index] += 1;
		gpu_data->buffer_vehicle_space.buffer_space[gpu_data->lane_pool.buffered_vehicle_start_index[lane_index] + i] = 0;
		//gpu_data->node_pool.buffer_counts[lane_index] -= 1;

	}
    gpu_data->node_pool.buffer_counts[lane_index] = 0;
	//�ſظ���
	//gpu_data->lane_pool.signal[lane_index] = -1;
	if (gpu_data->lane_pool.signal[lane_index] != -1) { //Ϊ�źſ��Ƶĳ���
		int temp = time_step - gpu_data->lane_pool.greenstart_time[lane_index];
		if (temp > gpu_data->lane_pool.cycle_offset[lane_index]) {
			gpu_data->lane_pool.greenstart_time[lane_index] += gpu_data->lane_pool.cycle_offset[lane_index];
		}
		if (temp>=0 && temp <=gpu_data->lane_pool.green[lane_index]) {
			gpu_data->lane_pool.signal[lane_index] = 1;
		}
		else {
			gpu_data->lane_pool.signal[lane_index] = 0;
		}
	}
	//�����������
	for (int i = gpu_data->lane_pool.vehicle_start_index[lane_index]; i < gpu_data->lane_pool.vehicle_start_index[lane_index] + gpu_data->lane_pool.vehicle_counts[lane_index]; i++) {
		if (GPU_veh[gpu_data->lane_vehicle_space.vehicle_space[i]].distant > 0) {
			GPU_veh[gpu_data->lane_vehicle_space.vehicle_space[i]].distant -= speed;
			if (GPU_veh[gpu_data->lane_vehicle_space.vehicle_space[i]].distant <= 0) {
				gpu_data->lane_pool.queue_length[lane_index] += 1;  //���������Ŷ�
				gpu_data->lane_pool.flow[lane_index] -= 1;
			}
		}
	}
	//�����Ƿ�������ŷ�������ͨ���������̵ơ����Ŷӳ���
	if (gpu_data->lane_pool.queue_length[lane_index] > 0 && gpu_data->lane_pool.output_capacity[lane_index] == 0 && (gpu_data->lane_pool.signal[lane_index] == 1 || gpu_data->lane_pool.signal[lane_index] == -1)) {
		gpu_data->lane_pool.vehicle_passed[lane_index] = true;
	}
	else {
		gpu_data->lane_pool.vehicle_passed[lane_index] = false;
	}
	int start = gpu_data->lane_pool.vehicle_start_index[lane_index];
	int first_veh = gpu_data->lane_vehicle_space.vehicle_space[start];

	//ÿ���5minͳ�Ƴ�����Ϣ
	if (time_step % 300 == 0 && time_step > 0) {
		//printf("time:%d lane:%d speed:%d first_veh:%d count:%d signal:%d can_go:%d queue:%d,travel:%d\n", time_step, lane_index, speed, gpu_data->lane_vehicle_space.vehicle_space[gpu_data->lane_pool.vehicle_start_index[lane_index]], gpu_data->lane_pool.vehicle_counts[lane_index], gpu_data->lane_pool.signal[lane_index], gpu_data->lane_pool.vehicle_passed[lane_index], gpu_data->lane_pool.queue_length[lane_index], GPUResult->travel[lane_index]);
		int t = time_step / 300 - 1;
		GPUResult->flow[t][lane_index] = gpu_data->lane_pool.flow[lane_index];
		GPUResult->count[t][lane_index] = gpu_data->lane_pool.vehicle_counts[lane_index];
		GPUResult->speed[t][lane_index] = gpu_data->road_pool.speed[gpu_data->lane_pool.road_ID[lane_index]];
		//GPUResult->signal[t][lane_index] = gpu_data->lane_pool.signal[lane_index];
		//printf("time:%d,lane:%d,count:%d,travel:%d\n",time_step,lane_index, gpu_data->lane_pool.vehicle_counts[lane_index], GPUResult->travel[lane_index]);
		if (GPUResult->comlete_num[lane_index] > 0) {
			GPUResult->avg_travel[t][lane_index] = GPUResult->travel[lane_index] / GPUResult->comlete_num[lane_index];
			GPUResult->complete[t][lane_index] = GPUResult->comlete_num[lane_index];
			GPUResult->travel[lane_index] = 0;
			GPUResult->comlete_num[lane_index] = 0;
			//gpu_data->lane_pool.complete_num[lane_index] = 0;
		}
	}

	gpu_data->lane_pool.empty_space[lane_index] = gpu_data->lane_pool.max_vehicles[lane_index]-gpu_data->lane_pool.vehicle_counts[lane_index];
	printf("time:%d lane:%d first_veh:%d distant:%f count:%d empty:%d road:%d can_go:%d queue:%d,last_veh:%d\n", time_step, lane_index ,gpu_data->lane_vehicle_space.vehicle_space[gpu_data->lane_pool.vehicle_start_index[lane_index]], GPU_veh[first_veh].distant, gpu_data->lane_pool.vehicle_counts[lane_index], gpu_data->lane_pool.empty_space[lane_index], gpu_data->lane_pool.road_ID[lane_index], gpu_data->lane_pool.vehicle_passed[lane_index], gpu_data->lane_pool.queue_length[lane_index], gpu_data->lane_vehicle_space.vehicle_space[gpu_data->lane_pool.vehicle_start_index[lane_index] + gpu_data->lane_pool.vehicle_counts[lane_index] - 1]);
	if (gpu_data->lane_pool.vehicle_passed[lane_index] = true && gpu_data->lane_pool.queue_length[lane_index] > 0 && GPU_veh[first_veh].distant <= 0) {
		if (GPU_veh[first_veh].path_num == GPU_veh[first_veh].whole_num - 1) {   //�ó����г̽���
			gpu_data->lane_pool.complete_num[lane_index] += 1;
			GPUResult->comlete_num[lane_index] += 1;
			GPUResult->total_complete[lane_index] += 1;
			GPU_veh[first_veh].com_time = time_step;
			GPUResult->travel[lane_index]+=time_step- GPU_veh[first_veh].entry_time;
			gpu_data->lane_vehicle_space.vehicle_space[start] = -1;
			for (int j = 0; j < gpu_data->lane_pool.vehicle_counts[lane_index] - 1; j++) {
				gpu_data->lane_vehicle_space.vehicle_space[start + j] = gpu_data->lane_vehicle_space.vehicle_space[start + j + 1];  //���γ���������ǰ��λ
			}
			gpu_data->lane_pool.empty_space[lane_index] += 1;
			gpu_data->lane_pool.vehicle_counts[lane_index] -= 1;
			gpu_data->lane_pool.queue_length[lane_index]-= 1;
		}
		else {  //�ó��������г�
			int current = GPU_veh[first_veh].path_num + 1;
			int obj_lane = Vehicle_getnextlane(gpu_data, GPU_veh[first_veh].path_road[current], GPU_veh[first_veh].path_directions[current]);
			GPU_veh[first_veh].next_lane = obj_lane; //ѡ������Ŀ�공��
			if (obj_lane == -1) {
				gpu_data->lane_pool.vehicle_passed[lane_index] = false;  //���׳��޷��ŷţ���������
			}
		}
	}
	//�����ŷ�ʱ�����
	if (gpu_data->lane_pool.output_capacity[lane_index] > 0) {
		gpu_data->lane_pool.output_capacity[lane_index] -= 1;
	}
	///__syncthreads();
	GPUResult->begin_num[lane_index] = gpu_data->lane_pool.begin_num[lane_index];
	//GPUResult->total_complete[lane_index] = gpu_data->lane_pool.complete_num[lane_index];
	GPUResult->comlete_num[lane_index] = gpu_data->lane_pool.complete_num[lane_index];
	return;
}

//�˺������Գ���������-�ڵ�Ϊ���е�Ԫ�����������γ���ת��������Ŀ�공��������
__global__ void simulateVehicle_prepass(GPUmemory*gpu_data, int time_step, int LaneSize, GPUvehicle * GPU_veh, simuResult* GPUResult) {
	unsigned node_index = blockIdx.x * blockDim.x + threadIdx.x;
	if (node_index >= LaneSize)
		return;
	//�����ڵ����ι�������
	for (int i = 0; i < gpu_data->node_pool.up_lane_num[node_index]; i++) {
		int up_lane = gpu_data->node_pool.up_lane_index[node_index][i]; //���γ�����
		int first_up_veh = gpu_data->lane_vehicle_space.vehicle_space[gpu_data->lane_pool.vehicle_start_index[up_lane]];
		//�����γ���ͷ��Ŀ�공��=�ó���������
		if (GPU_veh[first_up_veh].next_lane == gpu_data->lane_pool.lane_ID[node_index]) {
			//�����γ��������ŷŵ�����
			if ((gpu_data->lane_pool.queue_length[up_lane]>0) && (gpu_data->lane_pool.output_capacity[up_lane]==0) && (gpu_data->lane_pool.vehicle_passed[up_lane] = true) && (gpu_data->lane_pool.empty_space[node_index] > 0)) {
				int buffer_insert = gpu_data->lane_pool.buffered_vehicle_start_index[node_index] + gpu_data->node_pool.buffer_counts[node_index]; //+ gpu_data->lane_pool.buffer_counts[node_index];
				gpu_data->buffer_vehicle_space.buffer_space[buffer_insert] = first_up_veh;    //ת�������λ�����
				GPUResult->travel[up_lane] += time_step - GPU_veh[first_up_veh].entry_time;
				GPUResult->comlete_num[up_lane] += 1;
				int start = gpu_data->lane_pool.vehicle_start_index[up_lane];
				gpu_data->lane_vehicle_space.vehicle_space[start] = -1;
				for (int j = 0; j < gpu_data->lane_pool.vehicle_counts[up_lane] - 1; j++) {
					gpu_data->lane_vehicle_space.vehicle_space[start + j] = gpu_data->lane_vehicle_space.vehicle_space[start + j + 1];  //���γ���������ǰ��λ
				}
				gpu_data->lane_pool.vehicle_counts[up_lane] -= 1;
				gpu_data->lane_pool.queue_length[up_lane] -= 1;      //����������
				gpu_data->lane_pool.empty_space[up_lane] += 1;
				gpu_data->lane_pool.empty_space[node_index] -= 1;    //������������
				gpu_data->lane_pool.output_capacity[up_lane] = 2;  //ͨ��������λ
				gpu_data->node_pool.buffer_counts[node_index] += 1;
			}
		}
	}
	return;
}


__global__ void result_toCPU(GPUmemory* gpu_data, int LaneSize, simuResult* GPUResult) {
	int lane_index = blockIdx.x * blockDim.x + threadIdx.x;
	if (lane_index >= LaneSize)
		return;
}

//CUDA�쳣��׽����
#define CUDA_ERROR_CHECK
#define CudaSafeCall( err ) __cudaSafeCall( err, __FILE__, __LINE__ )
#define CudaCheckError()    __cudaCheckError( __FILE__, __LINE__ )
inline void __cudaSafeCall(cudaError err, const char *file, const int line)
{
#ifdef CUDA_ERROR_CHECK
	if (cudaSuccess != err)
	{
		fprintf(stderr, "cudaSafeCall() failed at %s:%i : %s\n",
			file, line, cudaGetErrorString(err));
		exit(-1);
	}
#endif

	return;
}
inline void __cudaCheckError(const char *file, const int line)
{
#ifdef CUDA_ERROR_CHECK
	cudaError err = cudaGetLastError();
	if (cudaSuccess != err)
	{
		fprintf(stderr, "cudaCheckError() failed at %s:%i : %s\n",
			file, line, cudaGetErrorString(err));
		exit(-1);
	}
	err = cudaDeviceSynchronize();
	if (cudaSuccess != err)
	{
		fprintf(stderr, "cudaCheckError() with sync failed at %s:%i : %s\n",
			file, line, cudaGetErrorString(err));
		exit(-1);
	}
#endif

	return;
}

//���з���������
bool StartSimulation() {
	cudaStream_t gpu_stream;
	cudaStreamCreate(&gpu_stream);
	unsigned thread = 128;
	unsigned road_block = ceil(1.0f *RoadSize / thread);
	unsigned lane_block = ceil(1.0f *LaneSize / thread);
	int time_step = 1;   //������
	int end_time =1000;  //�������ʱ��
	
	cudaEvent_t start,stop;//�¼�����  
	cudaEventCreate(&start);//�����¼�  
	cudaEventCreate(&stop);//�����¼�  
	cudaEventRecord(start,Stream0);//��¼��ʼ  

	for (int now_time = 0; now_time < end_time; now_time++) {
		printf("%d\n", now_time);
		load_demand<<<road_block, thread, 0, gpu_stream >>> (gpu_data, gpu_demand, now_time, RoadSize, GPU_veh);
		simulateVehicle_pass <<<lane_block, thread, 0, gpu_stream >>> (gpu_data, now_time, LaneSize, GPU_veh, GPUResult);
		simulateVehicle_prepass <<<lane_block, thread, 0, gpu_stream >>> (gpu_data, now_time, LaneSize, GPU_veh, GPUResult);
		//cudaMemcpy(CPUResult, GPUResult, sizeof(simuResult), cudaMemcpyDeviceToHost);  //���ݽ��
		//cudaDeviceSynchronize();
		CudaCheckError();
	    //result_toCPU <<<block, thread, 0, gpu_stream >>> (gpu_data, LaneSize, GPUResult);
	}
	cudaMemcpy(CPUResult, GPUResult, sizeof(simuResult), cudaMemcpyDeviceToHost);  //����GPU��������CPU
	
	cudaEventRecord(stop,Stream0);//��¼�����¼�  
	cudaEventSynchronize(stop);//�¼�ͬ�����ȴ������¼�֮ǰ���豸�����������  
	float elapsedTime;  
	cudaEventElapsedTime(&elapsedTime,start,stop);//���������¼�֮��ʱ������λΪms��  
	
	printf("GPU Elapsed time:%.6f ms.\n",elapsedTime);  

	
	std::cout << "END =============================================" << endl;
	int p = 0;
	int q = 0;
	for (int i = 0; i < LaneSize; i++) {
		p += CPUResult->total_complete[i];
		q += CPUResult->begin_num[i];
	}
	std::cout << "complete" << p << endl;  //������г̳�����
	std::cout << "generate" << q << endl;  //�ܼ���������
	
	ofstream out("lane_output.txt"); //��������ͳ�ƽ����Ŀ���ļ�
	for (int j = 0; j < 12; j++)
	{
		for (int i = 0; i < LaneSize; i++) {
			out << "time_step:" << j + 1 << ",lane:" << i << ",count:" << CPUResult->count[j][i] << ",speed:" << CPUResult->speed[j][i] << ",travel:" << CPUResult->avg_travel[j][i] <<",complete:"<< CPUResult->complete[j][i]<<",flow:"<< CPUResult->flow[j][i] << "\n";
		}
	}
	out.close();
	cudaDeviceReset();   //����GPU��Ϣ
	return true;
}
