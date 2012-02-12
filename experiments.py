'''
TODO: Percentage of top topics used. Choose top 5 query topics or 20, or 50

Created on Oct 20, 2011

@author: kykamath
'''
from models import MixedUsersModel, RankingModel, run, Analysis
from library.classes import GeneralMethods
#from library.plotting import smooth
from objects import User, Spammer
from settings import spamModelFolder
from library.file_io import FileIO
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from library.plotting import smooth

import matplotlib
import matplotlib.font_manager as fm
matplotlib.rc('xtick', labelsize=16)
matplotlib.rc('ytick', labelsize=16)
prop = fm.FontProperties(size=14)

labels = dict([(RankingModel.LATEST_MESSAGES, 'LMR'),
               (RankingModel.POPULAR_MESSAGES, 'PMR'),
               (RankingModel.LATEST_MESSAGES_DUPLICATES_REMOVED, 'LDMR'),
               (RankingModel.LATEST_MESSAGES_SPAM_FILTERED, 'LMR after Spam Filtering'),
               (RankingModel.POPULAR_MESSAGES_SPAM_FILTERED, 'PMR after Spam Filtering'),
               ])

def trendCurves():
    model = MixedUsersModel()
    experimentFileName = spamModelFolder+model.id
    conf = {'model': model, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.trendCurves, 1)], 'ratio': {'normal': 0.985, 'spammer': 0.015},
            'experimentFileName': experimentFileName}
    GeneralMethods.runCommand('rm -rf %s'%experimentFileName); run(**conf)
    Analysis.trendCurves(experimentFileName=experimentFileName)
    
def performanceAsPercentageOfSpammersVaries(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
        for spammerPercentage in range(1,21):
            spammerPercentage = spammerPercentage*0.05
#        for spammerPercentage in range(0,10):
#            spammerPercentage = spammerPercentage*0.005
            experimentFileName = spamModelFolder+'performanceAsPercentageOfSpammersVaries/%s/%0.3f'%(iteration,spammerPercentage)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesDuplicatesRemoved, RankingModel.popularMessages],
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerPercentage]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Percentage of Spammers', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Spammness with changing percentage of spammers')
        plt.legend(loc=2, prop=prop)
#        plt.show()
        plt.savefig('performanceAsPercentageOfSpammersVaries.png')
        plt.clf()
        
def performanceAsSpammerBudgetVaries(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
        for spammerBudget in range(0,11):
            spammerBudget = spammerBudget*0.1
            experimentFileName = spamModelFolder+'performanceAsSpammerBudgetVaries/%s/%0.3f'%(iteration,spammerBudget)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 0.985, 'spammer': 0.015},
                        'spammerMessagingProbability': spammerBudget,
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesDuplicatesRemoved, RankingModel.popularMessages],
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerBudget]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Spammer Messaging Probability', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Spammness with changing messaging probability')
        plt.legend(loc=2)
#        plt.show()
        plt.savefig('performanceAsSpammerBudgetVaries.png')
        plt.clf()
        
def performanceAsSpammerPayloadVaries(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
        for spammerPayload in range(1,11):
            experimentFileName = spamModelFolder+'performanceAsSpammerPayloadVaries/%s/%0.3f'%(iteration,spammerPayload)
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 0.985, 'spammer': 0.015},
                        'noOfPayloadsPerSpammer': spammerPayload,
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesDuplicatesRemoved, RankingModel.popularMessages],
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerPayload]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Spammer Payload', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Spammness with changing spammer payloads')
        plt.legend(prop=prop, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=3, fancybox=True, shadow=False)
#        plt.show()
        plt.savefig('performanceAsSpammerPayloadVaries.png')
        plt.clf()
        
def performanceAsNoOfGlobalPayloadsVary(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
        for noOfGlobalSpammerPayloads in range(1,500):
#        for noOfGlobalSpammerPayloads in range(10,11):
            Spammer.globalPayloads = None
            experimentFileName = spamModelFolder+'performanceAsNoOfGlobalPayloadsVary/%s/%0.3f'%(iteration,noOfGlobalSpammerPayloads)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 0.985, 'spammer': 0.015},
                        'noOfGlobalSpammerPayloads': noOfGlobalSpammerPayloads,
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesDuplicatesRemoved, RankingModel.popularMessages],
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][noOfGlobalSpammerPayloads]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: 
            dy = [np.mean(realDataY[ranking_id][x]) for x in dataX[:20]] + list(smooth([np.mean(realDataY[ranking_id][x]) for x in dataX[20:]])) #+smooth([np.mean(realDataY[ranking_id][x]) for x in dataX[20:]]
            plt.semilogx(dataX, dy[:len(dataX)], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
#        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])  
        plt.xlabel('No. of Global Payloads', fontsize=15, fontweight='bold')
        plt.ylabel('Spamness', fontsize=15, fontweight='bold')
#        plt.title('Spammness with changing global payloads')
        plt.legend(loc=4)
#        plt.show()
        plt.savefig('performanceAsNoOfGlobalPayloadsVary.png')
        plt.clf()
        
def performanceAsPercentageOfGlobalSpammerVaries(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
#        for spammerPercentage in range(1,21):
#            spammerPercentage = spammerPercentage*0.05
        for spammerPercentage in range(1,11):
            spammerPercentage = spammerPercentage*0.1
            experimentFileName = spamModelFolder+'performanceAsPercentageOfGlobalSpammerVaries/%s/%0.3f'%(iteration,spammerPercentage)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 
                        'ratio': {'normal': 0.985, 'spammer': 0.015},
                        'spamRatio': {'localPayloads': 1-spammerPercentage, 'globalPayloads': spammerPercentage},
                        'noOfGlobalSpammerPayloads': 10,
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesDuplicatesRemoved, RankingModel.popularMessages],
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerPercentage]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Percentage of Spammers Using Global Strategy', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Spammness when spammers use mixed strategy')
        plt.legend(loc=4)
#        plt.show()
        plt.savefig('performanceAsPercentageOfGlobalSpammerVaries.png')
        plt.clf()
        
def performanceWithSpamFilteringForPopularMessages(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(3):
        for spammerPercentage in range(1,21):
#            spammerPercentage = 20
            spammerPercentage = spammerPercentage*0.05
            experimentFileName = spamModelFolder+'performanceWithSpamFilteringForPopularMessages/%s/%0.3f'%(iteration,spammerPercentage)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
                        'rankingMethods':[RankingModel.popularMessages, RankingModel.popularMessagesSpamFiltered],
                        'experimentFileName': experimentFileName,
                        'noOfPayloadsPerSpammer': 1, 'noOfTopics': 10
                        }
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerPercentage]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in [RankingModel.POPULAR_MESSAGES, RankingModel.POPULAR_MESSAGES_SPAM_FILTERED]: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Percentage of Spammers', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Performance with spam filtering')
        plt.legend(loc=2)
#        plt.show()
        plt.savefig('performanceWithSpamFilteringForPopularMessages.png')
        plt.clf()
        
def performanceWithSpamFilteringForLatestMessages(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(3):
        for spammerPercentage in range(1,21):
#            spammerPercentage = 20
            spammerPercentage = spammerPercentage*0.05
            experimentFileName = spamModelFolder+'performanceWithSpamFilteringForLatestMessages/%s/%0.3f'%(iteration,spammerPercentage)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesSpamFiltered],
                        'experimentFileName': experimentFileName,
                        'noOfPayloadsPerSpammer': 1, 'noOfTopics': 10
                        }
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                tempData = defaultdict(list)
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        tempData[ranking_id]+=data['spammmess'][ranking_id]
                experimentData[iteration][spammerPercentage]=tempData
    if not generateData:
        realDataY = defaultdict(dict)
        for iteration in experimentData:
            dataY = defaultdict(list)
            dataX = []
            for perct in sorted(experimentData[iteration]):
                dataX.append(perct)
                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
            dataX=sorted(dataX)
            for ranking_id in dataY:
                for x, y in zip(dataX, dataY[ranking_id]): 
                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
                    realDataY[ranking_id][x].append(y)
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
        plt.xlabel('Percentage of Spammers', fontsize=16, fontweight='bold')
        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.title('Performance with spam filtering')
        plt.legend(loc=2)
#        plt.show()
        plt.savefig('performanceWithSpamFilteringForLatestMessages.png')
        plt.clf()
        
def performanceWithSpamDetection(generateData):
    experimentData = defaultdict(dict)
    ratios = [0.0,0.4,0.9]
    marker = dict([(0.0, 's'), (0.4, 'o'), (0.9, 'd')])
    spammerPercentages = [0.2, 0.01, 0.01]
    for iteration in range(5):
        for spamDetectionRatio, spammerPercentage in zip(ratios, spammerPercentages):
            experimentFileName = spamModelFolder+'performanceWithSpamDetection/%s/%0.3f'%(iteration,spamDetectionRatio)
            print experimentFileName
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 100, 'addUsersMethod': User.addUsersUsingRatioWithSpamDetection, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
    #                        'spammerMessagingProbability': spammerBudget,
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesSpamFiltered, RankingModel.popularMessages, RankingModel.popularMessagesSpamFiltered],
                        'spamDetectionRatio': spamDetectionRatio,
                        'experimentFileName': experimentFileName}
                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
            else:
                for data in FileIO.iterateJsonFromFile(experimentFileName):
                    for ranking_id in data['spammmess']:
                        if data['currentTimeStep'] not in experimentData[spamDetectionRatio]: experimentData[spamDetectionRatio][data['currentTimeStep']]=defaultdict(list)
                        experimentData[spamDetectionRatio][data['currentTimeStep']][ranking_id]+=data['spammmess'][ranking_id]
    if not generateData:
        sdr = {}
        for spamDetectionRatio in sorted(experimentData.keys()):
            dataToPlot = defaultdict(list)
            for timeUnit in experimentData[spamDetectionRatio]:
                dataToPlot['x'].append(timeUnit)
                for ranking_id in experimentData[spamDetectionRatio][timeUnit]: dataToPlot[ranking_id].append(np.mean(experimentData[spamDetectionRatio][timeUnit][ranking_id]))
            sdr[spamDetectionRatio]=dataToPlot
        for ranking_id in [RankingModel.LATEST_MESSAGES_SPAM_FILTERED, RankingModel.POPULAR_MESSAGES_SPAM_FILTERED]:
            for spamDetectionRatio in ratios:
                print ranking_id, spamDetectionRatio
                dataY = smooth(sdr[spamDetectionRatio][ranking_id],8)[:len(sdr[spamDetectionRatio]['x'])]
                dataX, dataY = sdr[spamDetectionRatio]['x'][10:], dataY[10:]
                if spamDetectionRatio==0.0: plt.plot([x-10 for x in dataX], dataY, label='%s'%(labels[ranking_id].split()[0]), lw=1, marker=marker[spamDetectionRatio])
                else: plt.plot([x-10 for x in dataX], dataY, label='%s (%d'%(labels[ranking_id].replace('Filtering', 'Detection'),spamDetectionRatio*100)+'%)', lw=1, marker=marker[spamDetectionRatio])
            plt.ylim(ymin=0, ymax=1)
            plt.xlim(xmin=0, xmax=90)
#            plt.title(ranking_id)
            plt.legend()
            plt.xlabel('Time', fontsize=16, fontweight='bold')
            plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#            plt.show()
            plt.savefig('performanceWithSpamDetection_%s.png'%ranking_id)
            plt.clf()
        
#def performanceWithSpamFilteringForPopularMessagesByTime(generateData):
#    experimentData = defaultdict(dict)
#    for iteration in range(5):
##        for spammerPercentage in range(1,21):
#            spammerPercentage = 5
#            spammerPercentage = spammerPercentage*0.05
#            experimentFileName = spamModelFolder+'performanceWithSpamFilteringForPopularMessagesByTime/%s/%0.3f'%(iteration,spammerPercentage)
#            print experimentFileName
#            if generateData:
#                model = MixedUsersModel()
#                conf = {'model': model, 'numberOfTimeSteps': 40, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
##                        'rankingMethods':[RankingModel.popularMessages, RankingModel.popularMessagesSpamFiltered],
#                        'rankingMethods':[RankingModel.latestMessages, RankingModel.latestMessagesSpamFiltered],
#                        'experimentFileName': experimentFileName,
#                        'noOfPayloadsPerSpammer': 1, 'noOfTopics': 10
#                        }
#                GeneralMethods.runCommand('rm -rf %s'%experimentFileName);run(**conf)
#            else:
##                tempData = defaultdict(dict)
#                for data in FileIO.iterateJsonFromFile(experimentFileName):
#                    for ranking_id in data['spammmess']:
#                        if data['currentTimeStep'] not in experimentData[ranking_id]: experimentData[ranking_id][data['currentTimeStep']] = []
#                        experimentData[ranking_id][data['currentTimeStep']].append(np.mean(data['spammmess'][ranking_id]))
##                experimentData[iteration]=tempData
#    if not generateData:
##        labels = dict(latest_messages_spam_filtered='Spam filtered',
##                      latest_messages='Not spam filtered')
##        for ranking_id in experimentData:
#        for ranking_id in ['latest_messages', 'latest_messages_spam_filtered']:
#            dataX, dataY = [], []
#            for k, v in experimentData[ranking_id].iteritems():
#                dataX.append(k), dataY.append(np.mean(v))
#            plt.plot(dataX, dataY, label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
#        plt.xlabel('Time', fontsize=16, fontweight='bold'), plt.ylabel('Spamness', fontsize=16, fontweight='bold')
#        plt.legend()
##        plt.show()
#        plt.savefig('performanceWithSpamFilteringForPopularMessagesByTime.png')
#        plt.clf()
##        realDataY = defaultdict(dict)
##        for iteration in experimentData:
##            dataY = defaultdict(list)
##            dataX = []
##            for perct in sorted(experimentData[iteration]):
##                dataX.append(perct)
##                for ranking_id, values in experimentData[iteration][perct].iteritems(): dataY[ranking_id].append(np.mean(values))
##            dataX=sorted(dataX)
##            for ranking_id in dataY:
##                for x, y in zip(dataX, dataY[ranking_id]): 
##                    if x not in realDataY[ranking_id]: realDataY[ranking_id][x]=[] 
##                    realDataY[ranking_id][x].append(y)
##        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=labels[ranking_id], lw=1, marker=RankingModel.marker[ranking_id])
##        plt.xlabel('Percentage of spammers', fontsize=16, fontweight='bold')
##        plt.ylabel('Spamness', fontsize=16, fontweight='bold')
###        plt.title('Performance with spam filtering')
##        plt.legend(loc=2)
###        plt.show()
##        plt.savefig('performanceWithSpamFilteringForPopularMessagesByTime.png')

#trendCurves()
#performanceAsPercentageOfSpammersVaries(generateData=False)
#performanceAsSpammerBudgetVaries(generateData=False)
#performanceAsSpammerPayloadVaries(generateData=False)
#performanceAsNoOfGlobalPayloadsVary(generateData=False)
#performanceAsPercentageOfGlobalSpammerVaries(generateData=False)
#performanceWithSpamFilteringForLatestMessages(generateData=False)
#performanceWithSpamFilteringForPopularMessages(generateData=False)
performanceWithSpamDetection(generateData=True)

#model = MixedUsersModel()
#spammerPercentage = 0.50
#conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 
#        'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
#    'rankingMethods':[RankingModel.latestMessages, RankingModel.popularMessages],
#    'experimentFileName': spamModelFolder+'temp'}
#GeneralMethods.runCommand('rm -rf %s'%experimentFileName);
#run(**conf)