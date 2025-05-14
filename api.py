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
    # 从保存的JSON文件中加载数据
    with open('bs_1/pre_results/shared_pool/api_data.json', 'r') as f:
        api_data = json.load(f)
    return jsonify(api_data['dashboard'])

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
    # 直接读取策略保存的API数据文件
        with open('bs_1/pre_results/shared_pool/api_data.json', 'r') as f:
            api_data = json.load(f)
        
        # 转换交易记录中的code为字符串类型（如果需要）
        trades = pd.DataFrame(api_data['trades'])
        trades['code'] = trades['code'].astype(str)
        
        return jsonify({
            "metrics": api_data['metrics'],
            "trades": trades.to_dict('records')
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)