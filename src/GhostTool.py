import maya.cmds as mc
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget,QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QAbstractItemView, QColorDialog
from PySide2.QtGui import QColor, QPainter, QBrush

def GetCurrentFrame():
    return int(mc.currentTime(q=True))#query

class Ghost:
    def __init__ (self):
        self.srcMeshes = set()#a set only holds unique elemts no duplicates like list
        self.ghostGrp = "ghost_grp"
        self.frameAttr = "frame"
        self.srcAttr = "src"
        self.color = [0,0,0]

        self.InitIfGhostGrpNotExist()

    def UpdateGhostColors(self, color: QColor):
        ghosts = mc.listRelatives(self.ghostGrp, c=True)
        self.color[0] = color.redF()
        self.color[1] = color.greenF()
        self.color[2] = color.blueF()
        
        for ghost in ghosts:
            mat = self.GetMaterialNameForGhost
            mc.setAttr(mat+".color", color.redF(), color.greenF(), color.blueF(),type = "doubles3" )

    def InitIfGhostGrpNotExist(self):
        if mc.objExists(self.ghostGrp):
            storedSrcMeshes = mc.getAttr(self.ghostGrp + "." + self.srcAttr)
            if storedSrcMeshes:
                self.srcMeshes = set(storedSrcMeshes.split(","))
            return
        
        mc.createNode("transform", n = self.ghostGrp)
        mc.addAttr(self.ghostGrp, ln = self.srcAttr, dt="string")
        
    def SetSelectedAsSrcMesh(self):
        selection = mc.ls(sl=True)
        self.srcMeshes.clear()#remove all elemts in the set
        for selected in selection:
            shapes = mc.listRelatives(selected, s = True)#find all shapes of the selected objects
            for s in shapes:
                if mc.objectType(s) == "mesh": # the object is a mesh
                    self.srcMeshes.add(selected) #add the mesh to our set

        mc.setAttr(self.ghostGrp + "." + self.srcAttr, ",".join(self.srcMeshes),type = "string") #", + .join" creates each element in to a string

    def addGhost(self):
        for srcMesh in self.srcMeshes:
            currentFrame = GetCurrentFrame()
            ghostName = srcMesh + "_" + str(currentFrame)
            if mc.objExists(ghostName):
                mc.delete(ghostName)
        
            mc.duplicate(srcMesh, n = ghostName)
            mc.parent(ghostName, self.ghostGrp)
            mc.addAttr(ghostName, ln = self.frameAttr, dv = currentFrame)#default value

            matName = self.GetMaterialNameForGhost(ghostName)#figure out the name for the material
            if not mc.objExists(matName): #check if material not exist
                mc.shadingNode("lambert", asShader = True, name = matName)#creat teh lambert mat if not exist

            sgName = self.GetShadingEnginForGhost(ghostName) #figure out the name of the shading engeine
            if not mc.objExists(sgName): #check if the shading engine exist
                mc.sets(name = sgName, renderable = True, empty = True) #creat teh shading if not exist

            mc.connectAttr(matName + ".outColor", sgName + ".surfaceShader", force = True)# connect the material to the shading engine
            mc.sets(ghostName, edit=True,forceElement = sgName)#asign material to ghost

            mc.setAttr(matName+".color", self.color[0],self.color[1],self.color[2],type="double3")              
    def GetMaterialNameForGhost(self, ghost):
        return ghost + "_mat"

    def GetShadingEnginForGhost(self, ghost):
        return ghost + "_sg"
    
    def GoToNextGhost(self):
        frames = self.GetGhostFramesSorted()#find all the frames we have in ascending order
        if not frames: # if there is not frames, there is not ghost, do nothing
            return
        currentFrame = GetCurrentFrame()
        for frame in frames:#find all the frames we have in ascending order
            if frame > currentFrame:#if we find one that is bigger than the current frame, it should be where we move time slider to 
                mc.currentTime(frame, e = True)#e means edit, we are editing teh time slider to at frame
                return
        mc.currentTime(frames[0], e=True)

    def GotToPrevGhost(self):
        frames = self.GetGhostFramesSorted()
        if not frames:
            return
        
        currentFrame = GetCurrentFrame()
        frames.reverse()
        for frame in frames:
            if frame < currentFrame:
                mc.currentTime(frame, e = True)
                return
            
        mc.currentTime(frames[0], e = True)
    
    def DeleteGhostOnCurrentFrame(self):
        #frames = self.GetGhostFramesSorted()
        #if not frames:
           #return

       # currentFrame = GetCurrentFrame()
        #for srcMesh in self.srcMeshes:
            #ghostName = srcMesh + "_" + str(currentFrame)
            #if mc.objExists(ghostName):
                #mc.delete(ghostName)

        currentFrames = GetCurrentFrame()
        ghosts = mc.listRelatives(self.ghostGrp, c = True)#gets all childer of the ghost grp
        for ghost in ghosts:
            ghostFrame = mc.getAttr(ghost+"."+self.frameAttr)#ask for the frame recorded for the ghost
            if ghostFrame == currentFrames: #if the ghost frame is the sames as current frame
                self.DeletGhost(ghost)#remove ghost'

    def DeletGhost(self, ghost):
        #delete material
        mat = self.GetMaterialNameForGhost(ghost)
        if mc.objExists(mat):
            mc.delete(mat)

        #delete shading engine
        sg = self. GetShadingEnginForGhost(ghost)
        if mc.objExists(sg):
            mc.delete(sg)

        #delete the ghost model
        if mc.objExists(self.ghostGrp):
            mc.delete(ghost)

    def DeleteGhostOnAllFrames(self):
        ghosts = mc.listRelatives(self.ghostGrp, c= True)
        for ghost in ghosts:
            self.DeletGhost(ghost)    

    def GetGhostFramesSorted(self):
        frames = set()
        ghosts = mc.listRelatives(self.ghostGrp, c=True)

        if not ghosts:
            return[]
        
        for ghost in ghosts:
            frame = mc.getAttr(ghost + "." + self.frameAttr)
            frames.add(frame)

        frames = list(frames)#this converts frmes to a list 
        frames.sort()#this sort the frames in accending order
        return frames#return sorted frames
    
class ColorPicker(QWidget):
    onColorChange = Signal(QColor)#this adds a built in class memeber called oncolorchange
    def __init__(self, width = 30, hight = 20):
        super().__init__()
        self.setFixedSize(width, hight)
        self.color = QColor()

    def mousePressEvent(self, event):
        color = QColorDialog().getColor(self.color)
        self.color = color
        self.onColorChange.emit(self.color)
        self.update()#update the widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0,0,self.width(), self.height())

class GhostWidget(QWidget):
    def __init__(self):
        super().__init__()#need to call if you are inheriting from parent class
        self.ghost = Ghost() #create ghost to bypass commant to.
        self.setWindowTitle("Ghotser Poser V1.0")
        self.masterLayout = QVBoxLayout() #creates a vertical layout
        self.setLayout(self.masterLayout) #tells the window to use the vertical layout created in previous line

        self.srcMeshlist = QListWidget()#creates a list to show stuff
        self.srcMeshlist.setSelectionMode(QAbstractItemView.ExtendedSelection)#allow multi-selection
        self.srcMeshlist.itemSelectionChanged.connect(self.SrcMeshSelectionChanged)
        self.masterLayout.addWidget(self.srcMeshlist) #this adds the list createed previously to layout

        addSrcMeshBtn = QPushButton("Add Source Mesh")#adding (self.) can be used to be refrenced another time
        addSrcMeshBtn.clicked.connect(self.AddSrcMeshBtnClicked)
        self.srcMeshlist.addItems(self.ghost.srcMeshes)
        self.masterLayout.addWidget(addSrcMeshBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.ctrlLayout)

        addGhostBtn = QPushButton("add/update")
        addGhostBtn.clicked.connect(self.ghost.addGhost)
        self.ctrlLayout.addWidget(addGhostBtn)

        prevGhostBtn = QPushButton("Prev")
        prevGhostBtn.clicked.connect(self.ghost.GotToPrevGhost)
        self.ctrlLayout.addWidget(prevGhostBtn)

        nextGhostBtn = QPushButton("Next")
        nextGhostBtn.clicked.connect(self.ghost.GoToNextGhost)
        self.ctrlLayout.addWidget(nextGhostBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.ctrlLayout)

        DelGhostBtn = QPushButton("Delete Current Ghost")
        DelGhostBtn.clicked.connect(self.ghost.DeleteGhostOnCurrentFrame)
        self.ctrlLayout.addWidget(DelGhostBtn)

        DelAllGhostBtn = QPushButton("Delete all Ghost")
        DelAllGhostBtn.clicked.connect(self.ghost.DeleteGhostOnAllFrames)
        self.ctrlLayout.addWidget(DelAllGhostBtn)

        colorPicker = ColorPicker()
        colorPicker.onColorChange.connect(self.ghost.UpdateGhostColors)
        self.masterLayout.addWidget(colorPicker)


        
    def SrcMeshSelectionChanged(self):
        mc.select(cl=True)#cancle everything
        for item in self.srcMeshlist.selectedItems():
            mc.select(item.text(), add = True)
      
    def AddSrcMeshBtnClicked(self):
        self.ghost.SetSelectedAsSrcMesh()#asks ghost to populate its srcMeshes with the current selection
        self.srcMeshlist.clear()#this clear our list widget
        self.srcMeshlist.addItems(self.ghost.srcMeshes)#this add srcMeshes collected eariler to the list widget


ghostwidget = GhostWidget()
ghostwidget.show()