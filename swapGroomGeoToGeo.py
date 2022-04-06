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

def validateObj(selectList):
    message = []
    if len(selectList) !=2 or selectList == None :
        pmc.warning("Select at least 2 objects to link")
        return False

    for item in selectList:
        if pmc.nodeType(item) == "transform":
            if pmc.listRelatives(item, shapes=True) == None:
                pmc.warning("No shape found on: " + item)
                message.append(False)
            else:
                message.append(True)
        else:
            pmc.warning("Please select a transform node")
            message.append(False)
    print(str(message[0]) + " | " + str(message[1]))
    return message[0] and message[1]

def organizeObj(selectList):
    for item in selectList:
        item = str(pmc.listRelatives(item,s=True)[0])
        geoReference = cmds.connectionInfo(item +'.referenceObject',sourceFromDestination=True)
        if geoReference != '':
            originalShape = item
            geoShape_reference = str(geoReference.split('.')[0])
            pmc.setAttr(geoShape_reference+".yetiSubdivision",1)
        else:
            geoShape = item
    return originalShape, geoShape, geoShape_reference

def returnGeoShapeByTypeConnection(shape,typeConnection):
    connectedShape = cmds.listConnections(shape + '.' + typeConnection, sh=True)
    return connectedShape

def connectObj(geoShape_reference,geoShape):
    pmc.connectAttr( geoShape_reference + ".message", geoShape + ".referenceObject", f=True)
    return cmds.isConnected(geoShape_reference + ".message", geoShape + ".referenceObject")

def disconnectObj(geoShape_reference,geoShape):
    if cmds.isConnected(geoShape_reference + ".message", geoShape + ".referenceObject") == True:
        pmc.disconnectAttr( geoShape_reference + ".message", geoShape + ".referenceObject")
        return cmds.isConnected(geoShape_reference + ".message", geoShape + ".referenceObject")

def swapGeometryOnGroom(originalShape,geoShape):
    pmc.mel.eval('pgYetiSwapGeometry("'+ originalShape +'","'+ geoShape +'")')

        
def swapGeometryOnGeoCollision(originalShape,geoShape):
    listCollisionGRM = cmds.connectionInfo(originalShape + ".worldMesh",dfs=True)
    if len(listCollisionGRM) != 0:
        for CollisionGRM in listCollisionGRM:
            pmc.disconnectAttr( originalShape + ".worldMesh", CollisionGRM,)
            pmc.connectAttr( geoShape + ".worldMesh" , CollisionGRM, f=True)
            

selectList = cmds.ls(sl=1, sn=True)

if validateObj(selectList):
    originalShape, geoShape, geoShape_reference = organizeObj(selectList)
    if not disconnectObj(geoShape_reference,originalShape):
        pmc.warning("Disconnected: " + originalShape)
        if connectObj(geoShape_reference,geoShape):
            pmc.warning("Connection successful")
            swapGeometryOnGeoCollision(originalShape,geoShape)
            swapGeometryOnGroom(originalShape ,geoShape)
        else:
            pmc.warning("Connection failed")
    else:
        pmc.warning("Disconnection failed")
else:
    pmc.warning("Try again by selecting 2 objects")
