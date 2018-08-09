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


def get_industry_diviation(strategy_df, industry_df, all_a_stock_df):
    """计算行业偏离,没有权重默认等权"""
    if 'weight' not in strategy_df:
        strategy_df['weight'] = 100.0000000/len(strategy_df)
        print 'no weight'
    if 'industry' not in industry_df.columns.values.tolist():
        industry_df = pd.merge(industry_df, pd.DataFrame(all_a_stock_df['industry'], index=all_a_stock_df.index),
                               left_index=True, right_index=True, how='left')
    if 'industry' not in strategy_df.columns.values.tolist():
        strategy_df = pd.merge(strategy_df, pd.DataFrame(all_a_stock_df['industry'], index=all_a_stock_df.index),
                               left_index=True, right_index=True, how='left')
    # 对策略行业进行加总
    strategy_group = list(strategy_df.groupby(['industry']))
    strategy_list = []
    strategy_weight_list = []
    strategy_len_list = []
    for industry_num in range(len(strategy_group)):
        strategy_list.append(strategy_group[industry_num][0])
        strategy_weight_list.append(strategy_group[industry_num][1].sum(0)['weight'])
        strategy_len_list.append(len(strategy_group[industry_num][1]))
    strategy_sum_industry_df = pd.DataFrame({'strategy_weight': strategy_weight_list,
                                             'strategy_len': strategy_len_list}, index=strategy_list)
    # 对申万行业进行加总
    industry_group = list(industry_df.groupby(['industry']))
    industry_list = []
    industry_weight_list = []
    industry_len_list = []
    for industry_num in range(len(industry_group)):
        industry_list.append(industry_group[industry_num][0])
        industry_weight_list.append(industry_group[industry_num][1].sum()['i_weight'])
        industry_len_list.append(len(industry_group[industry_num][1]))
    save_df = pd.merge(pd.DataFrame({'industry_weight': industry_weight_list, 'industry_len': industry_len_list},
                                    index=industry_list),
                       strategy_sum_industry_df, left_index=True, right_index=True, how='left').fillna(0)
    save_df['industry_deviation'] = save_df['strategy_weight'] - save_df['industry_weight']
    return save_df.sort_values(by=['industry_deviation'], ascending=False)


def get_tdays(day_list, col_name):
    tdays_dataframe = pd.read_excel(os.path.join('tdays', 'tdays.xls'))
    tdays_dataframe.index = tdays_dataframe.index.astype('str')
    # print day_list[0],args[1],args[2]
    tdays_dataframe = tdays_dataframe[day_list[0]:day_list[-1]]
    tdays_dataframe = tdays_dataframe[tdays_dataframe[col_name] == 1]
    return tdays_dataframe.index.tolist()
