import datetime
import csv
import copy
import numpy as np

class Result:
    # It is used to judge whether two lane directions are the same
    def comom_num(self,a, b):
        samedirect = 0
        samelane = ''
        Mix = 0
        for i in range(len(a)):
            for j in range(len(b)):
                if a[i] == b[j]:
                    samelane += a[i]
        for i in range(len(samelane)):
            if samelane[i] == '右':
                samedirect += 1
            elif samelane[i] == '左':
                samedirect += 1
            elif samelane[i] == '直':
                samedirect += 1
        for i in range(len(a)):
            if a[i] == '右':
                Mix += 1
            elif a[i] == '左':
                Mix += 1
            elif a[i] == '直':
                Mix += 1
        return samedirect, samelane, Mix

    # Statistics unit: statistics by vehicle individual
    def get_vehicle_result(self,simu_Result,out_put_path,stime,etime):
        #result = simu_Result[0]
        road_info = simu_Result[0]
        road_ID=[]
        road_freetravel=[]
        for i in range(len(road_info)):
            road_ID.append(road_info[i].road_ID)
            road_freetravel.append(int(road_info[i].road_len/(road_info[i].maxspeed/3.6)))
        Demand=simu_Result[1]
        out_put = []
        title = ["HPHM", "HPZL","RIQI","Ftime","Ttime","Froadid", "Troadid", "Path", "Travelfx","Traveltime","Traveldelay"]
        out_put.append(title)
        RIQI=stime.strftime('%Y-%m-%d')
        total_travel=0
        total_delay=0
        for i in range(len(Demand)):
            if len(Demand[i].stats)>0:
                temp = []
                temp.append(Demand[i].hphm)
                temp.append(0)
                temp.append(RIQI)
                temp.append(Demand[i].stats[0].in_time)
                temp.append(Demand[i].stats[-1].out_time)
                temp.append(Demand[i].stats[0].road)
                temp.append(Demand[i].stats[-1].road)
                path=[]
                fx=[]
                travel_time=[]
                travel_delay=[]
                for j in range(0,Demand[i].finish_num):
                    path.append(Demand[i].stats[j].road)
                    fx.append(Demand[i].stats[j].direction)
                    real_travel=(Demand[i].stats[j].out_time-Demand[i].stats[j].in_time).seconds
                    total_travel+=real_travel
                    for k in range(len(road_ID)):
                        if road_ID[k]==Demand[i].stats[j].road:
                            delay=real_travel-road_freetravel[k]
                            total_delay+=delay
                            travel_delay.append(str(delay))
                    travel_time.append(str(real_travel))
                if len(travel_time)==1:
                    travel_time=travel_time[0]
                    travel_delay=travel_delay[0]
                    fx=fx[0]
                    path=path[0]
                else:
                    travel_time='_'.join(travel_time)
                    travel_delay = '_'.join(travel_delay)
                    fx= '_'.join(fx)
                    path='_'.join(path)
                temp.append(path)
                temp.append(fx)
                temp.append(travel_time)
                temp.append(travel_delay)
                out_put.append(temp)
        stime=str(stime)[12:14]
        etime=str(etime)
        with open(out_put_path+"veh_out_put.csv", "w", newline='') as csvfile:  #输出为csv文件
            writer = csv.writer(csvfile)
            writer.writerows(out_put)
        return total_travel,total_delay





