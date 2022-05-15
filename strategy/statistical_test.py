# ！/usr/bin/env python
# encoding: utf-8
"""
@Author: Yeju Zhou
@File: statistical_test.py
@Time: 2022/5/14 16:08
@Describe: 基于统计学方法检验策略可靠性
"""
import numpy as np
from scipy import stats


def ttest(profit_pct, null_expectation=0):
    """
    对策略收益进行t检验
    :param profit_pct: 策略收益率
    :param null_expectation: expected value of null hypothesis
    :return: t值和p值
    """
    if len(profit_pct) <= 1:
        return np.NaN, np.NaN
    t, p = stats.ttest_1samp(profit_pct, null_expectation, nan_policy='omit')
    # 判断是否与理论均值有显著性差异:α=0.05
    p_value = p / 2  # 获取单边p值
    print("t-value:", t)
    print("p-value:", p_value)
    print(f"是否可以拒绝[H0]收益均值={null_expectation}：", p_value < 0.05)
    return t, p_value


def calculate_winning_rate(data) -> float:
    """
    计算策略胜率
    :param data: 股票数据，包含 profit_pct 列
    :return:
    """
    temp = data["profit_pct"]
    win_count = temp[temp >= 0].count()
    lose_count = temp[temp < 0].count()
    total_count = win_count + lose_count
    if total_count == 0:
        winning_rate = -1
    else:
        winning_rate = win_count / (win_count + lose_count)
    print(f"胜率={winning_rate}")
    return winning_rate
