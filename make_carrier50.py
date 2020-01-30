#搬送要求のファイルを出力する
import random
import numpy.random as rd

kumitate_sum = 2              #組み立て場所の総数
last_time = 200               #搬送物が発生する最終時刻
path_w = 'carrier_test4.txt'  #保存するファイル
carrier_sum = 50             #搬送物の総数

print('carrier_sum', 100)


with open(path_w, mode='w') as f:
    sum_time = 0
    for count in range(carrier_sum):
        lam = 0.04   
        x = rd.exponential(1./lam)
        time = int(x)
        while(time == 0):
            x = rd.exponential(1./lam)
            time = int(x)
        #time = random.randrange(tmp+1, last_time-carrier_sum+count)
        sum_time = time + sum_time
        #print(time, end=" ")
        f.write(str(sum_time))
        f.write(' ')
        
        start = random.randrange(kumitate_sum)
        #print(start, end=" ")
        f.write(str(start))
        f.write(' ')
        
        goal = random.randrange(kumitate_sum)
        while(start == goal):
            goal = random.randrange(kumitate_sum)
        #print(goal, end=" ")
        f.write(str(goal))
        f.write(' ')
        f.write('\n')
        #print('')
    
    f.write(str(-1))
    f.write(' ')
    f.write(str(-1))
    f.write(' ')
    f.write(str(-1))
    f.write(' ')
    f.write('\n')