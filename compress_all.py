# extract_all.py

import glob, os, zipfile

inputDir = r"F:\Books\python"

os.chdir(inputDir)
for dir in os.listdir("."):
	if (os.path.isdir(dir)):
		epubFile = zipfile.ZipFile(dir + ".epub", 'w', zipfile.ZIP_DEFLATED)
		
		os.chdir(dir)
		
		for root, dirs, files in os.walk("."):
			for file in files:
				print(root, file)
				epubFile.write(os.path.join(root, file))
		epubFile.close()
		
		os.chdir("..")
		