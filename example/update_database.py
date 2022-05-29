import time
from tqdm import tqdm
import data.stock as st


def update_daily_price_database(stock_codes=None, local=True):
    """
    更新股票行情数据，单线程下载
    :return:
    """
    if stock_codes is None:
        stock_codes = st.get_stock_list()
    start_time = time.time()
    for code in tqdm(stock_codes):
        st.update_daily_price(code, "price", local)
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f"Daily price updated: {time_elapsed} seconds elapsed.")


if __name__ == "__main__":
    # update_daily_price_database(st.get_index_list("000300.XSHG"), local=True)
    # update_daily_price_database(local=False)
    update_daily_price_database(["000001.XSHE"], local=False)
