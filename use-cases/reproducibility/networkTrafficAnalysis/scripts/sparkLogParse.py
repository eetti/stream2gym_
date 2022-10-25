#!/usr/bin/python3
# command to run this script: sudo python3 sparkLogParse.py <logDir>

import re
import sys

logDir = sys.argv[1]

with open(logDir, 'r') as fp:
        lines = fp.readlines()
        searchWord = '\'durationMs\': '
        #'\'durationMs\': '
        for row in lines:
            if searchWord in row:
                # print(row)
                # print("\n")
                durationString = row.split(searchWord)[1].split('}')[0]
                
                if 'queryPlanning' in durationString:
                    print(durationString)
                    addBatchTime = int(durationString.split('\'addBatch\': ')[1].split(',')[0])
                    getBatchTime = int(durationString.split('\'getBatch\': ')[1].split(',')[0])
                    latestOffsetTime = int(durationString.split('\'latestOffset\': ')[1].split(',')[0])
                    queryPlanningTime = int(durationString.split('\'queryPlanning\': ')[1].split(',')[0])
                    triggerExecutionTime = int(durationString.split('\'triggerExecution\': ')[1].split(',')[0])
                    walCommitTime = int(durationString.split('\'walCommit\': ')[1].split(',')[0])

                    totalTime = addBatchTime+getBatchTime+latestOffsetTime+queryPlanningTime+triggerExecutionTime+walCommitTime
                    print(str(totalTime)+'ms')