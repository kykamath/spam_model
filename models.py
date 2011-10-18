'''
Spam models.

Created on Oct 17, 2011

@author: kykamath
'''
from library.classes import FixedIntervalMethod
from library.classes import GeneralMethods
from objects import Topic, User
import random
from library.file_io import FileIO
from settings import spamModelFolder
from collections import defaultdict
import matplotlib.pyplot as plt

class Model(object):
    def __init__(self, id):
        self.id = id
#        self.noOfMessagesPerTimeStep = noOfMessagesPerTimeStep
#        self.newTopicProbability = newTopicProbability
        self.analysisFile = spamModelFolder+'model_analysis'
#    def process(self, currentTimeStep, currentTopics, currentUsers):
#        for i in range(self.noOfMessagesPerTimeStep):
#            topic = None
#            if not currentTopics: Topic.addNewTopics(currentTopics, 300)
#            if GeneralMethods.trueWith(self.newTopicProbability): 
#                topic = Topic(len(currentTopics))
#                currentTopics.append(topic)
#            else: topic=random.choice(currentTopics)
#            topic.countDistribution[currentTimeStep]+=1
#            topic.totalCount+=1
    def process(self, currentTimeStep, currentTopics, currentUsers, **conf):
        for user in currentUsers:
            if GeneralMethods.trueWith(conf['userMessagingProbability']):
                topic = None
                if not currentTopics: Topic.addNewTopics(currentTopics, 300)
                if GeneralMethods.trueWith(conf['newTopicProbability']): 
                    topic = Topic(len(currentTopics))
                    currentTopics.append(topic)
                else: topic=random.choice(currentTopics)
                topic.countDistribution[currentTimeStep]+=1
                topic.totalCount+=1
                
    def analysis(self, currentTimeStep=None, currentTopics=None, currentUsers=None, modeling=True):
        if modeling:
            topicDistribution = dict((str(topic.id), {'total': topic.totalCount, 'timeStep': topic.countDistribution[currentTimeStep]}) for topic in currentTopics)
            print currentTimeStep
            FileIO.writeToFileAsJson({'t':currentTimeStep, 'topics':topicDistribution}, self.analysisFile)
        else:
            topicsDataX = defaultdict(list)
            topicsDataY = defaultdict(list)
            for data in FileIO.iterateJsonFromFile(self.analysisFile):
                for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
            for topic in topicsDataX: plt.fill_between(topicsDataX[topic], topicsDataY[topic], color=GeneralMethods.getRandomColor(), alpha=0.6)
            plt.show()
    
        
def run(model, numberOfTimeSteps, analysisMethod, 
        addUsersMethod=User.addNewUsers, noOfUsers=10000, analysisFrequency=1, 
        **conf):
    currentTopics = []
    currentUsers = []
    addUsersMethod(currentUsers, noOfUsers, **conf)
    
    analysis = FixedIntervalMethod(analysisMethod, analysisFrequency)

    for currentTimeStep in range(numberOfTimeSteps):
        Topic.incrementTopicAge(currentTopics)
        model.process(currentTimeStep, currentTopics, currentUsers, **conf)
        analysis.call(currentTimeStep, currentTimeStep=currentTimeStep, currentTopics=currentTopics, currentUsers=currentUsers)

if __name__ == '__main__':
    model=Model(1)
    GeneralMethods.runCommand('rm -rf %s'%model.analysisFile)
    conf = { 'model': model, 'numberOfTimeSteps': 200, 'analysisMethod': model.analysis,
            'newTopicProbability': 0.001, 'userMessagingProbability': 0.1,
            }
    run(**conf)
    model.analysis(modeling=False)
    