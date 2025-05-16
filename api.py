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
    
    try:
        # 遍历目录获取股票代码和名称
        for dir_name in os.listdir(base_path):
            dir_path = os.path.join(base_path, dir_name)
            if os.path.isdir(dir_path) and dir_name != 'shared_pool':
                # 假设目录名就是股票代码
                code = dir_name
                # 这里可以添加从文件或其他地方获取股票名称的逻辑
                # 暂时使用代码作为名称
                name = f"股票{code}"
                stocks.append({"code": code, "name": name})
    except Exception as e:
        print(f"Error getting stock list: {e}")
    
    return jsonify(stocks)

# 仪表盘数据
@app.route('/api/dashboard')
def dashboard():
    try:
        # 从performance文件中获取基本指标
        perf_df = pd.read_csv('bs_1/pre_results/shared_pool/performance.csv')
        metrics = perf_df.iloc[0].to_dict()
        
        # 从strategy_results文件中获取资金曲线数据并进行数据清洗
        strat_df = pd.read_csv('bs_1/pre_results/shared_pool/strategy_results.csv')
        
        # 数据清洗：按date列去重，保留最后一条记录
        strat_df = strat_df.drop_duplicates(subset=['date'], keep='last')
        
        # 处理日期格式
        strat_df['date'] = pd.to_datetime(strat_df['date']).dt.strftime('%Y-%m-%d')
        
        # 获取股票数量（从trade_log中统计）
        trade_df = pd.read_csv('bs_1/pre_results/shared_pool/trade_log.csv')
        stock_count = len(trade_df['code'].unique())
        
        return jsonify({
            "stock_count": stock_count,
            "strategy_return": float(metrics.get('Total Return', 0)),
            "sharpe_ratio": float(metrics.get('Sharpe Ratio', 0)),
            "capital_dates": strat_df['date'].tolist(),
            "strategy_values": strat_df['total'].astype(float).tolist()
        })
    except Exception as e:
        print(f"Error in dashboard endpoint: {e}")
        return jsonify({
            "stock_count": 0,
            "strategy_return": 0,
            "sharpe_ratio": 0,
            "capital_dates": [],
            "strategy_values": []
        })

# 股票数据
@app.route('/api/stock/<code>')
def stock(code):
    try:
        df = pd.read_csv(f'bs_1/pre_results/{code}/predictions.csv')
        returns = df['true_price'].pct_change().fillna(0)
        
        accuracy = 1 - (df['true_price'] - df['predicted_price']).abs().mean() / df['true_price'].mean()
        if not isinstance(accuracy, float) or pd.isna(accuracy):
            accuracy = 0
            
        return jsonify({
            "dates": df['date'].astype(str).tolist(),
            "actual_prices": df['true_price'].astype(float).tolist(),
            "predicted_prices": df['predicted_price'].astype(float).tolist(),
            "accuracy": float(accuracy),
            "avg_return": float(returns.mean()),
            "volatility": float(returns.std())
        })
    except Exception as e:
        print(f"Error in stock endpoint for code {code}: {e}")
        return jsonify({
            "dates": [],
            "actual_prices": [],
            "predicted_prices": [],
            "accuracy": 0,
            "avg_return": 0,
            "volatility": 0
        })

# 股票评估指标
@app.route('/api/stock_metrics/<code>')
def stock_metrics(code):
    try:
        # 读取CSV并强制转换股票代码为字符串（避免前导0丢失）
        df = pd.read_csv('bs_1/pre_results/shared_pool/all_metrics_summary.csv')
        df['Symbol'] = df['Symbol'].astype(str).str.zfill(6)  # 补全6位代码
        
        # 处理请求中的代码（统一为6位字符串）
        request_code = str(code).strip().zfill(6)
        
        # 查找匹配项
        result = df[df['Symbol'] == request_code]
        if result.empty:
            return jsonify({"error": f"股票 {request_code} 不存在", "available_codes": df['Symbol'].head().tolist()}), 404
            
        return jsonify(result.iloc[0].to_dict())
        
    except FileNotFoundError:
        return jsonify({"error": "指标文件路径错误"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 策略数据
@app.route('/api/strategy')
def strategy():
    try:
        # 从performance文件中获取指标
        perf_df = pd.read_csv('bs_1/pre_results/shared_pool/performance.csv')
        metrics = perf_df.iloc[0].to_dict()
        
        # 从trade_log文件中获取交易记录，指定code列为字符串类型
        trade_df = pd.read_csv('bs_1/pre_results/shared_pool/trade_log.csv', dtype={'code': str})
        
        # 格式化指标名称以匹配前端期望
        formatted_metrics = {
            "init_capital": float(metrics.get('Initial Capital', 0)),
            "final_value": float(metrics.get('Final Value', 0)),
            "total_return": float(metrics.get('Total Return', 0)),
            "annual_return": float(metrics.get('Annualized Return', 0)),
            "max_drawdown": float(metrics.get('Max Drawdown', 0)),
            "sharpe_ratio": float(metrics.get('Sharpe Ratio', 0)),
            "win_rate": float(metrics.get('Win Rate', 0))
        }
        
        return jsonify({
            "metrics": formatted_metrics,
            "trades": trade_df.to_dict('records')
        })
    except Exception as e:
        print(f"Error in strategy endpoint: {e}")
        return jsonify({
            "metrics": {
                "init_capital": 0,
                "final_value": 0,
                "total_return": 0,
                "annual_return": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "win_rate": 0
            },
            "trades": []
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)