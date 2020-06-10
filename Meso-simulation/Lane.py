
class Lane:

    def __init__(self,lane_ID,direction,lane_length,signalornot,ht,wide_len,car_len,ssa,widen_len,stime,etime):
        self.lane_ID=lane_ID
        self.direction=direction
        self.lane_length=lane_length
        self.signalornot=signalornot
        self.ht=ht     #Saturation headway
        if widen_len == -1:
            self.widen=-1      #Whether a stretching-segment lane
            self.widen_len=0   #stretching-segment length
        else:
            self.widen=1
            self.widen_len=widen_len
        self.veh_list=[]    #vehicle objects running on the lane
        self.queue_list=[]  #vehicle objects queuing on the lane(only for stretching-segment version)
        self.run_num=0
        self.queue_num=0
        self.prequeue_num=0 #Number of vehicles ready to join the queue(only for stretching-segment version)）
        self.green_num=0    #Number of green lights passed, used for queuing statistics
        self.capcaity=int(lane_length/car_len)
        self.remain=lane_length/car_len
        self.signal=ssa   #Green time of signal scheme
        self.output=ht    #time count
        self.car_len=car_len
        self.time_queue = [0 for x in range(0, (etime - stime).seconds + 1)]

     # Add new vehicles to the lane
    def join_veh(self,veh,now):
        veh.entrytime=now
        veh.location=self.lane_length
        self.veh_list.append(veh)
        self.run_num+=1

    # Lane emission vehicle
    def pop_veh(self):
        del  self.veh_list[0].road_path[0]
        del  self.veh_list[0].direction_path[0]
        del  self.veh_list[0]
        self.output = self.ht
        self.queue_num -=1

    # Lane emission vehicle(only for stretching-segment version)
    def pop_veh_w(self):
        del  self.queue_list[0].road_path[0]
        del  self.queue_list[0].direction_path[0]
        del  self.queue_list[0]
        self.output = self.ht   #重置排放计数

    # Lane status update: signal control, remain capacity, emission time count
    def update(self,now,delta):
        temp=-1
        for i in range(len(self.signal)):
            if self.signal[i][0]<= now<=self.signal[i][1]:
                self.signalornot = 1
                temp=i
                self.green_num=i
        if temp==-1:
            self.signalornot = 0
        if self.output>0:
            self.output-=delta
        else:
            self.output=0 #self.ht
        #self.queue_num=len(self.queue_list)
        self.run_num=len(self.veh_list)-self.queue_num
        self.remain=self.capcaity-self.queue_num-self.run_num






