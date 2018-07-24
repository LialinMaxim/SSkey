import unittest
from tests import test_basic


if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromModule(test_basic)
    unittest.TextTestRunner().run(suit)
