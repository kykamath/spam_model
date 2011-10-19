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
from settings import spamModelFolder, stickinessLowerThreshold
from collections import defaultdict
from operator import itemgetter
import matplotlib.pyplot as plt

RANDOM_MODEL = 'random'
MIXED_USERS_MODEL = 'mixed_users'

def modified_log(i):
    if i==0: return 0
    else: return math.log(i)

class Model(object):
    def __init__(self, id=RANDOM_MODEL):
        self.modelFile = spamModelFolder+id
    def messageSelectionMethod(self, currentTimeStep, user, currentTopics, **conf): 
        message = None
        if GeneralMethods.trueWith(user.messagingProbability):
            if GeneralMethods.trueWith(user.newTopicProbability): topic = Topic(len(currentTopics)); currentTopics.append(topic); message=user.generateMessage(currentTimeStep, topic)
            else: message=user.generateMessage(currentTimeStep, random.choice(currentTopics))
        return message
    def process(self, currentTimeStep, currentTopics, currentUsers, **conf):
        if not currentTopics: Topic.addNewTopics(currentTopics, 300)
        for user in currentUsers:
            message = self.messageSelectionMethod(currentTimeStep, user, currentTopics, **conf)
            if message:
                topic = message.topic
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
                if 'conf' not in data:
                    for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
                else: topicColorMap=data['topic_colors']
            for topic in topicsDataX: plt.fill_between(topicsDataX[topic], topicsDataY[topic], color=topicColorMap[str(topic)], alpha=1.0)
            plt.show()
#            plt.savefig(self.modelFile+'.pdf')
    def plotTrendingTopics(self):
        topicsDataX, topicsDataY, trendingTopics, topicColorMap = defaultdict(list), defaultdict(list), [], {}
        for data in FileIO.iterateJsonFromFile(self.modelFile):
            if 'conf' not in data:
                for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
            else: 
                trendingTopics=data['trending_topics']
                topicColorMap=data['topic_colors']
        for topic in trendingTopics: plt.fill_between(topicsDataX[str(topic)], topicsDataY[str(topic)], color=topicColorMap[str(topic)], alpha=1.0)
        plt.show()
#        plt.savefig(self.modelFile+'_tt.pdf')
            
class MixedUsersModel(Model):
    def __init__(self): 
        super(MixedUsersModel, self).__init__(MIXED_USERS_MODEL)
        self.lastObservedTimeStep = None
        self.topicProbabilities = None
        self.topTopics = None
    def messageSelectionMethod(self, currentTimeStep, user, currentTopics, **conf):
        if self.lastObservedTimeStep!=currentTimeStep: self._updateTopicProbabilities(currentTimeStep, currentTopics, **conf)
        message = None
        if GeneralMethods.trueWith(user.messagingProbability):
            if GeneralMethods.trueWith(user.newTopicProbability): topic = Topic(len(currentTopics)); currentTopics.append(topic); message=user.generateMessage(currentTimeStep, topic)
            else: 
                if GeneralMethods.trueWith(user.probabilityOfPickingPopularTopic):
                        if user.topicClass!=None:
                            topicIndex = GeneralMethods.weightedChoice([i[1] for i in self.topicProbabilities[user.topicClass]])
                            topic = self.topicProbabilities[user.topicClass][topicIndex][0]
                            message=user.generateMessage(currentTimeStep, topic)
                            if not GeneralMethods.trueWith(topic.stickiness): message = None
                        else: 
                            topicIndex = GeneralMethods.weightedChoice([i[1] for i in self.topTopics])
                            topic = self.topTopics[topicIndex][0]
                            message=user.generateMessage(currentTimeStep, topic)
                else: message=user.generateMessage(currentTimeStep, random.choice(self.topicProbabilities[user.topicClass])[0])
        return message
    def _updateTopicProbabilities(self, currentTimeStep, currentTopics, **conf):
        self.topicProbabilities, self.topTopics = defaultdict(list), []
        totalMessagesSentInPreviousIntervals = 0.0
        numberOfPreviousIntervals = 1
        for topic in currentTopics: totalMessagesSentInPreviousIntervals+=topic.countDistribution[currentTimeStep-1]
        for topic in currentTopics:
            topicScore = 0.0
            for i in range(1, numberOfPreviousIntervals+1): topicScore+=topic.countDistribution[currentTimeStep-i]
            if totalMessagesSentInPreviousIntervals!=0: topicScore/=totalMessagesSentInPreviousIntervals
            else: topicScore = 1.0/len(currentTopics)
            topicScore = topicScore * math.exp(topic.decayCoefficient*topic.age)
            self.topicProbabilities[topic.topicClass].append((topic, topicScore))
        for topicClass in self.topicProbabilities.keys()[:]: self.topTopics+=sorted(self.topicProbabilities[topicClass], key=itemgetter(1), reverse=True)[:1]
        self.lastObservedTimeStep=currentTimeStep
        
def run(model, numberOfTimeSteps=200, addUsersMethod=User.addNormalUsers, noOfUsers=10000, analysisFrequency=1, **conf):
    currentTopics = []
    currentUsers = []
    addUsersMethod(currentUsers, noOfUsers, **conf)
    
    analysis = FixedIntervalMethod(model.analysis, analysisFrequency)
    
    for currentTimeStep in range(numberOfTimeSteps):
        Topic.incrementTopicAge(currentTopics)
        model.process(currentTimeStep, currentTopics, currentUsers, **conf)
        analysis.call(currentTimeStep, currentTimeStep=currentTimeStep, currentTopics=currentTopics, currentUsers=currentUsers)
    iterationInfo  = {'trending_topics': [topic.id for topic in currentTopics if topic.stickiness>=stickinessLowerThreshold],
                      'topic_colors': dict((str(topic.id), topic.color) for topic in currentTopics),
                      'conf': conf}
    FileIO.writeToFileAsJson(iterationInfo, model.modelFile)
    
if __name__ == '__main__':
#    model=Model()
    model = MixedUsersModel()
    GeneralMethods.runCommand('rm -rf %s'%model.modelFile)
    conf = {'model': model, 'addUsersMethod': User.addUsersUsingRatio, 'ratio': {'normal': 0.97, 'spammer': 0.03}}
    run(**conf)
    model.analysis(modeling=False)
    model.plotTrendingTopics()
