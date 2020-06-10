import copy

class Vehicle:

    def __init__(self,hphm,entrytime,location,road_path,direction_path):
        self.hphm=hphm    #License plate number
        self.entrytime=entrytime  #Entry road time
        self.location=location    #Distance from intersection stop line
        self.road_path=road_path  #trip route(road)
        self.direction_path=direction_path #trip route(direction)
        self.stats=[]          #Vehicle statistics
        self.change_lane=0     #Vehicles can only change lanes once in the stretching-segment version
        self.can_calibrate=0   #Is the sample available for calibration
        self.out_time=0        #Leave road time
        self.finish_num=0      #Number of completed road in trip route
        self.total_road_path = copy.deepcopy(road_path)  #total road in trip route
        self.total_direction_path = copy.deepcopy(direction_path) #total direction in trip route

    # Vehicle loaded on a new road
    def start_a_road(self,road_ID,lane_ID,direction,now):
        stats=Statistics()  #Initialize statistical unit
        stats.hphm=self.hphm
        stats.road=road_ID
        stats.lane=lane_ID
        stats.direction=direction
        stats.in_time=now
        stats.can_calibrate = self.can_calibrate
        stats.real_out_time=self.out_time
        self.stats.append(stats)

    # Vehicles leaving the parking lot
    def out_park(self,lane_ID,now):
        self.stats[-1].lane=lane_ID
        self.stats[-1].out_park_time=now

    # Vehicle finish travel on a road
    def finish_a_road(self,now,road,lane):
        self.stats[-1].direction=self.direction_path[0]
        self.stats[-1].out_time=now
        self.stats[-1].road = road
        self.stats[-1].lane=lane
        self.stats[-1].queue_num =self.stats[-1].green_e-self.stats[-1].green_s
        self.finish_num+=1
        if self.stats[-1].queue_num<=0:
            self.stats[-1].queue_time=-1

#Statistical unit
class Statistics:
    hphm=0
    road=-1        #current road
    lane=-1        #current lane
    direction=-1
    in_time=-1
    out_park_time=-1
    out_time=-1
    queue_time=-1  #join queue time
    green_s=0      #green time index when vehicle join queue
    green_e=0      #green time index when vehicle leave road
    queue_num=0    #Number of queues experienced
    can_calibrate = 0
    real_out_time=0




