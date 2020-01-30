from __future__ import print_function
import re, logging, sys
import random, math
import cmath
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
            
        self.v1 = v1              #x座標
        self.v2 = v2              #y座標
        self.celltype = celltype

    def __str__(self):
        '''str() 関数の引数として与えられた場合に返される文字列
'''
        retval = "v1={0} v2={1} celltype={2}".format(self.v1, self.v2, self.celltype)
        return retval

#搬送車のクラス
class Vehicle:
    speed = 1
    vehicle_x = []                   #他の搬送車の座標を保持
    vehicle_y = []
    static_potential = []            #静的なポテンシャルを保持
    static2_potential = []           #静的なポテンシャルを保持
    dynamic_potential = []           #動的なポテンシャルを保持
    next_x = -1                      #次に移動するセルの座標
    next_y = -1
    goal_x = -1                      #搬送予定場所の座標
    goal_y = -1
    limit_x = -1                     #時限ポテンシャルを定義する座標
    limit_y = -1
    carrier = -1                     #割り当てられた搬送物
    have_carrier = 0                 #搬送物を保持しているかどうか
    driving_time = 0                 #走行時間
    limit_count = 50                  #時限ポテンシャルのリミット
    
    def __init__(self, x, y, ready_x, ready_y, goal, direction, state, vehicle_n, muki):
        self.x = x                 #位置
        self.y = y   
        self.ready_x = ready_x     #待機場所を保持
        self.ready_y = ready_y
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
                if(mapping[i*map_side+j].celltype == 'wall'):
                    self.static_potential.append(8)
                    self.static2_potential.append(8)
                    self.dynamic_potential.append(8)
                elif(mapping[i*map_side+j].celltype == 'no_entry'):
                    self.static_potential.append(8)
                    self.static2_potential.append(8)
                    self.dynamic_potential.append(8)
                elif(mapping[i*map_side+j].celltype == 'accept'):
                    self.static_potential.append(0)
                    self.static2_potential.append(0)
                    self.dynamic_potential.append(0)
                elif(mapping[i*map_side+j].celltype == 'road'):
                    self.static_potential.append(0)
                    self.static2_potential.append(0)    
                    self.dynamic_potential.append(0) 
                
    #静的なポテンシャル場の更新
    def change_s_potential(self):
        for i in range(map_length):
            for j in range(map_side):
                if(self.static_potential[i*map_side+j] != 8):
                    if((j == self.goal_x) and (i == self.goal_y)):
                        self.static2_potential[i*map_side+j] = -3
                        #print(j, i, 1)
                    else:
                        self.static2_potential[i*map_side+j] = self.static_potential[i*map_side+j] + potential(j, i, self.goal_x, self.goal_y, 1)
                        #print(j, i, potential(j, i, self.goal_x, self.goal_y, 1))
                  
                        
                        
    #動的なポテンシャル場の更新
    def change_d_potential(self):
        '''
        for i in range(map_length):
            for j in range(map_side):
                if(self.static_potential[i*map_side+j] != 8):
                    self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                    for count in range(self.vehicle_n):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1
                        else:                                
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                        
                    if((self.limit_x != -1) or (self.limit_y != -1)):
                        self.limit_count = self.limit_count -1
                        if((j == self.limit_x) and (i == self.limit_y)):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1
                        else:
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + potential(j, i, self.limit_x, self.limit_y, 2)
                            
                        if(self.limit_count == 0):
                            self.limit_count = 50
                            self.limit_x = -1
                            self.limit_y = -1    
           '''            
        
        '''
        for i in range(map_length):
            for j in range(map_side):
                if(mapping[i*map_side+j].celltype == 'roal'):
                    for count in range(1):
                        tmp = 0
                        focus1 = -1
                        focus2 = -1
                        for count2 in range(3):
                            for count3 in range(count+1, 4):
                                x1 = kumitate[count].x[count2] - j
                                y1 = kumitate[count].y[count2] - i
                                x2 = kumitate[count].x[count3] - j
                                y2 = kumitate[count].y[count3] - i
                                kotae1 = cmath.phase(complex(x1, y1))
                                kotae2 = cmath.phase(complex(x2, y2))
                                if(tmp < abs(kotae1-kotae2)):
                                    tmp = abs(kotae1-kotae2)
                                    focus1 = count2
                                    focus2 = count3
              
                        #搬送車と焦点の直線距離を求める
                        f_distance1 = distance(kumitate[count].x[focus1], kumitate[count].y[focus1], j, i)
                        f_distance2 = distance(kumitate[count].x[focus2], kumitate[count].y[focus2], j, i)
                        if((focus1 == 0) and (focus2 == 3)):
                            #組み立て場所頂点1の方が近い場合
                            if(distance(kumitate[count].x[1], kumitate[count].y[1], j, i) < distance(kumitate[count].x[2], kumitate[count].y[2], j, i)):
                                obj_distance = distance(kumitate[count].x[1], kumitate[count].y[1], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[1], kumitate[count].y[1], kumitate[count].x[focus2], kumitate[count].y[focus2])
                            else:
                                obj_distance = distance(kumitate[count].x[2], kumitate[count].y[2], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[2], kumitate[count].y[2], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        elif((focus1 == 1) and (focus2 == 2)):
                            if(distance(kumitate[count].x[0], kumitate[count].y[0], j, i) < distance(kumitate[count].x[3], kumitate[count].y[3], j, i)):
                                obj_distance = distance(kumitate[count].x[0], kumitate[count].y[0], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[0], kumitate[count].y[0], kumitate[count].x[focus2], kumitate[count].y[focus2])
                            else:
                                obj_distance = distance(kumitate[count].x[3], kumitate[count].y[3], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[3], kumitate[count].y[3], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        else:
                            obj_distance = distance(kumitate[count].x[focus1], kumitate[count].y[focus1], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        k_distance = f_distance1 + f_distance2 - obj_distance
                        self.static_potential.append(potential2(k_distance))
                
                    for count in range(1, kumitate_sum):
                        tmp = 0
                        focus1 = -1
                        focus2 = -1
                        for count2 in range(3):
                            for count3 in range(count+1, 4):
                                x1 = kumitate[count].x[count2] - j
                                y1 = kumitate[count].y[count2] - i
                                x2 = kumitate[count].x[count3] - j
                                y2 = kumitate[count].y[count3] - i
                                kotae1 = cmath.phase(complex(x1, y1))
                                kotae2 = cmath.phase(complex(x2, y2))
                                if(tmp < abs(kotae1-kotae2)):
                                    tmp = abs(kotae1-kotae2)
                                    focus1 = count2
                                    focus2 = count3
             
                        #搬送車と焦点の直線距離を求める
                        f_distance1 = distance(kumitate[count].x[focus1], kumitate[count].y[focus1], j, i)
                        f_distance2 = distance(kumitate[count].x[focus2], kumitate[count].y[focus2], j, i)
                        if((focus1 == 0) and (focus2 == 3)):
                            if(distance(kumitate[count].x[1], kumitate[count].y[1], j, i) < distance(kumitate[count].x[2], kumitate[count].y[2], j, i)):
                                obj_distance = distance(kumitate[count].x[1], kumitate[count].y[1], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[1], kumitate[count].y[1], kumitate[count].x[focus2], kumitate[count].y[focus2])
                            else:
                                obj_distance = distance(kumitate[count].x[2], kumitate[count].y[2], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[2], kumitate[count].y[2], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        elif((focus1 == 1) and (focus2 == 2)):
                            if(distance(kumitate[count].x[0], kumitate[count].y[0], j, i) < distance(kumitate[count].x[3], kumitate[count].y[3], j, i)):
                                obj_distance = distance(kumitate[count].x[0], kumitate[count].y[0], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[0], kumitate[count].y[0], kumitate[count].x[focus2], kumitate[count].y[focus2])
                            else:
                                obj_distance = distance(kumitate[count].x[3], kumitate[count].y[3], kumitate[count].x[focus1], kumitate[count].y[focus1]) + distance(kumitate[count].x[3], kumitate[count].y[3], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        else:
                            obj_distance = distance(kumitate[count].x[focus1], kumitate[count].y[focus1], kumitate[count].x[focus2], kumitate[count].y[focus2])
                        k_distance = f_distance1 + f_distance2 - obj_distance
                        self.static_potential[i*map_side+j] = self.static_potential[i*map_side+j] + potential(k_distance)
        '''
        
        #時限ポテンシャルがない場合
        if((self.limit_x == -1) and (self.limit_y == -1)):
            for i in range(map_length):
                for j in range(map_side):
                    if(self.static_potential[i*map_side+j] != 8):
                        self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                        for count in range(self.vehicle_n):
                            if(count != self.vehicle_n):
                                if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                                    self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1
                                else:                                
                                    self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)                
                               
                        
        #時限ポテンシャルがある場合                            
        else:
            self.limit_count = self.limit_count -1
            for i in range(map_length):
                for j in range(map_side):
                    if(self.static_potential[i*map_side+j] != 8):
                        self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                        for count in range(self.vehicle_n):
                            if(count != self.vehicle_n):
                                if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                                    if((j == self.limit_x) and (i == self.limit_y)):
                                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1 + 1
                                    else:
                                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1 + potential(j, i, self.limit_x, self.limit_y, 2)
                                else:
                                    if((j == self.limit_x) and (i == self.limit_y)):
                                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1 + 1
                                    else:
                                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + potential(j, i, self.limit_x, self.limit_y, 2) + potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3) 
            if(self.limit_count == 0):
                self.limit_count = 50
                self.limit_x = -1
                self.limit_y = -1
                
        
        
                                

    #動的なポテンシャル場からセルを1つ選択する
    def select_cell(self):
        tmp = 8
        for i in range(self.y-1, self.y+2):
            for j in range(self.x-1, self.x+2):
                #print(j, i, self.dynamic_potential[i*map_side+j]) 
                if(self.dynamic_potential[i*map_side+j] < tmp):
                    tmp = self.dynamic_potential[i*map_side+j]
                    self.next_x = j
                    self.next_y = i
        #print(self.goal_x, self.goal_y, self.dynamic_potential[self.goal_y*map_side+self.goal_x])
        #停留している場合は時限ポテンシャルを定義する座標を決定
        if((self.next_x == self.x) and (self.next_y == self.y)):
            '''
            self.limit_x = self.x
            self.limit_y = self.y
            
            '''
            tmp_x = self.goal_x - self.x
            tmp_y = self.goal_y - self.y
            if((tmp_x <= 0) and (tmp_y <= 0)):
                self.limit_x = self.x +1
                self.limit_y = self.y +1
            elif((tmp_x > 0) and (tmp_y <= 0)):
                self.limit_x = self.x -1
                self.limit_y = self.y +1    
            elif((tmp_x <= 0) and (tmp_y > 0)):
                self.limit_x = self.x +1
                self.limit_y = self.y -1
            elif((tmp_x > 0) and (tmp_y > 0)):
                self.limit_x = self.x -1
                self.limit_y = self.y -1    
            
                    
    #選んだ座標を現在の座標とする
    def move(self):
        self.x = self.next_x
        self.y = self.next_y
        
    #搬送車が搬送物受け取り場所についたときの処理
    def change_goal(self):
        if(self.have_carrier == 0):
            self.have_carrier = 1
            self.goal = carrier[self.carrier].goal
            self.goal_x = point[carrier[self.carrier].goal].in_x
            self.goal_y = point[carrier[self.carrier].goal].in_y
        elif(self.have_carrier == 1):
            self.have_carrier = 0
            self.goal = -1
            self.goal_x = self.ready_x
            self.goal_y = self.ready_y
            self.state = 'ready_move'
            
            
                    
                                                    
#搬送場所の中心のクラス
class Kumitate:
    x = []
    y = []
    def __init__(self, num):
        self.num = num
    def yomikomi(self):
        for l in open('kumitate_test.txt').readlines():
            data = l[:-1].split(' ')
            self.x.append(int(data[0]))
            self.y.append(int(data[1]))            

#搬送地点のクラス
class Point:
     
        def __init__(self, num, in_x, in_y, out_x, out_y):
            self.num = num
            self.in_x = in_x
            self.in_y = in_y
            self.out_x = out_x
            self.out_y = out_y
            
#搬送物のクラス
class Carrier:
    def __init__(self, carrier_time, start, goal,carrier_n):
        self.carrier_time = carrier_time
        self.start = start
        self.goal = goal
        self.carrier_n = carrier_n
        
#楕円ポテンシャルの計算を行う関数
def potential2(d):
    return 0.1/d**2
        
#ポテンシャル関数の計算を行う関数    
def potential(x1, y1, x2, y2, type):
    if(type == 1):
        return -1/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 2):
        return 2/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 3):
        return 0.5/(math.sqrt((x1-x2)**2 + (y1-y2)**2))**2
    
#割り当てる搬送車を見つける関数
def wariate(start):
    minimize = 10000
    for count in range(vehicle_sum):
        if(vehicle[count].state == 'stop'):
            #print('割り当て可能な搬送車が見つかりました')
            tmp = distance(vehicle[count].x, vehicle[count].y, point[vehicle[count].goal].out_x, point[vehicle[count].goal].out_y)
            #print(count, tmp)
            if(minimize > tmp):
                minimize = tmp
                min_vehicle = count
    if(minimize == 10000):
        #print('割り当て可能な搬送車が見つかりませんでした')
        q.append(request_n)
        return -1
    else:
        print('割り当てた搬送車')
        print(minimize, min_vehicle)
        return min_vehicle

#2点間の座標の距離を返す関数
def distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


if __name__ == "__main__":
    
    mapping = []             #マップ情報をリスト型で保持
    request = []         #搬送要求をリスト型で保持
    request_n  = -1      #搬送要求数をカウント
    vehicle = []         #搬送車を格納
    vehicle_n = -1       #搬送車識別番号をカウント
    vehicle_sum = 2      #搬送車の総数
    vehicle_work = 0     #仕事中の搬送車
    kumitate_sum = 1     #組み立て場所の総数
    point = []           #搬送地点をリスト型で保持
    carrier = []         #搬送物をリスト型で保持
    go_carrier = 0       #割り当てを行う搬送物の管理を行う関数
    count = 0
    kumitate = []          #搬送場所の中心点をリスト型で保持    
    q = deque([])        #キューの箱
    map_length = 24      #マップの縦幅
    map_side = 29        #マップの横幅
        
    #マップの作成
    f = open('map_test.txt')
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
        
        
    #マップの表示
    '''
    for count in range(648):
        print(count, mapping[count].v1, mapping[count].v2, mapping[count].celltype)
    '''
  
    #搬送地点を作成
    count = 0
    for l in open('point_test.txt').readlines():
        data = l[:-1].split(' ')
        count = count+1
        in_x = int(data[0])
        in_y = int(data[1])
        out_x = int(data[2])
        out_y = int(data[3])
        obj = Point(count, in_x, in_y, out_x, out_y)
        point.append(obj)
        
    #搬送地点の表示
    '''
    print(point[0].in_x, point[0].in_y, point[0].out_x, point[0].out_y)
    '''
    
    #組み立て場所を読み込み
    count = 0
    for count in range(1):
        obj = Kumitate(count)
        kumitate.append(obj)
    
    kumitate[0].yomikomi()
        
    #組み立て場所を表示
    '''
    for count in range(4):
        print(kumitate[0].x[count], kumitate[0].y[count])
    '''
    
    #搬送車の作成
    for l in open('vehicle_position1_test.txt').readlines():
        data = l[:-1].split(' ')
        vehicle_n = vehicle_n+1
        x = int(data[0])
        y = int(data[1])
        obj = Vehicle(x, y, x, y, -1, -1, 'stop', vehicle_n, 1)
        vehicle.append(obj)
        
    #搬送車の初期位置の表示
    '''
    for count in range(2):
        print(vehicle[count].x, vehicle[count].y)
    '''
    
    #搬送物の生成
    count = 0
    for l in open('carrier_test.txt').readlines():
        count = count+1
        data = l[:-1].split(' ')
        carrier_time = int(data[0])
        start = int(data[1])
        goal = int(data[2])
        obj = Carrier(carrier_time, start, goal, count)
        carrier.append(obj)
    
    #搬送物の表示
    '''
    for count in range(2):
        print(carrier[count].carrier_time, carrier[count].start, carrier[count].goal, carrier[count].carrier_n)
    '''
    
    for count in range(vehicle_sum):
        #他の搬送車の初期位置を取得する
        vehicle[count].get_point()
        
        #ポテンシャル場の生成を行う関数
        vehicle[count].make_potential()        
    
    #他の搬送車の初期位置を表示する
    '''
    for count in range(vehicle_sum):
        for count2 in range(vehicle_sum):
            print(vehicle[count].vehicle_x[count2], vehicle[count].vehicle_y[count2])
    ''' 
    
    #ポテンシャル場を表示する
    '''
    for count in range(648):
        print(count, vehicle[0].static_potential[count], vehicle[0].static2_potential[count], vehicle[0].dynamic_potential[count], mapping[count].celltype)
    '''
    
    #時間を表す
    for time in range(100):
    
        #キューの割り当てを行う
        if(len(q) != 0):
            tmp = q.popleft()
            min_vehicle = wariate(request[tmp].start)
            if(min_vehicle == -1):
                q.append(tmp)
            else:
                #割り当て作業を行う
                print(min_vehicle)
                vehicle[min_vehicle].goal = carrier[tmp].start
                vehicle[min_vehicle].goal_x = point[carrier[tmp].start].out_x
                vehicle[min_vehicle].goal_y = point[carrier[tmp].start].out_y
                vehicle[min_vehicle].carrier = carrier[tmp].carrier_n
                vehicle[min_vehicle].state = 'move'
                vehicle[min_vehicle].change_s_potential()

        #搬送要求の発生時刻処理
        print('time', time)
        if(time == carrier[go_carrier].carrier_time):
            #搬送要求の割り当て処理
            min_vehicle = wariate(carrier[go_carrier].start)
            #割り当てる搬送車が見つからなかった場合
            if(min_vehicle == -1):
                q.append(go_carrier)
            else:
                vehicle[min_vehicle].goal = carrier[go_carrier].start
                vehicle[min_vehicle].goal_x = point[carrier[go_carrier].start].out_x
                vehicle[min_vehicle].goal_y = point[carrier[go_carrier].start].out_y
                vehicle[min_vehicle].carrier = carrier[go_carrier].carrier_n
                vehicle[min_vehicle].state = 'move'
                vehicle[min_vehicle].change_s_potential()
                
                #移動予定場所と組み立て場所のポテンシャル場の表示
                '''
                for count in range(648):
                    print(count, vehicle[min_vehicle].static2_potential[count], mapping[count].celltype)
                '''
                
            go_carrier = go_carrier+1
            
        #搬送車の移動
        for count in range(vehicle_sum):
            if(vehicle[count].state == 'ready_move'):
                vehicle[count].driving_time = vehicle[count].driving_time +1
                vehicle[count].change_point()
                vehicle[count].change_d_potential()
                vehicle[count].select_cell()
                vehicle[count].move()
                
                if((vehicle[count].x == vehicle[count].goal_x) and (vehicle[count].y == vehicle[count].goal_y)):
                    print('搬送車待機場所に到着しました')
                    print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    vehicle[count].goal_x = -1
                    vehicle[count].goal_y = -1
                    vehicle[count].state = 'stop'
            
            elif(vehicle[count].state == 'move'):
                vehicle[count].driving_time = vehicle[count].driving_time +1
                vehicle[count].change_point()
                
                #他の搬送車の現在地の表示
                '''
                for count2 in range(vehicle_sum):
                    print(vehicle[count].vehicle_x[count2], vehicle[count].vehicle_y[count2])
                '''
                
                vehicle[count].change_d_potential()
                
                #動的ポテンシャル場の表示
                '''
                for count2 in range(648):
                    print(count2, vehicle[count].dynamic_potential[count2], mapping[count2].celltype)
                '''
                
                vehicle[count].select_cell()
                
                #移動予定のセルの表示
                '''
                print(vehicle[count].next_x, vehicle[count].next_y)
                '''
                
                vehicle[count].move()
                
                #移動した現在地を表示
                print(count, vehicle[count].x, vehicle[count].y)
                
                if((vehicle[count].x == vehicle[count].goal_x) and (vehicle[count].y == vehicle[count].goal_y)):
                    print('搬送物受け取り地点に到達しました')
                    print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    vehicle[count].change_goal()
                    print('搬送物受け渡し地点', vehicle[count].goal_x, vehicle[count].goal_y)
                    vehicle[count].change_s_potential()
                
    #結果の出力
    sum_driving_time = 0
    for count in range(vehicle_sum):
        sum_driving_time = vehicle[count].driving_time + sum_driving_time
        
    print('走行時間の総和', sum_driving_time)            