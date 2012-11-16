from __future__ import division
'''
Created on Nov 11, 2012

@author: chunwei
'''
##################################################
# structure of StyleTree:
# a static linked list:
# * <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# * array:
# * hash     child   brother  imp  count
# * ---------------------------------------
# *  hash = hash(tagname)
# *  child always link to the latest added child 
# *  brother always link to the last brother found
# *  imp is finally calculated value using count
# *#################################################*/
#from type import Node
import math
def getTag(node):
    end = str(node).index('>')
    return str(node)[:end+1]

import re
def getTagName(node):
    t = re.compile("^<[\s]*(\S*)[\s>]")
    res = t.findall(str(node))[0]
    if res:
        return res[0]
    return False

class ElementNode:
    '''
    base tag class
    data structure:
        [
            tagname,
            childtags: [],
            count = 1,
            imp = 0,
        ]
    '''
    def __init__(self, name = ''):
        self._name = name
        self._childStyleNodes = []
        self._count = 1
        self._imp = 0
        self.type = 'elementnode'

    def setName(self, name):
        self._name =  name

    def getName(self):
        return self._name

    def getChildStyleNodes(self):
        return self._childStyleNodes

    def getImp(self):
        return self._imp

    def setImp(self, imp):
        self._imp = imp

    def addDataNode(self, node):
        '''
        add text img a p b 
        '''
        nodenames = [
            'img',
            'IMG',
            'P',
            'p',
            'b',
            'B',
        ]
        datanode = DataNode()
        tagname = getTagName(node)
        if tagname in nodenames:
            datanode.setTagNode(node)
            self.addChildStyleNode(datanode)
        elif datanode.setTextNode(node):
            self.addChildStyleNode(datanode)
        
    def addChildStyleNode(self, node):
        '''
        @ node : StyleNode
        '''
        self._childStyleNodes.append(node)

    def _searchStyleNode(self, stylenodename):
        for node in self.getChildStyleNodes():
            if node.getPreview() == stylenodename:
                return node
        return False

    def incCount(self):
        '''
        count pages that contain node
        '''
        self._count += 1

    def getCount(self):
        return self._count

    def registerStyleNode(self, stylenode):
        node = self._searchStyleNode(stylenode.getPreview())
        if node:
            node.incCount()
            print '.. return node ', node
            return node
        else:
            self.addChildStyleNode(stylenode)
            print '.. return stylenode ', stylenode
            return stylenode

    def __str__(self):
        #print 'element str:'
        res = "[.{%s} " % self.getName()
        for node in self.getChildStyleNodes():
            res += str(node)
            res += " "
        res += "]"
        return res
        
class StyleNode:
    def __init__(self):
        self._preview = ''
        self._imp = 0
        self._count = 1
        self._children = []
        self.type = 'stylenode'

    def generateStyleNode(self, node):
        childnodes = node.children()
        for i in range(len(childnodes)):
            childnode = childnodes.eq(i)
            element = ElementNode(self._getTag(childnode))
            print '.. Element : ',element
            self.addChildElement(element)


    def getPreview(self):
        #return self._preview
        return self.generatePreview()

    def getImp(self):
        return self._imp

    def getCount(self):
        return self._count

    def _setPreview(self, s):
        self._preview = s

    def addChildElement(self, childElement):
        self._children.append(childElement)

    def getChild(self, i):
        return self._children[i]

    def generatePreview(self):
        res = ''
        for child in self.getChildrenElements():
            res += child.getName()
            res += ' '
        #self._setPreview(res)
        return res
            
    def getChildrenElements(self):
        return self._children

    def incCount(self):
        self._count += 1
        for element in self.getChildrenElements():
            element.incCount()

    def setImp(self, imp):
        self._imp  = imp

    def __str__(self):
        #print 'stylenode str:'
        res = '[.' + "{(%s)}"%self.getPreview()
        res += " "
        for element in self.getChildrenElements():
            res += str(element)
        res += ']'
        return res

    def _getTag(self, node):
        end = str(node).index('>')
        return str(node)[:end+1]

from copy import deepcopy as dc
class DataNode(ElementNode):
    '''
    for nodes like b p img a
    '''
    def __init__(self, data = ''):
        ElementNode.__init__(self, hash(data))

    def setTextNode(self, node):
        '''
        text node and save hash
        '''
        _node = dc(node)
        _nodechildren = _node.children()
        for i in range(len(_nodechildren)):
            _node.remove(_nodechildren.eq(i))
        res = str(_node)
        if res.lstrip():
            self.setName (hash(str(_node)))
            return True
        return False

    def setTagNode(self, node):
        '''
        img a p b
        '''
        self.setName(hash(str(node)))

class StyleTree:
    def __init__(self):
        self.body = ElementNode('body')
        #num of sitepages
        self.pageNum = 0

    def calNodeImp(self, element):
        if element.getImp():
            return element.getImp()
        #else
        res = 0
        m = element.getCount()
        if m == 1:
            res = 1
        else:
            for stylenode in element.getChildStyleNodes():
                pi = stylenode.getCount() / self.pageNum
                res -= pi * math.log(m, pi)
        element.setImp(res)
        return res

    def calCompImp(self, node):
        r = 0.1
        if node.getImp():
            return node.getImp()
        #else
        res = 0
        if node.type == 'elementnode':
            res += (1 - r) * self.calNodeImp(node)
            tem = 0
            for stylenode in node.getChildStyleNodes():
                pi = stylenode.getCount() / self.pageNum
                tem += pi * self.calCompImp(stylenode)
            res += r * tem
        elif node.type == 'stylenode':
            children = node.getChildrenElements()
            k = len(children)
            for element in children:
                res += self.calCompImp(element)
            res /= k
        node.setImp(res)
        return res

    def show(self):
        '''
        show structure
        '''
        print self.body


if __name__ == '__main__':
    body = ElementNode('body')
    stylenode = StyleNode()
    p = ElementNode('p')
    b = ElementNode('b')
    stylenode.addChildElement(p)
    stylenode.addChildElement(b)
    print stylenode
    body.registerStyleNode(stylenode)
    q = ElementNode('q')
    c = ElementNode('c')
    stylenode2 = StyleNode()
    stylenode2.addChildElement(q)
    stylenode2.addChildElement(c)
    b.registerStyleNode(stylenode2)
    print 'body', body
