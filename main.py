from window_interface import ChamberWindow, TestSystemWindow
from analyse import Analyse,  TestSystemAnalyse


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

