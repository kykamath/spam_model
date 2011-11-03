'''
Created on Oct 17, 2011

@author: kykamath
'''
from collections import defaultdict
import random
from library.classes import GeneralMethods
from settings import stickinessLowerThreshold, noOfPayloadsPerTopic,\
    noOfPayloadsPerSpammer, noOfGlobalSpammerPayloads, globalSpammerId

topicClasses = range(4)

class PayLoad(object):
    def __init__(self, id, generatorId):
        self.id = str(generatorId)+'_'+str(id)
        self.generatorId = generatorId
        self.isSpam = False
    @staticmethod
    def generatePayloads(generatorId, noOfPayLoadsToGenerate): return [PayLoad(id, generatorId) for id in range(noOfPayLoadsToGenerate)]

class SpamPayLoad(PayLoad):
    def __init__(self, id, spammerId):
        super(SpamPayLoad, self).__init__(id, spammerId)
        self.isSpam = True
    @staticmethod
    def generatePayloads(generatorId, noOfPayLoadsToGenerate): return [SpamPayLoad(id, generatorId) for id in range(noOfPayLoadsToGenerate)]
    
class Topic(object):
    def __init__(self, id):
        self.id = id
        self.totalCount = 0
        self.countDistribution = defaultdict(int)
        self.age = 0
        self.topicClass = random.choice(topicClasses)
        self.decayCoefficient = -3
        if GeneralMethods.trueWith(0.05): self.stickiness = random.uniform(stickinessLowerThreshold, 1.0)
        else: self.stickiness = random.uniform(0.0, 0.1)
        self.payloads = PayLoad.generatePayloads(self.id, noOfPayloadsPerTopic)
        #Non-modeling attributes.
        self.color = GeneralMethods.getRandomColor()
    def getPayLoad(self): return random.choice(self.payloads)
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def incrementTopicAge(currentTopics):
        for topic in currentTopics: topic.age+=1
    @staticmethod
    def addNewTopics(currentTopics, noOfTopicsToAdd):
        if not currentTopics: initialId = 0
        else: initialId = currentTopics[-1].id+1
        [currentTopics.append(Topic(initialId+i)) for i in range(noOfTopicsToAdd)]
        
class Message:
    def __init__(self, id, timeStep, payLoad, topic):
        self.id = id
        self.timeStep = timeStep
        self.payLoad = payLoad
        self.topic = topic
        
class User(object):
    def __init__(self, id):
        self.id = id
        self.messagingProbability = 0.1
        self.numberOfTopicsPerMessage = 1
        self.messagesSent = 0
    def __str__(self): return ' '.join([str(self.id)])
    def generateMessage(self, timeStep, topic):
        self.messagesSent+=1
        return Message(str(self.id)+'_'+str(self.messagesSent), timeStep, topic.getPayLoad(), topic)
    @staticmethod
    def addNormalUsers(currentUsers, noOfUsersToAdd, **conf):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
        [currentUsers.append(NormalUser(initialId+i)) for i in range(noOfUsersToAdd)]
    @staticmethod
    def addSpammers(currentUsers, noOfUsersToAdd, **conf):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
#        for i in range(noOfUsersToAdd):
#            u = Spammer(initialId+i)
#            if 'spammerAttributes' in conf:
#                
#            currentUsers.append(u)
        [currentUsers.append(Spammer(initialId+i, **conf)) for i in range(noOfUsersToAdd)]
    @staticmethod
    def addUsersUsingRatio(currentUsers, noOfUsersToAdd, **conf):
        ratio = conf['ratio']
        if '%0.1f'%(ratio['normal']+ratio['spammer'])!='%0.1f'%1.0: raise Exception('Ratio Should sum to 1.0')
        User.addNormalUsers(currentUsers, int(noOfUsersToAdd*ratio['normal']), **conf)
        User.addSpammers(currentUsers, int(noOfUsersToAdd*ratio['spammer']), **conf)
    
class NormalUser(User):
    def __init__(self, id):
        super(NormalUser, self).__init__(id)
        self.topicClass = random.choice(topicClasses) # Models interest of a user. Ex. User interested in sports, technology.
        self.probabilityOfPickingPopularTopic = 0.40
        self.newTopicProbability = 0.001

class Spammer(User):
    globalPayloads = None
    def __init__(self, id, **conf):
        super(Spammer, self).__init__(id)
        self.topicClass = None
        self.probabilityOfPickingPopularTopic = 0.75
        self.newTopicProbability = 0.0
        self.messagingProbability = conf.get('spammerMessagingProbability', 0.2)
        if conf.get('noOfGlobalSpammerPayloads', False): 
            if not Spammer.globalPayloads: Spammer.globalPayloads = SpamPayLoad.generatePayloads(globalSpammerId, conf.get('noOfGlobalSpammerPayloads', noOfGlobalSpammerPayloads))
            self.payLoads = [random.choice(Spammer.globalPayloads)]
        else: self.payLoads = SpamPayLoad.generatePayloads(id, conf.get('noOfPayloadsPerSpammer', noOfPayloadsPerSpammer))
    def getPayLoad(self): return random.choice(self.payLoads)
    def generateMessage(self, timeStep, topic):
        self.messagesSent+=1
        return Message(str(self.id)+'_'+str(self.messagesSent), timeStep, self.getPayLoad(), topic)
        