import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class TradingStrategy:
    def __init__(self, results_dir='bs_1/results', init_capital=1000000, transaction_cost=0.001):
        self.base_path = Path(results_dir)
        self.init_capital = float(init_capital)  # 确保浮点数
        self.trans_cost = transaction_cost
        self.strategy_params = {
            'hold_threshold': 0.03,  # 预测值超过阈值买入
            'stop_loss': -0.05,      # 最大回撤止损
            'take_profit': 0.08      # 止盈线
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
        df['cummax'] = df['actual'].cummax()
        df['drawdown'] = (df['cummax'] - df['actual']) / df['cummax']
        
        df['signal'] = np.select(
            [
                df['predicted'] > self.strategy_params['hold_threshold'],
                df['drawdown'] >= abs(self.strategy_params['take_profit']),
                df['drawdown'] >= abs(self.strategy_params['stop_loss'])
            ],
            [1, -1, -1],
            default=0
        )
        return df

    def backtest_strategy(self, df):
        df = df.copy()
        df['position'] = 0.0
        df['cash'] = float(self.init_capital)
        df['total'] = float(self.init_capital)
        
        current_position = 0.0
        for i in range(1, len(df)):
            current_price = df.iloc[i]['open']  # 假设数据包含开盘价
            
            # 交易决策基于前一天信号
            prev_signal = df.iloc[i-1]['signal']
            
            if prev_signal != 0:
                if prev_signal == 1 and current_position == 0:  # 买入
                    available_cash = df.iloc[i-1]['cash']
                    trade_shares = available_cash / current_price
                    cost = trade_shares * current_price * self.trans_cost
                    current_position = trade_shares
                    df.iat[i, df.columns.get_loc('cash')] = available_cash - cost
                    
                elif prev_signal == -1 and current_position > 0:  # 卖出
                    trade_value = current_position * current_price
                    cost = trade_value * self.trans_cost
                    df.iat[i, df.columns.get_loc('cash')] += (trade_value - cost)
                    current_position = 0.0
                    
            # 更新市值
            df.iat[i, df.columns.get_loc('position')] = current_position
            df.iat[i, df.columns.get_loc('total')] = current_position * current_price + df.iat[i, df.columns.get_loc('cash')]
        
        return df

    def analyze_performance(self, df):
        """绩效分析"""
        df['returns'] = df['total'].pct_change()
        
        # 计算累计收益
        cumulative_return = df['total'].iloc[-1] / self.init_capital - 1
        
        # 年化收益率
        annualized_return = (1 + cumulative_return)**(252/len(df)) - 1
        
        # 夏普比率（假设无风险利率为0）
        sharpe_ratio = df['returns'].mean() / df['returns'].std() * np.sqrt(252)
        
        performance = {
            'Total Return': cumulative_return,
            'Annualized Return': annualized_return,
            'Max Drawdown': (df['total'].cummax() - df['total']).max() / df['total'].cummax().max(),
            'Sharpe Ratio': sharpe_ratio,
            'Win Rate': len(df[df['returns'] > 0]) / len(df)
        }
        return performance

    def plot_results(self, df, stock_code):
        save_dir = self.base_path / stock_code
        save_dir.mkdir(parents=True, exist_ok=True)
        # ...其余绘图代码不变...3
        """可视化结果"""
        plt.figure(figsize=(14,7))
        plt.plot(df['total'], label='Strategy')
        plt.plot(df['actual'] / df['actual'].iloc[0] * self.init_capital, label='Buy & Hold')
        plt.title(f'Trading Performance - {stock_code}')
        plt.legend()
        plt.grid(True)
        plt.savefig(save_dir/'strategy_performance.png')
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