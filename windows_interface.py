#version 1.11

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from tkinter import *
from analyse import *
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, time, timedelta
import matplotlib.dates as mdates 

class ChamberWindow(Analyse):

    def __init__(self,frame):
        self.frame = frame
        
        self.params = [] #переробити на словник
        self.data = {}
        self.initUI()
        
    def initUI(self):
#        self.filespaths = []
        self.entry_cal = DateEntry(
                                    self.frame,
                                    disableddayforeground='#DCDCDC', date_pattern='yyyy-mm-dd',
                                    showweeknumbers=False, locale='en_US'
                                    )
        self.entry_cal.grid(row=2,padx=10, column=4,sticky='w')
        self.entry_cal.bind('<<DateEntrySelected>>', self._click_calendar)
        #self.entry_cal.bind('<Return>', self._click_calendar)
        

        self.entry_cal2 = DateEntry(
                                    self.frame,
                                    disableddayforeground='#DCDCDC',date_pattern='yyyy-mm-dd',
                                    showweeknumbers=False, locale='en_US'
                                    )
        self.entry_cal2.grid(row=3,padx=10, column=4,sticky='w')
        self.entry_cal2.bind('<<DateEntrySelected>>', self._click_calendar)
        #self.entry_cal2.bind('<Return>', self._click_calendar)

        self.cmbbx11 = ttk.Combobox(self.frame,width=2)
        self.cmbbx11.grid(row=2, column=5)
 
        self.cmbbx12 = ttk.Combobox(self.frame,width=2)
        self.cmbbx12.grid(padx=3,row=2, column=6)

        self.cmbbx21 = ttk.Combobox(self.frame,width=2)
        self.cmbbx21.grid(row=3, column=5)
 
        self.cmbbx22 = ttk.Combobox(self.frame,width=2)
        self.cmbbx22.grid(row=3, column=6)

        self.en_title = Entry(self.frame,width=35)
        self.en_title.grid(padx=30,row=10,columns=2, column=3)

        self.lb_params = Listbox(self.frame,width=30,height=28,selectmode=EXTENDED)
        self.lb_params.grid(padx=10,rows=19,row=1,column=0)
        self.lb_params.bind('<Double-Button-1>',self.select_par)

        self.lb_sel_params = Listbox(self.frame,width=25,height=8)
        self.lb_sel_params.grid(padx=10,row=10,rows=6,column=1)
        self.lb_sel_params.bind('<Double-Button-1>',self.delete_sel_par)

        self.lb_files = Listbox(self.frame,width=25,height=6)
        self.lb_files.grid(padx=10,pady=15,row=2,rows=4,column=1)
        #self.lb_files.bind('<Double-Button-1>',self.delete_file)

        self.lbl_progress = Label(self.frame,font=16)
        self.lbl_progress.grid(row=0,column=1)
        self.lbl_progress['text'] = "Click 'Load files' for start"

        self.lbl_files = Label(self.frame,text='Selected files:')
        self.lbl_files.grid(row=1,column=1,sticky='w')

        self.lbl_selparams = Label(self.frame,text='Selected parameters:')
        self.lbl_selparams.grid(row=9,column=1,sticky='w')

        self.lbl_fromdate = Label(self.frame,text='Draw from date:')
        self.lbl_fromdate.grid(padx=30,row=2,column=3,sticky='w')

        self.lbl_todate = Label(self.frame,text='Draw to date:')
        self.lbl_todate.grid(padx=30,row=3,column=3,sticky='w')

        self.lbl_title = Label(self.frame,text='Chart title:')
        self.lbl_title.grid(padx=30,row=9,column=3,sticky='w')
        #self.lbl_title['text'] = 

        self.b = Button(self.frame,width=27,height=3,font=23,bd=8,relief='groove',text='DRAW',
                        command=self.click_draw)
        self.b.grid(row=18,column=4,columns=3)

        self.cl = Button(self.frame,text='Clear selected parameters',command=self.clear_sel_par)
        self.cl.grid(pady=10,row=17,column=1)

        self.open = Button(self.frame,width=20,height=2,font=17,text='LOAD FILES',command=self._fill_window)
        self.open.grid(pady=25,padx=10,row=0,column=0)

    def _get_filespaths(self):
        try:
            filespaths = list(filedialog.askopenfilenames())
            if filespaths[0]:
                print('List of files: ',filespaths)
        except:
            messagebox.showinfo('Caution','No new selected files')
        else:
            return filespaths

    def _fill_window(self):
        
        patterns = ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S','%Y-%m-%d\t%H:%M:%S', '%d-%m-%Y\t%H:%M:%S',
                    '%d-%m-%y\t%H:%M:%S', '%d.%m.%y\t%H:%M:%S', '%d.%m.%Y %H:%M:%S', '%d-%m-%Y;%H:%M:%S']
       
        
        self.filespaths = self._get_filespaths()
        self.chamberanalyse = ChamberAnalyse(self.filespaths)
        self._clear_widgets()
        self.chamberanalyse._get_separator()


        #self.chamberanalyse.regognition_items()
        
        
        #print(5*'\n')
        
        headerindex = self.chamberanalyse.get_index_of_header(self.filespaths)
        header = self.chamberanalyse.get_raw_row(self.filespaths,headerindex)
        self.filespaths, validnames = self.chamberanalyse.check_valid_header(self.filespaths,header)
        self.fill_lb(self.lb_files,validnames)
        
        self.params = header.strip().split(self.chamberanalyse.separator)
        self.fill_lb(self.lb_params,self.params)

        patterndate = r'.{0,19}\d\d[:.-\/].{0,1}\d\d[:.-\/].{0,1}'
        dtind = self.chamberanalyse.find_index_column(self.filespaths[0],patterndate)
        self.dtcol = {self.params[i]:i for i in dtind}
       
        datalimitsind = []
        n = len(self.params)
        for mode in [False,True]:
            limit = self.chamberanalyse.find_index_row(self.filespaths,patterndate,nparams=n,endline=mode)
            datalimitsind.append(limit)

        self.dtdata = {}
        if dtind == (0,1):
            itemreplace = (self.chamberanalyse.separator,' ',1)
        elif dtind == (0,):
            itemreplace = False
        elif len(dtind) > 2:
            print('Error: Number datetime columns is more than 2')
        pattern = self.chamberanalyse.get_datetime_pattern(self.filespaths,datalimitsind[0],coldate=dtind)
        
        for ind in range(datalimitsind[0],datalimitsind[1]+1):
            row = self.chamberanalyse.get_raw_row(self.filespaths,ind,replace=itemreplace)
            strdate = row.split(self.chamberanalyse.separator)[0]
            self.dtdata[ind] = datetime.strptime(strdate,pattern)
        print('pattern',pattern)
        #alldata = self.chamberanalyse.load_data(self.filespaths)
##        for ind in range(datalimitsind[0],datalimitsind[1]+1):
##            row = self.chamberanalyse.get_raw_row(self.filespaths,ind,replace=('.','-',-1))
##            self.dtdata[ind] = row.split(self.chamberanalyse.separator)[indexes]
        #print(self.dtdata)


 
        datelimits = []
        for ind in datalimitsind:
            row = self.chamberanalyse.get_raw_row(self.filespaths,ind,replace=('.','-',-1))
            if dtind == (0,1):
                row = row.replace(self.chamberanalyse.separator,' ',1)
                #indexes = dtind
            elif len(dtind) > 2:
                print('Error: Number datetime columns is more than 2')
            datelimit = row.split(self.chamberanalyse.separator)[0]
            datelimits.append(datelimit)
        for pattern in patterns:
            try:
                self.mindate = datetime.strptime(datelimits[0],pattern)
                self.maxdate = datetime.strptime(datelimits[1],pattern)
            except ValueError:
                continue
            else:
                self.dtpattern = patterns.index(pattern)
        self._set_date_limits_of_files(self.mindate,self.maxdate)
        self._set_time_limits_of_files(self.mindate,self.maxdate)

    def _clear_widgets(self):
        self.lb_files.delete(0,END)
        self.lb_params.delete(0,END)
        self.params.clear() 
        self.data.clear()
   
    def _fromto_selected_date(self):
        fromdate = self.entry_cal.get_date()
        todate = self.entry_cal2.get_date()
        #if fromdate > todate: #переробити
            #messagebox.showinfo('Caution',"Date 'from' must be lowed than date 'to'")
        return fromdate,todate

    def _fromto_selected_time(self):
        fromtime = time(hour=int(self.cmbbx11.get()), minute=int(self.cmbbx12.get()))
        totime = time(hour=int(self.cmbbx21.get()), minute=int(self.cmbbx22.get()))
        return fromtime,totime

    def _set_date_limits_of_files(self,mindate,maxdate):
        self.entry_cal.config(mindate=mindate,maxdate=maxdate)
        self.entry_cal2.config(mindate=mindate.date(),maxdate=maxdate.date())
        self.entry_cal.set_date(mindate.date())
        self.entry_cal2.set_date(maxdate.date())

    def _set_time_limits_of_files(self,mintime,maxtime):
        num = ['00','01','02','03','04','05','06','07','08','09'] + list(range(10,60))
        self.cmbbx11['values'] = num[mintime.hour:24]
        self.cmbbx11.set(num[mintime.hour])
        self.cmbbx12['values'] = num[mintime.minute:60]
        self.cmbbx12.set(num[mintime.minute])
        self.cmbbx21['values'] = num[:maxtime.hour+1]
        self.cmbbx21.set(num[maxtime.hour])
        self.cmbbx22['values'] = num[:maxtime.minute+1]
        self.cmbbx22.set(num[maxtime.minute]) 

    def _click_calendar(self,event):
        fromdate,todate = self._fromto_selected_date()
        mintime = time(hour=0,minute=0)
        if fromdate == self.mindate.date():
            mintime = self.mindate
        maxtime = time(hour=23,minute=59)  
        if todate == self.maxdate.date():
            maxtime = self.maxdate
        self._set_time_limits_of_files(mintime,maxtime)      
  
    def fill_lb(self,listbox,data):
        for i in data:
            listbox.insert(END,i)
        
    def select_par(self,event):
        select = self.lb_params.curselection()
        inserted = self.lb_sel_params.get(0,END)
        for i in select:
            if not self.params[i] in inserted:
                self.lb_sel_params.insert(END,self.params[i])

    def delete_sel_par(self,event):
        index = self.lb_sel_params.curselection()
        self.lb_sel_params.delete(index[0])

    def clear_sel_par(self):
        self.lb_sel_params.delete(0,END)
        
    def _date_to_pattern(self,datestr):
        if len(str(datestr.day)) < 10:
            day = '0'+str(datestr.day)
        else:
            day = datestr.day
        if len(str(datestr.month)) < 10:
            month = '0'+str(datestr.month)
        else:
            month = datestr.month
        if self.dtpattern == 4:
            return fr'{day}[-.]{month}[-.]\d\d[ ,;\t]{datestr.hour}:{datestr.minute}:\d\d'
        
    def click_draw(self):
        chart = Draw()
        fromtime,totime = self._fromto_selected_time()
        fromdate,todate = self._fromto_selected_date()
        
        #drawfrom = self._date_to_pattern(datetime.combine(fromdate, fromtime))
        #drawto = self._date_to_pattern(datetime.combine(todate, totime))
        drawfrom = datetime.combine(fromdate, fromtime)
        drawto = datetime.combine(todate, totime)
        print('from,to',drawfrom,'\n',drawto)



        limitindexes = []
        for limit in [drawfrom,drawto]:
            for ount,date in self.dtdata.items():
                if abs(date - limit) < timedelta(minutes=1):
                    limitindexes.append(ount)
                    break

        
        #minind = self.chamberanalyse.find_index_row(self.filespaths,drawfrom,column=(0,1))
        #maxind = self.chamberanalyse.find_index_row(self.filespaths,drawto,column=(0,1))
        print('minind,maxind: ',limitindexes)
        #print('draw fromto: ',drawfrom,drawto)
        selpar = {}
        selected = list(self.dtcol) + list(self.lb_sel_params.get(0,END)) 
        for sel in selected:
            index = self.params.index(sel)
            selpar[sel] = index
        #print(selpar)
        data = self.chamberanalyse._rows_to_columns(self.filespaths,selpar,limitindexes)
        x = []
        ydata = {}
        for k,v in data.items():
            #print('k',k, self.dtcol)
            if k in self.dtcol.keys():
                x.append(v)
            else:
                ydata[k] = v
        
        xdata = [datetime.combine(d,t) for d,t in zip(x[0],x[1])]
        title = self.en_title.get()
        del(data)
        chart.plots(xdata,ydata,title)


class TestSystemWindow(ChamberWindow,Analyse):

    def __init__(self,frame):
        ChamberWindow.__init__(self,frame)
        
        
    def initUI(self):
#        self.filespaths = []
        self.clearfails = Button(self.frame,width=17,height=2,font=17,text='PRINT DATA',command=self.print_data)
        self.clearfails.grid(pady=25,padx=10,row=5,column=2)

        self.open = Button(self.frame,text='Load TestSystem file(s)',font=20,height=3,command=self._fill_window)
        self.open.grid(pady=15,padx=55,row=0,column=0)

        self.filter = Button(self.frame,width=17,height=2,font=17,text='FILTER FAILS',state=DISABLED,command=self.filter_fail)
        self.filter.grid(pady=25,padx=10,row=3,column=2)

        self.reportfails = Button(self.frame,width=17,height=2,font=17,text='REPORT FAILS',state=DISABLED,command=self.report_fails)
        self.reportfails.grid(pady=25,padx=10,row=4,column=2)

        self.lblSelTable2 = Label(self.frame,width=175,height=3,anchor=E,wraplength=1600)
        self.lblSelTable2.grid(columns=4,row=9,column=0)
        self.lblSelTable2['text'] = "No selected"

        self.listfiles = Text(self.frame,height=3,width=110,bg='grey90')
        self.listfiles.grid(row=0,column=2,columns=2)
        self.listfiles.insert(END, 'Selected file(s):')
        self.init_table1()
        self.init_table2()

    def init_table1(self):
        
        self.table1 = ttk.Treeview(self.frame, height=28, show="headings", selectmode="browse")
        self.table1.tag_configure('fail',foreground='red')
        self.table1.tag_configure('pass',foreground='green')

        style = ttk.Style(self.frame)
        style.configure('Treeview', rowheight=24) 

        self.scrolltabley1 = Scrollbar(self.frame, command=self.table1.yview)
        self.table1.configure(yscrollcommand=self.scrolltabley1.set)
        self.scrolltabley1.grid(row=1,column=1,rows=7,sticky='ns')

        self.scrolltablex1 = Scrollbar(self.frame,orient=HORIZONTAL, command=self.table1.xview)
        self.table1.configure(xscrollcommand=self.scrolltablex1.set)
        self.scrolltablex1.grid(row=8,column=0,sticky='we')

        self.table1.grid(row=1,rows=7,column=0,sticky='e')
        self.table1.bind('<<TreeviewSelect>>',self.select_table1)
        headings1 = ('Nrow','Date','Time','Result')
        headwidths1 = (50,120,90,63)
        self.config_table(self.table1,headings1,headwidths1)

 
    def init_table2(self):

        self.table2 = ttk.Treeview(self.frame, height=28, show="headings", selectmode="browse")
        self.table2.tag_configure('fail',background='red',foreground='white')

        style = ttk.Style(self.frame)
        style.configure('Treeview', rowheight=24) 

        
        self.scrolltabley2 = Scrollbar(self.frame, command=self.table2.yview)
        self.table2.configure(yscrollcommand=self.scrolltabley2.set)
        self.scrolltabley2.grid(row=1,column=4,rows=7,sticky='ns')

        self.scrolltablex2 = Scrollbar(self.frame,orient=HORIZONTAL, command=self.table2.xview)
        self.table2.configure(xscrollcommand=self.scrolltablex2.set)
        self.scrolltablex2.grid(row=8,column=3,rows=1,sticky='we')

        self.table2.grid(row=1,rows=7,column=3,sticky='se')
        self.table2.bind('<<TreeviewSelect>>',self.select_table2)

        headings2 = ('parameters','results','Default','Min','Max')
        headwidths2 = (650,100,100,100,100)
        self.config_table(self.table2,headings2,headwidths2)

    def config_table(self,table,headings,headwidths):
        table["columns"] = headings
        for head,hwidth in zip(headings,headwidths):
            table.heading(head, text=head, anchor=CENTER)
            table.column(head,width=hwidth,minwidth=hwidth-8, anchor=W)


    def fill_text(self,widget,data):
        widget.delete(1.0, END)
        for i in data:
            widget.insert(END,i)
    
    def clear_table(self,table):
        for i in table.get_children():
            table.delete(i)
            
    def get_item_table(self,table):
        select = table.selection()
        return select, table.item(select,'values')
        
    def filter_fail(self):
        
        keyword = 'Failed'
        if not self.anmuut.datafilter:
            
            self.anmuut.datafilter = True
            self.filter.config(text='VIEW ALL DATA')
            #item = 'I001'
            #value=0
        else:
            self.anmuut.datafilter = False
            self.filter.config(text='FILTER FAILS')
            #selection = self.get_item_table(self.table1)
            #item = selection[0]
            #value = selection[1][0]
            #print(item,value)
        self.clear_table(self.table1)
        self.tempdata = self.anmuut.get_column(self.filespaths,0,colsubindex=[0,3],datafilter=self.anmuut.datafilter,wordfilter=keyword)
        self.fill_table1(self.tempdata)
        #self.table1.selection_set(item)
        #self.table1.see(value)
        self.tempdata = {}
        
        #self.table.tag_configure('ttk', background='yellow')
        #self.table.tag_configure('simple', foreground='red')
        #self.table.insert('', 1, text='Date', tags=('ttk', 'simple'))
        #self.table.tag_bind('ttk', '<1>', self.itemClicked)

    def report_fails(self):
        print('Fails:\n')
        for i in self.anmuut.fails:
            print(i)
        self.anmuut.fails = []
    
    def select_table1(self,event):
        select = self.table1.selection()
        data = self.table1.item(select,'values')
        self.clear_table(self.table2)
        self.fill_table2(keyrow=int(data[0]))

    def select_table2(self,event):
        select = self.table2.selection()
        data = self.table2.item(select,'values')
        self.lblSelTable2['text'] = '      '.join(data)
        
    def print_data(self,event):
        self.data = {}
        self.data = self.anmuut.load_files(self.filespaths)
        for k,v in self.data.items():
            print('%4s,%200s'% (k,v))

    def fill_table1(self,data):
        keyword = "Failed"
        for k,v in data.items():
            if keyword in v:
                tag='fail'
            else:
                tag='pass'
            self.table1.insert('',END,values=(k,v[0],v[1],v[2]),tags=tag)

    def fill_table2(self,keyrow=4):
        data = self.anmuut._get_rows(self.filespaths,keyrow,recogn=True)
        for ai,bi,ci,di,ei in zip(data[0],data[1],data[2],data[3],data[4]):
            #print('ai=',ai,'bi=',bi,'ci=',ci,'di=',di,'ei=',ei)
            if ei == 'NA':
                continue
            try:
                if not isinstance(ei,str) and (ei < bi or ei > ci):
                    self.table2.insert('',END,values=(ai,ei,di,bi,ci),tags='fail')
                    if ai not in self.anmuut.fails:
                        self.anmuut.fails.append(ai)
                    #print('Failed: ',ai,'value:',ei,'min:',bi,'max:',ci)
                elif isinstance(ei,str) and isinstance(bi,str) and isinstance(ci,str):
                    if ei != (ci or bi):
                        self.table2.insert('',END,values=(ai,ei,di,bi,ci),tags='fail')
                        if ai not in self.anmuut.fails:
                            self.anmuut.fails.append(ai)
                elif not self.anmuut.datafilter:
                    self.table2.insert('',END,values=(ai,ei,di,bi,ci))
            except TypeError:
                if not self.anmuut.datafilter:
                    self.table2.insert('',END,values=(ai,ei,di,bi,ci))
    

#    def get_paths(self):
 #       paths = list(filedialog.askopenfilenames())
  #      if paths:
  #          self.filespaths = paths
            

    def _fill_window(self):
        col = 0 
        
        self.filespaths = self._get_filespaths()
        self.anmuut =  TestSystemAnalyse(self.filespaths)
        
        if self.filespaths:
            listfiles = ['Selected file(s):\n']
            for i in self.filespaths:
                listfiles.append(i.split('/')[-1]+'\n')
            self.fill_text(self.listfiles,listfiles)
            self.clear_table(self.table1)
            
            data = self.anmuut.get_column(self.filespaths,col,colsubindex=(0,3))
            #print(data)
            self.fill_table1(data)
            self.filter.config(text='FILTER FAIL',state=NORMAL)
            self.reportfails.config(state=NORMAL)

            self.fill_table2()

class Draw():

    def plot(self,x,ydata,title,ax):
        print('start plot...')
        #print(data)
        #x = data['DateTime'] #зробити додатково вибір осі х у головному вікні
        #tys = []
        
        for par in ydata:
            y = ydata[par]
            ax.plot_date(x,y,label = par, fmt='-',ms=2)
            print('plot')
          

    def plots(self,x,ydata,title):
        fig, ax = plt.subplots(figsize=(12,7))
        ys1 = {}
        ys2 = {}
        ax1 = False
        for par in ydata.keys():
            if 'aaaaaaaaaFlow' in par:
                ys1[par] = ydata[par]
                
                #ax1.plot_date(x,y,label = par, fmt='-',ms=2)
                #ax1.legend(shadow=False)
                #print('plot twin: ',par)
            else:
                ys2[par] = ydata[par]
        if ys1:
            ax1 = ax.twinx()
            self.plot(x,ys1,title,ax1)
        self.plot(x,ys2,title,ax)
        self.show(ax,ax1,title,ydata)

    def show(self,ax,ax1,title,ydata):
              #ty = max(y) - min(y)
                #tys.append(ty)
        #ax1.yaxis.set_major_locator(ticker.FixedLocator([0,1,2,3,4,5]))
        #ax1.tick_params(axis='y',which='both',labelsize=12)
        #ax1.set_ylim(ymin=-1,ymax=4)
        #ax1.set_ylabel(par,fontsize=14,c='#0D1F34')
        ax.legend(shadow=False)
        #ax1.legend(shadow=False)
        ax.grid(which='major',linewidth = 0.3,linestyle = ':')
        ax.grid(which='minor',linewidth = 0.3,linestyle = ':')
        ax.set_title(title,fontsize=17)
        ax.set_ylabel('Temperature, C')
        #ax.set_xticklabels(rotation = 45,fontsize = 15)

        #tx = len(set(x))/8
        #ty = int(1+max(tys)/10            )
        #print('number of values "y": ',len(x))
        #print('ty = ',ty,'\ntx = ',tx)        
        yl = set()
        for key in ydata.keys():
            if 'Temp' in key:
                yl.add('Temperature, C    ')
            elif 'Press' in key:
                yl.add('Pressure    ')
            elif 'Flow' in key:
                yl.add('Flow, l/min    ')
        label = ' '
        for y in yl:
            label = label + y
        ax.set_ylabel(label,labelpad=22,fontsize=14,c='#0D1F34')
        ax.set_xlabel('Time',fontsize=14,c='#0D1F34')

        f = mdates.DateFormatter('%Y-%m-%d %H:%M')
        f1 = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=2))
        ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        #ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[4,8,12,16,20]))
        #ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(f)
        ax.xaxis.set_minor_formatter(f1)
        #ax.xaxis.set_major_locator(ticker.LinearLocator())
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=1))
        ax.tick_params(axis='x',which='both',labelrotation=40)
        ax.tick_params(axis='x',which='major',labelsize=12)
        ax.tick_params(axis='x',which='minor',labelsize=11)
        ax.tick_params(axis='y',which='both',labelsize=12)
        plt.xticks(horizontalalignment='right')
        #plt.yticks(fontsize=13)
        plt.tight_layout()
        plt.show()
 
root = Tk()
root.title('Log analyser')
root.geometry('1800x1000')
tab_control = ttk.Notebook(root)
frame1 = Frame(tab_control)
frame2 = Frame(tab_control)
#frame3 = Frame(tab_control)
#frame4 = Frame(tab_control)
tab_control.add(frame1,text=f"{'Chamber log files':^35s}")
tab_control.add(frame2,text=f"{'TestSystem log files':^35s}")
#tab_control.add(frame3,text=f"{'Files from Chamber':^35s}")
#tab_control.add(frame4,text=f"{'TEST':^35s}")
tab_control.pack(expand=1, fill='both')

chamber = ChamberWindow(frame1)
testsystem = TestSystemWindow(frame2)
#window3 = Window3(frame3)

root.mainloop()
