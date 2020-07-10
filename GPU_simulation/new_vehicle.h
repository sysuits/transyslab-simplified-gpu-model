#ifndef NEW_VEHICLE_H
#define NEW_VEHICLE_H

#include "sharedonGPU.h"

class NewVehicle {
public:
	int Lane_ID[RoadSize];
	int new_vehicle_size[RoadSize];
	int new_vehicles[RoadSize][LaneInputCapacity];
};

#endif