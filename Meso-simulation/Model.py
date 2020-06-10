import csv
import copy
import datetime
import numpy as np
import Road
import Lane
import Vehicle

#simulation main module

class Model:
    def __init__(self,roadname,car_len,stime,etime):
        self.roadname=roadname
        self.stime=stime
        self.etime=etime
        self.car_len=car_len

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
        #number of same lane group/same lane group/whether a mixed lane
        return samedirect, samelane, Mix

    #lane gets the corresponding green time
    def get_green(self,ssa, lane):
        Mix = self.comom_num(lane, '')[2]  #whether a mixed lane
        p = []
        for i in range(len(ssa)):
            p.append(ssa[i][0])
        if Mix  == 1:  #not a mixed lane
            for i in range(len(ssa)):
                p = self.comom_num(lane, ssa[i][0])
                lala = p[0]
                if lala > 0:
                    green_sp = copy.deepcopy(ssa[i][1])
        elif Mix > 1:  #if a mixed lane,should combine multiple lane green times
            temp = []
            for i in range(len(ssa)):
                p = self.comom_num(lane, ssa[i][0])
                lala = p[0]
                if lala > 0:
                    for k in range(len(ssa[i][1])):
                        temp.append(copy.deepcopy(ssa[i][1][k]))
            temp = np.array(list(set([tuple(t) for t in temp])))
            temp = temp.tolist()
            temp.sort()
            green_sp = temp
        return green_sp

    # Access to road information
    def get_roaddata(self,roadname,road_path):
        with open(road_path)as csv_file:
            reader = csv.reader(csv_file)
            data = [row[:] for row in reader]
            del data[0]
        one = []
        for i in range(len(roadname)):
            for j in range(len(data)):
                if roadname[i] == data[j][2]:
                   one.append(data[j])
        for i in range(len(one)):
            if one[i][3] == '掉左' or one[i][3] == '掉':
                one[i][3] = '左'
            if one[i][3] == '掉直':
                one[i][3] = '直左'
            if one[i][3] == '直行':
                one[i][3] = '直'
            one[i][4]=int(one[i][4])
            if one[i][5]=='':
                one[i][5]=-1
            else:
                one[i][5]=int(one[i][5])
        return one

    def get_one_roaddata(self,roadname,roaddata):
        one = []
        for i in range(len(roaddata)):
            if roadname == roaddata[i][2]:
                one.append(roaddata[i])
        return one

    # Obtain the road network data needed for simulation
    def get_init_network(self,roadname_list,signal_plan, roaddata,demand_data,stime,etime):
        Network= []
        car_len=self.car_len
        self.Demand = demand_data
        for i in range(len(roadname_list)): #for each road of the network
            res = self.get_one_roaddata(roadname_list[i],roaddata)
            widen_S=0  #the number of lanes with Stretching-segment Design
            for j in range(len(res)):
                if res[j][5]!=-1 and res[j][3]=='直':
                    widen_S+=1
                    widen_S_len=res[j][5]
            road_len = int(res[0][4])
            lane_num=2   #The number of lanes in the road,the default is 2
            #Initilize a road
            one_road=Road.Road(roadname_list[i],road_len,lane_num,40,10.8,1,1,car_len,stime,etime,widen_S)  #初始化路段对象
            ssa = []    #The green light interval corresponding to each turn
            ssa_right = ''  #Judge whether there is right turn signal control
            for j in range(len(signal_plan)):
                #print(roadname_list[i],signal_plan[j].roadname)
                if roadname_list[i] == signal_plan[j].roadname:
                    temp = []
                    temp.append(signal_plan[j].CDZ)  # 转向
                    temp.append(signal_plan[j].green)  # 绿灯区间
                    ssa.append(temp)
            for j in range(len(ssa)):
                ssa_right += ssa[j][0]
            o_lane = []
            road_right = ''  #Judge whether there is a right turn lane in the road information
            for j in range(len(res)):
                road_right += res[j][3]
                o_lane.append(res[j][3])
            if '右' in road_right and '右' not in ssa_right:  #Has right turn lane but no right turn signal control
                for j in range(len(o_lane)):
                    if '右' in o_lane[j] and len(o_lane[j]) == 1:
                        o_lane[j] = '右转nosig'   #Supplement the right turn lane without signal control
            elif '右' not in road_right:
                if '右' in ssa_right:
                    o_lane.append('右')   #Supplement the right turn lane
                else:
                    o_lane.append('右转nosig')   #Supplement the right turn lane without signal control
            #print(o_lane)
            lane = ['直' for x in range(len(o_lane))]
            for j in range(len(o_lane)):  #Change to standard turn order( left->straight->right )
                if '左' in o_lane[j]:
                    lane[0] = o_lane[j]
                    o_lane[j]=''
                if '左' in lane and '左' in o_lane[j]:
                    lane[1] = o_lane[j]
                if '右' in o_lane[j]:
                    lane[-1] = o_lane[j]
            Road_widen=[0 for x in range(len(lane))]  #Stretching-segment lane distribution
            #print(lane)
            for j in range(len(lane)): # for each lane of this road
                lane_ID=roadname_list[i]+'-'+str(j)
                direction=lane[j]
                if 'nosig' in lane[j]:
                    signalornot=1   #No signal control lane is always 1
                else:
                    signalornot=0
                ht=2        #Saturation headway,default is 2 second
                wideornot=0
                if 'nosig' in lane[j]:
                    SSA=[[stime, etime]]
                else:
                    SSA =self.get_green(ssa, lane[j])  #Obtain the green traffic time corresponding to each lane
                lane_len = road_len
                widen_len=-1
                for k in range(len(res)):
                    if res[k][5]!=-1:
                        if '左' in res[k][3] and '左' in direction and j==0:
                            widen_len=res[k][5]
                            Road_widen[j]='L'
                        if '右' in res[k][3] and '右' in direction and j==len(lane)-1:
                            widen_len = res[k][5]
                            Road_widen[j] = 'R'
                if widen_S>0:
                    if direction=='直' and len(lane)-1-widen_S<=j:
                        widen_len=widen_S_len
                        Road_widen[j] = 'S'
                # initilize a lane of this road
                one_lane = Lane.Lane(lane_ID, direction, lane_len, signalornot, ht, wideornot, car_len, SSA,widen_len,stime,etime)
                one_road.Lanes.append(one_lane)
            one_road.widen=Road_widen
            for j in range(len(self.Demand)):
                if self.Demand[j].road_path[0]==roadname_list[i] and stime<=self.Demand[j].entrytime<=etime:
                    time_index=(self.Demand[j].entrytime-stime).seconds
                    one_road.demand_time[time_index]+=1
                    one_road.demand[time_index].append(self.Demand[j])
            for j in range(len(one_road.Lanes)):
                if one_road.widen[j]!=0:
                    one_road.capcaity+=int(one_road.Lanes[j].widen_len/car_len)
                else:
                    one_road.capcaity += int(one_road.Lanes[j].lane_length/car_len)
            Network.append(one_road)
        self.Network=Network
        #self.Demand=demand_data
        return 0

    # After the vehicle arrives at the intersection, judge the downstream target lane / or select the lane when the vehicle leaves
    def get_nextlane(self,road,direction):
        next_lanes=[]
        next_queue=[]
        for i in range(len(road.Lanes)):
            #road capacity>0, lane capacity>0, and same direction
            if road.remain>0 and road.Lanes[i].remain>0 and self.comom_num(direction, road.Lanes[i].direction)[0] > 0 and road.widen[i]!='S':
                next_lanes.append(i)
                next_queue.append(road.Lanes[i].queue_num)
        if len(next_lanes)==0: #No eligible Lane
            return -1
        else:
            # Select the lane with the least queuing among the eligible lanes
            return next_lanes[next_queue.index(min(next_queue))]

    # Simulation main program(No stretching-segment setting version)
    def simulation(self,stime,etime):
        delta_num=1  #Simulation interval: 1 second
        delta = datetime.timedelta(seconds=delta_num)
        now = copy.deepcopy(stime)
        car_complete=0
        car_in_park=0
        car_in_lane=0
        while now < etime:
            #print(now)
            now_index = (now - self.stime).seconds
            for i in range(len(self.Network)):
                self.Network[i].update()  #all road status update
            for i in range(len(self.Network)):  #for each road of network
                #Demand to load at the current time step
                if self.Network[i].demand_time[now_index]>0:
                    j=0
                    while j <len(self.Network[i].demand[now_index]):
                        dir=self.Network[i].demand[now_index][j].direction_path[0]
                        obj_lane=self.get_nextlane(self.Network[i],dir)  #Get target lane for loading
                        if obj_lane!=-1:
                            self.Network[i].Lanes[obj_lane].join_veh(self.Network[i].demand[now_index][j],now)
                            self.Network[i].demand[now_index][j].start_a_road(self.Network[i].road_ID,self.Network[i].Lanes[obj_lane].lane_ID, dir, now)
                        else:  #If there is no target lane, turn to the road parking lot
                            self.Network[i].park.append(self.Network[i].demand[now_index][j])
                            self.Network[i].demand[now_index][j].start_a_road(self.Network[i].road_ID, -1,dir, now)
                        del self.Network[i].demand[now_index][j]
                        j-=1
                        j+=1
                # Demand in the parking lot to load
                if len(self.Network[i].park)>0:
                    j = 0
                    while j < len(self.Network[i].park):
                        obj_lane = self.get_nextlane(self.Network[i],self.Network[i].park[j].direction_path[0])
                        if obj_lane != -1 and self.Network[i].park_output==0:
                            self.Network[i].Lanes[obj_lane].join_veh(self.Network[i].park[j],now)
                            self.Network[i].park[j].out_park(self.Network[i].Lanes[obj_lane].lane_ID,now)
                            del self.Network[i].park[j]
                            self.Network[i].park_output =self.Network[i].park_ht
                            j -= 1
                        j += 1
                # for each lanes of the road
                for j in range(len(self.Network[i].Lanes)):
                    self.Network[i].Lanes[j].update(now,delta_num)  #Lane state update
                    speed=self.Network[i].speed
                    #print(now, self.Network[i].road_ID, self.Network[i].Lanes[j].direction,speed,self.Network[i].Lanes[j].run_num, self.Network[i].Lanes[j].queue_num)
                    for k in range(len(self.Network[i].Lanes[j].veh_list)):
                        if self.Network[i].Lanes[j].veh_list[k].location>0:
                            self.Network[i].Lanes[j].veh_list[k].location -= speed  #Update the distance between vehicle and intersection stop line
                            if self.Network[i].Lanes[j].veh_list[k].location <= 0:  #Vehicle arrives at the stop line
                                self.Network[i].Lanes[j].queue_num += 1
                                self.Network[i].Lanes[j].run_num -= 1
                                self.Network[i].Lanes[j].veh_list[k].stats[-1].queue_time=now
                                self.Network[i].Lanes[j].veh_list[k].stats[-1].green_s=copy.copy(self.Network[i].Lanes[j].green_num)
                    if len(self.Network[i].Lanes[j].veh_list)>0 and self.Network[i].Lanes[j].veh_list[0].location <= 0 :
                        if self.Network[i].Lanes[j].output == 0 and self.Network[i].Lanes[j].signalornot == 1:
                            self.Network[i].Lanes[j].veh_list[0].stats[-1].green_e = copy.copy(self.Network[i].Lanes[j].green_num)
                            # If it is the last road of the vehicle's journey
                            if len(self.Network[i].Lanes[j].veh_list[0].road_path) == 1:
                                self.Network[i].Lanes[j].veh_list[0].finish_a_road(now,self.Network[i].road_ID,self.Network[i].Lanes[j].lane_ID)
                                self.Network[i].Lanes[j].pop_veh()
                                car_complete += 1
                            else:
                                first_obj_road = self.Network[i].Lanes[j].veh_list[0].road_path[1]
                                for k in range(len(self.Network)):
                                    if self.Network[k].road_ID == first_obj_road:
                                        obj_road = k
                                obj_lane = self.get_nextlane(self.Network[obj_road],self.Network[i].Lanes[j].veh_list[0].direction_path[1])
                                if obj_lane != -1:
                                    self.Network[i].Lanes[j].veh_list[0].finish_a_road(now,self.Network[i].road_ID,self.Network[i].Lanes[j].lane_ID)
                                    self.Network[i].Lanes[j].veh_list[0].start_a_road(self.Network[obj_road].road_ID,self.Network[obj_road].Lanes[obj_lane].lane_ID,self.Network[i].Lanes[j].veh_list[0].direction_path[1], now)
                                    # Vehicle transfer to next road
                                    self.Network[obj_road].Lanes[obj_lane].join_veh(self.Network[i].Lanes[j].veh_list[0],now)
                                    self.Network[i].Lanes[j].pop_veh()
                    self.Network[i].Lanes[j].time_queue[now_index]=self.Network[i].Lanes[j].queue_num
            now += delta
        for i in range(len(self.Network)):
            car_in_park += len(self.Network[i].park)
            for j in range(len(self.Network[i].Lanes)):
                car_in_lane+=len(self.Network[i].Lanes[j].veh_list)
        print('car_complete:',car_complete,'car_in_park:',car_in_park,'car_in_lane:',car_in_lane)
        return self.Network,self.Demand

    # Simulation main program(Stretching-segment setting version)
    # The simulation mechanism of this version is similar to the no stretching-segment version.
    # The major difference in the queuing part of the road module. For details, see road.py
    def widen_simulation(self,stime,etime):
        delta_num=1
        delta = datetime.timedelta(seconds=delta_num)
        now = copy.deepcopy(stime)
        car_complete = 0
        while now < etime:
            now_index = (now - self.stime).seconds
            for i in range(len(self.Network)):
                self.Network[i].update()
            for i in range(len(self.Network)):
                if self.Network[i].demand_time[now_index]>0:
                    j=0
                    while j <len(self.Network[i].demand[now_index]):
                        dir=self.Network[i].demand[now_index][j].direction_path[0]
                        obj_lane=self.get_nextlane(self.Network[i],dir)
                        if obj_lane!=-1:
                            self.Network[i].Lanes[obj_lane].join_veh(self.Network[i].demand[now_index][j],now)
                            self.Network[i].demand[now_index][j].start_a_road(self.Network[i].road_ID,self.Network[i].Lanes[obj_lane].lane_ID, dir, now)
                        else:
                            self.Network[i].park.append(self.Network[i].demand[now_index][j])
                            self.Network[i].demand[now_index][j].start_a_road(self.Network[i].road_ID, -1,dir, now)
                        del self.Network[i].demand[now_index][j]
                        j-=1
                        j+=1
                if len(self.Network[i].park)>0:
                    j = 0
                    while j < len(self.Network[i].park):
                        obj_lane = self.get_nextlane(self.Network[i], self.Network[i].park[j].direction_path[0])
                        if obj_lane != -1 and self.Network[i].park_output==0:
                            self.Network[i].Lanes[obj_lane].join_veh(self.Network[i].park[j],now)
                            self.Network[i].park[j].out_park(self.Network[i].Lanes[obj_lane].lane_ID,now)
                            del self.Network[i].park[j]
                            self.Network[i].park_output =self.Network[i].park_ht
                            j -= 1
                        j += 1
                for j in range(len(self.Network[i].Lanes)):
                    self.Network[i].Lanes[j].update(now,delta_num)
                    speed=self.Network[i].speed
                    for k in range(len(self.Network[i].Lanes[j].veh_list)):
                        if self.Network[i].Lanes[j].veh_list[k].location>0:
                            self.Network[i].Lanes[j].veh_list[k].location -= speed
                            if self.Network[i].Lanes[j].veh_list[k].location <= 0:
                                self.Network[i].Lanes[j].prequeue_num += 1
                                self.Network[i].Lanes[j].veh_list[k].stats[-1].queue_time = now
                                self.Network[i].Lanes[j].veh_list[k].stats[-1].green_s = copy.copy(self.Network[i].Lanes[j].green_num)
                self.Network[i].join_queue()
                for j in range(len(self.Network[i].Lanes)):
                    if len(self.Network[i].Lanes[j].queue_list)>0 :
                        if self.Network[i].Lanes[j].output == 0 and self.Network[i].Lanes[j].signalornot == 1:
                            self.Network[i].Lanes[j].queue_list[0].stats[-1].green_e=copy.copy(self.Network[i].Lanes[j].green_num)
                            if len(self.Network[i].Lanes[j].queue_list[0].road_path) == 1:  # 若为该车行程中的最后一段路
                                self.Network[i].Lanes[j].queue_list[0].finish_a_road(now,self.Network[i].road_ID,self.Network[i].Lanes[j].lane_ID)
                                self.Network[i].Lanes[j].pop_veh_w()
                                car_complete += 1
                            else:
                                first_obj_road = self.Network[i].Lanes[j].queue_list[0].road_path[1]
                                for k in range(len(self.Network)):
                                    if self.Network[k].road_ID == first_obj_road:
                                        obj_road = k
                                obj_lane = self.get_nextlane(self.Network[obj_road],self.Network[i].Lanes[j].queue_list[0].direction_path[1])
                                if obj_lane != -1:
                                    self.Network[i].Lanes[j].queue_list[0].finish_a_road(now,self.Network[i].road_ID,self.Network[i].Lanes[j].lane_ID)
                                    self.Network[i].Lanes[j].queue_list[0].start_a_road(self.Network[obj_road].road_ID,self.Network[obj_road].Lanes[obj_lane].lane_ID,self.Network[i].Lanes[j].queue_list[0].direction_path[1], now)
                                    self.Network[obj_road].Lanes[obj_lane].join_veh(self.Network[i].Lanes[j].queue_list[0], now)  # 车辆转移至下一路段
                                    self.Network[i].Lanes[j].pop_veh_w()
                    self.Network[i].Lanes[j].time_queue[now_index] = len(self.Network[i].Lanes[j].queue_list)
                self.Network[i].pop_queue()
            now += delta
        car_in_park = 0
        car_in_lane = 0
        car_in_queue=0
        for i in range(len(self.Network)):
            car_in_park+=len(self.Network[i].park)
            for j in range(len(self.Network[i].Lanes)):
                car_in_lane += len(self.Network[i].Lanes[j].veh_list)
                car_in_queue += len(self.Network[i].Lanes[j].queue_list)
        print('car_complete:',car_complete,'car_in_park:',car_in_park,'car_in_lane:',car_in_lane,'car_in_queue:',car_in_queue)
        return self.Network,self.Demand