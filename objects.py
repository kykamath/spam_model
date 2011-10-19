'''
Created on Oct 17, 2011

@author: kykamath
'''
from collections import defaultdict
import random
from library.classes import GeneralMethods

topicClasses = range(4)

class Topic(object):
    def __init__(self, id):
        self.id = id
        self.totalCount = 0
        self.countDistribution = defaultdict(int)
        self.age = 0
        self.topicClass = random.choice(topicClasses)
#        if GeneralMethods.trueWith(0.1): self.sticky = True
#        else: self.sticky = False
        if GeneralMethods.trueWith(0.05): self.stickiness = random.uniform(0.6, 1.0)
        else: self.stickiness = random.uniform(0.0, 0.1)
        
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def incrementTopicAge(currentTopics):
        for topic in currentTopics: topic.age+=1
    @staticmethod
    def addNewTopics(currentTopics, noOfTopicsToAdd):
        if not currentTopics: initialId = 0
        else: initialId = currentTopics[-1].id+1
        [currentTopics.append(Topic(initialId+i)) for i in range(noOfTopicsToAdd)]
        
#class TrendingTopic(Topic):
#    def __init__(self, trendingProbability, *args, **kwargs):
#        super(TrendingTopic, self).__init__(*args, **kwargs)
#        self.trendingProbability = trendingProbability
    
class User(object):
    def __init__(self, id):
        self.id = id
        self.topicClass = random.choice(topicClasses)
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def addNewUsers(currentUsers, noOfUsersToAdd, **conf):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
        [currentUsers.append(User(initialId+i)) for i in range(noOfUsersToAdd)]
    
class NormalUser(User):
    pass

class Spammer(User):
    pass