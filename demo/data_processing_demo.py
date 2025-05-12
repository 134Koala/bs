import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os

def process_data(symbol):
    # 读取原始数据
    df = pd.read_csv(f"bs_1/stock_data/{symbol}.csv")
    
    # 特征工程[11](@ref)
    df["MA5"] = df["收盘"].rolling(5).mean()
    df["RSI"] = 100 - (100 / (1 + df["收盘"].pct_change().apply(lambda x: x if x>0 else 0).rolling(14).mean() / 
                            df["收盘"].pct_change().apply(lambda x: -x if x<0 else 0).rolling(14).mean()))
    df["MACD"] = df["收盘"].ewm(span=12).mean() - df["收盘"].ewm(span=26).mean()
    
    # 清洗数据
    df = df.dropna()
    print(df)
    features = ["开盘", "最高", "最低", "成交量", "MA5", "RSI", "MACD", "volatility"]
    target = "收盘"
    data = df[features + [target]].values
    print(data)
    # 创建时间序列数据集
    lookback = 30  # 使用30天数据预测
    X, y = [], []
    for i in range(lookback, len(df)):
        X.append(data[i-lookback:i, :-1])      
        y.append(data[i, -1])
    # 划分数据集（保持时间顺序）
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, shuffle=False)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, shuffle=False)
    # 仅用训练集数据拟合Scaler
    scaler = MinMaxScaler()
    scaler.fit(np.array(X_train).reshape(-1, len(features)))  # 注意维度处理

    # 标准化各数据集
    def scale_data(data):
        original_shape = data.shape
        scaled = scaler.transform(data.reshape(-1, len(features)))
        return scaled.reshape(original_shape)

    X_train = scale_data(np.array(X_train))
    X_val = scale_data(np.array(X_val))
    X_test = scale_data(np.array(X_test))
    print(f'train_lenth:',len(X_train))
    print(f'val_lenth:',len(X_val))
    print(f'test_lenth:',len(X_test))
    # 保存处理结果
    save_path = f"bs_1/processing_data/{symbol}/"
    os.makedirs(save_path, exist_ok=True)
    np.save(f"{save_path}X_train.npy", X_train)
    np.save(f"{save_path}y_train.npy", y_train)
    np.save(f"{save_path}X_val.npy", X_val)
    np.save(f"{save_path}y_val.npy", y_val)
    np.save(f"{save_path}X_test.npy", X_test)
    np.save(f"{save_path}y_test.npy", y_test)
    np.save(f"{save_path}scaler.npy", scaler)

if __name__ == "__main__":
    symbols = [f.split(".")[0] for f in os.listdir("stock_data")]
    for symbol in symbols:
        process_data(symbol)