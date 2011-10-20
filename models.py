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
from settings import spamModelFolder, stickinessLowerThreshold,\
    noOfMessagesToCalculateSpammness
from collections import defaultdict
from itertools import groupby
from operator import itemgetter
import matplotlib.pyplot as plt

RANDOM_MODEL = 'random'
MIXED_USERS_MODEL = 'mixed_users'

def modified_log(i):
    if i==0: return 0
    else: return math.log(i)
    
def norm(k): return sum([1/(math.log((1+i),2)) for i in range(1,k+1)])
def spammness(messages, norm): return sum([1/(math.log((1+i),2)) for m,i in zip(messages, range(1,len(messages)+1)) if m.payLoad.isSpam])/norm
norm_k=norm(noOfMessagesToCalculateSpammness)


class Analysis:
    @staticmethod
    def trendCurves(iterationData=None, modeling=True, modelFile=None):
        currentTimeStep, model, currentTopics, _, finalCall, conf = [None]*6
        if iterationData: 
            currentTimeStep, model, currentTopics, _, finalCall, conf = iterationData
            modelFile = spamModelFolder+model.id
        if modeling:
            if not finalCall:
                topicDistribution = dict((str(topic.id), {'total': topic.totalCount, 'timeStep': topic.countDistribution[currentTimeStep]}) for topic in currentTopics)
                print currentTimeStep
                FileIO.writeToFileAsJson({'t':currentTimeStep, 'topics':topicDistribution}, modelFile)
            else:
                iterationInfo  = {'trending_topics': [topic.id for topic in currentTopics if topic.stickiness>=stickinessLowerThreshold],
                      'topic_colors': dict((str(topic.id), topic.color) for topic in currentTopics),
                      'conf': conf}
                FileIO.writeToFileAsJson(iterationInfo, modelFile)
        else:
            topicsDataX = defaultdict(list)
            topicsDataY = defaultdict(list)
            for data in FileIO.iterateJsonFromFile(modelFile):
                if 'conf' not in data:
                    for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
                else: topicColorMap=data['topic_colors']; trendingTopics=data['trending_topics']
            for topic in topicsDataX: plt.fill_between(topicsDataX[topic], topicsDataY[topic], color=topicColorMap[str(topic)], alpha=1.0)
            plt.figure()
            for topic in trendingTopics: plt.fill_between(topicsDataX[str(topic)], topicsDataY[str(topic)], color=topicColorMap[str(topic)], alpha=1.0)
            plt.show()
    @staticmethod
    def measureRankingQuality(iterationData=None):
        _, model, _, _, _, conf = [None]*6
        if iterationData: 
            _, model, _, _, _, conf = iterationData
            rankingMethods = conf['rankingMethods']
        topTopics = sorted(model.topicsDistributionInTheTimeSet.iteritems(), key=itemgetter(1), reverse=True)[:5]
        model.topicsDistributionInTheTimeSet = defaultdict(int)
        for queryTopic,_ in topTopics:
            for rankingMethod in rankingMethods: 
                ranking_id, messages = rankingMethod(queryTopic, model.topicToMessagesMap)
                print ranking_id, spammness(messages, norm_k)

class RankingModel:
    LATEST_MESSAGES = 'latest_messages'
    POPULAR_MESSAGES = 'popular_messages'
    @staticmethod
    def latestMessages(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness): 
        return (RankingModel.LATEST_MESSAGES, sorted(topicToMessagesMap[queryTopic], key=lambda m: m.timeStep, reverse=True)[:noOfMessages])
    @staticmethod
    def popularMessages(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness): 
        def getEarliestMessage(messages): return sorted(messages, key=lambda m: m.timeStep, reverse=True)[0]
        payLoads, messageIdToMessage, payLoadsToMessageMap = [], {},defaultdict(list)
        for m in topicToMessagesMap[queryTopic]:
            payLoads.append(m.payLoad.id)
            messageIdToMessage[m.id] = m
            payLoadsToMessageMap[m.payLoad.id].append(m)
        rankedPayLoads = sorted([(id, len(list(occurences))) for id, occurences in groupby(sorted(payLoads))], key=itemgetter(1), reverse=True)[:noOfMessages]
        return (RankingModel.POPULAR_MESSAGES, [getEarliestMessage(payLoadsToMessageMap[pid]) for pid,_ in rankedPayLoads])

class Model(object):
    def __init__(self, id=RANDOM_MODEL):
        self.id = id
#        self.modelFile = spamModelFolder+id
        self.topicToMessagesMap = defaultdict(list)
        self.topicsDistributionInTheTimeSet = defaultdict(int)
        self.totalMessages, self.messagesWithSpamPayload = 0, 0
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
                self.topicToMessagesMap[topic.id].append(message)
                self.totalMessages+=1
                if message.payLoad.isSpam: self.messagesWithSpamPayload+=1
                self.topicsDistributionInTheTimeSet[topic.id]+=1
            
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
        
#def run(model, numberOfTimeSteps=200, addUsersMethod=User.addNormalUsers, noOfUsers=10000, analysisMethods = [], analysisFrequency=1, qualityMeasuringFrequency=1, **conf):
def run(model, numberOfTimeSteps=200, addUsersMethod=User.addNormalUsers, noOfUsers=10000, analysisMethods = [], **conf):
    currentTopics = []
    currentUsers = []
    addUsersMethod(currentUsers, noOfUsers, **conf)
    
#    trendCurves = FixedIntervalMethod(model.trendCurves, analysisFrequency)
#    measureQuality = FixedIntervalMethod(model.measureQuality, qualityMeasuringFrequency)
    analysis = []
    for method, frequency in analysisMethods: analysis.append(FixedIntervalMethod(method, frequency))
    
    for currentTimeStep in range(numberOfTimeSteps):
        Topic.incrementTopicAge(currentTopics)
        model.process(currentTimeStep, currentTopics, currentUsers, **conf)
        for method in analysis: method.call(currentTimeStep, iterationData=(currentTimeStep, model, currentTopics, currentUsers, False, conf))
#        trendCurves.call(currentTimeStep, currentTimeStep=currentTimeStep, currentTopics=currentTopics, currentUsers=currentUsers)
#        measureQuality.call(currentTimeStep, currentTimeStep=currentTimeStep, currentTopics=currentTopics, rankingMethod=rankingMethod)
#    iterationInfo  = {'trending_topics': [topic.id for topic in currentTopics if topic.stickiness>=stickinessLowerThreshold],
#                      'topic_colors': dict((str(topic.id), topic.color) for topic in currentTopics),
#                      'conf': conf}
#    FileIO.writeToFileAsJson(iterationInfo, model.modelFile)
    currentTimeStep+=1
    for method in analysis: method.call(currentTimeStep, iterationData=(currentTimeStep, model, currentTopics, currentUsers, True, conf))
    
#if __name__ == '__main__':
#    model=Model()
#    model = MixedUsersModel()
#    GeneralMethods.runCommand('rm -rf %s'%model.modelFile)
#    conf = {'model': model, 'addUsersMethod': User.addUsersUsingRatio, 'analysisMethods': [(Analysis.trendCurves, 1)], 'ratio': {'normal': 0.9, 'spammer': 0.1}}
#    run(**conf)
#    print model.totalMessages, model.messagesWithSpamPayload
#    model.analysis(modeling=False)
#    model.plotTrendingTopics()
