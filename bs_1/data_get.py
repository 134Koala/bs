import akshare as ak
import pandas as pd
import os

def fetch_stock_data():
    # 读取股票列表
    with open("bs_1/stock_list.txt", "r") as f:
        symbols = [line.strip() for line in f]
    
    # 日期范围设置
    date_ranges = {
        'train': ('20100101', '20191231'),
        'test': ('20200101', '20241231')
    }
    
    # 批量获取数据
    for symbol in symbols:
        try:
            # 创建个股目录
            stock_dir = f"bs_1/stock_data/{symbol}"
            os.makedirs(stock_dir, exist_ok=True)
            
            # 分别获取训练集和测试集
            for dataset in ['train', 'test']:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=date_ranges[dataset][0],
                    end_date=date_ranges[dataset][1],
                    adjust="hfq"
                )
                # 添加基础波动率特征
                df["volatility"] = df["最高"] - df["最低"]
                df.to_csv(f"{stock_dir}/{dataset}.csv", index=False)
            
            print(f"{symbol} 数据获取成功")
        except Exception as e:
            print(f"{symbol} 获取失败: {str(e)}")
if __name__ == "__main__":
    fetch_stock_data()