import akshare as ak
import pandas as pd
import os

def fetch_hs300_index_data():
    # 沪深300指数代码
    index_symbol = "000300"  # 或 "sh000300"
    
    # 日期范围设置
    date_ranges = {
        'train': ('20100101', '20191231'),
        'test': ('20200101', '20241231')
    }
    
    # 创建存储目录
    index_dir = f"bs_1/stock_data/{index_symbol}"
    os.makedirs(index_dir, exist_ok=True)
    
    try:
        for dataset in ['train', 'test']:
            df = ak.index_zh_a_hist(
                symbol=index_symbol,
                period="daily",
                start_date=date_ranges[dataset][0],
                end_date=date_ranges[dataset][1]
            )
            # 添加波动率特征
            df["volatility"] = df["最高"] - df["最低"]
            df.to_csv(f"{index_dir}/{dataset}.csv", index=False)
        
        print(f"沪深300指数 ({index_symbol}) 数据获取成功")
    except Exception as e:
        print(f"沪深300指数 ({index_symbol}) 获取失败: {str(e)}")

if __name__ == "__main__":
    fetch_hs300_index_data()