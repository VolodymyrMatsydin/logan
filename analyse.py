# version 1.17
# python 3.9

import pandas as pd
import re
import io
from datetime import datetime
from typing import Dict, Any

# list of various sources of log files
DATA_SOURCES = {
                "Climatic chamber_1": lambda x: ChamberAnalyse(x),
                'Test system (.cmr)': lambda x: TestSystemCmrAnalyse(x),
                'Rotronic': lambda x: RotronicAnalyse(x),
                'DMM': lambda x: DMMAnalyse(x),
                'Cooling system ZUT-Michalin': lambda x: CoolingSystemAnalyse(x),
                'Test system (.mmr)': lambda x: TestSystemMmrAnalyse(x),
                'YokogawaCSV': lambda x: YokogawaCSV(x)
                }


class BaseAnalyse():
    """Class not for instancing. Basic class for all of analyses classes.
    Receives 'kw', open 'filespaths' for parsing and create 'DataFrame'."""

    def __init__(self, kw: Dict[str, Any]) -> None:
        self._kw = kw
        self.sel_params = set()
        self.df = self.create_df()
        # self.dtcolumn = self.get_index_of_datetime_column()

    def create_df(self) -> pd.DataFrame:
        """Create dataframes from one or several the same type files and concatenate them."""
        if len(self.filespaths) > 1:
            list_df = []
            for path in self.filespaths:
                list_df.append(self._create_df(path))
                print('created df:', path)
            df = pd.concat(list_df)
            del list_df
        else:
            df = self._create_df(self.filespaths[0])
        return df

    def _create_df(self, filepath: str) -> pd.DataFrame:
        """Open 'filepath' for parsing and then create 'DataFrame'."""
        dataframe = pd.read_csv(filepath, **self._kw)
        assert not dataframe.empty, 'DataFrame has not been created.'
        return dataframe

    def get_index_of_datetime_column(self) -> int or Exception:
        """Search datetime column within the dataframe. Return dt_column index."""
        for par_count, parameter in enumerate(self.df):
            if isinstance(self.df[parameter][0], datetime) or self.df[parameter].dtype == "datetime64[ns]":
                print('dtcolumn:', par_count)
                return par_count
        raise


class ChamberAnalyse(BaseAnalyse):
    """Parses files from temperature chamber."""
    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': ';',
              'parse_dates': [0],
              'header': 3,
              'engine': 'c',
              'skiprows': (6,),
              'memory_map': True
              }
        BaseAnalyse.__init__(self, kw)


class TestSystemCmrAnalyse(BaseAnalyse):
    """Parses '.cmr' files from TestSystem."""
    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': ';',
              'parse_dates': [0],
              # dtype={'Source':'str', 'DTC':'str'},
              'na_values': [''],
              'keep_default_na': False,
              'low_memory': False,
              'converters': {'Source': str, 'DTC': lambda x: TestSystemCmrAnalyse._dtc_parser(x)},
              'header': 19,
              'engine': 'c',
              'skiprows': (20,)
              }
        for _ in [1, 2]:
            try:
                BaseAnalyse.__init__(self, kw)
            except pd.errors.ParserError:
                self.filespaths = [TestSystemCmrAnalyse._dtc_replacer(filespaths[0])]
            else:
                break

    @staticmethod
    def _dtc_replacer(filepath: str) -> io.StringIO:  # przerobic na paths
        """Replaces needless delimiters which matched patterns. Returns file object"""
        pattern = '\d{3}.{3}:.{5,}\n'
        with open(filepath, encoding='latin-1') as f:
            fileobj = f.read()
        string = re.sub(pattern, lambda x: x.group(0).replace(';', '\t').replace('\n', '', 1), fileobj)
        # print(string)
        return io.StringIO(string)

    @staticmethod
    def _dtc_parser(dtc_string: str) -> str:
        """Searches invalid DTC string and replace it with normal delimited string."""
        pattern = r'.[A-Z0-9]{5}:'
        if dtc_string:
            s = ''
            for i in re.findall(pattern, dtc_string):
                s = s + i
            return s
        else:
            return str(dtc_string)


class TestSystemMmrAnalyse(BaseAnalyse):
    """Parses 'mmr' text files TestSystem."""

    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw =  {'sep': ';',
               'parse_dates': [[0, 1]],
               'date_parser': self._recogn_date,
               'header': 0,
               # 'dtype': {'SERIAL_NUMBER': str},
               # 'na_filter': False,
               # 'converters': {'Time': TestSystemUUTAnalyse.change_time_format},
               'engine': 'c',
               'skiprows': (1, 2, 3),
               'skip_blank_lines': True,
               'memory_map': True
               }
        BaseAnalyse.__init__(self, kw)
        self.df.dropna(how='all', axis=1, inplace=True)

    def _recogn_date(self, dtstring: str) -> datetime.timestamp:
        """Recognizes datetime string and return the datetime instance."""
        return datetime.strptime(dtstring, '%Y.%m.%d %H:%M:%S:%f')


class CoolingSystemAnalyse(BaseAnalyse):
    """Parses log files from Cooling System."""

    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': ',',
              'parse_dates': [[0, 1]],
              'header': 0,
              'engine': 'c'
              }
        BaseAnalyse.__init__(self, kw)


class DMMAnalyse(BaseAnalyse):
    """Parses text files from DMM."""

    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': '\t',
              # parse_dates:{'Timestamp':[0,1]},
              # names:['Date', 'Time', 'Current, A'],
              # converters:{'Value':_replacer}
              'header': 0,
              'engine': 'c',
              'dayfirst': False,
              'memory_map': True
              }
        BaseAnalyse.__init__(self, kw)

        self.df['Timestamp'] = self._recogn_date(self.df['Date'] + ' ' + self.df['Time'])
        self.df.drop(['Date', 'Time'], 1, inplace=True)
        self.df['Value'].replace({' A': ''}, regex=True, inplace=True)
        self.df = self.df.astype({'Timestamp': 'datetime64', 'Value': float})

    def _recogn_date(self, series: pd.Series) -> pd.Series:
        """Recognizes datetime string and returns timestamp instance."""
        new_series = pd.to_datetime(series,
                                yearfirst=True,
                                format='%y-%m-%d %H:%M:%S.%f',
                                exact=True,
                                )
        return new_series


class YokogawaCSV(BaseAnalyse):
    """Parses '.csv' files from Yokogawa."""

    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': ',',
              'parse_dates': [0],
              'header': 2,
              'engine': 'c',
              'skiprows': 9,
              'memory_map': True
              }
        BaseAnalyse.__init__(self, kw)


class RotronicAnalyse(BaseAnalyse):
    """Parses '.xls' files from Rotronic."""

    def __init__(self, filespaths: Dict) -> None:
        self.filespaths = filespaths
        kw = {'sep': '\t',
              'parse_dates': [[0, 1]],
              'dayfirst': True,
              'header': 32,
              'names': ['Date', 'Time', 'Humidity, %', 'Temperature, ℃'],
              'usecols': ['Date', 'Time', 'Humidity, %', 'Temperature, ℃'],
              'engine': 'c',
              'skiprows': (43,),
              'memory_map': True
              }
        BaseAnalyse.__init__(self, kw)


if __name__ == '__main__':
    PATHS = [
        r's:\WMa\TEMP\My\Sample_files\Chamber_2\Chamber_log_EWR91188_mPad_k-02_LegB.txt',
        r's:\WMa\TEMP\My\Sample_files\TestSystemCmrOld\DUT01_mode_IIa_armed_LT_20210311131802.cmr',
        r's:\WMa\TEMP\My\Sample_files\Rotronic\41712069.XLS',
        r's:\WMa\TEMP\My\Sample_files\DMM_Log\006_IIa_armed_RT_retest.txt',
        r's:\WMa\TEMP\My\Sample_files\CoolingSystemZUT\20200515.csv',
        r'c:\Users\fjr0p1\AppData\Local\Programs\Python\Python39\Log_wiever\sample_files\mmr_report_94326017_socket0_FCT_16V_p23C_2021-07-16_104949.txt',
        r's:\WMa\TEMP\My\Sample_files\YOKOGAWA_to_csv_20210211_131338_468_000.csv'
    ]
    selected_class = 'Test system (.mmr)'
    for source, path in zip(DATA_SOURCES, PATHS):
        if source == selected_class:
            instance = DATA_SOURCES[selected_class]([path])
            break
    print(instance.df)
    print(instance.df.dtypes)
