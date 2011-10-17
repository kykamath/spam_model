'''
Spam models.

Created on Oct 17, 2011

@author: kykamath
'''
from library.classes import FixedIntervalMethod
from objects import Topic

UNIFORM_MODEL = 'uniform_model'
#GENERATE_TOPICS_METHOD = 'generate_topics_method'

class Model(object):
    def __init__(self, id):
        self.id = id
        self.addNewTopics = Topic.addNewTopics
#        self.currentTopics = []
#        self.generateTopicsMethod = Model.generateTopics
#    @staticmethod
#    def addNewTopics(currentTopics, numberOfTopicsToGenerate):
#        print 'adding new topics'
#    @staticmethod
#    def 
    
def run(model, numberOfTimeSteps, topicAddingFrequency, noOfTopicsToAdd):
    currentTopics = []
    addNewTopics = FixedIntervalMethod(model.addNewTopics, topicAddingFrequency)
    model.addNewTopics(currentTopics, noOfTopicsToAdd)
    for currentTimeStep in range(numberOfTimeSteps):
        print currentTimeStep, len(currentTopics)
        addNewTopics.call(currentTimeStep, currentTopics=currentTopics, noOfTopicsToAdd=noOfTopicsToAdd)
    
#class UniformModel(Model):
#    def __init__(self, **kwargs):
#        super(UniformModel, self).__init__(UNIFORM_MODEL)
#        self.topicGeneratorMethod = kwargs() 


if __name__ == '__main__':
    conf = { 'model': Model(1), 'numberOfTimeSteps': 100,
             'topicAddingFrequency': 10, 'noOfTopicsToAdd': 5
            
            }
    run(**conf)