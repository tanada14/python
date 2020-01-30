from __future__ import print_function
import re, logging, sys
import random, math
from collections import deque

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("Cell")
logger.setLevel(logging.DEBUG)

#セルのクラス
class Cell:
    
    def __init__(self, v1=None, v2=None, celltype=None, move=None, line=None):
        '''メンバの値を設定する
'''
        if line is None:
            assert v1 is not None and v2 is not None and celltype is not None and move is not None, "invalid arguments={}".format( (v1, v2, celltype, move) )
        else:
            ## スペースで区切られた3つの要素 (整数 整数 文字列) からメンバの値を設定する
            m = re.match("^(\d+)\s+(\d+)\s+(\w+)\s+(\w+).*$", line)
            assert m is not None, "invalid line={}".format(line)
            v1, v2, celltype, move = m.groups()
            
        self.v1 = v1              #x座標
        self.v2 = v2              #y座標
        self.celltype = celltype
        self.move = move

    def __str__(self):
        '''str() 関数の引数として与えられた場合に返される文字列
'''
        retval = "v1={0} v2={1} celltype={2} move={3}".format(self.v1, self.v2, self.celltype, self.move)
        return retval

#搬送車のクラス
class Vehicle:
    speed = 1
    vehicle_x = []                   #他の搬送車の座標を保持
    vehicle_y = []
    #static_potential = []            #静的なポテンシャルを保持
    #static2_potential = []           #静的なポテンシャルを保持
    #dynamic_potential = []           #動的なポテンシャルを保持
    next_x = -1                      #次に移動するセルの座標
    next_y = -1
    goal_x = -1                      #搬送予定場所の座標
    goal_y = -1
    carrier = -1                     #割り当てられた搬送物
    have_carrier = 0                 #搬送物を保持しているかどうか
    driving_time = 0                 #走行時間
    
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

    #ポテンシャル法を用いない方法での移動
    def select_cell(self):
        if(mapping[self.y*map_side + self.x].move == 'right'):
            self.next_y = self.y
            self.next_x = self.x +1
        elif(mapping[self.y*map_side + self.x].move == 'left'):
            self.next_y = self.y
            self.next_x = self.x -1
        elif(mapping[self.y*map_side + self.x].move == 'up'):
            self.next_y = self.y -1
            self.next_x = self.x
        elif(mapping[self.y*map_side + self.x].move == 'down'):
            self.next_y = self.y +1
            self.next_x = self.x
        elif(mapping[self.y*map_side + self.x].move == 'leftdown'):
            if(self.x == self.goal_x):
                self.next_y = self.y +1
                self.next_x = self.x
            elif(self.y == self.goal_y):
                self.next_y = self.y
                self.next_x = self.x -1
            else:
                self.next_y = self.y +1
                self.next_x = self.x
        elif(mapping[self.y*map_side + self.x].move == 'rightup'):
            if(self.x == self.goal_x):
                self.next_y = self.y -1
                self.next_x = self.x
            elif(self.y == self.goal_y):
                self.next_y = self.y
                self.next_x = self.x +1
            else:
                self.next_y = self.y -1
                self.next_x = self.x
        elif(mapping[self.y*map_side + self.x].move == 'rightdown'):
            if(self.x == self.goal_x):
                self.next_y = self.y +1
                self.next_x = self.x
            elif(self.y == self.goal_y):
                self.next_y = self.y
                self.next_x = self.x +1
            else:
                self.next_y = self.y
                self.next_x = self.x +1
        elif(mapping[self.y*map_side + self.x].move == 'leftup'):
            if(self.x == self.goal_x):
                self.next_y = self.y -1
                self.next_x = self.x
            elif(self.y == self.goal_y):
                self.next_y = self.y
                self.next_x = self.x -1
            else:
                self.next_y = self.y
                self.next_x = self.x -1                        

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
            
    #待機場所のセルへ移動するための特別な移動
    def special_move(self):
        self.x = self.goal_x
        self.y = self.goal_y
        self.state = 'stop'
        self.goal_x = -1
        self.goal_y = -1
            
                                                    
#搬送場所の中心のクラス
class Center:
    def __init__(self, num, x, y):
        self.num = num
        self.x = x
        self.y = y
                                            
                                    


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
    para = 10
    
    def __init__(self, occured_time, start, goal,carrier_n, arrival_time):
        self.occured_time = occured_time
        self.start = start
        self.goal = goal
        self.carrier_n = carrier_n
        self.arrival_time = arrival_time
        self.ok = 0
        
    def arrival(self, have_carrier, time):
        if(have_carrier == 1):
            self.arrival_time = time
    
    def time_required(self):
        if(self.start == 0):
            if((self.arrival_time-self.occured_time) <= (60*self.para)):
                self.ok = 1
        elif(self.start == 1):
            if((self.arrival_time-self.occured_time) <= (1*self.para)):
                self.ok = 1        
        
#ポテンシャル関数の計算を行う関数    
def potential(x1, y1, x2, y2, type):
    if(type == 1):
        return 1/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 2):
        return -0.5/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 3):
        return -0.3/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
#割り当てる搬送車を見つける関数
def wariate(start):
    minimize = 10000
    for count in range(vehicle_sum):
        if((vehicle[count].state == 'stop') or (vehicle[count].state == 'ready_move')):
            #print('割り当て可能な搬送車が見つかりました')
            tmp = destance(vehicle[count].x, vehicle[count].y, point[vehicle[count].goal].out_x, point[vehicle[count].goal].out_y)
            #print(count, tmp)
            if(minimize > tmp):
                minimize = tmp
                min_vehicle = count
    if(minimize == 10000):
        #print('割り当て可能な搬送車が見つかりませんでした')
        #q.append(request_n)
        return -1
    else:
        '''
        print('time', time)
        print('割り当てた搬送車', min_vehicle)
        '''
        #print(vehicle[min_vehicle].x, vehicle[min_vehicle].y)
        return min_vehicle

#2点間の座標の距離を返す関数
def destance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == "__main__":
    
    mapping = []             #マップ情報をリスト型で保持
    request = []         #搬送要求をリスト型で保持
    request_n  = -1      #搬送要求数をカウント
    vehicle = []         #搬送車を格納
    vehicle_n = -1       #搬送車識別番号をカウント
    vehicle_sum = 3      #搬送車の総数
    vehicle_work = 0     #仕事中の搬送車
    kumitate_sum = 2     #組み立て場所の総数
    point = []           #搬送地点をリスト型で保持
    carrier = []         #搬送物をリスト型で保持
    go_carrier = 0       #割り当てを行う搬送物の管理を行う関数
    sum_carrier = -1     #搬送物の合計個数
    count = 0
    center = []          #搬送場所の中心点をリスト型で保持    
    q = deque([])        #キューの箱
    map_length = 44      #マップの縦幅
    map_side = 27        #マップの横幅
    path = 'vehicle_visual.txt'
    
    #マップの作成
    f = open('map_test2.txt')
    data1 = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()
    
    i=0
    j=0
    for line in data1:
        if(line == '#'):
            #print(i, j, 'wall')
            l = str(i) + ' ' + str(j) + ' ' + 'wall' + ' ' + 'no'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '-'):
            #print(i, j, 'road')
            l = str(i) + ' ' + str(j) + ' ' + 'road' + ' ' + 'no'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '>'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'right'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '<'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'left'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '^'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'up'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == 'v'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'down'
            obj = Cell(line = l)
            mapping.append(obj)            
        elif(line == 'a'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'leftdown'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == 'b'):
            l = str(i) + ' ' + str(j) + ' ' + 'roal' + ' ' + 'rightup'
            obj = Cell(line = l)
            mapping.append(obj)            
        elif(line == '+'):
            #print(i, j, 'no entry')
            l = str(i) + ' ' + str(j) + ' ' + 'no_entry' + ' ' + 'no'
            obj = Cell(line = l)
            mapping.append(obj)
        elif(line == '*'):
            #print(i, j, 'accept')
            l = str(i) + ' ' + str(j) + ' ' + 'accept' + ' ' + 'no'
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
    for count in range(1188):
        print(count, mapping[count].v1, mapping[count].v2, mapping[count].celltype, mapping[count].move)
    '''
  
    #搬送地点を作成
    count = 0
    for l in open('point_test2.txt').readlines():
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
    for count in range(3):
        print(point[count].in_x, point[count].in_y, point[count].out_x, point[count].out_y)
    '''
    
    #搬送車の作成
    for l in open('vehicle_position1_test2.txt').readlines():
        data = l[:-1].split(' ')
        vehicle_n = vehicle_n+1
        x = int(data[0])
        y = int(data[1])
        obj = Vehicle(x, y, x, y, -1, -1, 'stop', vehicle_n, 1)
        vehicle.append(obj)
        
    #搬送車の初期位置の表示
    '''
    for count in range(vehicle_sum):
        print(vehicle[count].x, vehicle[count].y)
    '''
    
    #搬送物の生成
    count = 0
    for l in open('carrier_test4.txt').readlines():
        data = l[:-1].split(' ')
        occured_time = int(data[0])
        start = int(data[1])
        goal = int(data[2])
        obj = Carrier(occured_time, start, goal, count, -1)
        carrier.append(obj)
        count = count+1
    sum_carrier = count -1
    
    #搬送物の表示
    '''
    for count in range(3):
        print(carrier[count].occured_time, carrier[count].start, carrier[count].goal, carrier[count].carrier_n)
    '''
       
    for count in range(vehicle_sum):
        #他の搬送車の初期位置を取得する
        vehicle[count].get_point()
                
    #他の搬送車の初期位置を表示する
    '''
    for count in range(vehicle_sum):
        for count2 in range(vehicle_sum):
            print(vehicle[count].vehicle_x[count2], vehicle[count].vehicle_y[count2])
    ''' 
    
    #搬送車経路を示すファイル
    f = open(path, 'w')
    
    #時間を表す
    for time in range(10000):    
    
        #キューの割り当てを行う
        if(len(q) != 0):
            tmp = q.popleft()
            min_vehicle = wariate(carrier[tmp].start)
            if(min_vehicle == -1):
                q.append(tmp)
            else:
                #割り当て作業を行う
                #print(min_vehicle)
                vehicle[min_vehicle].goal = carrier[tmp].start
                vehicle[min_vehicle].goal_x = point[carrier[tmp].start].out_x
                vehicle[min_vehicle].goal_y = point[carrier[tmp].start].out_y
                vehicle[min_vehicle].carrier = carrier[tmp].carrier_n
                vehicle[min_vehicle].state = 'move'
                
                f.write(str(time)+' ')
                f.write(str(vehicle_sum+min_vehicle)+' '+str(vehicle[min_vehicle].goal_x)+' '+str(vehicle[min_vehicle].goal_y)+'\n')
                
        #搬送要求の発生時刻処理
        #print('time', time)
        if(time == carrier[go_carrier].occured_time):
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
                
                f.write(str(time)+' ')
                f.write(str(vehicle_sum+min_vehicle)+' '+str(vehicle[min_vehicle].goal_x)+' '+str(vehicle[min_vehicle].goal_y)+'\n')
                
            go_carrier = go_carrier+1
            
        #搬送車の移動
        for count in range(vehicle_sum):
            if(vehicle[count].state == 'move'):
                vehicle[count].driving_time = vehicle[count].driving_time +1
                vehicle[count].change_point()
                vehicle[count].select_cell()
                vehicle[count].move()
                
                #移動した現在地を表示
                #print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                
                f.write(str(time)+' ')
                f.write(str(count)+' '+str(vehicle[count].x)+' '+str(vehicle[count].y)+'\n')
            
                if((vehicle[count].x == vehicle[count].goal_x) and (vehicle[count].y == vehicle[count].goal_y)):
                    '''
                    print('time', time)
                    print('搬送物受け取り地点に到達しました')
                    print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    '''
                    
                    #搬送物の到着時間を記録
                    carrier[vehicle[count].carrier].arrival(vehicle[count].have_carrier, time)
                    
                    vehicle[count].change_goal()
                    last = time
                    
            elif(vehicle[count].state == 'ready_move'):
                vehicle[count].driving_time = vehicle[count].driving_time +1
                vehicle[count].change_point()
                vehicle[count].select_cell()
                vehicle[count].move()
                
                #移動した現在地を表示
                #print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                f.write(str(time)+' ')
                f.write(str(count)+' '+str(vehicle[count].x)+' '+str(vehicle[count].y)+'\n')
                
                if((vehicle[count].x - vehicle[count].goal_x)**2 + (vehicle[count].y - vehicle[count].goal_y)**2 == 1):
                    #特別な移動
                    #print('time', time)
                    vehicle[count].special_move()
                    #print('待機地点に到達しました')
                    #print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    f.write(str(time)+' ')
                    f.write(str(count)+' '+str(vehicle[count].x)+' '+str(vehicle[count].y)+'\n')
                    
    #結果の出力
    sum_driving_time = 0
    for count in range(vehicle_sum):
        sum_driving_time = vehicle[count].driving_time + sum_driving_time
    
    #搬送物の発生から到着に要した時間
    sum_ok = 0
    for count in range(sum_carrier):
        carrier[count].time_required()
        sum_ok = sum_ok + carrier[count].ok
        #print(count, carrier[count].occured_time, carrier[count].arrival_time)
    print(sum_ok)
    
    #print('終了時刻', last)   
    print('走行時間の総和', sum_driving_time)
    print('最終走行完了時間', last-carrier[0].occured_time)
    
    f.close()