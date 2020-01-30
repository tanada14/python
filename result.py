import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
fp = FontProperties(fname=r'C:\WINDOWS\Fonts\YuGothic.ttf', size=10)
path = 'result3.txt'
Sum = 10 #試行回数
division = 10
ExTotal = [[0 for i in range(Sum)] for j in range(division)]
ExFinal = [[0 for i in range(Sum)] for j in range(division)]
ExCollision = [[0 for i in range(Sum)] for j in range(division)]
PrTotal = [[0 for i in range(Sum)] for j in range(division)]
PrFinal = [[0 for i in range(Sum)] for j in range(division)]
PrCollision = [[0 for i in range(Sum)] for j in range(division)]
time = -1
time2 = 0
total = 0
final = 0
ExorPr = 0 #exsistingmethod だと０　proposedmethod　だと　１
f = open(path,'r',encoding="utf-8_sig")
for line in f:
    if(line == 'carrier_sum 100\n'):
        time = time +1
        #print('time', time)
    elif(line == '衝突しました\n'):
        if(ExorPr == 0):
            ExCollision[time2][time] = ExCollision[time2][time] +1
            #print('ExCollision', ExCollision[time2][time])
        elif(ExorPr == 1):
            PrCollision[time2][time] = PrCollision[time2][time] +1
            #print('PrCollision', PrCollision[time2][time])
    elif(line == '走行時間の総和\n'):
        total = 1
        #print('total')
    elif(total == 1):
        if(ExorPr == 0):
            ExTotal[time2][time] = int(line)
            #print('ExTotal', ExTotal[time2][time])
            total = 0
        elif(ExorPr == 1):
            PrTotal[time2][time] = int(line)
            #print('PrTotal', PrTotal[time2][time])
            total = 0
    elif(line == '最終走行完了時間\n'):
        final = 1
        #print('final')
    elif(final == 1):
        if(ExorPr == 0):
            ExFinal[time2][time] = int(line)
            #print('ExFinal', ExFinal[time2][time])
            final = 0
            ExorPr = 1
        elif(ExorPr == 1):
            PrFinal[time2][time] = int(line)
            #print('PrFinal', PrFinal[time2][time])
            final = 0
            ExorPr = 0
            if(time == Sum-1):
                #print(time2)
                time = -1
                time2 = time2 + 1
                
f.close()

print('既存手法')
print(ExTotal[time2-1])
print(ExFinal[time2-1])
print(ExCollision[time2-1])
print('提案手法')
print(PrTotal[time2-1])
print(PrFinal[time2-1])
print(PrCollision[time2-1])
#--------------------------------------------------------------------------
#それぞれの平均をとる
AvExTotal = [0]*division
AvExFinal = [0]*division
AvExCollision = [0]*division
AvPrTotal = [0]*division
AvPrFinal = [0]*division
AvPrCollision = [0]*division

for time2 in range(division):
    AvExTotal[time2] = sum(ExTotal[time2])/len(ExTotal[time2])
    AvExFinal[time2] = sum(ExFinal[time2])/len(ExFinal[time2])
    AvExCollision[time2] = sum(ExCollision[time2])/len(ExCollision[time2])
    AvPrTotal[time2] = sum(PrTotal[time2])/len(PrTotal[time2])
    AvPrFinal[time2] = sum(PrFinal[time2])/len(PrFinal[time2])
    AvPrCollision[time2] = sum(PrCollision[time2])/len(PrCollision[time2])
    
#----------------------------------------------------------------------------
#グラフに描画する
#総走行時間
plt.title("総走行時間による比較", fontname="MS Gothic")
plt.xlabel("搬送物数", fontname="MS Gothic")
plt.ylabel("総走行時間", fontname="MS Gothic")
plt.grid(True)

plt.xlim(0, Sum*division+10)     
plt.ylim(0, round(max(AvExTotal)+10, -1))      

plt.xticks(np.arange(0, Sum*division+1, 10))
plt.yticks(np.arange(0, round(max(AvExTotal)+1000, -1)+1, 1000))

#plt.axes().set_aspect('equal')

left = np.array(list(range(10, Sum*division+10, 10)))
height1 = np.array(AvExTotal)
height2 = np.array(AvPrTotal)
p1 = plt.plot(left, height1, marker="o", color="red")
p2 = plt.plot(left, height2, marker="o", color="blue")
plt.legend((p1[0], p2[0]), ("既存手法", "提案手法"), loc=2, prop=fp)
plt.show()
#最終走行完了時刻
plt.title("最終走行完了時刻による比較", fontname="MS Gothic")
plt.xlabel("搬送物数", fontname="MS Gothic")
plt.ylabel("最終走行完了時刻", fontname="MS Gothic")
plt.grid(True)

plt.xlim(0, Sum*division+10)     
plt.ylim(0, round(max(AvExFinal)+10, -1))      

plt.xticks(np.arange(0, Sum*division+1, 10))
plt.yticks(np.arange(0, round(max(AvExFinal)+1000, -1)+1, 1000))

#plt.axes().set_aspect('equal')

left = np.array(list(range(10, Sum*division+10, 10)))
height1 = np.array(AvExFinal)
height2 = np.array(AvPrFinal)
p1 = plt.plot(left, height1, marker="o", color="red")
p2 = plt.plot(left, height2, marker="o", color="blue")
plt.legend((p1[0], p2[0]), ("既存手法", "提案手法"), loc=2, prop=fp)
plt.show()
#衝突回数
plt.title("衝突回数による比較", fontname="MS Gothic")
plt.xlabel("搬送物数", fontname="MS Gothic")
plt.ylabel("衝突回数", fontname="MS Gothic")
plt.grid(True)

plt.xlim(0, Sum*division+10)     
plt.ylim(0, round(max(AvExCollision)+1, -1))      

plt.xticks(np.arange(0, Sum*division+1, 10))
plt.yticks(np.arange(0, round(max(AvExCollision)+3, -1)+1, 1))

#plt.axes().set_aspect('equal')

left = np.array(list(range(10, Sum*division+10, 10)))
height1 = np.array(AvExCollision)
height2 = np.array(AvPrCollision)
p1 = plt.plot(left, height1, marker="o", color="red")
p2 = plt.plot(left, height2, marker="o", color="blue")
plt.legend((p1[0], p2[0]), ("既存手法", "提案手法"), loc=2, prop=fp)
plt.show()