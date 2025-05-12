import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class TradingStrategy:
    def __init__(self, results_dir='bs_1/results', init_capital=1000000, transaction_cost=0.001):
        """
        参数说明：
        - results_dir: 预测结果目录
        - init_capital: 初始资金(默认100万)
        - transaction_cost: 单边交易成本(默认0.1%)
        """
        self.base_path = Path(results_dir)
        self.init_capital = init_capital
        self.trans_cost = transaction_cost
        self.strategy_params = {
            'hold_threshold': 0.03,  # 预测涨幅超过3%买入
            'stop_loss': -0.05,      # 止损线-5%
            'take_profit': 0.08      # 止盈线8%
        }

    def load_predictions(self):
        """加载所有股票的预测数据"""
        stock_dfs = []
        for stock_dir in self.base_path.iterdir():
            if stock_dir.is_dir():
                csv_path = stock_dir / 'predictions.csv'
                if csv_path.exists():
                    df = pd.read_csv(csv_path, parse_dates=['date'], index_col='date')
                    df['code'] = stock_dir.name  # 添加股票代码列
                    stock_dfs.append(df)
        return pd.concat(stock_dfs).sort_index()

    def generate_signals(self, df):
        """生成交易信号"""
        # 计算预测收益率
        df['pred_return'] = df['predicted'].pct_change()
        
        # 生成交易信号
        df['signal'] = np.select(
            [
                df['pred_return'] > self.strategy_params['hold_threshold'],
                (df['actual'] / df['actual'].cummax()) < (1 + self.strategy_params['take_profit']),
                df['pred_return'] < self.strategy_params['stop_loss']
            ],
            [1, -1, -1],  # 满足止盈/止损时卖出
            default=0
        )
        return df

    def backtest_strategy(self, df):
        """策略回测引擎"""
        # 初始化持仓
        df['position'] = 0.0
        df['cash'] = self.init_capital
        df['total'] = float(self.init_capital)
        
        current_position = 0
        for i in range(1, len(df)):
            # 生成交易信号
            if df.iloc[i]['signal'] != df.iloc[i-1]['signal']:
                # 计算交易量（全仓交易）
                trade_value = df.iloc[i-1]['cash']
                trade_shares = trade_value / df.iloc[i]['actual']
                
                # 更新持仓
                current_position = trade_shares if df.iloc[i]['signal'] == 1 else 0
                
                # 计算交易成本
                transaction_cost = trade_value * self.trans_cost
                
                # 更新资金
                df.iat[i, df.columns.get_loc('cash')] = df.iloc[i-1]['cash'] - transaction_cost
                df.iat[i, df.columns.get_loc('position')] = current_position
                
            # 更新市值
            df.iat[i, df.columns.get_loc('total')] = current_position * df.iloc[i]['actual'] + df.iloc[i]['cash']
        
        return df

    def analyze_performance(self, df):
        """绩效分析"""
        # 计算收益率
        df['returns'] = df['total'].pct_change()
        
        # 关键指标
        performance = {
            'Total Return': df['total'].iloc[-1] / self.init_capital - 1,
            'Annualized Return': df['returns'].mean() * 252,
            'Max Drawdown': (df['total'].cummax() - df['total']).max() / df['total'].cummax().max(),
            'Sharpe Ratio': df['returns'].mean() / df['returns'].std() * np.sqrt(252),
            'Win Rate': len(df[df['returns'] > 0]) / len(df)
        }
        return performance

    def plot_results(self, df, stock_code):
        """可视化结果"""
        plt.figure(figsize=(14,7))
        plt.plot(df['total'], label='Strategy')
        plt.plot(df['actual'] / df['actual'].iloc[0] * self.init_capital, label='Buy & Hold')
        plt.title(f'Trading Performance - {stock_code}')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'results/{stock_code}/strategy_performance.png')
        plt.close()

    def run(self):
        """执行完整策略测试"""
        all_performance = []
        
        # 初始化列名模板（确保始终包含必要字段）
        column_template = {
            'Stock': '',
            'Total Return': np.nan,
            'Annualized Return': np.nan,
            'Max Drawdown': np.nan,
            'Sharpe Ratio': np.nan,
            'Win Rate': np.nan
        }

        for stock_dir in self.base_path.iterdir():
            if stock_dir.is_dir():
                stock_code = stock_dir.name
                perf = column_template.copy()
                perf['Stock'] = stock_code
                
                try:
                    # 加载数据
                    df = pd.read_csv(stock_dir/'predictions.csv', parse_dates=['date'], index_col='date')
                    
                    # 策略执行
                    df = self.generate_signals(df)
                    df = self.backtest_strategy(df)
                    
                    # 绩效分析
                    calculated_perf = self.analyze_performance(df)
                    perf.update(calculated_perf)  # 更新计算结果
                    
                    # 保存结果
                    df.to_csv(stock_dir/'strategy_results.csv')
                    self.plot_results(df, stock_code)
                    
                except Exception as e:
                    print(f"股票{stock_code}回测失败: {str(e)}")
                    perf['Error'] = str(e)  # 记录错误信息
                    
                all_performance.append(perf)

        # 生成汇总报告
        summary_df = pd.DataFrame(all_performance)
        summary_df.to_csv(self.base_path/'strategy_summary.csv')
        
        # 打印前检查数据有效性
        if not summary_df.empty:
            print("策略回测完成，关键指标：")
            print(summary_df[['Stock', 'Total Return', 'Sharpe Ratio', 'Max Drawdown']])
        else:
            print("警告：没有成功回测的股票！")
        
        return summary_df

if __name__ == "__main__":
    strategy = TradingStrategy()
    results = strategy.run()