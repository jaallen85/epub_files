# fix_epub_metadata.py

import sys, os, shutil, tempfile
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
import zipfile

class MainWindow(QMainWindow):
	def __init__(self, filePath = ""):
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
		
		if (filePath != ""):
			self._pathEdit.setText(filePath)
			self.setEpubFile(filePath)
				
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
		self._titleEdit.textEdited.connect(self.updateNewOpfFile)
		
		self._authorEdit = QLineEdit()
		self._authorEdit.textEdited.connect(self.updateNewOpfFile)

		self._authorFileAsEdit = QLineEdit()
		self._authorFileAsEdit.textEdited.connect(self.updateNewOpfFile)

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
		self._newOpfEdit.setTabStopWidth(16)
		self._newOpfEdit.setWordWrapMode(QTextOption.NoWrap)
		self._newOpfEdit.setFont(QFont("Consolas", 9))
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
			self.setEpubFile(filePath)
			
	def selectCoverImage(self):
		filePath = QFileDialog.getOpenFileName(self, "Select Cover Image", "",
			"jpeg Files (*.jpeg, *.jpg);;All Files (*)")[0]
		
		if (filePath != ""):
			self.writeCoverImage(self._pathEdit.text(), filePath)

			coverImage = self.readCoverImage(self._pathEdit.text())
			self._coverImageLabel.setPixmap(QPixmap.fromImage(coverImage.scaled(self._coverImageLabel.size(), Qt.KeepAspectRatio)))
			
	def updateNewOpfFile(self):
		self._newOpfEdit.setPlainText(self.buildNewOpf(self._originalOpfEdit.toPlainText(), 
			self._titleEdit.text(), self._authorEdit.text(), self._authorFileAsEdit.text()))
		
	def updateEpubFileMetadata(self):
		self.writeOpfFile(self._pathEdit.text(), self._newOpfEdit.toPlainText())
		self.setEpubFile(self._pathEdit.text())
		
	def setEpubFile(self, epubPath):
		(fullOpfText, title, author, authorFileAs) = self.readOpfFile(epubPath)
		self._originalOpfEdit.setPlainText(fullOpfText.decode("utf-8"))				
		self._titleEdit.setText(title)
		self._authorEdit.setText(author)
		self._authorFileAsEdit.setText(authorFileAs)

		coverImage = self.readCoverImage(epubPath)
		self._coverImageLabel.setPixmap(QPixmap.fromImage(coverImage.scaled(self._coverImageLabel.size(), Qt.KeepAspectRatio)))

		self.updateNewOpfFile()
		
	#-----------------------------------------------------------------------------------------------

	def readOpfFile(self, epubPath):
		fullOpfText = ""
		title = ""
		author = ""
		authorFileAs = ""
		
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
										
		return (fullOpfText, title, author, authorFileAs)

	def writeOpfFile(self, epubPath, opfContents):
		opfPath = ""
		with zipfile.ZipFile(epubPath, 'r') as epubFile:
			opfPath = self.getOpfPath(epubFile)
		
		if (opfPath != ""):
			self.removeFromEpub(epubPath, opfPath)
			with zipfile.ZipFile(epubPath, 'a') as epubFile:
				epubFile.writestr(opfPath, opfContents)

	def buildNewOpf(self, originalOpfText, title, author, authorFileAs):
		metadataStart = originalOpfText.find("<metadata")
		metadataEnd = originalOpfText.find("</metadata>") + 11
		metadataStr = originalOpfText[metadataStart:metadataEnd]
		
		identifierStart = metadataStr.find("<dc:identifier")
		identifierEnd = metadataStr.find("</dc:identifier>") + 16
		identifierStr = metadataStr[identifierStart:identifierEnd]
		
		# Fix for Barnes and Noble NOOK (original)
		# name must be first attribute of meta tag, otherwise cover art doesn't work
		coverIndex = metadataStr.find("name=\"cover\"")
		coverStart = metadataStr.rfind("<meta", 0, coverIndex)
		coverEnd = metadataStr.find("/>", coverIndex) + 2
		coverStr = metadataStr[coverStart:coverEnd]
		
		coverIndex = coverStr.find("name=\"cover\"")
		coverStr = coverStr[:coverIndex] + coverStr[coverIndex+12:]
		coverStr = coverStr[:5] + " name=\"cover\"" + coverStr[5:]
		
		newMetadataStr = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">\n"
		newMetadataStr += "\t\t" + identifierStr + "\n"
		newMetadataStr += "\t\t<dc:title>" + title + "</dc:title>\n"
		newMetadataStr += "\t\t<dc:creator"
		if (authorFileAs != ""):
			newMetadataStr += " opf:file-as=\"" + authorFileAs + "\""
		newMetadataStr += ">" + author + "</dc:creator>\n"
		newMetadataStr += "\t\t<dc:language>en</dc:language>\n"
		newMetadataStr += "\t\t" + coverStr + "\n"
		newMetadataStr += "\t</metadata>"
		
		newOpfText = originalOpfText[:metadataStart] + newMetadataStr + originalOpfText[metadataEnd:]
		return newOpfText
		
	#-----------------------------------------------------------------------------------------------
	
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
		
		if (coverPath != ""):
			self.removeFromEpub(epubPath, coverPath)
			with zipfile.ZipFile(epubPath, 'a') as epubFile:
				epubFile.write(imagePath, coverPath)
	
	def getCoverImagePath(self, epubFile):
		coverPath = ""
		coverId = ""
		
		opfPath = self.getOpfPath(epubFile)
		with epubFile.open(opfPath) as opfFile:
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
										coverPath = os.path.dirname(opfPath) + "/" + attr.value("href")
								xml.skipCurrentElement()
						else:
							xml.skipCurrentElement()
				else:
					xml.skipCurrentElement()
		
		return coverPath
	
	#-----------------------------------------------------------------------------------------------
	
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

	def removeFromEpub(self, epubPath, arcname):
		tempdir = tempfile.mkdtemp()
		try:
			tempname = os.path.join(tempdir, 'new.zip')
			with zipfile.ZipFile(epubPath, 'r') as zipread:
				with zipfile.ZipFile(tempname, 'w') as zipwrite:
					for item in zipread.infolist():
						if (item.filename != arcname):
							data = zipread.read(item.filename)
							zipwrite.writestr(item, data)
			shutil.move(tempname, epubPath)
		finally:
			shutil.rmtree(tempdir)
			
#===================================================================================================

if (__name__ == "__main__"):
	app = QApplication(sys.argv)
	if (len(sys.argv) > 1):
		window = MainWindow(sys.argv[1])
	else:
		window = MainWindow()
	window.show()
	sys.exit(app.exec_())
