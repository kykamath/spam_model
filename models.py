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

RANDOM_MODEL = 'random'
NON_SPAM_MODEL = 'non_spam'

class Model(object):
    def __init__(self, id=RANDOM_MODEL):
        self.modelFile = spamModelFolder+id
    def topicSelectionMethod(self, user, currentTopics): return random.choice(currentTopics) 
    def process(self, currentTimeStep, currentTopics, currentUsers, **conf):
        for user in currentUsers:
            if GeneralMethods.trueWith(conf['userMessagingProbability']):
                topic = None
                if not currentTopics: Topic.addNewTopics(currentTopics, 300)
                if GeneralMethods.trueWith(conf['newTopicProbability']): 
                    topic = Topic(len(currentTopics))
                    currentTopics.append(topic)
                else: topic=self.topicSelectionMethod(user, currentTopics)
                topic.countDistribution[currentTimeStep]+=1
                topic.totalCount+=1
    def analysis(self, currentTimeStep=None, currentTopics=None, currentUsers=None, modeling=True):
        if modeling:
            topicDistribution = dict((str(topic.id), {'total': topic.totalCount, 'timeStep': topic.countDistribution[currentTimeStep]}) for topic in currentTopics)
            print currentTimeStep
            FileIO.writeToFileAsJson({'t':currentTimeStep, 'topics':topicDistribution}, self.modelFile)
        else:
            topicsDataX = defaultdict(list)
            topicsDataY = defaultdict(list)
            for data in FileIO.iterateJsonFromFile(self.modelFile):
                for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
            for topic in topicsDataX: plt.fill_between(topicsDataX[topic], topicsDataY[topic], color=GeneralMethods.getRandomColor(), alpha=0.6)
            plt.show()
            
class NonSpamModel(Model):
    pass
    
        
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
    model=Model()
    GeneralMethods.runCommand('rm -rf %s'%model.modelFile)
    conf = { 'model': model, 'numberOfTimeSteps': 200, 'analysisMethod': model.analysis,
            'newTopicProbability': 0.001, 'userMessagingProbability': 0.1,
            }
    run(**conf)
    model.analysis(modeling=False)
    