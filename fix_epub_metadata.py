# fix_epub_metadata.py

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
	def __init__(self):
		QWizard.__init__(self)
		
		metadataLayout = QHBoxLayout()
		metadataLayout.addWidget(self.createMetadataWidget(), 100)
		metadataLayout.addWidget(self.createCoverWidget())

		changesLayout = QHBoxLayout()
		changesLayout.addWidget(self.createOriginalWidget())
		changesLayout.addWidget(self.createChangesWidget())
		
		mainWidget = QWidget()
		mainLayout = QVBoxLayout()
		mainLayout.addWidget(self.createInputPathWidget())
		mainLayout.addLayout(metadataLayout)
		mainLayout.addLayout(changesLayout, 100)
		mainLayout.addWidget(self.createButtonBox())
		mainWidget.setLayout(mainLayout)
		self.setCentralWidget(mainWidget)
		
		self.setWindowTitle("Fix ePub Metadata")
		self.resize(1000, 800)
		
	def createInputPathWidget(self):
		groupBox = QGroupBox("Input Path")
		
		self._pathEdit = QLineEdit()
		
		pathButton = QPushButton("Browse...")
		pathButton.clicked.connect(self.openEpubFile)
		
		pathLayout = QHBoxLayout()
		pathLayout.addWidget(self._pathEdit, 100)
		pathLayout.addWidget(pathButton)
		
		groupLayout = QFormLayout()
		groupLayout.addRow("Input File:", pathLayout)
		groupLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		groupLayout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		groupLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
		groupLayout.itemAt(0, QFormLayout.LabelRole).widget().setMinimumWidth(100)
		groupBox.setLayout(groupLayout)
		
		return groupBox
		
	def createMetadataWidget(self):
		groupBox = QGroupBox("Metadata")
		
		self._titleEdit = QLineEdit()
		self._titleEdit.textEdited.connect(self.updateOpfFromMetadata)
		
		self._authorEdit = QLineEdit()
		self._authorEdit.textEdited.connect(self.updateOpfFromMetadata)

		self._authorFileAsEdit = QLineEdit()
		self._authorFileAsEdit.textEdited.connect(self.updateOpfFromMetadata)

		groupLayout = QFormLayout()
		groupLayout.addRow("Title:", self._titleEdit)
		groupLayout.addRow("Author:", self._authorEdit)
		groupLayout.addRow("Author (file-as):", self._authorFileAsEdit)
		groupLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		groupLayout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		groupLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
		groupLayout.itemAt(0, QFormLayout.LabelRole).widget().setMinimumWidth(100)
		groupBox.setLayout(groupLayout)
		
		return groupBox

	def createCoverWidget(self):
		groupBox = QGroupBox("Cover")

		self._coverImageLabel = QLabel()
		self._coverImageLabel.setMinimumSize(QSize(160, 200))
		
		imageButton = QPushButton("Browse...")
		imageButton.clicked.connect(self.selectCoverImage)
		
		rightLayout = QVBoxLayout()
		rightLayout.addWidget(imageButton)
		rightLayout.addWidget(QWidget(), 100)
		
		groupLayout = QHBoxLayout()
		groupLayout.addWidget(self._coverImageLabel, 100)
		groupLayout.addLayout(rightLayout)
		groupBox.setLayout(groupLayout)

		return groupBox

	def createOriginalWidget(self):
		groupBox = QGroupBox("Original OPF File")
		
		self._originalOpfEdit = QTextEdit()
		self._originalOpfEdit.setReadOnly(True)
		
		groupLayout = QHBoxLayout()
		groupLayout.addWidget(self._originalOpfEdit)
		groupBox.setLayout(groupLayout)

		return groupBox

	def createChangesWidget(self):
		groupBox = QGroupBox("New OPF File")
		
		self._newOpfEdit = QTextEdit()
		self._newOpfEdit.setReadOnly(False)
		
		groupLayout = QVBoxLayout()
		groupLayout.addWidget(self._newOpfEdit)
		groupBox.setLayout(groupLayout)

		return groupBox

	def createButtonBox(self):
		buttonBox = QDialogButtonBox(Qt.Horizontal)
		buttonBox.setCenterButtons(True)
		
		updateButton = buttonBox.addButton("  Update  ", QDialogButtonBox.AcceptRole)
		updateButton.setMinimumHeight(QFontMetrics(updateButton.font()).height() + 16)
		updateButton.clicked.connect(self.updateEpubFileMetadata)
		
		closeButton = buttonBox.addButton("  Cancel  ", QDialogButtonBox.RejectRole)
		closeButton.setMinimumHeight(QFontMetrics(closeButton.font()).height() + 16)
		closeButton.clicked.connect(self.close)
		
		return buttonBox

	#-----------------------------------------------------------------------------------------------
	
	def openEpubFile(self):
		pass
		
	def updateOpfFromMetadata(self):
		pass
		
	def selectCoverImage(self):
		pass

	def updateEpubFileMetadata(self):
		pass
		
#===================================================================================================

if (__name__ == "__main__"):
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
