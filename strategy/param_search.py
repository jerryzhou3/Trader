# ！/usr/bin/env python
# encoding: utf-8
"""
@Author: Yeju Zhou
@File: param_search.py.py
@Time: 2022/5/14 16:39
@Describe: 寻找最优参数
"""

from moving_average import *


if __name__ == "__main__":
    code_list = ["000001.XSHE", "002466.XSHE", "002460.XSHE", "000762.XSHE"]
    for code in code_list:
        data = import_data_wrapper(code)
        # 参数：周期参数
        params = [5, 10, 20, 60, 120, 250]
        # 存放参数与收益
        res = []
        # 匹配并计算不同的周期参数对：5-10，5-20 …… 120-250
        for short in params:
            for long in params:
                if long > short:
                    data = ma_strategy(data=data, short_window=short, long_window=long)
                    data = calculate_profit_pct(data)
                    data = calculate_cum_profit(data)
                    if len(data) > 0:
                        # 获取周期参数，及其对应累计收益率
                        cum_profit = data["cum_profit_pct"].iloc[-1]  # 获取累计收益率最终数据
                        res.append([short, long, cum_profit])  # 将参数放入结果列表

        # 将结果列表转换为df，并找到最优参数
        res = pd.DataFrame(res, columns=["short_win", "long_win", "cum_profit_pct"])
        # 排序
        res = res.sort_values(by="cum_profit_pct", ascending=False)  # 按收益倒序排列
        print(code, "\n", res)
