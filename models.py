'''
Spam models.

Created on Oct 17, 2011

@author: kykamath
'''
from library.classes import FixedIntervalMethod
from library.classes import GeneralMethods
from objects import Topic, User
import random, math
from library.file_io import FileIO
from settings import spamModelFolder
from collections import defaultdict
from operator import itemgetter
import matplotlib.pyplot as plt

RANDOM_MODEL = 'random'
NON_SPAM_MODEL = 'non_spam'

def modified_log(i):
    if i==0: return 0
    else: return math.log(i)

class Model(object):
    def __init__(self, id=RANDOM_MODEL):
        self.modelFile = spamModelFolder+id
    def topicSelectionMethod(self, currentTimeStep, user, currentTopics, **conf): 
        topic = None
        if GeneralMethods.trueWith(conf['newTopicProbability']): topic = Topic(len(currentTopics)); currentTopics.append(topic)
        else: topic=random.choice(currentTopics)
        return topic
    def process(self, currentTimeStep, currentTopics, currentUsers, **conf):
        for user in currentUsers:
            if GeneralMethods.trueWith(conf['userMessagingProbability']):
                if not currentTopics: Topic.addNewTopics(currentTopics, 300)
                topic = self.topicSelectionMethod(currentTimeStep, user, currentTopics, **conf)
                if topic:
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
#            plt.savefig(self.modelFile+'.pdf')
            
class NonSpamModel(Model):
    def __init__(self): 
        super(NonSpamModel, self).__init__(NON_SPAM_MODEL)
        self.lastObservedTimeStep = None
        self.topicProbabilities = None
    def topicSelectionMethod(self, currentTimeStep, user, currentTopics, **conf):
        if self.lastObservedTimeStep!=currentTimeStep: self._updateTopicProbabilities(currentTimeStep, currentTopics)
        topic = None
        if GeneralMethods.trueWith(conf['newTopicProbability']): 
#            pass
            topic = Topic(len(currentTopics)); currentTopics.append(topic)
        else: 
#            if self.topicProbabilities[user.topicClass][:10]:
            topic=random.choice(self.topicProbabilities[user.topicClass][:10])[0]
#            print topic.topicClass, topic.id
        return topic
    def _updateTopicProbabilities(self, currentTimeStep, currentTopics):
        self.topicProbabilities = defaultdict(list)
        totalMessagesSentInPreviousIntervals = 0.0
        numberOfPreviousIntervals = 1
        for topic in currentTopics:
            for i in range(0, numberOfPreviousIntervals): totalMessagesSentInPreviousIntervals+=topic.countDistribution[currentTimeStep-i]
        topicsToRemove = []
        for topic in currentTopics:
            topicScore = 0.0
            for i in range(1, numberOfPreviousIntervals+1): topicScore+=topic.countDistribution[currentTimeStep-i]
            if totalMessagesSentInPreviousIntervals!=0: topicScore/=totalMessagesSentInPreviousIntervals
            else: topicScore = 1.0/len(currentTopics)
            topicScore = modified_log(topicScore) + modified_log(math.exp(-0.5*topic.age))#+modified_log(topic.stickiness)
#            if topic.age>50: topicsToRemove.append(topic)
#            else: 
            self.topicProbabilities[topic.topicClass].append((topic, topicScore))
#        for topic in topicsToRemove: currentTopics.remove(topic)
#        Topic.addNewTopics(currentTopics, len(topicsToRemove))
        for topicClass in self.topicProbabilities.keys()[:]: 
            self.topicProbabilities[topicClass] = sorted(self.topicProbabilities[topicClass], key=itemgetter(1), reverse=True)
#            print self.topicProbabilities[topicClass][:5]
#            print self.topicProbabilities[topicClass]  
        self.lastObservedTimeStep=currentTimeStep
        
        
def run(model, numberOfTimeSteps=100, 
        addUsersMethod=User.addNewUsers, noOfUsers=10000, analysisFrequency=1, 
        **conf):
    currentTopics = []
    currentUsers = []
    addUsersMethod(currentUsers, noOfUsers, **conf)
    
    analysis = FixedIntervalMethod(model.analysis, analysisFrequency)
    
    for currentTimeStep in range(numberOfTimeSteps):
        Topic.incrementTopicAge(currentTopics)
        model.process(currentTimeStep, currentTopics, currentUsers, **conf)
        analysis.call(currentTimeStep, currentTimeStep=currentTimeStep, currentTopics=currentTopics, currentUsers=currentUsers)

if __name__ == '__main__':
#    model=Model()
    model = NonSpamModel()
    GeneralMethods.runCommand('rm -rf %s'%model.modelFile)
    conf = {'model': model, 'newTopicProbability': 0.001, 'userMessagingProbability': 0.1}
    run(**conf)
    model.analysis(modeling=False)
    
