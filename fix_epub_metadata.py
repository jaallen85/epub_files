# fix_epub_metadata.py

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
import zipfile

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
		self.resize(1400, 800)
				
	def createInputPathWidget(self):
		groupBox = QGroupBox("Input Path")
		
		self._pathEdit = QLineEdit()
		self._pathEdit.setReadOnly(True)
		
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
		self._coverImageLabel.setFixedSize(QSize(160, 200))
		
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
		self._originalOpfEdit.setTabStopWidth(16)
		self._originalOpfEdit.setWordWrapMode(QTextOption.NoWrap)
		self._originalOpfEdit.setFont(QFont("Consolas", 9))
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
		filePath = QFileDialog.getOpenFileName(self, "Select ePub File", self._pathEdit.text(),
			"ePub Files (*.epub);;All Files (*)")[0]
		if (filePath != ""):
			self._pathEdit.setText(filePath)
			
			# (title, author, authorFileAs, coverImage, fullOpfText) = self.getEpubMetadata(filePath)
			# self._titleEdit.setText(title)
			# self._authorEdit.setText(author)
			# self._authorFileAsEdit.setText(authorFileAs)
			# self._coverImageLabel.setPixmap(QPixmap.fromImage(coverImage.scaled(self._coverImageLabel.size(), Qt.KeepAspectRatio)))
			# self._originalOpfEdit.setPlainText(fullOpfText.decode("utf-8"))				

			#self.updateOpfFromMetadata()
			
			coverImage = self.readCoverImage(filePath)
			self._coverImageLabel.setPixmap(QPixmap.fromImage(coverImage.scaled(self._coverImageLabel.size(), Qt.KeepAspectRatio)))
		
	def updateOpfFromMetadata(self):
		pass
		
	def selectCoverImage(self):
		filePath = QFileDialog.getOpenFileName(self, "Select Cover Image", "",
			"jpeg Files (*.jpeg, *.jpg);;All Files (*)")[0]
		
		if (filePath != ""):
			self.writeCoverImage(self._pathEdit.text(), filePath)

			coverImage = self.readCoverImage(self._pathEdit.text())
			self._coverImageLabel.setPixmap(QPixmap.fromImage(coverImage.scaled(self._coverImageLabel.size(), Qt.KeepAspectRatio)))
			
	def updateEpubFileMetadata(self):
		pass
		
	#-----------------------------------------------------------------------------------------------

	def getEpubMetadata(self, epubPath):
		title = ""
		author = ""
		authorFileAs = ""
		fullOpfText = ""
		
		with zipfile.ZipFile(epubPath, 'r') as epubFile:
			with epubFile.open(self.getOpfPath(epubFile)) as opfFile:
				fullOpfText = opfFile.read()
				xml = QXmlStreamReader(fullOpfText)
				while (xml.readNextStartElement()):
					if (xml.name() == "package"):
						while (xml.readNextStartElement()):
							if (xml.name() == "metadata"):
								while (xml.readNextStartElement()):
									if (xml.name() == "title"):
										xml.readNext()
										title = xml.text()
										xml.readNext()
									elif (xml.name() == "creator"):
										attr = xml.attributes()
										
										xml.readNext()
										author = xml.text()
										xml.readNext()
										
										if (attr.hasAttribute("file-as")):
											authorFileAs = attr.value("file-as")
										else:
											lastSpace = author.rfind(" ")
											authorFileAs = author[lastSpace+1:] + ", " + author[:lastSpace]
									else:
										xml.skipCurrentElement()
							else:
								xml.skipCurrentElement()
					else:
						xml.skipCurrentElement()
										
		return (title, author, authorFileAs, fullOpfText)

	def getOpfPath(self, epubFile):
		opfPath = ""
		
		with epubFile.open("META-INF/container.xml") as containerFile:
			xml = QXmlStreamReader(containerFile.read())
			while (opfPath == "" and xml.readNextStartElement()):
				if (xml.name() == "container"):
					while (opfPath == "" and xml.readNextStartElement()):
						if (xml.name() == "rootfiles"):
							while (opfPath == "" and xml.readNextStartElement()):
								if (xml.name() == "rootfile"):
									attr = xml.attributes()
									if (attr.hasAttribute("full-path") and attr.hasAttribute("media-type") and 
										attr.value("media-type") == "application/oebps-package+xml"):
										opfPath = attr.value("full-path")
								xml.skipCurrentElement()
						else:
							xml.skipCurrentElement()					
				else:
					xml.skipCurrentElement()
		
		return opfPath

		
	def readCoverImage(self, epubPath):
		image = QImage()
		
		with zipfile.ZipFile(epubPath, 'r') as epubFile:
			coverPath = self.getCoverImagePath(epubFile)
			if (coverPath != ""):
				with epubFile.open(coverPath, 'r') as jpegFile:
					image = QImage.fromData(jpegFile.read(), "image/jpeg")
		
		return image
		
	def writeCoverImage(self, epubPath, imagePath):
		coverPath = ""
		with zipfile.ZipFile(epubPath, 'r') as epubFile:
			coverPath = self.getCoverImagePath(epubFile)
		
		# Note: this code doesn't work
		#Updating a file in a ZIP is not supported. You need to rebuild a new archive without the file, then add the updated version.
		if (coverPath != ""):
			with zipfile.ZipFile(epubPath, 'a') as epubFile:
				epubFile.write(imagePath, coverPath)
	
	def getCoverImagePath(self, epubFile):
		coverPath = ""
		coverId = ""
		
		with epubFile.open(self.getOpfPath(epubFile)) as opfFile:
			xml = QXmlStreamReader(opfFile.read())
			while (xml.readNextStartElement()):
				if (xml.name() == "package"):
					while (xml.readNextStartElement()):
						if (xml.name() == "metadata"):
							while (xml.readNextStartElement()):
								if (xml.name() == "meta"):
									attr = xml.attributes()
									if (attr.hasAttribute("name") and attr.hasAttribute("content") and
										attr.value("name") == "cover"):
										coverId = attr.value("content")
								xml.skipCurrentElement()
						elif (xml.name() == "manifest" and coverId != ""):
							while (xml.readNextStartElement()):
								if (xml.name() == "item"):
									attr = xml.attributes()
									if (attr.hasAttribute("id") and attr.hasAttribute("href") and
										attr.value("id") == coverId):
										coverPath = attr.value("href")
								xml.skipCurrentElement()
						else:
							xml.skipCurrentElement()
				else:
					xml.skipCurrentElement()
		
		return coverPath
		
#===================================================================================================

if (__name__ == "__main__"):
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
