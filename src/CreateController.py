#alt+shift+m = send code to maya
import maya.cmds as mc

from PySide2.QtWidgets import QWidget,QVBoxLayout, QLabel, QPushButton

def CreateBox(name, size):
    pntPositions = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    mc.curve(n = name, d=1, p = pntPositions)
    mc.setAttr(name + ".scale", size, size, size, type = "float3")
    mc.makeIdentity()#freeze transformation

def  CreateCircleController(jnt, size):

    name = "ac_" + jnt
    mc.circle(n = name, nr= (1,0,0), r = size/2)
    ctrlGrpName = name + "_grp"
    mc.group(name, n = ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(name, jnt)

    return name, ctrlGrpName

class CreateLimbController():
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
    
    def FindJntsBasedOnRootSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def RigLimb(self):
        rootCtrl, RootCtrlGrp = CreateCircleController(self.root, 20)
        midCtrl, midCtrlGrp = CreateCircleController(self.mid, 20)
        endCtrl, endCtrlGrp = CreateCircleController(self.end, 20)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        CreateBox(ikEndCtrl, 10)
        ikEndCtrlGrp = ikEndCtrl + "_grp"
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        mc.orientConstraint(ikEndCtrlGrp,self.end)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sj = self.root, ee= self.end, sol="ikRPsolver") #ee is the last joint



class CreateControllerWidget(QWidget): #incharge of talking to the real code
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create IKFK Limb")
        self.setGeometry(100,100,300,300)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        hintLabel = QLabel("Please Select the root of the limb:")
        self.masterLayout.addWidget(hintLabel)

        findJntBtn = QPushButton("Find Jnts")
        findJntBtn.clicked.connect(self.FindJntBtnClicked)

        self.masterLayout.addWidget(findJntBtn)


        self.autoFindJntDisplay = QLabel("")
        self.masterLayout.addWidget(self.autoFindJntDisplay)
        self.adjustSize()

        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterLayout.addWidget(rigLimbBtn)

        self.createLimbCtrl = CreateLimbController()

    def FindJntBtnClicked(self):
        self.createLimbCtrl.FindJntsBasedOnRootSel()
        self.autoFindJntDisplay.setText(f"{self.createLimbCtrl.root}, {self.createLimbCtrl.mid}, {self.createLimbCtrl.end}")
        print("I am clicked")

    def RigLimbBtnClicked(self):
        self.createLimbCtrl.RigLimb()


controllerWidget = CreateControllerWidget()
controllerWidget.show()
