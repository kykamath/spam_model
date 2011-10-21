'''
Created on Oct 20, 2011

@author: kykamath
'''
from models import MixedUsersModel, RankingModel, run, Analysis
from library.classes import GeneralMethods
from objects import User
from settings import spamModelFolder
from library.file_io import FileIO
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

def trendCurves():
    model = MixedUsersModel()
    experimentFileName = spamModelFolder+model.id
    conf = {'model': model, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.trendCurves, 1)], 'ratio': {'normal': 0.97, 'spammer': 0.03},
            'experimentFileName': experimentFileName}
    GeneralMethods.runCommand('rm -rf %s'%experimentFileName); run(**conf)
    Analysis.trendCurves(experimentFileName=experimentFileName)
    
def performanceAsPercentageOfSpammersVaries(generateData):
    experimentData = defaultdict(dict)
    for iteration in range(10):
        for spammerPercentage in range(1,21):
            spammerPercentage = spammerPercentage*0.05
            experimentFileName = spamModelFolder+'performanceAsPercentageOfSpammersVaries/%s/%0.3f'%(iteration,spammerPercentage)
            if generateData:
                model = MixedUsersModel()
                conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
                        'rankingMethods':[RankingModel.latestMessages, RankingModel.popularMessages],
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
                
#            print dataY
#            for ranking_id in dataY:
#                realDataY[ranking_id].append() 
        for ranking_id in dataY: plt.plot(dataX, [np.mean(realDataY[ranking_id][x]) for x in dataX], label=ranking_id, lw=2, marker='s')
        plt.xlabel('Percentage of spammers')
        plt.ylabel('Spammness')
        plt.title('Spammness with changing percentage of spammers')
        plt.legend(loc=2)
        plt.show()
        

#trendCurves()
performanceAsPercentageOfSpammersVaries(generateData=False)


#model = MixedUsersModel()
#spammerPercentage = 0.50
#conf = {'model': model, 'numberOfTimeSteps': 10, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.measureRankingQuality, 1)], 
#        'ratio': {'normal': 1-spammerPercentage, 'spammer': spammerPercentage},
#    'rankingMethods':[RankingModel.latestMessages, RankingModel.popularMessages],
#    'experimentFileName': spamModelFolder+'temp'}
#GeneralMethods.runCommand('rm -rf %s'%experimentFileName);
#run(**conf)