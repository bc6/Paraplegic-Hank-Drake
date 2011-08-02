import collections
import weakref
import functools
import os
import time
import inspect
import unittest
from catmaConfig import MODIFIER_BASE, MODIFIER_MULTIPLY, MODIFIER_ADD
from axiom import BaseType, Int, Float, Bool, String, Enumerate, AxiomError, Value
import axiom2
UnitTestFolder = 'UnitTestFolder'
UnitTestFolderID = 9999999

class TestAxiom(unittest.TestCase):
    catmaSvc = None
    ax = None
    testAxiom = None

    def setUp(self):
        pass



    def tearDown(self):
        if self.ax:
            self.ax.EndUnitTest()
        if self.catmaSvc:
            self.ax = self.catmaSvc.GetAX2()
            for test in self.testAxiom._tests:
                test.SetAxiom(self.catmaSvc, self.testAxiom)




    def SetAxiom(self, catmaSvc, testAxiom):
        if catmaSvc:
            self.catmaSvc = catmaSvc
            self.ax = catmaSvc.GetAX2()
            self.testAxiom = testAxiom



    def testAddMemberFunction(self):
        newTypeName = 'UnitTestType1'
        typeDef = self.ax.CreateType(newTypeName, standalone=False)
        attrName = 'hardProtection'
        typeDef.AddMember('Float hardProtection = 0')
        self.assert_(attrName in typeDef._members)
        self.failUnlessRaises(RuntimeError, typeDef.AddMember, 'float attrName1 = 0')
        self.failUnlessRaises(RuntimeError, typeDef.AddMember, 'float = 0')
        self.failUnlessRaises(RuntimeError, typeDef.AddMember, 'Float attrName1 = ')



    def testHasClassMemberFunction(self):
        newTypeName = 'TestType'
        typeDef = self.ax.CreateType(newTypeName, standalone=False)
        typeDef.AddMember('Float hardProtection = 0')
        self.assert_(not typeDef.HasClassMember())
        newTypeName = 'UnitTestType1'
        typeDef = self.ax.CreateType(newTypeName, standalone=False)
        typeDef.AddMember('UnitTestType1 classTypeMember')
        self.assert_(typeDef.HasClassMember())



    def testPopulateValueContainerFunction(self):
        pathNode = self.ax.GetRootNode()
        testValueContainer = axiom2.ValueContainer(None, axiom2.HIERARCHICAL_VALUE_CONTAINER, '', pathNode)
        newTypeName = 'TestType2'
        typeDef = self.ax.CreateType(newTypeName, standalone=False)
        typeDef.AddMember('Float hardProtection = 0')
        self.failUnlessRaises(TypeError, typeDef.PopulateValueContainer, testValueContainer, '')
        attrName = 'hardProtection'
        findAttrValue = testValueContainer.FindValueOrContainer(attrName, True)
        self.assert_(findAttrValue == None)



    def testGetAttributeTypeInstanceFunction(self):
        newTypeName = 'TestType3'
        typeDef = self.ax.CreateType(newTypeName, standalone=False)
        typeDef.AddMember('Float hardProtection = 0')
        self.assert_(typeDef.GetAttributeTypeInfo(['hardProtection'])['typeInstance'] == typeDef._members['hardProtection'])
        self.assert_(typeDef.GetAttributeTypeInfo(['hardProtectionXXX']) == None)
        self.assert_(typeDef.GetAttributeTypeInfo(['hardProtection.0.att']) == None)
        self.failUnlessRaises(RuntimeError, typeDef.GetAttributeTypeInfo, ['hardProtection', 'attr'])



    def testAddChildFunction(self):
        rootNode = self.ax.GetRootNode()
        if rootNode:
            pathList = 'Outer.Inner'
            folderID = None
            classes = ['DustVIC']
            isType = True
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            folderID = 100001
            classes = None
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            classes = ['DustVIC']
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = ''
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = None
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = '.Inner'
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = 'Outer'
            classes = ['Float']
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = 'TypeOuter'
            classes = ['DustVIC']
            self.assert_(rootNode.AddChild(pathList, folderID, classes, '', isType) == rootNode._subNodes[pathList])
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = 'TypeOuter.Inner'
            self.failUnlessRaises(RuntimeError, rootNode.AddChild, pathList, folderID, classes, '', isType)
            pathList = 'NontypeOuter'
            isType = False
            classes = ['DustVIC']
            self.assert_(rootNode.AddChild(pathList, folderID, classes, '', isType) == rootNode._subNodes[pathList])
            pathList = 'NontypeOuter.Inner'
            self.assert_(rootNode.AddChild(pathList, folderID, classes, '', isType) == rootNode._subNodes['NontypeOuter']._subNodes['Inner'])



    def testGetChildFunction(self):
        rootNode = self.ax.GetRootNode()
        pathList = 'TypeOuterNot'
        self.failUnlessRaises(RuntimeError, rootNode.GetChild, pathList)
        pathList = 'TypeOuter'
        classes = ['DustVIC']
        folderID = 100001
        isType = True
        rootNode.AddChild(pathList, folderID, classes, '', isType)
        self.assert_(rootNode.GetChild(pathList) == rootNode._subNodes[pathList])
        pathList = 'NontypeOuter'
        isType = False
        classes = ['DustVIC']
        rootNode.AddChild(pathList, folderID, classes, '', isType)
        pathList = 'NontypeOuter.Inner'
        rootNode.AddChild(pathList, folderID, classes, '', isType)
        self.assert_(rootNode.GetChild(pathList) == rootNode._subNodes['NontypeOuter']._subNodes['Inner'])
        pathList = ''
        self.assert_(rootNode.GetChild(pathList) == rootNode)



    def testFolderNodeEditValueFunction(self):
        rootNode = self.ax.GetRootNode()
        if rootNode:
            pathList = 'NontypeOuter2'
            folderID = 100003
            classes = ['DustVIC']
            isType = False
            newNode = rootNode.AddChild(pathList, folderID, classes, '', isType)
            attrName = 'mVICProp.maxShield'
            newValue = 100
            modifier = MODIFIER_BASE
            newAction = axiom2.VALUE_INIT
            newValueObj = newNode.EditValue(attrName, newValue, modifier, newAction)
            self.assert_(newValueObj.value == newValue)
            attrName = 'attrNotExist'
            self.failUnlessRaises(RuntimeError, newNode.EditValue, attrName, newValue, modifier, newAction)



    def testCreateTypeFunction(self):
        newTypeName = 'UnitTestDustGameProperty'
        self.assert_(self.ax.CreateType(newTypeName, standalone=False) == self.ax._typeDefs[newTypeName])
        self.failUnlessRaises(RuntimeError, self.ax.CreateType, newTypeName)
        newTypeName = ''
        self.failUnlessRaises(RuntimeError, self.ax.CreateType, newTypeName)
        newTypeName = 'UnitTestDustGameProperty2'
        self.failUnlessRaises(RuntimeError, self.ax.CreateType, newTypeName, int)



    def testGetTypeDefsFunction(self):
        newTypeName = 'UnitTestType2'
        typeDef = self.ax.CreateType(newTypeName, standalone=True)
        self.assert_(self.ax._typeDefs == self.ax.GetTypeDefs())



    def testGetTypeFunction(self):
        newTypeName = 'UnitTestType3'
        typeDef = self.ax.CreateType(newTypeName, standalone=True)
        self.assert_(self.ax._typeDefs[newTypeName] == self.ax.GetType(newTypeName))
        errorTypeName = ''
        self.failUnlessRaises(AxiomError, self.ax.GetType, errorTypeName)
        errorTypeName = 'errorTypeName'
        self.failUnlessRaises(AxiomError, self.ax.GetType, errorTypeName)



    def testCreateFolderNodeFunction(self):
        newPathNode = 'path1'
        self.assert_(self.ax.CreateFolderNode(newPathNode) == self.ax._folderNodes[newPathNode])
        self.failUnlessRaises(RuntimeError, self.ax.CreateFolderNode, newPathNode)



    def testGetRootNodeFunction(self):
        rootNode = ''
        self.assert_(self.ax.GetRootNode() == self.ax._folderNodes[rootNode])



    def testGetAvailableClassNamesFunction(self):
        newTypeName = 'UnitTestType4'
        typeDef = self.ax.CreateType(newTypeName, standalone=True)
        classNames = self.ax.GetAvailableClassNames()
        self.assert_(newTypeName in classNames)



    def testAddFolderFunction(self):
        if self.ax:
            self.ax.AddFolder(UnitTestFolder, UnitTestFolderID, 'Entity', '', False)
            pathList = UnitTestFolder + '.AddFolder'
            folderID = None
            classes = ['DustVIC']
            isType = True
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            folderID = 100011
            classes = None
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            classes = ['DustVIC']
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = ''
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = None
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = '.Inner'
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = 'AddFolderOuter'
            classes = 'Float'
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = UnitTestFolder + '.AddFolderTypeOuter'
            classes = 'DustVIC'
            self.ax.AddFolder(pathList, folderID, classes, '', isType)
            self.assert_(self.ax.GetNodeByPath(pathList) is not None)
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = UnitTestFolder + '.AddFolderTypeOuter.Inner'
            self.failUnlessRaises(RuntimeError, self.ax.AddFolder, pathList, folderID, classes, '', isType)
            pathList = UnitTestFolder + '.AddFolderNontypeOuter'
            isType = False
            classes = 'DustVIC'
            folderID = 100012
            self.ax.AddFolder(pathList, folderID, classes, '', isType)
            self.assert_(self.ax.GetNodeByPath(pathList) is not None)
            pathList = UnitTestFolder + '.AddFolderNontypeOuter.Inner2'
            folderID = 100013
            self.ax.AddFolder(pathList, folderID, classes, '', isType)
            self.assert_(self.ax.GetNodeByPath(pathList) is not None)



    def testRemoveFolderFunction(self):
        self.ax.AddFolder(UnitTestFolder, UnitTestFolderID, 'Entity', '', False)
        pathList = UnitTestFolder + '.RemoveFolder'
        folderID = 1111111
        classes = 'DustVIC'
        isType = False
        self.ax.AddFolder(pathList, folderID, classes, '', isType)
        self.assert_(self.ax.GetNodeByPath(pathList) is not None)
        pathList = UnitTestFolder + '.RemoveFolder'
        self.ax.RemoveFolder(pathList)
        self.failUnlessRaises(RuntimeError, self.ax.GetNodeByPath, pathList)
        pathList = UnitTestFolder + '.RemoveFolder.InnerFolder'
        self.failUnlessRaises(RuntimeError, self.ax.GetNodeByPath, pathList)



    def testAxiomEditValueFunction(self):
        self.ax.AddFolder(UnitTestFolder, UnitTestFolderID, 'Entity', '', False)
        pathList = UnitTestFolder + '.EditValueFolder'
        folderID = 12000
        classes = 'DustVIC'
        isType = False
        attrName = 'mVICProp.maxShield'
        value = 100
        modifier = MODIFIER_BASE
        self.ax.AddFolder(pathList, folderID, classes, '', isType)
        self.assert_(self.ax.GetNodeByPath(pathList) is not None)
        pathList = 'errorPath'
        self.failUnlessRaises(RuntimeError, self.ax.EditValue, pathList, attrName, value, modifier, axiom2.VALUE_INIT)
        path = None
        self.failUnlessRaises(RuntimeError, self.ax.EditValue, pathList, attrName, value, modifier, axiom2.VALUE_INIT)
        pathList = UnitTestFolder + '.EditValueFolder'
        self.ax.EditValue(pathList, attrName, value, modifier, axiom2.VALUE_INIT)
        folderNode = self.ax.GetNodeByPath(pathList)
        valueCon = folderNode.GetValueContainer()
        allvalues = []
        findValue = None
        valueCon.GetAllValues(allvalues, True, True)
        for (attr, val,) in allvalues:
            if attr == attrName:
                findValue = val
                break

        self.assert_(findValue is not None and findValue.calculated == value)



    def testAxiomEditSetFunction(self):
        self.ax.AddFolder(UnitTestFolder, UnitTestFolderID, 'Entity', '', False)
        folderPath = UnitTestFolder + '.EditSet'
        folderID = 17000
        classes = 'ConsoleCommand'
        isType = False
        self.ax.AddFolder(folderPath, folderID, classes, '', isType)
        addedFolderNode = self.ax.GetNodeByPath(folderPath)
        self.assert_(addedFolderNode is not None)
        attrName = 'mCommands'
        elementName = 'elementString'
        operation = axiom2.SET_APPEND
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, 'errorPath', attrName, elementName, operation)
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, None, attrName, elementName, operation)
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, folderPath, None, elementName, operation)
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, folderPath, attrName, None, operation)
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, folderPath, attrName, elementName, None)
        attrName = 'mCommandsError'
        self.failUnlessRaises(RuntimeError, self.ax.EditSet, folderPath, attrName, elementName, operation)
        attrName = 'mCommands'
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        newAttrName = attrName + '.' + elementName
        value = addedFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value.calculated is None)
        operation = axiom2.SET_DELETE
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        value = addedFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value is None)
        operation = axiom2.SET_CLEAR
        attrName = 'mCommands'
        elementName = 'whatEverElementName'
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        attrName = 'mDebugProperty.arrayFloat'
        elementName = 'elementFloat'
        newAttrName = attrName + '.' + elementName
        value = addedFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value is None)
        childFolderPath = folderPath + '.ChildEditSet'
        folderID = 17001
        classes = 'ConsoleCommand'
        isType = False
        self.ax.AddFolder(childFolderPath, folderID, classes, '', isType)
        addedChildFolderNode = self.ax.GetNodeByPath(folderPath)
        self.assert_(addedChildFolderNode is not None)
        attrName = 'mCommands'
        elementName = 'elementString'
        operation = axiom2.SET_APPEND
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        newAttrName = attrName + '.' + elementName
        value = addedChildFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value.calculated is None)
        attrName = 'mCommands'
        elementName = 'elementString'
        newAttrName = attrName + '.' + elementName
        operation = axiom2.SET_DELETE
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        value = addedChildFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value is None)
        attrName = 'mCommands'
        elementName = 'elementString'
        newAttrName = attrName + '.' + elementName
        value = addedChildFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value is None)
        operation = axiom2.SET_CLEAR
        attrName = 'mCommands'
        elementName = 'WhatEverElementString'
        self.ax.EditSet(folderPath, attrName, elementName, operation)
        attrName = 'mCommands'
        elementName = 'elementString'
        newAttrName = attrName + '.' + elementName
        value = addedChildFolderNode.FindValueOrContainer(newAttrName, True)
        self.assert_(value is None)



    def testAxiomMoveFolderNodeFunction(self):
        self.ax.AddFolder(UnitTestFolder, UnitTestFolderID, 'Entity', '', False)
        folderPath = UnitTestFolder + '.MoveFolderNodeNonType'
        folderID = 12000
        classes = 'DustVIC'
        isType = False
        self.ax.AddFolder(folderPath, folderID, classes, '', isType)
        addedFolderNode = self.ax.GetNodeByPath(folderPath)
        self.assert_(addedFolderNode is not None)
        newValueObj = addedFolderNode.EditValue('mVICProp.maxShield', 100, MODIFIER_BASE, axiom2.VALUE_INIT)
        self.assert_(newValueObj.calculated == 100)
        childFolderPath = folderPath + '.ChildTypeFolder'
        folderID = 12001
        classes = 'DustVIC'
        isType = True
        self.ax.AddFolder(childFolderPath, folderID, classes, '', isType)
        addedFolderNode = self.ax.GetNodeByPath(childFolderPath)
        self.assert_(addedFolderNode is not None)
        newValueObj = addedFolderNode.EditValue('mVICProp.maxShield', 10, MODIFIER_ADD, axiom2.VALUE_ADD)
        self.assert_(newValueObj.calculated == 110)
        oldFolderPath = childFolderPath
        newFolderPath = childFolderPath
        self.failUnlessRaises(RuntimeError, self.ax.MoveFolderNode, oldFolderPath, newFolderPath)
        oldFolderPath = folderPath
        newFolderPath = childFolderPath
        self.failUnlessRaises(RuntimeError, self.ax.MoveFolderNode, oldFolderPath, newFolderPath)
        folderPath = UnitTestFolder + '.MoveFolderNodeType'
        folderID = 12002
        classes = 'DustVIC'
        isType = True
        self.ax.AddFolder(folderPath, folderID, classes, '', isType)
        addedFolderNode = self.ax.GetNodeByPath(folderPath)
        self.assert_(addedFolderNode is not None)
        newValueObj = addedFolderNode.EditValue('mVICProp.maxShield', 300, MODIFIER_BASE, axiom2.VALUE_INIT)
        self.assert_(newValueObj.calculated == 300)
        oldFolderPath = childFolderPath
        newFolderPath = folderPath
        self.failUnlessRaises(RuntimeError, self.ax.MoveFolderNode, oldFolderPath, newFolderPath)
        olderFolderPath = UnitTestFolder + '.MoveFolderNodeType'
        newFolderPath = UnitTestFolder + '.MoveFolderNodeNonType'
        self.ax.MoveFolderNode(olderFolderPath, newFolderPath)
        self.failUnlessRaises(RuntimeError, self.ax.GetNodeByPath, olderFolderPath)
        newFolderPath = newFolderPath + '.MoveFolderNodeType'
        newFolderNode = self.ax.GetNodeByPath(newFolderPath)
        self.assert_(newFolderNode is not None)
        findValue = newFolderNode.FindValueOrContainer('mVICProp.maxShield', True)
        self.assert_(findValue.calculated == 300)
        newValueObj = newFolderNode.EditValue('mVICProp.maxShield', 300, MODIFIER_ADD, axiom2.VALUE_EDIT)
        self.assert_(newValueObj.calculated == 400)



if __name__ == '__main__':
    unittest.main()

