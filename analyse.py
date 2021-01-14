#version 1.11

import re
from tkinter import messagebox
from datetime import datetime

DATA_PATTERN = r'.{0,19}\d\d[:.-\/].{0,1}\d\d[:.-\/].{0,1}'
DATE_PATTERNS = ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S',
                 '%Y-%m-%d\t%H:%M:%S', '%d-%m-%Y\t%H:%M:%S',
                    '%d-%m-%y\t%H:%M:%S', '%d.%m.%y\t%H:%M:%S',
                 '%d.%m.%Y %H:%M:%S', '%d-%m-%Y;%H:%M:%S']

class Analyse():

    def __init__(self,filespaths,symbols=False,joincol=False):

        
        self.symbols=symbols
        self.joincol = joincol
        self.freqdelim = None
        self.datafilter = False
        self.fails = []
        self.filespaths = filespaths
        self.separator = self._get_separator()
        self.count_parameters = self._get_count_of_parameters()
        self.header = None

    def chain(self,paths,rowPattern=False):
        """provide one line per call within paths"""
        i = -1
        for path in paths:
            n = i+1
            for i,line in enumerate(open(path)):
                i = i+n
                if rowPattern:
                    if line.split(self.separator)  and not re.search(rowPattern,line):
                        print(line[0:33])
                        continue
                yield i,line

    def reverse_chain(self,path):
        for i,line in enumerate(reversed(open(path).readlines())):
            yield i,line

            
    def load_files(self,paths):
        
        data = {}
        for ount,line in self.chain(paths):
            data[ount] = line.strip().split(self.separator)
        return data

    def _get_count_of_parameters(self):
        temp = []
        for ount, line in self.reverse_chain(self.filespaths[0]):
            items = line.strip().split(self.separator)
            temp.append(len(items))
        if temp[0] == temp[1] and temp[0] == temp[2]:
            return temp[0]
        else:
            print('Program had not defined number of parameters for the file. The file have different number of parameters in different rows')
        
    def _get_separator(self):
        separators = [',',';',';;','\t']
        row1 = row2 = row3 = []
        rows = [row1,row2,row3]
        for (count,line),row in zip(self.reverse_chain(self.filespaths[0]),rows):
            for sep in separators:
                row.append(len(line.split(sep)))
            #print(row1,'\n',row2,'\n',row3,'\n')
        if max(row1) == max(row2) and max(row1) == max(row3):
            ind = row1.index(max(row1))
            #print('separator: ',separators[ind])
        else:
            print('Program had not defined a separator for the file')
        return separators[ind]
           

    def get_index_of_header(self,filepath):
        #count_params = self._get_count_of_parameters()
        for ount, line in self.chain(filepath):
            data = line.strip().split(self.separator)
            if len(data) == self.count_parameters:
                return ount
                
            
            

    def _freq_delim(self,path):
        med = 0
        for count,line in enumerate(open(path)):
            med = med + line.count(self.separator)
            if count == 100:
                break
        return int(.8*med/30)

    def find_index_row(self,paths,pattern,nparams=1,column=(0,),endline=False,printed=False):
        
        for count,line in self.chain(paths):
            if endline:
                continue
            if column == (0,1):
                line = line.replace(self.separator,' ',1)
            items = line.split(self.separator)
            item = items[column[0]]
            if printed:
                print(item,'111111111',pattern)
            if re.search(pattern,item):
                if len(items) >= nparams:
                    
                    break
        return count

    def find_index_column(self,path,pattern):
        #if not self.freqdelim:
            #self.freqdelim = self._freq_delim(path)
        #count_params = self._get_count_of_parameters()
        indexes = []
        for line in open(path):
            items = line.split(self.separator)
            if len(items) == self.count_parameters:
                for count,item in enumerate(items):
                    #if re.match(pattern,item) and line.count(self.separator) >= self.freqdelim:
                    if re.match(pattern,item):
                        indexes.append(count)
            if indexes:
                return tuple(indexes)

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

    def load_data(self,filespaths):
        
        data = {}
        for rowcount,row in self.chain(filespaths,rowPattern=DATA_PATTERN):
            items = row.strip().split(self.separator)
            
            if len(items) == self.count_parameters:
                recognizedItems = self.regognition_items(items,self.dtpattern)
                data[rowcount] = recognizedItems
            else:
                print('row not valid\n',row)
        #print(min(data),max(data),'\n',data)
        return data

    def get_data_indexes(self,filespaths):
        dataIndexes = []
        for direction in [self.chain(filespaths,DATA_PATTERN), self.reverse_chain(filespaths)]:
            for rowCount,row in direction:
                if re.find(row,DATA_PATTERN):
                    dataIndexes.append(rowCount)
                    break
                
            

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


    def get_datetime_pattern(self,filespaths,lineindex,coldate=0):
        for countline,line in self.chain(filespaths):
            if countline == lineindex:
                if coldate == (0,1):
                    line = line.replace(self.separator,' ',1)
                for pattern in DATE_PATTERNS:
                    try:
                        strdate = line.split(self.separator)[0]
                        datetime.strptime(strdate,pattern)
                    except ValueError:
                        continue
                    else:
                        self.dtpattern = pattern
                        return pattern
        
                    
        
        
    def check_valid_header(self,filespaths,keyline): 
        """checks whether all value from header in all files is the same.
        Remove invalid files from the list 'filespaths'. Return validfiles """
        validfiles = []
        names = []
        notvalid = []
        pathdelim = '/'
        for path in filespaths:
            for count,line in enumerate(open(path)):
                if line == keyline:
                    validfiles.append(path)
                    names.append(path.split(pathdelim)[-1])
                    break
                if count > 100:
                    break
        for name in filespaths:
            if not name in validfiles:
                notvalid.append(name.split(pathdelim)[-1])
        if notvalid:
            warning =  f"The file(s) {notvalid} and the sample file '{filespaths[0].split(pathdelim)[-1]}' is not the same type. First one(s) will remove from list of input files."
            messagebox.showinfo('Warning',warning)
        return tuple(validfiles), tuple(names)

    def regognition_items(self,listitems,datetimePattern):
        temp = []
        for item in listitems:
            try:
                if '.' in item:
                    item = float(item)
                else:
                    item = int(item)
            except ValueError:
                try:
                    item = datetime.strptime(item,datetimePattern)
                except ValueError:
                    pass
            finally:
                temp.append(item)

                
        for i in temp:
            print(i,'      ', type(i))
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

         
    def rows_to_columns(self,filespaths,params,selparams,minind,maxind):
        
        #print('draw within dates: ',minind,'-',maxind)

        selind = list(map(lambda p: params.index(p),selparams))
        temp = {}
        for par in selparams:
            temp[par] = []
        #index = -1
        count = -1
        start = False
        stop = False
        for path in filespaths:
            if stop:
                #print('stop brake: ',count)
                break
            for line in open(path):
                
                count += 1
                if count < minind and not start:
                    #print('y start: ',count, line[:30])
                    continue
                    
                start = True
                if line[1].isdigit():
                #if self.symbols:
                #    line = line.replace(self.symbols,'')
                #if self.joincol:
                 #   line = line.replace(self.separator,' ',1)

                    items = list(map(lambda i: line.split(self.separator)[i],selind))

                    #print(items)
                    data = self.recogn_row(items)
                    #print('count,data: ',count,data)
                    for ind,par in zip(selind,selparams):
                        i = selind.index(ind)
                        temp[par].append(data[i])
                if count == maxind:
                    #print('y stop: ',count, line[:30])
                    stop = True
                    break
        return temp

    def _rows_to_columns(self,filespaths,selparams,limitindexes):
        data = dict.fromkeys(selparams,[])
        for count,line in self.chain(filespaths):
            if count >= limitindexes[0] and count <= limitindexes[1]:
                for (par, value),head in zip(data,selparams.values()):
                    item = line.split()[head]
                    print(item,'\n',head)






class ChamberAnalyse(Analyse):

    def read_header(self,filespaths):
        if len(filespaths) > 1:
            self.check_valid_header(filespaths)
        for line in open(filespaths[0]).readlines():
            if 'Temper' in line:
                if self.joincol:
                    line = line.replace(self.separator,' ',1)
                data = line.replace('"','').strip().replace(';','DateTime;',1).split(self.separator)
                break
        return data      

class TestSystemAnalyse(Analyse):

    def __init__(self,filespaths):
        Analyse.__init__(self,filespaths)
        self.separator = ';;' #!!!!!!!!!!!!!!!!!!!!! przerobic _get_separator()
    def get_rows(self,filespath,keyrow):
        i = 0
        
        for path in filespath:
            
            
            for line in f.readlines():
                if i == 0:
                    data1 = line.strip().split(self.separator) #parameters
                elif i == 1:
                    data2 = line.strip().split(self.separator)[1:] #min
                    data2 = self._recogn_row(data2)
                elif i == 2:
                    data3 = line.strip().split(self.separator)[1:] #max
                    data3 = self._recogn_row(data3)
                elif i == 3:
                    data4 = line.strip().split(self.separator)[1:] #default
                    data4 = self._recogn_row(data4)
                elif i == keyrow:
                    data5 = line.strip().replace(';*;',self.separator).split(self.separator) #measure
                    data5 = self._recogn_row(data5)
                i += 1
            break
        #print(data1,data5,data4,data3,data2)
        return data1,data5,data4,data2,data3

    def _get_rows(self,filespaths,keyrow,recogn=False):
        data = []       
#        for path in filespaths:
        for count,line in self.chain(filespaths):
            if count in [0,1,2,3,keyrow]:
                line = line.replace(';','- -',3).replace(';*;',';;')
                items = line.strip().split(self.separator)
                if recogn:
                    items = self._recogn_row(items)
                data.append(items)
#        if len(data) == 5:
        return data

    def get_column(self,filespaths,index,colsubindex=False,colsubdelim=';',datafilter=False,wordfilter=None):
        data = {}
        for count,line in self.chain(filespaths):
            if line[1].isdigit():
                if datafilter and not wordfilter in line:
                    continue
                temp = line.split(self.separator)[index]
                #item = temp.replace(';',' ')
                if colsubindex:
                    temp = temp.split(colsubdelim)[colsubindex[0]:colsubindex[1]]
                data[count] = temp
        return data

if __name__ == '__main__':

##    filepaths = ['c:/Users/Настюшка/AppData/Local/Programs/Python/Python37/Project/Input_files/Cooling/20200421.csv',
##    'c:/Users/Настюшка/AppData/Local/Programs/Python/Python37/Project/Input_files/Cooling/20200422.csv',
##    'c:/Users/Настюшка/AppData/Local/Programs/Python/Python37/Project/Input_files/Cooling/20200423.csv']

    filepaths = ['e:/Projects/Input_files/Cooling/20200501.csv',
'e:/Projects/Input_files/Cooling/20200502.csv',
'e:/Projects/Input_files/Cooling/20200429.csv',
'e:/Projects/Input_files/Cooling/20200430.csv']

#filepaths = ['e:/Projects/Input_files/MUUT hPAD/[87213004]_[C1.SW350]_[K-09 Damp heat cyclic]_[2020-04-24][15.04.28][02]_01.txt']
    
#files = Analyse(filepaths,symbols='"',joincol=True)
##    files.check_valid_header()
##    print('\nvalid',files.validfiles)
##    files.check_valid_rows()
#    print('data',files.data['20200417.csv'][10])
#    files.number_rows()
#    files.read_header()
#    print('\nparams',files.params)
    
#files.rows_to_columns(filepaths)
#    print(files.params)
#    files.analyse_columns()
