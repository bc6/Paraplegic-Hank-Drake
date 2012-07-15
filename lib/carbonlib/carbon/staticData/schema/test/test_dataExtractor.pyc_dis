#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\staticData\schema\test\test_dataExtractor.py
if __name__ == '__main__':
    import sys, os
    carbonLibPath = os.path.abspath(os.path.join(__file__, '../../../../../'))
    sys.path.append(carbonLibPath)
import unittest
import carbon.staticData.schema.dataExtractor as dataExtractor

class DataExtractionTest(unittest.TestCase):

    def testSimpleDataExtraction(self):
        schema = {'type': 'int',
         'export': True}
        data = 5
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertEquals(data, extractedData)

    def testSimpleThatIsNotFoundDataExtraction(self):
        schema = {'type': 'int'}
        data = 5
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertNotEquals(data, extractedData)
        self.assertEquals(None, extractedData)

    def testSimpleObjectDataExtraction(self):
        schema = {'type': 'object',
         'attributes': {'a': {'type': 'int',
                              'export': True}}}
        data = {'a': 19}
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertTrue('a' in extractedData)

    def testSimpleDictDataExtraction(self):
        schema = {'type': 'dict',
         'keyTypes': {'type': 'string'},
         'valueTypes': {'type': 'int',
                        'export': True}}
        data = {'a': 19}
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertTrue('a' in extractedData)

    def testSimpleListDataExtraction(self):
        schema = {'type': 'list',
         'itemTypes': {'type': 'int',
                       'export': True}}
        data = [155, 100]
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertEquals(2, len(extractedData))
        for i in range(len(extractedData)):
            self.assertEquals(extractedData[i], data[i])

    def testSimpleEmptyListDataExtraction(self):
        schema = {'type': 'list',
         'itemTypes': {'type': 'int',
                       'export': True}}
        data = []
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertEquals(data, extractedData)

    def testSimpleNoneValueDataExtraction(self):
        schema = {'type': 'string',
         'export': True}
        data = None
        extractedData = dataExtractor.ExtractData(data, schema, {'export': True})
        self.assertEquals(data, extractedData)

    def testMultipleFieldDataExtraction(self):
        schema = {'type': 'object',
         'attributes': {'a': {'type': 'int',
                              'IWantThis': True},
                        'b': {'type': 'vector3'},
                        'c': {'type': 'string',
                              'ButIAlsoWantThis': 5}}}
        data = {'a': 100,
         'b': (100, 100, 100),
         'c': 'whoop I Got This!!'}
        extractedData = dataExtractor.ExtractData(data, schema, {'IWantThis': True,
         'ButIAlsoWantThis': 5,
         'IWillNeverFindThis': 100})
        self.assertEquals(2, len(extractedData))
        self.assertTrue('a' in extractedData)
        self.assertFalse('b' in extractedData)
        self.assertTrue('c' in extractedData)
        self.assertEquals(data['a'], extractedData['a'])
        self.assertEquals(data['c'], extractedData['c'])

    def testFullNodeDeletionInDataExtraction(self):
        schema = {'type': 'object',
         'attributes': {'simpleObject': {'type': 'object',
                                         'attributes': {'verySimpleInt': {'type': 'int'}}},
                        'complexObject': {'type': 'object',
                                          'attributes': {'otherSimpleObject': {'type': 'object',
                                                                               'attributes': {'otherVerySimpleInt': {'type': 'int'}}},
                                                         'yetAnotherSimpleObject': {'type': 'object',
                                                                                    'attributes': {'yetAnotherVerySimpleInt': {'type': 'int',
                                                                                                                               'weWantThis': True}}}}}}}
        data = {'simpleObject': {'verySimpleInt': 10},
         'complexObject': {'otherSimpleObject': {'otherVerySimpleInt': 100},
                           'yetAnotherSimpleObject': {'yetAnotherVerySimpleInt': 1000}}}
        extractedData = dataExtractor.ExtractData(data, schema, {'weWantThis': True})
        self.assertEquals(1, len(extractedData))
        self.assertTrue('complexObject' in extractedData)
        self.assertTrue('yetAnotherSimpleObject' in extractedData['complexObject'])
        self.assertFalse('simpleObject' in extractedData)
        self.assertFalse('otherSimpleObject' in extractedData['complexObject'])
        self.assertEquals(data['complexObject']['yetAnotherSimpleObject'], extractedData['complexObject']['yetAnotherSimpleObject'])


if __name__ == '__main__':
    import sys
    suite = unittest.TestLoader().loadTestsFromTestCase(DataExtractionTest)
    unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)