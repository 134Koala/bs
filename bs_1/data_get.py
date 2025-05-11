import akshare as ak
import pandas as pd
import os
from datetime import datetime

def fetch_stock_data():
    # 参数设置
    with open("stock_list.txt", "r") as f:
        symbols = [line.strip() for line in f]
    # start_date = input("请输入开始日期(YYYYMMDD): ")
    # end_date = input("请输入结束日期(YYYYMMDD): ")
    start_date = 20100101
    end_date =20231231

    # 创建存储目录
    os.makedirs("stock_data", exist_ok=True)
    
    # 批量获取数据
    for symbol in symbols:
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq"
            )
            # 添加波动率特征[9](@ref)
            df["volatility"] = df["最高"] - df["最低"]
            df.to_csv(f"stock_data/{symbol}.csv", index=False)
            print(f"{symbol} 数据获取成功")
        except Exception as e:
            print(f"{symbol} 获取失败: {str(e)}")

if __name__ == "__main__":
    fetch_stock_data()