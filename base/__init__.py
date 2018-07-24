# -*- coding:utf-8 -*-
__author__ = 'kaI'
from update import *

reload(sys)
sys.setdefaultencoding('utf-8')


class BaseDataKai(object):
    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'base\\base_data')

        self.all_A_stocks_df = pd.read_excel(self.path+'\\all_A_stock.xls', index_col=0)
        self.tdays_df = pd.read_excel(self.path+'\\tdays.xls', index_col=0)
        self.tdays_df.index = self.tdays_df.index.astype('str')
        self.ic_df = pd.read_excel(self.path+'\\ic_wind_constituent.xls', index_col=0)
        self.if_df = pd.read_excel(self.path+'\\if_wind_constituent.xls', index_col=0)

        self.update = False

    def update_data(self):
        if not self.update:
            return
        save_dir = self.path
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        update_base_data = UpdateBaseData(date_str=date_str, save_dir=save_dir)
        # 更新全A股票信息
        update_base_data.get_all_a_stock()
        # 更新IC、IF指数成分信息
        update_base_data.get_index_constituent()
        # 更新st股信息
        update_base_data.get_all_st_stock()
        # 更新解锁信息
        update_base_data.get_unlocking_stock()
        # 更新股东持股信息
        update_base_data.get_holder_info()
        # 更新日期df
        update_base_data.get_tdays()
