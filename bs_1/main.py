import argparse
import os
from data_get import fetch_stock_data
from bs_1.data_processing_demo import process_data
from model import train_model
from prediction import predict
from Trading_strategy import trading_strategy
def main():
    parser = argparse.ArgumentParser(description="Stock Prediction System")
    parser.add_argument("--symbol", help="指定股票代码")
    args = parser.parse_args()
    
    # 全流程执行
    fetch_stock_data()
    
    if args.symbol:
        process_data(args.symbol)
        train_model(args.symbol)
        predictions = predict(args.symbol)
        print(trading_strategy(predictions))
    else:
        symbols = [f.split(".")[0] for f in os.listdir("stock_data")]
        for symbol in symbols:
            process_data(symbol)
            train_model(symbol)
            predictions = predict(symbol)
            print(f"{symbol}策略结果:", trading_strategy(predictions))

if __name__ == "__main__":
    main()