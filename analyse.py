#version 1.16

import re
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import re
import io

DATA_PATTERN = r'.{0,19}\d\d[:.-\/].{0,1}\d\d[:.-\/].{0,1}'

DATE_PATTERNS_2 = [r'^.{0,2}\d\d[-.\\/]\d\d[-.\\/].{0,2}\d\d[_ ]\d\d[:.]\d\d[:.]\d\d.{0,4}$',
                   r'^.{0,2}\d\d[-.\\/]\d\d[-.\\/].{0,2}\d\d$',
                   r'^\d\d[:.]\d\d[:.]\d\d$',
                   r'^\d\d[:.]\d\d[:.]\d\d[.]\d\d$']

DATE_PATTERNS = ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S',
                 '%Y-%m-%d\t%H:%M:%S', '%d-%m-%Y\t%H:%M:%S',
                    '%d-%m-%y\t%H:%M:%S', '%d.%m.%y\t%H:%M:%S',
                 '%d.%m.%Y %H:%M:%S', '%d-%m-%Y;%H:%M:%S',
                 '%y-%m-%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S',
                 '%m-%d-%Y %H:%M:%S', '%Y-%m-%d_%H:%M:%S.%f']
class BaseAnalyse():

    def __init__(self, filespaths, **kw):
         self.filespaths = filespaths
         self._kw = kw
         print(self.filespaths)
         self.df = self._create_df(filespaths)
         self.dtcolumn = self._kw.get('dtcolumn', None)
         #selfdf1 = self._create_df_from_table(self.filespaths[0], **self.kwds)

    def _create_df(self, filespaths):
        """"""
        method = self._choice_method(filespaths)
        if len(self.filespaths) > 1:
            list_df = []
            for path in filespaths:
                list_df.append(method(path))
            df = pd.concat(list_df)
            del(list_df)
        else:
            df = method(filespaths[0])
        return df
    
    def _choice_method(self, filepath):
##        if '.xxls' in filepath.lower(): #przerobic
##            return self._create_df_from_excel
##        else:
        return self._create_df_from_csv_txt_cmr

    def _create_df_from_csv_txt_cmr(self, filepath):
        dataframe = pd.read_csv(filepath, **self._kw)
        return dataframe

    def _create_df_from_excel(self, filepath):
        dataframe = pd.read_excel(filepath, **self._kw)
        return dataframe

    def get_index_of_datetime_column(self):
        if self.dtcolumn is None:
            for i, par in enumerate(self.df):
                if isinstance(self.df[par][0], datetime) or self.df[par].dtype == "datetime64[ns]":
                    self.dtcolumn = i
                    break
            print('self.dtcolumn', self.dtcolumn)
        return self.dtcolumn

    def get_indexes_columns(self, columnnames):
        """get int indexes of column names of dataframe"""
        indexes = []
        for i, name in enumerate(self.df):
            if name in columnnames:
                indexes.append(i)
        return indexes


class ChamberAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        BaseAnalyse.__init__(self, filespaths,
                             sep=';',
                             parse_dates=[0],
                             header=3,
                             engine='c',
                             skiprows=(6,),
                             memory_map=True
                             )
   
        
class TestSystemCmrNewAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        fileobj = [_dtc_replacer(filespaths[0])]
        
        BaseAnalyse.__init__(self, fileobj,
                             sep=';',
                             parse_dates=[0],
                             header=19,
                             engine='c',
                             skiprows=(20,)
                             )
        

class TestSystemCmrOldAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        BaseAnalyse.__init__(self, filespaths,
                             sep=';',
                             parse_dates=[0],
                             dtype={'DTC':'object'},
                             na_values=['N/A'],
                             keep_default_na=False,
                             low_memory=False,
                             #converters={'DTC':lambda x: x.replace('', 'NA') },
                             header=19,
                             engine='c',
                             skiprows=(20,)
                             )

class DMMAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        BaseAnalyse.__init__(self, filespaths,
                             sep='\t',
                             #parse_dates={'Timestamp':[0,1]},
                             #names=['Date', 'Time', 'Current, A'],
                             #converters={'Value':_replacer}
                             header=0,
                             engine='c',
                             dayfirst=False,
                             memory_map=True
                             )
        
        self.df['Timestamp'] = self._recogn_date(self.df['Date'] + ' ' + self.df['Time'])
        self.df.drop(['Date', 'Time'], 1, inplace=True)
        self.df['Value'].replace({' A':''}, regex=True, inplace=True)
        self.df = self.df.astype({'Timestamp':'datetime64', 'Value':float})
        
       
    def _recogn_date(self, df):
        new_df = pd.to_datetime(df,
                                 yearfirst=True,
                                 format='%y-%m-%d %H:%M:%S.%f',
                                 exact=True,
                                 )
        return new_df

class CoolingSystemAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        BaseAnalyse.__init__(self, filespaths,
                             sep='\t',
                             parse_dates=[[0,1]],
                             header=0,
                             engine='c',
                             )
    
        
class RotronicAnalyse(BaseAnalyse):
    
    def __init__(self, filespaths, **kw):
        """dtcolumn=None"""
        BaseAnalyse.__init__(self, filespaths,
                             sep='\t',
                             parse_dates=[[0, 1]],
                             header=32,
                             names=['Date', 'Time','Humidity, %', 'Temperature, ℃'],
                             usecols=['Date', 'Time','Humidity, %', 'Temperature, ℃'],
                             engine='c',
                             skiprows=(43,),
                             memory_map=True
                             )

def _dtc_replacer(filepath): #przerobic na paths
    """it replaces needless delimiters which matched patterns. Returns file object"""
    pattern = '\d{3}.{3}:.{5,}\n'
    with open(filepath, encoding='latin-1') as f:
        fileobj = f.read()
    string = re.sub(pattern, lambda x: x.group(0).replace(';', '\t').replace('\n', '',1), fileobj)
    #print(string)
    return io.StringIO(string)
             
class Analyse():
    
    def __init__(self,filespaths,log_instance=None, filterinputdata=False):

        self.log_instance = log_instance
        self.filespaths = filespaths
        self.filterinputdata = filterinputdata
        
##        self.scan_file()
##
##    def scan_file(self):
                             
        self.separator = self._get_separator(self.filespaths[0])
        self.replacements = [('"',''), # log file from cooling system
                             (' A',''), # log file from DMM
                             (f' {self.separator}',f'{self.separator}')]  # log file from chamber
                              
        self.number_of_parameters = self._get_number_of_parameters(self.filespaths[0])
        self.headerindex, self.rawheader = self._get_raw_header(self.filespaths[0])
        
        self.validfiles = self._check_valid_header(self.filespaths,
                                                   self.headerindex,
                                                   self.rawheader)
        self.firstDataIndex = self._get_first_data_index(self.validfiles,
                                                         self.number_of_parameters,
                                                         DATA_PATTERN)
            
        self.datetimeColumnsIndex = self.find_index_column(self.validfiles[0],
                                                           self.firstDataIndex,
                                                          DATE_PATTERNS_2,
                                                           ('"',''))
        if self.datetimeColumnsIndex == (0,1):
            self.rawheader = self.rawheader.replace(self.separator,'',1)
        if self.check_unique_parameters(self.rawheader):
            self.header = self.rawheader.split(self.separator)
        else:
            self.header = self.get_two_line_header(self.validfiles[0],
                                                    self.headerindex,
                                                    self.rawheader,
                                                    self.datetimeColumnsIndex)
            
        self.datetimePattern = self.get_datetime_pattern(self.validfiles,
                                                         DATE_PATTERNS,
                                                         self.firstDataIndex,
                                                         self.datetimeColumnsIndex)
        self.data = self.load_data(self.validfiles,
                                   self.firstDataIndex,
                                   self.datetimePattern,
                                   self.datetimeColumnsIndex,
                                   replace=[('A',''),('"','')],
                                   filterinputdata = self.filterinputdata)  # przerobic!!!!!!!!!!!!!!
        for k,v in self.data.items():
            self.logging(f'ONE DATA ROW: {k,v}', 'with_timestamp')
            break

        self.minDate, self.maxDate = self.min_max_date(self.data)

    def logging(self, data, mode="simple"):
        """Send log data to log_instance if it presense, otherwise print log data.
        It is possible runs in next modes: "simple", "error", with_timestamp"."""
        if self.log_instance:
            if mode == 'simple':
                self.log_instance.simple_log(data)
            elif mode == 'error':
                self.log_instance.log_error(data)
            elif mode == 'with_timestamp':
                self.log_instance.log_with_timestamp(data)
        else:
            print(data)
        
    def chain(self, paths, row_start=False, row_end=False, filterinputdata=False):
        """provide one line per call within paths"""
        i = -1
        n = 0
        for path in paths:
            n = i+n+1
            with open(path) as f:
                for i,row in enumerate(f):
                    if row_start:
                        if i < row_start:
                            continue
                    if filterinputdata:
                        if i%2 == 0:
                            continue
                    if self.replacements:
                        for r in self.replacements:
                            if len(r) == 3:
                                row = row.replace(r[0],r[1],r[2])
                            elif len(r) == 2:
                                row = row.replace(r[0],r[1])
                    if row_end:
                        if i > row_end:
                            return StopIteration
                    yield i+n, row

    def slow_chain(self, file_path, row_start=False, row_end=False):
        """The function work with one file. Provides one edited data row"""
        with open(file_path) as f:
            for i,row in enumerate(f):
                    if i < row_start:
                        continue
                    if row_end and i > row_end:
                        return StopIteration
                    if self.replacements:
                        for r in self.replacements:
                            if len(r) == 3:
                                row = row.replace(r[0],r[1],r[2])
                            elif len(r) == 2:
                                row = row.replace(r[0],r[1])
                    yield i, row

    def reverse_chain(self,filePath):
        try:
            for i,line in enumerate(reversed(open(filePath, encoding='utf-8').readlines())):
                yield i,line
        except UnicodeDecodeError:
            for i,line in enumerate(reversed(open(filePath, encoding='latin-1').readlines())):
                yield i,line
            

            
##    def load_files(self,paths):
##        
##        data = {}
##        for ount,line in self.chain(paths):
##            data[ount] = line.strip().split(self.separator)
##        return data

        
    def _get_separator(self,file_path):
        separators = [',',';','\t']
        length_rows = [[],[],[]]
        for (i,row),item in zip(self.reverse_chain(file_path),length_rows):
            for sep in separators:
                item.append(len(row.split(sep)))
        if max(length_rows[0]) == max(length_rows[1]) and max(length_rows[0]) == max(length_rows[2]):
            ind = length_rows[0].index(max(length_rows[0]))
            separator = separators[ind]
            self.logging(f'SEPARATOR: {repr(separator)}')
            return separator
        else:
            self.logging('Program had not defined a separator for the file','error')

    def _get_number_of_parameters(self, file_path, replace=None):
        """Get number of parameters of one input file.
            Need separator and scan rows of the file from end"""
        n = []
        i = 0
        for row_count, row in self.reverse_chain(file_path):
            if i > 2:
                break
            if replace:
                row = row.replace(replace[0],replace[1])
            items = row.strip().split(self.separator)
            n.append(len(items))
            i += 1
        if n[0] == n[1] and n[0] == n[2]:
            self.logging(f'NUMBER OF PARAMETERS: {n[0]}')
            return n[0]
        else:
            self.logging("""Program had not defined number of parameters for the file.
                        The file have different number of parameters in different rows: {n}""", 'error')
        
    def _get_raw_header(self, file_path, replace=False):
        """Read file sequently and return raw row and rowindex
        which have as number of parameters as self.number_of_parameters"""
        for row_count, row in self.slow_chain(file_path):
            if replace:
                row = row.replace(replace[0], replace[1])
            header = row.strip().split(self.separator)
            if len(header) == self.number_of_parameters:
                self.logging(f'HEADER INDEX, HEADER LINE: {row_count}, "{row[:85]}..."')
                return row_count, row
        self.logging('Program had not find a header for the file','error')
                
    def min_max_date(self,data):
        dateList = []
        for rowIndex, dataLine in data.items():
            dateList.append(dataLine[0])
        return min(dateList), max(dateList)
        

    def find_index_dateitem(self,dateItem):
        temp = {}
        for rowCount, dataLine in self.data.items():
            if dateItem > dataLine[0]:
                value = dateItem-dataLine[0]
            elif dateItem <= dataLine[0]:
                value = dataLine[0] - dateItem
            temp[value] = rowCount
        return temp[min(temp)]

    def find_index_column(self,filePath,firstDataIndex,patterns,replace=False): ###przerobic
        indexes = []
        for rowCount,row in self.chain([filePath]):
            if rowCount < firstDataIndex:
                continue
            if replace:
                row = row.replace(replace[0],replace[1])
            items = row.split(self.separator)
            for itemCount,item in enumerate(items):
                for pattern in patterns:
                    #print(pattern,item)
                    if re.match(pattern,item):
                        indexes.append(itemCount)
                        break
            #print(indexes)
            if len(indexes) == 2:
                self.log_instance.simple_log(f'COLUMN INDEXES: {indexes}')
                return tuple(indexes)
            elif indexes == [0]:
                self.log_instance.simple_log(f'COLUMN INDEX: {indexes}')
                return 0
            else:
                self.log_instance.log_error('Program had not find indexes for the file')
                break

    # def find_datetime_col(self,path):
    #     pattern = r'.{0,19}\d\d[:.-\/].{0,1}\d\d[:.-\/].{0,1}'
    #     index = []
    #     for line in open(path):
    #         if len(line)>3 and line[1].isdigit():
    #             items = line.split(self.separator)[:2]
    #             for count,item in enumerate(items):
    #                 if re.match(pattern,item):
    #                     index.append(count)
    #             return tuple(index)

    def load_data(self,filespaths,
                  firstDataIndex=None,
                  dtPattern=None,
                  columnDateIndexes=None,
                  subcolumnDateIndexes=None,
                  replace=[],
                  endDataIndex=None,
                  filterinputdata=False):
        data = {}
        for rowcount,row in self.chain(filespaths,firstDataIndex,endDataIndex, filterinputdata):
            if columnDateIndexes == (0,1):
                row = row.replace(self.separator,' ',1)
            elif subcolumnDateIndexes == (0,1):
                row = row.replace(self.subseparator,' ',1).replace(self.subseparator,self.separator,2)
            if replace:
                for i in replace:
                    if len(i) == 3:
                        row = row.replace(i[0],i[1],i[2])
                    else:
                        row = row.replace(i[0],i[1])
                #row = row.replace(replace[0],replace[1])
            items = row.strip().split(self.separator)
            recognizedItems = self.regognition_items(items,dtPattern)
            data[rowcount] = recognizedItems
        return data

    def _get_first_data_index(self,filesPaths,numberParams,dataPattern,replace=None):
            for rowCount,row in self.chain(filesPaths):
                if re.search(dataPattern,row):
                    if replace:
                        row = row.replace(replace[0],replace[1])
                    n = len(row.split(self.separator))
                    if n == numberParams:
                        self.log_instance.simple_log(f'FIRST DATA ROW INDEX: {rowCount}')
                        return rowCount
            return 0
                
            

    def get_column(self,filespaths,colind,startind=0,recogn=None):
        """Get one or two neighboring columns"""
       
        data = []
        for path in filespaths:
            for count,line in enumerate(open(path)):
                if count >= startind:
                # if len(line) < 3 or not line[1].isdigit():
                #     countline = count
                #     continue
                #if replace != None:
                #    line = line.replace(replace,'-')
                #if self.symbols:
                    #line = line.replace(self.symbols,'')
                    #items = line.replace(';*;',self.separator).split(self.separator)[i]
                    items = line.split(self.separator)
                    value = items[colind[0]]
                    if len(colind) == 2:
                        value = value + ' ' + items[colind[1]]
                    if recogn:
                        value = self.recogn_row([value])
                    #for i in index:
                        #values = values + items[i] + ' '
                #items = self.recogn_row([items.rstrip()])
                    data.append(value[0])
                else:
                    data.append('')
            
        #print(data)
        return tuple(data)
    
    def get_col(self,filespaths,indexes,replace=None,fromline=None,toline=None):
        data = []
        for path in filespaths:
            for count,line in enumerate(open(path)):
                if fromline and count < fromline:
                    continue
                items = line.replace(';*;',self.separator).split(self.separator)
                temp = []
                for i in indexes:
                    if replace:
                        items = items[i].replace(replace[0],replace[1])
                    temp.append(items)
                data.append(self.recogn_row(temp)[0])
        return data


    def get_datetime_pattern(self, filesPaths, patterns, dataRowIndex, columnDateIndexes=0, subcolumnDateIndexes=0):
        for rowCount,row in self.chain(filesPaths,dataRowIndex):
            if columnDateIndexes == (0,1):
                row = row.replace(self.separator,' ',1).replace('"','')
            elif subcolumnDateIndexes == (0,1):
                row = row.replace(self.subseparator,' ',1).replace(self.subseparator,self.separator,1)
##            else:
##                row = row.replace(f' {self.separator}',f'{self.separator}')
            #print(row)
            for pattern in patterns:
                try:
                    strDate = row.split(self.separator)[0]
                    datetime.strptime(strDate,pattern)
                except ValueError:
                    continue
                else:
                    self.log_instance.simple_log(f'DATETIME PATTERN: {pattern}')
                    return pattern
            self.log_instance.log_error('Program had not define datetime pattern for the file')
            break
        
                    
    def check_unique_parameters(self, rawheader):
        #two_line_header = False
        header = rawheader.split(self.separator)
        for item in header:
            if header.count(item) > 1:
                #two_line_header = True
                return False
        return True

    def get_two_line_header(self, file_path, headerindex, rawheader, dt_columns=0):
        new_header = []
        rawheader_1 = rawheader.split(self.separator)
        for row_count, row in self.slow_chain(file_path, row_start=headerindex+1):
            if dt_columns == (0,1):
                row = row.replace(self.separator, '', 1)
            rawheader_2 = row.split(self.separator)
            break
        if len(rawheader_1) == len(rawheader_2):
            for one, two in zip(rawheader_1, rawheader_2):
                new_header.append(one+two)
            return new_header
        else:
            self.logging('len(header_1) and len(header_2) dont match','error')
                
                    
                
        
    def _check_valid_header(self, filespaths, headerindex, rawheader): 
        """checks whether all value of header in all files is the same.
        Remove invalid files from the list 'filespaths'. Return validfiles """
        validfiles = []
        names = []
        notvalid = []
        pathdelim = '/'
        for path in filespaths:
            for row_count, row in self.slow_chain(path):
                if row_count != headerindex:
                    continue
                else:
                    if row == rawheader:
                        validfiles.append(path)
                        names.append(path.split(pathdelim)[-1])
                        break
                notvalid.append(path.split(pathdelim)[-1])
        if notvalid:
            warning =  f"The file(s) {notvalid} and the file '{names[0]}' is not the same type. First one(s) will remove from list of input files."
            messagebox.showinfo('Warning',warning)
        
        self.logging('VALIDFILES:')
        for name in names:
            self.logging(name)
        return tuple(validfiles)

    def regognition_items(self,listitems,dtPattern):
        temp = []
        for item in listitems:
            try:
                if '.' in item:
                    item = float(item)
                else:
                    item = int(item)
            except ValueError:
                try:
                    item = datetime.strptime(item,dtPattern)
                except ValueError:
                    pass
            finally:
                temp.append(item)
        #for i in temp:
            #print(i,'      ', type(i))
        return(temp)

    def recogn_row(self,row):
        YYYYMM = r'.{0,2}\d{4}[/.-]\d\d[/.-]\d{2}.{1}\d\d[:.]\d\d[:.]\d\d'
        MMYYYY = r'.{0,2}\d{2}[/.-]\d\d[/.-]\d{4}.{1}\d\d[:.]\d\d[:.]\d\d'
        integer = r'^-{0,1}.[0-9]{1,50}$'
        typefloat = r'^-{0,1}[0-9]{1,50}[.][0-9]{1,50}$'
        na = r'[nN][Aa]'
        repl = r'^".*"$'
        data = []
        for value in row:
            if re.match(repl,value):
                value = value.replace('"','') 
            if re.match(typefloat,value):
                value = float(value)
            elif re.match(integer,value):
                value = int(value)
            elif re.match(MMYYYY,value):
                v = value.replace('/','-',2).replace('.',':')
                value = datetime.strptime(v,'%d-%m-%Y %H:%M:%S')
            elif re.match(YYYYMM,value):
                v = value.replace('/','-',2)
                value = datetime.strptime(v,'%Y-%m-%d %H:%M:%S')
            elif re.match(na,value):
                value = 0
            data.append(value)
        return tuple(data)

    def _recogn_row(self,row): #переробити на re
        data = []
        for value in row:
            # if '"' in value:
            #     value = value.replace('"','')
            if value.count('/') > 1 or value.count('.') > 1:
                data.append(value.replace('/','-'))
            elif value.count('.') == 1 and value.replace('.','').isdigit():
                data.append(float(value))
            elif value.isdigit() or (value[1:].isdigit() and value[0] == '-'):
                data.append(int(value))
            else:
                data.append(value)
        return data

    
    def get_raw_row(self,paths,index='END',replace=None,reverse=None):
        if reverse != None:
            readmode = self.reverse_chain(paths[-1])
        elif reverse == None:
            readmode = self.chain(paths)
        for count,line in readmode:
            if count == index:
                if replace:
                    line = line.replace(replace[0],replace[1],replace[2])
                return line

    # def replacer(self,items,replace=None):
    #     if replace:
    #         temp = []
    #         for item in items:
    #             for r1,r2 in zip(replace):
    #                 item = replace(r1,r2)
    #             data.append(item)
    #     return temp

         
##    def rows_to_columns(self,filespaths,params,selparams,minind,maxind):
##        
##        #print('draw within dates: ',minind,'-',maxind)
##
##        selind = list(map(lambda p: params.index(p),selparams))
##        temp = {}
##        for par in selparams:
##            temp[par] = []
##        #index = -1
##        count = -1
##        start = False
##        stop = False
##        for path in filespaths:
##            if stop:
##                #print('stop brake: ',count)
##                break
##            for line in open(path):
##                
##                count += 1
##                if count < minind and not start:
##                    #print('y start: ',count, line[:30])
##                    continue
##                    
##                start = True
##                if line[1].isdigit():
##                #if self.symbols:
##                #    line = line.replace(self.symbols,'')
##                #if self.joincol:
##                 #   line = line.replace(self.separator,' ',1)
##
##                    items = list(map(lambda i: line.split(self.separator)[i],selind))
##
##                    #print(items)
##                    data = self.recogn_row(items)
##                    #print('count,data: ',count,data)
##                    for ind,par in zip(selind,selparams):
##                        i = selind.index(ind)
##                        temp[par].append(data[i])
##                if count == maxind:
##                    #print('y stop: ',count, line[:30])
##                    stop = True
##                    break
##        return temp

    def rows_to_columns(self,data,selparams,limitindexes=False):
        #temp = dict.fromkeys(selparams,[])
        temp = {par : [] for par in selparams }
        for rowCount, rowItems in data.items():
            if limitindexes and (rowCount < limitindexes[0] or rowCount > limitindexes[1]):
                continue
            for parameter, parValues in temp.items():
                value = rowItems[selparams[parameter]]
                parValues.append(value)
        return temp






   

class TestSystemAnalyse_1(Analyse):

    def __init__(self,filespaths,log_instance=None):
        #Analyse.__init__(self,filespaths)
        self.filespaths = filespaths
        self.log_instance = log_instance
        self.replacements = [(';*;',';;'), # log file from cooling system
                             (';\n','\n')]

##        c=0
##        for line in open(self.filespaths[0]).readlines():
##            line = line.replace(';',';;',3)
##            print(c,len(line.split(';;')))
##            c += 1

        
        self.separator = self._get_separator(self.filespaths)
        self.subseparator = ';'
        self.datetimecolumnconfig = (0,(0,1)) #0-column, (0,1)-subcolumns
        self.subcolumnconfig = (0,(0,3))    #0-column, (0,3)-subcolumnsc 0,1,2
        self.keyword = 'Failed'
        self.datafilter = False
        self.fails = []
        self.number_of_parameters = self._get_number_of_parameters(self.filespaths[0], replace=(';*;',';;'))
        self.headerindex, self.rawheader = self._get_raw_header(self.filespaths[0])
        #print('self.rawheader',self.rawheader)
        
        self.validfiles = self._check_valid_header(self.filespaths,
                                                   self.headerindex,
                                                   self.rawheader)
        self.firstDataIndex = self._get_first_data_index(self.validfiles,
                                                         self.number_of_parameters,
                                                         DATA_PATTERN,
                                                         replace=(';*;',';;'))
        self.datetimeColumnsIndex = 0
        self.header = self.rawheader.replace(';',';;',3).split(self.separator)
        #print(self.firstDataIndex)
        if self.firstDataIndex:
            self.subcolumnDateIndexes = (0,1)
            self.datetimePattern = self.get_datetime_pattern(self.validfiles,
                                                         DATE_PATTERNS,
                                                         self.firstDataIndex,
                                                         self.datetimeColumnsIndex,
                                                         self.subcolumnDateIndexes)
        else:
            self.firstDataIndex = 1 #przerobić na metod !!11!!!!!!!!!
            self.datetimePattern = '%S.%f'
            self.subcolumnDateIndexes = False
        self.data = self.load_data(self.validfiles,
                                   self.firstDataIndex,
                                   self.datetimePattern,
                                   self.datetimeColumnsIndex,
                                   self.subcolumnDateIndexes,
                                   replace=[(';*;',';;')])
        for k,v in self.data.items():
            self.log_instance.log_with_timestamp(f'ONE DATA ROW: {k,v}')
            break
        
        self.additionalData = self.load_data(self.validfiles,
                                             0,
                                             self.datetimePattern,
                                             self.datetimeColumnsIndex,
                                             self.subcolumnDateIndexes,
                                             replace=[(';*;',';;',3),(';\n','\n')],
                                             endDataIndex = 3)

        
    def _get_separator(self,filesPaths):
        #print(filePath)
        separators = (';;',';')
        for rowCount, row in self.chain(filesPaths):
            if rowCount == 0:
                for sep in separators:
                    if sep in row:
                        self.log_instance.simple_log(f'SEPARATOR: {sep}')
                        return sep
            else:
                self.log_instance.log_error('program not find separator')
                break
                    
            
                
        
##    def get_rows(self,filespath,keyrow):
##        i = 0
##        
##        for path in filespath:
##            
##            
##            for line in f.readlines():
##                if i == 0:
##                    data1 = line.strip().split(self.separator) #parameters
##                elif i == 1:
##                    data2 = line.strip().split(self.separator)[1:] #min
##                    data2 = self._recogn_row(data2)
##                elif i == 2:
##                    data3 = line.strip().split(self.separator)[1:] #max
##                    data3 = self._recogn_row(data3)
##                elif i == 3:
##                    data4 = line.strip().split(self.separator)[1:] #default
##                    data4 = self._recogn_row(data4)
##                elif i == keyrow:
##                    data5 = line.strip().replace(';*;',self.separator).split(self.separator) #measure
##                    data5 = self._recogn_row(data5)
##                i += 1
##            break
##        #print(data1,data5,data4,data3,data2)
##        return data1,data5,data4,data2,data3

##    def _get_rows(self,filespaths,keyrow,recogn=False):
##        temp = []       
###        for path in filespaths:
##        #for rowCount,row in self.chain(filespaths):
##        for rowCount,row in self.additionalData.items():
##            if rowCount in [0,1,2,3]:
##                #line = line.replace(';','- -',3).replace(';*;',';;')
##                #items = line.strip().split(self.separator)
##                #if recogn:
##                    #items = self._recogn_row(items)
##                
##                temp.append(row)
###        if len(data) == 5:
##        #print(data)
##        return temp

    def get_column(self,filesPaths,colindex,firstdataindex,subcolumnconfig=None,subseparator=';',datafilter=False,wordfilter=None):
        data = {}
        for rowCount,row in self.chain(filesPaths):
            if rowCount < firstdataindex:
                continue
            if datafilter and not wordfilter in row:
                continue
            temp = row.split(self.separator)[colindex]
            #item = temp.replace(';',' ')
            if subcolumnconfig:
                temp = temp.split(subseparator)[subcolumnconfig[1][0]:subcolumnconfig[1][1]]
            data[rowCount] = temp
        return data

if __name__ == '__main__':
    PATHS = [r'c:\Users\fjr0p1\Downloads\tym\Chamber_log_EWR91188_mPad_k-02_LegB.txt']
             #r'c:\Users\fjr0p1\Downloads\tym\cut2_Chamber_log_EWR91188_mPad_k-02_LegB.txt']
    #an = ChamberAnalyse(PATHS)
    #an.get_index_of_datetime_column()
    #for i in [an.df.head(5), an.get_index_of_datetime_column()]:
        #print(i)
    #print(an.df.dtypes)
    PATHS = [r'c:\Users\fjr0p1\Downloads\tym\DUT01_mode_IIa_armed_20210201203824.cmr']
    #PATHS = [r's:\WMa\TEMP\My\Sample_files\TestSystemCmrOld\DUT01_mode_IIa_armed_LT_20210311131802.cmr']
    ts = TestSystemCmrNewAnalyse(PATHS)
    #print(ts.df.head(55))
    print(ts.df['DTC'][2571:2575])
    #print(ts.df['Lin2Errors'])
    #PATHS = [r'c:\Users\fjr0p1\Downloads\tym\Rotronic_70722040.XLS', r'c:\Users\fjr0p1\Downloads\tym\Ey6242057.xls']
    #ro = RotronicAnalyse(PATHS)
    #ro.get_index_of_datetime_column()
    #print(ro.df.head(55))
    #PATHS = [r's:\WMa\TEMP\My\Sample_files\DMM_Log\DMM_log.txt']
    #dmm = DMMAnalyse(PATHS)
    #print(dmm.df.head(44))
    #print(dmm.df.dtypes)
