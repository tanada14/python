import numpy as np
import matplotlib.pyplot as plt
# 折れ線グラフを出力

ExCollision = [100]*10


plt.title("This is a title")
plt.xlabel("x axis")
plt.ylabel("y axis")
plt.grid(True)

plt.xlim(0, 100)     
plt.ylim(0)      

plt.xticks(np.arange(0, 100+1, 10))
plt.yticks(np.arange(0, 200+1, 10))

#plt.axes().set_aspect('equal')

left = np.array(list(range(10, 100+10, 10)))
height = np.array(ExCollision)
p1 = plt.plot(left, height, marker="o", color="red")
p2 = plt.plot(left, height/2, marker="o", color="blue")
plt.legend((p1[0], p2[0]), ("Class 1", "Class 2"), loc=2)
plt.show()