import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

def compute_features(df, mode='train'):
    """特征工程（防止数据泄露版本）"""
    df = df.copy()
    # 读取沪深300数据
    hs300_train = pd.read_csv("bs_1/stock_data/000300/train.csv")
    hs300_test = pd.read_csv("bs_1/stock_data/000300/test.csv")

    # 基础特征
    features = ['开盘', '收盘', '最高', '最低', '成交量', 'volatility']
    
    # 移动平均线
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA10'] = df['收盘'].rolling(10).mean()
    
    # RSI
    delta = df['收盘'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (avg_gain / (avg_loss + 1e-8))))
    
    # MACD
    ema12 = df['收盘'].ewm(span=12, adjust=False).mean()
    ema26 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    
    # 量价比（成交量/收盘价）
    df['volume_price_ratio'] = df['成交量'] / (df['收盘'] + 1e-8)

    # 添加沪深300特征
    hs300_data = hs300_train if mode == 'train' else hs300_test
    hs300_data = hs300_data[['日期', '收盘', '成交量', 'volatility']]
    hs300_data.columns = ['日期', 'hs300_close', 'hs300_volume', 'hs300_volatility']
    
    # 合并沪深300数据
    df = pd.merge(df, hs300_data, on='日期', how='left')
    
    # 计算个股与沪深300的相对指标
    df['relative_close'] = df['收盘'] / (df['hs300_close'] + 1e-8)
    df['relative_volume'] = df['成交量'] / (df['hs300_volume'] + 1e-8)
    df['relative_volatility'] = df['volatility'] / (df['hs300_volatility'] + 1e-8)
    
    # 特征筛选
    final_features = ['日期', '开盘', '收盘', '最高', '最低', '成交量', 
                     'MA5', 'MA10', 'volatility', 'RSI', 
                     'MACD', 'volume_price_ratio',
                     'hs300_close', 'hs300_volume', 'hs300_volatility',
                     'relative_close', 'relative_volume', 'relative_volatility']
    
    df = df[final_features].dropna()

    return df

def create_sequences(data, lookback=30):
    """创建时间序列数据集"""
    X, y ,dates,opens= [], [],[],[]
    for i in range(lookback, len(data)):
        X.append(data.iloc[i-lookback:i, :-1].values)  
        y.append(data.iloc[i, 1])  # 收盘价作为目标
        dates.append(data.iloc[i, -1])  # 日期列
        opens.append(data.iloc[i, 0])  # 开盘价
    return np.array(X), np.array(y),np.array(dates), np.array(opens)

def process_data(symbol):
    # 创建处理目录
    process_dir = f"bs_1/processing_data/{symbol}"
    os.makedirs(process_dir, exist_ok=True)
    
    # 读取原始数据
    train_df = pd.read_csv(f"bs_1/stock_data/{symbol}/train.csv")
    test_df = pd.read_csv(f"bs_1/stock_data/{symbol}/test.csv")
    
    # 特征工程
    train_processed = compute_features(train_df, mode='train')
    test_processed = compute_features(test_df, mode='test')

    # 提取日期列
    train_dates = train_processed['日期']
    test_dates = test_processed['日期']

    # 移除非特征列（日期）
    train_processed = train_processed.drop(columns=['日期'])
    test_processed = test_processed.drop(columns=['日期'])

    # print(train_processed)

    # 合并特征与目标进行标准化
    full_scaler = MinMaxScaler()
    train_scaled = pd.DataFrame(full_scaler.fit_transform(train_processed), 
                               columns=train_processed.columns)
    test_scaled = pd.DataFrame(full_scaler.transform(test_processed), 
                              columns=test_processed.columns)
    # print(train_scaled.head)

    # 重新附加日期列
    train_scaled['date'] = train_dates.reset_index(drop=True)
    test_scaled['date'] = test_dates.reset_index(drop=True)

    # 创建序列数据集
    X_train, y_train, _ , _ = create_sequences(train_scaled)
    X_test, y_test ,test_dates, test_opens= create_sequences(test_scaled)

    
    # X_train, y_train = create_sequences(train_processed)
    # X_test, y_test = create_sequences(test_processed)

    # print(X_test.shape)
    # print(y_test)

    # # 数据标准化
    # scaler = MinMaxScaler()
    # scaler.fit(X_train.reshape(-1, X_train.shape[2]))



    
    # 保存处理结果
    np.save(f"{process_dir}/test_dates.npy", test_dates)
    np.save(f"{process_dir}/test_opens.npy", test_opens)  # 新增保存开盘价
    np.save(f"{process_dir}/X_train.npy", X_train)
    np.save(f"{process_dir}/y_train.npy", y_train)
    np.save(f"{process_dir}/X_test.npy", X_test)
    np.save(f"{process_dir}/y_test.npy", y_test)
    np.save(f"{process_dir}/scaler.npy", full_scaler)
if __name__ =="__main__":
    symbols = [f.split(".")[0] for f in os.listdir("bs_1/stock_data")]
    for symbol in symbols:
        print(f"正在处理 {symbol}...")
        process_data(symbol)