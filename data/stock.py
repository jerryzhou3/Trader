from jqdatasdk import *
import os
from util import *

auth_flag = False


def auth_check():
    global auth_flag
    if not auth_flag:
        auth(os.getenv("JQUSERNAME"), os.getenv("JQPASSWORD"))


def get_stock_list():
    """
    获取所有A股股票列表，上交所.XSHG，深交所.XSHE
    :return: stock_list
    """
    auth_check()
    stock_list = list(get_all_securities(["stock"]).index)
    return stock_list


def get_local_stock_list():
    file_root = os.path.join(os.path.dirname(__file__), "price")
    stock_list = []
    for file in os.listdir(file_root):
        stock_list.append(file.strip(".csv"))
    return stock_list


def get_index_list(index_symbol='000300.XSHG'):
    """
    获取指数成分股，指数代码查询：https://www.joinquant.com/indexData
    :param index_symbol: 指数的代码，默认沪深300
    :return: list，成分股代码
    """
    file_path = os.path.join(os.path.dirname(__file__), "index_list", index_symbol)
    if os.path.exists(file_path):
        stocks = json.load(open(file_path))
        print(f"从本地读取指数 {index_symbol} 股票列表")
        print(f"指数 {index_symbol} 中含有 {len(stocks)} 支股票")
    else:
        auth_check()
        stocks = get_index_stocks(index_symbol)
        with open(file_path, "w") as f:
            f.write(json.dumps(stocks))
        print(f"缓存指数 {index_symbol} 股票列表到本地")
        print(f"指数 {index_symbol} 中含有 {len(stocks)} 支股票")
    return stocks


def get_single_price(code, frequency, start_date=None, end_date=None, export=False):
    """
    获取单个股票行情数据
    :param code: 股票代码
    :param frequency: 数据周期
    :param start_date: 起始日期
    :param end_date: 结束日期
    :param export: 是否储存数据到本地
    :return: data
    """
    if start_date is None:
        auth_check()
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    auth_check()
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


def export_data(data, code, type, overwrite=False):
    """
    导出股票相关数据
    :param data: 股票数据
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :param overwrite: 是否重写所有数据
    :return: None
    """
    file_path = os.path.join(os.path.dirname(__file__), type, f"{code}.csv")
    data.index.names = ["date"]
    if os.path.exists(file_path) and not overwrite:
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
    :param use_cols: 截取列名
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
    alert = True
    if end_date is None:
        end_date = datetime.datetime.today()
    latest_possible_trading_date = get_latest_possible_trading_day(end_date)
    if timestamp_to_string(data.index[-1]) >= latest_possible_trading_date:
        alert = False
    if alert:
        print(f"{code} {type} data might be obsolete!")
    return data


def transfer_price_frequency(data, frequency):
    """
    转换股票数据周期：开盘价（周期第一天），收盘价（周期最后一天），最高价（周期内最高价），最低价（周期内最低价）
    如当天所有数据均为空值 NaN，则被舍弃（长假期等非交易日导致所有股票均无交易）
    :param data: 股票数据
    :param frequency: 数据周期
    :return: trans
    """
    default_cols = ["open", "close", "high", "low", "volume", "money"]
    multi_index = False
    trans = pd.DataFrame()
    for col in data.columns:
        col_name = col
        if not isinstance(col, str) and not isinstance(col, tuple):
            raise Exception("Unhandled DataFrame column structure!")
        if isinstance(col, tuple):
            multi_index = True
            for c in col:
                if c in default_cols:
                    col_name = c
                    break
        if col_name == "open":
            trans[col] = data[col].resample(frequency).first()
        elif col_name == "close":
            trans[col] = data[col].resample(frequency).last()
        if col_name == "high":
            trans[col] = data[col].resample(frequency).max()
        if col_name == "low":
            trans[col] = data[col].resample(frequency).min()
        if col_name == "volume":
            trans[col] = data[col].resample(frequency).sum()
        if col_name == "money":
            trans[col] = data[col].resample(frequency).sum()
    if multi_index:
        trans.columns = pd.MultiIndex.from_tuples(list(trans.columns))
    trans = trans.dropna(how="all")
    return trans


def get_single_finance(code, date=None, statDate=None):
    """
    获取单个股票财务指标
    :param code: 股票代码
    :param date: 查询日期
    :param statDate: 财报统计的季度或年份
    :return: data
    """
    auth_check()
    data = get_fundamentals(query(indicator).filter(indicator.code == code), date=date, statDate=statDate)
    return data


def get_single_valuation(code, date=None, statDate=None):
    """
    获取单个股票估值指标
    :param code: 股票代码
    :param date: 查询日期
    :param statDate: 财报统计的季度或年份
    :return: data
    """
    auth_check()
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


def update_daily_price(code, type="price", local=True, fetch=False):
    """
    更新单个股票行情数据
    :param code: 股票代码
    :param type: 股票数据类型：price, finance
    :param local: 是否只更新数据库中存在的股票数据
    :param fetch: 重新获取股票数据
    :return: None
    """
    if fetch:
        data = get_single_price(code, "daily")
        export_data(data, code, "price", overwrite=True)
        print(f"股票数据已重新获取：{code}")
        return
    file_path = get_data_path(code, type)
    if os.path.exists(file_path):
        update = False
        overwrite = False
        latest_possible_trading_day = get_latest_possible_trading_day(datetime.datetime.today())
        try:
            end_date = pd.read_csv(file_path, usecols=["date"])["date"].iloc[-1]
            if end_date < latest_possible_trading_day:
                update = True
        except IndexError:
            update = True
            end_date = None
            overwrite = True
        if update:
            data = get_single_price(code, "daily", end_date, latest_possible_trading_day)
            export_data(data, code, "price", overwrite=overwrite)
            print(f"股票数据已更新： {code}")
    elif not local:
        data = get_single_price(code, "daily")
        export_data(data, code, "price")
        print(f"股票数据已添加：{code}")


if __name__ == "__main__":
    index_list = get_index_list()
    print(len(index_list))
