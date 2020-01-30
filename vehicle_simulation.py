from __future__ import print_function
import re, logging, sys
import random, math
from collections import deque

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("Cell")
logger.setLevel(logging.DEBUG)

#セルのクラス
class Cell:
    
    def __init__(self, v1=None, v2=None, celltype=None, line=None):
        '''メンバの値を設定する
'''
        if line is None:
            assert v1 is not None and v2 is not None and celltype is not None, "invalid arguments={}".format( (v1, v2, celltype) )
        else:
            ## スペースで区切られた3つの要素 (整数 整数 文字列) からメンバの値を設定する
            m = re.match("^(\d+)\s+(\d+)\s+(\w+).*$", line)
            assert m is not None, "invalid line={}".format(line)
            v1, v2, celltype = m.groups()
            
        self.v1 = v1
        self.v2 = v2
        self.celltype = celltype

    def __str__(self):
        '''str() 関数の引数として与えられた場合に返される文字列
'''
        retval = "v1={0} v2={1} celltype={2}".format(self.v1, self.v2, self.celltype)
        return retval

#搬送車のクラス
class Vehicle:
    speed = 1                        #搬送車の速度を規定
    vehicle_x = []                   #他の搬送車の座標を保持
    vehicle_y = []
    static_potential = []            #静的なポテンシャルを保持
    static2_potential = []           #静的なポテンシャルを保持
    dynamic_potential = []           #動的なポテンシャルを保持
    next_x = -1                      #次に移動するセルの座標
    next_y = -1
    
    def __init__(self, x, y, goal, direction, state, vehicle_n, muki):
        self.x = x                 #位置
        self.y = y   
        self.goal = goal           #移動予定場所
        self.direction = direction #移動方向
        self.state = state         #状態
        self.vehicle_n = vehicle_n #搬送車識別番号
        self.muki = muki           #搬送車が向いている向き
        
    #他の搬送車の初期位置を取得する    
    def get_point(self):
        for count in range(vehicle_sum):
            self.vehicle_x.append(vehicle[count].x)
            self.vehicle_y.append(vehicle[count].y)
            
    #他の搬送車の現在地を取得する        
    def change_point(self):
        for count in range(vehicle_sum):
            self.vehicle_x[count] = vehicle[count].x
            self.vehicle_y[count] = vehicle[count].y
            
    #ポテンシャル場の生成
    def make_potential(self):
        for i in range(map_length):
            for j in range(map_side):
                if(mapping[i+j].celltype == 'wall'):
                    self.static_potential.append(-16)
                    self.static2_potential.append(-16)
                    self.dynamic_potential.append(-16)
                elif(mapping[i+j].celltype == 'no_entry'):
                    self.static_potential.append(-16)
                    self.static2_potential.append(-16)
                    self.dynamic_potential.append(-16)
                elif(mapping[i+j].celltype == 'accept'):
                    self.static_potential.append(-16)
                    self.static2_potential.append(-16)
                    self.dynamic_potential.append(-16)
                elif(mapping[i+j].celltype == 'road'):
                    self.static_potential.append(potential(i, j, center[0].x, center[0].y, 2))
                    for k in range(1, kumitate_sum):
                        self.static_potential[i+j] = self.static_potential[i+j] + potential(j, i, center[k].x, center[k].y, 2)
                    self.static2_potential.append(0)    
                    self.dynamic_potential.append(0)
                    
    #静的なポテンシャル場の更新
    def change_s_potential(self, x1, y1):
        for i in range(map_length):
            for j in range(map_side):
                if(static_potential[i+j] != -16):
                    static2_potential[i+j] = static_potential[i+j] + potential(j, i, x1, y1, 1)
    
    #動的なポテンシャル場の更新
    def change_d_potential(self):
        for i in range(map_length):
            for j in range(map_side):
                self.dynamic_potential[i+j] = self.static2_potential[i+j]
                for count in range(vehicle_sum):
                    if(count != vehicle_n):
                        self.dynamc_potential[i+j] = self.dynamic_potential[i+j] + potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
    
    #動的なポテンシャル場からセルを1つ選択する
    def select_cell(self):
        tmp = -16
        for i in range(self.y-1, self.y+2):
            for j in range(self.x-1, self.y+2):
                if(self.dynamic_potential[i+j] > tmp):
                    tmp = dynamic_potential[i+j]
                    next_x = j
                    next_y = i
                    
    #選んだ座標を現在の座標とする
    def move(self):
        self.x = self.next_x
        self.y = self.next_y
        
        

#搬送物のクラス
class Carrier:
    def __init__(self, born, start, goal, vehicle, starttime, goaltime, state):
        self.born = born           #発生時刻
        self.start = start         #出発時刻
        self.goal = goal           #目的場所
        self.vehicle = vehicle     #割り当てられた搬送車
        self.starttime = starttime #乗車時刻
        self.goaltime = goaltime   #降車時刻
        self.state = state         #状態
        
#搬送地点のクラス
class Point:
     
    def __init__(self, num, in_x, in_y, out_x, out_y):
        self.num = num
        self.in_x = in_x
        self.in_y = in_y
        self.out_x = out_x
        self.out_y = out_y
        
#搬送場所の中心のクラス
class Center:
    def __init__(self, num, x, y):
        self.num = num
        self.x = x
        self.y = y
            
#スケジューラのクラス
class Scheduler:
    def __init__(self, start, goal, request_n):
        self.start = start         #搬送物の出発位置
        self.goal = goal           #搬送物の目的位置
        self.request_n = request_n #搬送要求番号
        
#2点間の座標の距離を返す関数
def destance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

#割り当てる搬送車を見つける関数
def wariate(start):
    minimize = 10000
    for count in range(vehicle_sum):
        if(vehicle[count].state == 'stop'):
            print('割り当て可能な搬送車が見つかりました')
            tmp = destance(vehicle[count].x, vehicle[count].y, point[start].out_x, point[start].out_y)
            print(count, tmp)
            if(minimize > tmp):
                minimize = tmp
                min_vehicle = count
    if(minimize == 10000):
        print('割り当て可能な搬送車が見つかりませんでした')
        q.append(request_n)
        return -1
    else:
        print('割り当てた搬送車')
        print(minimize, min_vehicle)
        return min_vehicle
    
#ポテンシャル関数の計算を行う関数    
def potential(x1, y1, x2, y2, type):
    if(type == 1):
        return 1/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 2):
        return -2/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 3):
        return -0.5/math.sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == "__main__":
    
    mapping = []             #マップ情報をリスト型で保持
    request = []         #搬送要求をリスト型で保持
    request_n  = -1      #搬送要求数をカウント
    vehicle = []         #搬送車を格納
    vehicle_n = -1       #搬送車識別番号をカウント
    vehicle_sum = 8      #搬送車の総数
    vehicle_work = 0     #仕事中の搬送車
    kumitate_sum = 8     #組み立て場所の総数
    point = []           #搬送地点をリスト型で保持
    center = []          #搬送場所の中心点をリスト型で保持
    count = 0
    q = deque([])        #キューの箱
        
    
    #マップの作成
    f = open('map1.txt')
    data1 = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()
    
    i=0
    j=0
    for line in data1:
        if(line == '#'):
            #print(i, j, 'wall')
            l = str(i) + ' ' + str(j) + ' ' + 'wall'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '-'):
            #print(i, j, 'road')
            l = str(i) + ' ' + str(j) + ' ' + 'road'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '+'):
            #print(i, j, 'no entry')
            l = str(i) + ' ' + str(j) + ' ' + 'no_entry'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '*'):
            #print(i, j, 'accept')
            l = str(i) + ' ' + str(j) + ' ' + 'accept'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '/'):
            j=j+1
            i=0
        else:
            i=i-2
        i=i+1
        
    #搬送地点を作成
    count = 0
    for l in open('point1.txt').readlines():
        data = l[:-1].split(' ')
        count = count+1
        in_x = int(data[0])
        in_y = int(data[1])
        out_x = int(data[2])
        out_y = int(data[3])
        obj = Point(count, in_x, in_y, out_x, out_y)
        point.append(obj)
        
    #組み立て場所の中心点を読み込み
    count = 0
    for l in open('kumitatecenter.txt').readlines():
        data = l[:-1].split(' ')
        count = count+1
        x = int(data[0])
        y = int(data[1])
        obj = Center(count, x, y)
        center.append(obj)
        
    #搬送車の作成
    for l in open('vehicle_position1.txt').readlines():
        data = l[:-1].split(' ')
        vehicle_n = vehicle_n+1
        x = int(data[0])
        y = int(data[1])
        obj = Vehicle(x, y, -1, -1, 'stop', vehicle_n, 1)
        vehicle.append(obj)
        
    for count in range(vehicle_sum):
        #他の搬送車の初期位置を取得する
        vehicle[count].get_point()
        
        #ポテンシャル場の生成を行う関数
        vehicle[count].make_potential()
        
    #時間を表す
    #for time in range(10):
    
    #キューの割り当てを行う
    if(len(q) != 0):
        tmp = q.popleft()
        min_vehicle = wariate(request[tmp].start)
        if(min_vehicle == -1):
            q.append(tmp)
        else:
            #割り当て作業を行う
            print(min_vehicle)
            vehicle[min_vehicle].goal = request[tmp].start
            vehicle[min_vehicle].state = 'move'
        
        
    #この繰り返しで搬送要求が発生するか決定
    if(random.random() < 0.9):
        print('搬送要求が発生')
        request_n = request_n+1
        print(request_n)
        
        #スタートとゴールを設定
        start = random.randint(1, 7)
        goal = random.randint(start, 8)
        
        #搬送物のオブジェクトを生成
        obj = Scheduler(start, goal, request_n)
        request.append(obj)
        print(request[request_n].request_n, request[request_n].start, request[request_n].goal)
        
        #割り当てる搬送車を決定し割り当てを行う
        min_vehicle = wariate(request[request_n].start)
        print(min_vehicle)
        vehicle[min_vehicle].goal = request[request_n].start
        vehicle[min_vehicle].state = 'move'
        vehicle[min_vehicle].change_s_potential(point[start].out_x, point[start].out_y)
        
    #搬送車の移動
    for count in range(vehicle_sum):
        if(vehicle[count].state == 'move'):
            vehicle[count].change_point()
            vehicle[count].change_d_potential()
            vehicle[count].select_cell()
            vehicle[count].move()
            
            
            
        
            
            

        
