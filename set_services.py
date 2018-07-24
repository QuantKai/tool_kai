# -*- coding:utf-8 -*-
import pandas as pd
import os


def get_tdays(day_list, col_name):
    tdays_dataframe = pd.read_excel(os.path.join('tdays', 'tdays.xls'))
    tdays_dataframe.index = tdays_dataframe.index.astype('str')
    # print day_list[0],args[1],args[2]
    tdays_dataframe = tdays_dataframe[day_list[0]:day_list[-1]]
    tdays_dataframe = tdays_dataframe[tdays_dataframe[col_name]==1]
    return tdays_dataframe.index.tolist()



