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
from settings import stickinessLowerThreshold, noOfMessagesToCalculateSpammness
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
print sum([1/(math.log((1+i),2)) for m,i in zip([1,0,0,0,0,0,0,0,0,0], range(1,11)) if m])/norm_k


class Analysis:
    @staticmethod
    def trendCurves(iterationData=None, experimentFileName=None):
        if iterationData: 
            currentTimeStep, _, currentTopics, _, finalCall, conf = iterationData
            experimentFileName = conf['experimentFileName']
            if not finalCall:
                topicDistribution = dict((str(topic.id), {'total': topic.totalCount, 'timeStep': topic.countDistribution[currentTimeStep]}) for topic in currentTopics)
#                print currentTimeStep
                FileIO.writeToFileAsJson({'t':currentTimeStep, 'topics':topicDistribution}, experimentFileName)
            else:
                iterationInfo  = {'trending_topics': [topic.id for topic in currentTopics if topic.stickiness>=stickinessLowerThreshold],
                      'topic_colors': dict((str(topic.id), topic.color) for topic in currentTopics),
                      'conf': conf}
                FileIO.writeToFileAsJson(iterationInfo, experimentFileName)
        else:
            topicsDataX = defaultdict(list)
            topicsDataY = defaultdict(list)
            for data in FileIO.iterateJsonFromFile(experimentFileName):
                if 'conf' not in data:
                    for topic in data['topics']: topicsDataX[topic].append(data['t']), topicsDataY[topic].append(data['topics'][topic]['timeStep'])
                else: topicColorMap=data['topic_colors']; trendingTopics=data['trending_topics']
            for topic in topicsDataX: plt.fill_between(topicsDataX[topic], topicsDataY[topic], color=topicColorMap[str(topic)], alpha=1.0)
            plt.figure()
            for topic in trendingTopics: plt.fill_between(topicsDataX[str(topic)], topicsDataY[str(topic)], color=topicColorMap[str(topic)], alpha=1.0)
            plt.show()
    @staticmethod
    def measureRankingQuality(iterationData=None, experimentFileName=None):
#        def getTopTopics(model, noOfTopics):
#            topics = set()
#            topTopics = model.topTopics[:]
#            while True:
#                topicIndex = GeneralMethods.weightedChoice([i[1] for i in topTopics])
#                topic = topTopics[topicIndex][0].id
#                del topTopics[topicIndex]
#                if topic not in topics: topics.add(topic)
#                if len(topics)==noOfTopics or len(topics)==len(model.topTopics): break
#            return [(t, 0) for t in topics]
                
        if iterationData: 
            currentTimeStep, model, _, _, finalCall, conf = iterationData
            if not finalCall:
                rankingMethods = conf['rankingMethods']
                experimentFileName = conf['experimentFileName']
                topTopics = sorted(model.topicsDistributionInTheTimeSet.iteritems(), key=itemgetter(1), reverse=True)[:10]
#                topTopics = getTopTopics(model, 10)
#                topTopics = random.sample(sorted(model.topicsDistributionInTheTimeSet.iteritems(), key=itemgetter(1), reverse=True)[:10], min(len(model.topicsDistributionInTheTimeSet),5))
#                topTopics = random.sample(model.topicsDistributionInTheTimeSet.items(), min(len(model.topicsDistributionInTheTimeSet),5))
                iterationData = {'currentTimeStep': currentTimeStep, 'spammmess': defaultdict(list)}
                for rankingMethod in rankingMethods: 
                    for queryTopic,_ in topTopics:
                        ranking_id, messages = rankingMethod(queryTopic, model.topicToMessagesMap, **conf)
#                        if spammness(messages, norm_k)==0:
#                            print 'c'
#                        print rankingMethod, spammness(messages, norm_k)
                        iterationData['spammmess'][ranking_id].append(spammness(messages, norm_k))
#                        print ranking_id, spammness(messages, norm_k)
                FileIO.writeToFileAsJson(iterationData, experimentFileName)
                model.topicsDistributionInTheTimeSet = defaultdict(int)
                
class SpamDetectionModel:
    FILTER_SCORE_THRESHOLD = 0.25
    FILTER_METHOD = 'filter_method'
    @staticmethod
    def filterMethod(queryTopic, topicToMessagesMap):
        payLoadsAndUsers = sorted([(m.payLoad.id, m.id.split('_')[0]) for m in topicToMessagesMap[queryTopic]], key=itemgetter(0))
        payLoadsAndUsers = [(k, list(l)) for k,l in groupby(payLoadsAndUsers, key=itemgetter(0))]
        payLoadId_UserCount_MessageCount = [(id, len(set(t[1] for t in l))/float(len(l)), len(set(t[1] for t in l)), float(len(l))  )for id, l in payLoadsAndUsers]
        spamPayloads = [t[0] for t in payLoadId_UserCount_MessageCount if t[1]<=SpamDetectionModel.FILTER_SCORE_THRESHOLD]
#        if spamPayloads:
#            print 'c'
        return spamPayloads

class RankingModel:
    LATEST_MESSAGES = 'latest_messages'
    LATEST_MESSAGES_DUPLICATES_REMOVED = 'latest_messages_dup_removed'
    POPULAR_MESSAGES = 'popular_messages'
    LATEST_MESSAGES_SPAM_FILTERED = 'latest_messages_spam_filtered'
    POPULAR_MESSAGES_SPAM_FILTERED = 'popular_messages_spam_filtered'
    marker = {LATEST_MESSAGES: 'o', POPULAR_MESSAGES: 's', LATEST_MESSAGES_DUPLICATES_REMOVED: '^', 
              LATEST_MESSAGES_SPAM_FILTERED: 's', POPULAR_MESSAGES_SPAM_FILTERED: 's'}
    @staticmethod
    def latestMessages(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness, **conf): return (RankingModel.LATEST_MESSAGES, sorted(topicToMessagesMap[queryTopic], key=lambda m: m.timeStep, reverse=True)[:noOfMessages])
    @staticmethod
    def latestMessagesSpamFiltered(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness, **conf): 
#        spamDectectionMethod = conf.get('spamDectectionMethod', None)
        spamPayloads = SpamDetectionModel.filterMethod(queryTopic, topicToMessagesMap)
        sortedMessages = sorted(topicToMessagesMap[queryTopic], key=lambda m: m.timeStep, reverse=True)
        messagesAfterSpamRemoved = filter(lambda m: m.payLoad.id not in spamPayloads, sortedMessages)
        return (RankingModel.LATEST_MESSAGES_SPAM_FILTERED, messagesAfterSpamRemoved[:noOfMessages])
    @staticmethod
    def latestMessagesDuplicatesRemoved(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness, **conf): 
        messagesToReturn, observedPayload = [], set()
        for message in sorted(topicToMessagesMap[queryTopic], key=lambda m: m.timeStep, reverse=True):
            if message.payLoad.id not in observedPayload: messagesToReturn.append(message); observedPayload.add(message.payLoad.id)
            if len(messagesToReturn)==noOfMessages: break
        return (RankingModel.LATEST_MESSAGES_DUPLICATES_REMOVED, messagesToReturn)
    @staticmethod
    def popularMessages(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness, **conf): 
        def getEarliestMessage(messages): return sorted(messages, key=lambda m: m.timeStep, reverse=True)[0]
        payLoads, messageIdToMessage, payLoadsToMessageMap = [], {},defaultdict(list)
        for m in topicToMessagesMap[queryTopic]:
            payLoads.append(m.payLoad.id)
            messageIdToMessage[m.id] = m
            payLoadsToMessageMap[m.payLoad.id].append(m)
        rankedPayLoads = sorted([(id, len(list(occurences))) for id, occurences in groupby(sorted(payLoads))], key=itemgetter(1), reverse=True)[:noOfMessages]
        return (RankingModel.POPULAR_MESSAGES, [getEarliestMessage(payLoadsToMessageMap[pid]) for pid,_ in rankedPayLoads])
    @staticmethod
    def popularMessagesSpamFiltered(queryTopic, topicToMessagesMap, noOfMessages=noOfMessagesToCalculateSpammness, **conf):
        spamPayloads = SpamDetectionModel.filterMethod(queryTopic, topicToMessagesMap)
        def getEarliestMessage(messages): return sorted(messages, key=lambda m: m.timeStep, reverse=True)[0]
        payLoads, messageIdToMessage, payLoadsToMessageMap = [], {},defaultdict(list)
        for m in topicToMessagesMap[queryTopic]:
            payLoads.append(m.payLoad.id)
            messageIdToMessage[m.id] = m
            payLoadsToMessageMap[m.payLoad.id].append(m)
        rankedPayLoads = sorted([(id, len(list(occurences))) for id, occurences in groupby(sorted(payLoads)) if id not in spamPayloads], key=itemgetter(1), reverse=True)[:noOfMessages]
        return (RankingModel.POPULAR_MESSAGES_SPAM_FILTERED, [getEarliestMessage(payLoadsToMessageMap[pid]) for pid,_ in rankedPayLoads])

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
        if not currentTopics: Topic.addNewTopics(currentTopics, conf.get('noOfTopics', 300))
        random.shuffle(currentUsers)
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
                else: 
                    if user.topicClass!=None: 
                        message=user.generateMessage(currentTimeStep, random.choice(self.topicProbabilities[user.topicClass])[0])
                    else:
                        topicIndex = GeneralMethods.weightedChoice([i[1] for i in self.allTopics])
                        topic = self.allTopics[topicIndex][0]
                        message=user.generateMessage(currentTimeStep, topic)
        return message
    def _updateTopicProbabilities(self, currentTimeStep, currentTopics, **conf):
        self.topicProbabilities, self.topTopics, self.allTopics = defaultdict(list), [], []
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
        for topicClass in self.topicProbabilities.keys()[:]: 
            self.topTopics+=sorted(self.topicProbabilities[topicClass], key=itemgetter(1), reverse=True)[:16]
            self.allTopics+=sorted(self.topicProbabilities[topicClass], key=itemgetter(1), reverse=True)
        self.lastObservedTimeStep=currentTimeStep
        
def run(model, numberOfTimeSteps=200, addUsersMethod=User.addNormalUsers, noOfUsers=10000, analysisMethods = [], **conf):
    currentTopics, currentUsers = [], []
    addUsersMethod(currentUsers, noOfUsers, **conf)
    random.shuffle(currentUsers)
    conf['spamDectectionMethod'] = SpamDetectionModel.filterMethod
    analysis = []
    for method, frequency in analysisMethods: analysis.append(FixedIntervalMethod(method, frequency))
    
    for currentTimeStep in range(numberOfTimeSteps):
        print currentTimeStep
        Topic.incrementTopicAge(currentTopics)
        model.process(currentTimeStep, currentTopics, currentUsers, **conf)
        for method in analysis: method.call(currentTimeStep, iterationData=(currentTimeStep, model, currentTopics, currentUsers, False, conf))
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
