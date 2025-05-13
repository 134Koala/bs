import numpy as np
import pandas as pd
import os
from keras.models import load_model
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def calculate_metrics(true, pred):
    """计算量化指标"""
    mae = mean_absolute_error(true, pred)
    mse = mean_squared_error(true, pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(true, pred)
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R2': r2
    }

def plot_results(dates, true, pred, symbol):
    """可视化结果"""
    import pandas as pd
    import numpy as np
    
    # 转换日期格式
    if isinstance(dates[0], (np.str_, str)):  # 处理字符串或numpy字符串
        dates = pd.to_datetime(dates)  # 转换为datetime64[ns]类型
    elif isinstance(dates[0], np.datetime64):  # 已经是numpy日期类型
        dates = dates.astype('datetime64[s]')  # 统一精度
    
    plt.figure(figsize=(15, 6))
    plt.plot(dates, true, label='True Price', color='blue')
    plt.plot(dates, pred, label='Predicted Price', color='red', linestyle='--')
    
    # 改进的日期标签处理
    n = len(dates)
    step = max(1, n//10)  # 显示约10个标签
    plt.xticks(ticks=dates[::step], 
               labels=[pd.to_datetime(d).strftime('%Y-%m-%d') for d in dates[::step]],
               rotation=45)
    
    plt.title(f'{symbol} Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(f"bs_1/pre_results/{symbol}/plots", exist_ok=True)
    plt.savefig(f"bs_1/pre_results/{symbol}/plots/prediction_plot.png", 
                bbox_inches='tight')
    plt.close()
    
def predict_stock(symbol):
    # 创建结果目录
    result_dir = f"bs_1/pre_results/{symbol}"
    os.makedirs(result_dir, exist_ok=True)
    
    # 加载数据
    data_path = f"bs_1/processing_data/{symbol}"
    X_test = np.load(f"{data_path}/X_test.npy")
    y_test = np.load(f"{data_path}/y_test.npy")  # 加载真实值
    test_dates = np.load(f"{data_path}/test_dates.npy")
    test_opens = np.load(f"{data_path}/test_opens.npy")  # 加载开盘价
     # 加载包含目标变量的scaler
    full_scaler = np.load(f"{data_path}/scaler.npy", allow_pickle=True).item()    
    # 加载模型
    model = load_model(f"bs_1/model/{symbol}_best.h5")
    
    # 生成预测
    predictions = model.predict(X_test)
    
     # 构建正确的伪矩阵
    dummy = np.zeros((len(predictions), full_scaler.n_features_in_))
    dummy[:, 1] = predictions.flatten()  # 收盘价是第1列

    # 构建正确的伪矩阵用于真实值反标准化
    dummy_true = np.zeros((len(y_test), full_scaler.n_features_in_))
    dummy_true[:, 1] = y_test.flatten()  # 收盘价是第1列

    # 构建伪矩阵用于开盘价反标准化
    dummy_opens = np.zeros((len(test_opens), full_scaler.n_features_in_))
    dummy_opens[:, 0] = test_opens  # 开盘价是第0列

    # 正确反标准化
    pred_prices = full_scaler.inverse_transform(dummy)[:, 1]  # 取第1列(收盘价)
    true_prices = full_scaler.inverse_transform(dummy_true)[:, 1]  # 取第1列(收盘价)
    open_prices = full_scaler.inverse_transform(dummy_opens)[:, 0]  # 取第0列(开盘价)
    
    # 计算量化指标
    metrics = calculate_metrics(true_prices, pred_prices)

    # 保存结果
    result_df = pd.DataFrame({
        'date': test_dates,
        'open': open_prices,  # 添加开盘价
        'true_price': true_prices,
        'predicted_price': pred_prices
    })
    
    # 保存预测结果和指标
    result_df.to_csv(f"{result_dir}/predictions.csv", index=False)
    
    with open(f"{result_dir}/metrics.txt", 'w') as f:
        for key, value in metrics.items():
            f.write(f"{key}: {value}\n")
    
    # 可视化结果
    plot_results(test_dates, true_prices, pred_prices, symbol)
    
    print(f"完成 {symbol} 的预测和评估")

if __name__ == "__main__":
    symbols = [f.split(".")[0] for f in os.listdir("bs_1/processing_data")]
    for symbol in symbols:
        print(f"正在处理 {symbol}...")
        predict_stock(symbol)