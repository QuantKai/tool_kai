# -*- coding:utf-8 -*-
__author__ = 'kai'
from base import *
from back_test import *
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

path_kai = 'D:\\kaI\\tool_kai'
os.chdir(path_kai)


class ToolKai(object):
    def __init__(self, base_data=True, back_test_data=False):
        if base_data:
            # 基础数据
            self.get_base_data()

        if back_test_data:
            # 回测基础数据
            self.get_back_test_data()

    def get_base_data(self):
        self.base_data = BaseDataKai()
        self.all_a_stock_df = self.base_data.all_A_stocks_df
        self.all_a_stock = self.all_a_stock_df.index.tolist()
        self.tdays_df = self.base_data.tdays_df
        self.ic_df = self.base_data.ic_df
        self.if_df = self.base_data.if_df

    def get_back_test_data(self):
        self.back_test_data = BackTestDataKai(all_a_stock_df=self.all_a_stock_df, tdays_df=self.tdays_df)
        self.all_a_amt_df = self.back_test_data.all_a_amt_df
        self.all_a_vwap_df = self.back_test_data.all_a_vwap_df
        self.index_close_df = self.back_test_data.index_close_df
        self.all_a_close_df = self.back_test_data.all_a_close_df

