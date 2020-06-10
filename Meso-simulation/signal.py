
import csv
import datetime
import copy

class signal:
    def __init__(self,signal_path, road_data,stime, etime):
        if 'ssa' not in signal_path: #Adopt data of signal control scheme
            self.signal_plan =self.get_sigalplan(signal_path, stime, etime)
        else:  #Adopt real time signal state data
            self.signal_plan = self.get_ssadata(road_data,signal_path,stime, etime)

    def get_sigalplan(self, signal_path, stime, etime):
        with open(signal_path)as csv_file:
            reader = csv.reader(csv_file)
            data = [row[:] for row in reader]
            del data[0]
        one = data
        for i in range(len(one)):
            if '' in one[i][0]:
                one[i][0]=int(one[i][0])
                one[i][0]=str(one[i][0])
        LKBH = []
        for i in range(len(one)):
            if one[i][0] not in LKBH:
                LKBH.append(one[i][0])  #Intersection ID
            one[i][1] = int(one[i][1])  #signal phase number
            one[i][5] = int(one[i][5]) + 3  # green+yellow
            one[i][6] = int(one[i][6])  # offset
            one[i][7] = int(one[i][7])  # cycle
            one[i].append([])
        XWH = [[] for x in range(len(LKBH))]
        GREEN = [[] for x in range(len(LKBH))]
        for i in range(len(one)):
            for j in range(len(LKBH)):
                if one[i][0] == LKBH[j] and one[i][1] not in XWH[j]:
                    XWH[j].append(one[i][1])
                    GREEN[j].append(one[i][5])
        all_ssa=[]
        for i in range(len(one)):   #Expand the signal control data to the green light period
            st = stime + datetime.timedelta(seconds=one[i][6])
            for j in range(len(XWH)):
                if one[i][0] == LKBH[j]:
                    for k in range(len(XWH[j])):
                        if one[i][1] > XWH[j][k]:
                            st += datetime.timedelta(seconds=GREEN[j][k])
            et = st + datetime.timedelta(seconds=one[i][5])
            one[i][8].append(copy.deepcopy([st, et]))
            while et < etime:  #Completion of green light period
                st += datetime.timedelta(seconds=one[i][7])
                et = st + datetime.timedelta(seconds=one[i][5])
                one[i][8].append(copy.deepcopy([st, et]))
            while one[i][8][0][0] > stime + datetime.timedelta(seconds=(one[i][7] - one[i][5])):
                et = one[i][8][0][0] - datetime.timedelta(seconds=(one[i][7] - one[i][5]))
                st = et - datetime.timedelta(seconds=one[i][5])
                one[i][8].insert(0, copy.deepcopy([st, et]))
            #Initialize signal control object
            one_ssa=signalwork()
            one_ssa.JCKBH=one[i][0]
            one_ssa.XWH=one[i][1]
            one_ssa.JKD=one[i][2]
            one_ssa.roadname=one[i][3]
            one_ssa.CDZ = one[i][4]
            one_ssa.XW_green = one[i][5]
            one_ssa.offset = one[i][6]
            one_ssa.cycle = one[i][7]
            one_ssa.green= one[i][8]
            #print(one_ssa.roadname,one_ssa.CDZ,one_ssa.green)
            all_ssa.append(one_ssa)
        return all_ssa

    def get_ssadata(self,roaddata,signal_path,stime, etime):
        with open(signal_path)as csv_file:
            reader = csv.reader(csv_file)
            data = [row[:] for row in reader]
            del data[0]
        all_road=[]
        all_ssa=[]
        for k in range(len(roaddata)):
            roadname= roaddata[k][2]
            if roadname in all_road:
                continue
            all_road.append(roadname)
            jckbh = roaddata[k][0]
            jkd = roaddata[k][1]
            ssa_data = []
            for i in range(len(data)):
                if data[i][0] == jckbh and data[i][3] == jkd and stime<=datetime.datetime.strptime(data[i][5], "%Y-%m-%d %H:%M:%S")<etime:
                    obj=-1
                    for j in range(len(ssa_data)):
                        if data[i][2]==ssa_data[j].XWH and data[i][1]==ssa_data[j].FAH and data[i][4]==ssa_data[j].CDZ:
                            obj=j
                    if obj==-1:
                        one_ssa = signalwork()
                        one_ssa.JCKBH = data[i][0]
                        one_ssa.FAH = data[i][1]
                        one_ssa.XWH = data[i][2]
                        one_ssa.JKD = data[i][3]
                        one_ssa.CDZ = data[i][4]
                        one_ssa.roadname = roadname
                        if isinstance(data[i][5],str)==True:
                            data[i][5] = datetime.datetime.strptime(data[i][5], "%Y-%m-%d %H:%M:%S")
                            data[i][6] = datetime.datetime.strptime(data[i][6], "%Y-%m-%d %H:%M:%S")
                        one_ssa.green = [[data[i][5], data[i][6]]]
                        ssa_data.append(one_ssa)
                    else:
                        if isinstance(data[i][5],str)==True:
                            data[i][5] = datetime.datetime.strptime(data[i][5], "%Y-%m-%d %H:%M:%S")
                            data[i][6] = datetime.datetime.strptime(data[i][6], "%Y-%m-%d %H:%M:%S")
                        ssa_data[obj].green.append([data[i][5],data[i][6]])
            for i in range(len(ssa_data)):
                xw = ssa_data[i].green[0][-1] - ssa_data[i].green[0][0]
                xwc =ssa_data[i].green[1][0] - ssa_data[i].green[0][-1]
                if xw.seconds == 0 or xwc.seconds == 0:
                    xw = ssa_data[i].green[-1][-1] - ssa_data[i].green[-1][0]
                    xwc = ssa_data[i].green[-1][0] - ssa_data[i].green[-2][-1]
                while etime - ssa_data[i].green[-1][-1] > xwc:
                    a = ssa_data[i].green[-1][-1] + xwc
                    b = a + xw
                    temp = [a, b]
                    ssa_data[i].green.append(temp)
                all_ssa.append(ssa_data[i])
        return all_ssa


# signal control object
class signalwork:
    JCKBH=0  #Intersection ID
    FAH=0    #signal scheme number
    XWH=0    #signal phase number
    JKD=0    #direction of the approach,such as east、north
    CDZ=0    #lane group,such as light、straight、right
    roadname=0
    stime=0  #Start time of this green light interval
    etime=0
    XW_green = 0  #green time of signal phase(second)
    cycle=0       #cycle time of signal phase(second)
    offset=0
    green=[]      #green time step list

