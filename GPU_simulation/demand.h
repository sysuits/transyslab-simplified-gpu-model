#ifndef DEMAND_H
#define DEMAND_H
#include "new_vehicle.h"

class Demand {
public:
	NewVehicle new_vehicle_everystep[TotalTimeSteps];
};
#endif