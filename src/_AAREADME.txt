Requiements:
PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/download
NumPy/SciPy : http://www.numpy.org/
dip.ui : http://www.riverbankcomputing.co.uk/software/dip/download

Files:
main.py :  this is the enry point for the program.
Ui_MainWindow.ui :  Main user interface designed using uic  (part of Qt or PyQt lib)
Ui_MainWindow.py: Python code generated from Ui_MainWindow.ui . Note this file should NEVER edited or changed.
		  Any change should be applied to Ui_MainWindow.ui first and then convert it this file.
CustomItems.py: Custom graphic Items based on PyQt & PyQTgraph libraries.
EditPlotWidget.py: Main plot widget that we plot the wave forms and alows us to edit them (adding annotations).
ProjectManager.py: Manage a project (e.g. load/create etc)

Third party programs/libs:

edfplus.py :  read edf files.  https://github.com/breuderink/eegtools/blob/master/eegtools/io/edfplus.py

PyQtgraph:  provides some additional functions for plotting graphs (need PyQt to be installed). http://www.pyqtgraph.org/

