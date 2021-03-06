#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

# prefer to use this library for huge xml file support
import sys
etree = None
try:
    from lxml import etree
except ImportError:
    pass

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import cElementTree as ET


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val


class Xml2Dict(object):
    """
    Xml to Dict
    """

    def __init__(self, coding='UTF-8'):
        """
        Convert xml string to python dict

        @param coding: expected value in UTF-8, ISO, etc ...
        @type coding: string
        """
        self.coding = coding

    def __getNbChildren(self, node):
        """
        Returns the number of child

        @param node: element
        @type node: ET

        @return: number of child
        @rtype: Integer
        """
        size = len(node.getchildren())
        return size

    def __makeDict(self, nodeName, nodeAttrib, nodeValue):
        """
        Contructs a python dictionnary
        <test id="1">toto</test> => {'test': 'toto', '@test': {'id': '1'} }

        @param nodeName: node name
        @type nodeName: string

        @param nodeAttrib: node attributes
        @type nodeAttrib: dict

        @param nodeValue: node value
        @type nodeValue: string

        @return: node converted
        @rtype: dict
        """
        ret = {}
        if sys.version_info > (3,):
            nodeValue = bytes2str(nodeValue)
        ret[nodeName] = nodeValue
        ret["@%s" % nodeName] = nodeAttrib
        return ret

    def __makeList(self, dico, nodeName, nodeAttrib, nodeValue):
        """
        Contructs python list

        @param dico: dictionnary
        @type dico: dict

        @param nodeName: node name
        @type nodeName: string

        @param nodeAttrib: node attributes
        @type nodeAttrib: dict

        @param nodeValue: node value
        @type nodeValue: string
        """
        if sys.version_info > (3,):
            nodeValue = bytes2str(nodeValue)

        if not isinstance(dico[nodeName], list):
            dico[nodeName] = [dico[nodeName]]
        rslt = self.__makeDict(nodeName=nodeName, nodeAttrib=nodeAttrib,
                               nodeValue=nodeValue)
        dico[nodeName].append(rslt[nodeName])
        # attribs
        if not isinstance(dico["@%s" % nodeName], list):
            dico["@%s" % nodeName] = [dico["@%s" % nodeName]]
        dico["@%s" % nodeName].append(nodeAttrib)

    def __parseNode(self, node):
        """
        Parses the given node as an argument

        @param node: element
        @type node: ET

        @return:
        @rtype: dict
        """
        ret = {}
        # iter of all children
        for child in node.getchildren():
            # retrieve tag, attrib and number of child
            ctag = child.tag  # node name
            cattrib = dict(child.attrib)
            nbChild = self.__getNbChildren(node=child)
            if nbChild == 0:
                # child is null the retrieve the value of the node
                ctext = child.text
                if ctext is None:
                    ctext = ""
                ctext = ctext.encode(self.coding)
                # if node name already exists then contructs list
                if ctag in ret:
                    self.__makeList(
                        dico=ret,
                        nodeName=ctag,
                        nodeAttrib=cattrib,
                        nodeValue=ctext)
                else:
                    # constructs dictionnary
                    rslt = self.__makeDict(
                        nodeName=ctag, nodeAttrib=cattrib, nodeValue=ctext)
                    ret.update(rslt)
            else:
                # child > 0 so recursive call
                if ctag in ret:
                    self.__makeList(
                        dico=ret,
                        nodeName=ctag,
                        nodeAttrib=cattrib,
                        nodeValue=self.__parseNode(
                            node=child))
                else:
                    rslt = self.__makeDict(
                        nodeName=ctag,
                        nodeAttrib=cattrib,
                        nodeValue=self.__parseNode(
                            node=child))
                    ret.update(rslt)
        return ret

    def parseXml(self, xml, huge_tree=False):
        """
        Converts XML to Dict

        @param xml: XML message to convert
        @type xml: string

        @return: dictionnary
        @rtype: dict
        """
        ret = None
        if etree is None:
            root = ET.fromstring(xml)
        else:
            parser = etree.XMLParser(huge_tree=huge_tree)
            root = etree.fromstring(xml, parser)

        nbChild = self.__getNbChildren(node=root)
        if nbChild > 0:
            ret = self.__makeDict(nodeName=root.tag, nodeAttrib=dict(root.attrib),
                                  nodeValue=self.__parseNode(node=root))
        else:
            rtext = root.text.encode(self.coding)
            if rtext is None:
                rtext = ""
            rtext = rtext.encode(self.coding)
            ret = self.__makeDict(nodeName=root.tag, nodeAttrib=dict(root.attrib),
                                  nodeValue=rtext)
        return ret
