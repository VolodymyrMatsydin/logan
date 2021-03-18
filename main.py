#version 1.16

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
from analyse import *
from drawing import *
from tkcalendar import DateEntry
from datetime import datetime, time, timedelta
#import pandas as pd


SOURCES = [[1,"Climatic chamber", ChamberAnalyse],
           [2,'Test system (.cmr) new', TestSystemCmrNewAnalyse],
           [3,'Rotronic', RotronicAnalyse],
           [4,'DMM', DMMAnalyse],
           [5,'Cooling system ZUT-Michalin', CoolingSystemAnalyse],
            [6, 'Test system (.cmr) old', TestSystemCmrOldAnalyse]]
HEADINGS_1 = ['N', 'sources']
HEADWIDTH_1 = [50, 600]
PATHDELIM = '/'



class BaseWindow():
    
    def __init__(self, frame, **kw):
        self.frame = frame
        self.sources = kw #przerobic
        self.init_start_window()
        

    def init_start_window(self):
        
        #self.label_frame = LabelFrame(self.frame, labelanchor=NW, fg='blue', text='Please, select source of log files and click LOAD FILES')
        #self.label_frame.pack(padx=30, pady=50, expand=1, fill='both')
        
        #self.lb_sources = Listbox(self.label_frame, width=150, height=10, selectmode=SINGLE)
        #self.lb_sources.pack(pady=20)

        self._init_table_of_sources(self.frame)
        self.config_table(self.table_of_sources,
                          headwidth=HEADWIDTH_1,
                          columns=HEADINGS_1)

        self.var1 = IntVar()
        self.filterdata = Checkbutton(self.frame,
                                      text='filter input data',
                                      variable=self.var1)
        self.filterdata.pack(pady=30)
        #self.filterdata.bind('<Leave>',self.check)
        
        self.fill_table(self.table_of_sources, SOURCES)
        self.loadfiles_but = Button(self.frame, width=30, height=5, text='LOAD FILES', font=27, command=self.fill_window)
        self.loadfiles_but.pack(pady=30)
        
        #self.fill_listbox(self.lb_sources, SOURCES)
        



    def init_ui_1(self):

        self.par_table = ttk.Treeview(self.frame,
                                  height=26,
                                  show="headings"
                                  )
        
        scrolltabley1 = Scrollbar(self.frame, command=self.par_table.yview)
        self.par_table.configure(yscrollcommand=scrolltabley1.set)
        scrolltabley1.grid(rows=19, row=2, column=1, sticky='ns')
       
        self.par_table.grid(rows=19, row=2, column=0, sticky='e')
        self.par_table.bind('<Double-Button-1>', self.click_par_table)
        
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

        #self.lb_params = Listbox(self.frame,width=30,height=28,selectmode=EXTENDED)
        #self.lb_params.grid(padx=10,rows=19,row=2,column=0)
        #self.lb_params.bind('<Double-Button-1>',self.select_par)

        self.lb_sel_params = Listbox(self.frame,width=25,height=8)
        self.lb_sel_params.grid(padx=10,row=10,rows=6,column=2)
        self.lb_sel_params.bind('<Double-Button-1>',self.delete_sel_par)

        self.listfiles = Text(self.frame, height=4, width=120, bg='grey90')
        self.listfiles.grid(row=0, column=0, columns=9, padx=30)
        #self.listfiles.insert(END, 'Selected files:')

        self.lbl_selparams = Label(self.frame,text='Selected parameters:')
        self.lbl_selparams.grid(row=9,column=2,sticky='w')

        self.lbl_fromdate = Label(self.frame,text='Draw from date:')
        self.lbl_fromdate.grid(padx=30,row=2,column=3,sticky='w')

        self.lbl_todate = Label(self.frame,text='Draw to date:')
        self.lbl_todate.grid(padx=30,row=3,column=3,sticky='w')

        self.lbl_title = Label(self.frame,text='Chart title:')
        self.lbl_title.grid(padx=30,row=9,column=3,sticky='w')

        self.drawdots = Button(self.frame,width=27,height=3,font=23,bd=8,state=DISABLED,
                        relief='groove',text='PLOT 1',
                        command=self.click_drawdots)
        self.drawdots.grid(row=18,column=3,columns=3)

        self.drawline = Button(self.frame,width=27,height=3,font=23,bd=8,state=DISABLED,
                               relief='groove',text='PLOT 2',
                               command=self.click_drawline)
        self.drawline.grid(row=18,column=5,columns=3)

        self.cl = Button(self.frame,text='Clear selected parameters',command=self.clear_sel_par)
        self.cl.grid(pady=10,row=17,column=2)

        self.open = Button(self.frame,width=20,height=2,font=17,text='CLOSE',command=self.click_close)
        self.open.grid(pady=25, padx=30, row=0, column=11)

        

    def init_ui_2(self):
        self.open = Button(self.frame,text='Load TestSystem file(s)',font=20,height=3,command=self._get_filespaths)
        self.open.grid(pady=15,padx=55,row=0,column=0)

        self.filter = Button(self.frame,width=17,height=2,font=17,text='FILTER FAILS',state=DISABLED,command=self.filter_fail)
        self.filter.grid(pady=25,padx=10,row=3,column=2)

        #self.reportfails = Button(self.frame,width=17,height=2,font=17,text='REPORT FAILS',state=DISABLED,command=self.report_fails)
        #self.reportfails.grid(pady=25,padx=10,row=4,column=2)

        self.drawdots = Button(self.frame,width=17,height=2,font=17,text='DRAW (dots)',state=DISABLED,command=self.click_drawdots)
        self.drawdots.grid(pady=25,padx=10,row=5,column=2)

        self.drawline = Button(self.frame,width=17,height=2,font=17,text='DRAW (line)',state=DISABLED,command=self.click_drawline)
        self.drawline.grid(pady=25,padx=10,row=6,column=2)

        self.lblSelTable2 = Label(self.frame,width=175,height=3,anchor=E,wraplength=1600)
        self.lblSelTable2.grid(columns=4,row=9,column=0)
        self.lblSelTable2['text'] = "No selected"

        self.listfiles = Text(self.frame, height=5, width=120, bg='grey90')
        self.listfiles.grid(row=0, column=0, columns=10)
        self.listfiles.insert(END, 'Selected files:')

    def _init_table_of_sources(self, frame):
        
        self.table_of_sources = ttk.Treeview(frame,
                                   height=10,
                                   show="headings",
                                   selectmode="browse")
        self.table_of_sources.tag_configure('fail',foreground='red')
        self.table_of_sources.tag_configure('pass',foreground='green')
        self.table_of_sources.bind('<Double-Button-1>', self.fill_window)

        style = ttk.Style(frame)
        style.configure('Treeview', rowheight=24) 

        self.scrolltabley1 = Scrollbar(frame, command=self.table_of_sources.yview)
        self.table_of_sources.configure(yscrollcommand=self.scrolltabley1.set)
        self.scrolltabley1.pack(side=RIGHT)

        self.scrolltablex1 = Scrollbar(frame,orient=HORIZONTAL, command=self.table_of_sources.xview)
        self.table_of_sources.configure(xscrollcommand=self.scrolltablex1.set)
        self.scrolltablex1.pack(side=BOTTOM)

        self.table_of_sources.pack(side=TOP)
        #self.table_of_sources.bind('<<TreeviewSelect>>',self.select_table1)
        #headings1 = ('Nrow','Date','Time','Result')
        #headwidths1 = (50,120,90,63)

 
    def init_table2(self):

        self.table2 = ttk.Treeview(self.frame, height=28, show="headings", selectmode="extended")
        self.table2.tag_configure('fail',background='red',foreground='white')

        style = ttk.Style(self.frame)
        style.configure('ttk.Treeview', rowheight=24) 

        
        self.scrolltabley2 = Scrollbar(self.frame, command=self.table2.yview)
        self.table2.configure(yscrollcommand=self.scrolltabley2.set)
        self.scrolltabley2.grid(row=1,column=4,rows=7,sticky='ns')

        self.scrolltablex2 = Scrollbar(self.frame,orient=HORIZONTAL, command=self.table2.xview)
        self.table2.configure(xscrollcommand=self.scrolltablex2.set)
        self.scrolltablex2.grid(row=8,column=3,rows=1,sticky='we')

        self.table2.grid(row=1,rows=7,column=3,sticky='se')
        self.table2.bind('<<TreeviewSelect>>',self.select_table2)

        headings2 = ('parameters','results','Default','Min','Max')
        headwidths2 = (550,200,100,100,100)

    def config_table(self, table, **kwds):
        #table["columns"] = list(headings)
        columns = kwds.get('columns', [''])
        headwidth = kwds.get('headwidth', [290])
        selectmode=kwds.get('selectmode','browse')
        table['columns'] = columns
        table['selectmode'] = selectmode
        
        #columns = table['columns']
        
        for head, hwidth in zip(columns, headwidth):
            
            table.heading(head, text=head, anchor=CENTER)
            table.column(head, width=hwidth, minwidth=hwidth-8, anchor=W)
            
    def fill_table(self, table, data, datafilter=False):
        """"""
        tag = 'pass' #przerobic
        for values in data:
            if datafilter and datafilter in values:
                tag=datafilter
            if ' ' in values:
                table.insert('', END, values=(values,), tags=tag)
            else:
                #print(values)
                table.insert('', END, values=values, tags=tag)
        table.selection_set('I001')

    def clear_table(self,table):
        for i in table.get_children():
            table.delete(i)

    def select_table_1(self):
        select = self.table_of_sources.selection()
        data = self.table_of_sources.item(select,'values')
        return data

    def fill_lb(self,listbox,data):
        items = listbox.get(0,END)
        for i in data:
            if i not in items:
                listbox.insert(END,i)

    def click_par_table(self, event):
        select = self.par_table.selection()
        data = self.par_table.item(select,'values')
        #self.clear_table(self.par_table)
        self.fill_lb(self.lb_sel_params, data)
    
    def click_drawdots(self):
        pass

    def _click_calendar(self):
        pass

    def click_drawline(self):
        
        title = self.en_title.get()
        xind = self.analyse.get_index_of_datetime_column()
        params_to_plot = list(self.lb_sel_params.get(0, END))
        yinds = self.analyse.get_indexes_columns(params_to_plot)
        print('xind',xind,'yinds',yinds)
        chart = Draw(title=title)
        chart.plot_lines(self.analyse.df.iloc(axis=1)[xind], self.analyse.df.iloc(axis=1)[yinds])

    def clear_sel_par(self):
        self.lb_sel_params.delete(0,END)

    def filter_fail(self):
        pass

    def select_par(self):
        pass
    
    def click_close(self):
        self.destroy_children(self.frame)
        self.init_start_window()

    def delete_sel_par(self, event):
        index = self.lb_sel_params.curselection()
        self.lb_sel_params.delete(index[0])

    def fill_listbox(self, listbox, data):
        for item in data:
            listbox.insert(END,item)

    def fill_text(self, widget, data):
        widget['state'] = NORMAL
        widget.delete(1.0, END)
        for i in data:
            widget.insert(END,i+'\n')
        widget['state'] = DISABLED

    def get_filespaths(self):
        try:
            filespaths = list(filedialog.askopenfilenames())
            if filespaths[0]:
                worklog.simple_log('-'*70)
                worklog.log_with_timestamp('')
                for i, path in enumerate(filespaths):
                    worklog.simple_log(f'INPUT FILE N{i+1}: {path.split(PATHDELIM)[-1]}')
        except IndexError:
            messagebox.showinfo('Caution','No new selected files')
        else:
            return filespaths
        
    def destroy_children(self, widget):
        for children in widget.winfo_children():
            children.destroy()

    def choice_of_instance(self, selected):
        types = SOURCES
        for i in types:
            if selected == i[0]:
                
                return i[2]
        
    def fill_window(self, event=None):
        selected = int(self.select_table_1()[0])
        filespaths = self.get_filespaths()
        if filespaths:
            self.destroy_children(self.frame)
            self.init_ui_1()
            classcall = self.choice_of_instance(selected)
            #print(classcall)
            self.analyse = classcall(filespaths)
            #self.df = analyse.create_df()
            #print(self.df.head(), self.df.describe())
            filesnames = [path.split(PATHDELIM)[-1] for path in filespaths]
            self.fill_text(self.listfiles, filesnames)
            self.config_table(self.par_table, selectmode='extended')
            #parameters = [(i, v) for i,v in enumerate(df.keys())]
            self.fill_table(self.par_table, self.analyse.df.keys())
            self.drawdots.config(state=NORMAL)
            self.drawline.config(state=NORMAL)
            #print(df['A:Temperature '])

    def click_plot(self):
        chart = Draw(worklog)
        
"""
class Window():
    
    def __init__(self,frame):
        self.frame = frame
        self.initUI()
        
    def initUI(self):
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
        self.lb_params.grid(padx=10,rows=19,row=2,column=0)
        self.lb_params.bind('<Double-Button-1>',self.select_par)

        self.lb_sel_params = Listbox(self.frame,width=25,height=8)
        self.lb_sel_params.grid(padx=10,row=10,rows=6,column=1)
        self.lb_sel_params.bind('<Double-Button-1>',self.delete_sel_par)

        self.listfiles = Text(self.frame,height=3,width=110,bg='grey90')
        self.listfiles.grid(row=0,column=1,columns=7)
        self.listfiles.insert(END, 'Selected file(s):')

        self.lbl_selparams = Label(self.frame,text='Selected parameters:')
        self.lbl_selparams.grid(row=9,column=1,sticky='w')

        self.lbl_fromdate = Label(self.frame,text='Draw from date:')
        self.lbl_fromdate.grid(padx=30,row=2,column=3,sticky='w')

        self.lbl_todate = Label(self.frame,text='Draw to date:')
        self.lbl_todate.grid(padx=30,row=3,column=3,sticky='w')

        self.lbl_title = Label(self.frame,text='Chart title:')
        self.lbl_title.grid(padx=30,row=9,column=3,sticky='w')

        self.drawdots = Button(self.frame,width=27,height=3,font=23,bd=8,state=DISABLED,
                        relief='groove',text='DRAW (dots)',
                        command=self.click_drawdots)
        self.drawdots.grid(row=18,column=3,columns=3)

        self.drawline = Button(self.frame,width=27,height=3,font=23,bd=8,state=DISABLED,
                               relief='groove',text='DRAW (line)',
                               command=self.click_drawline)
        self.drawline.grid(row=18,column=5,columns=3)

        self.cl = Button(self.frame,text='Clear selected parameters',command=self.clear_sel_par)
        self.cl.grid(pady=10,row=17,column=1)

        self.open = Button(self.frame,width=20,height=2,font=17,text='LOAD FILES',command=self._get_filespaths)
        self.open.grid(pady=25,padx=10,row=0,column=0)

        self.var1 = IntVar()
        self.filterdata = Checkbutton(self.frame, text='filter input data', variable=self.var1)
        self.filterdata.grid(row=1, column=0)
        #self.filterdata.bind('<Leave>',self.check)
        

    def check(self, event):
        print('func',self.var1.get())

    def _get_filespaths(self):
        
        try:
            filespaths = list(filedialog.askopenfilenames())
            if filespaths[0]:
                pathdelim = '/'
                worklog.simple_log('-'*70)
                worklog.log_with_timestamp('')
                for i,path in enumerate(filespaths):
                    worklog.simple_log(f'INPUT FILE N{i+1}: {path.split(pathdelim)[-1]}')
        except IndexError:
            messagebox.showinfo('Caution','No new selected files')
        else:
            self._fill_window(filespaths)

    def _fill_window(self,filesPaths):
        
        # create instance of Analyse class for analyse logs from chamber
        self.ca = Analyse(filesPaths, worklog, filterinputdata=self.var1.get()) 
        
        self._clear_widgets()
        self.fill_text(self.listfiles,self.ca.validfiles)
        self.fill_lb(self.lb_params,self.ca.header)

        self._set_date_limits_of_files(self.ca.minDate, self.ca.maxDate)
        self._set_time_limits_of_files(self.ca.minDate, self.ca.maxDate)
        self.drawdots.config(state=NORMAL)
        self.drawline.config(state=NORMAL)

    def _clear_widgets(self):
        self.lb_sel_params.delete(0,END)
        self.lb_params.delete(0,END)

    def fill_text(self,widget,data):
        widget.delete(1.0, END)
        for i in data:
            widget.insert(END,i+'\n')        
   
    def _fromto_selected_date(self):
        fromdate = self.entry_cal.get_date()
        todate = self.entry_cal2.get_date()
        #if fromdate > todate: #переробити
            #messagebox.showinfo('Caution',"Date 'from' must be lowed than date 'to'")
        return fromdate, todate

    def _fromto_selected_time(self):
        fromtime = time(hour=int(self.cmbbx11.get()), minute=int(self.cmbbx12.get()))
        totime = time(hour=int(self.cmbbx21.get()), minute=int(self.cmbbx22.get()))
        return fromtime,totime

    def _set_date_limits_of_files(self, mindate, maxdate):
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

    def _click_calendar(self, event):
        fromdate, todate = self._fromto_selected_date()
        mintime = time(hour=0, minute=0)
        if fromdate == self.ca.minDate.date():
            mintime = self.ca.minDate
        maxtime = time(hour=23,minute=59)  
        if todate == self.ca.maxDate.date():
            maxtime = self.ca.maxDate
        self._set_time_limits_of_files(mintime, maxtime)      
  
    def fill_lb(self,listbox,data):
        for i in data:
            listbox.insert(END,i)
        
    def select_par(self,event):
        select = self.lb_params.curselection()
        inserted = self.lb_sel_params.get(0,END)
        for i in select:
            if not self.ca.header[i] in inserted:
                self.lb_sel_params.insert(END,self.ca.header[i])

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
        
    def get_draw_data(self):
        
        fromtime,totime = self._fromto_selected_time()
        fromdate,todate = self._fromto_selected_date()
        
        drawfrom = datetime.combine(fromdate, fromtime)
        drawto = datetime.combine(todate, totime)
        worklog.simple_log(f'plot from {drawfrom}\nplot to {drawto}')

        plotDataIndexes = []
        for limit in [drawfrom,drawto]:
            rowIndex = self.ca.find_index_dateitem(limit)
            plotDataIndexes.append(rowIndex)
        worklog.simple_log(f'MIN SELECTED ROW INDEX: {plotDataIndexes[0]}  MAX SELECTED ROW INDEX: {plotDataIndexes[1]}')
        selpar = {}
        selectedParamsList = list(self.lb_sel_params.get(0,END)) 
        for sel in selectedParamsList:
            selIndex = self.ca.header.index(sel)
            selpar[sel] = selIndex
        selpar['DateTime'] = 0
        #print('selpar: ',selpar)
        title = 'Sample plot'
        drawData = self.ca.rows_to_columns(self.ca.data,selpar,plotDataIndexes)
        return drawData, title
        
    def click_drawdots(self):
        chart = Draw(worklog)
        drawData, title = self.get_draw_data()
        if len(drawData) > 1:
            chart.plotdots(drawData,title)
    
    def click_drawline(self):
        chart = Draw(worklog)
        drawData, title = self.get_draw_data()
        if len(drawData) > 1:
            chart.plotline(drawData,title)
        
class ChamberWindow(Window):
    pass

class TestSystemWindow(Window,Analyse):

    def __init__(self,frame):
        Window.__init__(self,frame)
        
        
    def initUI(self):
#        self.ts.filespaths = []
        #self.clearfails = Button(self.frame,width=17,height=2,font=17,text='PRINT DATA',command=self.print_data)
        #self.clearfails.grid(pady=25,padx=10,row=5,column=2)

        self.open = Button(self.frame,text='Load TestSystem file(s)',font=20,height=3,command=self._get_filespaths)
        self.open.grid(pady=15,padx=55,row=0,column=0)

        self.filter = Button(self.frame,width=17,height=2,font=17,text='FILTER FAILS',state=DISABLED,command=self.filter_fail)
        self.filter.grid(pady=25,padx=10,row=3,column=2)

        self.reportfails = Button(self.frame,width=17,height=2,font=17,text='REPORT FAILS',state=DISABLED,command=self.report_fails)
        self.reportfails.grid(pady=25,padx=10,row=4,column=2)

        self.drawdots = Button(self.frame,width=17,height=2,font=17,text='DRAW (dots)',state=DISABLED,command=self.click_drawdots)
        self.drawdots.grid(pady=25,padx=10,row=5,column=2)

        self.drawline = Button(self.frame,width=17,height=2,font=17,text='DRAW (line)',state=DISABLED,command=self.click_drawline)
        self.drawline.grid(pady=25,padx=10,row=6,column=2)

        self.lblSelTable2 = Label(self.frame,width=175,height=3,anchor=E,wraplength=1600)
        self.lblSelTable2.grid(columns=4,row=9,column=0)
        self.lblSelTable2['text'] = "No selected"

        self.listfiles = Text(self.frame,height=3,width=110,bg='grey90')
        self.listfiles.grid(row=0,column=2,columns=2)
        self.listfiles.insert(END, 'Selected file(s):')
        self.init_table_of_sources()
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

        self.table2 = ttk.Treeview(self.frame, height=28, show="headings", selectmode="extended")
        self.table2.tag_configure('fail',background='red',foreground='white')

        style = ttk.Style(self.frame)
        style.configure('ttk.Treeview', rowheight=24) 

        
        self.scrolltabley2 = Scrollbar(self.frame, command=self.table2.yview)
        self.table2.configure(yscrollcommand=self.scrolltabley2.set)
        self.scrolltabley2.grid(row=1,column=4,rows=7,sticky='ns')

        self.scrolltablex2 = Scrollbar(self.frame,orient=HORIZONTAL, command=self.table2.xview)
        self.table2.configure(xscrollcommand=self.scrolltablex2.set)
        self.scrolltablex2.grid(row=8,column=3,rows=1,sticky='we')

        self.table2.grid(row=1,rows=7,column=3,sticky='se')
        self.table2.bind('<<TreeviewSelect>>',self.select_table2)

        headings2 = ('parameters','results','Default','Min','Max')
        headwidths2 = (550,200,100,100,100)
        self.config_table(self.table2,headings2,headwidths2)

    def config_table(self,table,headings,headwidths):
        table["columns"] = headings
        for head,hwidth in zip(headings,headwidths):
            table.heading(head, text=head, anchor=CENTER)
            table.column(head,width=hwidth,minwidth=hwidth-8, anchor=W)
    
    def clear_table(self,table):
        for i in table.get_children():
            table.delete(i)
            
    def get_item_table(self,table):
        select = table.selection()
        return select, table.item(select,'values')
        
    def filter_fail(self):
        
        keyword = 'Failed'
        if not self.ts.datafilter:
            
            self.ts.datafilter = True
            self.filter.config(text='VIEW ALL DATA')
            #item = 'I001'
            #value=0
        else:
            self.ts.datafilter = False
            self.filter.config(text='FILTER FAILS')
            #selection = self.get_item_table(self.table1)
            #item = selection[0]
            #value = selection[1][0]
            #print(item,value)
        self.clear_table(self.table1)
        self.tempdata = self.ts.get_column(self.ts.filespaths,
                                           self.ts.datetimecolumnconfig[0],
                                           self.ts.firstDataIndex,
                                           self.ts.subcolumnconfig,
                                           datafilter=self.ts.datafilter,
                                           wordfilter=self.ts.keyword)
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
        for i in self.ts.fails:
            print(i)
        self.ts.fails = []
    
    def select_table1(self,event):
        select = self.table1.selection()
        data = self.table1.item(select,'values')
        self.clear_table(self.table2)
        self.fill_table2(keyrow=int(data[0]))


    def select_table2(self,event):
        select = self.table2.selection()
        if len(select) == 1:
            data = self.table2.item(select,'values')
            self.lblSelTable2['text'] = '      '.join(data)

    def fill_table1(self,data):
        """"""
        for k,v in data.items():
            if self.ts.keyword in v:
                tag='fail'
            else:
                tag='pass'
            if len(v) == 3:
                self.table1.insert('',END,values=(k,v[0],v[1],v[2]),tags=tag)
            elif len(v) == 1:
                self.table1.insert('',END,values=(k,'',v[0]),tags=tag)

    def fill_table2(self,keyrow=4):
        values = self.ts.data[keyrow]
        addData = self.ts.additionalData
        for ai,bi,ci,di,ei in zip(addData[0],addData[1],addData[2],addData[3],values):    
            if ei == 'NA':
                continue
            if (isinstance(ei,int) or isinstance(ei,float)) and not isinstance(bi,str) and not isinstance(ci,str):
                if ei < bi or ei > ci:
                   self.table2.insert('',END,values=(ai,ei,di,bi,ci),tags='fail')
                   continue
            if not self.ts.datafilter:
                self.table2.insert('',END,values=(ai,ei,di,bi,ci))
                
   
    def _fill_window(self,filesPaths):
        self.ts =  TestSystemAnalyse(filesPaths,worklog)
        fileNames = []
        for path in filesPaths:
            fileNames.append(path.split('/')[-1])
        self.fill_text(self.listfiles,fileNames)
        self.clear_table(self.table1)
        
        tableData = self.ts.get_column(self.ts.filespaths,
                                       self.ts.datetimecolumnconfig[0],
                                       self.ts.firstDataIndex,
                                       self.ts.subcolumnconfig)
        self.fill_table1(tableData)
        self.filter.config(text='FILTER FAIL',state=NORMAL)
        self.reportfails.config(state=NORMAL)
        self.drawdots.config(state=NORMAL)
        self.drawline.config(state=NORMAL)

        self.fill_table2()

    def get_draw_data(self):
        selpar = {}
        select = self.table2.selection()
        #print('select',select)
        for i in select:
            parameter = self.table2.item(i,'values')[0]
            dataColumnIndex = self.ts.header.index(parameter)-1
            selpar[parameter] = dataColumnIndex
        selpar['DateTime'] = 0
        drawData = self.ts.rows_to_columns(self.ts.data,selpar)
##        for i in [select,parameter,dataColumnIndex,drawData]:
##            print('\n',i)
        #print(drawData)
        title = parameter
        return drawData, title
    
    def click_drawdots(self):
        chart = Draw(worklog)
        drawData, title = self.get_draw_data()
        chart.plotdots(drawData,title)

    def click_drawline(self):
        chart = Draw(worklog)
        drawData, title = self.get_draw_data()
        #chart.plotline(drawData,title)
        chart.subplots(drawData,title)
"""
class WorkLog():
    
    def __init__(self,frame):
        self.frame = frame
        self.text = scrolledtext.ScrolledText(self.frame,height=40,width=130,bg='white')
        self.text.grid(row=0,column=0,padx=20)
        self.text.tag_config("error", foreground="red")
        self.text.tag_config("timestamp", foreground="green")

    def simple_log(self,data):
        self.text.insert(END,data+'\n')
        self.text.see(END)

    def log_error(self,data):
        self.text.insert(END,data+'\n',"error")
        self.text.see(END)
    
    def log_with_timestamp(self,data):
        timestamp = datetime.now()
        time = datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S')
        self.text.insert(END,time,"timestamp")
        self.text.insert(END,'   ')
        self.text.insert(END,data+'\n')
        self.text.see(END)
            


root = Tk()
root.title('Log analyser')
root.geometry('1800x1000')
tab_control = ttk.Notebook(root)
#frame_0 = Frame(tab_control)
frame_0 = LabelFrame(tab_control, labelanchor=NW, fg='blue', text='Please, select source of log files and click LOAD FILES')

#frame1 = Frame(tab_control)
#frame2 = Frame(tab_control)
frame_3 = Frame(tab_control)
tab_control.add(frame_0,text=f"{'Main':^35s}")
#tab_control.add(frame1,text=f"{'Chamber log files':^35s}")
#tab_control.add(frame2,text=f"{'TestSystem log files':^35s}")
tab_control.add(frame_3,text=f"{'Work log':^30s}")
tab_control.pack(expand=1, fill='both')


kw = dict(sources=SOURCES)
mainwindow = BaseWindow(frame_0, **kw)
#chamber = ChamberWindow(frame1)

#testsystem = TestSystemWindow(frame2)
worklog = WorkLog(frame_3)




root.mainloop()

if __name__ == "main":
    pass


#to do:
#regognition_items, datetimePattern,coldate = (0,1),
#load_data(replace)
#select date
#get_datetime_pattern - subcolumnDateIndexes
#find_index_column w cykle
