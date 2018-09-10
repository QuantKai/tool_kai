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

    def get_industry_diviation(self, strategy_df, index_name):
        """计算策略行业偏离"""
        if index_name.lower() == 'ic':
            industry_df = self.ic_df
        elif index_name.lower == 'if':
            industry_df = self.if_df
        else:
            return None
        return get_industry_diviation(strategy_df=strategy_df,
                                      industry_df=industry_df,
                                      all_a_stock_df=self.all_a_stock_df)

    def wind_to_df(self, wind_data):
        return wind_data_to_df(wind_data=wind_data)

    def get_front_financial_date(self, trade_date, num=2, ahead=0):
        """:return 前N季度末日期"""
        return get_front_financial_date(trade_date=trade_date, kai_tdays_df=self.tdays_df, num=num, ahead=ahead)

    def get_front_trade_date(self, trade_date, period='w', num=2, ahead=0):
        """:return 前N交易类型交易日"""
        return get_front_trade_date(trade_date=trade_date, kai_tdays_df=self.tdays_df,
                                    period=period, num=num, ahead=ahead)

    def is_trade_time(self, date_str, style='stock'):
        """判断是否是交易时间"""
        return is_trade_time(date_str=date_str, style=style, tdays_df=self.tdays_df)
