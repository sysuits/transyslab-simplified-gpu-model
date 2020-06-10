import Model
import datetime
import Result
import Demand
import signal
import copy

class Meso_Simu:
    def __init__(self,roadname,road_path,demand_path,signal_path,out_put_path,total_stime):
        self.roadname = roadname
        self.road_path =road_path
        self.demand_path = demand_path
        self.signal_path =signal_path
        self.out_put_path=out_put_path
        self.car_len = 5.6  # 5(vehicle length)+0.6(space headway)
        self.total_stime=total_stime

    def simulation(self,stime,etime):
        print(stime, etime)
        test_Network = Model.Model(self.roadname, self.car_len, stime, etime)
        road_data = test_Network.get_roaddata(self.roadname, self.road_path)  # initialize all road
        signal_data = signal.signal(self.signal_path, road_data, stime, etime)  # initialize signal
        demand_data = Demand.Demand(self.demand_path, self.roadname, stime, etime)  # # initialize vehicle(demand)
        # initialize road network
        test_Network.get_init_network(self.roadname, signal_data.signal_plan, road_data, demand_data.Demand, stime,etime)  # 路网完成初始化
        #run simulation
        self.simu_result = test_Network.simulation(stime, etime)
        simu_result = Result.Result().get_vehicle_result(self.simu_result, self.out_put_path, stime,etime)
        return simu_result









