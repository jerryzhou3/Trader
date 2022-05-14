from strategy.base import *
import matplotlib.pyplot as plt

# 获取三只股票数据：天齐锂业002466.XSHE，赣锋锂业002460.XSHE，西藏矿业000762.XSHE
code_list = ["002466.XSHE", "002460.XSHE", "000762.XSHE"]
sharpe_daily_list = []
sharpe_annual_list = []
for code in code_list:
    data = import_data_wrapper(code, "daily", "2021-01-01")
    sharpe_daily, sharpe_annual = calculate_sharpe_ratio(data)
    sharpe_daily_list.append(sharpe_daily)
    sharpe_annual_list.append(sharpe_annual)

x = np.arange(len(code_list))
width = 0.3
fig, ax = plt.subplots(dpi=500)
rects1 = ax.bar(x - width/2, sharpe_daily_list, width, label='Sharpe Daily')
rects2 = ax.bar(x + width/2, sharpe_annual_list, width, label='Sharpe Annual')
ax.set_ylabel('Sharpe Ratio')
ax.set_title('Share Ratio')
ax.set_xticks(x, code_list)
ax.legend()
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
fig.tight_layout()
plt.show()
