# main.py (整合后的主文件)
import argparse
import pandas as pd
import os
from data_get import fetch_stock_data
from data_processing import process_data
from model import train_model
from prediction import predict_stock
from Trading_strategy import TradingStrategy

def main():
    parser = argparse.ArgumentParser(description="量化投资系统")
    parser.add_argument("--symbol", help="指定单个股票代码运行")
    parser.add_argument("--all", action="store_true", help="运行全部股票")
    args = parser.parse_args()

    # 数据获取阶段
    # print("正在获取股票数据...")
    # fetch_stock_data()

    # # 数据处理和模型训练
    # if args.symbol:
    #     print(f"正在处理 {args.symbol}...")
    #     process_data(args.symbol)
    #     train_model(args.symbol)
    # elif args.all:
    #     symbols = [f.split(".")[0] for f in os.listdir("bs_1/stock_data")]
    #     for symbol in symbols:
    #         print(f"正在处理 {symbol}...")
    #         process_data(symbol)
    #         train_model(symbol)

    # 预测阶段
    symbols = [f.split(".")[0] for f in os.listdir("bs_1/processing_data")]
    for symbol in symbols:
        print(f"正在处理 {symbol}...")
        predict_stock(symbol)

    # 执行交易策略
    print("正在执行交易策略回测...")    
    try:
        strategy = TradingStrategy()
        results = strategy.run()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()