from flask import Flask, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)

# 仪表盘数据
@app.route('/api/dashboard')
def dashboard():
    # 从performance文件中获取基本指标
    perf_df = pd.read_csv('bs_1/pre_results/shared_pool/performance.csv')
    metrics = perf_df.iloc[0].to_dict()
    
    # 从strategy_results文件中获取资金曲线数据
    strat_df = pd.read_csv('bs_1/pre_results/shared_pool/strategy_results.csv')
    
    # 处理日期格式
    strat_df['date'] = pd.to_datetime(strat_df['date']).dt.strftime('%Y-%m-%d')
    
    # 获取股票数量（从trade_log中统计）
    trade_df = pd.read_csv('bs_1/pre_results/shared_pool/trade_log.csv')
    stock_count = len(trade_df['code'].unique())
    
    return jsonify({
        "stock_count": stock_count,
        "strategy_return": metrics['Total Return'],
        "sharpe_ratio": metrics['Sharpe Ratio'],
        "capital_dates": strat_df['date'].tolist(),
        "strategy_values": strat_df['total'].tolist(),
        # 基准曲线（这里假设使用第一个股票作为基准）
        "benchmark_values": strat_df['true_price'].tolist()
    })

# 股票数据
@app.route('/api/stock/<code>')
def stock(code):
    df = pd.read_csv(f'bs_1/pre_results/{code}/predictions.csv')
    returns = df['true_price'].pct_change()
    return jsonify({
        "dates": df['date'].tolist(),
        "actual_prices": df['true_price'].tolist(),
        "predicted_prices": df['predicted_price'].tolist(),
        "accuracy": 1 - (df['true_price'] - df['predicted_price']).abs().mean() / df['true_price'].mean(),
        "avg_return": returns.mean(),
        "volatility": returns.std()
    })

# 策略数据
@app.route('/api/strategy')
def strategy():
    # 从performance文件中获取指标
    perf_df = pd.read_csv('bs_1/pre_results/shared_pool/performance.csv')
    metrics = perf_df.iloc[0].to_dict()
    
    # 从trade_log文件中获取交易记录
    trade_df = pd.read_csv('bs_1/pre_results/shared_pool/trade_log.csv')
    
    # 转换交易记录中的code为字符串类型
    trade_df['code'] = trade_df['code'].astype(str)
    
    # 格式化指标名称以匹配前端期望
    formatted_metrics = {
        "init_capital": metrics['Initial Capital'],
        "final_value": metrics['Final Value'],
        "total_return": metrics['Total Return'],
        "annual_return": metrics['Annualized Return'],
        "max_drawdown": metrics['Max Drawdown'],
        "sharpe_ratio": metrics['Sharpe Ratio'],
        "win_rate": metrics['Win Rate']
    }
    
    return jsonify({
        "metrics": formatted_metrics,
        "trades": trade_df.to_dict('records')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)