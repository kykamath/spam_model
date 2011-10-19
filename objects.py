'''
Created on Oct 17, 2011

@author: kykamath
'''
from collections import defaultdict
import random
from library.classes import GeneralMethods
from settings import stickinessLowerThreshold

topicClasses = range(4)

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
        #Non-modeling attributes.
        self.color = GeneralMethods.getRandomColor()
        
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def incrementTopicAge(currentTopics):
        for topic in currentTopics: topic.age+=1
    @staticmethod
    def addNewTopics(currentTopics, noOfTopicsToAdd):
        if not currentTopics: initialId = 0
        else: initialId = currentTopics[-1].id+1
        [currentTopics.append(Topic(initialId+i)) for i in range(noOfTopicsToAdd)]
        
class User(object):
    def __init__(self, id):
        self.id = id
        self.messagingProbability = 0.1
        self.numberOfTopicsPerMessage = 1
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def addNormalUsers(currentUsers, noOfUsersToAdd, **conf):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
        [currentUsers.append(NormalUser(initialId+i)) for i in range(noOfUsersToAdd)]
    @staticmethod
    def addSpammers(currentUsers, noOfUsersToAdd, **conf):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
        [currentUsers.append(Spammer(initialId+i)) for i in range(noOfUsersToAdd)]
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
    def __init__(self, id):
        super(Spammer, self).__init__(id)
        self.topicClass = None
        self.probabilityOfPickingPopularTopic = 1.0
        self.newTopicProbability = 0.0
        