# -*- coding:utf-8 -*-
__author__ = 'kaI'
import pandas as pd
import os


def drop_st_stocks(df, st_df):
    drop_index = set(st_df.index.tolist()).intersection(set(df.index.tolist()))
    if not drop_index:
        return df
    return df.drop(drop_index)


def drop_suspend_stocks(df, suspend_df):
    drop_index = set(suspend_df['wind_code'].tolist()).intersection(set(df.index.tolist()))
    if not drop_index:
        return df
    return df.drop(drop_index)


def drop_new_stocks(df, all_a_stock_df, days):
    import datetime
    date = datetime.datetime.now()-datetime.timedelta(days=days)
    new_stocks_df = all_a_stock_df[pd.to_datetime(all_a_stock_df['ipo_date']) > date]
    drop_index = set(new_stocks_df.index.tolist()).intersection(set(df.index.tolist()))
    return df.drop(drop_index)


def get_tdays(day_list, col_name):
    tdays_dataframe = pd.read_excel(os.path.join('tdays', 'tdays.xls'))
    tdays_dataframe.index = tdays_dataframe.index.astype('str')
    # print day_list[0],args[1],args[2]
    tdays_dataframe = tdays_dataframe[day_list[0]:day_list[-1]]
    tdays_dataframe = tdays_dataframe[tdays_dataframe[col_name] == 1]
    return tdays_dataframe.index.tolist()


