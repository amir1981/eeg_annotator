This is EEG Annotator version 0.2.2
===================================
---------------------------
What's new in this release?
---------------------------
*Release date: 2014-09-11*
	- Some parts have been edited for creating the stand-alone executable. As after installing setup.exe, the application can be lunched in every folder, we
	should use the addresses which are not relative.
	- Print_plot() has been edited to receive start time and end time from user for printing EEG signals and their annotations. This part is using dip.ui 
	module. dip.ui module implements a toolkit independent API for defining a user interface declaratively. Using dip.ui we are avoiding to create a lot
    of .ui files and their related .py files for ever small GUI task. 
	
---------------------------
Release History
---------------------------
*EEG Annotator version 0.2*
*Release date: 2014-08-30*
What is new in V0.2:
	- Auto-EEG software in V0.1 used a python code, "edfplus.py", to read the information inside the EDF files including EDF header and EDF data records. 
	As this code reads the whole information inside the EDF file at once, the time of reading of the EDF files was increasing when the size of the EDF files 
	was increasing. The goal of this assignment was writing a new Python code, "ISIPEDFReader.py", for reading the EDF files in a way that it reads just the 
	data records within the time (st_time, en_time). Using this approach, every time that the user is moving the time scroll bar or changing timing scales, 
	the "main.py" file sends new (st_time, en_time) to "ISIPEDFReader.py" and "ISIPEDFReader.py" returns data records to "main.py" immediately.Then application 
	plots signals and their annotation whitin the time of the plot window. For this version "edfplus.py" has been replaced with "ISIPEDFReader.py". 
	Additionally, "main.py" and "EditPlotWidgen" has been edited.

*EEG Annotator version 0.2.1*	
*Release date: 2014-09-05*
	- Print option has been added in menu/file. Using this option, user can print whole the EEG file and save in a folder. The folder can be selected by user 
	and files will be saved in separate JPEG files. 	
	- One of the statements in "EditPlotWidgen.py" in class method of "EditPlotWidget.update()" has been edited. This statement could be one of the sources 
	for memory leak.
	
---------------------------
What is EEG Annotator anyway?
---------------------------
EEG annoator is a Python GUI tool to help annotating EEG files. The current version in under development and is not complete.

---------------------------
Requiements
---------------------------
Python V2.7x (or consistent) 
PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download
NumPy/SciPy : http://www.numpy.org/
dip.ui : http://www.riverbankcomputing.co.uk/software/dip/download

---------------------------
Files/Directories:
---------------------------
src :  source code
example_project: an example project.