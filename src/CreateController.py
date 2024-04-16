#alt+shift+m = send code to maya
import maya.cmds as mc #this imports the camands for maya packaes

from PySide2.QtWidgets import QWidget,QVBoxLayout, QLabel, QPushButton #this line imports the specific classes needed for the code

def CreateBox(name, size):#is used to defince what to creaete a box as with the two peramiters 
    pntPositions = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    #cordinates to where the line is to be crated around
    mc.curve(n = name, d=1, p = pntPositions) #creates the line around the name, degree, and the postions above
    mc.setAttr(name + ".scale", size, size, size, type = "float3")# uses the set attribute camand to scale the box
    mc.makeIdentity(name, apply = True)#freeze transformation

def  CreateCircleController(jnt, size): #a definition to create the cirlce with its two paramaters

    name = "ac_" + jnt #this names the controller by adding the ac and jnt
    mc.circle(n = name, nr= (1,0,0), r = size/2) #creates a circle with a name a normal vector and its radious size
    ctrlGrpName = name + "_grp" #crates a ctrlgroup name 
    mc.group(name, n = ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt) #matches the transformations of the controll group with the joints 
    mc.orientConstraint(name, jnt) #creates and oreint constraint on the the controller and joint 

    return name, ctrlGrpName #returns the new name and the new control grp

def CreatePlus(name, size):
    pntPositions = ((0.5,0,1),(0.5,0,0.5),(1,0,0.5),(1,0,-0.5),(0.5, 0,-0.5), (0.5, 0, -1),(-0.5, 0, -1),(-0.5,0,-0.5),(-1, 0, -0.5),(-1,0,0.5),(-0.5,0,0.5),(-0.5,0,1),(0.5,0,1))
    mc.curve(n = name, d=1, p = pntPositions) #creates the line around the name, degree, and the postions above
    mc.setAttr(name + ".scale", size, size, size, type = "float3")# uses the set attribute camand to scale the box
    mc.makeIdentity(name, apply = True)#freeze transformation

def SetChannelHidden(name, channel):
    mc.setAttr(name + "." + channel, k=False, channelBox = False)

def GetObjPos(obj):
    #q means we are querying
    #t means we are querying the translate
    #x means we are querying in the world space
    pos = mc.xform(obj, q=True, t=True, ws=True)
    return Vector(pos[0],pos[1],pos[2] )

def SetObjPos(obj, pos):
    mc.setAttr(obj + ".translate", pos.x, pos.y, pos.z, type = "float3")

class Vector:
#class overloading
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
#this enables vector + vector
    def __add__(self, other):
        return Vector(self.x + other.x,self.y + other.y,self.z + other.z )
#this enables vector - vector
    def __sub__(self, other):
        return Vector(self.x - other.x,self.y - other.y,self.z - other.z )
#this are defining * float
    def __mul__(self, scalar):
        return Vector(self.x * scalar,self.y * scalar,self.z * scalar )
#we are defining vector / float
    def __truediv__(self, scalar):
        return Vector(self.x / scalar,self.y / scalar,self.z / scalar )
    
    def GetLength(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def GetNormalize (self):
        return self/self.GetLength()
    
    def __str__(self):
        return f"{self.x}, {self.y}, {self.z}"

class CreateLimbController(): #a class that is going to be called upon to create the limb controller
    def __init__(self): #initiallize the class with three atributes with empty strings
        self.root = ""
        self.mid = ""
        self.end = ""
    
    def FindJntsBasedOnRootSel(self): #this is used to find the joints within the controller
        self.root = mc.ls(sl=True, type = "joint")[0] #sets which joint is the root 
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0] #sets which joint is the middle and list relatives for the childs
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0] #sets which joint is the end

    def RigLimb(self): #defines the the method to rig a limb within the create controller class
        rootCtrl, RootCtrlGrp = CreateCircleController(self.root, 20) #calls back to create cirlce controller function and places them on its respective sections with the size of 20
        midCtrl, midCtrlGrp = CreateCircleController(self.mid, 20)
        endCtrl, endCtrlGrp = CreateCircleController(self.end, 20)

        mc.parent(midCtrlGrp, rootCtrl)#this line parents each control group made
        mc.parent(endCtrlGrp, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end #is used to name and creat a box with the size of 10
        CreateBox(ikEndCtrl, 10)
        ikEndCtrlGrp = ikEndCtrl + "_grp" #create a ik end contorler
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end) #matches transformations of the group to end
        endJntOrientConstraint = mc.orientConstraint(ikEndCtrlGrp,self.end)[0]#creats and orient constraint

        ikHandleName = "ikHandle_" + self.end #creats ik handle from the root to the end
        mc.ikHandle(n=ikHandleName, sj = self.root, ee= self.end, sol="ikRPsolver") #see is the last joint

        poleVector = mc.getAttr(ikHandleName+".poleVector")[0] #search for polevector frome maya
        poleVector = Vector(poleVector[0], poleVector[1], poleVector[2])
        poleVector = poleVector.GetNormalize()
        print(poleVector)

        rootPos = GetObjPos(self.root)
        endPos = GetObjPos(self.end)

        rootToEndVec = endPos - rootPos
        armHalfLength = rootToEndVec.GetLength()/2

        poleVectorPos = rootPos + rootToEndVec/2 + poleVector * armHalfLength
        ikMidCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n=ikMidCtrl)#make a locator with the name ac_ik_ + self.mid
        ikMidCtrlGrp = ikMidCtrl + "_grp" #figure out the group name of that locator
        mc.group(ikMidCtrl, n = ikMidCtrlGrp)#group the ocator with the name
        SetObjPos(ikMidCtrl, poleVectorPos)#make the locator to the polevector location we figured
        mc.poleVectorConstraint(ikMidCtrl, ikHandleName) #do pole vector constraint
        mc.parent(ikHandleName, ikEndCtrl)
        mc.hide(ikHandleName)

        ikfkBlendCtrl = "ac_" + self.root + "_ikfkBlend"
        CreatePlus(ikfkBlendCtrl, 2)
        ikfkBlendCtrlGrp = ikfkBlendCtrl + "_grp"
        mc.group(ikfkBlendCtrl, n = ikfkBlendCtrlGrp)
        ikfkBlendCtrlPos = rootPos + Vector(rootPos.x,0,0)
        SetObjPos(ikfkBlendCtrlGrp, ikfkBlendCtrlPos)
        mc.setAttr(ikfkBlendCtrlGrp + ".rx", 90)

        SetChannelHidden(ikfkBlendCtrl, 'tx')#short hand attribute
        SetChannelHidden(ikfkBlendCtrl, 'ty')
        SetChannelHidden(ikfkBlendCtrl, 'tz')
        SetChannelHidden(ikfkBlendCtrl, 'rx')
        SetChannelHidden(ikfkBlendCtrl, 'ry')
        SetChannelHidden(ikfkBlendCtrl, 'rz')
        SetChannelHidden(ikfkBlendCtrl, 'sx')
        SetChannelHidden(ikfkBlendCtrl, 'sy')
        SetChannelHidden(ikfkBlendCtrl, 'sz')
        SetChannelHidden(ikfkBlendCtrl, 'v')

        ikfkBlendAttr = "ikfkblend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttr, k= True)#k=keyable
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikHandleName + ".ikBlend")#list two dots connceting
        
        reverseNode = "reverse_" + self.root + "_ikfkBlend"
        mc.createNode("reverse", n = reverseNode)

        #connect the blend for fkik switch
        mc.connectAttr(ikfkBlendCtrl +"." + ikfkBlendAttr, reverseNode + ".inputX")
        mc.connectAttr(reverseNode + ".outputX", endJntOrientConstraint + ".w0")
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, endJntOrientConstraint + ".w1")
        #hiding
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikMidCtrlGrp + ".v")
        mc.connectAttr(reverseNode + ".outputX", rootCtrl + ".v")
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikEndCtrlGrp + ".v")

        mc.group(ikfkBlendCtrlGrp, ikEndCtrlGrp, ikMidCtrlGrp, RootCtrlGrp, n = RootCtrlGrp + "_limb")

        

class CreateControllerWidget(QWidget): #incharge of talking to the real code
    def __init__(self): # initulize the class 
        super().__init__() #creates a box layout
        self.setWindowTitle("Create IKFK Limb")
        self.setGeometry(100,100,300,300)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        hintLabel = QLabel("Please Select the root of the limb:") #creats the message for the users to read
        self.masterLayout.addWidget(hintLabel)

        findJntBtn = QPushButton("Find Jnts") #creates a button that adds it to the layout and calles to the button clicked function
        findJntBtn.clicked.connect(self.FindJntBtnClicked)
        self.masterLayout.addWidget(findJntBtn)


        self.autoFindJntDisplay = QLabel("") #creats ta lable and adjust the widget size based on the infromation
        self.masterLayout.addWidget(self.autoFindJntDisplay)
        self.adjustSize()

        rigLimbBtn = QPushButton("Rig Limb") #line creats a button that initiatze the rig limb function
        rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterLayout.addWidget(rigLimbBtn)

        self.createLimbCtrl = CreateLimbController() #starts the creatlimbcontroller class

    def FindJntBtnClicked(self): #starts when the button is clicked
        self.createLimbCtrl.FindJntsBasedOnRootSel()# calls back into the create limbcontroller to find the names 
        self.autoFindJntDisplay.setText(f"{self.createLimbCtrl.root}, {self.createLimbCtrl.mid}, {self.createLimbCtrl.end}") #display the names 
        print("I am clicked")

    def RigLimbBtnClicked(self):
        self.createLimbCtrl.RigLimb() #initialize the create limb function

controllerWidget = CreateControllerWidget() #creats an instance of the creatcontrollerwidget to show
controllerWidget.show()
