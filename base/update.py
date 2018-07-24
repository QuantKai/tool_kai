# -*- coding:utf-8 -*-
import pandas as pd
from WindPy import *
import datetime
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class UpdateBaseData(object):
    def __init__(self, date_str, save_dir):
        self.date_str = date_str
        self.save_dir = save_dir
        w.start()

    # 下载A股基础数据，避免重复下载浪费资源

    # 获取全A股票以及行业
    def get_all_a_stock(self):
        all_a = w.wset("sectorconstituent", "date="+self.date_str+";sectorid=a001010100000000")
        all_a_df = pd.DataFrame({'sec_name': all_a.Data[2]}, index=all_a.Data[1])
        all_a_industries = w.wss(all_a.Data[1], "industry_sw", "tradeDate="+self.date_str+";industryType=1")
        wind_data = w.wss(all_a.Data[1], "SHSC,SHSC2,marginornot", "tradeDate="+self.date_str)
        all_a_df['industry'] = all_a_industries.Data[0]
        all_a_df['SHSC'] = wind_data.Data[0]
        all_a_df['SHSC2'] = wind_data.Data[1]
        all_a_df['marginornot'] = wind_data.Data[2]
        wind_data = w.wss(all_a.Data[1], "ipo_date")
        all_a_df['ipo_date'] = [str(data)[0:10] for data in wind_data.Data[0]]
        all_a_df.to_excel(os.path.join(self.save_dir, 'all_A_stock.xls'))

    # 获取中证500，沪深300行业成分
    def get_index_constituent(self):
        ic_wind_constituent_data = w.wset("indexconstituent", "date="+self.date_str +
                                          ";windcode=000905.SH;field=wind_code,sec_name,i_weight")
        ic_df = pd.DataFrame({'sec_name': ic_wind_constituent_data.Data[1],
                              'i_weight': ic_wind_constituent_data.Data[2]},
                             index=ic_wind_constituent_data.Data[0], columns=['sec_name', 'i_weight'])
        ic_df.to_excel(os.path.join(self.save_dir, 'ic_wind_constituent.xls'))
        if_wind_constituent_data = w.wset("indexconstituent", "date="+self.date_str +
                                          ";windcode=000300.SH;field=wind_code,sec_name,i_weight")
        if_df = pd.DataFrame({'sec_name': if_wind_constituent_data.Data[1],
                              'i_weight': if_wind_constituent_data.Data[2]},
                             index=if_wind_constituent_data.Data[0], columns=['sec_name', 'i_weight'])
        if_df.to_excel(os.path.join(self.save_dir, 'if_wind_constituent.xls'))

    def get_all_st_stock(self):
        all_a_df = pd.read_excel(os.path.join(self.save_dir, 'all_A_stock.xls'))
        st_sec_name = [sec_name for sec_name in all_a_df['sec_name'].tolist() if "ST" in sec_name or "*ST" in sec_name]
        st_df = pd.merge(pd.DataFrame(index=st_sec_name), all_a_df, left_index=True, right_on='sec_name')
        st_df.to_excel(os.path.join(self.save_dir, 'st_wind_constituent.xls'))

    # 获取解禁信息
    def get_unlocking_stock(self):
        all_a_df = pd.read_excel(os.path.join(self.save_dir, 'all_A_stock.xls'))
        end_day = '20181231'
        unlocking_stocks = w.wss(all_a_df.index.tolist(), "share_rtd_unlockingdate,share_tradable_current,share_rtd_bance,share_rtd_datatype,share_tradable_sharetype","tradeDate="+end_day+";unit=1")
        print unlocking_stocks
        unlocking_stocks_df = pd.DataFrame(index=all_a_df.index)
        for col in range(len(unlocking_stocks.Fields)):
            unlocking_stocks_df[unlocking_stocks.Fields[col]] = unlocking_stocks.Data[col]
        unlocking_stocks_df.to_excel(os.path.join(self.save_dir, 'unlocking_stocks.xls'))

    # 获取前十股东信息
    def get_holder_info(self):
        if not os.path.exists('holder_liq'):
            os.mkdir('holder_liq')
        a_day = '20180322'
        all_a_df = pd.read_excel(os.path.join(self.save_dir, 'all_A_stock.xls'))
        holder_info_df = pd.DataFrame(index=all_a_df.index.tolist())
        for num in range(10):
            order = str(num+1)
            wind_data = w.wss(all_a_df.index.tolist(), "holder_liqname,holder_liqquantity,holder_liqpct", "tradeDate="+a_day+";order="+order+";unit=1")
            print wind_data
            for data in range(len(wind_data.Fields)):
                holder_info_df[wind_data.Fields[data]+'_'+order] = wind_data.Data[data]
            print holder_info_df
        holder_info_df.to_excel(os.path.join('holder_liq', a_day+'.xls'))

    def get_tdays(self):
        now_day = '2020-1-31'
        if not os.path.exists(os.path.join(self.save_dir, 'tdays.xls')):
            tdays_df = pd.DataFrame()
        else:
            tdays_df = pd.read_excel(os.path.join(self.save_dir, 'tdays.xls'))
        if len(tdays_df):
            start_day = tdays_df.index.tolist()[-1]
        else:
            start_day = '2000-01-01'
        print start_day, now_day
        alldays_data_df = pd.DataFrame({'alldays': 1}, index=w.tdays(start_day, now_day, "Days=Alldays").Data[0])
        weekdays_data_df = pd.DataFrame({'weekdays': 1}, index=w.tdays(start_day, now_day, "Days=Weekdays").Data[0])
        tradedays_d_data_df = pd.DataFrame({'tradedays_d': 1},index=w.tdays(start_day, now_day, "Period=D").Data[0])
        tradedays_w_data_df = pd.DataFrame({'tradedays_w': 1},index=w.tdays(start_day, now_day, "Period=W").Data[0])
        tradedays_m_data_df = pd.DataFrame({'tradedays_m': 1},index=w.tdays(start_day, now_day, "Period=M").Data[0])
        new = pd.merge(alldays_data_df, weekdays_data_df, left_index=True, right_index=True, how='left')
        new = pd.merge(new, tradedays_d_data_df, left_index=True, right_index=True, how='left')
        new = pd.merge(new, tradedays_w_data_df, left_index=True, right_index=True, how='left')
        new = pd.merge(new, tradedays_m_data_df, left_index=True, right_index=True, how='left')

        def deal(time_str):
            time_str = ''.join(str(time_str)[0:10])
            return time_str

        new.index = map(deal, new.index.tolist())
        tdays_df = tdays_df.append(new)
        tdays_df.to_excel(os.path.join(self.save_dir, 'tdays.xls'))

