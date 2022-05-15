from jqdatasdk import *
import pandas as pd
import datetime
import os

auth_flag = False


def auth_check(func):
    def _wrapper(*args, **kwargs):
        global auth_flag
        if not auth_flag:
            auth("13668130088", "Zyj-1998323")
        res = func(*args, **kwargs)
        return res
    return _wrapper


@auth_check
def get_stock_list():
    """
    获取所有A股股票列表，上交所.XSHG，深交所.XSHE
    :return: stock_list
    """
    stock_list = list(get_all_securities(["stock"]).index)
    return stock_list


def get_local_stock_list():
    file_root = os.path.join(os.path.dirname(__file__), "price")
    stock_list = []
    for file in os.listdir(file_root):
        stock_list.append(file.strip(".csv"))
    return stock_list


@auth_check
def get_index_list(index_symbol='000300.XSHG'):
    """
    获取指数成分股，指数代码查询：https://www.joinquant.com/indexData
    :param index_symbol: 指数的代码，默认沪深300
    :return: list，成分股代码
    """
    stocks = get_index_stocks(index_symbol)
    return stocks


@auth_check
def get_single_price(code, frequency, start_date=None, end_date=None, export=False):
    """
    获取单个股票行情数据
    :param code: 股票代码
    :param frequency: 数据周期
    :param start_date: 起始日期
    :param end_date: 结束日期
    :return: data
    """
    if start_date is None:
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    data = get_price(code, start_date=start_date, end_date=end_date, frequency=frequency, panel=False)
    data.index.names = ["date"]
    if export:
        export_data(data, code, "price")
    return data


def get_data_path(code, type):
    """
    获取股票数据路径
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :return: file_path
    """
    file_path = os.path.join(os.path.dirname(__file__), type, f"{code}.csv")
    return file_path


def export_data(data, code, type):
    """
    导出股票相关数据
    :param data: 股票数据
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :return: None
    """
    file_path = os.path.join(os.path.dirname(__file__), type, f"{code}.csv")
    data.index.names = ["date"]
    if os.path.exists(file_path):
        existing_data = import_data(code, type)
        concat = pd.concat([existing_data, data]).drop_duplicates().sort_index()
        concat.to_csv(file_path)
    else:
        data.to_csv(file_path)
    print("导出至 {}".format(file_path))


def import_data(code, type, start_date=None, end_date=None):
    """
    导出股票相关数据
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :param start_date: 起始日期
    :param end_date: 结束日期
    :return: None
    """
    file_path = os.path.join(os.path.dirname(__file__), type, f"{code}.csv")
    if not os.path.exists(file_path):
        raise Exception(f"{file_path} not found!")
    data = pd.read_csv(file_path, index_col=0)
    data.index = data.index.astype("datetime64[ns]")
    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data


def transfer_price_frequency(data, frequency):
    """
    转换股票数据周期：开盘价（周期第一天），收盘价（周期最后一天），最高价（周期内最高价），最低价（周期内最低价）
    :param data: 股票数据
    :param frequency: 数据周期
    :return: trans
    """
    trans = pd.DataFrame()
    trans["open"] = data["open"].resample(frequency).first()
    trans["close"] = data["close"].resample(frequency).last()
    trans["high"] = data["high"].resample(frequency).max()
    trans["low"] = data["low"].resample(frequency).min()
    return trans


@auth_check
def get_single_finance(code, date=None, statDate=None):
    """
    获取单个股票财务指标
    :param code: 股票代码
    :param date: 查询日期
    :param statDate: 财报统计的季度或年份
    :return: data
    """
    data = get_fundamentals(query(indicator).filter(indicator.code == code), date=date, statDate=statDate)
    return data


@auth_check
def get_single_valuation(code, date=None, statDate=None):
    """
    获取单个股票估值指标
    :param code: 股票代码
    :param date: 查询日期
    :param statDate: 财报统计的季度或年份
    :return: data
    """
    data = get_fundamentals(query(valuation).filter(valuation.code == code), date=date, statDate=statDate)
    return data


def calculate_change_percent(data):
    """
    涨跌幅 = （当期收盘价 - 前期收盘价） / 前期收盘价
    :param data:
    :return:
    """
    data["close_pct"] = (data["close"] - data["close"].shift(1)) / data["close"].shift(1)
    return data


@auth_check
def update_daily_price(code, type='price', local=True):
    """
    更新单个股票行情数据
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :return: None
    """
    file_path = get_data_path(code, type)
    if os.path.exists(file_path):
        start_date = pd.read_csv(file_path, usecols=["date"])["date"].iloc[-1]
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        if today > start_date:
            data = get_single_price(code, "daily", start_date, today)
            export_data(data, code, "price")
            print(f"股票数据已更新： {code}")
    elif not local:
        data = get_single_price(code, "daily")
        export_data(data, code, "price")
        print(f"股票数据已更新：{code}")
