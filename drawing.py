# version 1.17
# python 3.9

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from typing import Dict, List, Any


class Draw:
    """Class for drawing time lines using pyplot methods plot and scatter."""

    def __init__(self, **kw: Any) -> None:
        self.title = kw.get('title', 'Sample_chart')

    # def draw_scatter(self, drawdata: list[tuple]) -> None:
    #     self.columns_by_types = self._separate_y_columns_by_types(drawdata)
    #
    # def draw_dots(self, xdata, ysdata):  # przerobić
    #     """plot as dots"""
    #     assert len(ysdata) >= 1, 'not enough parameters to plot'
    #     self._plot(xdata, ysdata, self.axes.plot_date)

    def draw_lines(self, drawdata: List[tuple]) -> None:
        """Draw as lines on one or two axes."""
        for xdata, ysdata in drawdata:
            assert len(ysdata) >= 1, 'not enough parameters to plot'
        self.columns_by_types = self._separate_y_columns_by_types(drawdata)
        if len(self.columns_by_types) == 1:
            self._draw(drawdata)
        else:
            self._draw_sharex(drawdata)

    # to do
    def draw_table(self, drawdata: List[tuple]) -> None:

        #rows = xydata[0][0]
        #ydata = xydata[0][1]
        #data = ydata.to_numpy()
        #columns = ydata.keys()
        #self.columns_by_types = self._separate_y_columns_by_types(drawdata)
        for (x, ysdata) in drawdata:
            index = np.arange(len(ysdata.keys()))
            print('index:', index)
            print('ys:', ysdata.keys())
            for ount in range(len(ysdata)):
                print('row:', ysdata.iloc(axis=0)[ount])
                #for x, y, label in self._yield_columns_data(drawdata):
            #print('x', x)
            #print('y', y)
                plt.bar(index, ysdata.iloc(axis=0)[ount])
            #plt.scatter(x, y, c='r', s=75, label=label)
            #plt.table([[1, 2]], loc='bottom', rowLabels=['a'])
        #y_offset = np.zeros(len(columns))
        # print('index:', index, 'rows:', rows,'columns:',columns)
        #cell_text = []
        # for col in columns:
            # plt.bar(index, data[row], 1)#, bottom=y_offset)#, color=colors[row])
            # y_offset = y_offset + data[row]
        # cell_text.append(['%1.1f' % x for x in data[row]])
        # print(cell_text)
        plt.legend()
        plt.show()

    def _separate_y_columns_by_types(self, drawdata: List[tuple]) -> Dict[int, List]:
        """Separates selected columns to draw by types their data.
        Returns dict like {int_and_float:[list columns], string:[list columns]}"""
        columns_by_types = {0: [], 1: []}
        for x_data, ys_data in drawdata:
            for y_label, y_values in ys_data.items():
                if y_values[0].__class__ == str:
                    columns_by_types[1].append(y_label)
                else:
                    columns_by_types[0].append(y_label)
        columns_by_types = {k: v for k, v in columns_by_types.items() if v}
        return columns_by_types

    def _get_column_data_type(self, column: str) -> int:
        """Returns type of 'column' data - 0 or 1."""
        for key in self.columns_by_types:
            if column in self.columns_by_types[key]:
                return key

    def _yield_columns_data(self, drawdata: List[tuple]) -> tuple:
        """Yields (x, y, label) data from 'drawdata'."""
        for (x_data, ys_data) in drawdata:
            for y_name, y_data in ys_data.items():
                yield (x_data, y_data, y_name)

    # def _define_drawing_method(self, separated_columns: Dict[int: List], list_of_methods: List):
    #     """the method defines whether is necessary single plot or two subplots.
    #     Returns respectives method"""
    #     number_types = len(separated_columns.keys())
    #     if number_types == 1:
    #         return list_of_methods[0]
    #     elif number_types == 2:
    #         return list_of_methods[1]

    def _draw(self, plotdata: List[tuple]) -> None:
        """Draw one or many time lines on one axes. Plot methods are plt.plot or plt.scatter."""
        self.fig, self.axes = plt.subplots(figsize=(12, 7))
        self._set_ylabels_to_axes([self.axes])
        for x, y, label in self._yield_columns_data(plotdata):
            self.axes.plot(x, y, label=label)
        self._show_drawing()

    def _draw_sharex(self, plotdata: List[tuple]) -> None:
        """Draw one or many time lines on two axes. Plot methods are plt.plot or plt.scatter."""
        number_axes = 2
        self.fig, self.axes = plt.subplots(nrows=number_axes, figsize=(12, 7), sharex='col')
        self._set_ylabels_to_axes(list(self.axes))
        for x, y, label in self._yield_columns_data(plotdata):
            col_type = self._get_column_data_type(label)
            self.axes[col_type].plot(x, y, label=label)
        self._show_drawing(self.axes[0])

    def _set_ylabels_to_axes(self, axes: List) -> None:
        """Sets labels to the each of axes."""
        for axes_number, labels in self._join_labels().items():
            axes[axes_number].set_ylabel(labels, fontsize=14, c='#0D1F34')

    def _join_labels(self) -> Dict[int, str]:
        """Joins y labels from list of labels."""
        labels_dict = {}
        for columns_type, list_labels in self.columns_by_types.items():
            labels_dict[columns_type] = '\n'.join(list_labels)
        return labels_dict

    def _show_drawing(self, ax2: plt.Axes = None) -> None:
        """Configures axis, text and labels on axes."""
        if ax2:
            ax = self.axes[1]
            ax2.legend(shadow=False)
            ax2.set_title(self.title, fontsize=17)
        else:
            ax = self.axes
        # ax1.yaxis.set_major_locator(ticker.FixedLocator([0,1,2,3,4,5]))
        # ax1.tick_params(axis='y',which='both',labelsize=12)
        # ax1.set_ylim(ymin=-1,ymax=4)
        ax.legend(shadow=False)

        ax.grid(which='major', linewidth=0.3, linestyle=':')
        ax.grid(which='minor', linewidth=0.3, linestyle=':')
        ax.set_title(self.title, fontsize=17)
        # ax.yaxis.set_wrap(True)
        # ax.set_xticklabels(rotation = 45,fontsize = 15)

        ax.set_xlabel('Time', fontsize=14, c='#0D1F34')
        f = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        f1 = mdates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=2))
        ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        # ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[4,8,12,16,20]))
        # ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(f)
        ax.xaxis.set_minor_formatter(f1)
        # ax.xaxis.set_major_locator(ticker.LinearLocator())
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=1))
        # ax.yaxis.set_major_locator(ticker.AutoLocator())
        ax.tick_params(axis='x', which='both', labelrotation=40)
        ax.tick_params(axis='x', which='major', labelsize=12)
        ax.tick_params(axis='x', which='minor', labelsize=11)
        ax.tick_params(axis='y', which='both', labelsize=12)
        plt.xticks(horizontalalignment='right')
        # plt.yticks(fontsize=13)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    import pandas as pd

    draw = Draw(title='E-19 test')
    data = {
        'timestamp': [datetime(2021, 3, 11, 9, 34, 39, 84252),
                      datetime(2021, 3, 11, 11, 34, 39, 84252),
                      datetime(2021, 3, 11, 15, 38, 39, 84252),
                      datetime(2021, 3, 11, 19, 49, 39, 84252)],
        'Current': [1.1, 2.34, 8.5, 30],
        'Temperature': [23, -40, -40, 85],
        'Humidity': [10, 20, 22, 45],
        'Status': ['passed', 'falied', 'passed', 'passed'],
        'Mode': ['2a', '2b', '2c', '2d'],
        'void': ['', '', '', '']
    }
    df = pd.DataFrame(data)
    x = df.pop('timestamp')
    #draw.draw_lines([(x, df)])

    #draw.draw_lines([(x, df[['Current', 'Temperature']])])
    #draw.draw_table([(x, df[['Current', 'Temperature']])])
    draw.draw_table([(x, df[['Current', 'Temperature']])])