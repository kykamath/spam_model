'''
Created on Oct 17, 2011

@author: kykamath
'''
import unittest
from models import Model

class ModelTests(unittest.TestCase):
    def test_init(self):
        model = Model(10)
        self.assertEqual(10, model.id)
        model.topicGenerator()
        
if __name__ == '__main__':
    unittest.main()