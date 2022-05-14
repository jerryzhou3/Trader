import time
from tqdm import tqdm
import data.stock as st


def update_daily_price_database(local=True):
    """
    更新股票行情数据，单线程下载
    :return:
    """
    stock_codes = st.get_stock_list()
    start_time = time.time()
    for code in tqdm(stock_codes):
        st.update_daily_price(code, "price", local)
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f"Daily price updated: {time_elapsed} seconds elapsed.")


def init_daily_price_database():
    update_daily_price_database(local=False)


if __name__ == "__main__":
    update_daily_price_database(local=True)
