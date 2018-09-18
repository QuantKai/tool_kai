# -*- coding: utf-8 -*-
# __author__ = 'Jared-Wong'
import os, datetime, sys
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import xlrd
import xlwt
from sklearn import linear_model

# import improveWeight

# 文件版本
file_ver = ''
# 回测结束日期
end_date = datetime.datetime.now()-datetime.timedelta(days=1)
end_date = end_date.strftime('%Y-%m-%d')
end_date = '2018-07-10'

# ----------------------------参数设置---------------------------------
# 保证金比例和Beta
deposit_if = 0.2
deposit_ic = 0.3
deposit_ih = 0.2
beta = 1

# 单利/复利模式
# interest_mode = 'danli'
interest_mode = 'fuli'

# 是否扣除成本
# cost_mode = False
cost_mode = True

# 成本估计
sellcost_rate = 0.0013
buycost_rate = 0.0003
impactcost_rate = 0.0010

# ---------------------------------------------------------------------


root_dir = os.getcwd()

if not(os.path.exists('BT_Output')):
    os.makedirs('BT_Output')
# if not(os.path.exists('hold_improve')):
# 	os.makedirs('hold_improve')

# 读入回测所需要的数据
stocks_data_df = pd.read_csv('stock_data/allAclose'+file_ver+'.csv', index_col = 0)
all_trade_date = stocks_data_df.index.tolist()
index_data_df = pd.read_csv('stock_data/indexClose'+file_ver+'.csv', index_col = 0)
stocks_vwap_df = pd.read_csv('stock_data/allAvwap'+file_ver+'.csv', index_col = 0)
stocks_amt_df = pd.read_csv('stock_data/allAamt'+file_ver+'.csv', index_col = 0)


hold_file = []
shift_trade_date = []
hold_file_dict = {}


def read_file(file_path):
    global hold_file
    global shift_trade_date
    global hold_file_dict

    hold_file = []
    shift_trade_date = []
    hold_file_dict = {}

    for root, dirs, files in os.walk(root_dir+'\\'+file_path):
        hold_file = files
    print hold_file

    for fn in hold_file:
        shift_trade_date.append(fn[0:10])
        hold_file_dict[shift_trade_date[-1]] = fn
    shift_trade_date.sort()

# # 改进权重
# def modifyWeight(shift_trade_date, hold_file_dict):
# 	improve_hold_file_dict = {}
# 	for i in range(0, len(shift_trade_date)):
# 		origin_df = pd.read_excel('hold_stocks\\'+hold_file_dict[shift_trade_date[i]], index_col = None)
# 		stocks = origin_df['stock'].values.tolist()
# 		sweight = origin_df['weight'].values.tolist()
# 		sname = origin_df['sec_name'].values.tolist()
# 		date_len = 30
# 		now_date = shift_trade_date[i]
# 		front_date = all_trade_date[all_trade_date.index(now_date)-date_len]
# 		data_df = stocks_data_df[stocks].loc[front_date:now_date]
# 		# print len(data_df)
# 		# os._exit(0)
# 		shift_data_df = data_df.shift(1)
# 		ret_df = data_df / shift_data_df - 1
# 		ret_df = ret_df.drop(ret_df.index[0])
# 		ret_df = ret_df.fillna(0)
# 		wscore, wError = improveWeight.Efficient_Weight(ret_df)
# improveWeight.save_modify_holding(stocks, sweight, sname, wscore, wError, 'hold_improve/'+shift_trade_date[i]+'.xls')
# 		improve_hold_file_dict[shift_trade_date[i]] = shift_trade_date[i]+'.xls'
# 	return improve_hold_file_dict


# 回测函数主体
def backTest(fn):
    # 初始化储存回测数据
    Asset_analysis = {}
    Asset_analysis['trade_date'] = []
    # IF
    Asset_analysis['hold_chg_if'] = []
    Asset_analysis['long_equity_if'] = []
    Asset_analysis['IF_chg'] = []
    Asset_analysis['short_equity_if'] = []
    Asset_analysis['daily_profit_if'] = []
    Asset_analysis['daily_profit_if_strabp'] = []
    Asset_analysis['accumulate_equity_if'] = []
    Asset_analysis['retracement_if'] = []
    Asset_analysis['free_cash_if'] = []
    # IC
    Asset_analysis['hold_chg_ic'] = []
    Asset_analysis['long_equity_ic'] = []
    Asset_analysis['IC_chg'] = []
    Asset_analysis['short_equity_ic'] = []
    Asset_analysis['daily_profit_ic'] = []
    Asset_analysis['daily_profit_ic_strabp'] = []
    Asset_analysis['accumulate_equity_ic'] = []
    Asset_analysis['retracement_ic'] = []
    Asset_analysis['free_cash_ic'] = []
    # IH
    Asset_analysis['hold_chg_ih'] = []
    Asset_analysis['long_equity_ih'] = []
    Asset_analysis['IH_chg'] = []
    Asset_analysis['short_equity_ih'] = []
    Asset_analysis['daily_profit_ih'] = []
    Asset_analysis['daily_profit_ih_strabp'] = []
    Asset_analysis['accumulate_equity_ih'] = []
    Asset_analysis['retracement_ih'] = []
    Asset_analysis['free_cash_ih'] = []
    # 统计换手率和成本
    Turnover_analysis = {}
    Turnover_analysis['trade_date'] = []
    Turnover_analysis['turnover_rate_if'] = []
    Turnover_analysis['trade_cost_if'] = []
    Turnover_analysis['turnover_rate_ic'] = []
    Turnover_analysis['trade_cost_ic'] = []
    Turnover_analysis['turnover_rate_ih'] = []
    Turnover_analysis['trade_cost_ih'] = []
    Turnover_analysis['behold_size'] = []
    Turnover_analysis['turnover_rate_long'] = []
    Turnover_analysis['trade_cost_long'] = []
    # 统计不对冲的策略表现
    onlyLong_analysis = {}
    onlyLong_analysis['trade_date'] = []
    onlyLong_analysis['long_stock_equity'] = []
    onlyLong_analysis['long_hold_equity'] = []
    onlyLong_analysis['long_spare_money'] = []
    onlyLong_analysis['retracement_long'] = []
    onlyLong_analysis['short_if_equity'] = []
    onlyLong_analysis['short_ic_equity'] = []
    onlyLong_analysis['short_ih_equity'] = []
    onlyLong_analysis['excess_if'] = []
    onlyLong_analysis['excess_ic'] = []
    onlyLong_analysis['excess_ih'] = []

    # 遍历换仓日期
    for i in range(0, len(shift_trade_date)):
        if shift_trade_date[i] >= end_date:
            break
        if i==0:
            Asset_analysis['accumulate_equity_if'].append(1)
            Asset_analysis['accumulate_equity_ic'].append(1)
            Asset_analysis['accumulate_equity_ih'].append(1)
            last_buy_stocks = []
            last_buy_weight = []
            onlyLong_analysis['long_stock_equity'].append(1)
            onlyLong_analysis['short_if_equity'].append(1)
            onlyLong_analysis['short_ic_equity'].append(1)
            onlyLong_analysis['short_ih_equity'].append(1)

            free_money_if = (1 / (1+deposit_if*beta)) * (buycost_rate+impactcost_rate) * 1.1
            init_accumulate_equity_if = (1 - free_money_if) / (1+deposit_if*beta)
            free_money_ic = (1 / (1+deposit_ic*beta)) * (buycost_rate+impactcost_rate) * 1.1
            init_accumulate_equity_ic = (1 - free_money_ic) / (1+deposit_ic*beta)
            free_money_ih = (1 / (1+deposit_ih*beta)) * (buycost_rate+impactcost_rate) * 1.1
            init_accumulate_equity_ih = (1 - free_money_ih) / (1+deposit_ih*beta)

            onlylong_spare_money = 1 * (buycost_rate+impactcost_rate)
            onlylong_stock_equity = 1 - onlylong_spare_money
            onlylong_if_equity = onlyLong_analysis['short_if_equity'][-1]
            onlylong_spare_money_if = 0
            onlylong_ic_equity = onlyLong_analysis['short_ic_equity'][-1]
            onlylong_spare_money_ic = 0
            onlylong_ih_equity = onlyLong_analysis['short_ih_equity'][-1]
            onlylong_spare_money_ih = 0

        # 初始化净值，换仓时重新分配两边的资金比例
        if i != 0:
            if interest_mode == 'danli':
                temp_if = (Asset_analysis['long_equity_if'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_if'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_if*beta))
                temp_if = temp_if / (1 + (buycost_rate+impactcost_rate) / (1+deposit_if*beta))
                if Asset_analysis['accumulate_equity_if'][-1] - 1 > temp_if:
                    init_accumulate_equity_if = 1 / (1+deposit_if*beta)
                    free_money_if = Asset_analysis['accumulate_equity_if'][-1] - 1
                else:
                    free_money_if = temp_if
                    init_accumulate_equity_if = (Asset_analysis['accumulate_equity_if'][-1] - free_money_if) / (1+deposit_if*beta)

                temp_ic = (Asset_analysis['long_equity_ic'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_ic'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_ic*beta))
                temp_ic = temp_ic / (1 + (buycost_rate+impactcost_rate) / (1+deposit_ic*beta))
                if Asset_analysis['accumulate_equity_ic'][-1] - 1 > temp_ic:
                    init_accumulate_equity_ic = 1 / (1+deposit_ic*beta)
                    free_money_ic = Asset_analysis['accumulate_equity_ic'][-1] - 1
                else:
                    free_money_ic = temp_ic
                    init_accumulate_equity_ic = (Asset_analysis['accumulate_equity_ic'][-1] - free_money_ic) / (1+deposit_ic*beta)

                temp_ih = (Asset_analysis['long_equity_ih'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_ih'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_ih*beta))
                temp_ih = temp_ih / (1 + (buycost_rate+impactcost_rate) / (1+deposit_ih*beta))
                if Asset_analysis['accumulate_equity_ih'][-1] - 1 > temp_ih:
                    init_accumulate_equity_ih = 1 / (1+deposit_ih*beta)
                    free_money_ih = Asset_analysis['accumulate_equity_ih'][-1] - 1
                else:
                    free_money_ih = temp_ih
                    init_accumulate_equity_ih = (Asset_analysis['accumulate_equity_ih'][-1] - free_money_ih) / (1+deposit_ih*beta)

                # 统计不对冲的
                if onlyLong_analysis['long_stock_equity'][-1] - 1 > onlyLong_analysis['long_hold_equity'][-1] * (sellcost_rate+buycost_rate+2*impactcost_rate):
                    onlylong_stock_equity = 1
                    onlylong_spare_money = onlyLong_analysis['long_stock_equity'][-1] - 1
                else:
                    onlylong_spare_money = onlyLong_analysis['long_hold_equity'][-1] * (sellcost_rate+buycost_rate+2*impactcost_rate)
                    onlylong_stock_equity = onlyLong_analysis['long_stock_equity'][-1] - onlylong_spare_money
                onlylong_if_equity = onlyLong_analysis['short_if_equity'][-1]
                onlylong_spare_money_if = 0
                onlylong_ic_equity = onlyLong_analysis['short_ic_equity'][-1]
                onlylong_spare_money_ic = 0
                onlylong_ih_equity = onlyLong_analysis['short_ih_equity'][-1]
                onlylong_spare_money_ih = 0

            elif interest_mode == 'fuli':
                temp_if = (Asset_analysis['long_equity_if'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_if'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_if*beta))
                temp_if = temp_if / (1 + (buycost_rate+impactcost_rate) / (1+deposit_if*beta))
                free_money_if = temp_if
                init_accumulate_equity_if = (Asset_analysis['accumulate_equity_if'][-1] - free_money_if) / (1+deposit_if*beta)

                temp_ic = (Asset_analysis['long_equity_ic'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_ic'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_ic*beta))
                temp_ic = temp_ic / (1 + (buycost_rate+impactcost_rate) / (1+deposit_ic*beta))
                free_money_ic = temp_ic
                init_accumulate_equity_ic = (Asset_analysis['accumulate_equity_ic'][-1] - free_money_ic) / (1+deposit_ic*beta)

                temp_ih = (Asset_analysis['long_equity_ih'][-1] * (sellcost_rate+impactcost_rate) + Asset_analysis['accumulate_equity_ih'][-1] * (buycost_rate+impactcost_rate) / (1+deposit_ih*beta))
                temp_ih = temp_ih / (1 + (buycost_rate+impactcost_rate) / (1+deposit_ih*beta))
                free_money_ih = temp_ih
                init_accumulate_equity_ih = (Asset_analysis['accumulate_equity_ih'][-1] - free_money_ih) / (1+deposit_ih*beta)
                # init_accumulate_equity_if = Asset_analysis['accumulate_equity_if'][-1] / (1+deposit_if*beta)
                # init_accumulate_equity_ic = Asset_analysis['accumulate_equity_ic'][-1] / (1+deposit_ic*beta)
                # init_accumulate_equity_ih = Asset_analysis['accumulate_equity_ih'][-1] / (1+deposit_ih*beta)
                # free_money_if = 0
                # free_money_ic = 0
                # free_money_ih = 0
                # 统计不对冲的
                onlylong_spare_money = onlyLong_analysis['long_hold_equity'][-1] * (sellcost_rate+buycost_rate+2*impactcost_rate)
                onlylong_stock_equity = onlyLong_analysis['long_stock_equity'][-1] - onlylong_spare_money
                onlylong_if_equity = onlyLong_analysis['short_if_equity'][-1]
                onlylong_spare_money_if = 0
                onlylong_ic_equity = onlyLong_analysis['short_ic_equity'][-1]
                onlylong_spare_money_ic = 0
                onlylong_ih_equity = onlyLong_analysis['short_ih_equity'][-1]
                onlylong_spare_money_ih = 0
            else:
                print 'Mode Error!!'
                os._exit(0)

        # 多头累计净值
        long_equity_if = init_accumulate_equity_if
        long_equity_ic = init_accumulate_equity_ic
        long_equity_ih = init_accumulate_equity_ih

        # 空头初始净值
        short_equity_if = init_accumulate_equity_if * beta * deposit_if
        short_equity_ic = init_accumulate_equity_ic * beta * deposit_ic
        short_equity_ih = init_accumulate_equity_ih * beta * deposit_ih

        # 将股指空头端权益初始化
        if_equity = init_accumulate_equity_if
        ic_equity = init_accumulate_equity_ic
        ih_equity = init_accumulate_equity_ih

        # 判断是否为最后一次持仓
        tday = shift_trade_date[i]
        if i != len(shift_trade_date) - 1:
            ntday = shift_trade_date[i+1]
        else:
            ntday = None

        # 读取当月持仓文件
        if tday not in all_trade_date:
            print tday, 'is not trade date!!'
        if fn[-4:] == 'impr':
            hold_stocks_df = pd.read_excel('hold_improve\\'+hold_file_dict[tday], index_col = None)
        else:
            if hold_file_dict[tday][-3:] == 'xls':
                hold_stocks_df = pd.read_excel('hold_stocks\\'+hold_file_dict[tday], index_col = None)
            elif hold_file_dict[tday][-3:] == 'csv':
                hold_stocks_df = pd.read_csv('hold_stocks\\'+hold_file_dict[tday], index_col = None)

        buy_stocks = hold_stocks_df['stock'].tolist()
        buy_weight = hold_stocks_df['weight'].tolist()
        # 检验权重分配
        if sum(buy_weight) < 99 or sum(buy_weight) > 101:
            print shift_trade_date[i], 'hold stocks **weight** wrong!!', sum(buy_weight)
            os._exit(0)

        # 获取持持仓时间段内的交易日
        hold_time_trade_day = []
        if ntday != None:
            sid = all_trade_date.index(tday)+1
            if ntday < end_date:
                eid = all_trade_date.index(ntday)+1
            else:
                eid = all_trade_date.index(end_date)
            hold_time_trade_day = all_trade_date[sid:eid+1]
        else:
            sid = all_trade_date.index(tday)+1
            eid = all_trade_date.index(end_date)
            hold_time_trade_day = all_trade_date[sid:eid+1]
        print
        print hold_time_trade_day

        # 使用vwap判断股票是否停牌
        stocks_vwap = stocks_vwap_df.loc[hold_time_trade_day[0]]
        last_trade_date = tday
        # last_trade_date = all_trade_date[all_trade_date.index(hold_time_trade_day[0])-1]
        cancel_weight = 0
        cancel_id = []
        for s in range(0, len(buy_stocks)):
            if math.isnan(stocks_vwap[buy_stocks[s]]):
                print shift_trade_date[i], buy_stocks[s], 'stock suspended in', hold_time_trade_day[0], s
                cancel_weight += buy_weight[s]
                cancel_id.append(s)
            elif stocks_vwap[buy_stocks[s]] / stocks_data_df[buy_stocks[s]].loc[last_trade_date] > 1.09:
                print shift_trade_date[i], buy_stocks[s], 'stock limit up in', hold_time_trade_day[0], last_trade_date, s
                cancel_weight += buy_weight[s]
                cancel_id.append(s)
        if len(cancel_id) != 0:
            print shift_trade_date[i], 'sholud cancel stocks num:', len(cancel_id)
        cancel_id.sort(reverse=True)
        for s in cancel_id:
            del buy_stocks[s]
            del buy_weight[s]
        # print sum(buy_weight),
        for s in range(0, len(buy_stocks)):
            buy_weight[s] += float(cancel_weight) / len(buy_stocks)
        # print sum(buy_weight)
        if sum(buy_weight) < 99 or sum(buy_weight) > 101:
            print shift_trade_date[i], cancel_weight,  'hold stocks **weight** error after suspend stocks cal!!', sum(buy_weight)
            os._exit(0)
        print

        # 回测开始的时候初始化
        if i==0:
            Asset_analysis['trade_date'].append(hold_time_trade_day[0])
            Turnover_analysis['behold_size'].append(0)
            # IF
            Asset_analysis['hold_chg_if'].append(0)
            Asset_analysis['long_equity_if'].append(long_equity_if)
            Asset_analysis['IF_chg'].append(0)
            Asset_analysis['short_equity_if'].append(short_equity_if)
            Asset_analysis['daily_profit_if'].append(0)
            Asset_analysis['daily_profit_if_strabp'].append(0)
            Asset_analysis['retracement_if'].append(0)
            # IC
            Asset_analysis['hold_chg_ic'].append(0)
            Asset_analysis['long_equity_ic'].append(long_equity_ic)
            Asset_analysis['IC_chg'].append(0)
            Asset_analysis['short_equity_ic'].append(short_equity_ic)
            Asset_analysis['daily_profit_ic'].append(0)
            Asset_analysis['daily_profit_ic_strabp'].append(0)
            Asset_analysis['retracement_ic'].append(0)
            # IH
            Asset_analysis['hold_chg_ih'].append(0)
            Asset_analysis['long_equity_ih'].append(long_equity_ih)
            Asset_analysis['IH_chg'].append(0)
            Asset_analysis['short_equity_ih'].append(short_equity_ih)
            Asset_analysis['daily_profit_ih'].append(0)
            Asset_analysis['daily_profit_ih_strabp'].append(0)
            Asset_analysis['retracement_ih'].append(0)

            onlyLong_analysis['long_hold_equity'].append(onlylong_stock_equity)
            onlyLong_analysis['retracement_long'].append(0)
            onlyLong_analysis['trade_date'].append(hold_time_trade_day[0])
            onlyLong_analysis['excess_if'].append(0)
            onlyLong_analysis['excess_ic'].append(0)
            onlyLong_analysis['excess_ih'].append(0)

        # 计算当期换手率和换仓成本
        Turnover_analysis['trade_date'].append(hold_time_trade_day[0])
        same_equity_if = 0
        same_equity_ic = 0
        same_equity_ih = 0
        same_equity_long = 0
        for sss in range(0, len(buy_stocks)):
            if buy_stocks[sss] in last_buy_stocks:
                idx = last_buy_stocks.index(buy_stocks[sss])

                if Asset_analysis['long_equity_if'][-1] * last_buy_weight[idx] < long_equity_if * buy_weight[sss]:
                    same_equity_if += Asset_analysis['long_equity_if'][-1] * last_buy_weight[idx] / 100.0
                else:
                    same_equity_if += long_equity_if * buy_weight[sss] / 100.0

                if Asset_analysis['long_equity_ic'][-1] * last_buy_weight[idx] < long_equity_ic * buy_weight[sss]:
                    same_equity_ic += Asset_analysis['long_equity_ic'][-1] * last_buy_weight[idx] / 100.0
                else:
                    same_equity_ic += long_equity_ic * buy_weight[sss] / 100.0

                if Asset_analysis['long_equity_ih'][-1] * last_buy_weight[idx] < long_equity_ih * buy_weight[sss]:
                    same_equity_ih += Asset_analysis['long_equity_ih'][-1] * last_buy_weight[idx] / 100.0
                else:
                    same_equity_ih += long_equity_ih * buy_weight[sss] / 100.0

                if onlyLong_analysis['long_hold_equity'][-1] * last_buy_weight[idx] < onlylong_stock_equity * buy_weight[sss]:
                    same_equity_long += onlyLong_analysis['long_hold_equity'][-1] * last_buy_weight[idx] / 100.0
                else:
                    same_equity_long += onlylong_stock_equity * buy_weight[sss] / 100.0
            # print same_equity_if, same_equity_ic, same_equity_ih
        # if i != 0:
        # 	os._exit(0)

        sell_equity_if = Asset_analysis['long_equity_if'][-1] - same_equity_if
        buy_equity_if = long_equity_if - same_equity_if
        turnover_rate_if = max(sell_equity_if, buy_equity_if) / ((Asset_analysis['long_equity_if'][-1] + long_equity_if) / 2)
        Turnover_analysis['turnover_rate_if'].append(turnover_rate_if)
        if i == 0:
            Turnover_analysis['trade_cost_if'].append(buy_equity_if*(buycost_rate+impactcost_rate))
        else:
            Turnover_analysis['trade_cost_if'].append(sell_equity_if*(sellcost_rate+impactcost_rate) + buy_equity_if*(buycost_rate+impactcost_rate))

        sell_equity_ic = Asset_analysis['long_equity_ic'][-1] - same_equity_ic
        buy_equity_ic = long_equity_ic - same_equity_ic
        turnover_rate_ic = max(sell_equity_ic, buy_equity_ic) / ((Asset_analysis['long_equity_ic'][-1] + long_equity_ic) / 2)
        Turnover_analysis['turnover_rate_ic'].append(turnover_rate_ic)
        if i == 0:
            Turnover_analysis['trade_cost_ic'].append(buy_equity_ic*(buycost_rate+impactcost_rate))
        else:
            Turnover_analysis['trade_cost_ic'].append(sell_equity_ic*(sellcost_rate+impactcost_rate) + buy_equity_ic*(buycost_rate+impactcost_rate))

        sell_equity_ih = Asset_analysis['long_equity_ih'][-1] - same_equity_ih
        buy_equity_ih = long_equity_ih - same_equity_ih
        turnover_rate_ih = max(sell_equity_ih, buy_equity_ih) / ((Asset_analysis['long_equity_ih'][-1] + long_equity_ih) / 2)
        Turnover_analysis['turnover_rate_ih'].append(turnover_rate_ih)
        if i == 0:
            Turnover_analysis['trade_cost_ih'].append(buy_equity_ih*(buycost_rate+impactcost_rate))
        else:
            Turnover_analysis['trade_cost_ih'].append(sell_equity_ih*(sellcost_rate+impactcost_rate) + buy_equity_ih*(buycost_rate+impactcost_rate))

        sell_equity_long = onlyLong_analysis['long_hold_equity'][-1] - same_equity_long
        buy_equity_long = onlylong_stock_equity - same_equity_long
        turnover_rate_long = max(sell_equity_long, buy_equity_long) / ((onlyLong_analysis['long_hold_equity'][-1] + onlylong_stock_equity) / 2)
        Turnover_analysis['turnover_rate_long'].append(turnover_rate_long)
        if i == 0:
            Turnover_analysis['trade_cost_long'].append(buy_equity_long * (buycost_rate+impactcost_rate))
        else:
            Turnover_analysis['trade_cost_long'].append(sell_equity_long * (sellcost_rate+impactcost_rate) + buy_equity_long * (buycost_rate+impactcost_rate))

        # 扣除手续费、冲击成本
        if cost_mode:
            tag = False
            onlylong_spare_money -= Turnover_analysis['trade_cost_long'][-1]
            free_money_if -= Turnover_analysis['trade_cost_if'][-1]
            free_money_ic -= Turnover_analysis['trade_cost_ic'][-1]
            free_money_ih -= Turnover_analysis['trade_cost_ih'][-1]
            if onlylong_spare_money < 0:
                print 'onlylong_spare_money < 0 !!!!!!!!!!!!!!!!!!'
                tag = True
            if free_money_if < 0:
                print 'free_money_if < 0 !!!!!!!!!!!!!!!!!!', free_money_if, Turnover_analysis['trade_cost_if'][-1]
                tag = True
            if free_money_ic < 0:
                print 'free_money_ic < 0 !!!!!!!!!!!!!!!!!!', free_money_ic, Turnover_analysis['trade_cost_ic'][-1]
                tag = True
            if free_money_ih < 0:
                print 'free_money_ih < 0 !!!!!!!!!!!!!!!!!!', free_money_ih, Turnover_analysis['trade_cost_ih'][-1]
                tag = True
            if tag == True:
                os._exit(0)

        if i == 0:
            Asset_analysis['free_cash_if'].append(free_money_if)
            Asset_analysis['free_cash_ic'].append(free_money_ic)
            Asset_analysis['free_cash_ih'].append(free_money_ih)
            onlyLong_analysis['long_spare_money'].append(onlylong_spare_money)

        # 回测计算主体开始-----------------------------------------------
        # 遍历持仓周期内的每个交易日
        for t in range(1, len(hold_time_trade_day)):
            Asset_analysis['trade_date'].append(hold_time_trade_day[t])
            onlyLong_analysis['trade_date'].append(hold_time_trade_day[t])

            buy_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t-1]].values
            sell_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t]].values
            # # 期初期末用vwap交易，期间追踪用close价
            # if t == 1:
            # 	buy_price_data = stocks_vwap_df[buy_stocks].loc[hold_time_trade_day[t-1]].values
            # 	# buy_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t-1]].values
            # else:
            # 	buy_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t-1]].values
            # if t == len(hold_time_trade_day) - 1:
            # 	# sell_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t]].values
            # 	sell_price_data = stocks_vwap_df[buy_stocks].loc[hold_time_trade_day[t]].values
            # 	for v in range(0, len(sell_price_data)):
            # 		if math.isnan(sell_price_data[v]):
            # 			sell_price_data[v] = stocks_data_df[buy_stocks[v]].loc[hold_time_trade_day[t]]
            # 			for d_id in range(all_trade_date.index(hold_time_trade_day[t])+1, len(all_trade_date)):
            # 				if not math.isnan(stocks_vwap_df[buy_stocks[v]].loc[all_trade_date[d_id]]):
            # 					sell_price_data[v] = stocks_vwap_df[buy_stocks[v]].loc[all_trade_date[d_id]]
            # 					break
            # else:
            # 	sell_price_data = stocks_data_df[buy_stocks].loc[hold_time_trade_day[t]].values

            if t == 1:
                start_price = buy_price_data
                buy_weight_adj = np.array(buy_weight)
            else:
                buy_weight_adj = buy_price_data * buy_weight / start_price
                buy_weight_adj = buy_weight_adj / sum(buy_weight_adj) * 100.0

            # 存下当期最后的持仓股票和权重，方便计算换手率
            if t == len(hold_time_trade_day) - 1:
                last_buy_stocks = buy_stocks
                last_buy_weight = sell_price_data * buy_weight / start_price
                last_buy_weight = last_buy_weight / sum(last_buy_weight) * 100.0


            # 计算持仓的浮动涨跌
            hold_chg = sum((sell_price_data / buy_price_data - 1) * (buy_weight_adj / 100.0))
            long_equity_if *= (hold_chg + 1)
            long_equity_ic *= (hold_chg + 1)
            long_equity_ih *= (hold_chg + 1)
            onlylong_stock_equity *= (hold_chg + 1)
            onlyLong_analysis['long_stock_equity'].append(onlylong_stock_equity + onlylong_spare_money)
            onlyLong_analysis['long_hold_equity'].append(onlylong_stock_equity)
            onlyLong_analysis['long_spare_money'].append(onlylong_spare_money)
            onlyLong_analysis['retracement_long'].append(onlyLong_analysis['long_stock_equity'][-1] - max(onlyLong_analysis['long_stock_equity']))

            # 沪深300
            Asset_analysis['hold_chg_if'].append(hold_chg)
            Asset_analysis['long_equity_if'].append(long_equity_if)
            # 股指期货
            index_chg = index_data_df['000300.SH'].loc[hold_time_trade_day[t]] / index_data_df['000300.SH'].loc[hold_time_trade_day[t-1]] - 1
            Asset_analysis['IF_chg'].append(index_chg)
            if_equity *= (index_chg + 1)
            onlylong_if_equity *= (index_chg + 1)
            onlyLong_analysis['short_if_equity'].append(onlylong_if_equity + onlylong_spare_money_if)
            onlyLong_analysis['excess_if'].append(onlyLong_analysis['long_stock_equity'][-1] - onlyLong_analysis['short_if_equity'][-1])
            Asset_analysis['short_equity_if'].append(short_equity_if - (if_equity - init_accumulate_equity_if))
            Asset_analysis['daily_profit_if'].append((Asset_analysis['long_equity_if'][-1] + Asset_analysis['short_equity_if'][-1]) / (Asset_analysis['accumulate_equity_if'][-1] - free_money_if) - 1)
            Asset_analysis['daily_profit_if_strabp'].append(hold_chg - index_chg)
            Asset_analysis['accumulate_equity_if'].append(free_money_if + Asset_analysis['long_equity_if'][-1] + Asset_analysis['short_equity_if'][-1])
            Asset_analysis['retracement_if'].append(Asset_analysis['accumulate_equity_if'][-1] - max(Asset_analysis['accumulate_equity_if']))
            Asset_analysis['free_cash_if'].append(free_money_if)

            # 中证500
            Asset_analysis['hold_chg_ic'].append(hold_chg)
            Asset_analysis['long_equity_ic'].append(long_equity_ic)
            # 股指期货
            index_chg = index_data_df['000905.SH'].loc[hold_time_trade_day[t]] / index_data_df['000905.SH'].loc[hold_time_trade_day[t-1]] - 1
            Asset_analysis['IC_chg'].append(index_chg)
            ic_equity *= (index_chg + 1)
            onlylong_ic_equity *= (index_chg + 1)
            onlyLong_analysis['short_ic_equity'].append(onlylong_ic_equity + onlylong_spare_money_ic)
            onlyLong_analysis['excess_ic'].append(onlyLong_analysis['long_stock_equity'][-1] - onlyLong_analysis['short_ic_equity'][-1])
            Asset_analysis['short_equity_ic'].append(short_equity_ic - (ic_equity - init_accumulate_equity_ic))
            Asset_analysis['daily_profit_ic'].append((Asset_analysis['long_equity_ic'][-1] + Asset_analysis['short_equity_ic'][-1]) / (Asset_analysis['accumulate_equity_ic'][-1] - free_money_ic) - 1)
            Asset_analysis['daily_profit_ic_strabp'].append(hold_chg - index_chg)
            Asset_analysis['accumulate_equity_ic'].append(free_money_ic + Asset_analysis['long_equity_ic'][-1] + Asset_analysis['short_equity_ic'][-1])
            Asset_analysis['retracement_ic'].append(Asset_analysis['accumulate_equity_ic'][-1] - max(Asset_analysis['accumulate_equity_ic']))
            Asset_analysis['free_cash_ic'].append(free_money_ic)

            # 上证50
            Asset_analysis['hold_chg_ih'].append(hold_chg)
            Asset_analysis['long_equity_ih'].append(long_equity_ih)
            # 股指期货
            index_chg = index_data_df['000016.SH'].loc[hold_time_trade_day[t]] / index_data_df['000016.SH'].loc[hold_time_trade_day[t-1]] - 1
            Asset_analysis['IH_chg'].append(index_chg)
            ih_equity *= (index_chg + 1)
            onlylong_ih_equity *= (index_chg + 1)
            onlyLong_analysis['short_ih_equity'].append(onlylong_ih_equity + onlylong_spare_money_ih)
            onlyLong_analysis['excess_ih'].append(onlyLong_analysis['long_stock_equity'][-1] - onlyLong_analysis['short_ih_equity'][-1])
            Asset_analysis['short_equity_ih'].append(short_equity_ih - (ih_equity - init_accumulate_equity_ih))
            Asset_analysis['daily_profit_ih'].append((Asset_analysis['long_equity_ih'][-1] + Asset_analysis['short_equity_ih'][-1]) / (Asset_analysis['accumulate_equity_ih'][-1] - free_money_ih) - 1)
            Asset_analysis['daily_profit_ih_strabp'].append(hold_chg - index_chg)
            Asset_analysis['accumulate_equity_ih'].append(free_money_ih + Asset_analysis['long_equity_ih'][-1] + Asset_analysis['short_equity_ih'][-1])
            Asset_analysis['retracement_ih'].append(Asset_analysis['accumulate_equity_ih'][-1] - max(Asset_analysis['accumulate_equity_ih']))
            Asset_analysis['free_cash_ih'].append(free_money_ih)

            # 计算每天可容纳资金量
            amt_data = stocks_amt_df[buy_stocks].loc[hold_time_trade_day[t]].values
            behold_money = (amt_data * 0.1) / (buy_weight_adj / 100).tolist()
            comb = zip(behold_money, buy_weight_adj)
            comb.sort(key=lambda x:x[0])
            temp_weight = 0
            temp_bhmoney = []
            for bh in range(0, len(comb)):
                if comb[bh][0] == 0:
                    continue
                temp_weight += comb[bh][1]
                temp_bhmoney.append(comb[bh][0])
                if temp_weight > 10:
                    break
            Turnover_analysis['behold_size'].append(sum(temp_bhmoney) / len(temp_bhmoney))



    xls = xlwt.Workbook()
    sheet_if = xls.add_sheet(u"对沪深300")
    sheet_ic = xls.add_sheet(u"对中证500")
    sheet_ih = xls.add_sheet(u"对上证50")

    sheet_if.write(0, 0, u'交易日期')
    sheet_if.write(0, 1, u'当日持仓涨跌幅(%)')
    sheet_if.write(0, 2, u'当日多头净值')
    sheet_if.write(0, 3, u'当日沪深300涨跌幅(%)')
    sheet_if.write(0, 4, u'当日空头净值')
    sheet_if.write(0, 5, u'当日账户利润(BP)')
    sheet_if.write(0, 6, u'当日策略利润(BP)')
    sheet_if.write(0, 8, u'累计净值')
    sheet_if.write(0, 9, u'回撤')
    sheet_if.write(0, 10, u'空余资金')
    sheet_if.write(0, 11, u'同期上证指数')
    sheet_if.write(0, 12, u'同期深证指数')
    sheet_if.write(0, 13, u'同期创业板指数')
    sheet_if.write(0, 14, u'同期沪深300指数')
    sheet_if.write(0, 15, u'同期中证500指数')
    sheet_if.write(0, 16, u'同期上证50指数')

    sheet_ic.write(0, 0, u'交易日期')
    sheet_ic.write(0, 1, u'当日持仓涨跌幅(%)')
    sheet_ic.write(0, 2, u'当日多头净值')
    sheet_ic.write(0, 3, u'当日中证500涨跌幅(%)')
    sheet_ic.write(0, 4, u'当日空头净值')
    sheet_ic.write(0, 5, u'当日账户利润(BP)')
    sheet_ic.write(0, 6, u'当日策略利润(BP)')
    sheet_ic.write(0, 8, u'累计净值')
    sheet_ic.write(0, 9, u'回撤')
    sheet_ic.write(0, 10, u'空余资金')
    sheet_ic.write(0, 11, u'同期上证指数')
    sheet_ic.write(0, 12, u'同期深证指数')
    sheet_ic.write(0, 13, u'同期创业板指数')
    sheet_ic.write(0, 14, u'同期沪深300指数')
    sheet_ic.write(0, 15, u'同期中证500指数')
    sheet_ic.write(0, 16, u'同期上证50指数')

    sheet_ih.write(0, 0, u'交易日期')
    sheet_ih.write(0, 1, u'当日持仓涨跌幅(%)')
    sheet_ih.write(0, 2, u'当日多头净值')
    sheet_ih.write(0, 3, u'当日上证50涨跌幅(%)')
    sheet_ih.write(0, 4, u'当日空头净值')
    sheet_ih.write(0, 5, u'当日账户利润(BP)')
    sheet_ih.write(0, 6, u'当日策略利润(BP)')
    sheet_ih.write(0, 8, u'累计净值')
    sheet_ih.write(0, 9, u'回撤')
    sheet_ih.write(0, 10, u'空余资金')
    sheet_ih.write(0, 11, u'同期上证指数')
    sheet_ih.write(0, 12, u'同期深证指数')
    sheet_ih.write(0, 13, u'同期创业板指数')
    sheet_ih.write(0, 14, u'同期沪深300指数')
    sheet_ih.write(0, 15, u'同期中证500指数')
    sheet_ih.write(0, 16, u'同期上证50指数')

    win_if = 0
    win_ic = 0
    win_ih = 0
    for i in range(0, len(Asset_analysis['trade_date'])):
        # 沪深300
        sheet_if.write(i+1, 0, Asset_analysis['trade_date'][i])
        sheet_if.write(i+1, 1, str(round(Asset_analysis['hold_chg_if'][i] * 100, 2)) + '%')
        sheet_if.write(i+1, 2, round(Asset_analysis['long_equity_if'][i], 4))
        sheet_if.write(i+1, 3, str(round(Asset_analysis['IF_chg'][i] * 100, 2)) + '%')
        sheet_if.write(i+1, 4, round(Asset_analysis['short_equity_if'][i], 4))
        sheet_if.write(i+1, 5, round(Asset_analysis['daily_profit_if'][i] * 10000, 2))
        sheet_if.write(i+1, 6, round(Asset_analysis['daily_profit_if_strabp'][i] * 10000, 2))
        if Asset_analysis['daily_profit_if'][i] > 0:
            win_if += 1

        sheet_if.write(i+1, 7, Asset_analysis['trade_date'][i])
        sheet_if.write(i+1, 8, Asset_analysis['accumulate_equity_if'][i])
        sheet_if.write(i+1, 9, Asset_analysis['retracement_if'][i])
        sheet_if.write(i+1, 10, Asset_analysis['free_cash_if'][i])

        index_data = index_data_df.loc[Asset_analysis['trade_date'][i]]
        sheet_if.write(i+1, 11, index_data['000001.SH'])
        sheet_if.write(i+1, 12, index_data['399001.SZ'])
        sheet_if.write(i+1, 13, index_data['399006.SZ'])
        sheet_if.write(i+1, 14, index_data['000300.SH'])
        sheet_if.write(i+1, 15, index_data['000905.SH'])
        sheet_if.write(i+1, 16, index_data['000016.SH'])

        # 中证500
        sheet_ic.write(i+1, 0, Asset_analysis['trade_date'][i])
        sheet_ic.write(i+1, 1, str(round(Asset_analysis['hold_chg_ic'][i] * 100, 2)) + '%')
        sheet_ic.write(i+1, 2, round(Asset_analysis['long_equity_ic'][i], 4))
        sheet_ic.write(i+1, 3, str(round(Asset_analysis['IC_chg'][i] * 100, 2)) + '%')
        sheet_ic.write(i+1, 4, round(Asset_analysis['short_equity_ic'][i], 4))
        sheet_ic.write(i+1, 5, round(Asset_analysis['daily_profit_ic'][i] * 10000, 2))
        sheet_ic.write(i+1, 6, round(Asset_analysis['daily_profit_ic_strabp'][i] * 10000, 2))
        if Asset_analysis['daily_profit_ic'][i] > 0:
            win_ic += 1

        sheet_ic.write(i+1, 7, Asset_analysis['trade_date'][i])
        sheet_ic.write(i+1, 8, Asset_analysis['accumulate_equity_ic'][i])
        sheet_ic.write(i+1, 9, Asset_analysis['retracement_ic'][i])
        sheet_ic.write(i+1, 10, Asset_analysis['free_cash_ic'][i])

        index_data = index_data_df.loc[Asset_analysis['trade_date'][i]]
        sheet_ic.write(i+1, 11, index_data['000001.SH'])
        sheet_ic.write(i+1, 12, index_data['399001.SZ'])
        sheet_ic.write(i+1, 13, index_data['399006.SZ'])
        sheet_ic.write(i+1, 14, index_data['000300.SH'])
        sheet_ic.write(i+1, 15, index_data['000905.SH'])
        sheet_ic.write(i+1, 16, index_data['000016.SH'])

        # 上证50
        sheet_ih.write(i+1, 0, Asset_analysis['trade_date'][i])
        sheet_ih.write(i+1, 1, str(round(Asset_analysis['hold_chg_ih'][i] * 100, 2)) + '%')
        sheet_ih.write(i+1, 2, round(Asset_analysis['long_equity_ih'][i], 4))
        sheet_ih.write(i+1, 3, str(round(Asset_analysis['IH_chg'][i] * 100, 2)) + '%')
        sheet_ih.write(i+1, 4, round(Asset_analysis['short_equity_ih'][i], 4))
        sheet_ih.write(i+1, 5, round(Asset_analysis['daily_profit_ih'][i] * 10000, 2))
        sheet_ih.write(i+1, 6, round(Asset_analysis['daily_profit_ih_strabp'][i] * 10000, 2))
        if Asset_analysis['daily_profit_ih'][i] > 0:
            win_ih += 1

        sheet_ih.write(i+1, 7, Asset_analysis['trade_date'][i])
        sheet_ih.write(i+1, 8, Asset_analysis['accumulate_equity_ih'][i])
        sheet_ih.write(i+1, 9, Asset_analysis['retracement_ih'][i])
        sheet_ih.write(i+1, 10, Asset_analysis['free_cash_ih'][i])

        index_data = index_data_df.loc[Asset_analysis['trade_date'][i]]
        sheet_ih.write(i+1, 11, index_data['000001.SH'])
        sheet_ih.write(i+1, 12, index_data['399001.SZ'])
        sheet_ih.write(i+1, 13, index_data['399006.SZ'])
        sheet_ih.write(i+1, 14, index_data['000300.SH'])
        sheet_ih.write(i+1, 15, index_data['000905.SH'])
        sheet_ih.write(i+1, 16, index_data['000016.SH'])

    sheet_if.write(0, 17, u'胜率')
    sheet_if.write(0, 18, str(100.0 * float(win_if) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_if.write(0, 19, u'最大回撤')
    sheet_if.write(0, 20, min(Asset_analysis['retracement_if']))
    sheet_if.write(0, 21, u'累计净值')
    sheet_if.write(0, 22, Asset_analysis['accumulate_equity_if'][-1])
    sheet_if.write(i+4, 0, u'胜率')
    sheet_if.write(i+4, 1, str(100.0 * float(win_if) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_if.write(i+4, 2, u'最大回撤')
    sheet_if.write(i+4, 3, min(Asset_analysis['retracement_if']))

    sheet_ic.write(0, 17, u'胜率')
    sheet_ic.write(0, 18, str(100.0 * float(win_ic) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_ic.write(0, 19, u'最大回撤')
    sheet_ic.write(0, 20, min(Asset_analysis['retracement_ic']))
    sheet_ic.write(0, 21, u'累计净值')
    sheet_ic.write(0, 22, Asset_analysis['accumulate_equity_ic'][-1])
    sheet_ic.write(i+4, 0, u'胜率')
    sheet_ic.write(i+4, 1, str(100.0 * float(win_ic) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_ic.write(i+4, 2, u'最大回撤')
    sheet_ic.write(i+4, 3, min(Asset_analysis['retracement_ic']))

    sheet_ih.write(0, 17, u'胜率')
    sheet_ih.write(0, 18, str(100.0 * float(win_ih) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_ih.write(0, 19, u'最大回撤')
    sheet_ih.write(0, 20, min(Asset_analysis['retracement_ih']))
    sheet_ih.write(0, 21, u'累计净值')
    sheet_ih.write(0, 22, Asset_analysis['accumulate_equity_ih'][-1])
    sheet_ih.write(i+4, 0, u'胜率')
    sheet_ih.write(i+4, 1, str(100.0 * float(win_ih) / len(Asset_analysis['trade_date']))[0:5] + '%')
    sheet_ih.write(i+4, 2, u'最大回撤')
    sheet_ih.write(i+4, 3, min(Asset_analysis['retracement_ih']))

    month_date = []
    for i in range(0, len(Asset_analysis['trade_date']) - 1):
        if int(Asset_analysis['trade_date'][i][5:7]) != int(Asset_analysis['trade_date'][i+1][5:7]):
            month_date.append(Asset_analysis['trade_date'][i+1])
    if Asset_analysis['trade_date'][-1] not in month_date:
        month_date.append(Asset_analysis['trade_date'][-1])

    sheet_if.write(3, 20, u'区间')
    sheet_if.write(3, 21, u'净值变化')
    sheet_if.write(3, 22, u'累计BP')

    sheet_ic.write(3, 20, u'区间')
    sheet_ic.write(3, 21, u'净值变化')
    sheet_ic.write(3, 22, u'累计BP')

    sheet_ih.write(3, 20, u'区间')
    sheet_ih.write(3, 21, u'净值变化')
    sheet_ih.write(3, 22, u'累计BP')

    # print month_date
    eid = Asset_analysis['trade_date'].index(month_date[0])
    sheet_if.write(4, 20, '~ ' + month_date[0])
    sheet_if.write(4, 21, Asset_analysis['accumulate_equity_if'][eid] - 1)
    sheet_if.write(4, 22, round(sum(Asset_analysis['daily_profit_if'][0:eid+1]) * 10000, 2))

    sheet_ic.write(4, 20, '~ ' + month_date[0])
    sheet_ic.write(4, 21, Asset_analysis['accumulate_equity_ic'][eid] - 1)
    sheet_ic.write(4, 22, round(sum(Asset_analysis['daily_profit_ic'][0:eid+1]) * 10000, 2))

    sheet_ih.write(4, 20, '~ ' + month_date[0])
    sheet_ih.write(4, 21, Asset_analysis['accumulate_equity_ih'][eid] - 1)
    sheet_ih.write(4, 22, round(sum(Asset_analysis['daily_profit_ih'][0:eid+1]) * 10000, 2))

    cnt = 4
    for i in range(1, len(month_date)):
        sid = Asset_analysis['trade_date'].index(month_date[i-1])
        eid = Asset_analysis['trade_date'].index(month_date[i])

        sheet_if.write(cnt+i, 20, month_date[i-1] + ' ~ ' + month_date[i])
        sheet_if.write(cnt+i, 21, Asset_analysis['accumulate_equity_if'][eid] - Asset_analysis['accumulate_equity_if'][sid])
        sheet_if.write(cnt+i, 22, round(sum(Asset_analysis['daily_profit_if'][sid+1:eid+1]) * 10000, 2))

        sheet_ic.write(cnt+i, 20, month_date[i-1] + ' ~ ' + month_date[i])
        sheet_ic.write(cnt+i, 21, Asset_analysis['accumulate_equity_ic'][eid] - Asset_analysis['accumulate_equity_ic'][sid])
        sheet_ic.write(cnt+i, 22, round(sum(Asset_analysis['daily_profit_ic'][sid+1:eid+1]) * 10000, 2))

        sheet_ih.write(cnt+i, 20, month_date[i-1] + ' ~ ' + month_date[i])
        sheet_ih.write(cnt+i, 21, Asset_analysis['accumulate_equity_ih'][eid] - Asset_analysis['accumulate_equity_ih'][sid])
        sheet_ih.write(cnt+i, 22, round(sum(Asset_analysis['daily_profit_ih'][sid+1:eid+1]) * 10000, 2))

    # 写文件：换手统计
    sheet_turnover = xls.add_sheet(u'换仓成本统计')
    sheet_turnover.write(0, 0, u'换仓日期')
    sheet_turnover.write(0, 1, u'对沪深300换手率')
    sheet_turnover.write(0, 2, u'对沪深300换手成本')
    sheet_turnover.write(0, 4, u'累计换手成本')
    sheet_turnover.write(0, 5, u'原净值(对300)')
    sheet_turnover.write(0, 6, u'扣成本后净值(对300)')
    for i in range(0, len(Turnover_analysis['trade_date'])):
        sheet_turnover.write(i+1, 0, Turnover_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 1, Turnover_analysis['turnover_rate_if'][i])
        sheet_turnover.write(i+1, 2, Turnover_analysis['trade_cost_if'][i])
    accumulate_cost_if = 0
    for i in range(0, len(Asset_analysis['trade_date'])):
        if Asset_analysis['trade_date'][i] in Turnover_analysis['trade_date']:
            idx = Turnover_analysis['trade_date'].index(Asset_analysis['trade_date'][i])
            accumulate_cost_if += Turnover_analysis['trade_cost_if'][idx]
        sheet_turnover.write(i+1, 3, Asset_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 4, accumulate_cost_if)
        sheet_turnover.write(i+1, 5, Asset_analysis['accumulate_equity_if'][i])
        sheet_turnover.write(i+1, 6, Asset_analysis['accumulate_equity_if'][i] - accumulate_cost_if)

    sheet_turnover.write(0, 8, u'每日可容纳资金')
    for i in range(0, len(Asset_analysis['trade_date'])):
        sheet_turnover.write(i+1, 8, Turnover_analysis['behold_size'][i])

    sheet_turnover.write(0, 10, u'换仓日期')
    sheet_turnover.write(0, 11, u'对中证500换手率')
    sheet_turnover.write(0, 12, u'对中证500换手成本')
    sheet_turnover.write(0, 14, u'累计换手成本')
    sheet_turnover.write(0, 15, u'原净值(对500)')
    sheet_turnover.write(0, 16, u'扣成本后净值(对500)')
    for i in range(0, len(Turnover_analysis['trade_date'])):
        sheet_turnover.write(i+1, 10, Turnover_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 11, Turnover_analysis['turnover_rate_ic'][i])
        sheet_turnover.write(i+1, 12, Turnover_analysis['trade_cost_ic'][i])
    accumulate_cost_ic = 0
    for i in range(0, len(Asset_analysis['trade_date'])):
        if Asset_analysis['trade_date'][i] in Turnover_analysis['trade_date']:
            idx = Turnover_analysis['trade_date'].index(Asset_analysis['trade_date'][i])
            accumulate_cost_ic += Turnover_analysis['trade_cost_ic'][idx]
        sheet_turnover.write(i+1, 13, Asset_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 14, accumulate_cost_ic)
        sheet_turnover.write(i+1, 15, Asset_analysis['accumulate_equity_ic'][i])
        sheet_turnover.write(i+1, 16, Asset_analysis['accumulate_equity_ic'][i] - accumulate_cost_ic)

    sheet_turnover.write(0, 20, u'换仓日期')
    sheet_turnover.write(0, 21, u'对上证50换手率')
    sheet_turnover.write(0, 22, u'对上证50换手成本')
    sheet_turnover.write(0, 24, u'累计换手成本')
    sheet_turnover.write(0, 25, u'原净值(对50)')
    sheet_turnover.write(0, 26, u'扣成本后净值(对50)')
    for i in range(0, len(Turnover_analysis['trade_date'])):
        sheet_turnover.write(i+1, 20, Turnover_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 21, Turnover_analysis['turnover_rate_ih'][i])
        sheet_turnover.write(i+1, 22, Turnover_analysis['trade_cost_ih'][i])
    accumulate_cost_ih = 0
    for i in range(0, len(Asset_analysis['trade_date'])):
        if Asset_analysis['trade_date'][i] in Turnover_analysis['trade_date']:
            idx = Turnover_analysis['trade_date'].index(Asset_analysis['trade_date'][i])
            accumulate_cost_ih += Turnover_analysis['trade_cost_ih'][idx]
        sheet_turnover.write(i+1, 23, Asset_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 24, accumulate_cost_ih)
        sheet_turnover.write(i+1, 25, Asset_analysis['accumulate_equity_ih'][i])
        sheet_turnover.write(i+1, 26, Asset_analysis['accumulate_equity_ih'][i] - accumulate_cost_ih)

    sheet_turnover.write(0, 28, u'换仓日期')
    sheet_turnover.write(0, 29, u'单边换手率')
    sheet_turnover.write(0, 30, u'单边换手成本')
    for i in range(0, len(Turnover_analysis['trade_date'])):
        sheet_turnover.write(i+1, 28, Turnover_analysis['trade_date'][i])
        sheet_turnover.write(i+1, 29, Turnover_analysis['turnover_rate_long'][i])
        sheet_turnover.write(i+1, 30, Turnover_analysis['trade_cost_long'][i])

    # 输出策略单边情况
    sheet_onlyLong = xls.add_sheet(u'单边不对冲')
    sheet_onlyLong.write(0, 1, u'策略单边净值')
    sheet_onlyLong.write(0, 2, u'策略持仓净值')
    sheet_onlyLong.write(0, 3, u'策略空余资金')
    sheet_onlyLong.write(0, 4, u'回撤')
    sheet_onlyLong.write(0, 5, u'沪深300净值')
    sheet_onlyLong.write(0, 6, u'超额沪深300')
    sheet_onlyLong.write(0, 7, u'中证500净值')
    sheet_onlyLong.write(0, 8, u'超额中证500')
    sheet_onlyLong.write(0, 9, u'上证50净值')
    sheet_onlyLong.write(0, 10, u'超额上证50')
    win_long = 0
    onlylong_chg = [0]
    for i in range(0, len(onlyLong_analysis['trade_date'])):
        sheet_onlyLong.write(i+1, 0, onlyLong_analysis['trade_date'][i])
        sheet_onlyLong.write(i+1, 1, onlyLong_analysis['long_stock_equity'][i])
        if i != 0:
            chg_tmp = onlyLong_analysis['long_stock_equity'][i] / onlyLong_analysis['long_stock_equity'][i-1] - 1
            onlylong_chg.append(chg_tmp)
            if chg_tmp > 0:
                win_long += 1
        sheet_onlyLong.write(i+1, 2, onlyLong_analysis['long_hold_equity'][i])
        sheet_onlyLong.write(i+1, 3, onlyLong_analysis['long_spare_money'][i])
        sheet_onlyLong.write(i+1, 4, onlyLong_analysis['retracement_long'][i])
        sheet_onlyLong.write(i+1, 5, onlyLong_analysis['short_if_equity'][i])
        sheet_onlyLong.write(i+1, 6, onlyLong_analysis['excess_if'][i])
        sheet_onlyLong.write(i+1, 7, onlyLong_analysis['short_ic_equity'][i])
        sheet_onlyLong.write(i+1, 8, onlyLong_analysis['excess_ic'][i])
        sheet_onlyLong.write(i+1, 9, onlyLong_analysis['short_ih_equity'][i])
        sheet_onlyLong.write(i+1, 10, onlyLong_analysis['excess_ih'][i])
    sheet_onlyLong.write(0, 13, u'胜率')
    sheet_onlyLong.write(0, 14, str(100.0 * float(win_long) / len(onlyLong_analysis['trade_date']))[0:5] + '%')
    sheet_onlyLong.write(0, 15, u'最大回撤')
    sheet_onlyLong.write(0, 16, min(onlyLong_analysis['retracement_long']))

    xl = ['IF', 'IC', 'IH']
    Y = onlylong_chg
    for i in range(0, len(xl)):
        X = []
        for j in range(0, len(Asset_analysis[xl[i]+'_chg'])):
            X.append([Asset_analysis[xl[i]+'_chg'][j]])
        clf = linear_model.LinearRegression()
        try:
            clf.fit(X, Y)
        except Exception, e:
            print e
        sheet_onlyLong.write(i+2, 13, 'Beta_'+xl[i])
        sheet_onlyLong.write(i+2, 14, clf.coef_.tolist()[0])
        sheet_onlyLong.write(i+2, 15, 'Alpha_'+xl[i])
        sheet_onlyLong.write(i+2, 16, clf.intercept_)



    suffix = ''
    if interest_mode == 'danli':
        suffix += '_SimpInst'
    elif interest_mode == 'fuli':
        suffix += '_CompInst'
    if cost_mode:
        suffix += '_ConsiderCost'
    else:
        suffix += '_RemvCost'
    # 保存文件！！！！！
    xls.save('BT_Output/'+fn+suffix+'.xls')


if __name__ == '__main__':
    read_file('hold_stocks')
    filename = raw_input('plz input strategy name:  ')
    backTest(filename)
    # improve_hold_file_dict = modifyWeight(shift_trade_date, hold_file_dict)
    # backTest(shift_trade_date, improve_hold_file_dict, filename+'_impr')
