import Vehicle
import copy

class Road:

    def __init__(self,road_ID,road_len,lane_num,maxspeed,minspeed,alpha,beta,car_len,stime,etime,widen_S):
        self.road_ID=road_ID
        self.road_len=road_len  #road length(m)
        self.lane_num=lane_num  #number of lanes
        self.Lanes=[]   #lanes list of the road
        self.flow=0
        self.density=0
        self.maxspeed=maxspeed      #freespeed of the road
        self.speed = maxspeed/3.6   #current speed
        self.jam_density=1000/car_len  #jam density
        self.minspeed=minspeed         #jam speed
        self.alpha=alpha
        self.beta=beta       #alpha、beta in the formula of speed-density,default is 1
        self.park=[]         #parking lot of the road,unlimited capacity
        self.park_output=2   #Parking lot emission time count
        self.park_ht = 2     #Vehicle saturation time interval
        self.demand_time=[0 for x in range(0,(etime-stime).seconds+1)] #demand time step
        self.demand = [[] for x in range(0,(etime-stime).seconds+1)]   #demand
        self.capcaity=0     #total capacity of the road
        self.remain=0       #remain capcaity
        self.car_len=car_len
        self.widen=[0 for x in range(0,lane_num)]  #Lane stretching-segment design type, 0 if none
        self.widen_S=widen_S   #the number of straight lanes with stretching-segment design

    # Road status update: speed, remaining capacity, parking lot discharge time count
    def update(self):
        lane_num=self.lane_num
        self.flow = 0
        veh_num=0
        for i in range(len(self.Lanes)):
            self.flow+= self.Lanes[i].run_num
            veh_num+=self.Lanes[i].run_num+self.Lanes[i].queue_num
        self.density=(self.flow/lane_num)/self.road_len
        self.speed=self.minspeed+(self.maxspeed-self.minspeed)*((1-(self.density/self.jam_density)**self.alpha)**self.beta)
        self.speed/=3.6
        #print(self.speed)
        self.remain=self.capcaity-veh_num
        if self.park_output>0:
            self.park_output-=1
        else:
            self.park_output=0

    # Vehicle transfer from driving set to queuing set (only for stretching-segment version)
    def prequeue_trans(self,out_lane,in_lane):
        for k in range(0,self.Lanes[out_lane].prequeue_num):
            self.Lanes[in_lane].queue_list.append(self.Lanes[out_lane].veh_list[k])
        del self.Lanes[out_lane].veh_list[:self.Lanes[out_lane].prequeue_num]
        self.Lanes[out_lane].prequeue_num = 0

    # It is used to judge whether two lane directions are the same
    def comom_num(self,a, b):
        samedirect = 0
        samelane = ''
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
        return samedirect  # number of same lane groups

    # Vehicles join queue set(only for stretching-segment version)
    def join_queue(self):
        for j in range(len(self.Lanes)):
            self.Lanes[j].queue_num = len(self.Lanes[j].queue_list)
            if self.Lanes[j].prequeue_num>0 and 0<j<len(self.Lanes)-1 and self.widen[j]==0: #No stretching-segment lane
                widen_index=-1
                if self.widen[j-1]==self.widen[j+1]==0:
                    self.prequeue_trans(j,j)
                if self.widen[j-1]!=0:
                    widen_index=j-1     #stretching-segment lane index
                    near=j             #no stretching-segment lane index
                if self.widen[j+1]!=0:
                    widen_index=j+1
                    near = j
                    if self.widen[j+1]=='S':
                        widen_index =len(self.Lanes)-1
                        near = -1
                if widen_index!=-1:
                    if self.Lanes[widen_index].queue_num*self.car_len>self.Lanes[widen_index].widen_len:  #stretching-segment lane saturated
                        self.prequeue_trans(j,widen_index)
                    else:  #stretching-segment lane not saturated
                        self.Lanes[j].near_queue =0
                        if '直' in self.Lanes[j].direction and self.widen[j + 1] == 'S':
                            S_list = [j]
                            S_queue = [self.Lanes[j].queue_num]
                            if self.Lanes[j].queue_num * self.car_len < self.Lanes[j + 1 + self.widen_S].widen_len:
                                for k in range(len(self.widen)):
                                    if self.widen[k] == 'S' and self.Lanes[k].remain > 0:
                                        S_list.append(k)
                                        S_queue.append(self.Lanes[k].queue_num)
                                obj_lane = S_list[S_queue.index(min(S_queue))]
                                if self.Lanes[j + 1].remain <= 0:
                                    obj_lane = copy.copy(j)
                            else:
                                obj_lane = copy.copy(j)
                            self.prequeue_trans(j, obj_lane)
                        else:
                            self.prequeue_trans(j, j)
            if self.Lanes[j].prequeue_num > 0 and (j==len(self.Lanes)-1 or j==0) and self.widen[j]!='S':  #stretching-segment lane
                if self.widen[j]==0:
                    self.prequeue_trans(j, j)
                else:
                    if j==0 :
                        near=1
                    if j==len(self.Lanes)-1:
                        near=j-1
                    if self.Lanes[near].queue_num*self.car_len>self.Lanes[j].widen_len:  #no stretching-segment lane saturated
                        self.prequeue_trans(j, near)
                    else:
                        self.prequeue_trans(j, j)
            self.Lanes[j].prequeue_num=0
            self.Lanes[j].queue_num=len(self.Lanes[j].queue_list)

    #Vehicle exit queue set(only for stretching-segment version)
    def pop_queue(self):
        for j in range(len(self.Lanes)):
            self.Lanes[j].queue_num = len(self.Lanes[j].queue_list)
            if self.Lanes[j].queue_num>0 and self.widen[j]!=0 and self.widen[j]!='S':  #Stretching-segment lane dissipation
                k=0
                while k <len( self.Lanes[j].queue_list):
                    if (k+1)*self.car_len<self.Lanes[j].widen_len and self.Lanes[j].queue_list[k].change_lane==0:
                        if self.comom_num(self.Lanes[j].direction,self.Lanes[j].queue_list[k].direction_path[0])==0:
                            if j == 0 and self.Lanes[j].widen_len -len(self.Lanes[j + 1].queue_list)*self.car_len>0:
                                self.Lanes[j].queue_list[k].change_lane+=1
                                self.Lanes[j + 1].queue_list.append(self.Lanes[j].queue_list[k])
                                del self.Lanes[j].queue_list[k]
                                k -= 1
                            if j == len(self.Lanes) - 1 and self.Lanes[j].widen_len -len(self.Lanes[j-1].queue_list)*self.car_len>0:  #Stretching-segmentright turn
                                self.Lanes[j].queue_list[k].change_lane += 1
                                if self.widen[j - 1]=='S':  #Include stretching-segment straight
                                    obj_lane=j-1-self.widen_S
                                    self.Lanes[obj_lane].queue_list.append(self.Lanes[j].queue_list[k])
                                    del self.Lanes[j].queue_list[k]
                                    k -= 1
                                else:
                                    self.Lanes[j - 1].queue_list.append(self.Lanes[j].queue_list[k])
                                    del self.Lanes[j].queue_list[k]
                                    k -= 1
                        else:
                            self.Lanes[j].queue_list[k].change_lane += 1
                            if j==0 and self.Lanes[j + 1].queue_num<self.Lanes[j].queue_num and self.Lanes[j].widen_len -len(self.Lanes[j + 1].queue_list)*self.car_len>0 and self.comom_num(self.Lanes[j+1].direction,self.Lanes[j].queue_list[k].direction_path[0])>0:
                                self.Lanes[j + 1].queue_list.append(self.Lanes[j].queue_list[k])
                                del self.Lanes[j].queue_list[k]
                                k -= 1
                            if j==len(self.Lanes) - 1 and self.Lanes[j - 1].queue_num<self.Lanes[j].queue_num and self.Lanes[j].widen_len -len(self.Lanes[j - 1].queue_list)*self.car_len>0 and self.comom_num(self.Lanes[j-1].direction,self.Lanes[j].queue_list[k].direction_path[0])>0:
                                self.Lanes[j - 1].queue_list.append(self.Lanes[j].queue_list[k])
                                del self.Lanes[j].queue_list[k]
                                k -= 1
                    k+=1
            widen_index = -1
            if j>0 and self.widen[j - 1] != 0:
                widen_index = j - 1
            if j+1<len(self.Lanes) and self.widen[j + 1] != 0 :
                widen_index = j + 1
                if self.widen[j + 1] == 'S':
                    widen_index = len(self.Lanes) - 1
            if widen_index != -1 and self.Lanes[j].widen==0: #No stretching-segment lane dissipation
                k = 0
                while k < len(self.Lanes[j].queue_list):
                    if (k+1) * self.car_len < self.Lanes[widen_index].widen_len and self.Lanes[j].queue_list[k].change_lane==0:
                        if self.comom_num(self.Lanes[j].direction,self.Lanes[j].queue_list[k].direction_path[0]) == 0:
                            self.Lanes[j].queue_list[k].change_lane += 1
                            self.Lanes[widen_index].queue_list.append(self.Lanes[j].queue_list[k])
                            del self.Lanes[j].queue_list[k]
                            k -= 1
                        else:
                            if self.Lanes[widen_index].queue_num<self.Lanes[j].queue_num:
                                self.Lanes[j].queue_list[k].change_lane += 1
                                self.Lanes[widen_index].queue_list.append(self.Lanes[j].queue_list[k])
                                del self.Lanes[j].queue_list[k]
                                k -= 1
                    k+=1
            self.Lanes[j].queue_num = len(self.Lanes[j].queue_list)



