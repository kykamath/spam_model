'''
Created on Oct 17, 2011

@author: kykamath
'''
from collections import defaultdict

class Topic(object):
    def __init__(self, id):
        self.id = id
        self.totalCount = 0
        self.countDistribution = defaultdict(int)
        self.age = 0
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def incrementTopicAge(currentTopics):
        for topic in currentTopics: topic.age+=1
    @staticmethod
    def addNewTopics(currentTopics, noOfTopicsToAdd):
        if not currentTopics: initialId = 0
        else: initialId = currentTopics[-1].id+1
        [currentTopics.append(Topic(initialId+i)) for i in range(noOfTopicsToAdd)]
#    @staticmethod
#    def removeOldTopics(currentTopics, noOfTopicsToRemove): 
#        if noOfTopicsToRemove>0:
#            j = 0
#            for i in currentTopics[:]: 
#                currentTopics.remove(i)
#                j+=1
#                if j==noOfTopicsToRemove: break
        
class TrendingTopic(Topic):
    def __init__(self, trendingProbability, *args, **kwargs):
        super(TrendingTopic, self).__init__(*args, **kwargs)
        self.trendingProbability = trendingProbability
    
class User(object):
    def __init__(self, id):
        self.id = id
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def addNewUsers(currentUsers, noOfUsersToAdd):
        if not currentUsers: initialId = 0
        else: initialId = currentUsers[-1].id+1
        [currentUsers.append(User(initialId+i)) for i in range(noOfUsersToAdd)]
    
class NormalUser(User):
    pass

class Spammer(User):
    pass