'''
Created on August 12, 2014 
Reader for EDF+ files.

@author: MGM

EDF reader for EEG annotator V0.2 & V0.2.1

V0.02: EDF reader in V0.01 reads the whole information inside the EDF file at once. As the time of reading of the EDF files is
increasing when the size of the EDF files is increasing, this code was edited in te form of "isipedfreader.py", for reading the 
EDF files in a way that it reads just the data records within the time (t1, t2). Using this approach, every time that the user 
is moving the time scroll bar or changing timing scales, the "main.py" file sends new (t1, t2) to "ISIPEDFreader.py" and 
"ISIPEDFreader.py" returns data records to "main.py" immediately. The main function of "isipedfreader.py" can be called by:
Data_Records,sample_rate,physical_channels,time,tmp, total_time_recording= load_edf(file,t1,t2)


Note : This version has been edited by MGM. All of the statements which added or edited for this version 
       has been commented by this method: #MGM(V0.2):(Explanation)
'''

import re, datetime, operator, logging
import numpy as np
from collections import namedtuple

EVENT_CHANNEL = 'EDF Annotations'
log = logging.getLogger(__name__)

class EDFEndOfData: pass


def tal(tal_str):
    '''Return a list with (onset, duration, annotation) tuples for an EDF+ TAL
       stream.
    '''
    exp = '(?P<onset>[+\-]\d+(?:\.\d*)?)' + \
    '(?:\x15(?P<duration>\d+(?:\.\d*)))?' + \
    '(\x14(?P<annotation>[^\x00]*))?' + \
    '(?:\x14\x00)'

    def annotation_to_list(annotation):
        return unicode(annotation, 'utf-8').split('\x14') if annotation else []
    
    def parse(dic):
        return (
                float(dic['onset']), 
                float(dic['duration']) if dic['duration'] else 0.,
                annotation_to_list(dic['annotation']))
    
    return [parse(m.groupdict()) for m in re.finditer(exp, tal_str)]


def edf_header(f):
    h = {}
    assert f.tell() == 0  # check file position
    assert f.read(8) == '0       '

    # recording info)
    h['local_subject_id'] = f.read(80).strip()
    h['local_recording_id'] = f.read(80).strip()

    # parse timestamp
    (day, month, year) = [int(x) for x in re.findall('(\d+)', f.read(8))]
    (hour, minute, sec)= [int(x) for x in re.findall('(\d+)', f.read(8))]
    h['date_time'] = str(datetime.datetime(year + 2000, month, day, 
    hour, minute, sec))

    # misc
    h['header_nbytes'] = int(f.read(8))
    subtype = f.read(44)[:5]
    h['EDF+'] = subtype in ['EDF+C', 'EDF+D']
    h['contiguous'] = subtype != 'EDF+D'
    h['n_records'] = int(f.read(8))
    h['record_length'] = float(f.read(8))  # in seconds
    nchannels = h['n_channels'] = int(f.read(4))

    # read channel info
    channels = range(h['n_channels'])
    h['label'] = [f.read(16).strip() for n in channels]  # @UnusedVariable
    h['transducer_type'] = [f.read(80).strip() for n in channels]  # @UnusedVariable
    h['units'] = [f.read(8).strip() for n in channels]  # @UnusedVariable
    h['physical_min'] = np.asarray([float(f.read(8)) for n in channels])  # @UnusedVariable
    h['physical_max'] = np.asarray([float(f.read(8)) for n in channels])  # @UnusedVariable
    h['digital_min'] = np.asarray([float(f.read(8)) for n in channels])  # @UnusedVariable
    h['digital_max'] = np.asarray([float(f.read(8)) for n in channels])  # @UnusedVariable
    h['prefiltering'] = [f.read(80).strip() for n in channels]  # @UnusedVariable
    h['n_samples_per_record'] = [int(f.read(8)) for n in channels]  # @UnusedVariable
    f.read(32 * nchannels)  # reserved
  
    assert f.tell() == h['header_nbytes']
    return h 


class BaseEDFReader:
    def __init__(self, file, st_time, en_time):  #MGM(V0.2): This class changed in V0.2 for partially reading of the EDF file. # @ReservedAssignment
        self.file = file
        self.st_time = st_time    #MGM(V0.2): The starting time for reading raw data records.
        self.en_time = en_time    #MGM(V0.2): The ending time for reading raw data records.
        self.t_counter = 0
        self.t_offset = 0

    def read_header(self):
        self.header = h = edf_header(self.file)

        # calculate ranges for rescaling
        self.dig_min = h['digital_min']
        self.phys_min = h['physical_min']
        phys_range = h['physical_max'] - h['physical_min']
        dig_range = h['digital_max'] - h['digital_min']
        assert np.all(phys_range > 0)
        assert np.all(dig_range > 0)
        self.gain = phys_range / dig_range

  
    def read_raw_record(self):
        '''Read a record with data and return a list containing arrays with raw
           bytes.
        '''
        result = []
        #MGM(V0.02): This part reads raw data records from start time to end time.
        self.n_samples_per_record = self.header['n_samples_per_record']  #MGM(V0.02): Sample per second is one of the important parameters to assign the start point of data for start time.
        self.t_offset = self.header['header_nbytes'] + \
                        (((self.n_samples_per_record[0] * 2) * self.header['n_channels']) *  \
                         (self.st_time + self.t_counter))    #MGM(V0.2): The formula for computing the start time of the raw data. this line adds to change the start point
        samples = self.file.seek(self.t_offset, 0)  #MGM(V0.2): Jumps to starting point of raw data and starts reading.
        self.t_counter+=1   #MGM(V0.2): Pointer for number of recording that should be read.
        #MGM(V0.2): Reading all raw data for duration of a recording time for all of signals.
        for nsamp in self.header['n_samples_per_record']:#MGM(V0.2)
            samples = self.file.read(nsamp * 2)#MGM(V0.2)
            if self.t_counter==(self.en_time-self.st_time+1):#MGM(V0.2)
                raise EDFEndOfData
            result.append(samples)
        return result

    
    def convert_record(self, raw_record):
        '''Convert a raw record to a (time, signals, events) tuple based on
        information in the header.
        '''
        h = self.header
        dig_min, phys_min, gain = self.dig_min, self.phys_min, self.gain
        time = float('nan')
        signals = []
        events = []
        for (i, samples) in enumerate(raw_record):
            if h['label'][i] == EVENT_CHANNEL:
                ann = tal(samples)
                time = ann[0][0]
                events.extend(ann[1:])
            else:
            # 2-byte little-endian integers
                dig = np.fromstring(samples, '<i2').astype(np.float32)
                phys = (dig - dig_min[i]) * gain[i] + phys_min[i]
                signals.append(phys)
        return time, signals, events


    def read_record(self):
        return self.convert_record(self.read_raw_record())


    def records(self):
        '''
        Record generator.
        '''
        try:
            while True:
                yield self.read_record()
        except EDFEndOfData:
            pass


def load_edf(edffile, st_time, en_time): 
    '''Load an EDF+ file.
    
      Very basic reader for EDF and EDF+ files. While BaseEDFReader does support
      exotic features like non-homogeneous sample rates and loading only parts of
      the stream, load_edf expects a single fixed sample rate for all channels and
      loads file partially for st_time to en_time.
    
      Parameters
      ----------
      edffile : file-like object or string
    
      Returns
      -------
      Named tuple with the fields:
        X : NumPy array with shape p by n.
          Raw recording of n samples in p dimensions.
        sample_rate : float
          The sample rate of the recording. Note that mixed sample-rates are not
          supported.
        sens_lab : list of length p with strings
          The labels of the sensors used to record X.
        time : NumPy array with length n
          The time offset in the recording for each sample.
        annotations : a list with tuples
          EDF+ annotations are stored in (start, duration, description) tuples.
          start : float
            Indicates the start of the event in seconds.
          duration : float
            Indicates the duration of the event in seconds.
          description : list with strings
            Contains (multiple?) descriptions of the annotation event.
          totaltime : The whole time of the recording
    '''
    if isinstance(edffile, basestring):
        with open(edffile, 'rb') as f:
            return load_edf(f, st_time, en_time)   #MGM(V0.2): Convert filename to file and changed in V0.2 for partially reading of the EDF file.
    
    reader = BaseEDFReader(edffile, st_time, en_time)   #MGM(V0.2): This class changed in V0.2 for partially reading of the EDF file.
    reader.read_header()
    
    h = reader.header
    log.debug('EDF header: %s' % h)
    
    # get sample rate info
    nsamp = np.unique([n for (l, n) in zip(h['label'], h['n_samples_per_record']) if l != EVENT_CHANNEL])
    assert nsamp.size == 1, 'Multiple sample rates not supported!'
    sample_rate = float(nsamp[0]) / h['record_length']
    
    rectime, X, annotations = zip(*reader.records())
    X = np.hstack(X)
    annotations = reduce(operator.add, annotations)
    chan_lab = [lab for lab in reader.header['label'] if lab != EVENT_CHANNEL]
    
    #MGM(V0.2): create timestamps
    if reader.header['contiguous']:
        time = np.arange(X.shape[1]) / sample_rate
        time = time + st_time    #MGM(V0.2): this line adds to change the start point
    else:
        reclen = reader.header['record_length']
        within_rec_time = np.linspace(0, reclen, nsamp, endpoint=False)
        time = np.hstack([t + within_rec_time + st_time for t in rectime])  #MGM(V0.2): This class changed in V0.2 for partially reading of the EDF file.
         
    totaltime = h['n_records'] * h['record_length']  #MGM(V0.2): Comput total time of the recording
    #MGM(V0.2): return whole duration of the EDF
    tup = namedtuple('EDF', 'X sample_rate chan_lab time annotations totaltime')    #MGM(V0.2): Total time added. 
    return tup(X, sample_rate, chan_lab, time, annotations, totaltime)  #MGM(V0.2): Total time added. 