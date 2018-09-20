# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from datetime import datetime
from datetime import timedelta

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# CloudWatch doesn't like blank NextTokens, so if it's '' or None, 
# don't try adding the parameter
def getmetricdata(**kwargs):
    if kwargs.get('NextToken') is None or kwargs.get('NextToken') == '':
        return cloudwatch.get_metric_data(MetricDataQueries = 
            kwargs.get("MetricDataQueries"),
            StartTime=kwargs.get("StartTime"),
            EndTime=kwargs.get("EndTime"),
            MaxDatapoints=5000
            )
    else:
        return cloudwatch.get_metric_data(MetricDataQueries = 
            kwargs.get("MetricDataQueries"),
            StartTime=kwargs.get("StartTime"),
            EndTime=kwargs.get("EndTime"),
            NextToken=kwargs.get("NextToken"),
            MaxDatapoints=5000
            )
        
# comb through concurrency to get peak concurrency time window for last week
# maxval by default is zero
maxval = 0
# set next_token to blank to handle paging
next_token = ''
# set start time to seven days ago and end time to now
starttime = datetime.utcnow() - timedelta(days=14)
endtime = datetime.utcnow()


# grab Concurrent Executions metric from CloudWatch for Lambda, paging if necessary
while next_token is not None:
    peakresponse = getmetricdata(MetricDataQueries=[
        {
            'Id': 'concurrent',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/Lambda',
                    'MetricName': 'ConcurrentExecutions',
                },
                'Period': 60,
                'Stat': 'Maximum',
                'Unit': 'Count'
            },
            'Label': 'Concurrent',
            'ReturnData': True
        }
    ],
        StartTime=starttime,
        EndTime=endtime,
        NextToken=next_token
        )

    # comb through results to get the highest value. There's fancier ways to do this, but this is pretty quick and readable
    for result in peakresponse['MetricDataResults']:
        for i in range(len(result['Timestamps'])):
            if result['Values'][i] > maxval:
                maxval=result['Values'][i]
                timestamp=result['Timestamps'][i]
        if result['StatusCode']=='PartialData':
            next_token=peakresponse['NextToken']
        else:
            next_token=None


# print out results
print('Peak Concurrency of '+str(maxval)+' reported at '+str(timestamp) +' UTC')
print('Pulling Metrics from '+str(timestamp) + ' UTC')
print()
print('{:<80} | {:<25} | {:<11} | {:<14} | {:<17}'.format(
    'Function Name','Timestamp','Invocations','Duration (sec)','Concurrency (est)')
    )
print('-'*159)

# now that we have the peak concurrency time, 
# grab metrics for all functions around that time
# first, create Lambda client and paginator to get the functions
awslambda = boto3.client('lambda')
lpaginator = awslambda.get_paginator('list_functions')
literator = lpaginator.paginate()

# select time range, which is 6 minutes before and 2 minutes 
# after the peak concurrency
starttime = timestamp - timedelta(minutes=6)
endtime = timestamp + timedelta(minutes=2)

# List metrics through the pagination interface
for functionlist in literator:
    # for each funcion name in the list of functions, get the metric data
    if 'Functions' in functionlist:
        for func_name in functionlist['Functions']:
            next_token=''
            # if more results, paginate (unlikely as only 5 are expected)
            while next_token is not None:
                response = getmetricdata(
                    MetricDataQueries=[
                        {
                            'Id': 'invocations',
                            'MetricStat': {
                                'Metric': {
                                    'Namespace': 'AWS/Lambda',
                                    'MetricName': 'Invocations',
                                    'Dimensions': [
                                        {
                                            'Name': 'FunctionName',
                                            'Value': func_name['FunctionName']
                                        },
                                    ]
                                },
                                'Period': 60,
                                'Stat': 'Sum',
                                'Unit': 'Count'
                            },
                            'Label': 'Invocations',
                            'ReturnData': True
                        },
                        {
                            'Id': 'duration',
                            'MetricStat': {
                                'Metric': {
                                    'Namespace': 'AWS/Lambda',
                                    'MetricName': 'Duration',
                                    'Dimensions': [
                                        {
                                            'Name': 'FunctionName',
                                            'Value': func_name['FunctionName']
                                        },
                                    ]
                                },
                                'Period': 60,
                                'Stat': 'Average',
                                'Unit': 'Milliseconds'
                            },
                            'Label': 'Duration',
                            'ReturnData': True
                        },
                    ],
                    StartTime=starttime,
                    EndTime=endtime,
                    ScanBy='TimestampDescending',
                    nextToken=next_token
                )

                if len(response['MetricDataResults'][0]['Timestamps']) > 0:
                        for i in range(len(response['MetricDataResults'][0]['Timestamps'])):
                            # print out the results to the screen. If you want it to go to a file, just pipe the output to a file ( > output.txt)
                            print('{:<80} | {:<25} | {:>11.3f} | {:>14.2f} | {:>17.1f}'.format(
                               func_name['FunctionName'],
                               str(response['MetricDataResults'][0]['Timestamps'][i]), 
                               response['MetricDataResults'][0]['Values'][i],
                               response['MetricDataResults'][1]['Values'][i]/1000,
                               round(response['MetricDataResults'][0]['Values'][i]/60 *response['MetricDataResults'][1]['Values'][i]/1000)
                               )
                            )

                        if response['MetricDataResults'][0]['StatusCode']=='PartialData':
                            next_token=response['NextToken']
                        else:
                            next_token=None
                else:
                    # Lambda doesn't output metrics if there aren't any to report, so note that
                    print('{:<80} | {:<25} | {:<11} | {:<14} | {:<17}'.format(func_name['FunctionName'],'No Data','','',''))
                    next_token=None


