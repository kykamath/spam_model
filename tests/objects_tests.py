'''
Created on Oct 17, 2011

@author: kykamath
'''
import unittest
from objects import Topic, TrendingTopic

class TopicTests(unittest.TestCase):
    def test_init(self):
        topic = Topic(10)
        self.assertEqual(10, topic.id)
    def test_generate(self):
        topics = []
        Topic.addNewTopics(topics, 2)
        Topic.addNewTopics(topics, 5)
        self.assertEqual(7, len(topics))
        for i in range(7): self.assertEqual(i, topics[i].id)
        
class TrendingTopicTests(unittest.TestCase):
    def test_init(self):
        topic = TrendingTopic(0.5, 10)
        self.assertEqual(10, topic.id)
        self.assertEqual(0.5, topic.trendingProbability)

if __name__ == '__main__':
    unittest.main()