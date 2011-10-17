'''
Created on Oct 17, 2011

@author: kykamath
'''
class Topic(object):
    def __init__(self, id):
        self.id = id
    def __str__(self): return ' '.join([str(self.id)])
    @staticmethod
    def addNewTopics(currentTopics, noOfTopicsToAdd):
        if not currentTopics: initialId = 0
        else: initialId = currentTopics[-1].id+1
        [currentTopics.append(Topic(initialId+i)) for i in range(noOfTopicsToAdd)]
        
class TrendingTopic(Topic):
    def __init__(self, trendingProbability, *args, **kwargs):
        super(TrendingTopic, self).__init__(*args, **kwargs)
        self.trendingProbability = trendingProbability
    
class User(object):
    pass

class NormalUser(User):
    pass

class Spammer(User):
    pass