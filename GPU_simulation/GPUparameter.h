#ifndef GPUPARAMETER_h
#define GPUPARAMETER_h

class GPUParameter {

public:

	int GPURoadSize;
	int GPULaneSize;
	int GPUNodeSize;
	int veh_len;
	int TotalVehNum;
	int GPULaneInputCapacityPerTimeStep;
	int TotalTimeSteps;
};
#endif