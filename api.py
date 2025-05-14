from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 获取股票列表
@app.route('/api/stocks')
def stock_list():
    # 假设股票数据存储在bs_1/pre_results目录下的各个子目录中
    base_path = 'bs_1/pre_results'
    stocks = []
    
    # 遍历目录获取股票代码和名称
    for dir_name in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, dir_name)) and dir_name != 'shared_pool':
            # 假设目录名就是股票代码
            code = dir_name
            # 这里可以添加从文件或其他地方获取股票名称的逻辑
            # 暂时使用代码作为名称
            name = f"股票{code}"
            stocks.append({"code": code, "name": name})
    
    return jsonify(stocks)

# 仪表盘数据
@app.route('/api/dashboard')
def dashboard():
    # 从performance文件中获取基本指标
    perf_df = pd.read_csv(f'bs_1/pre_results/shared_pool/performance.csv')
    metrics = perf_df.iloc[0].to_dict()
    
    # 从strategy_results文件中获取资金曲线数据并进行数据清洗
    strat_df = pd.read_csv('D:/bs/bs_1/pre_results/shared_pool/strategy_results.csv')
    
    # 数据清洗：按date列去重，保留最后一条记录
    strat_df = strat_df.drop_duplicates(subset=['date'], keep='last')
    
    # 处理日期格式
    strat_df['date'] = pd.to_datetime(strat_df['date']).dt.strftime('%Y-%m-%d')
    
    # 获取股票数量（从trade_log中统计）
    trade_df = pd.read_csv('D:/bs/bs_1/pre_results/shared_pool/trade_log.csv')
    stock_count = len(trade_df['code'].unique())
    
    return jsonify({
        "stock_count": stock_count,
        "strategy_return": metrics['Total Return'],
        "sharpe_ratio": metrics['Sharpe Ratio'],
        "capital_dates": strat_df['date'].tolist(),
        "strategy_values": strat_df['total'].tolist()
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
# 策略数据
@app.route('/api/strategy')
def strategy():
    # 从performance文件中获取指标
    perf_df = pd.read_csv('bs_1/pre_results/shared_pool/performance.csv')
    metrics = perf_df.iloc[0].to_dict()
    
    # 从trade_log文件中获取交易记录，指定code列为字符串类型
    trade_df = pd.read_csv('bs_1/pre_results/shared_pool/trade_log.csv', dtype={'code': str})
    
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