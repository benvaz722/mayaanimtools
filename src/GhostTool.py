import maya.cmds as mc
from PySide2.QtWidgets import QWidget,QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QAbstractItemView

def GetCurrentFrame():
    return int(mc.currentTime(q=True))#query

class Ghost:
    def __init__ (self):
        self.srcMeshes = set()#a set only holds unique elemts no duplicates like list
        self.ghostGrp = "ghost_grp"
        self.frameAttr = "frame"
        self.srcAttr = "src"

        self.InitIfGhostGrpNotExist()

    def InitIfGhostGrpNotExist(self):
        if mc.objExists(self.ghostGrp):
            storedSrcMeshes = mc.getAttr(self.ghostGrp + "." + self.srcAttr)
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
            currentFrame = GetCurrentFrame
            ghostName = srcMesh + "_" + str(currentFrame)
            if mc.objExists(ghostName):
                mc.delete(ghostName)
        
            mc.duplicate(srcMesh, n = ghostName)
            mc.parent(ghostName, self.ghostGrp)
            mc.addAttr(ghostName, ln = self.frameAttr, dv = currentFrame)#default value

    def GoToNextGhost(self):
        frames = self.GetGhostFramesSorted()
        currentFrame = GetCurrentFrame
        for frame in frames:
            if frame > currentFrame:
                mc.currentTime(frame, e = True)#e means edit, we are editing teh time slider to at frame
                return
        mc.currentTime(frames[0], e=True)

    def GotToPrevGhost(self):
        pass
        
    def GetGhostFramesSorted(self):
        frames = set()
        for ghost in mc.listRelatives(self.ghostGrp, c=True):
            frame = mc.getAttr(ghost + "." + self.frameAttr)
            frames.add(frame)

        frames = list(frames)#this converts frmes to a list 
        frames.sort()#this sort the frames in accending order
        return frames#return sorted frames
    
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
        prevGhostBtn.clicked.connect(self.ghost.GoToPrevGhost)
        self.ctrlLayout.addWidget(prevGhostBtn)

        nextGhostBtn = QPushButton("Next")
        nextGhostBtn.clicked.connect(self.ghost.GoToNextGhost)
        self.ctrlLayout.addWidget(nextGhostBtn)
        
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