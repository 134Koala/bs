import os
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from keras.models import load_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from matplotlib import dates as mdates
# 创建必要的目录
os.makedirs("D:/bs/bs_1/compare/model", exist_ok=True)
os.makedirs("D:/bs/bs_1/compare/pre_result", exist_ok=True)

def calculate_metrics(y_true, y_pred, model_name):
    """计算并返回各种评估指标"""
    metrics = {
        'Model': model_name,
        'MSE': mean_squared_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE': mean_absolute_percentage_error(y_true, y_pred) * 100,  # 转换为百分比
        'R2': r2_score(y_true, y_pred)
    }
    return metrics

def save_metrics_to_csv(metrics_dict, filename="model_metrics.csv"):
    """将评估指标保存到CSV文件"""
    metrics_df = pd.DataFrame.from_dict(metrics_dict, orient='index').T
    
    # 如果文件已存在，则追加新数据
    filepath = f"D:/bs/bs_1/compare/pre_result/{filename}"
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        metrics_df = pd.concat([existing_df, metrics_df], ignore_index=True)
    
    metrics_df.to_csv(filepath, index=False)
    print(f"Metrics saved to {filepath}")

def load_processed_data(symbol='000300'):
    """加载处理后的时间序列数据"""
    data_dir = f"D:/bs/bs_1/processing_data/{symbol}"
    
    X_train = np.load(f"{data_dir}/X_train.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    test_dates = np.load(f"{data_dir}/test_dates.npy")
    test_opens = np.load(f"{data_dir}/test_opens.npy")
    scaler = np.load(f"{data_dir}/scaler.npy", allow_pickle=True).item()
    
    return X_train, y_train, X_test, y_test, test_dates, test_opens, scaler

def build_lstm_model(input_shape):
    """构建LSTM模型"""
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(32, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1)  # 预测收盘价
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_lstm(X_train, y_train, epochs=100, batch_size=32):
    """训练LSTM模型"""
    # 分割验证集
    split = int(0.8 * len(X_train))
    X_val, y_val = X_train[split:], y_train[split:]
    X_train, y_train = X_train[:split], y_train[:split]
    
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint('D:/bs/bs_1/compare/model/best_lstm_model.h5', save_best_only=True)
    ]
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    return model, history

def train_random_forest(X_train, y_train, X_test=None, y_test=None, n_estimators=100):
    """训练随机森林模型"""
    # 转换数据形状为2D
    X_train_rf = X_train.reshape(X_train.shape[0], -1)
    
    # 如果没有测试集，从训练集分割
    if X_test is None or y_test is None:
        X_train_rf, X_test_rf, y_train, y_test = train_test_split(
            X_train_rf, y_train, test_size=0.2, random_state=42
        )
    else:
        X_test_rf = X_test.reshape(X_test.shape[0], -1)
    
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_rf, y_train)
    
    # 评估模型
    train_pred = model.predict(X_train_rf)
    test_pred = model.predict(X_test_rf)
    
    print("Random Forest Performance:")
    print("Train MSE:", mean_squared_error(y_train, train_pred))
    print("Test MSE:", mean_squared_error(y_test, test_pred))
    print("Train MAE:", mean_absolute_error(y_train, train_pred))
    print("Test MAE:", mean_absolute_error(y_test, test_pred))
    
    return model, (train_pred, test_pred)

def save_predictions(model, model_name, X_test, test_dates, test_opens, scaler):
    """保存预测结果"""
    # 预测
    if model_name == 'lstm':
        preds = model.predict(X_test).flatten()
    else:  # random forest
        X_test_rf = X_test.reshape(X_test.shape[0], -1)
        preds = model.predict(X_test_rf)
    
    # 反归一化
    temp_array = np.zeros((len(preds), scaler.n_features_in_))
    temp_array[:, 1] = preds  # 收盘价在原始特征中是第1列(从0开始)
    temp_array = scaler.inverse_transform(temp_array)
    preds = temp_array[:, 1]
    
    # 获取真实收盘价
    true_close = scaler.inverse_transform(X_test[:, -1, :])[:, 1]
    
    # 计算指标
    metrics = calculate_metrics(true_close, preds, model_name)
    save_metrics_to_csv(metrics)
    
    # 保存结果
    result_df = pd.DataFrame({
        'date': test_dates,
        'open': test_opens,
        'true_close': true_close,
        'pred_close': preds
    })
    
    result_df.to_csv(f"D:/bs/bs_1/compare/pre_result/{model_name}_predictions.csv", index=False)
    print(f"{model_name} predictions saved to pre_result/{model_name}_predictions.csv")
    return result_df, metrics

def visualize_results(lstm_df, rf_df, lstm_metrics, rf_metrics):
    """可视化预测结果和指标"""
    plt.figure(figsize=(18, 8))  # 增大图表尺寸
    
    # 转换日期格式
    lstm_df['date'] = pd.to_datetime(lstm_df['date'])
    rf_df['date'] = pd.to_datetime(rf_df['date'])
    
    # 绘制真实值
    plt.plot(lstm_df['date'], lstm_df['true_close'], 
             label='True Close', color='black', linewidth=2)
    
    # 绘制预测值
    plt.plot(lstm_df['date'], lstm_df['pred_close'], 
             label='LSTM Predictions', color='blue', alpha=0.7)
    plt.plot(rf_df['date'], rf_df['pred_close'], 
             label='RF Predictions', color='red', alpha=0.7)
    
    plt.title('Model Predictions Comparison', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Close Price', fontsize=12)
    plt.legend(fontsize=12)
    
    # 优化日期显示
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # 每3个月显示一个标签
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # 简化日期格式
    plt.xticks(rotation=45, ha='right')  # 旋转45度，右对齐
    
    plt.grid(True, linestyle='--', alpha=0.6)  # 添加网格线
    plt.tight_layout()  # 自动调整布局
    
    # 保存图表
    plt.savefig('D:/bs/bs_1/compare/pre_result/predictions_comparison.png', 
                dpi=300, bbox_inches='tight')

def plot_training_history(history):
    """绘制LSTM训练历史"""
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Train MAE')
    plt.plot(history.history['val_mae'], label='Validation MAE')
    plt.title('Model MAE')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('D:/bs/bs_1/compare/pre_result/lstm_training_history.png')

def main():
    # 1. 加载处理后的数据
    print("Loading processed data...")
    X_train, y_train, X_test, y_test, test_dates, test_opens, scaler = load_processed_data()
    
    # 2. 训练LSTM模型
    print("\nTraining LSTM model...")
    lstm_model, lstm_history = train_lstm(X_train, y_train, epochs=100)
    lstm_model.save('D:/bs/bs_1/compare/model/lstm_model.h5')
    plot_training_history(lstm_history)
    
    # 3. 训练随机森林模型
    print("\nTraining Random Forest model...")
    rf_model, (rf_train_pred, rf_test_pred) = train_random_forest(X_train, y_train, X_test, y_test)
    
    # 保存随机森林模型
    import joblib
    joblib.dump(rf_model, 'D:/bs/bs_1/compare/model/rf_model.pkl')
    
    # 4. 保存预测结果并获取指标
    print("\nSaving predictions and calculating metrics...")
    lstm_df, lstm_metrics = save_predictions(lstm_model, 'lstm', X_test, test_dates, test_opens, scaler)
    rf_df, rf_metrics = save_predictions(rf_model, 'rf', X_test, test_dates, test_opens, scaler)
    
    # 5. 可视化结果
    visualize_results(lstm_df, rf_df, lstm_metrics, rf_metrics)
    
    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()