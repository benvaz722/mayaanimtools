#alt+shift+m = send code to maya
import maya.cmds as mc

from PySide2.QtWidgets import QWidget,QVBoxLayout, QLabel, QPushButton

class CreateControllerWidget(QWidget):
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
        self.adjustSize()

    def FindJntBtnClicked(self):
        print("I am clicked")


controllerWidget = CreateControllerWidget()
controllerWidget.show()
