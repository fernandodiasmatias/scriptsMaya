# swapGroomGeoToGeo #########################################################################
#																							#
# the operation is summarized in selecting two geometries one with Yeti Groom and			#
# another one with identical geometry but without yeti Gromm and running the script.		#
#																							#
# The main motivation for the script is to facilitate the grooming process for assets		#
# that needed a simulation on their geometry and need to have original yeti groom restored	#
#																							#
#script by Fernando Dias Matias																#
#																							#
#############################################################################################

import pymel.core as pmc
import maya.cmds as cmds
import sys

import pymel.core as pmc
import maya.cmds as cmds
from sys import exit

class swapGroomGeoToGeo():

    def __init__(self):

        self.selectList = pmc.ls(sl=True)
        self.originalShape = None
        self.geoShape = None
        self.geoShape_reference = None
        self.organizeObj()
        self.listCollisionGRM = []
        
        
    def validateItem(self):
        valid = []
        hasYeti = []

        if len(self.selectList) !=2 or self.selectList == None :
            pmc.warning("Select at least 2 objects to link")
            return False
        
        item1 = pmc.listRelatives(self.selectList[0], shapes=True)[0]
        item2 = pmc.listRelatives(self.selectList[1], shapes=True)[0]
        identical = item1.numFaces() == item2.numFaces()
       
        for item in self.selectList:
            hasYeti.append(pmc.hasAttr(item,"yetiSubdivision",checkShape=True))
            if pmc.nodeType(item) == "transform":
                if pmc.listRelatives(item, shapes=True) != None:
                    valid.append(True)
                else:
                    pmc.warning("No shape found on: " + item)
                    valid.append(False)        
            else:
                pmc.warning("Please select a transform node")
                valid.append(False)
        message = (valid[0] and valid[1]) and (hasYeti[0] or hasYeti[1]) and (identical)

        return message


    def organizeObj(self):
        for item in self.selectList:
            item = str(pmc.listRelatives(item,s=True)[0])
            geoReference = cmds.connectionInfo(item +'.referenceObject',sourceFromDestination=True)
            if geoReference != '':
                self.originalShape = item
                self.geoShape_reference = str(geoReference.split('.')[0])
            else:
                self.geoShape = item

    def returnGeoShapeByTypeConnection(self, shape,typeConnection):
        connectedShape = cmds.listConnections(shape + '.' + typeConnection, sh=True)
        return connectedShape

    def connectObj(self):
        pmc.connectAttr( self.geoShape_reference + ".message", self.geoShape + ".referenceObject", f=True)
        connected = cmds.isConnected(self.geoShape_reference + ".message", self.geoShape + ".referenceObject")
        return connected

    def disconnectObj(self):
        if cmds.isConnected(self.geoShape_reference + ".message", self.originalShape + ".referenceObject") == True:
            pmc.disconnectAttr( self.geoShape_reference + ".message", self.originalShape + ".referenceObject")
            disconnected = not cmds.isConnected(self.geoShape_reference + ".message", self.originalShape + ".referenceObject")
            return disconnected
            
    def swapGeometryOnGeoCollision(self):
        if len(self.listCollisionGRM) != 0:
            for CollisionGRM in self.listCollisionGRM:
                pmc.disconnectAttr( self.originalShape + ".worldMesh", CollisionGRM,)
                pmc.connectAttr( self.geoShape + ".worldMesh" , CollisionGRM, f=True)


    def swapGeometryOnGroom(self):
        try:
            pmc.mel.eval('pgYetiSwapGeometry("'+ self.originalShape +'","'+ self.geoShape +'")')
            pmc.setAttr(self.geoShape+".yetiSubdivision",1)
        except:
            pmc.warning("No Yeti Groom found on: " + self.originalShape)

    def listCollisionOnGRM(self):
        try:
            self.listCollisionGRM = cmds.connectionInfo(self.originalShape + ".worldMesh",dfs=True)
            return self.listCollisionGRM
        except:
            pmc.warning("No Yeti Groom found on: " + self.originalShape)

swGrm = swapGroomGeoToGeo()

if swGrm.validateItem():
    if swGrm.disconnectObj():
        pmc.warning("Disconnected: " + swGrm.originalShape)
        if swGrm.connectObj():
            pmc.warning("Connection successful")
            swGrm.swapGeometryOnGeoCollision()
            swGrm.swapGeometryOnGroom()
        else:
            pmc.warning("Connection failed")
    else:
        pmc.warning("Disconnection failed")
else:
    pmc.warning("Try again by selecting 2 objects, one with Yeti Groom and another one with identical geometry but without yeti Gromm")
