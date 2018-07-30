# -*- coding:utf-8 -*-
__author__ = 'kai'
from base import *
from back_test import *
from set_services import *
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')


class ToolKai(object):
    def __init__(self, base_data=True, back_test_data=False, base_update=False, back_test_update=False):
        self.path_kai = 'D:\\kaI\\tool_kai'
        os.chdir(self.path_kai)

        if base_data:
            # 基础数据
            self.get_base_data()

        if back_test_data:
            # 回测基础数据
            self.get_back_test_data()

        if base_update:
            self.get_base_data()
            self.base_data.update = True
            self.base_data.update_data()

        if back_test_update:
            self.get_back_test_data()
            self.back_test_data.update = True
            self.back_test_data.update_data()

    def get_base_data(self):
        """获取基础数据"""
        self.base_data = BaseDataKai()
        self.all_a_stock_df = self.base_data.all_A_stocks_df
        self.all_a_stock = self.all_a_stock_df.index.tolist()
        self.tdays_df = self.base_data.tdays_df
        self.ic_df = self.base_data.ic_df
        self.if_df = self.base_data.if_df
        self.st_df = self.base_data.st_df

    def get_back_test_data(self):
        """获取回测框架基础数据"""
        self.back_test_data = BackTestDataKai(all_a_stock_df=self.all_a_stock_df, tdays_df=self.tdays_df)
        self.all_a_amt_df = self.back_test_data.all_a_amt_df
        self.all_a_vwap_df = self.back_test_data.all_a_vwap_df
        self.index_close_df = self.back_test_data.index_close_df
        self.all_a_close_df = self.back_test_data.all_a_close_df

    def drop_st(self, df):
        """剔除st股"""
        return drop_st_stocks(df=df, st_df=self.st_df)

    def drop_new(self, df, days=180):
        """剔除次新股"""
        return drop_new_stocks(df=df, all_a_stock_df=self.all_a_stock_df, days=days)

    def drop_suspend(self, df, end_date):
        """剔除停牌股"""
        data_path = os.path.join(self.path_kai, 'base\\base_data\\suspend_data\\')
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        if not os.path.exists(data_path+str(end_date)+'.xls'):
            w.start()
            start_data = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=1)
            start_data = start_data.strftime('%Y-%m-%d')
            wind_data = w.wset("tradesuspend", "startdate="+start_data+";enddate="+end_date)
            suspend_df = pd.DataFrame()
            for col in range(len(wind_data.Fields)):
                suspend_df[wind_data.Fields[col]] = wind_data.Data[col]
            suspend_df.to_excel(os.path.join(data_path+str(end_date)+'.xls'))
        else:
            suspend_df = pd.read_excel(os.path.join(data_path+str(end_date)+'.xls'))
        return drop_suspend_stocks(df=df, suspend_df=suspend_df)
