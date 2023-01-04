# command to run this script: sudo python3 use-cases/app-testing/millitary-coordination/scripts/cpuMemUsagePlot.py
#!/bin/usr/python3
import matplotlib.pyplot as plt

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf()

# plot the median cpu usage 
def medianCPUPlot():
    medianCPUUsage1 = [2.2, 4.2, 5.8, 6.5, 9.1]
    medianCPUUsage2 = [2.2, 4.4, 5.8, 8.350000000000001, 9.4] 
    medianCPUUsage3 = [2.3, 4.4, 5.85, 7.9, 9.6] 

    # average median from 3 round of experiments
    avgMedianCPUUsage = [(i+j+k) / 3 for i, j, k in zip(medianCPUUsage1,medianCPUUsage2,medianCPUUsage3)]
    print(avgMedianCPUUsage)

    hostList = [2,4,6,8,10]

    # plot and save median CPU usage with respect to hosts
    plt.plot(hostList,avgMedianCPUUsage,color='blue')
    plt.xlabel('Number of hosts', fontsize=16)
    plt.ylabel('Median CPU usage(%)', fontsize=16)
    plt.savefig("medianCPUUsage.png",format='png', bbox_inches="tight")

# medianCPUPlot()

# clearing the existing plot
clearExistingPlot()

# plot average peak memory usage for 16MiB & 32MiB buffer memory
hostList = ['2','4','6','8','10']
# peak memory usage results from 3 rounds of experiments (for 16MiB buffer memory)
peakMemUsage1 = [31.44, 37.61, 44.4, 50.88, 55.95] 
peakMemUsage2 = [31.63, 37.68, 44.8, 50.88, 56.18] 
peakMemUsage3 = [31.46, 37.81, 44.8, 50.88, 56.59]

avgPeakMemUsage1 = [(i+j+k) / 3 for i, j, k in zip(peakMemUsage1,peakMemUsage2, peakMemUsage3)]
# print(avgPeakMemUsage1)
plt.plot(hostList,avgPeakMemUsage1,color='red', label='16MiB')


# peak memory usage results from 3 rounds of experiments (for default 32MiB buffer memory)
peakMemUsage4 = [49.97, 53.74, 59.92, 66.26, 73.61]
peakMemUsage5 = [47.64, 53.93, 60.82, 65.05, 72.58]
peakMemUsage6 = [47.88, 54.24, 60.05, 65.09, 72.32]

avgPeakMemUsage2 = [(i+j+k) / 3 for i, j, k in zip(peakMemUsage4,peakMemUsage5, peakMemUsage6)]
# print(avgPeakMemUsage2)
plt.plot(hostList,avgPeakMemUsage2,color='blue', label='32MiB')

plt.xlabel('Number of hosts', fontsize=16)
plt.ylabel('Peak Memory usage(%)', fontsize=16)
plt.legend(title='Buffer Memory')
plt.savefig("use-cases/app-testing/millitary-coordination/logs/cpu-mem/MemoryUsage.png",format='png', bbox_inches="tight")