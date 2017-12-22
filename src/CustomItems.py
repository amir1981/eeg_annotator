'''
Created on May 17, 2014

@author: amir

CustomItems for EEG annotator V0.2.1

Note : This version has been edited by MGM. All of the statements which added or edited for this version 
       has been commented by this method: #MGM(V0.2.1):(Explanation)
'''
"""
This file contains all customized items based on pyqtgraph items.
     
"""
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pyqtgraph.graphicsItems as gi
import pyqtgraph.functions as fn

# Customized ROI  used  for  plotting the annotations
# this class adds text, background and some other features to the ROI

class CustomROI(pg.ROI):
    
     # define signal
     sigMouseClicked=QtCore.Signal(int)
     sigShiftMouseClicked=QtCore.Signal(int)
     sigMoved=QtCore.Signal(int,float,float,float,float)
     sigHover=QtCore.Signal(float,bool)
     
     
     def __init__(self, pos,id=None, **kargs):
        pg.ROI.__init__(self, pos,**kargs)
        self.posx=pos[0];
        self.posy=pos[1];
        # set the size and color of the handle
        self.handleSize=9;
        self.handlePen = QtGui.QPen(QtGui.QColor(255, 255, 255))
        self.hand1=None;
        self.hand2=None;
      
        
        
        #status
        self._isLocked = False;
        self._remove_flag = False;
        self._empty = True;
        self._updated = False;
        self._selected= False;
        
        self._old_style=""; # save old style before applying new ones
        self._current_style="empty"; #default style since _empty =True is the default state
        
        # content : this is where graphical object store the logical class
        self.content=-1;
        
        if "parent" in kargs:
            self.parent = kargs["parent"];
            
       
        # object id (used to refer to this object by parent or other classes)
        self.id = id;
        self.content=None; # logical object linked to this  graphic object
        
    
        #define the Brush and default color 
        brush = QtGui.QBrush(QtGui.QColor(0, 255, 255, 150))
        self.setBrush(brush)
    
     
        
        
        # define the text item and set it to empty string
        # it is positioned at top left of the  box
        self.text_label=""
        self.showText=False;
        self.textItem = pg.TextItem(self.text_label);
        self.textItem.setParentItem(self)
        width,height =  self.size()
       
       
        self.textItem.setPos(0,height+.1*height)
        
        self.menu = None
     
     def setContent(self,classid):
         self.content=classid
     
           
     def setLabel(self,label):
         if label=="":
            
             self.textItem.setParentItem(None)
             self.textItem=None;
             self.update()
             
         self.text_label=label
         #html_text="<font size=1>"+label+"<\/font>";    #MGM(V0.2.1): For printing the annotation's labels legibly
         self.textItem = pg.TextItem();
         #self.textItem.setHtml(html_text)    #MGM(V0.2.1):  For printing the annotation's labels legibly
         self.textItem.setText(label)    #MGM(V0.2.1):  For printing the annotation's labels legibly
         self.textItem.setParentItem(self)
         width,height =  self.size()
         
         self.textItem.setPos(0,height+0*height)    #MGM(V0.2.1):  For printing the annotation's labels legibly
         
         
     def setState(self,isLocked=None,isEmpty=None,isUpdated=None,isRemoved=None,isSelected=None):
         if isLocked is not None:
             self._isLocked = isLocked
         if isEmpty is not None:    
             self._empty= isEmpty
         if isUpdated is not None:    
             self._updated = isUpdated
         if isRemoved is not None:    
             self._remove_flag = isRemoved;
         if isSelected is not None:    
             self._selected = isSelected;
         
         
         if isLocked:
             self._lock();
         elif isLocked<>None:
             self._unlock();
             pass 
         
         self.setStyle(self._isLocked,self._empty,self._updated,self._remove_flag,self._selected)    
            
     
     def is_empty(self):
         return self._empty;
     
     # re-implement to check for  collisions and overlaps   
     def translate(self, *args, **kargs):
        """
        Move the ROI to a new position.
        Accepts either (x, y, snap) or ([x,y], snap) as arguments
        If the ROI is bounded and the move would exceed boundaries, then the ROI
        is moved to the nearest acceptable position instead.
        
        snap can be:
           None (default): use self.translateSnap and self.snapSize to determine whether/how to snap
           False:          do not snap
           Point(w,h)      snap to rectangular grid with spacing (w,h)
           True:           snap using self.snapSize (and ignoring self.translateSnap)
           
        Also accepts *update* and *finish* arguments (see setPos() for a description of these).
        """

        if len(args) == 1:
            pt = args[0]
        else:
            pt = args
            
        newState = self.stateCopy()
        newState['pos'] = newState['pos'] + pt
        
        ## snap position
        #snap = kargs.get('snap', None)
        #if (snap is not False)   and   not (snap is None and self.translateSnap is False):
        
        snap = kargs.get('snap', None)
        if snap is None:
            snap = self.translateSnap
        if snap is not False:
            newState['pos'] = self.getSnapPosition(newState['pos'], snap=snap)
        
        #d = ev.scenePos() - self.mapToScene(self.pressPos)
        if self.maxBounds is not None:
            r = self.stateRect(newState)
            #r0 = self.sceneTransform().mapRect(self.boundingRect())
            d = pg.Point(0,0)
            if self.maxBounds.left() > r.left():
                d[0] = self.maxBounds.left() - r.left()
            elif self.maxBounds.right() < r.right():
                d[0] = self.maxBounds.right() - r.right()
            if self.maxBounds.top() > r.top():
                d[1] = self.maxBounds.top() - r.top()
            elif self.maxBounds.bottom() < r.bottom():
                d[1] = self.maxBounds.bottom() - r.bottom()
            newState['pos'] += d
        
        #self.state['pos'] = newState['pos']
        update = kargs.get('update', True)
        finish = kargs.get('finish', True)
        self.setPos(newState['pos'], update=update, finish=finish)
      
        self.sigMoved.emit(self.id,newState['pos'].x(),newState['pos'].y(),self.size().x(),self.size().y())
        
        
     # just copied (for some reason without coping this here the position of text changes when the size of 
     # ROI changes)   
     def stateChanged(self, finish=True):
        """Process changes to the state of the ROI.
        If there are any changes, then the positions of handles are updated accordingly
        and sigRegionChanged is emitted. If finish is True, then 
        sigRegionChangeFinished will also be emitted."""
        
        changed = False
        if self.lastState is None:
            changed = True
        else:
            for k in list(self.state.keys()):
                if self.state[k] != self.lastState[k]:
                    changed = True
        
        self.prepareGeometryChange()
        if changed:
            ## Move all handles to match the current configuration of the ROI
            for h in self.handles:
                if h['item'] in self.childItems():
                    p = h['pos']
                    h['item'].setPos(h['pos'] * self.state['size'])
                #else:
                #    trans = self.state['pos']-self.lastState['pos']
                #    h['item'].setPos(h['pos'] + h['item'].parentItem().mapFromParent(trans))
                    
            self.update()
            self.sigRegionChanged.emit(self)
        elif self.freeHandleMoved:
            self.sigRegionChanged.emit(self)
            
        self.freeHandleMoved = False
        self.lastState = self.stateCopy()
            
        if finish:
            self.stateChangeFinished()
        
     def setBrush(self, *br, **kargs):
        """Set the brush that fills the region. Can have any arguments that are valid
        for :func:`mkBrush <pyqtgraph.mkBrush>`.
        """
        self.brush = fn.mkBrush(*br, **kargs)
        
        self.currentBrush = self.brush
     
  
     # modify the paint method so it also take care of the brush         
     def paint(self, p, opt, widget):
        p.save()
        r = self.boundingRect()
        p.setRenderHint(QtGui.QPainter.Antialiasing,True)
        p.setPen(self.currentPen)
        p.setBrush(self.currentBrush)
        p.translate(r.left(), r.top())
        p.scale(r.width(), r.height())
        p.drawRect(0, 0, 1, 1)
        p.restore()
     
     def make_selected(self):
         self.setState(isSelected=True)
     
     def isLocked(self):
         return self._isLocked;
     
     def isEmpty(self):
         return self._empty;
     
     def isRemoved(self):
         return self._remove_flag
     
     #lock the ROI
     def _lock(self):
         self._isLocked = True;
         self.translatable = False;
         #try:
          
         if len(self.handles)>0:
             self.removeHandle(self.hand1)
             self.removeHandle(self.hand2)
         #except:
          #   print "problem"
           #  pass
   
     def _add_handle(self):
        
        
        self.hand1=self.addScaleHandle([1, .5], [0, .5])
        self.hand2=self.addScaleHandle([0, .5], [1, .5])    
     #unlock the ROI
     def _unlock(self):
        self._isLocked = False;
        self.translatable = True;
        self._add_handle();
                       
     def set_handle_color(self):
         pass
     
     def set_brush(self):
         pass
     
     def set_text(self):
         pass
     
     # set the menu   
     def set_menu(self,menu):
         self.menu=menu
     
     def deselect(self):
         self.setState(isSelected=False)
            
     def hoverEvent(self, ev):
        if not ev.isExit() and ev.acceptDrags(QtCore.Qt.LeftButton):
            self.currentPen = fn.mkPen(255, 0, 0)  
            self.sigHover.emit(self.posy,True)       
        else:
            self.currentPen=self.pen
            pg.ROI.hoverEvent(self,ev)
            self.sigHover.emit(self.posy,False) 
            pass 
        self.update()
        
     #def  
 
 
     #  mouse click +  shift+click
     def  mouseClickEvent(self,ev):
        modifiers = QtGui.QApplication.keyboardModifiers();
        if modifiers == QtCore.Qt.ShiftModifier and self._isLocked == False and ev.button() == QtCore.Qt.RightButton:
            #self.setStyle("selected")
            self.setState(self._isLocked, self._empty, self._updated, self._remove_flag,isSelected=True)
            self.sigShiftMouseClicked.emit(self.id);
            
        else:
            self.sigMouseClicked.emit(self.id)
            
            menu = self.getMenu()
            pos = ev.screenPos()
            menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        
     def set_for_remove(self):  
         self.setState(isLocked=True, isUpdated=False,isRemoved=True,isSelected=self._selected)
         self.stateChanged(finish=True)
         
     def set_for_update(self):
         self.setState(isLocked=True, isEmpty=False, isUpdated=True, isRemoved=True,isSelected=self._selected) 
         self.stateChanged(finish=True)
             
 
     # remove this item. The parent item should be set in constructor (e.g. pw.ItemPlot or anything with a viewbox that this object is located)
     # this method just remove the graphic Item from the scene (if it is related to a logical item it does not affect that)
     def removeItem(self,evt):
         #evt.removeTimer.stop() # for a  bug  mentioned in: https://groups.google.com/forum/#!searchin/pyqtgraph/remove/pyqtgraph/OyhbLmzsdk0/alDwTlVbut8J
         self.parent.vb.scene().removeItem(evt)
 
     def setStyle(self,isLocked=False,isEmpty=True,isUpdated=False,isRemoved=False,isSelected=False):
         
        
         if isEmpty == True and isRemoved==True:
            
             self.sigRemoveRequested.emit(self)
             
         elif isEmpty==True:
             self.pen = fn.mkPen(color='y',width=4)
             self.currentPen = self.pen
             brush = QtGui.QBrush(None)
             self.setBrush(brush)
             if self.showText==True:
                self.text_label = "Empty";
             else:
                self.text_label = "";
                
         elif isUpdated==True:
             self.pen = fn.mkPen(color='g',width=4)
             self.currentPen = self.pen
         elif isRemoved==True:
             self.pen = fn.mkPen(color='r',width=4)
             self.currentPen = self.pen
             if self.showText==True:
                self.text_label = "Removed("+self.text_label+")";
             else:
                self.text_label = "";
         else:  #all 3 all false --> confirmed   
                self.pen= fn.mkPen(color='w')
                self.currentPen = self.pen  
         if  isSelected:
               self.pen = fn.mkPen(color='w',width=2,style=QtCore.Qt.DashDotLine)
               self.currentPen = self.pen
         

                     
         self.update()    
              
              
              
                            
              
###  Custom ViewBox     
class CustomViewBox(pg.ViewBox):
    
    sigLRegionSelected=QtCore.Signal(float,float,float,float)
    sigRRegionSelected=QtCore.Signal(float,float,float,float)
    
    sigRightClick=QtCore.Signal(float,float,object)
    
    sigLeftClick=QtCore.Signal(float,float,object)
    
    sigPanDrag=QtCore.Signal(float)
    
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)
        self.vbox_mode="pan";
    
    
    def set_mode(self,mode):
        if mode=="pan":
            self.vbox_mode="pan";
            self.setMouseMode(self.PanMode)
        elif mode=="zoom":
            self.vbox_mode="zoom"
            self.setMouseMode(self.RectMode)
        elif mode=="add":
            self.vbox_mode="add"
            self.setMouseMode(self.RectMode)
        else:
            # 
            print "mode is not supported by veiwbox (CustomViewBox Class)."
            exit();    
            
                    
    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if self.vbox_mode == "zoom":
          
            if ev.button() == QtCore.Qt.RightButton:
                modifiers = QtGui.QApplication.keyboardModifiers();
                pos = ev.screenPos()
                self.sigRightClick.emit(pos.x(),pos.y(),modifiers);  
                        
        elif self.vbox_mode == "add":
            if ev.button() == QtCore.Qt.RightButton:
                modifiers = QtGui.QApplication.keyboardModifiers();
                pos = ev.screenPos()
                
                self.sigRightClick.emit(pos.x(),pos.y(),modifiers);
            
            if ev.button() == QtCore.Qt.LeftButton:
                modifiers = QtGui.QApplication.keyboardModifiers();
                pos = ev.screenPos()
                self.sigLeftClick.emit(pos.x(),pos.y(),modifiers);
                
         
    def mouseDragEvent(self, ev,axis=0):
        
        if self.vbox_mode == "add":
            if ev.button() == QtCore.Qt.RightButton:
                   ev.accept()  ## we accept all buttons
                   pos = ev.pos()
                   lastPos = ev.lastPos()
                   dif = pos - lastPos
                   dif = dif * -1
                   if ev.button() & (QtCore.Qt.RightButton):
                       self.rbScaleBox.setPen(fn.mkPen((0,0,0), width=1))
                       self.rbScaleBox.setBrush(fn.mkBrush(255,0,0,100))
                       if self.state['mouseMode'] == self.RectMode:
                           if ev.isFinish():  ## This is the final move in the drag; change the view scale now
                               self.rbScaleBox.hide()
                               self.rbScaleBox.setPen(fn.mkPen((255,255,100), width=1))
                               self.rbScaleBox.setBrush(fn.mkBrush(255,255,0,100))
                               ax = QtCore.QRectF(pg.Point(ev.buttonDownPos(ev.button())), pg.Point(pos))
                          
                               ax = self.childGroup.mapRectFromParent(ax)
                               posx_st,posy_st,posx_en,posy_en = ax.getCoords()
                            
                               self.sigRRegionSelected.emit(posx_st,posy_st,posx_en,posy_en)
                           else:
                               ## update shape of scale box
                               self.updateScaleBox(ev.buttonDownPos(), ev.pos())
            else:
                
                ## if axis is specified, event will only affect that axis.
                ev.accept()  ## we accept all buttons
                pos = ev.pos()
                lastPos = ev.lastPos()
                dif = pos - lastPos
                dif = dif * -1
                if ev.button() & (QtCore.Qt.LeftButton | QtCore.Qt.MidButton):
                    if self.state['mouseMode'] == self.RectMode:
                        if ev.isFinish():  ## This is the final move in the drag; change the view scale now
                            self.rbScaleBox.hide()
                           
                            ax = QtCore.QRectF(pg.Point(ev.buttonDownPos(ev.button())), pg.Point(pos))
                          
                            ax = self.childGroup.mapRectFromParent(ax)
                            posx_st,posy_st,posx_en,posy_en = ax.getCoords()
                            
                            self.sigLRegionSelected.emit(posx_st,posy_st,posx_en,posy_en)
                        else:
                            ## update shape of scale box
                            self.updateScaleBox(ev.buttonDownPos(), ev.pos())
        elif self.vbox_mode =="pan":
           
             posx=self.state["viewRange"][0][0];
            
             self.sigPanDrag.emit(posx)
             
             pg.ViewBox.mouseDragEvent(self,ev,axis=0)
            
        elif self.vbox_mode=="zoom":
            pg.ViewBox.mouseDragEvent(self,ev)                        
                            
                            
                            
                            
                        
class CustomContextMenu(QtGui.QWidget):
    sigReturn=QtCore.Signal(int)
    def __init__(self,items_map, color_map,parent=None):
        super(CustomContextMenu, self).__init__()
        self._rowlen=3
        #self.w = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.initUI(items_map,color_map)
        self.selected_id = -1;
        self.parent=parent;
    
    def select_classid(self,class_id):
        for ibutton in self._buttons:
            self._buttons[ibutton].setChecked(False)
        
        
        if class_id is not None:
            self._buttons[class_id].setChecked(True);
        
    def initUI(self,items_map,color_map):
    
        self.items_map = items_map;
        self.color_map = color_map;
        nrows=round(len(items_map)/6.0)
        count=0
        row=0
        col=0
        self._buttons={};
        for item_id in self.items_map:
            new_button = QtGui.QPushButton(self.items_map[item_id], self)
            new_button.setCheckable(True);
            new_button.setStyleSheet("background-color: rgb"+str(self.color_map[item_id])+";")
            new_button.clicked[bool].connect(self.select_class)
            new_button._id=item_id;
            new_button._count=count;
            self.layout.addWidget(new_button, row, col)
            self._buttons[item_id]=(new_button)
            count += 1;
            col += 1;
            if col>=self._rowlen:
                row +=1
                col = 0
        if row>1:
            cspan=self._rowlen
        else:
            cspan=col;
                            
        sep=QtGui.QFrame();
        sep.setFrameShape(QtGui.QFrame.HLine)     
        sep.setFrameShadow(QtGui.QFrame.Sunken)   
        self.layout.addWidget(sep,row+1,0,1,cspan)
        self.ok_button =   QtGui.QPushButton("OK", self)    
        self.ok_button.clicked[bool].connect(self.ok_pressed)
        self.cancel_button= QtGui.QPushButton("Cancel", self)  
        self.cancel_button.clicked[bool].connect(self.cancel_pressed)
        self.layout.addWidget(self.ok_button,row+2,0)
        self.layout.addWidget(self.cancel_button,row+2,1)
        self.remove_button= QtGui.QPushButton("Remove", self)  
        self.remove_button.clicked[bool].connect(self.remove_pressed)
        self.layout.addWidget(self.remove_button,row+2,2)
        
        
        
    def select_class(self,pressed): 
        source=self.sender()
        self.selected_id = source._id;
        for ibutton in self._buttons:
            self._buttons[ibutton].setChecked(False)
        source.setChecked(True)
            
    def ok_pressed(self):
        if self.selected_id==-1:
            self.selected_id=-3 # ok pressed  but  no class change ( move, scale)
        self.sigReturn.emit(self.selected_id)
     
        self.selected_id=-1
        self.parentWidget().close()
        pass
    def cancel_pressed(self):
        self.sigReturn.emit(-1)
        self.parentWidget().close()
        
    def remove_pressed(self):
        self.sigReturn.emit(-2)
        self.parentWidget().close() 
        
    def hideEvent(self,ev):
        for ibutton in self._buttons:
            self._buttons[ibutton].setChecked(False)
            
            

            
class CustomTextBox(CustomROI):
    def __init__(self, pos,id=None, **kargs):
        CustomROI.__init__(self, pos,**kargs) 
        self.setState(isLocked=True,isEmpty=False) 
        
    def setLabel(self,label):
         if label=="":
             self.textItem.setParentItem(None)
             self.textItem=None;
             self.update()
             
         self.text_label=label
         html_text="<font size=1><b>"+label+"</b><\/font>";
         self.textItem = pg.TextItem();
         self.textItem.setHtml(html_text)
         self.textItem.setParentItem(self)
         width,height =  self.size()
         self.textItem.setPos(0,height)
         
    def set_menu(self,menu):
         self.menu=menu
                  
    def setPosX(self,posx):
        self.setPos([posx,self.posy])
          
    #  mouse click +  shift+click
    def  mouseClickEvent(self,ev):
          self.sigMouseClicked.emit(self.content)
          menu = self.getMenu()
          pos = ev.screenPos()
          menu.popup(QtCore.QPoint(pos.x(), pos.y()))
          
         
         
# context menu for each  channel (for now  just to adjust the amplitude scale)
class CustomChannelMenu(QtGui.QWidget):
    sigReturn=QtCore.Signal(int)
    sigSpinChanged=QtCore.Signal(int,float)
    
    def __init__(self,parent=None):
        super(CustomChannelMenu, self).__init__()
        self._rowlen=3
        #self.w = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.initUI()
        self.parent=parent;
        self.id = None;
            
    def initUI(self):
          label = QtGui.QLabel();
          label.setText("amplitude scale:")
          self.amplitude_scale = QtGui.QDoubleSpinBox() 
          self.amplitude_scale.setMaximum(10000)
          self.amplitude_scale.setMinimum(1)
          self.amplitude_scale.valueChanged.connect(self.ampScale_value_changed)   
          self.layout.addWidget(label)   
          self.layout.addWidget(self.amplitude_scale) 
          
#         self.amplitude_scale = QtGui.QLineEdit(self)   
#         self.layout.addWidget(self.amplitude_scale) 
#         sep=QtGui.QFrame();
#         sep.setFrameShape(QtGui.QFrame.HLine)     
#         sep.setFrameShadow(QtGui.QFrame.Sunken)   
#         self.layout.addWidget(sep)
#         self.ok_button =   QtGui.QPushButton("OK", self)    
#         self.ok_button.clicked[bool].connect(self.ok_pressed)
#         self.cancel_button= QtGui.QPushButton("Cancel", self)  
#         self.cancel_button.clicked[bool].connect(self.cancel_pressed)
#         self.layout.addWidget(self.ok_button)
#         self.layout.addWidget(self.cancel_button)
       
     
    def ok_pressed(self):
        if self.selected_id==-1:
            self.selected_id=-3 # ok pressed  but  no class change ( move, scale)
        self.sigReturn.emit(self.selected_id)
     
        self.selected_id=-1
        self.parentWidget().close()
        pass
    def cancel_pressed(self):
        self.sigReturn.emit(-1)
        self.parentWidget().close()
    
    def set_ampScale(self,id,val):
        self.id  = id;
        self.amplitude_scale.setValue(val)
            
    def ampScale_value_changed(self,val):
        self.sigSpinChanged.emit(self.id,val)
     
                              