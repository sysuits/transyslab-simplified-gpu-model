#ifndef SHAREDONGPU_H
#define SHAREDONGPU_H

const int RoadSize = 24;    //路段数量
const int LaneSize = 66;    //车道数量
//const int NodeSize = 9;      
const float veh_len = 5.6;   //车身长度
const int TotalVehNum = 1000;   //总车辆数
const int NetworkMaxNum = 5000; //路网容纳总车辆数
const int LaneInputCapacity = 15;  //仿真间隔车道输入上限
const int TotalTimeSteps =3601;  //仿真总时长
const int Maxpath = 30;     //路径包含路段数上限
const int Maxuplane =20;   //上游车道数上限
const int park_cap = 40;    //停车场容量上限
const int static_num = 12;  //统计间隔 3600/300=12

#endif
