# -*- coding:utf-8 -*-
__author__ = 'kaI'
from update import *
reload(sys)
sys.setdefaultencoding('utf-8')


class BackTestDataKai(object):
    def __init__(self, all_a_stock_df, tdays_df):
        self.path = os.path.join(os.getcwd(), 'back_test\\stock_data')
        self.all_a_stock_df = all_a_stock_df
        self.tdays_df = tdays_df
        self.all_a_stock_df = all_a_stock_df

        self.all_a_amt_df = pd.read_csv(self.path+'\\allAamt.csv', index_col=0).T
        self.all_a_vwap_df = pd.read_csv(self.path+'\\allAvwap.csv', index_col=0).T
        self.index_close_df = pd.read_csv(self.path+'\\indexClose.csv', index_col=0).T
        self.all_a_close_df = pd.read_csv(self.path+'\\allAclose.csv', index_col=0).T

        self.update = False

    def update_data(self):
        if not self.update:
            return
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        now_date = self.tdays_df[self.tdays_df['tradedays_d'] == 1].loc[:now_date].index.tolist()[-2]
        update_back_test_data = UpdateBackTestData(now_date=now_date, all_a_stock_df=self.all_a_stock_df)
        update_back_test_data.update_allAamt()
        update_back_test_data.update_allAclose()
        update_back_test_data.update_allAvwap()
        update_back_test_data.update_indexClose()
        update_back_test_data.update_ipo_date()
