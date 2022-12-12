#!/bin/usr/python3

import matplotlib.pyplot as plt

fig = plt.figure()

nConcurrentUsers = [20, 40, 60, 80, 100]
avgExecTimeRound1 = [1585.595, 2074.278, 2420.265, 2587.151, 2432.62]
plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dotted')


plt.xlabel('Concurrent users', fontsize=16)
plt.ylabel('Average execution time(ms)', fontsize=16)
plt.title('Distributed streaming processing execution time',fontsize=20)
plt.legend()
plt.show()

