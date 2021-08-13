# version 1.17
# python 3.9

from tkinter import Tk, Listbox, Label, Button, LabelFrame, Scrollbar, Entry, NW, CENTER, W, END, NORMAL, DISABLED, N, S
from tkinter import filedialog, messagebox, scrolledtext, ttk
from analyse import *
from drawing import Draw
from typing import Any, Iterable


class BaseWindow:
    """Builds window interface for 'Log wiever' application.
    Conclude two frames - application and frame for log information.
    First frame build list of sources of log files. After selected files,
    there is possibility to select some columns to draw."""

    def __init__(self, root_instance: Tk) -> None:
        """Receives window instance and then run build start window for select files."""
        self.root = root_instance
        self._build_tabs(self.root)
        self._init_start_ui(self.main_tab)

    def _build_tabs(self, root: Tk) -> None:
        """Builds two tabs - main and log."""
        tab_control = ttk.Notebook(root)
        self.main_tab = LabelFrame(tab_control, labelanchor=NW, fg='black', text='---')
        self.log_tab = LabelFrame(tab_control, labelanchor=NW, fg='black', text='LOG')
        
        tab_control.add(self.main_tab, text=f"{'Main':^30s}")
        tab_control.add(self.log_tab,text=f"{'Work log':^30s}")
        tab_control.pack(expand=1, fill='both')

    def _init_start_ui(self, frame: LabelFrame) -> None:
        """Initializes dict for paths of selected files, separated by sources.
        Builds start window (table of sources, buttons, text widget)."""
        self.filespaths = {}
        self.destroy_children(frame)
        self._init_table_of_sources(frame)

        self.addfiles_but = Button(frame, width=30, height=3,
                                    text='ADD FILES', font=27,
                                    command=lambda: self._add_filespaths(self.table_of_sources.selection()[0]))
        self.addfiles_but.grid(row=1, column=5, pady=10)

        self.files_list = scrolledtext.ScrolledText(frame, height=8, width=100, bg='grey90')
        self.files_list.grid(row=2, column=0, columns=10, padx=10, pady=20)
        self.files_list.insert(END, 'Selected files:\n')

        self.go_but = Button(frame,
                             width=30,
                             height=5,
                             text='GO',
                             font=33,
                             command=lambda: app.init_main_ui()
                             )
        self.go_but.grid(row=3, column=7, columns=2, sticky='e')
        self.fill_table(self.table_of_sources, DATA_SOURCES)

    def reinit_start_ui(self) -> None:
        """Destroy current window and reinitialize start window."""
        self.destroy_children(self.main_tab)
        self._init_start_ui(self.main_tab)

    def init_main_ui(self, frame: LabelFrame) -> None:
        """Create the next window interface."""
        self.par_tables = []
        self.destroy_children(frame)
        self._init_parameter_tables(frame)
        self._set_click_table_function()

        self.en_title = Entry(frame,width=35)
        self.en_title.grid(padx=30,row=10,columns=2, column=3)

        self.lb_sel_params = Listbox(frame, width=25, height=15)
        self.lb_sel_params.grid(padx=10, row=2, column=3)
        self.lb_sel_params.bind('<Double-Button-1>', app.click_sel_params)

        self.lbl_selparams = Label(frame, text='Selected parameters:')
        self.lbl_selparams.grid(row=1, column=3, padx=15, sticky='w')

        self.lbl_title = Label(frame,text='Chart title:')
        self.lbl_title.grid(padx=30,row=9, column=3, sticky='w')

        self.drawtable = Button(frame, width=27, height=3, font=23, bd=8, state=DISABLED,
                                relief='groove', text='DRAW TABLE',
                                command=app.click_drawtable)
        self.drawtable.grid(row=18,column=3,columns=2)

        self.drawline = Button(frame, width=27, height=3, font=23, bd=8,
                               relief='groove', text='DRAW LINES',
                               command=app.click_drawlines)
        self.drawline.grid(row=18,column=5,columns=3)

        self.cl = Button(frame, text='Clear selected parameters', command=app.click_clear_sel_params)
        self.cl.grid(pady=10, row=3, column=3)

        self.close_but = Button(frame,width=20,height=2,font=17,text='CLOSE', command=app.click_close)
        self.close_but.grid(pady=25, padx=30, row=0, columns=2, column=10)

    def _init_table_of_sources(self, frame: LabelFrame) -> None:
        """Initialize table of sources and configure it."""
        self.table_of_sources = ttk.Treeview(frame,
                                             height=12,
                                             show="headings"
                                             )
        style = ttk.Style(frame)
        style.configure('Treeview', rowheight=30, font=('Arial',16))
        self.table_of_sources.tag_configure('default', foreground='black')
        self.table_of_sources.tag_configure('pass', foreground='green')
        self.table_of_sources.grid(row=0, column=5, sticky='e')
        self.table_of_sources.bind('<Double-Button-1>',
                                   lambda coords: self._add_filespaths(self.table_of_sources.identify_row(coords.y)))

        scroll_y = Scrollbar(frame, command=self.table_of_sources.yview)
        self.table_of_sources.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=6, sticky='nsw')

        self.config_table(self.table_of_sources, selectmode='browse', height=10)

    # def _init_tables(self, frame):
    #     number_tables = len(self.filespaths)
    #     print('number_tables:', number_tables)
    #     if number_tables == 1:
    #         self._init_par_table(frame)
    #     elif number_tables == 2:
    #         self._init_two_par_tables(frame)
    #     elif number_tables == 3:
    #         self._init_three_par_tables(frame)
    #     self._set_click_table_function()

    def _init_parameter_tables(self, frame: LabelFrame) -> None:
        """Builds one, two or three tables with list of parameters (columns)."""
        self.par_tables = []
        count_tables = len(self.filespaths)
        row = 1
        rows = 18
        height = int(24/count_tables)
        for i in range(1, count_tables+1):
            table = ttk.Treeview(frame)
            self._init_table_scrollbar(frame, table, row)
            table.grid(rows=int(rows/count_tables), row=row, column=0, padx=15, pady=10)
            self.config_table(table, height=height)
            row = int(row + rows/count_tables)
            self.par_tables.append(table)
        #print(self.par_tables)

    def _init_table_scrollbar(self, frame: LabelFrame, table: ttk.Treeview, row: int) -> None:
        """Builds y scrollbars for the parameters tables"""
        scrolltabley = Scrollbar(frame, command=table.yview)
        table.configure(yscrollcommand=scrolltabley.set)
        scrolltabley.grid(row=row, column=2, rowspan=8, sticky=N+S)

    def _set_click_table_function(self) -> None:
        """Sets binding method to all tables with parameters (columns)."""
        if self.par_tables:
            for table in self.par_tables:
                table.bind('<Double-Button-1>', app.click_par_table)

    def config_table(self, table: ttk.Treeview, **kwds) -> None:
        """Method for a table configuration."""
        height = kwds.get('height', 24)
        columns = kwds.get('columns', [''])
        show = kwds.get('show', 'headings')
        headwidths = kwds.get('headwidths', [490])
        selectmode=kwds.get('selectmode','extended')
        table.config(selectmode=selectmode, columns=columns, height=height, show=show)
        for heading, headwidth in zip(columns, headwidths):
            table.heading(heading, text=heading, anchor=CENTER)
            table.column(heading, width=headwidth, minwidth=headwidth-8, anchor=W)

    def fill_table(self, table: ttk.Treeview, data: dict, **kwds) -> None:
        """Fills the table with data."""
        assert len(data) > 0, 'wrong data passes to the table'
        tag = kwds.get('tag', 'default')
        for values in data:
            table.insert('', END, values=(values,), tags=tag)

    def _get_tablevalue_under_cursor(self, item: str) -> str:
        """Gets string value under the focused row the table of sources."""
        value = self.table_of_sources.item(item, 'values')[0]
        return value
  
    def _add_filespaths(self, item: str) -> None:
        """Handles click on 'Add files' button or doubleclick on row of the table of sources."""
        value = self._get_tablevalue_under_cursor(item)
        try:
            filespaths = list(filedialog.askopenfilenames())
            if filespaths[0]:
                if self.filespaths.get(value, 0):
                    [self.filespaths[value].add(path) for path in filespaths]
                else:
                    self.filespaths[value] = set(filespaths)
        except IndexError:
            messagebox.showinfo('Caution','No selected files')
        else:
            self.fill_text(self.files_list, (value + ' files',))
            for path in filespaths:
                self.fill_text(self.files_list, ('\t'+path.split('/')[-1],))

    def fill_text(self, widget: Any, data: Iterable[str]) -> None:
        """Fills text widget with the iterated data."""
        widget['state'] = NORMAL
        #widget.delete(1.0, END)
        for i in data:
            widget.insert(END, i+'\n')
        widget['state'] = DISABLED

    def fill_lb(self, listbox: Listbox, data: Iterable[str]) -> None:
        """Fills listbox with the iterated data."""
        items = listbox.get(0, END)
        for i in data:
            if i not in items:
                listbox.insert(END, i)

    def get_title(self) -> str:
        """Gets string title from entry widget."""
        return self.en_title.get()

    def destroy_children(self, widget) -> None:
        """Destroys child elements the widget."""
        for children in widget.winfo_children():
            children.destroy()

    def clear_sel_par(self) -> None:
        """Method clear listbox with selected parameters."""
        self.lb_sel_params.delete(0, END)

    def fill_listbox_sel_params(self, sel_par: str) -> None:
        """Puts selected parameter to the listbox of selected parameters."""
        self.fill_lb(self.lb_sel_params, (sel_par,))

    def remove_selected_element(self) -> str:
        """Remove selected parameter from listbox of selected parameters."""
        index_to_delete = self.lb_sel_params.curselection()[0]
        value_to_delete = self.lb_sel_params.get(index_to_delete)
        self.lb_sel_params.delete(index_to_delete)
        return value_to_delete


class App:
    """Class for manage the application."""
    def __init__(self, root_instance) -> None:
        """Delegates initialisation of the start window."""
        self.w = BaseWindow(root_instance)

    def init_main_ui(self) -> None:
        """Delegates initialisation of the next window. Also runs parsing selected files."""
        self.w.init_main_ui(self.w.main_tab)
        self._get_data_from_files()
    
    def _get_data_from_files(self) -> None:
        """Initialise application attribute for analyse instances and fill it.
        Fill parameters tables."""
        self.analyse_instances = []
        for tablename, table in zip(self.w.filespaths, self.w.par_tables):
            analyse_instance = DATA_SOURCES[tablename](list(self.w.filespaths[tablename]))
            self.analyse_instances.append(analyse_instance)
            #print('analyses:', self.w.filespaths[tablename], analyse_instance.df)
            self.w.fill_table(table, analyse_instance.df)
        
    def click_sel_params(self, event: Any) -> None:
        """After double click on element of listbox "selected parameters",
        it delegates window instance to delete selected parameter.
        Also delete element of list of analyse instance attribute."""
        deleted_value = self.w.remove_selected_element()
        for inst in self.analyse_instances:
            if deleted_value in inst.sel_params:
                inst.sel_params.remove(deleted_value)

    def click_clear_sel_params(self) -> None:
        """Delegate to clear selected parameters in both instance's attribute and listbox."""
        self.clear_sel_params()
        self.w.clear_sel_par()

    def clear_sel_params(self) -> None:
        """Clear selected parameters for all analyse instances."""
        for inst in self.analyse_instances:
            inst.sel_params.clear()

    def click_close(self) -> None:
        """Clear list of analyse instances. Delegate to the interface instance to destroy the window widgets."""
        self.analyse_instances.clear()
        self.w.reinit_start_ui()

    def click_par_table(self, event: Any) -> None:
        """Add selected parameter to the list of selected parameters.
        Delegate to the window instance to fill with selected parameters."""
        for table, analyse_instance in zip(self.w.par_tables, self.analyse_instances):
            if table.state():
                select = table.selection()[0]
                selected_parameter = table.item(select, 'values')[0]
                analyse_instance.sel_params.add(selected_parameter)
                self.w.fill_listbox_sel_params(selected_parameter)
                # print('sel params:', analyse_instance.__class__, analyse_instance.sel_params)
                break

    def get_drawdata(self) -> list[tuple]:
        """Takes data for selected parameters."""
        drawdata = []
        for analyse_instance in self.analyse_instances:
            dt_index = analyse_instance.get_index_of_datetime_column()
            drawdata.append((analyse_instance.df.iloc(axis=1)[dt_index], analyse_instance.df[analyse_instance.sel_params]))
        return drawdata

    def click_drawlines(self) -> None:
        """Handles the button click."""
        title = self.w.get_title()
        chart = Draw(title=title)
        drawdata = self.get_drawdata()
        chart.draw_lines(drawdata)

    def click_drawtable(self) -> None:
        """Handles the button click."""
        title = self.w.get_title()
        chart = Draw(title=title)
        drawdata = self.get_drawdata()
        chart.draw_table(drawdata)


root = Tk()
root.geometry('1700x1100')
app = App(root)
root.mainloop()