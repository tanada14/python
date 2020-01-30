from __future__ import print_function
import re, logging, sys
import random, math
import cmath
from collections import deque
from queue import LifoQueue

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("Cell")
logger.setLevel(logging.DEBUG)

#セルのクラス
class Cell:
    def __init__(self, x, y, celltype):
        self.x = x
        self.y = y
        self.celltype = celltype
        
#搬送車のクラス
class Vehicle:
    speed = 1
    map_length = 44                                                    #マップの縦幅
    map_side = 27                                                      #マップの横幅    
    node_num = map_length*map_side                                     #ノード数
    route_list = [[float(0) for i in range(1188)] for j in range(1188)]#アークと重み
    unsearched_nodes = list(range(1188))                               #未探索ノード
    distance = [math.inf] * 1188                                       #始点からの重みの和
    
    def __init__(self, x, y, ready_x, ready_y, goal, direction, state, vehicle_n, muki):
        self.x = x                                    #位置
        self.y = y   
        self.ready_x = ready_x                        #待機場所を保持
        self.ready_y = ready_y
        self.goal = goal                              #移動予定場所
        self.direction = direction                    #移動方向
        self.next_direction = -1                      #次の時刻の移動方向
        self.state = state                            #状態
        self.vehicle_n = vehicle_n                    #搬送車識別番号
        self.muki = muki                              #搬送車が向いている向き
        self.vehicle_x = []                           #他の搬送車の座標を保持
        self.vehicle_y = []
        self.static_potential = []                    #静的なポテンシャルを保持
        self.static2_potential = []                   #静的なポテンシャルを保持
        self.dynamic_potential = []                   #動的なポテンシャルを保持
        self.next_x = -1                              #次に移動するセルの座標
        self.next_y = -1
        self.next_next_x = -1                         #次の次に移動する予定のセルの座標（必ず移動するとは限らない）
        self.next_next_y = -1
        self.goal_x = -1                              #搬送予定場所の座標
        self.goal_y = -1
        self.limit_x = -1                             #時限ポテンシャルを定義する座標
        self.limit_y = -1
        self.limit_x2 = -1
        self.limit_y2 = -1
        self.double_limit = 0                         #時限ポテンシャルを二つ定義しているか判定する
        self.carrier = -1                             #割り当てられた搬送物
        self.have_carrier = 0                         #搬送物を保持しているかどうか
        self.driving_time = 0                         #走行時間
        self.limit_count = 50                         #時限ポテンシャルのリミット
        self.limit_count2 = 10
        self.rank = self.vehicle_n                    #搬送車の優先順位
        self.previous_nodes = [-1] * Vehicle.node_num #最短距離の前ノード
        self.f_dijkstra = 0
        self.q = LifoQueue()
        self.prev_x = -1                              #搬送車の単位時間前の位置
        self.prev_y = -1
        self.q_control = -1
            
        
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
                        self.static2_potential[i*map_side+j] = -1.1
                    else:
                        tmp = potential(j,i,self.goal_x,self.goal_y,1)
                        self.static2_potential[i*map_side+j] = self.static_potential[i*map_side+j] + tmp
                        
                  
                        
                        
    #動的なポテンシャル場の更新
    def change_d_potential(self):
        #ダイクストラ法で移動するか
        if(self.rank == 0):
            if(self.f_dijkstra == 0):
                self.dijkstra()
                self.f_dijkstra = 1
                
                
        else:
            #時限ポテンシャルがない場合
            if((self.limit_x == -1) and (self.limit_y == -1)):
                for i in range(map_length):
                    for j in range(map_side):
                        if(self.static_potential[i*map_side+j] != 8):
                            self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                            #搬送車ポテンシャルをdynamic_potentialに追加
                            self.vehicle_potential(i, j)
                            
            #時限ポテンシャルがある場合                            
            elif(self.double_limit == 0):
                self.limit_count = self.limit_count -1
                for i in range(map_length):
                    for j in range(map_side):
                        if(self.static_potential[i*map_side+j] != 8):
                            self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                            #搬送車ポテンシャルをdynamic_potentialに追加
                            self.vehicle_potential(i, j)
                            #時限ポテンシャルをdynamic_potentialに追加
                            self.limit_potential1(i, j)
                if(self.limit_count == 0):
                    self.limit_count = 50
                    self.limit_x = -1
                    self.limit_y = -1
            #ダブル時限ポテンシャルがある場合        
            elif(self.double_limit == 1):
                self.limit_count = self.limit_count -1
                self.limit_count2 = self.limit_count2 -1
                for i in range(map_length):
                    for j in range(map_side):
                        if(self.static_potential[i*map_side+j] != 8):
                            self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]
                            #搬送車ポテンシャルをdynamic_potentialに追加
                            self.vehicle_potential(i, j)
                            #時限ポテンシャルをdynamic_potentialに追加
                            self.limit_potential1(i, j)
                            #二次時限ポテンシャルをdynamic_potentialに追加
                            self.limit_potential2(i, j)
                if(self.limit_count2 == 0):
                    self.limit_count2 = 10
                    self.limit_x2 = -1
                    self.limit_y2 = -1
                    self.double_limit = 0 
                if(self.limit_count == 0):
                    self.limit_count = 50
                    self.limit_x = -1
                    self.limit_y = -1

    #搬送車ポテンシャル
    def vehicle_potential(self, i, j):
        for k in range(self.rank):
            count = rank.v_rank[k]
            
            if(vehicle[count].direction == vehicle[count].next_direction):
                if(vehicle[count].direction == 0):
                    if((j == self.vehicle_x[count]) and (i >= self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                    
                elif(vehicle[count].direction == 1):
                    if((j >= self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                              
                elif(vehicle[count].direction == 2):
                    if((j == self.vehicle_x[count]) and (i <= self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                           
                elif(vehicle[count].direction == 3):
                    if((j <= self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp
                            
                elif(vehicle[count].direction == 4):
                    if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                    else:
                        tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp

            else:
                if(vehicle[count].direction == 0):
                    if((j == self.vehicle_x[count]) and (i >= self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                    
                elif(vehicle[count].direction == 1):
                    if((j >= self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                              
                elif(vehicle[count].direction == 2):
                    if((j == self.vehicle_x[count]) and (i <= self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                           
                elif(vehicle[count].direction == 3):
                    if((j <= self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp
                            
                elif(vehicle[count].direction == 4):
                    if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                    else:
                        tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp

                if(vehicle[count].next_direction == 0):
                    if((j == vehicle[count].next_x) and (i >= vehicle[count].next_y)):
                        if((j == vehicle[count].next_x) and (i == vehicle[count].next_y)):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, vehicle[count].next_x, vehicle[count].next_y, 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                    
                elif(vehicle[count].next_direction == 1):
                    if((j >= vehicle[count].next_x) and (i == vehicle[count].next_y)):
                        if((j == vehicle[count].next_x) and (i == vehicle[count].next_y)):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, vehicle[count].next_x, vehicle[count].next_y, 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                         
                elif(vehicle[count].next_direction == 2):
                    if((j == vehicle[count].next_x) and (i <= vehicle[count].next_y)):
                        if((j == vehicle[count].next_x) and (i == vehicle[count].next_y)):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, vehicle[count].next_x, vehicle[count].next_y, 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp                                
                elif(vehicle[count].next_direction == 3):
                    if((j <= vehicle[count].next_x) and (i == vehicle[count].next_y)):
                        if((j == vehicle[count].next_x) and (i == vehicle[count].next_y)):
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                        else:
                            tmp = potential(j, i, vehicle[count].next_x, vehicle[count].next_y, 3)
                            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp
                '''            
                elif(vehicle[count].next_direction == 4):
                    if((j == vehicle[count].next_x) and (i == vehicle[count].next_y)):
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1.2
                    else:
                        tmp = potential(j, i, vehicle[count].next_x, vehicle[count].next_y, 3)
                        self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp 
                '''
                
            '''
            if((j == self.vehicle_x[count]) and (i == self.vehicle_y[count])):
                self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1
            else:
                tmp = potential(j, i, self.vehicle_x[count], self.vehicle_y[count], 3)
                self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp
            '''
                    
    #時限ポテンシャル
    def limit_potential1(self, i, j):
        if((j == self.limit_x) and (i == self.limit_y)):
            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +1
        else:
            tmp = potential(j, i, self.limit_x, self.limit_y, 2)
            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] + tmp
            
    #二次時限ポテンシャル
    def limit_potential2(self, i, j):
        if((j == self.limit_x2) and (i == self.limit_y2)):
            self.dynamic_potential[i*map_side+j] = self.dynamic_potential[i*map_side+j] +3
        
    #ダイクストラ法による経路導出
    def dijkstra(self):
        #初期化
        Vehicle.route_list = [[float(0) for i in range(Vehicle.node_num)] for j in range(Vehicle.node_num)]
        Vehicle.unsearched_nodes = list(range(Vehicle.node_num))
        Vehicle.distance = [math.inf] * Vehicle.node_num
        self.previous_nodes = [-1] * Vehicle.node_num
        while(self.q.qsize()>0):
            tmp = self.q.get(False, None)
        
        
        #重みの生成
        for i in range(1, map_length-1):
            for j in range(1, map_side-1):
                self.dynamic_potential[i*map_side+j] = self.static2_potential[i*map_side+j]+1
        for i in range(1, map_length-1):
            for j in range(1, map_side-1):
                tmp = i*map_side+j
                if(self.dynamic_potential[tmp - map_side] != 9):
                    Vehicle.route_list[tmp][tmp - map_side] = (self.dynamic_potential[tmp]+self.dynamic_potential[tmp-map_side])/2
                if(self.dynamic_potential[tmp + map_side] != 9):
                    Vehicle.route_list[tmp][tmp + map_side] = (self.dynamic_potential[tmp]+self.dynamic_potential[tmp+map_side])/2                   
                if(self.dynamic_potential[tmp - 1] != 9):
                    Vehicle.route_list[tmp][tmp - 1] = (self.dynamic_potential[tmp]+self.dynamic_potential[tmp- 1])/2                    
                if(self.dynamic_potential[tmp + 1] != 9):
                    Vehicle.route_list[tmp][tmp + 1] = (self.dynamic_potential[tmp]+self.dynamic_potential[tmp+ 1])/2                    

        #本計算
        #print('vehicle_n', self.vehicle_n)
        #スタート位置の設定
        self.distance[self.y*map_side+self.x] = 0
        #print('スタート', self.y*map_side+self.x)
        #ゴールの設定
        goal = self.goal_y*map_side+self.goal_x
        #print('ゴール', goal)
        #無限ループ防止
        kill = 0
        #ゴールのノードが探索済みになるまで繰り返す
        while(Vehicle.unsearched_nodes.count(goal) != 0):
            kill = kill+1
            #未探索ノードの内distanceが最小のものを選択する
            posible_min_distance = math.inf
            target_min_index = -1
            for node_index in Vehicle.unsearched_nodes:
                if(posible_min_distance > Vehicle.distance[node_index]):
                    posible_min_distance = Vehicle.distance[node_index]
                    target_min_index = node_index
            #print('target_min_index', target_min_index)
            #print(target_min_index%map_side, int(target_min_index/map_side))
            #選択したノードを未探索ノードから除く
            if(target_min_index != -1):
                Vehicle.unsearched_nodes.remove(target_min_index)
            #コストの更新
            target_edge = Vehicle.route_list[target_min_index]
            for index, route_dis in enumerate(target_edge):
                if(route_dis != 0):
                    if((index in Vehicle.unsearched_nodes) == True):
                        if(Vehicle.distance[index] > (Vehicle.distance[target_min_index]+route_dis)):
                            #print('距離', Vehicle.distance[index], Vehicle.distance[target_min_index]+route_dis)
                            Vehicle.distance[index] = Vehicle.distance[target_min_index]+route_dis
                            self.previous_nodes[index] = target_min_index
                            #print('index', index, 'self.previous_nodes[index]', self.previous_nodes[index])
                       
            if(kill == map_side*map_length + 100):
                print('ダイクストラプログラムの異常終了')
                sys.exit()
                break                
        
        #探索したノードをスタックに入れる
        tmp = goal
        kill = 0
        #print('queue', end=" ")
        self.q.put(tmp)
        #print(tmp, end=" ")
        #print(tmp)
        while(self.previous_nodes[tmp] != -1):
            self.q.put(self.previous_nodes[tmp])
            #print(self.previous_nodes[tmp], end=" ")
            tmp = self.previous_nodes[tmp]
            kill = kill +1
            if(kill == map_side*map_length + 100):
                print('スタック異常終了')
                break
        self.q_control = 0
        #print(" ")
    
    #動的なポテンシャル場からセルを1つ選択する
    def select_cell(self):
        #print(self.rank)
        #ダイクストラ法の場合
        if(self.rank == 0):
            if(self.q_control == 0):
                tmp = self.q.get(False, None)
                self.next_x = tmp%map_side
                self.next_y = int(tmp/map_side)
                #print('select_cell', tmp, self.next_x, self.next_y, self.goal_x, self.goal_y)
                if((self.next_x == self.goal_x) and (self.next_y == self.goal_y)):
                    #print('f_dijkstra')
                    self.f_dijkstra = 0
                else:
                    tmp = self.q.get(False, None)
                    self.next_next_x = tmp%map_side
                    self.next_next_y = int(tmp/map_side)
                self.q_control = 1
            elif(self.q_control == 1):
                self.next_x = self.next_next_x
                self.next_y = self.next_next_y
                if((self.next_x == self.goal_x) and (self.next_y == self.goal_y)):
                    #print('f_dijkstra')
                    self.f_dijkstra = 0
                else:
                    tmp = self.q.get(False, None)
                    self.next_next_x = tmp%map_side
                    self.next_next_y = int(tmp/map_side)
                
            
        else:
            tmp = 8
            
            j = [self.x, self.x-1, self.x+1, self.x, self.x]
            i = [self.y-1, self.y, self.y, self.y+1, self.y]
            for i, j in zip(i, j):
                if(self.dynamic_potential[i*map_side+j] < tmp):
                    tmp = self.dynamic_potential[i*map_side+j]
                    self.next_x = j
                    self.next_y = i
                    
            j = [self.next_x, self.next_x-1, self.next_x+1, self.next_x, self.next_x]
            i = [self.next_y-1, self.next_y, self.next_y, self.next_y+1, self.next_y]
            for i, j in zip(i, j):
                if(self.dynamic_potential[i*map_side+j] < tmp):
                    tmp = self.dynamic_potential[i*map_side+j]
                    self.next_next_x = j
                    self.next_next_y = i
            '''
            for i in range(self.y-1, self.y+2):
                for j in range(self.x-1, self.x+2):
                    if(self.dynamic_potential[i*map_side+j] < tmp):
                        tmp = self.dynamic_potential[i*map_side+j]
                        self.next_x = j
                        self.next_y = i
            '''

            #print(self.goal_x, self.goal_y, self.dynamic_potential[self.goal_y*map_side+self.goal_x])
            #停留している場合は時限ポテンシャルを定義する座標を決定
            if((self.next_x == self.x) and (self.next_y == self.y)):
                tmp_x = self.goal_x - self.x
                tmp_y = self.goal_y - self.y
                if((tmp_x <= 0) and (tmp_y <= 0)):
                    self.limit_x2 = self.x +1
                    self.limit_y2 = self.y +1
                elif((tmp_x > 0) and (tmp_y <= 0)):
                    self.limit_x2 = self.x -1
                    self.limit_y2 = self.y +1    
                elif((tmp_x <= 0) and (tmp_y > 0)):
                    self.limit_x2 = self.x +1
                    self.limit_y2 = self.y -1
                elif((tmp_x > 0) and (tmp_y > 0)):
                    self.limit_x2 = self.x -1
                    self.limit_y2 = self.y -1    

                if((self.limit_x == self.limit_x2) and (self.limit_y == self.limit_y2)):
                    self.double_limit = 1
                    self.limit_x2 = self.x
                    self.limit_y2 = self.y
                    #print('ダブルポテンシャル', self.limit_x, self.limit_y, self.limit_x2, self.limit_y2)
                else:
                    self.limit_x = self.limit_x2
                    self.limit_y = self.limit_y2
                    self.limit_x2 = -1
                    self.limit_y2 = -1            
    
    def search_direction(self):
        if(self.y == self.next_y-1):
            self.direction = 0
        elif(self.x == self.next_x-1):
            self.direction = 1
        elif(self.y == self.next_y+1):
            self.direction = 2
        elif(self.x == self.next_x+1):
            self.direction = 3
        elif((self.x == self.next_x) and (self.y == self.next_y)):
            self.direction = 4
        if(self.next_y == self.next_next_y-1):
            self.next_direction = 0
        elif(self.next_x == self.next_next_x-1):
            self.next_direction = 1
        elif(self.next_y == self.next_next_y+1):
            self.next_direction = 2
        elif(self.next_x == self.next_next_x+1):
            self.next_direction = 3
        elif((self.next_x == self.next_next_x) and (self.next_y == self.next_next_y)):
            self.next_direction = 4
        '''
        if(self.y == self.next_y-1 == self.next_next_y-2):
            self.direction = 0
        elif(self.x == self.next_x-1 == self.next_next_x-2):
            self.direction = 1
        elif(self.y == self.next_y+1 == self.next_next_y+2):
            self.direction = 2
        elif(self.x == self.next_x+1 == self.next_next_x+2):
            self.direction = 3
        if(self.next_y == self.next_next_y-1):
            self.next_direction = 0
        elif(self.next_x == self.next_next_x-1):
            self.next_direction = 1
        elif(self.next_y == self.next_next_y+1):
            self.next_direction = 2
        elif(self.next_x == self.next_next_x+1):
            self.next_direction = 3
        '''

    #選んだ座標を現在の座標とする
    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
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
            
#搬送車のランクのクラス
class Rank:
    def __init__(self, vehicle_sum):
        self.vehicle_sum = vehicle_sum
        self.v_rank = []
        for count in range(vehicle_sum):
            self.v_rank.append(count)
        self.last_move = -1
        self.last_ready = -1
            
    def change_rank(self, before_state, state, vehicle_n):
        next_point = -1
        for count in range(self.vehicle_sum):
            if(self.v_rank[count] == vehicle_n):
                point = count
                break
            
        if((before_state == 'stop') and (state == 'move')):
            self.last_move = self.last_move+1
            self.last_ready = self.last_ready+1
            next_point = self.last_move
        elif((before_state == 'move') and (state == 'move')):
            next_point = self.last_move
        elif((before_state == 'move') and (state == 'ready_move')):
            next_point = self.last_ready
            self.last_move = self.last_move-1
            self.last_ready = self.last_ready
        elif((before_state == 'ready_move') and (state == 'stop')):
            next_point = self.last_ready
            self.last_ready = self.last_ready-1
        elif((before_state == 'ready_move') and (state == 'move')):
            next_point = self.last_move+1
            self.last_move = self.last_move+1
            self.last_ready = self.last_ready
        
        if(point > next_point):
            tmp = self.v_rank[next_point]
            for count in range(next_point+1, self.vehicle_sum):
                tmp2 = self.v_rank[count]
                self.v_rank[count] = tmp
                tmp = tmp2
                if(count == point):
                    break
            self.v_rank[next_point] = tmp
        elif(point < next_point):
            tmp = self.v_rank[point]
            for count in range(point+1, next_point+1):
                self.v_rank[count-1] = self.v_rank[count]
            self.v_rank[next_point] = tmp
            
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
    
    def __init__(self, occured_time, start, goal, carrier_n, arrival_time):
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
        return -1/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 2):
        return 1/math.sqrt((x1-x2)**2 + (y1-y2)**2)
    elif(type == 3):
        return 1.1/(math.sqrt((x1-x2)**2 + (y1-y2)**2))**2
    
#割り当てる搬送車を見つける関数
def matching(start):
    minimize = 10000
    for count in range(vehicle_sum):
        if((vehicle[count].state == 'stop') or (vehicle[count].state == 'ready_move')):
            #print('割り当て可能な搬送車が見つかりました')
            tmp = distance(vehicle[count].x, vehicle[count].y, point[start].out_x, point[start].out_y)
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
        print('割り当てた搬送車')
        print(minimize, min_vehicle)
        '''
        return min_vehicle
    
def get_match(min_vehicle, tmp):
    vehicle[min_vehicle].goal = carrier[tmp].start
    vehicle[min_vehicle].goal_x = point[carrier[tmp].start].out_x
    vehicle[min_vehicle].goal_y = point[carrier[tmp].start].out_y
    vehicle[min_vehicle].carrier = carrier[tmp].carrier_n
    
#2点間の座標の距離を返す関数
def distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


if __name__ == "__main__":
    
    mapping = []               #マップ情報をリスト型で保持
    request = []               #搬送要求をリスト型で保持
    request_n  = -1            #搬送要求数をカウント
    vehicle = []               #搬送車を格納
    vehicle_n = -1             #搬送車識別番号をカウント
    vehicle_sum = 3            #搬送車の総数
    vehicle_work = 0           #仕事中の搬送車
    kumitate_sum = 2           #組み立て場所の総数
    point = []                 #搬送地点をリスト型で保持
    carrier = []               #搬送物をリスト型で保持
    go_carrier = 0             #割り当てを行う搬送物の管理を行う関数
    sum_carrier = -1           #搬送物の合計個数
    count = 0 
    q = deque([])              #キューの箱
    map_length = 44            #マップの縦幅
    map_side = 27              #マップの横幅
    path = 'vehicle_visual.txt'
    path2 = 'collision.txt'
    last = 100
        
    #マップの作成
    f = open('map_test3.txt')
    data1 = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()
    
    i=0
    j=0
    for line in data1:
        if(line == '#'):
            obj = Cell(i, j, 'wall')
            mapping.append(obj)
        elif(line == '-'):
            obj = Cell(i, j, 'road')
            mapping.append(obj)
        elif(line == '+'):
            obj = Cell(i, j, 'no_entry')
            mapping.append(obj)
        elif(line == '*'):
            obj = Cell(i, j, 'accept')
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
        print(count, mapping[count].x, mapping[count].y, mapping[count].celltype)
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
    for count in range(2):
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
    for count in range(2):
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
    
    #ランククラスの生成
    rank = Rank(vehicle_sum)
    
    
    #搬送車経路を示すファイル
    f = open(path, 'w')
    f2 = open(path2, 'w')
    
    #時間を表す
    for time in range(5000):
    
        f.write(str(time)+' ')
        #割当未完了の搬送物が存在する場合
        if(len(q) > 0):
            tmp = q.popleft()
            #割当てる搬送車を決定
            min_vehicle = matching(carrier[tmp].start)
            if(min_vehicle == -1):
                q.append(tmp)
            else:
                #搬送車への割当処理
                get_match(min_vehicle, tmp)
                
                if(vehicle[min_vehicle].rank == 0):
                    vehicle[min_vehicle].f_dijkstra = 0
                    
                tmp = vehicle[min_vehicle].state
                vehicle[min_vehicle].state = 'move'
                rank.change_rank(tmp, 'move', min_vehicle)
                for count2 in range(vehicle_sum):
                    vehicle[rank.v_rank[count2]].rank = count2
                    if((vehicle[rank.v_rank[count2]].rank != 0) and (vehicle[rank.v_rank[count2]].f_dijkstra == 1)):
                        vehicle[rank.v_rank[count2]].f_dijkstra = 0
                vehicle[min_vehicle].change_s_potential()
                '''
                print("搬送物が割り当てられました")
                print('vehicle_n', vehicle[min_vehicle].vehicle_n)
                '''

        #搬送要求の発生時刻処理
        '''
        print('')
        print('time', time, end=" ")
        '''
        #搬送要求の発生時刻
        if(time == carrier[go_carrier].occured_time):
            #割当てる搬送車を決定
            min_vehicle = matching(carrier[go_carrier].start)
            #割り当てる搬送車が見つからなかった場合
            if(min_vehicle == -1):
                q.append(go_carrier)
            else:
                #搬送車への割当処理
                get_match(min_vehicle, go_carrier)
                
                if(vehicle[min_vehicle].rank == 0):
                    vehicle[min_vehicle].f_dijkstra = 0
                    
                tmp = vehicle[min_vehicle].state
                vehicle[min_vehicle].state = 'move'
                rank.change_rank(tmp, 'move', min_vehicle)
                for count2 in range(vehicle_sum):
                    vehicle[rank.v_rank[count2]].rank = count2
                    if((vehicle[rank.v_rank[count2]].rank != 0) and (vehicle[rank.v_rank[count2]].f_dijkstra == 1)):
                        vehicle[rank.v_rank[count2]].f_dijkstra = 0
                vehicle[min_vehicle].change_s_potential()
                '''
                print("搬送物が割り当てられました")
                print('vehicle_n', vehicle[min_vehicle].vehicle_n)
                '''
                #移動予定場所と組み立て場所のポテンシャル場の表示
                '''
                for count in range(648):
                    print(count, vehicle[min_vehicle].static2_potential[count], mapping[count].celltype)
                '''
            go_carrier = go_carrier+1
        
        for count in range(vehicle_sum):
            if(vehicle[count].state == 'ready_move'):
                
                #vehicle[count].driving_time = vehicle[count].driving_time +1
                vehicle[count].change_point()
                vehicle[count].change_d_potential()
                vehicle[count].select_cell()
                vehicle[count].search_direction()
                
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
                vehicle[count].search_direction()
                
                #移動予定のセルの表示
                '''
                print(vehicle[count].next_x, vehicle[count].next_y)
                '''
        
        for count in range(vehicle_sum):
            if(vehicle[count].state == 'ready_move'):
                vehicle[count].move()
                
                if((vehicle[count].x == vehicle[count].goal_x) and (vehicle[count].y == vehicle[count].goal_y)):
                    
                    '''
                    print('time', time)
                    print('搬送車待機場所に到着しました')
                    print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    '''
                    vehicle[count].goal_x = -1
                    vehicle[count].goal_y = -1
                    vehicle[count].state = 'stop'
                    rank.change_rank('ready_move', 'stop', count)
                    
                #移動した現在地を表示
                #print(count, '(', vehicle[count].x, vehicle[count].y, ')', end=" ")
                
            elif(vehicle[count].state == 'move'):
                vehicle[count].move()
               
                #移動した現在地を表示
                #print(count, '(', vehicle[count].x, vehicle[count].y, ')', end=" ")
                
                if((vehicle[count].x == vehicle[count].goal_x) and (vehicle[count].y == vehicle[count].goal_y)):   
                    '''
                    print('time', time)
                    print('搬送物受け取り地点に到達しました')
                    print('搬送車識別番号', '現在地', count, vehicle[count].x, vehicle[count].y)
                    '''
                    
                    #搬送物の到着時間を記録
                    carrier[vehicle[count].carrier].arrival(vehicle[count].have_carrier, time)
                       
                        
                    vehicle[count].change_goal()
                    
                    tmp = vehicle[count].state
                    
                    rank.change_rank('move', tmp, count)
                    
                    #f.write(str(time)+' ')
                    #f.write(str(vehicle_sum+count)+' '+str(vehicle[count].goal_x)+' '+str(vehicle[count].goal_y)+'\n')
                    #print('搬送物受け渡し地点', vehicle[count].goal_x, vehicle[count].goal_y)
                    
                    vehicle[count].change_s_potential()
                    
                    last = time
                 
            f.write(str(count)+' '+str(vehicle[count].x)+' '+str(vehicle[count].y)+' ')
        
        #搬送車の優先度を変更
        for count2 in range(vehicle_sum):
            vehicle[rank.v_rank[count2]].rank = count2
            if((vehicle[rank.v_rank[count2]].rank != 0) and (vehicle[rank.v_rank[count2]].f_dijkstra == 1)):
                vehicle[rank.v_rank[count2]].f_dijkstra = 0

        
        for count in range(vehicle_sum):
            f.write(str(count+vehicle_sum)+' '+str(vehicle[count].goal_x)+' '+str(vehicle[count].goal_y)+' ')
            
        for count in range(vehicle_sum):
            f.write(str(vehicle[count].rank)+' ')
            
        f.write('\n')
        
        #衝突していないか確認            
        for count in range(vehicle_sum):
            for count2 in range(count+1, vehicle_sum):
                if((vehicle[count].x == vehicle[count2].x) and (vehicle[count].y == vehicle[count2].y)):
                    if((vehicle[count].state != 'stop') and (vehicle[count2].state != 'stop')):
                        #print('time', time)                    
                        print('衝突しました')
                        #print('搬送車番号', count, count2)
                        #print('衝突座標', vehicle[count].x, vehicle[count].y)
                        f2.write(str(time)+' '+str(vehicle[count].prev_x)+' '+str(vehicle[count].prev_y)+' '+str(vehicle[count2].prev_x)+' '+str(vehicle[count2].prev_y)+' ')
                        for num in [count, count2]:
                            for i in  range(vehicle[num].prev_y-1,vehicle[num].prev_y+2):
                                for j in range(vehicle[num].prev_x-1,vehicle[num].prev_x+2):
                                    f2.write(str(round(vehicle[num].static2_potential[i*map_side+j], 4))+' ')
                                 
                            for i in  range(vehicle[num].prev_y-1,vehicle[num].prev_y+2):
                                for j in range(vehicle[num].prev_x-1,vehicle[num].prev_x+2):
                                    f2.write(str(round(vehicle[num].dynamic_potential[i*map_side+j], 4))+' ')
                            
                        f2.write('\n')
                        #sys.exit()
                        
                        
    #結果の出力
    sum_driving_time = 0
    for count in range(vehicle_sum):
        sum_driving_time = vehicle[count].driving_time + sum_driving_time
        if((vehicle[count].state == 'move') or(vehicle[count].state == 'ready_move')):
            print('搬送車が移動中に終了しました')
    
    #搬送物の発生から到着に要した時間
    sum_ok = 0
    for count in range(sum_carrier):
        carrier[count].time_required()
        sum_ok = sum_ok + carrier[count].ok
        #print(count, carrier[count].occured_time, carrier[count].arrival_time)
    print(sum_ok)
    
    #print('終了時刻', last)    
    print('走行時間の総和')
    print(sum_driving_time)
    print('最終走行完了時間')
    print(last-carrier[0].occured_time)
    
    f.close()
    f2.close()