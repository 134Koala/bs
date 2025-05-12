import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSING_PATH = os.path.join(BASE_DIR, "processing_data")
MODEL_PATH = os.path.join(BASE_DIR, "model")
RESULTS_PATH = os.path.join(BASE_DIR, "results")

def predict_all_stocks():
    if not os.path.exists(PROCESSING_PATH):
        print(f"错误：目录 {PROCESSING_PATH} 不存在！")
        # 自动创建目录（若需要）
        os.makedirs(PROCESSING_PATH, exist_ok=True)
        print(f"已自动创建目录：{PROCESSING_PATH}")

    """批量预测所有股票"""
    # 获取股票列表
    stock_codes = [d for d in os.listdir(PROCESSING_PATH) 
                  if os.path.isdir(os.path.join(PROCESSING_PATH, d))]
    
    all_metrics = []
    
    for code in stock_codes:
        try:
            # 路径配置
            data_dir = os.path.join(PROCESSING_PATH, code)
            model_path = os.path.join(MODEL_PATH, f"{code}_best.h5")
            result_dir = os.path.join(RESULTS_PATH, code)
            os.makedirs(result_dir, exist_ok=True)
            
            # 跳过无数据股票
            if not os.path.exists(os.path.join(data_dir, "X_test.npy")):
                continue
                
            # 加载数据
            X_test = np.load(os.path.join(data_dir, "X_test.npy"))
            y_test = np.load(os.path.join(data_dir, "y_test.npy"))
            scaler = np.load(os.path.join(data_dir, "scaler.npy"), allow_pickle=True).item()
            dates_test = np.load(os.path.join(data_dir, "dates_test.npy"), allow_pickle=True)  # 修复日期加载
            open_test = np.load(os.path.join(data_dir, "open_test.npy"))  # 加载开盘价
            n_features = X_test.shape[2]  # 新增行：从数据维度获取特征数
            # 加载模型
            model = load_model(model_path)
            
            # 预测处理
            predictions = model.predict(X_test)
            
            # 反标准化（修复预测值部分保持不变）
            dummy_pred = np.zeros((len(predictions), n_features))  # 修改处
            dummy_pred[:, -1] = predictions.flatten()
            pred_prices = scaler.inverse_transform(dummy_pred)[:, -1]

            dummy_open = np.zeros((len(open_test), n_features))
            dummy_open[:, -1] = open_test.flatten()  # 假设open是最后一个特征
            open_prices = scaler.inverse_transform(dummy_open)[:, -1]
            # 修复实际值计算
            dummy_actual = np.zeros((len(y_test), n_features))
            dummy_actual[:, -1] = y_test.flatten()
            actual_prices = scaler.inverse_transform(dummy_actual)[:, -1]
            # 构建结果
            results = pd.DataFrame({
                "date": pd.to_datetime(dates_test),  # 确保转换为datetime类型
                "actual": actual_prices,  # 使用修正后的实际值
                "predicted": pred_prices,
                "open":open_prices
            })
            # 计算指标
            metrics = {
                "stock_code": code,
                "MAE": mean_absolute_error(results.actual, results.predicted),
                "RMSE": np.sqrt(mean_squared_error(results.actual, results.predicted)),
                "R2": r2_score(results.actual, results.predicted)
            }
            all_metrics.append(metrics)
            
            # 保存结果
            results.to_csv(os.path.join(result_dir, "predictions.csv"), index=False)
            
            # 可视化
            plt.figure(figsize=(12, 6))
            plt.plot(results.actual, label="Actual")
            plt.plot(results.predicted, label="Predicted")
            plt.title(f"{code} Stock Price Prediction")
            plt.legend()
            plt.savefig(os.path.join(result_dir, "prediction_plot.png"))
            plt.close()
            
            print(f"{code} 预测完成，结果保存在 {result_dir}")
        except Exception as e:
            print(f"{code} 预测失败: {str(e)}")
            continue
    
    # 保存汇总指标
    pd.DataFrame(all_metrics).to_csv(os.path.join(RESULTS_PATH, "all_metrics.csv"), index=False)
    print("\n所有股票预测完成.汇总指标已保存")
# if __name__ == "__main__":
#     predict_all_stocks()