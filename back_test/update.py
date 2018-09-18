# -*- coding:utf-8 -*-
import pandas as pd
import os
import sys
from WindPy import *
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')


class UpdateBackTestData(object):
    def __init__(self, now_date, all_a_stock_df):
        self.now_date = now_date
        self.all_a_stock_df = all_a_stock_df
        self.all_a_stock = all_a_stock_df.index.tolist()
        self.path = os.path.join(os.getcwd(), 'back_test\\stock_data')
        print u'数据下载至', self.now_date
        self.allAamt, self.ipo_date, self.allAvwap, self.indexClose, self.allAclose = self.prepare_datas()

    def prepare_datas(self):
        print os.getcwd()
        files_list = os.listdir(self.path)

        for file in files_list:
            file = file.decode('gbk')
            if 'allAamt' in file:
                allAamt = file

            if 'ipo_date' in file:
                ipo_date = file

            if 'allAvwap' in file:
                allAvwap = file

            if 'indexClose' in file:
                indexClose = file

            if 'allAclose' in file:
                allAclose = file

        return allAamt, ipo_date, allAvwap, indexClose, allAclose

    def update_allAamt(self):
        print u'尝试下载allAamt......'
        allAamt_df = pd.read_csv(os.path.join(self.path, self.allAamt), index_col=0)
        start_date = str(allAamt_df.index[-1])
        if '-' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        elif '/' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d').strftime('%Y%m%d')
        if not start_date == ''.join(self.now_date.split('-')):
            print u'allAamt数据至', start_date, ', today is ', self.now_date
            w.start()
            wind_data = w.wsd(self.all_a_stock, "amt", start_date, self.now_date, "ShowBlank=0;PriceAdj=F")
            print wind_data
            new_df = pd.DataFrame(index=[str(data).split(' ')[0] for data in wind_data.Times])
            for stock_num in range(len(self.all_a_stock)):
                new_df[self.all_a_stock[stock_num]] = wind_data.Data[stock_num]
            new_df.index = pd.to_datetime(new_df.index)
            new_df.index = [inn.strftime('%Y-%m-%d') for inn in new_df.index]
            allAamt_df.drop([allAamt_df.index.tolist()[-1]], inplace=True)
            allAamt_df = allAamt_df.append(new_df, sort=True)
        else:
            print u'无需下载allAamt数据'
        allAamt_df.to_csv(os.path.join(self.path, self.allAamt))

    def update_allAclose(self):
        print u'尝试下载allAclose......'
        allAclose_df = pd.read_csv(os.path.join(self.path, self.allAclose), index_col=0)
        start_date = str(allAclose_df.index[-1])
        if '-' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        elif '/' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d').strftime('%Y%m%d')
        if not start_date == ''.join(self.now_date.split('-')):
            print u'allAclose数据至', start_date, ', today is ', self.now_date
            w.start()
            wind_data = w.wsd(self.all_a_stock, "close", start_date, self.now_date, "ShowBlank=0;PriceAdj=B")
            print wind_data
            new_df = pd.DataFrame(index=[str(data).split(' ')[0] for data in wind_data.Times])
            for stock_num in range(len(self.all_a_stock)):
                new_df[self.all_a_stock[stock_num]] = wind_data.Data[stock_num]
            new_df.index = pd.to_datetime(new_df.index)
            new_df.index = [inn.strftime('%Y-%m-%d') for inn in new_df.index]
            allAclose_df.drop([allAclose_df.index.tolist()[-1]], inplace=True)
            allAclose_df = allAclose_df.append(new_df, sort=True)
        else:
            print u'无需下载allAclose数据'
        allAclose_df.to_csv(os.path.join(self.path, self.allAclose))

    def update_allAvwap(self):
        print u'尝试下载allAvwap......'
        allAvwap_df = pd.read_csv(os.path.join(self.path, self.allAvwap), index_col=0)
        start_date = str(allAvwap_df.index[-1])
        if '-' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        elif '/' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d').strftime('%Y%m%d')
        if not start_date == ''.join(self.now_date.split('-')):
            print u'allAvwap数据至', start_date, ', today is ', self.now_date
            w.start()
            wind_data = w.wsd(self.all_a_stock, "vwap", start_date, self.now_date, "ShowBlank=0;PriceAdj=B")
            print wind_data
            new_df = pd.DataFrame(index=[str(data).split(' ')[0] for data in wind_data.Times])
            for stock_num in range(len(self.all_a_stock)):
                new_df[self.all_a_stock[stock_num]] = wind_data.Data[stock_num]
            new_df.index = pd.to_datetime(new_df.index)
            new_df.index = [inn.strftime('%Y-%m-%d') for inn in new_df.index]
            allAvwap_df.drop([allAvwap_df.index.tolist()[-1]], inplace=True)
            allAvwap_df = allAvwap_df.append(new_df, sort=True)
        else:
            print u'无需下载allAvwap数据'
        allAvwap_df.to_csv(os.path.join(self.path, self.allAvwap))

    def update_indexClose(self):
        print u'尝试下载indexClose......'
        indexClose_df = pd.read_csv(os.path.join(self.path, self.indexClose), index_col=0, dtype=str)
        start_date = str(indexClose_df.index[-1])
        if '-' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        elif '/' in start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d').strftime('%Y%m%d')
        if not start_date == ''.join(self.now_date.split('-')):
            print u'allAvwap数据至', start_date, ', today is ', self.now_date
            all_stock_list = indexClose_df.columns.tolist()
            w.start()
            wind_data = w.wsd(all_stock_list, "close", start_date, self.now_date, "PriceAdj=B")
            print wind_data
            new_df = pd.DataFrame(index=[str(data).split(' ')[0] for data in wind_data.Times])
            for stock_num in range(len(wind_data.Codes)):
                new_df[wind_data.Codes[stock_num]] = wind_data.Data[stock_num]
            new_df.index = pd.to_datetime(new_df.index)
            new_df.index = [inn.strftime('%Y-%m-%d') for inn in new_df.index]
            indexClose_df.drop([indexClose_df.index.tolist()[-1]], inplace=True)
            indexClose_df = indexClose_df.append(new_df, sort=True)
        else:
            print u'无需下载indexClose数据'
        indexClose_df.to_csv(os.path.join(self.path, self.indexClose))

    def update_ipo_date(self):
        print u'尝试下载ipo_date......'
        ipo_date_df = pd.read_csv(os.path.join(self.path, self.ipo_date), index_col=0)
        stock = list(set(self.all_a_stock)-set(ipo_date_df.index.tolist()))
        if len(stock):
            print u'缺少股票:', stock
            w.start()
            wind_data = w.wss(stock, "ipo_date")
            print wind_data
            new_df = pd.DataFrame({"ipo_date": [str(data).split(' ')[0] for data in wind_data.Data[0]]}, index=stock)
        else:
            new_df = pd.DataFrame()
            print u'无需下载ipo_date数据'
        ipo_date_df = ipo_date_df.append(new_df, sort=True)
        ipo_date_df.to_csv(os.path.join(self.path, self.ipo_date))





