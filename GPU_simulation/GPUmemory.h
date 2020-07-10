#ifndef GPUMEMORY_H
#define GPUMEMORY_H

//#include "GPUvehicle.h"
#include "lane_vehicle_pool.h"
#include "buffer_vehicle_pool.h"
#include "lane_pool.h"
#include "road_pool.h"
#include "node_pool.h"
#include"MIT_node_pool.h"
//#include "new_vehicle.h"
//#include "sharedonGPU.h"

class GPUmemory {
public:
	LanePool lane_pool;
	RoadPool road_pool;
	NodePool node_pool;
	//MIT_NodePool MIT_node_pool;

	LaneVehicleSpace lane_vehicle_space;
	BufferVehicleSpace buffer_vehicle_space;

	//NewVehicle new_vehicle_everystep[TotalTimeSteps];

	size_t total_size() {
		return sizeof(LanePool) + sizeof(NodePool) + sizeof(RoadPool) + sizeof(LaneVehicleSpace) + sizeof(BufferVehicleSpace);//+sizeof(MIT_NodePool);
	}
};
#endif

