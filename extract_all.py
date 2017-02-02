# extract_all.py

import glob, os, zipfile

inputDir = r"F:\Books\python"

os.chdir(inputDir)
for file in glob.glob("*.epub"):
	epubFile = zipfile.ZipFile(file, 'r')
	epubFile.extractall(file[:-5])
	epubFile.close()
	