'''
Created on May 17, 2014

@author: Amir Harati


main program for EEG annotator V0.2.1

Note : This version has been edited by MGM. All of the statements which added or edited for this version 
       has been commented by this method: #MGM(V0.2.1):(Explanation)
'''
from pyqtgraph.Qt import QtGui, QtCore  # @UnusedImport
import pyqtgraph as pg  # @NoMove @UnusedImport
import numpy as np  # @NoMove @UnusedImport
from CustomItems import *  # @NoMove @UnusedWildImport
import copy 


class EditPlotWidget(pg.Qt.QtGui.QWidget):
    """ EditPlotWidget is  Widget based on PlotWidget that adds several features including:
        1- having scroll bar 2-show multiple channels in one plot 3-show annotation for each signal
        4- control over the scale for each signal 5- time scale for all signals (how many seconds per page)
        6- support tree event based modes: 6-1- pan 6-2- zoom 6-3-edit 6-4-remove.
        7- edit/remove allows user to define  new labels over each (or multiple) signal(s) and select and annotate 
        the signal based on some predefined classes passed to the widget by user.
    """
    sigDocChanged=QtCore.Signal()
    sigConfirmed=QtCore.Signal()
    sigTimeRangeChanged=QtCore.Signal()  #MGM(V0.2): When the time range in the plot window is changing by moving slider or changing other features this signal will emit.
    
    sigRightAnnotationExist = QtCore.Signal(bool)
    sigLeftAnnotationExist  = QtCore.Signal(bool)
    
    def __init__(self, parent = None,signals_no = 1,mode = 'pan',time_scale = 10,amplitude_scale = None,signal_labels = None,background='default', **kargs):
        """
            parameters:
            1- signal_no :  number of signal to plot.
            2- mode: mode of the widget.('pan','zoom','edit','remove')
            3- time_scale: seconds per page
            4- amplitude_scale: for each signal (channel) determines each pixel is equivalent to
            how much micro-Volts and  should be a vector with length equals to "signals_no"
            5- signal_labels: a list of string that contains labels for each signal (left of y-axis)
        """
        
        #MGM(V0.2): These instance variables are defined for plotting and controlling the time axis  
        #
        self.timeaxis_start=0   #MGM(V0.2): The starting point on the time axis in the plot window
        self.timeaxis_end=20    #MGM(V0.2): The ending point on the time axis in the plot window
        self.total_time_recording = 100 #MGM(V0.2): The variable of total_time_recording is using to plot the axis time for the whole time of the recording.
         
        # internal variables
         
        #number of all annotations (including removed ones; this is used to generate unique ids)
        self._annotation_count=0;
        self._annotation_objects={} # graphic objects
        self._preComputedView={}
        self._sorted_annotation_objects=[];
         
        self.left_most_id=0;
        self.right_most_id=0;
        self._remove_list=[]; # id of  objects to be removed
        self._add_list=[]; #id to be added
        self._change_list=[]; #id of annotation objects that has changed
         
        self._nextRightAnnotation=None;
        self._nextLeftAnnotation=None;
         
        self._empty_objects=0; # number of empty (newly created but not assigined) annotations on the screen
         
        self._selected_list=[]; # a list of selected  annotation objects (ids) by  mouse  drag or other means
         
        self._showLabels=False;
         
        # data  (might need to change for performance)
        self._x=[1,2]; #MGM(V0.2): Default values has been changed. 
        self._y={}; # dict for y  
                
        #class mapping :  A dictionary in which keys are  class numbers and map is the  class name.
        self.class_mapping={}
        self.class_color_mapping={}
         
        self.channel_color={}
         
        # number of signals to be displayed
        # maximum and minimum for the y-axis
        self.ymax=10000;
        self.ymin=0;
        self.setSignalNo(signals_no)
        self.time_scale=time_scale;
        self.posx=0;
        if amplitude_scale == None:
            self.amplitude_scale=[1 for k in range(self.signals_no)];  # @UnusedVariable
        elif len(amplitude_scale)== self.signals_no:
            self.amplitude_scale=amplitude_scale;
        elif len(amplitude_scale)==1:
            self.amplitude_scale=[amplitude_scale for k in range(self.signals_no)];  # @UnusedVariable
                
        else:
            print "length of amplitude_scale list should be the same as signals_no"
            exit(); 
         
        if signal_labels == None:
            self.signal_labels=["" for k in range(self.signals_no)];  # @UnusedVariable
        elif len(signal_labels)== self.signals_no:
            self.signal_labels=signal_labels;
        else:
         
            print "length of signal_labels list should be the same as signals_no"
            exit();     
        self.sig_names={}; # where we  save the text box objects
      
        # annotation list:  This list is used to store the annotations for each channel
        # [[ch,st,en,cl],[ch,st,en,cl],...]
        # ch is the channel number, st  start time in second, en end time and cl is the class
        # _annotations  is the internal annotation list  and annotations is the list avalible to
        # outside world.
        self._annotations={};  #logical objects
        self.annotations=[];
        # a flag that determines if the Widget accept new annotation to set by outside world
        self.accept_annotation=1;
        
        # internal state to indicate if this is confirmed
        self._isConfirmed = True
        self._annotations_old = {} 
         
        # annotation menu
        self.annotation_menu1=QtGui.QMenu()
        self.annotation_menu1.setTitle("")
        self.annotation_menu1_edit=QtGui.QAction("Edit", self.annotation_menu1)      
        self.annotation_menu1_edit.triggered.connect(self.menu1_edit) 
        self.annotation_menu1.addAction(self.annotation_menu1_edit)
        self.annotation_menu1.annotation_menu_edit=self.annotation_menu1_edit;
        self.annotation_menu1_remove=QtGui.QAction("Remove", self.annotation_menu1)      
        self.annotation_menu1_remove.triggered.connect(self.menu1_remove) 
        self.annotation_menu1.addAction(self.annotation_menu1_remove)
        self.annotation_menu1.annotation_menu_remove=self.annotation_menu1_remove;
                 
        self.annotation_menu2=QtGui.QMenu()
        self.annotation_menu2.setTitle("Edit Mode")
         
        self.annotation_menu3=QtGui.QMenu()
        self.annotation_menu3.setTitle("Edit Mode")

        self.customMenu1=None;
        self.customMenu2=None;
        
        # menu for channels 
        self.channel_menu=QtGui.QMenu()
        self.customChannelMenu=None;
        
        self.selected_annotation_id=None;
        
        #check for viewBox and set it if not specified
        if 'viewBox' in kargs:
            # just provided for more customized vbox however any vbox used here should support
            # and follow CustomViewBox(perhaps should be derivative) 
            self.viewBox = kargs['viewBox']
        else:
            self.viewBox = CustomViewBox();
            kargs['viewBox']=self.viewBox;
            self.vb_mode = "pan"
            self.viewBox.set_mode(self.vb_mode)
         
        #connect viewbox signals
        self.viewBox.sigLRegionSelected.connect(self.add_annotations)
        self.viewBox.sigRRegionSelected.connect(self.select_annotations)
        self.viewBox.sigRightClick.connect(self.right_click_process)
        self.viewBox.sigLeftClick.connect(self.left_click_process)
        self.viewBox.sigPanDrag.connect(self.updatePanDrag)
                
        # initilaize the QWidget   
        pg.Qt.QtGui.QWidget.__init__(self, parent)
          
        # make a PlotWidget item and pass needed parameters
        self.PlotWidget=pg.PlotWidget(parent=parent, background=background,**kargs)
        self.PlotWidget.setYRange(self.ymin,self.ymax)
        self.PlotWidget.plotItem.setClipToView(clip=True)
        self.PlotWidget.plotItem.hideAxis('left')
        self.PlotWidget.plotItem.showGrid(x=True, y=True,alpha= .1) 
          
        self.ylabels=[];
        for i in range(self.signals_no):  # @UnusedVariable
            self.ylabels.append(pg.QtGui.QLabel());
                                
        self.set_xlim = self.PlotWidget.setXRange
        self.set_xlim(0, self.time_scale)
              
        #define a layout for the widget
        self.lygrid=QtGui.QGridLayout(self);
         
         
             
        #add items to the layout
        self.lygrid.addWidget(self.PlotWidget,0,1,self.signals_no+1,1)
         
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, parent=parent)
          
        self.lygrid.addWidget(self.slider,self.signals_no+2,1,1,1)
        self.set_slider(self)
 
    def sendChangedSignal(self):
        self.sigDocChanged.emit();
       
    
    def connect_channel_name_signals(self,key):
        self.sig_names[key].sigMouseClicked.connect(self.set_selected_channel_id)
        
    def set_selected_channel_id(self,id):  # @ReservedAssignment
        self.selected_channel_id=id; 
        
        if id in self.sig_names:            
            self.customChannelMenu.set_ampScale(id,self.entered_amplitue_scale[id])    
        
    def prepare_ChannelMenu(self):
        if self.customChannelMenu==None:
            self.customChannelMenu=CustomChannelMenu();
            wac=QtGui.QWidgetAction(self.channel_menu)
            wac.setDefaultWidget(self.customChannelMenu);
            self.channel_menu.addAction(wac)
            self.customChannelMenu.sigSpinChanged.connect(self.process_ChannelMenu)
    
    def process_ChannelMenu(self,id,val):  # @ReservedAssignment
        self.entered_amplitue_scale[id] = val
        self.setAmplitudescale(self.entered_amplitue_scale)
        self.update()
                    
    def prepare_CustomMenu(self):
        
        if self.customMenu1==None:             
            self.customMenu1=CustomContextMenu(self.class_mapping,self.class_color_mapping);
            wac=QtGui.QWidgetAction(self.annotation_menu2)
            wac.setDefaultWidget(self.customMenu1);
            self.annotation_menu2.addAction(wac)
            self.customMenu1.sigReturn.connect(self.process_CustomMenu)
            
        if self.customMenu2==None:          
            self.customMenu2=CustomContextMenu(self.class_mapping,self.class_color_mapping);
            wac=QtGui.QWidgetAction(self.annotation_menu3)
            wac.setDefaultWidget(self.customMenu2);
            self.annotation_menu3.addAction(wac)
            self.customMenu2.sigReturn.connect(self.process_CustomMenu)
         
    def process_CustomMenu(self,classid):
        # backup
        if self._isConfirmed:
            self._annotations_old = copy.deepcopy(self._annotations);
            self._isConfirmed = False
            
        if classid == -2 : #  remove
            self.sendChangedSignal();

            if len(self._selected_list)>0:
                for id in self._selected_list:  # @ReservedAssignment
                    if self._annotation_objects[id].isEmpty():
                        self._annotation_objects[id].deselect()
                        self._annotation_objects[id].set_for_remove();
                        self._annotations[id][4]=False;
                        self._annotations[id][5]=True;
                        self._annotations[id][6] = True
                        
                    else:                        
                        self._annotation_objects[id].deselect()
                        self._remove_list.append(id)  
                        if id in self._annotation_objects:
                            self._annotation_objects[id].set_menu(self.annotation_menu1)  
                        self._annotation_objects[id].set_for_remove(); 
                        self._annotations[id][4]=False;
                        self._annotations[id][5]=True;
                        self._annotations[id][6] = False
                    self._selected_list=[];        
                return
                    
            if self._annotation_objects[self.selected_annotation_id].isEmpty():
                self._annotation_objects[self.selected_annotation_id].set_for_remove();
                self._annotations[self.selected_annotation_id][4]=False;
                self._annotations[self.selected_annotation_id][5]=True;
                 
                self._annotations[self.selected_annotation_id][6]=True
                return
             
            self._annotation_objects[self.selected_annotation_id].set_for_remove();
            self._remove_list.append(self.selected_annotation_id)
            self._annotations[self.selected_annotation_id][4]=False;
            self._annotations[self.selected_annotation_id][5]=True;
            self._annotations[self.selected_annotation_id][6] = False
            
        elif classid>-1: #-1:cancel button
            
            self.sendChangedSignal()      
            if len(self._selected_list)>0: # multiple selection
           
                for id in self._selected_list:     # @ReservedAssignment
                    if self._annotation_objects[id].isEmpty():
                        self._empty_objects -=1;
                        self._add_list.append(id)
                    else:
                        self._change_list.append(id)    
                         
                    self._annotation_objects[id].set_for_update();
                     
                    # update _annotation
                    self._annotations[id][4]=False;
                    self._annotations[id][5]=False;
                    self._annotations[id][3]=classid;
                    self._annotations[id][1]=self._annotation_objects[id].pos().x();
                    self._annotations[id][2]=self._annotation_objects[id].pos().x() + self._annotation_objects[id].size().x();
                    self._annotations[id][6] = False
                    #self._annotation_objects[id].setState(isSelected=False,isRemoved=False);
                     
                    color=self.class_color_mapping[classid];
                    self._annotation_objects[id].setBrush(color)
                    self._annotation_objects[id].setContent(classid)
                    self._annotation_objects[id].update()
                    if id in self._remove_list:
                        self._remove_list.remove(id) # remove form _remove_list
                    self._annotation_objects[id].set_for_update();
                     
                    self._annotation_objects[id].setState(isLocked=True,isRemoved=False,isSelected=False)    
                    self._annotation_objects[id].set_menu(self.annotation_menu1)
                self._selected_list=[];
                return         
             
            if self._annotation_objects[self.selected_annotation_id].isEmpty():
                self._empty_objects -=1;
                self._add_list.append(self.selected_annotation_id)
            else:
                self._change_list.append(self.selected_annotation_id)    
                
            # update _annotation
            self._annotations[self.selected_annotation_id][4]=False;
            self._annotations[self.selected_annotation_id][5]=False;
            self._annotations[self.selected_annotation_id][6] = False
            self._annotations[self.selected_annotation_id][3]=classid;
            self._annotations[self.selected_annotation_id][1]=self._annotation_objects[self.selected_annotation_id].pos().x();
            self._annotations[self.selected_annotation_id][2]=self._annotation_objects[self.selected_annotation_id].pos().x() + self._annotation_objects[self.selected_annotation_id].size().x();     
                                  
            color=self.class_color_mapping[classid];
        
            self._annotation_objects[self.selected_annotation_id].setBrush(color)
            self._annotation_objects[self.selected_annotation_id].setContent(classid)
            self._annotation_objects[self.selected_annotation_id].update()
            if self.selected_annotation_id in self._remove_list:
                self._remove_list.remove(self.selected_annotation_id) # remove form _remove_list
            self._annotation_objects[self.selected_annotation_id].set_for_update();
        
           
            self._annotation_objects[self.selected_annotation_id].setState(isLocked=True,isRemoved=False)    
            self._annotation_objects[self.selected_annotation_id].set_menu(self.annotation_menu1)
        
        if classid == -3: #ok pressed without selecting a class(move)
            # add  to sorted list
            self._annotations[self.selected_annotation_id][4]=False;
            self._annotations[self.selected_annotation_id][5]=False;
            self._annotations[self.selected_annotation_id][6] = False
            self._annotations[self.selected_annotation_id][1]=self._annotation_objects[self.selected_annotation_id].pos().x();
            self._annotations[self.selected_annotation_id][2]=self._annotation_objects[self.selected_annotation_id].pos().x() + self._annotation_objects[self.selected_annotation_id].size().x();             
            
            self.sendChangedSignal();
            if self._annotation_objects[self.selected_annotation_id].isEmpty()==False:
                self._annotation_objects[self.selected_annotation_id].set_for_update();
                self._annotation_objects[self.selected_annotation_id].setState(isLocked=True,isRemoved=False)    
                self._annotation_objects[self.selected_annotation_id].set_menu(self.annotation_menu1)
        
                self._annotations[self.selected_annotation_id][4]=False;
                self._annotations[self.selected_annotation_id][5]=False;
                self._annotations[self.selected_annotation_id][6] = False
         
    def setClassMapping(self,class_ids,class_names):
        for i,j in zip(class_ids,class_names):
            self.class_mapping[i] = j
           
              
    def setClassColorMapping(self,class_ids,class_colors):
        for i,j in zip(class_ids,class_colors):
            self.class_color_mapping[i] = j
           
    def setSignalNo(self,signal_no):
        self.signals_no = signal_no
        #steps between each signal
        self.ystep=(self.ymax-self.ymin)/self.signals_no;
         
        #compute the shift  needed to add to each signal
        self.yshift=[];
        for i in range(self.signals_no):
            self.yshift.append(self.ymin+i*self.ystep)
    
    def setSignalLabels(self,signal_labels):
        self.signal_labels = signal_labels
                 
    def setTimescale(self,timescale):
        h=self.return_channel_height()
        self.time_scale   = timescale
        self.xpos_changed(self.PlotWidget.plotItem.vb.state['viewRange'][0][0])
        for tbox in self.sig_names:
            self.sig_names[tbox].setSize([self.time_scale/15,max(h/4,360)])
            
        self.pre_compute_view()
        self.plot_annotations()
        self.update()
        
    def changeAmplitudescale(self,amplitude_scale):
        self.setAmplitudescale(amplitude_scale)   
        self.update()
        
    def setAmplitudescale(self,amplitude_scale):
        
        '''
            scale = 100 -->  100 microVolt / 10 mm . Since each mm is  K pixel it means 100 MVol/k10
            the output is :  K/scale
        '''
        K= 37 *(self.ymax-self.ymin)/self.PlotWidget.height(); # each mm is around 3.7 pixels 10 mm is 37 pixels
        
        if amplitude_scale == None:
            self.amplitude_scale=[K for k in range(self.signals_no)];
            self.entered_amplitue_scale = self.amplitude_scale;
        elif type(amplitude_scale) is int:
            self.amplitude_scale=[K/amplitude_scale for k in range(self.signals_no)];
            self.entered_amplitue_scale = [amplitude_scale for k in range(self.signals_no)];
        elif type(amplitude_scale) is float:
            self.amplitude_scale=[K/amplitude_scale for k in range(self.signals_no)];     
            self.entered_amplitue_scale = [amplitude_scale for k in range(self.signals_no)];              
        elif len(amplitude_scale)== self.signals_no:
            self.amplitude_scale=[K/amplitude_scale[k] for k in range(self.signals_no)];
            self.entered_amplitue_scale = [amplitude_scale[k] for k in range(self.signals_no)];
        else:
            print "length of amplitude_scale list should be the same as signals_no"
            exit();
         
    def updatePanDrag(self,posx):
        self.xpos_changed(posx)
        self.slider.setValue(posx)
    
    def clear(self):
        self.PlotWidget.plotItem.clear(); 
        self._x=[1,2];
        self._y={}
            
    def update(self):
        self.PlotWidget.plotItem.clear();     
        for i in range(self.signals_no):      
            self.plot(i,x=None,y=None)   
        #MGM(V0.2.1):to make more efficient the program and it probably solves the memory leak which has been viewed before.        
        rlist = []  #MGM(V0.2.1)
        for k in self._annotation_objects:  #MGM(V0.2.1)
            rlist.append(k) #MGM(V0.2.1)
        for r in rlist: #MGM(V0.2.1)
            del self._annotation_objects[r] #MGM(V0.2.1)
        #self._annotation_objects ={}     #MGM(V0.2.1):to make more efficient the program and it probably solves the memory leak which has been viewed before.
        self.plot_annotations(); 
                                
    def connect_to_signals(self,key):
        self._annotation_objects[key].sigMouseClicked.connect(self.set_selected_annotation_id)
        self._annotation_objects[key].sigShiftMouseClicked.connect(self.add_to_selected)
        self._annotation_objects[key].sigMoved.connect(self.check_collisions)
        self._annotation_objects[key].sigRemoveRequested.connect(self.remove_process)
        self._annotation_objects[key].sigHover.connect(self.highlight)
        self._annotation_objects[key].sigRegionChanged.connect(self.regionChange)
    
    # update _annotation in case the size  changed
    def regionChange(self):
        for key in self._annotation_objects:
            if key in self._annotations:
                self._annotations[key][1] = self._annotation_objects[key].pos().x();
                self._annotations[key][2] = self._annotation_objects[key].size().x()+self._annotation_objects[key].pos().x(); 
                if self._annotation_objects[key].isLocked()==False:
                    self._annotations[key][4] = None;
        self.sigDocChanged.emit();            
     
    def check_collisions(self,id,x,y,width,height):  # @ReservedAssignment
        
        for key in self._annotation_objects:
                if self._annotation_objects[key].id <> id and self._annotation_objects[key].pos().y() == y and ((self._annotation_objects[key].pos().x()<x+width and self._annotation_objects[key].pos().x() >x) or (x<self._annotation_objects[key].pos().x()+self._annotation_objects[key].size().x() and x>self._annotation_objects[key].pos().x())):
                    if x<self._annotation_objects[key].pos().x():
                        pos=pg.Point(self._annotation_objects[key].pos().x()-width,y)
                    if x>self._annotation_objects[key].pos().x(): 
                        pos=pg.Point(self._annotation_objects[key].pos().x()+self._annotation_objects[key].size().x(),y)
                    self._annotation_objects[id].setPos(pos)
                    # set the pos  for _annotation onject too
        
        self._annotations[id][1] = self._annotation_objects[id].pos().x();
        self._annotations[id][2] = self._annotation_objects[id].size().x()+self._annotation_objects[id].pos().x();
         
        self._annotations[id][4] = None;

    # remove an object from screen 
    def  remove_process(self,evt):
        self._annotation_objects[evt.id].removeItem(self._annotation_objects[evt.id])
        #evt.removeTimer.stop() # for a  bug  mentioned in: https://groups.google.com/forum/#!searchin/pyqtgraph/remove/pyqtgraph/OyhbLmzsdk0/alDwTlVbut8J
        
        # if an empty object is removed delete it from  everywhere and reduce the empty counter by one
        if evt._empty:
            self._empty_objects -=1;
            del self._annotation_objects[evt.id]
        
        
    def right_click_process(self,posx,poy,modifiers):
        # de_select
        if modifiers <> QtCore.Qt.ShiftModifier:
                
            for id in self._selected_list:  # @ReservedAssignment
            
                self._annotation_objects[id].deselect();
            self._selected_list=[];   
        
        if self.vb_mode=="zoom":
            
            if len(self._y) > 0 :
                self.PlotWidget.plotItem.vb.autoRange()
                self.xpos_changed(self.posx)               
                self.update() 

    def left_click_process(self,posx,posy,modifiers):
        if len(self._selected_list)>0:
            self.PlotWidget.plotItem.vb.menu=self.annotation_menu3
            self.PlotWidget.plotItem.vb.menu.popup(QtCore.QPoint(posx,posy))
                    
    #process a selected region (box) and generate empty annotation  graphic objects
    #logical objects should be added somewhere else 
    def add_annotations(self,posx_st,posy_st,posx_en,posy_en):         
        if posx_st<0:
            posx_st=0;     
        h=self.return_channel_height();
        posx_en2=posx_en;
        posx_st2=posx_st;
        _empty_objects=self._empty_objects;
        for i in range(self.signals_no):
            posx_en = posx_en2;
            posx_st = posx_st2;
            y = self.return_channel_pos(i);
            if  y > posy_st  and y<  posy_en:
        
                if _empty_objects == 0:
                    # check for collisions  (if an object already existed in the box)
                    for ekey in self._annotation_objects:
                        if self._annotation_objects[ekey].pos().y() == y-h/2 and ((self._annotation_objects[ekey].pos().x()<posx_en and self._annotation_objects[ekey].pos().x() >posx_st) or (posx_st<self._annotation_objects[ekey].pos().x()+self._annotation_objects[ekey].size().x() and posx_st>self._annotation_objects[ekey].pos().x())):
                            if posx_st<self._annotation_objects[ekey].pos().x():
                                posx_en = self._annotation_objects[ekey].pos().x();
                            if posx_st>self._annotation_objects[ekey].pos().x(): 
                                posx_st = self._annotation_objects[ekey].pos().x()+self._annotation_objects[ekey].size().x();
                    
                    
                    if (posx_st<> posx_en):
                       
                        key = self.generate_id()
                        self._annotation_objects[key]=CustomROI([posx_st,y-h/2],size=[posx_en - posx_st,h],id=key,maxBounds=QtCore.QRectF(0,y-h/2,10000,h),parent=self.PlotWidget.plotItem)
                        self.connect_to_signals(key)
                        self.PlotWidget.plotItem.addItem(self._annotation_objects[key])
                        self._empty_objects +=1;
                        self.PlotWidget.update() 
                        
                     
                        self._annotation_objects[key].setState(isLocked=False,isEmpty=True,isUpdated=False,isRemoved=False,isSelected=False)         
                        self._annotation_objects[key].set_menu(self.annotation_menu3) 
                        
                        
                        # add to  _annotation  dictionary 
                        # we have to add the created object (empty) to the _annotations and
                        # also we need to calculate views that it will be visible 
                        annotation = [i,posx_st,posx_en,None,False,False,True]
                        self._annotations[key] = annotation
                        self.pre_compute_view()
                else:                    
                    pass
                
                
    def add_to_selected(self,id):  # @ReservedAssignment
        self._selected_list.append(id)
                    
    def select_annotations(self,posx_st,posy_st,posx_en,posy_en):  
        if posx_st<0:
            posx_st=0;
      
        h=self.return_channel_height();
        posx_en2=posx_en;
        posx_st2=posx_st;
        for i in range(self.signals_no):
            posx_en = posx_en2;
            posx_st = posx_st2;
            y = self.return_channel_pos(i);
            if  y > posy_st  and y<  posy_en:
                for ekey in self._annotation_objects:
                    if self._annotation_objects[ekey].pos().y() == y-h/2 and ((self._annotation_objects[ekey].pos().x()<posx_en and self._annotation_objects[ekey].pos().x() >posx_st) or (posx_st<self._annotation_objects[ekey].pos().x()+self._annotation_objects[ekey].size().x() and posx_st>self._annotation_objects[ekey].pos().x())):
                        if self._annotation_objects[ekey].isLocked()==False:
                            self._annotation_objects[ekey].make_selected();
                            self._selected_list.append(ekey)             
                
         
    def menu1_edit(self):
        # unlock the annotation box for edit
        self._annotation_objects[self.selected_annotation_id].setState(isLocked=False)
        self._annotation_objects[self.selected_annotation_id].set_menu(self.annotation_menu2)
        self.old_pos=self._annotation_objects[self.selected_annotation_id].pos()
        self.old_size=self._annotation_objects[self.selected_annotation_id].size()
        
    def menu1_remove(self):
        # call the  process meanu function to remove
        self.process_CustomMenu(-2)
              
    def set_slider(self, parent):        
        # Slider only support integer ranges so use ms as base unit
        self.step=10.0;self.xmin=0.; self.xmax=self.total_time_recording;   #MGM(V0.2): The value of self.xmax changes in a way that slider covers whole the time of the recording.  
        self.scale=self.time_scale/self.step;
        smin, smax = self.xmin*self.scale, self.xmax*self.scale 
        self.slider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.slider.setTickInterval((smax-smin)/10.)
        self.slider.setMinimum(smin)
        self.slider.setMaximum(smax-self.step*self.scale)
        self.slider.setSingleStep(self.step*self.scale/5.)
        self.slider.setPageStep(self.step*self.scale)
        self.slider.setValue(0)  # set the initial position
        self.slider.valueChanged.connect(self.xpos_changed)
         
    #MGM(V0.2): This function (which was part of xpos_changed(pos) in v0.1) checks to see if there is any next/previous annotation for 
    #           activation/inactivation of Go Next and Go Back features. 
    def check_annotation(self,st_page,en_page):        
        #MGM(V0.2): check for next annotation and send a proper signal
        try:
            self._nextRightAnnotation= next(x[1] for x in self._sorted_annotation_objects if x[1] > en_page)
        except StopIteration:
            self._nextRightAnnotation = None;
        if self._nextRightAnnotation <> None:
            self.sigRightAnnotationExist.emit(True)
        else:
            self.sigRightAnnotationExist.emit(False)       
              
        #MGM(V0.2): check for previous annotation and send proper signal
        try:
            self._nextLeftAnnotation= next(x[1] for x in reversed(self._sorted_annotation_objects) if x[1] < st_page)
              
        except StopIteration:
            self._nextLeftAnnotation = None;
        if self._nextLeftAnnotation <> None:
            self.sigLeftAnnotationExist.emit(True)
        else:
            self.sigLeftAnnotationExist.emit(False)         
        
        
    # change the view based on position of slider      
    def xpos_changed(self, pos):      
        self.posx =pos/ self.scale
        if (self.posx<0): #MGM(V0.2): To limit the minimum of the time axis to zero
            self.posx = 0 #MGM(V0.2)
        self.set_xlim(self.posx, self.posx + self.time_scale, padding=0.001) #MGM(V0.02): The value of padding has been changed. It seems this bug is related to PyQtgrapg. With paddin=0 this function is not working properly. 
        self.timeaxis_start = self.posx;    #MGM(V0.2): The starting point on the time axis in the plot window
        self.timeaxis_end = self.posx + self.time_scale #MGM(V0.2): The ending point on the time axis in the plot window
        self.sigTimeRangeChanged.emit() #MGM(V0.2): When the time range in the plot window is changing by moving slider or changing other features this signal will emit.
  
        self.check_annotation(self.timeaxis_start, self.timeaxis_end)    #MGM(V0.2): To check for next/previous annotation
            
        # repose  sig_name
        for i in self.sig_names:
          
            if self.sig_names[i].content is not None:
                    self.sig_names[i].setPosX(self.posx)
        
        self.plot_annotations()
        
    def return_channel_pos(self,k):
        return self.yshift[k]    
    
    def return_channel(self,ypos):
        h=self.return_channel_height()
        channel=0;
     
        for  y in self.yshift:
            
            if y==ypos+h/2:
                return channel
            channel +=1
    
    def return_channel_height(self):
        if len(self.yshift) <= 1:
            return self.ymax-self.ymin
        else:
            return self.yshift[1]-self.yshift[0];
        
    
    def setData(self,channel,x,y):
        if x is not None:
            self._x=x;
        self._y[channel] = y;
        self.set_slider(self)
        
    def setChannelColor(self,color):
        for k in range(self.signals_no):
            self.channel_color[k]=color[k];
    
    def highlight(self,channel_posy,highlighted): 
        channel_no = self.return_channel(channel_posy)
        if highlighted == True:
            self.plot_item=self.PlotWidget.plotItem.plot(self._x,self.amplitude_scale[channel_no]*self._y[channel_no]+self.yshift[channel_no])  
       
            self.plot_item.setPen(color=(255,255,255))
        else:
            self.plot(channel_no, x=None, y=None)    
                      
    def plot(self,channel_no,x,y):
        h=self.return_channel_height()
        if y is not None:
            self.setData(channel_no,x,y)
      
        self.plot_item=self.PlotWidget.plotItem.plot(self._x,self.amplitude_scale[channel_no]*self._y[channel_no]+self.yshift[channel_no])  
       
        self.plot_item.setPen(color=self.channel_color[channel_no])
        
        
        
        sig_name = CustomTextBox([0,self.yshift[channel_no]+h/8],size=[self.time_scale/15,max(h/4,360)]);
        sig_name.setLabel(self.signal_labels[channel_no])
        sig_name.set_menu(self.channel_menu)
        tmp=list(self.channel_color[channel_no])
        tmp.append(150)
        sig_name.setBrush(tuple(tmp))
        
        
        if sig_name.content is None:
            self.PlotWidget.plotItem.addItem(sig_name)
        
        sig_name.setContent(channel_no)
        
        self.sig_names[channel_no] = sig_name
        self.connect_channel_name_signals(channel_no)
        self.prepare_ChannelMenu()
        
    def reset_annotation(self):
        self._annotation_count = 0;
        self._annotations={};
        self._annotation_objects={};
        self._add_list=[];
        self._change_list=[];
        self._remove_list=[];
        self._sorted_annotations_st=[]
        self._sorted_annotations_en=[]
        # left most and right most id of  annotations that can be seen in the current view
        self.left_most_id=0;
        self.right_most_id =0;
        
    
    # self._annotations{}={id: [channel_id,start,end,class_id,confirmed,removed]}   
    def  set_annotations(self,annotations):
        self.reset_annotation()
        if self.accept_annotation:
            for annotation in annotations:
                id=self.generate_id();  # @ReservedAssignment
                annotation.append(True); # confirmed
                annotation.append(False);# not removed 
                annotation.append(False); #not empty
                self._annotations[id]=annotation 
        #self.pre_compute_view();    #MGM(V0.02): It is commented and added any necessary place separately to make more efficient the program.
          
          
    def pre_compute_view(self):        
            self._preComputedView={}
            self._sorted_annotation_objects=[];
            keys=range(int(-2*self.time_scale),int(self.total_time_recording)+1)    #MGM(V0.02): The ending time changed to make possible using Go Next/Back Annotation. Now precmpute view is calculating for whole the time of the recording.
            self._preComputedView = dict.fromkeys(keys)
            for k in self._preComputedView:
                self._preComputedView[k]=[];       
            for id in self._annotations:  # @ReservedAssignment
                self._sorted_annotation_objects.append([id,self._annotations[id][1]]) # list of tuple (id,start)
                st = self._annotations[id][1]
                en = self._annotations[id][2]
                for k in range(int(st)-1-int(self.time_scale),int(en)+int(self.time_scale)):
                        if (st >= k and st <= k+self.time_scale) or (en >= k and en <= k+self.time_scale)  :
                            self._preComputedView[k].append(id)
                        else:
                            pass
                
                if en-st>self.time_scale:
                    for k in self._preComputedView:
                        if (st<k and en>k+self.time_scale):
                            if id not in self._preComputedView[k]:
                                self._preComputedView[k].append(id)
                                
            self._sorted_annotation_objects.sort(key=lambda tup:tup[1])
                        
    def get_annotation(self):
        pass
                                
    def set_selected_annotation_id(self,id):  # @ReservedAssignment
        self.selected_annotation_id=id; 
        if id in self._annotation_objects:
            self.customMenu1.select_classid(self._annotation_objects[id].content)  
        
    def generate_id(self):
        self._annotation_count +=1;
        return (self._annotation_count-1)
    
    def showLabels(self):
        self._showLabels=True
        self.update()
        
    def hideLabels(self):
        self._showLabels=False
        self.update()
                     
    def plot_annotations(self):
        if len(self._annotation_objects)>0:
            key_to_remove=[]
            for key in self._annotation_objects:
                if key not in  self._preComputedView[int(self.posx)]:
                    self.PlotWidget.plotItem.removeItem(self._annotation_objects[key])
                    key_to_remove.append(key)
            for k in  key_to_remove:
                del self._annotation_objects[k]        
         
        # find the view
        if(len(self._preComputedView)>0):
            h=self.return_channel_height()
             
            for key in self._preComputedView[int(self.posx)]:
                if key not in self._annotation_objects:
                    if self._annotations[key][6] == True and self._annotations[key][5] ==True:
                        continue
                   
                    ypos=self.return_channel_pos(self._annotations[key][0])
                    xpos_st=self._annotations[key][1]
                    xpos_en=self._annotations[key][2]
                 
                    self._annotation_objects[key]=CustomROI([xpos_st,ypos-h/2], size=[xpos_en-xpos_st,h],id=key,maxBounds=QtCore.QRectF(0,ypos-h/2,10000,h),parent=self.PlotWidget.plotItem)
                    if self._showLabels:
                        self._annotation_objects[key].setLabel(self.class_mapping[self._annotations[key][3]])
                                
                    if self._annotations[key][6] ==  True:
                        self._annotation_objects[key].setState(isLocked=False,isEmpty=True)
                         
                    # the object is not Empty and is in edit mode
                    if self._annotations[key][4] == None and self._annotations[key][6]==False:
                        self._annotation_objects[key].setState(isLocked=False,isEmpty=False,isUpdated=True)

                    # if this is set for remove
                    if self._annotations[key][4] == False and self._annotations[key][5] == True and self._annotations[key][6]==False: 
                        
                        self._annotation_objects[key].setState(isRemoved=True)
                    
                    #modified
                    if self._annotations[key][4] == False and self._annotations[key][5] == False and self._annotations[key][6]==False: 
                        
                        self._annotation_objects[key].setState(isUpdated=True)    
                     
                    if self._annotations[key][6]==False:
                        color=self.class_color_mapping[self._annotations[key][3]];  
                        self._annotation_objects[key].setContent(self._annotations[key][3]) 
                        self._annotation_objects[key].setBrush(color);   
                    else:      
                        pass
                                          
                    self.connect_to_signals(key)
                    self.PlotWidget.plotItem.addItem(self._annotation_objects[key])
                    if self._annotations[key][4] <> None and self._annotations[key][6]==False:
                        self._annotation_objects[key].setState(isLocked=True,isEmpty=False)       
                        self._annotation_objects[key].set_menu(self.annotation_menu1) 
                    elif self._annotations[key][6] ==False:
                        self._annotation_objects[key].set_menu(self.annotation_menu2)   
                    else: 
                        self._annotation_objects[key].set_menu(self.annotation_menu3)
                                 
            self.prepare_CustomMenu() 
               
    def replot_annotations(self):
        for key in self._annotation_objects:
            
            if self._showLabels:
                if self._annotation_objects[key].content <> None and self._annotation_objects[key].content <> -1:
                    self._annotation_objects[key].setLabel(self.class_mapping[self._annotation_objects[key].content])
            else:
                self._annotation_objects[key].setLabel("")
                   
            self.PlotWidget.plotItem.addItem(self._annotation_objects[key])
            
    def confirmChanges(self):
        
        self._annotation_count=0;
        self._remove_list=[]; # id of  objects to be removed
        self._add_list=[]; #id to be added
        self._change_list=[]; #id of annotation objects that has changed
         
        self._empty_objects=0; # number of empty (newly created but not assigined) annotations on the screen
         
        self._selected_list=[]; # a list of selected  annotation objects (ids) by  mouse  drag or other means

        set_for_remove=[]
        for key in self._annotations:
            
            # confirm the annotation
            self._annotations[key][4] = True
            
            # remove annotation if needed
            if self._annotations[key][5] == True or self._annotations[key][6] == True:
                set_for_remove.append(key)
        
        for id in set_for_remove:  # @ReservedAssignment
            del self._annotations[id]
            
        self.sigConfirmed.emit()    
        self._isConfirmed = True
        
        
    def cancelChanges(self):
     
        self._remove_list=[]; # id of  objects to be removed
        self._add_list=[]; #id to be added
        self._change_list=[]; #id of annotation objects that has changed
         
        self._empty_objects=0; # number of empty (newly created but not assigined) annotations on the screen
         
        self._selected_list=[]; # a list of selected  annotation objects (ids) by  mouse  drag or other means

        self._annotation_objects={};
    
        self._annotations={}
        for key in self._annotations_old:
            if self._annotations_old[key][6]==False:
                self._annotations[key] = self._annotations_old[key]
       
       
        self._isConfirmed = True
        
        self.pre_compute_view()
            
        self.update();
   
    # go to the next page that contains an annotation
    def goNext(self):        
            if self._nextRightAnnotation is not None:
                self.xpos_changed(self._nextRightAnnotation)
                self.slider.setValue(self.posx)
                
    def goBack(self):                
            if self._nextLeftAnnotation is not None:
                self.xpos_changed(self._nextLeftAnnotation)
                self.slider.setValue(self.posx)    
                
                
                