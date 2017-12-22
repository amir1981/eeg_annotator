'''
Created on May 25, 2014

@author: Amir Harati

This file contains a class that manage how to read/create and interpret a project file.
'''
import StringIO,ConfigParser, os,re,shutil 

class ProjectManager:
    def __init__(self):
        # options that should be existed in the project file
        self.options=['name','eeg_list','report_list','annotation_list','class_mapping','montage','config','add_new_user','users_list','root','final','finished']
        self.project_info= dict.fromkeys(self.options);
        self.eeg_files_full={}; #full path 
        self.eeg_files=[];  # just file names
        self.finished_files=[]; # finished files
        self.report_files={};
        self.annotation_files={};
        self.class_mapping={};
        self.class_mapping_colors={}; # colors for each class
        self.montage_def={}
        self.montage_names={}
        self.montage_scales={}
        self.montage_color={}
        self.montage_order={}
        
        self.usernames=[];
        self.users={}
        
    
    def read(self,filename):
        # a string to save the content of the project file and attach a section in top pf it
        project_str = '[root]\n' + open(filename,'r').read();
        # memic a file object
        project_fp = StringIO.StringIO(project_str)
        # define the parser object and parse the file
        parser = ConfigParser.RawConfigParser();
        parser.readfp(project_fp)
        
        for option in self.options:
            try:
                str0 = parser.get('root',option)
            except ConfigParser.NoOptionError:
                # exit if the option is not existed in project file.
                print option+" is not existed in your project file." 
                exit();
            tmp = str0.split("#")  # remove the  comment if existed
            if tmp[0] == "None":
                tmp[0] = None;
            if tmp[0] == "True" :
                tmp[0] = True;
            if tmp[0] == "False":
                tmp[0] = False;    
            self.project_info[option] = tmp[0];
        
        # read the eeg_list
        self.read_datafeilds();
    
    # save annotation file from current place to last_session dir for  username
    def save(self,key,username):
        if username in self.usernames:
           
            shutil.copy(self.annotation_files[key],username+"/last_session/annotations")
        else:
            print username + " is not in the list."
            exit()
            
    # write annotation data into file in annotation_files dictionary and accessed by key
    def writeAnnotationFile(self,key,annotations):
      
        fp =open(self.annotation_files[key],"w");
        for id in annotations:
            line = str(self.montage_map_order2id[annotations[id][0]]);
            line = line +"," +str(annotations[id][1])
            line = line +"," +str(annotations[id][2])
            line = line +","+ str(annotations[id][3])+"\n"    
            fp.write(line)
        fp.close()    
            
    def readListFile(self,filename,keys):
        '''
            example of list file: 
                eegfile1 : labelfile1
                eegfile2 : labelfile2
        '''
        # if keys is None generate it from the file (each line  is  key : value)
        if keys is None:
            keys=[];
            p=re.compile('#(.*)')
            try:
                lines = [line.strip() for line in open(filename)]
            except IOError:
                print "File :" +filename+" not existed (specified in project file)."
                exit()
                
            for line in lines:
                if p.match(line) is None:
                    tmp=line.split(":")
                    try: 
                      keys.append(int(tmp[0]))
                    except:
                      keys.append((tmp[0]))   
          
        tmp_dict = dict.fromkeys(tuple(keys))
        
        # a string to save the content of the project file and attach a section in top pf it
        file_str = '[root]\n' + open(filename,'r').read();
        # memic a file object
        file_fp = StringIO.StringIO(file_str)
        # define the parser object and parse the file
        parser = ConfigParser.RawConfigParser();
        parser.readfp(file_fp)
        
        for key in keys:
            str0 = parser.get('root',str(key))
            tmp = str0.split("#")  # remove the  comment if existed
            tmp_dict[key] = tmp[0];
        return tmp_dict,keys;    
               
    def read_datafeilds(self):
        # read eeg_list  file
        tmp = open(self.project_info['eeg_list'],'rU').readlines()
        for i in range(len(tmp)):
             tmp[i] = tmp[i].rstrip('\n')
             self.eeg_files.append(os.path.basename(tmp[i])); 
        self.eeg_files_full = dict.fromkeys(tuple(self.eeg_files))
        for i in range(len(tmp)):
            self.eeg_files_full[self.eeg_files[i]]=tmp[i]
            
      
            
        #read report_list file
        if self.project_info['report_list'] is not None:
            values,keys = self.readListFile(self.project_info['report_list'],None)
            self.report_files = dict.fromkeys(self.eeg_files);
            for key in keys:
                self.report_files[key] = values[key]
        
        #read annotation_list file
        if self.project_info['annotation_list'] is not None:
            values,keys = self.readListFile(self.project_info['annotation_list'],None) 
            self.annotation_files = dict.fromkeys(self.eeg_files)
            for key in keys:
                self.annotation_files[key] = values[key]  
        else:
            self.annotation_files = dict.fromkeys(self.eeg_files) # set them to None
        
        # read class_mapping  (class_id:class_name,(RGB tuple)
        values,keys = self.readListFile(self.project_info['class_mapping'],None) # read the keys from the file
        self.class_mapping = dict.fromkeys(keys);
        self.class_mapping_colors = dict.fromkeys(keys)
        
        for key in values:
            
            tmp=re.search(r'(.+)\,(\(.*\))',values[key]);# value itself has two parts  (class_name,RGB tuple)
            self.class_mapping[key] = tmp.group(1)
            self.class_mapping_colors[key] = tuple(int(v) for v in re.findall("[0-9]+",tmp.group(2)))
        
        # read montage : channel_id, definition(e.g. FP1-REF -- F7-REF), name,amplitude_scale,color RGB,order_no
        # channel_id is the same as channel_id in  annotation files 
        values,keys = self.readListFile(self.project_info['montage'],None) # read the keys from the file   
        self.montage_ids = keys #[ int(key) for key in keys2];
        #keys = self.montage_ids  
        self.montage_def = dict.fromkeys(keys)
        self.montage_names = dict.fromkeys(keys)
        self.montage_scales = dict.fromkeys(keys)
        self.montage_color = dict.fromkeys(keys)
        self.montage_order = dict.fromkeys(keys)
        
        for key in values:
            tmp=re.search(r'(.+)\,(.*)\,(.*)\,(\(.*\))\,(\d+)',values[key]);
            self.montage_def[key] = tmp.group(1);
            self.montage_names[key] = tmp.group(2)
            self.montage_scales[key] = float(tmp.group(3))
            self.montage_color[key] = tuple(int(v) for v in re.findall("[0-9]+",tmp.group(4)))
            self.montage_order[key] = int(tmp.group(5)) 
            
        # read config here 
        # add later
        
        
        # read user lists  (username : First_name Last_name
        #
        values,keys = self.readListFile(self.project_info['users_list'],None) # read the keys from the file       
        self.usernames=keys;
        self.users = dict.fromkeys(tuple(keys))
        for key in values:
            self.users[key] = values[key];
                  
    def add_finished_file(self,filename):
        with open(self.project_info["finished"],'a') as f:
            if filename not in self.finished_files:
                f.write(filename)
                f.write("\n")
        f.close()
            
    # add new user         
    def add_user(self,username,user):   
        self.usernames.append(username)
        self.users[username] = user
        # write to the file  ( to be updated later)
        with open(self.project_info["users_list"],'w') as f:
            for username, user in self.users.items():
                f.write(username)
                f.write(":")
                f.write(user)
                f.write("\n")
        f.close()
        
    def create_dir_structure(self,username):
        root=self.project_info["root"];
        if username in self.usernames:
            try:
                os.makedirs(username);
            except OSError: # if existed just pass
                pass     
            try:
                os.makedirs(username + "/"+root);  
            except OSError: # if existed just pass
                pass 
            try:    
                os.makedirs(username + "/"+root+"/annotations") 
            except OSError: # if existed just pass
                pass    
        else:
            print "Username is not in the list."
            exit()
        
        # copy the config file if not existed
        if os.path.isfile(username+"/"+self.project_info["config"])==False:
            try:
                shutil.copyfile(self.project_info["config"],username+"/"+self.project_info["config"])
            except IOError:
                print self.project_info["config"]+"can not be copied into "+username+". Either directory is not writable or file is not existed"   
                exit()
        
        # copy the finished file if not existed
        if os.path.isfile(username+"/"+self.project_info["finished"])==False:
            try:
                shutil.copyfile(self.project_info["finished"],username+"/"+self.project_info["finished"])
            except IOError:
                print self.project_info["finished"]+"can not be copied into "+username+". Either directory is not writable or file is not existed"   
                exit()
        self.project_info["finished"] = username+"/"+self.project_info["finished"] 
        
        #populate the finished list
        tmp = open(self.project_info['finished'],'rU').readlines()
        for i in range(len(tmp)):
             tmp[i] = tmp[i].rstrip('\n')
             self.finished_files.append(os.path.basename(tmp[i])); 
                              
       
        # copy annotations into  username/annotations  if not existed  but in any case  change the self.annotation_files to new directory
        for key in self.annotation_files:
          
            if self.annotation_files[key] is not None  and os.path.isfile(self.annotation_files[key]) is True: # if an annotation file is existed copy it to root/annotations other wise we build an empty file based on  corresponding EEG-file
                basename = os.path.basename(self.annotation_files[key])
                
                if os.path.isfile(username+"/"+root+"/annotations/"+basename)==False:
                    try:
                        shutil.copyfile(self.annotation_files[key], username+"/"+root+"/annotations/"+basename)
                    except IOError:
                        print self.annotation_files[key]+" can not be copied into "+username+"/"+root+"/annotations. Either directory is not writable or file is not existed"   
                        exit() 
                self.annotation_files[key]=username+"/"+root+"/annotations/"+basename; #update the file list        
            else: #if annotation is not existed
                basename = os.path.basename(key);
                tmp=basename.split(".")
                filename = tmp[0]+".rec"; # it is the default when there is no annotation file
                self.annotation_files[key]=username+"/"+root+"/annotations/"+filename;
                # create an empty file if needed
                if os.path.isfile(self.annotation_files[key])==False:  
                    open(self.annotation_files[key], 'a').close() 
                    
        #if last_session is not existed (if we have just created the root)copy root into it
        try:
            os.mkdir(username+"/last_session")        
        except OSError:
            pass
        try:
            os.mkdir(username+"/last_session/annotations")        
        except OSError:
            pass
             
        # copy annotations if needed
        #    
        for key in self.annotation_files: # annotation_files is pointing to root sub-directories 
            
            basename = os.path.basename(self.annotation_files[key])
            if os.path.isfile(username+"/last_session/annotations/"+basename)==False: #copy it is not there
                try:
                   shutil.copyfile(self.annotation_files[key], username+"/last_session/annotations/"+basename)
                except IOError:
                   print self.annotation_files[key]+" can not be copied into "+username+"/last_session/annotations. Either directory is not writable or file is not existed"
            self.annotation_files[key]=username+"/last_session/annotations/"+basename; #update the file list
             
             
        # now copy the last_session to current_session (forced)
             
        # first delete the current session if existed
        try:
            shutil.rmtree(username+"/current_session")
        except:
            pass
        try:
        
            os.mkdir(username+"/current_session")
            os.mkdir(username+"/current_session/annotations")
        except:
            
            pass    
                 
        # copy files into current session from last session
        for key in self.annotation_files: # annotation_files is pointing to root sub-directories 
            basename = os.path.basename(self.annotation_files[key])
                 
            try:
                shutil.copyfile(self.annotation_files[key], username+"/current_session/annotations/"+basename)
            except IOError:
                print self.annotation_files[key]+" can not be copied into "+username+"/current_session/annotations. Either directory is not writable or file is not existed"
            self.annotation_files[key]=username+"/current_session/annotations/"+basename; #update the file list
             
             
            
                        
    def calculate_montage(self,physical_channels): 
      
        self.montage_pairs = dict.fromkeys(self.montage_ids)
        for key in self.montage_def:
            mdef=self.montage_def[key];
            pairs=[x.strip() for x in mdef.split('--')]
            
            self.montage_pairs[key]=[]
            for i in range(len(pairs)): # 1 or 2 elements in "pairs" 
                ind = physical_channels.index(pairs[i])
                self.montage_pairs[key].append(ind)
        
        order=[];
        for key in self.montage_order:
            order.append(self.montage_order[key])
        self.montage_map_order2id = dict(zip(order,self.montage_ids)) # map orders to ids
        
                    