'''
Created on May 25, 2014

@author: Amir Harati

main program for EEG annotator V0.2.2

Note : This version has been edited by MGM. All of the statements which added or edited for this version 
       has been commented by this method: #MGM(V0.2.2):(Explanation)
'''

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg  # @NoMove @UnusedImport
import numpy as np  # @NoMove @UnusedImport
import shutil  # @NoMove @UnusedImport
import os as os
from ProjectManager import ProjectManager
from Ui_MainWindow import  Ui_MainWindow
import ISIPEDFReader    
from dip.ui import (Dialog, GroupBox)   #MGM(V0.2.2): To import dip.ui which implements a user interface declaratively.

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        
        #MGM(V0.2.1): This part is implementing multithreading techniques using Qtimer(0).In multithreaded applications,
        #you can use QTimer in any thread that has an event loop. A QTimer with a timeout of 0 will time out as soon as
        #all the events in the window system's event queue have been processed. This was used to do heavy work of 
        #the annotations' calculations while providing a snappy user interface. Otherwise after printing is finished it 
        #takes a couple of minutes to run QtGui.QApplication.instance().exec_() again.   
        self.timer = QtCore.QTimer()    #MGM(V0.2.1): To define a timer for using in self.print_plot() 
        self.timer.timeout.connect(self.print_plot) #MGM(V0.2.1): To run self.print_plot() after timer emits timeout signal
        self.print_plot_Qtimer_Counter=0    #MGM(V0.2.1): This is a counter that is used in self.print_plot() to calculate the number of pages which have been printed. We can control Qtimer.stop by using this counter. 
        
        
        #MGM(V0.2): These instance variables are defined for reading of the EDF files partially  
        #
        self.timeaxis_start=0   #MGM(V0.2): The starting point on the time axis in the plot window
        self.timeaxis_end=10    #MGM(V0.2): The ending point on the time axis in the plot window
        self.time_readedf_start=0   #MGM(V0.2): The starting point for reading raw data records from EDF file.    
        self.time_readedf_end=1     #MGM(V0.2): The ending point for reading raw data records from EDF file. In order than related function run for the first time, this value is chosen lesser than self.timeaxis_end.
        
        self._showLabels=False;
        self._needSave=False;
        
        self._script_dir=os.path.abspath(os.path.dirname(__file__));
        
        # User Interface  designed by designer
        #
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        
        # toolbar
        # MGM(V0.2.2): This part has been edited for creating the stand-alone executable. As after installing
        #              setup.exe, the application can be lunched in every folder, we should use a address which
        #              is not relative.
        self.viewGroup = QtGui.QActionGroup(self);   
        self.panAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/pan_mode.png'), 'Pan', self) 
        self.zoomAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/zoom_mode.png'), 'Zoom', self)
        self.editAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/edit_mode.png'), 'Edit', self)
        self.nextAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/next.png'), 'Next', self)
        self.backAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/prev.png'), 'Back', self)
        self.nextAction.setShortcut('Right')
        self.backAction.setShortcut('Left')
        
        self.panAction.setCheckable(True)
        self.panAction.setChecked(True); 
        self.zoomAction.setCheckable(True)
        self.editAction.setCheckable(True)
        self.panAction.setDisabled(True)
        self.zoomAction.setDisabled(True)
        self.editAction.setDisabled(True)
        self.nextAction.setDisabled(True)
        self.backAction.setDisabled(True)
        
        # connect to functions
        #
        self.panAction.triggered.connect(self.setPan)
        self.zoomAction.triggered.connect(self.setZoom)
        self.editAction.triggered.connect(self.setEdit)
        
        self.nextAction.triggered.connect(self.goNext);
        self.backAction.triggered.connect(self.goBack);
        
        self.ui.plotWidget.sigTimeRangeChanged.connect(self.EDFDynamicPlotter)    #MGM(V0.2): When the time range in the plot window is changing by moving slider or changing other features this signal will emit.        
        
        #connect  changed signal from EditPlotWidget
        #
        self.ui.plotWidget.sigDocChanged.connect(self.onDocChange)
        self.ui.plotWidget.sigConfirmed.connect(self.onConfirm)
        self.ui.plotWidget.sigRightAnnotationExist.connect(self.manageNextAnnotationButton)
        self.ui.plotWidget.sigLeftAnnotationExist.connect(self.manageBackAnnotationButton)
        
        self.viewGroup.addAction(self.panAction)
        self.viewGroup.addAction(self.zoomAction)
        self.viewGroup.addAction(self.editAction)
        
        self.toolbar=QtGui.QToolBar()
        
        self.toolbar.addAction(self.panAction)
        self.toolbar.addAction(self.zoomAction)
        self.toolbar.addAction(self.editAction)
        spacer = QtGui.QWidget() 
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.backAction)
        self.toolbar.addAction(self.nextAction)
        
        # MGM(V0.2.2): This part has been edited for creating the stand-alone executable. As after installing
        #              setup.exe, the application can be lunch in every folder, we should use a address which
        #              is not relative.        
        self.confirmAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/confirm.png'), 'Confirm', self)
        self.confirmAction.setDisabled(True)
        self.cancelAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/cancel.png'), 'Cancel', self)
        self.cancelAction.setDisabled(True)
        self.saveAction = QtGui.QAction(QtGui.QIcon(self._script_dir+'/resource/save.png'), 'Save', self)
        self.saveAction.setDisabled(True)
        
        self.saveAction.triggered.connect(self.savePressed)
        self.confirmAction.triggered.connect(self.confirmPressed)
        self.cancelAction.triggered.connect(self.cancelPressed)
        
        spacer = QtGui.QWidget() 
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.cancelAction)
        self.toolbar.addAction(self.confirmAction)
        self.toolbar.addAction(self.saveAction)
        
        self.addToolBar(self.toolbar)
        
        # Project manager : a class that contains all methods to manage(create,read,interpret) a project 
        #
        self.pmanager = None;
        self.project_directory=[];
        self.status="project_close"
        self.current_user=""; # current active username
        self.current_annotation_key=None;
        
    
        #connect signals to slots
        #
        # actionNew
        self.ui.actionNew.setDisabled(True)
        
        #actionOpen
        self.ui.actionOpen.triggered.connect(self.open_project)
        
        # MGM(V0.2.1 ): : When print option in menu is pressed by user, print_plot() will be called.
        self.ui.actionPrint.triggered.connect(self.print_plot)  #MGM(V0.2.1)
        
        # actionExit
        self.ui.actionExit.triggered.connect(self.exit)
            
        #amplitude scale
        self.ui.amplitudeSpinBox.setValue(0.00)
        self.ui.amplitudeSpinBox.setMinimum(1)
        self.ui.amplitudeSpinBox.setMaximum(5000)
        self.ui.amplitudeSpinBox.valueChanged.connect(self.ui.plotWidget.changeAmplitudescale)
        
        self.ui.timeSpinBox.setValue(10.0)  #MGM(V0.2): The parameter of setValue changed from 0 to 10.00 
        self.ui.timeSpinBox.setMinimum(1)
        self.ui.timeSpinBox.setMaximum(300)
        self.ui.timeSpinBox.valueChanged.connect(self.ui.plotWidget.setTimescale)
        
        self.ui.showLabelButton.pressed.connect(self.showLabelPressed)
        
        self.ui.markFinishButton.pressed.connect(self.markFinishPressed)
        self.ui.markFinishButton.setDisabled(True)
    
    
    def setPan(self):
        self.ui.plotWidget.vb_mode="pan"
        self.ui.plotWidget.viewBox.set_mode("pan")
    
    def setEdit(self):
        self.ui.plotWidget.vb_mode="add"
        self.ui.plotWidget.viewBox.set_mode("add")
        pass
    
    def setZoom(self):
        self.ui.plotWidget.vb_mode="zoom"
        self.ui.plotWidget.viewBox.set_mode("zoom")
        pass
    
    
    def manageBackAnnotationButton(self,state):
        if state:
            self.backAction.setEnabled(True)
        else:
            self.backAction.setDisabled(True)
                
    # if  user pressed next
    def goBack(self):
        self.ui.plotWidget.goBack()
        
    def manageNextAnnotationButton(self,state):
        if state:
            self.nextAction.setEnabled(True)
        else:
            self.nextAction.setDisabled(True)
                
    # if  user pressed next
    def goNext(self):
        self.ui.plotWidget.goNext()
        
    # by save we just copy current session to last session
    def savePressed(self):
        self.pmanager.save(self.current_annotation_key, self.current_user)
        self.needSave = False
        self.saveAction.setDisabled(True)
        
    #if cancel pressed
    #
    def cancelPressed(self):
        self.ui.plotWidget.cancelChanges();
        self.confirmAction.setDisabled(True)
        self.cancelAction.setDisabled(True)
        
    # if Confirm pressed
    #
    def confirmPressed(self):
        self.ui.plotWidget.confirmChanges();
        
        
    #when confirmed is done
    def onConfirm(self):
        self.pmanager.writeAnnotationFile(self.current_annotation_key, self.ui.plotWidget._annotations)
        # reload the label
        annotations = self.loadAnnotations(self.pmanager.annotation_files[self.current_annotation_key],self.pmanager.montage_order)
        self.ui.plotWidget.set_annotations(annotations)
        self.ui.plotWidget.pre_compute_view()   #MGM(V0.2): This line added because now pre_compute_view() is not a part of set_annotations()
        self.ui.plotWidget.update()
        self.confirmAction.setDisabled(True)
        self.cancelAction.setDisabled(True)
        self.needSave = True
        self.saveAction.setEnabled(True)
           
    # when document changes due to edit or add new annotations
    #
    def onDocChange(self):
        self.confirmAction.setEnabled(True)
        self.cancelAction.setEnabled(True)
        self.status="changed"
    
    
    def markFinishPressed(self):
        # check if user want to mark the last  file as finished.
        #
        
            choice = QtGui.QMessageBox.question(self,'Message','Do you want to mark '+self.current_annotation_key+'as <b>Finished</b>?', QtGui.QMessageBox.Yes |QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if choice == QtGui.QMessageBox.Yes:
                self.pmanager.add_finished_file(self.current_annotation_key);
                self.pmanager.finished_files.append(self.current_annotation_key)
                self.edfListUpdate();
            elif choice == QtGui.QMessageBox.Cancel:
                return;
         
    #MGM(V0.2.1): When print option in menu is pressed by user print_plot() will be called. It is using Qtimer(0)
    #             multi-threading method which has been described before.
    #
    def print_plot(self):
        
        
        #MGM(V0.2.1): Start Qtimer and initialize related parameters for printing
        if (self.print_plot_Qtimer_Counter==0):    

            # MGM(V0.2.2): This part is using dip.ui module. dip.ui module implements a toolkit independent API
            #              for defining a user interface declaratively. Using dip.ui we are avoiding to create a lot
            #              of .ui files and their related .py files for ever small task. Here we want to create a user
            #              interface to get start time and end time for printing EEG signals and their annotations.                        
            model = dict(start_time_print='0',end_time_print=str(self.ui.plotWidget.total_time_recording))  # MGM(V0.2.2): Create the model.
            view_factory = Dialog(GroupBox('start_time_print','end_time_print'),window_title="Print Setting")   # MGM(V0.2.2): Define the view.
            view = view_factory(model)  # MGM(V0.2.2): Create an instance of the view bound to the model.
            view.execute()  # MGM(V0.2.2): Enter the dialog's modal event loop.
            self.start_time_print = float(model['start_time_print'])    # MGM(V0.2.2): Receive start time for printing.
            self.end_time_print = float(model['end_time_print'])    # MGM(V0.2.2): Receive end time for printing.
            
            # MGM(V0.2.2): Check the parameters.
            if (self.start_time_print<0):
                self.start_time_print=0
            if  (self.end_time_print>self.ui.plotWidget.total_time_recording):
                self.end_time_print=self.ui.plotWidget.total_time_recording


            
            #MGM(V0.2.1): Open a dialog box for selecting a folder by user to save. Printed files will be saved in this folder.
            self.print_directory = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory", QtCore.QDir.currentPath());
            #MGM(V0.2.1): To start the Qtimer. It will be running until calling the timer.stop.
            self.timer.start(0)
            
            #MGM(V0.2.1): Calculate the number of pages which should be printed.
            #MGM(V0.2.2): Edited to calculate based on the parameters entered by the user.
            self.number_pages = int((self.end_time_print - self.start_time_print)/self.ui.plotWidget.time_scale) + 1
            
            
            #MGM(V0.2.1): To initialize progress bar.
            self.progress = QtGui.QProgressDialog("Printing files...", "Cancel", 0, self.number_pages, self)
            self.progress.setWindowModality(QtCore.Qt.WindowModal)
        
        #MGM(V0.2.1): Moves and plots pages for a new print action.
        #MGM(V0.2.2): Edited to calculate based on the parameters entered by the user.        
        self.ui.plotWidget.xpos_changed(self.start_time_print + (self.print_plot_Qtimer_Counter*self.ui.plotWidget.time_scale))
        self.ui.plotWidget.slider.setValue(self.start_time_print + (self.print_plot_Qtimer_Counter*self.ui.plotWidget.time_scale))
        
        #MGM(V0.2.1): To print plot window and export in .jpeg format using pyqtgraph library 
        self.exportplotpng = pg.exporters.ImageExporter.ImageExporter(self.ui.plotWidget.PlotWidget.plotItem.scene()) #MGM(V0.2.1): To export the plot. @UndefinedVariable
        self.exportplotpng.parameters()['width'] = 1500 #MGM(V0.2.1) The with of the resolution of jpeg files. 
        self.exportplotpng.export(self.print_directory + '\\' + str(self.print_plot_Qtimer_Counter) + '.jpg')    #MGM(V0.2.1): To save the files in the folder which has been selected by user previously.

        #MGM(V0.2.1): To increase the progress bar. 
        self.progress.setValue(self.print_plot_Qtimer_Counter)
        
        #MGM(V0.2.1): To calculate the number of pages which has been printed. 
        self.print_plot_Qtimer_Counter+=1
            
        #MGM(V0.2.1): To check if all pages have been printed or not. If yes timer will be stopped and progress bar will be finished.
        if (self.print_plot_Qtimer_Counter== self.number_pages):
            self.progress.setValue(self.number_pages)   #MGM(V0.2.1): To finish the progress bar.
            self.timer.stop()   #MGM(V0.2.1): To stop the timer 
            self.print_plot_Qtimer_Counter=0    #MGM(V0.2.1): To reset the counter of number of pages which have been printed. 

        #MGM(V0.2.1): To implement the cancel button in progress bar.        
        if self.progress.wasCanceled():
            self.progress.setValue(self.number_pages)
            self.timer.stop()
            self.print_plot_Qtimer_Counter=0
        
   
    # called when show label button pressed
    #
    def showLabelPressed(self):
        if self._showLabels:
            
            self._showLabels = False;
            self.ui.plotWidget.hideLabels();
          
        else:
            self._showLabels = True;                
            self.ui.plotWidget.showLabels();
            
    # redirect the close event into  exit function 
    #
    def closeEvent(self,ev):  
        if self.exit():
            ev.accept();
        else:
            ev.ignore();
      
    # manage exiting from the program
    #
    def exit(self):    
        
        if self.saveAction.isEnabled():
            choice = QtGui.QMessageBox.question(self,'Warning','Do you want to save changes?', QtGui.QMessageBox.Yes |QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if choice == QtGui.QMessageBox.Cancel:
                return False;
            elif choice == QtGui.QMessageBox.Yes:
                self.savePressed();               
            else:
                choice_final=QtGui.QMessageBox.question(self,'Warning','All changes will be lost',QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,QtGui.QMessageBox.Cancel);
                if choice_final == QtGui.QMessageBox.Cancel:
                    return False;
               
        if self.confirmAction.isEnabled():
            choice = QtGui.QMessageBox.question(self,'Warning','You made some changes without confirming and saving. Do you like to apply and save the changes?', QtGui.QMessageBox.Yes |QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if choice == QtGui.QMessageBox.Cancel:
                return False;
            elif choice == QtGui.QMessageBox.Yes:
                self.confirmPressed()
                self.savePressed();
            else:
                choice_final=QtGui.QMessageBox.question(self,'Warning','All changes will be lost',QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,QtGui.QMessageBox.Cancel);
                if choice_final == QtGui.QMessageBox.Cancel:
                    return False;        
    
        QtGui.qApp.quit();
        return True
        
    # open a project
    #    
    def open_project(self):
        self.pmanager = ProjectManager();
        self.ui.plotWidget.clear()
        self.ui.plotWidget.reset_annotation() #MGM(V0.2): For erasing annotations which have been loaded for previous files.
        filter_pname=QtCore.QString() #MGM(V0.2): The name of filter changed to filter_pname for removing the warning
        pname= str(QtGui.QFileDialog.getOpenFileName(self, 'Open Project', 'Projects','*.prj',filter_pname))
        
        # pass to project manager
        if pname:
            self.ui.markFinishButton.setDisabled(True)
            self.project_directory = os.path.dirname(pname)
            os.chdir(self.project_directory)
            # read the project
            self.pmanager.read(pname)    
            
            # ask for username and  "login"  the user (or add it  the list of users or close the project)
            while 1==1:
                text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter your user-name:')
                if ok:
                    
                    username=str(text);
                    if username in self.pmanager.usernames or self.pmanager.project_info["add_new_user"] == True:
                        self.status = "project_open"
                    else:
                        self.status = "project_close"
                            
                    break;
                else:
                    choice = QtGui.QMessageBox.question(self, 'Message',"Do you want to continue?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                    if choice == QtGui.QMessageBox.No:
                        self.status="project_close"
                        break;
            # return if the project is not open        
            if self.status == "project_close":        
                return 
            
            if username in self.pmanager.usernames:
                    choice = QtGui.QMessageBox.question(self, 'Message',"Are you "+self.pmanager.users[username]+"?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                    if choice == QtGui.QMessageBox.Yes:
                        self.status="project_open"
                    else:
                        self.status="project_close"
                            
            elif self.pmanager.project_info["add_new_user"]:
                    while 1==1:
                        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Please, enter your first and last names:')
                        if ok:
                            self.pmanager.add_user(username,str(text))
                            break;
                        else:
                            choice = QtGui.QMessageBox.question(self, 'Message',"Do you want to continue?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                            if choice == QtGui.QMessageBox.No:
                                self.status="project_close"
                                break;       
                    if self.status == "project_close":
                        return;    
            self.current_user = username;        
            # Now that user logged in successfully continue:
            # Create (if not existed) necessary directory structure (project_dir/username/root) and copy needed files
            self.pmanager.create_dir_structure(self.current_user)
            self.edfListUpdate();
            
    def edfListUpdate(self):
        
        self.ui.edfListWidget.clear()
        for eeg_file in self.pmanager.eeg_files:
            
            self.litem=QtGui.QListWidgetItem(self.ui.edfListWidget)
            self.litem.setText(eeg_file)
            if eeg_file in self.pmanager.finished_files:
                icon=QtGui.QIcon(self._script_dir+"/resource/accept.png")
            else:
                icon=QtGui.QIcon(self._script_dir+"/resource/blank.png")
                    
            self.litem.setIcon(icon)
            
        self.ui.edfListWidget.itemClicked.connect(self.edfChanged)

    def loadAnnotations(self,fname,map2order):
        with open(fname) as f:
            content = f.readlines()  
        annotations = [];
        
        for line in content:
            tmp=line.split(",")
            
            chn_num=map2order[int(tmp[0])]
            st=float(tmp[1])
            en=float(tmp[2])
            cl=int(tmp[3])
            annotations.append([chn_num,st,en,cl])
        return annotations;    
                       
    def  edfChanged(self,curr):
        
        self.timeaxis_start=0   #MGM(V0.2): To reset this parameter after opening a new EDF file. 
        self.timeaxis_end=10    #MGM(V0.2): To reset this parameter after opening a new EDF file.
        self.time_readedf_start=0   #MGM(V0.2): To reset this parameter after opening a new EDF file.
        self.time_readedf_end=10    #MGM(V0.2): To reset this parameter after opening a new EDF file.

        key=str(curr.text())
        
        # first check to see if the current open file is confirmed or saved
        # then ask the user if the task (for the open file) is finished or not
        
        if self.saveAction.isEnabled() or self.confirmAction.isEnabled():
            choice = QtGui.QMessageBox.question(self,'Warning','You made some changes without confirming and saving. Do you like to apply and save the changes?', QtGui.QMessageBox.Yes |QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if choice == QtGui.QMessageBox.Cancel:
                return;
            elif choice == QtGui.QMessageBox.Yes:
                self.confirmPressed()
                self.savePressed();
            else:
                choice_final=QtGui.QMessageBox.question(self,'Warning','All changes will be lost',QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,QtGui.QMessageBox.Cancel);
                if choice_final == QtGui.QMessageBox.Cancel:
                    return;     
     

        
        self.needSave = False;
        
        # enable the toolbar
        #
        self.panAction.setEnabled(True)
        self.zoomAction.setEnabled(True)
        self.editAction.setEnabled(True)
        
        # disable confirm, cancel and save
        self.cancelAction.setDisabled(True)
        self.confirmAction.setDisabled(True)
        self.saveAction.setDisabled(True)
        
        self.backAction.setDisabled(True)
        self.nextAction.setDisabled(True)
        
        self.ui.markFinishButton.setEnabled(True)
        
        self.current_annotation_key=key;
        fname = self.pmanager.eeg_files_full[key]
        
        y, sample_rate, physical_channels, time,tmp,  self.ui.plotWidget.total_time_recording= ISIPEDFReader.load_edf(fname,0,100)  #MGM(V0.2): Reads EDF file for 100 seconds. The variable of total_time_recording is using to transfer the the total time of the recording to EditPlotWidget module# @UnusedVariable 
        
        # calculate the montage
        #
        self.pmanager.calculate_montage(physical_channels)
        
        cm_id=[]
        cm_name=[];
        cm_color=[]
        for k in self.pmanager.class_mapping:
            cm_id.append(k)
            cm_name.append(self.pmanager.class_mapping[k])
           
        for k in self.pmanager.class_mapping_colors:
            cm_color.append(self.pmanager.class_mapping_colors[k])    
        self.ui.plotWidget.setClassMapping(cm_id,cm_name)
        
        self.ui.plotWidget.setClassColorMapping(cm_id,cm_color)
        
        
        self.ui.plotWidget.setSignalNo(len(self.pmanager.montage_ids))
       
        sig_labs=[self.pmanager.montage_names[self.pmanager.montage_map_order2id[i]] for i in self.pmanager.montage_map_order2id]
        self.ui.plotWidget.setSignalLabels(sig_labs)
        self.ui.plotWidget._x=time;
        
        for id in self.pmanager.montage_ids:  # @ReservedAssignment
           
            if len(self.pmanager.montage_pairs[id])==2:
                self.ui.plotWidget._y[self.pmanager.montage_order[id]] = y[self.pmanager.montage_pairs[id][0]] - y[self.pmanager.montage_pairs[id][1]]
            elif len(self.pmanager.montage_pairs[id])==1:
                self.ui.plotWidget._y[self.pmanager.montage_order[id]] = y[self.pmanager.montage_pairs[id][0]] 
            else:
                print "montage definition is either one or two channels"
                exit()
                
        # remove y
        del y;
        
        amps=[self.pmanager.montage_scales[self.pmanager.montage_map_order2id[i]] for i in self.pmanager.montage_map_order2id] 
              
        
        # the assumption is that the first channel id is a representative  of all (special channels with different scale should be set using config)
        self.ui.plotWidget.setAmplitudescale(amps) 
        annotations = self.loadAnnotations(self.pmanager.annotation_files[key],self.pmanager.montage_order)
        
        self.ui.plotWidget.set_annotations(annotations)
        self.ui.plotWidget.pre_compute_view()   #MGM(V0.2): This line added because now pre_compute_view() is not a part of set_annotations() 
        
        
        ccolor = [self.pmanager.montage_color[self.pmanager.montage_map_order2id[i]] for i in self.pmanager.montage_map_order2id ]
       
        self.ui.plotWidget.setChannelColor(ccolor)
        
        self.ui.amplitudeSpinBox.setValue(self.pmanager.montage_scales[self.pmanager.montage_ids[0]]) 
              
        self.ui.plotWidget.set_slider(self.ui.plotWidget)   #MGM(V0.2): This line moved here. As running this line sooner is causing an error regarding recalling the class method of EDFDynamicPlotter.
        self.ui.plotWidget.update()
        
        # should be after update other wise it call the update function prematurely 
       
        self.ui.plotWidget.setTimescale(10) #MGM(V0.2): This line moved here to reset time scale when EDF file changes.
        self.ui.timeSpinBox.setValue(10)    #MGM(V0.2): This line moved here to reset time scale when EDF file changes.
    
        self.ui.showLabelButton.setEnabled(True)
        
        self.ui.plotWidget.check_annotation(0, 10)  #MGM(V0.2): To check annotations when a new EDF file selects by user. Without this line Go Next annotation will remain inactive, when a new EDF file is loaded. 
        

    #MGM(V0.2): This class method reads EDF file - which has been loaded before - partially and plot signals and 
    #           related annotations within the time of the plot window. For having a smoother slider this variable 
    #           is reading raw data recording from (timeaxis_start - 100 sec) to (timeaxis_end + 100 sec).
    # 
    def EDFDynamicPlotter(self):

        key=self.current_annotation_key    #MGM(V0.2): Assign EDF file which has been selected by user before.    
        fname = self.pmanager.eeg_files_full[key]   #MGM(V0.2): Open EDF file which has been selected before.
        
        self.timeaxis_start=int(self.ui.plotWidget.timeaxis_start)    #MGM(V0.2): Getting the starting point on the time axis in the plot window. We need integer of this value to have an integer multiple of duration of time recording.
        self.timeaxis_end=int(self.ui.plotWidget.timeaxis_end)     #MGM(V0.2): Getting the ending point on the time axis in the plot window. We need integer of this value to have an integer multiple of duration of time recording.
        
        if ((self.timeaxis_end>self.time_readedf_end) or (self.timeaxis_start<self.time_readedf_start)):    #MGM(V0.2): This line is checking the value of time axis when time range changes. If the time is out of 200 sec buffer it reads new raw data records.
            self.time_readedf_start=self.timeaxis_start - 100   #MGM(V0.2):For having a smoother slider this variable is reading raw data recording from (timeaxis_start - 100 sec) to (timeaxis_end + 100 sec).
            self.time_readedf_end=self.timeaxis_end + 100   #MGM(V0.2):For having a smoother slider this variable is reading raw data recording from (timeaxis_start - 100 sec) to (timeaxis_end + 100 sec).
            if(self.time_readedf_start<0):  #MGM(V0.2): To limit the starting point of time axis 
                self.time_readedf_start=0   #MGM(V0.2): To limit the starting point of time axis
            if (self.time_readedf_end>self.ui.plotWidget.total_time_recording): #MGM(V0.2): To limit the ending point of time axis 
                self.time_readedf_end=self.ui.plotWidget.total_time_recording   #MGM(V0.2): To limit the ending point of time axis 
            y, sample_rate, physical_channels, time, tmp, self.ui.plotWidget.total_time_recording= ISIPEDFReader.load_edf(fname,self.time_readedf_start,self.time_readedf_end)  #MGM(V0.2): Reads EDF file Partially. The variable of total_time_recording is using as transfer the the total time of the recording to EditPlotWidget module# @UnusedVariable 
            
            sig_labs=[self.pmanager.montage_names[self.pmanager.montage_map_order2id[i]] for i in self.pmanager.montage_map_order2id]   #MGM(V0.2):
            self.ui.plotWidget.setSignalLabels(sig_labs)    #MGM(V0.2)
            self.ui.plotWidget._x=time; #MGM(V0.2)
            
            for id in self.pmanager.montage_ids:  #MGM(V0.2) # @ReservedAssignment    
               
                if len(self.pmanager.montage_pairs[id])==2: #MGM(V0.2)
                    self.ui.plotWidget._y[self.pmanager.montage_order[id]] = y[self.pmanager.montage_pairs[id][0]] - y[self.pmanager.montage_pairs[id][1]]  #MGM(V0.2):
                elif len(self.pmanager.montage_pairs[id])==1:   #MGM(V0.2)
                    self.ui.plotWidget._y[self.pmanager.montage_order[id]] = y[self.pmanager.montage_pairs[id][0]]  #MGM(V0.2) 
                else:   #MGM(V0.2):
                    print "montage definition is either one or two channels"    #MGM(V0.2)
                    exit()  #MGM(V0.2)                    
            # remove y
            del y;  #MGM(V0.2):            
            #annotations = self.loadAnnotations(self.pmanager.annotation_files[key],self.pmanager.montage_order) #MGM(V0.2)    #MGM(V0.2.1):To make more efficient    #MGM(V0.2):To make more efficient the program the program
            #self.ui.plotWidget.set_annotations(annotations) #MGM(V0.2)    #MGM(V0.2.1):To make more efficient the program            
            
            ccolor = [self.pmanager.montage_color[self.pmanager.montage_map_order2id[i]] for i in self.pmanager.montage_map_order2id ]  #MGM(V0.2):
            self.ui.plotWidget.setChannelColor(ccolor)  #MGM(V0.2):            
            
            self.ui.amplitudeSpinBox.setValue(self.pmanager.montage_scales[self.pmanager.montage_ids[0]])   #MGM(V0.2): 
            self.ui.plotWidget.update() #MGM(V0.2):            
            # should be after update other wise it call the update function prematurely 
            self.ui.showLabelButton.setEnabled(True);   #MGM(V0.2):
        
              
                    
# main function
def main():
    
    app = QtGui.QApplication([])  # @UnusedVariable
    window=Main()
    window.show()
   
    #sys.exit(app.exec_())
    QtGui.QApplication.instance().exec_()
    os._exit(0); # to remove segmentation fault error


# run the main function
if __name__ == "__main__":
    main()
    