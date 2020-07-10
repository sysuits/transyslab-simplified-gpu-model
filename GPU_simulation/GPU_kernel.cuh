//#pragma once
#ifndef GPU_KERNEL_CU_H_
#define GPU_KERNEL_CU_H_

#include <cuda.h>
#include <cuda_runtime.h>
#include <cuda_runtime_api.h>
#include "GPUmemory.h"
#include "simuResult.h"
#include <device_launch_parameters.h>
//#include "device_functions.h"
#include "GPUparameter.h"
#include "GPUvehicle.h"

//using namespace std;

__global__ void simulateVehicle_pass(GPUmemory*gpu_data, int time_step, int kLaneSize, GPUParameter* parameter_on_gpu, GPUvehicle * vpool_gpu);
__global__ void simulateVehicle_prepass(GPUmemory*gpu_data, int time_step, int kLaneSize, GPUParameter* parameter_on_gpu, GPUvehicle * vpool_gpu);
__global__ void result_toCPU(GPUmemory* gpu_data,simuResult* GPUResult);
__device__ int Vehicle_getnextlane(GPUmemory* gpu_data,int road_index, int direction);



#endif