import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from joblib import dump
import os

def compute_features(data):
    """特征工程，仅使用历史数据"""
    data = data.copy()
    # MA5
    data["MA5"] = data["收盘"].rolling(5).mean()
    # RSI
    delta = data["收盘"].pct_change()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-8)  # 避免除零
    data["RSI"] = 100 - (100 / (1 + rs))
    # MACD
    ema12 = data["收盘"].ewm(span=12, adjust=False).mean()
    ema26 = data["收盘"].ewm(span=26, adjust=False).mean()
    data["MACD"] = ema12 - ema26
    # 波动率（假设原始数据有"涨跌幅"列）
    data["volatility"] = data["收盘"].pct_change().rolling(30).std()
    return data

def create_sequences(data, lookback, features, target):
    """创建时间序列数据集（修复索引问题版本）"""
    X, y = [], []
    # 转换为numpy数组以提高效率
    data_features = data[features].values
    data_target = data[target].values
    for i in range(lookback, len(data)):
        X.append(data_features[i-lookback:i])  # 直接使用位置切片
        y.append(data_target[i])  # 直接使用位置索引
    return np.array(X), np.array(y)

def process_data(symbol):
    # 读取并排序数据
    df = pd.read_csv(f"bs_1/stock_data/{symbol}.csv").sort_values("日期")
    
    # 按时间分割数据集（训练70%，验证15%，测试15%）
    train_idx = int(0.7 * len(df))
    val_idx = train_idx + int(0.15 * len(df))
    
    # 原始数据分割（未处理特征）
    train_raw = df.iloc[:train_idx]
    val_raw = df.iloc[train_idx:val_idx]
    test_raw = df.iloc[val_idx:]
    
    # 处理训练集特征
    train_processed = compute_features(train_raw).dropna().reset_index(drop=True)
    
    # 处理验证集特征（合并训练集原始数据）
    val_combined = pd.concat([train_raw, val_raw])
    val_processed = compute_features(val_combined).dropna().reset_index(drop=True)
    val_processed = val_processed[val_processed["日期"].isin(val_raw["日期"])]
    
    # 处理测试集特征（合并训练+验证原始数据）
    test_combined = pd.concat([train_raw, val_raw, test_raw])
    test_processed = compute_features(test_combined).dropna().reset_index(drop=True)
    test_processed = test_processed[test_processed["日期"].isin(test_raw["日期"])]
    
    # 特征列定义
    features = ["开盘", "最高", "最低", "成交量", "MA5", "RSI", "MACD", "volatility"]
    target = "收盘"
    lookback = 30
    
    # 创建时间序列数据集（确保使用历史数据）
    X_train, y_train = create_sequences(train_processed, lookback, features, target)
    
    # 验证集需要包含训练集的历史数据
    val_series = pd.concat([train_processed, val_processed])
    X_val, y_val = create_sequences(val_series, lookback, features, target)
    X_val, y_val = X_val[-len(val_processed):], y_val[-len(val_processed):]  # 取最后部分
    
    # 测试集包含所有历史数据
    test_series = pd.concat([val_series, test_processed])
    X_test, y_test = create_sequences(test_series, lookback, features, target)
    X_test, y_test = X_test[-len(test_processed):], y_test[-len(test_processed):]
    
    # print(len(X_test),len(X_train),len(X_val) )
    
    # 归一化（仅用训练集拟合）
    scaler = MinMaxScaler()
    scaler.fit(X_train.reshape(-1, len(features)))
    
    # 标准化数据集
    X_train = scaler.transform(X_train.reshape(-1, len(features))).reshape(X_train.shape)
    X_val = scaler.transform(X_val.reshape(-1, len(features))).reshape(X_val.shape)
    X_test = scaler.transform(X_test.reshape(-1, len(features))).reshape(X_test.shape)
    
    # 保存结果
    save_path = f"bs_1/processing_data/{symbol}/"
    os.makedirs(save_path, exist_ok=True)
    np.save(f"{save_path}X_train.npy", X_train)
    np.save(f"{save_path}y_train.npy", y_train)
    np.save(f"{save_path}X_val.npy", X_val)
    np.save(f"{save_path}y_val.npy", y_val)
    np.save(f"{save_path}X_test.npy", X_test)
    np.save(f"{save_path}y_test.npy", y_test)
    np.save(f"{save_path}scaler.npy", scaler)
    # 新增：保存测试集日期数据
    np.save(f"{save_path}dates_test.npy", test_processed["日期"].values)
    # 新增：保存验证集日期数据（根据实际需要）
    np.save(f"{save_path}dates_val.npy", val_processed["日期"].values)
    # 新增：保存训练集日期数据（根据实际需要）
    np.save(f"{save_path}dates_train.npy", train_processed["日期"].values)
    # 保存测试集的开盘价数据
    np.save(f"{save_path}open_test.npy", test_processed["开盘"].values)

# if __name__ == "__main__":
#     symbols = [f.split(".")[0] for f in os.listdir("bs_1/stock_data")]
#     for symbol in symbols:
#         print(f"正在处理 {symbol}...")
#         process_data(symbol)