#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""
Test config module
"""
from ea.libs.FileModels import GenericModel
from ea.libs.PyXmlDict import Dict2Xml as PyDictXml
from ea.libs.PyXmlDict import Xml2Dict as PyXmlDict
import sys
import re

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


r = re.compile(
    u"[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF\u0100-\uD7FF\uE000-\uFDCF\uFDE0-\uFFFD]")


def removeInvalidXML(string):
    """
    Remove invalid XML
    """
    def replacer(m):
        """
        return empty string
        """
        return ""
    return re.sub(r, replacer, string)


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val


class DataModel(GenericModel.GenericModel):
    """
    Data model for test config
    """

    def __init__(self, userName='unknown', timeout="10.0", parameters=[]):
        """
        This class describes the model of one script document,
        and provides a xml <=> python encoder
        The following xml :
        <?xml version="1.0" encoding="utf-8" ?>
            <file>
                <properties">
                    <parameters>
                        <parameter>
                            <name>...</name>
                            <type>...</type>
                            <description>...</description>
                            <value>...</value>
                        </parameter>
                    </parameters>
                </properties>
            </file>
        """
        GenericModel.GenericModel.__init__(self)

        # init xml encoder
        self.codecX2D = PyXmlDict.Xml2Dict()
        self.codecD2X = PyDictXml.Dict2Xml(coding=None)

        # init file properties
        self.properties = {'properties': {
            'parameters': {
                'parameter': [{'type': 'bool',
                               'name': 'DEBUG',
                               'description': '',
                               'value': 'False',
                               'color': '',
                               'scope': 'local'},
                              {'type': 'float',
                               'name': 'TIMEOUT',
                               'description': '',
                               'value': timeout,
                               'color': '',
                               'scope': 'local'}]
            }
        }
        }
        if len(parameters):
            self.properties["properties"]["parameters"]["parameter"] = parameters

    def toXml(self):
        """
        Python data to xml

        @return:
        @rtype:
        """
        try:
            # !!!!!!!!!!!!!!!!!!!!!!!!!!
            self.fixPyXML(
                data=self.properties['properties']['parameters'],
                key='parameter')
            # !!!!!!!!!!!!!!!!!!!!!!!!!!
            xmlDataList = ['<?xml version="1.0" encoding="utf-8" ?>']
            xmlDataList.append('<file>')
            if sys.version_info > (3,):  # python3 support
                xmlDataList.append(
                    bytes2str(
                        self.codecD2X.parseDict(
                            dico=self.properties)))
            else:
                xmlDataList.append(
                    self.codecD2X.parseDict(
                        dico=self.properties))
            xmlDataList.append('</file>')
            ret = '\n'.join(xmlDataList)

            # remove all invalid xml data
            ret = removeInvalidXML(ret)
        except Exception as e:
            self.error("TestConfig > To Xml %s" % str(e))
            ret = None
        return ret

    def fixParameterstoUTF8(self):
        """
        Fix encodage not pretty....
        """
        for param in self.properties['properties']['parameters']['parameter']:
            param['value'] = param['value'].decode("utf-8")
            param['description'] = param['description'].decode("utf-8")
            param['name'] = param['name'].decode("utf-8")

    def onLoad(self, decompressedData):
        """
        Called on data model loading
        """
        # reset properties
        self.properties = {}
        self.testdef = ""
        self.testexec = ""
        decodedStatus = False

        # decode content
        try:
            ret = self.codecX2D.parseXml(xml=decompressedData)
        except Exception as e:
            self.error("TestConfig > Parse Xml %s" % str(e))
        else:
            try:
                properties = ret['file']['properties']
            except Exception as e:
                self.error("TestConfig > extract properties %s" % str(e))
            else:
                try:
                    # if type(properties['parameters']) == str:
                    if isinstance(properties['parameters'], str) or isinstance(
                            properties['parameters'], bytes):  # python3 support
                        properties['parameters'] = {
                            'parameter': [], '@parameter': []}

                    self.fixXML(data=properties['parameters'], key='parameter')
                    if '@parameter' in properties['parameters']:
                        self.fixXML(
                            data=properties['parameters'],
                            key='@parameter')

                    # BEGIN NEW in 19.0.0 : add missing scope parameters
                    for p in properties['inputs-parameters']['parameter']:
                        if "scope" not in p:
                            p["scope"] = "local"
                            p["@scope"] = {}
                    for p in properties['outputs-parameters']['parameter']:
                        if "scope" not in p:
                            p["scope"] = "local"
                            p["@scope"] = {}
                    # END OF NEW
                except Exception as e:
                    self.error("TestConfig >  fix xml %s" % str(e))
                else:
                    try:
                        self.properties = {'properties': properties}
                        if sys.version_info < (3,):  # python3 support
                            self.fixParameterstoUTF8()
                    except Exception as e:
                        self.error("TestConfig >  fix utf8 %s" % str(e))
                    else:
                        decodedStatus = True
        return decodedStatus
