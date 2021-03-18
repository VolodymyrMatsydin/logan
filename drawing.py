#version 1.16

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from datetime import datetime

class Draw():
    def __init__(self, **kw):
        #self.log_instance = log_instance
        self.fig, self.axes = plt.subplots(figsize=(12,7))
        self.title = kw.get('title', 'Sample_chart')
    
##    def plot_dots(self, data):
##        """11032021.draw one or many time plots as dots. As input: {'name_par: data_par}"""
##        plot_data = data
##        fig, ax = plt.subplots(figsize=(12,7))
##        for par, par_data in plot_data.items():
##            if par == 'timestamp':
##                continue
##            ax.plot_date(plot_data['timestamp'], par_data, label = par, ms=6)
##        self._show_drawing(ax)
##
##    def plot_lines(self, data):
##        """10032021.draw one or many time lines. As input: {'name_par: data_par}"""
##        plot_data = data
##        fig, ax = plt.subplots(figsize=(12,7))
##        for par, par_data in plot_data.items():
##            if par == 'timestamp':
##                continue
##            ax.plot(plot_data['timestamp'], par_data, label=par)
##        self._show_drawing(ax)


    def plot_dots(self, xdata, ysdata):
        """plot as dots"""
        self._plot(xdata, ysdata, self.axes.plot_date)

    def plot_lines(self,  xdata, ysdata):
        """plot as lines"""
        self._plot(xdata, ysdata, self.axes.plot)

    def _plot(self,  xdata, ysdata, method):
        """12032021.draw one or many time lines. As input: {'name_par: data_par},
            method is method to plot"""
        x = xdata
        ys = ysdata
        #x = self.get_xdata(plot_data)
        for par, par_data in ys.items():
            method(x, par_data, label=par)
        self._create_column_of_ylabels(ysdata)
        self._show_drawing()

    def _create_column_of_ylabels(self, labels):
        """create column of labels from list of labels"""
        self.ylabels = ''
        for i in labels:
            self.ylabels = self.ylabels + i + '\n'

##    to delete
##    def get_xdata(self, plot_data):
##        """takes out datetime values from plot_data"""
##        for par in plot_data:
##            if isinstance(plot_data[par][0], datetime):
##                return plot_data.pop(par)
##        raise ValueError('plot_data must include datetime values')

    def subplots(self,data,title):
        x = data['DateTime']
        
        n = i = len(data)-1
        if n > 9:
            i = n = 9
        for k,v in data.items():
            if k == 'DateTime':
                continue
            positionAxes = int(str(n)+f'1{i}')
            if i == 0:
                break
            elif i == len(data)-1 or 9:
                ax1 = plt.subplot(positionAxes)
                ax1.set_ylabel(k)
            else:
                ax = plt.subplot(positionAxes,sharex=ax1)
                ax.set_ylabel(k)
            plt.plot(x,v,label=k)
            i -= 1
            
        plt.show()
        
            

    def plots(self,data,title):
        plotData = data
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
        self._show_drawing(ax,ax1,title,ydata)

    def _show_drawing(self, ax1=None, ydata=None):
        ax = self.axes
        #ax1.yaxis.set_major_locator(ticker.FixedLocator([0,1,2,3,4,5]))
        #ax1.tick_params(axis='y',which='both',labelsize=12)
        #ax1.set_ylim(ymin=-1,ymax=4)
        #ax1.set_ylabel(par,fontsize=14,c='#0D1F34')
        ax.legend(shadow=False)
        #ax1.legend(shadow=False)
        ax.grid(which='major',linewidth = 0.3,linestyle = ':')
        ax.grid(which='minor',linewidth = 0.3,linestyle = ':')
        ax.set_title(self.title,fontsize=17)
        #ax.yaxis.set_wrap(True)
        ax.set_ylabel(self.ylabels, fontsize=14, c='#0D1F34')
        #ax.set_xticklabels(rotation = 45,fontsize = 15)

        #ax.set_ylabel(label,labelpad=22,fontsize=14,c='#0D1F34')
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
        #ax.yaxis.set_major_locator(ticker.AutoLocator())
        ax.tick_params(axis='x',which='both',labelrotation=40)
        ax.tick_params(axis='x',which='major',labelsize=12)
        ax.tick_params(axis='x',which='minor',labelsize=11)
        ax.tick_params(axis='y',which='both',labelsize=12)
        plt.xticks(horizontalalignment='right')
        #plt.yticks(fontsize=13)
        plt.tight_layout()
        plt.show()


    
    
if __name__ == '__main__':
    
    draw = Draw(title='E-19 test')
    data = {
            'timestamp': [datetime(2021, 3, 11, 9, 34, 39, 84252),
                          datetime(2021, 3, 11, 11, 34, 39, 84252),
                          datetime(2021, 3, 11, 15, 38, 39, 84252),
                          datetime(2021, 3, 11, 19, 49, 39, 84252)],
            'Current': [1, 2, 8, 30],
            'Temperature': [23, -40, -40, 85],
            'Humidity': [10, 20, 22, 45]
            }
    x = data.pop('timestamp')
    #print(x, data)
    draw.plot_lines(x, data)
    
    
