#!/bin/usr/python3

import matplotlib.pyplot as plt

fig = plt.figure()

# nConcurrentUsers = [20, 40, 60,80,100]
# avgExecTimeRound1 = [4740, 4112, 4636.0, 3868.0, 4996.0]
# avgExecTimeRound2 = [3374, 4084, 4859.0, 3146.923076923 , 5493]
# avgExecTimeRound3 = [6075, 3434, 4168, 4027.8 , 3326]

# plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dashed', label='Round1')
# plt.plot(nConcurrentUsers,avgExecTimeRound2,color='red',linestyle='dashed', label='Round2')
# plt.plot(nConcurrentUsers,avgExecTimeRound3,color='green',linestyle='dashed', label='Round3')

nConcurrentUsers = [20, 40, 60, 80, 100]
avgExecTimeRound1 = [1585.595, 2074.278, 2420.265, 2587.151, 2432.62]
plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dotted')


plt.xlabel('Concurrent users', fontsize=16)
plt.ylabel('Average execution time(ms)', fontsize=16)
plt.title('Distributed streaming processing execution time',fontsize=20)
plt.legend()
plt.show()

