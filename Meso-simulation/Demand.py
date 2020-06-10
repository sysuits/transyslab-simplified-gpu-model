import Vehicle
import datetime
import csv

class Demand:
    def __init__(self,demand_path,roadname,stime,etime):
        self.stime=stime
        self.etime=etime
        #Two types of data can be used as input demand data
        if 'inout' not in demand_path:  #Route data of vehicles
            self.Demand = self.get_demand(demand_path)
        else:  #Vehicles entering and leaving the road data
            self.Demand = self.get_inout_demand(self.road_data, demand_path, roadname, stime, etime)

    # Vehicles entering and leaving the road data
    def get_inout_demand(self,roaddata,demand_path,roadname,stime, etime):
        roadname = str(roadname)
        for i in range(len(roaddata)):
            if '掉' in roaddata[i][3]:
                roaddata[i][3] = '左'
            elif roaddata[i][3] == '掉直':
                roaddata[i][3] = '直左'
        with open(demand_path)as csv_file:
            reader = csv.reader(csv_file)
            inout = [row[:] for row in reader]
            del inout[0]
        pretime = datetime.timedelta(seconds=600)
        stime = datetime.datetime.strptime(stime, r"%Y%m%d %H:%M:%S")
        stime = stime + pretime
        etime = datetime.datetime.strptime(etime, r"%Y%m%d %H:%M:%S")
        etime = etime - pretime
        data = []
        for i in range(len(inout)):
            if inout[i][0] == roadname and stime<=data[i][2]<=etime:
                data.append(inout[i])
        fx_name = []
        Demand = []
        for i in range(len(data)):
            data[i] = list(data[i])
            data[i][2] = datetime.datetime.strptime(data[i][2], "%Y-%m-%d %H:%M:%S")
            data[i][3] = datetime.datetime.strptime(data[i][3], "%Y-%m-%d %H:%M:%S")
            if '左' in data[i][4] or '掉' in data[i][4]:
                data[i][4] = '左'
            elif '右' in data[i][4]:
                data[i][4] = '右'
            elif '直' in data[i][4]:
                data[i][4] = '直'
            bh = data[i][7]
            for j in range(len(roaddata)):
                if roaddata[j][5] == bh:
                    rfx = roaddata[j][3]
            fx_name.append(data[i][4])
            if data[i][5] == data[i][6] == '1' and data[i][2] >= stime+pretime and data[i][3] <= etime-pretime and self.comom_num(rfx, data[i][4])[0] > 0:
                data[i][5] = 1
                if (data[i][3] - data[i][2]).seconds > 280:
                    data[i][5] = 0
            else:
                data[i][5] = 0
            if len(data[i][7]) <= 2:
                data[i][7] = int(data[i][7])
            hphm = data[i][0]
            entrytime = data[i][2]
            road_path = [roadname]
            direction_path = [data[i][4]]
            one_veh = Vehicle.Vehicle(hphm, entrytime, 0, road_path, direction_path)
            one_veh.can_calibrate=data[i][5]
            one_veh.out_time=data[i][3]
            Demand.append(one_veh)
        print("Demand number:", len(Demand))
        return Demand

    # Route data of vehicles
    def get_demand(self,demand_path):
        with open(demand_path)as csv_file:
            reader = csv.reader(csv_file)
            data = [row[:] for row in reader]
            del data[0]
        Demand = []
        for i in range(len(data)):
            if len(data[i][1]) > 8:
                data[i][1] = data[i][1][:19]  #Remove milliseconds
                data[i][1] = data[i][1][11:]
            data[i][1] = datetime.datetime.strptime(data[i][1], r"%H:%M:%S")
            if self.stime<=data[i][1]<self.etime:
                # Organize path data in a list
                if '-' in data[i][2]:
                    data[i][2] = data[i][2].split('-')
                if '-' in data[i][3]:
                    data[i][3] = data[i][3].split('-')
                if isinstance(data[i][2], str) == True:
                    data[i][2] = [data[i][2]]
                    data[i][3] = [data[i][3]]
                hphm = data[i][0]
                entrytime = data[i][1]
                road_path = data[i][2]
                direction_path = data[i][3]
                one_veh = Vehicle.Vehicle(hphm, entrytime, 0, road_path, direction_path)
                Demand.append(one_veh)
        print("Demand number:",len(Demand))
        return Demand

