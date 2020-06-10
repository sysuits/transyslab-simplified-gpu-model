import Meso_Simu
import copy
import datetime

total_stime = datetime.datetime(1900, 1, 1, 17, 0, 0)   #simulation start time
total_etime = datetime.datetime(1900, 1, 1, 17, 25, 0)  #simulation end time

#range of network
roadname = ['40014002', '40024001', '40024003', '40034002', '40014004', '40044001', '40024005', '40054002','40034006', '40064003', '40044005', '40054004', '40064005', '40054006', '40044007', '40074004','40054008', '40084005', '40064009', '40094006', '40074008', '40084007', '40084009', '40094008']

#path of input data
road_path = 'C:\\Users\\lenovo\\Desktop\\仿真程序及说明\\simulation\\input_data\\road_data.csv'
demand_path = 'C:\\Users\\lenovo\\Desktop\\仿真程序及说明\\simulation\\input_data\\trip_data.csv'
#signal scheme data or real time signal state data,select one of them as input signal data
signal_path='C:\\Users\\lenovo\\Desktop\\仿真程序及说明\\simulation\\input_data\\signal_data.csv'
#signal_path = 'C:\\Users\\lenovo\\Desktop\\仿真程序及说明\\simulation\\input_data\\ssa_data.csv'
#path of out put data
out_put_path = "C:\\Users\\lenovo\\Desktop\\仿真程序及说明\\simulation\\"

#Initialize simulator
simulator=Meso_Simu.Meso_Simu(roadname,road_path,demand_path,signal_path,out_put_path,total_stime)

stime=total_stime
etime=total_etime

#Run simulation
result=simulator.simulation(stime,etime)


