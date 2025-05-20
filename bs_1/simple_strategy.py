import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

class SimpleStrategy:
    def __init__(self, results_dir='bs_1/pre_results', init_capital=1000000):
        self.base_path = Path(results_dir)
        self.init_capital = float(init_capital)
        self.trans_cost = 0.001  # 双边交易成本
        self.params = {
            'buy_threshold': -0.03,
            'sell_threshold': 0.05,
            'max_stocks': 5
        }
        self.trade_log = []

    def load_data(self):
        """修正后的数据加载方法"""
        stock_dfs = []
        for stock_dir in self.base_path.iterdir():
            if not stock_dir.is_dir():
                continue
                
            csv_path = stock_dir / 'predictions.csv'
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                
                # 修改1: 先添加code列再验证
                df['code'] = stock_dir.name  # 从目录名获取股票代码
                
                # 修改2: 调整需要验证的列（排除自动生成的code列）
                required_cols = {'date', 'predicted_price', 'true_price', 'open'} 
                if not required_cols.issubset(df.columns):
                    missing = required_cols - set(df.columns)
                    raise ValueError(f"{stock_dir.name} 缺失关键列: {missing}")
                
                # 处理日期格式
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                stock_dfs.append(df)

        if not stock_dfs:
            raise ValueError("未找到任何有效股票数据")
            
        full_df = pd.concat(stock_dfs).sort_index()
        return full_df

    def generate_signals(self, df):
        """生成交易信号"""
        df = df.copy()
        
        # 修改: 按股票分组计算预测收益
        df['pred_return'] = df.groupby('code')['predicted_price'].pct_change()
        
        # 修改: 使用动态波动率计算阈值（20日滚动波动）
        df['market_vol'] = df.groupby('code')['pred_return'].transform(
            lambda x: x.rolling(20, min_periods=5).std()
        )
        df['buy_thresh'] = self.params['buy_threshold'] - 1.5 * df['market_vol']
        df['sell_thresh'] = self.params['sell_threshold'] + 1.0 * df['market_vol']
        
        # 生成信号
        df['signal'] = np.select(
            condlist=[
                df['pred_return'] < df['buy_thresh'],
                df['pred_return'] > df['sell_thresh']
            ],
            choicelist=[1, -1],
            default=0
        )
        return df

    def backtest(self, df):
        """改进后的回测引擎"""
        df = df.copy()
        df['position'] = 0.0
        df['cash'] = self.init_capital
        df['total'] = self.init_capital
        
        holdings = {}  # {code: shares}
        cash = self.init_capital
        
        # 确保时间序列处理
        for date in pd.to_datetime(df.index.unique()).sort_values():
            date_str = date.strftime('%Y-%m-%d')
            daily_data = df.loc[[date]]
            
            # 卖出处理
            for code, group in daily_data.groupby('code'):
                if code in holdings and group['signal'].iloc[0] == -1:
                    price = group['open'].iloc[0]
                    shares = holdings[code]
                    
                    # 精确计算交易成本
                    sell_value = shares * price
                    cash += sell_value * (1 - self.trans_cost)
                    
                    self.trade_log.append({
                        'date': date_str, 'code': code, 'action': 'sell',
                        'price': price, 'shares': shares, 
                        'value': sell_value, 'cash_after': cash
                    })
                    del holdings[code]
            
            # 买入处理
            buy_candidates = daily_data[
                (daily_data['signal'] == 1) & 
                (~daily_data['code'].isin(holdings.keys()))
            ]
            
            if not buy_candidates.empty and len(holdings) < self.params['max_stocks']:
                max_buy = self.params['max_stocks'] - len(holdings)
                available_per_stock = cash * 0.99 / max_buy  # 保留1%现金
                
                # 按预测收益降序排序选择最佳标的
                sorted_candidates = buy_candidates.sort_values('pred_return', ascending=False)
                for _, row in sorted_candidates.iloc[:max_buy].iterrows():
                    code = row['code']
                    price = row['open']
                    max_shares = available_per_stock / (price * (1 + self.trans_cost))
                    
                    if max_shares >= 100:  # 整手交易限制
                        max_shares = int(max_shares // 100) * 100
                        cost = max_shares * price * (1 + self.trans_cost)
                        cash -= cost
                        holdings[code] = max_shares
                        
                        self.trade_log.append({
                            'date': date_str, 'code': code, 'action': 'buy',
                            'price': price, 'shares': max_shares,
                            'value': max_shares * price, 'cash_after': cash
                        })
            
            # 更新组合价值（修正价格获取方式）
            current_prices = daily_data.set_index('code')['open']
            position_value = sum(
                shares * current_prices.get(code, 0)
                for code, shares in holdings.items()
            )
            df.loc[date, 'cash'] = cash
            df.loc[date, 'total'] = cash + position_value
            
        return df

    def analyze(self, df):
        """改进的绩效分析"""
        daily_total = df.groupby('date')['total'].first()
        
        # 计算收益率
        returns = daily_total.pct_change().fillna(0)
        
        # 修改: 更专业的绩效指标
        return {
            'Initial Capital': self.init_capital,
            'Final Value': daily_total.iloc[-1],
            'Total Return': daily_total.iloc[-1] / self.init_capital - 1,
            'Annualized Return': np.power(daily_total.iloc[-1]/self.init_capital, 252/len(daily_total)) - 1,
            'Max Drawdown': (daily_total.cummax() - daily_total).max() / daily_total.cummax().max(),
            'Sharpe Ratio': np.sqrt(252) * returns.mean() / returns.std(),
            'Total Trades': len(self.trade_log)
        }

    def plot_results(self, df):
        """改进的可视化"""
        save_dir = self.base_path / 'simple_strategy'
        save_dir.mkdir(exist_ok=True)
        
        # 资金曲线
        plt.figure(figsize=(14, 7))
        df.groupby('date')['total'].first().plot(label='Strategy')
        plt.title(f'Strategy Performance (Final: {df["total"].iloc[-1]:.2f})')
        plt.savefig(save_dir/'performance.png')
        plt.close()
        
        # 交易记录
        trade_df = pd.DataFrame(self.trade_log)
        trade_df.to_csv(save_dir/'trades.csv', index=False)
        
        # 持仓分布
        if not trade_df.empty:
            plt.figure(figsize=(10,6))
            trade_df.groupby('code')['value'].sum().plot.pie(autopct='%1.1f%%')
            plt.title('Position Distribution')
            plt.savefig(save_dir/'positions.png')
            plt.close()

    def run(self):
        """执行回测"""
        try:
            data = self.load_data()
            data = self.generate_signals(data)
            results = self.backtest(data)
            performance = self.analyze(results)
            
            print("\n改进版策略回测结果:")
            for k, v in performance.items():
                if isinstance(v, float):
                    print(f"{k:<18}: {v:.4f}" if abs(v) < 1 else f"{k:<18}: {v:.2f}")
                else:
                    print(f"{k:<18}: {v}")
            
            self.plot_results(results)
            return performance
            
        except Exception as e:
            import traceback
            print(f"严重错误: {str(e)}\n{traceback.format_exc()}")
            raise

if __name__ == "__main__":
    strategy = SimpleStrategy()
    strategy.run()