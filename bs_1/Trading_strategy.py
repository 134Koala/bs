import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

class TradingStrategy:
    def __init__(self, results_dir='bs_1/pre_results', init_capital=1000000, transaction_cost=0.001):
        self.base_path = Path(results_dir)
        self.init_capital = float(init_capital)
        self.trans_cost = transaction_cost
        # self.strategy_params = {
        #     'hold_threshold': 0.005,  # 提高信号阈值
        #     'stop_loss': -0.02,      # 收紧止损
        #     'take_profit': 0.03,     # 降低止盈
        #     'max_position_per_stock': 0.08,  # 降低单股仓位
        #     'min_position_days': 5,   # 缩短最小持仓天数
        #     'max_position_days': 20,  # 添加最大持仓天数
        #     'volatility_factor': 0.5  # 波动率调整因子
        # }
        
        self.strategy_params = {
            'hold_threshold': 0.005,  # 更小的阈值
            'stop_loss': -0.03,      # 更宽松的止损
            'take_profit': 0.05,     # 更保守的止盈
            'max_position_per_stock': 0.1,  # 更小的单股仓位
            'min_position_days': 3,    # 最小持仓天数
            'max_position_days': 20,  # 添加最大持仓天数
            'volatility_factor': 0.5  # 波动率调整因子
        }

        # 只对000001和000002两只整体下跌的股票进行操作，调整策略参数
        # self.strategy_params = {
        #     'hold_threshold': -0.003,  # 改为负值阈值，捕捉下跌信号
        #     'stop_loss': 0.02,        # 止损改为正值（对空头而言是上涨止损）
        #     'take_profit': -0.03,     # 止盈改为负值（目标下跌幅度）
        #     'max_position_per_stock': 0.05,  # 进一步降低仓位（下跌风险更大）
        #     'min_position_days': 3,   # 缩短持仓时间（快速获利了结）
        #     'max_position_days': 10,  # 更严格限制最大持仓天数
        #     'volatility_factor': 0.8  # 提高波动率敏感性
        # }
        self.trade_log = []

    def load_predictions(self):
        """加载所有股票的预测数据并合并"""
        stock_dfs = []
        for stock_dir in self.base_path.iterdir():
            if stock_dir.is_dir():
                csv_path = stock_dir / 'predictions.csv'
                if csv_path.exists():
                    try:
                        df = pd.read_csv(csv_path, parse_dates=['date'], index_col='date')
                        df['code'] = stock_dir.name  # 添加股票代码列
                        print(f"Loaded {stock_dir.name}, shape: {df.shape}")  # 调试输出
                        stock_dfs.append(df)
                    except Exception as e:
                        print(f"Error loading {csv_path}: {str(e)}")
                        continue
        
        if not stock_dfs:
            raise ValueError("No valid prediction data found in the directory")
            
        combined = pd.concat(stock_dfs).sort_index()
        print(f"Combined data shape: {combined.shape}")  # 调试输出
        return combined

    def generate_signals(self, df):
        """改进的信号生成函数"""
        grouped = df.groupby('code')
        
        def process_group(group):
            # 计算收益率和波动率
            group['return'] = group['true_price'].pct_change()
            group['pred_return'] = group['predicted_price'].pct_change()
            rolling_std = group['return'].rolling(10).std()
            group['volatility'] = rolling_std.bfill()  # 使用bfill()替代fillna(method='bfill')
            
            # 动态调整阈值
            dynamic_threshold = self.strategy_params['hold_threshold'] * (
                1 + self.strategy_params['volatility_factor'] * group['volatility'])
            
            # 改进的信号条件
            buy_condition = (
                (group['pred_return'] > dynamic_threshold) &
                (group['return'].shift(1) <= self.strategy_params['take_profit'])
            )
            
            # 先计算信号
            group['signal'] = np.select(
                [buy_condition],
                [1],
                default=0
            )
            
            # 然后计算持仓天数
            group['hold_days'] = (group['signal'] == 1).groupby(
                (group['signal'] != 1).cumsum()).cumsum()
            
            # 现在可以计算卖出信号
            sell_condition = (
                (group['return'] >= self.strategy_params['take_profit']) |
                (group['return'] <= self.strategy_params['stop_loss']) |
                (group['hold_days'] >= self.strategy_params['max_position_days'])
            )
            
            # 更新信号列
            group['signal'] = np.select(
                [buy_condition, sell_condition],
                [1, -1],
                default=0
            )
            
            return group
        
        result = grouped.apply(process_group, include_groups=False)
        result['code'] = result.index.get_level_values('code')
        return result.reset_index(level='code', drop=True)

    def backtest_strategy(self, df):
        """共享资金池的回测策略"""
        # 检查必要列是否存在
        # required_columns = ['code', 'signal', 'open', 'true_price', 'hold_days']
        # if not all(col in df.columns for col in required_columns):
        #     missing = [col for col in required_cols if col not in df.columns]
        #     raise ValueError(f"DataFrame缺少必要列: {missing}")
        
        # 添加波动率加权仓位分配
        df['position_weight'] = 1 / (1 + df['volatility'])

        # 初始化资金和持仓
        df = df.copy()
        df['position'] = 0.0  # 持仓股数
        df['cash'] = self.init_capital  # 初始资金
        df['total'] = self.init_capital  # 总资产
        df['trade'] = ''  # 交易记录
        
        # 按日期分组处理
        dates = df.index.unique().sort_values()
        
        # 持仓字典：{股票代码: {'shares': 持仓股数, 'entry_date': 买入日期}}
        positions = {}
        cash = self.init_capital
        
        for date in dates:
            daily_data = df.loc[date]
            
            # 如果是单只股票的数据，转换为DataFrame格式
            if isinstance(daily_data, pd.Series):
                daily_data = pd.DataFrame([daily_data])
            
            # 先处理卖出信号
            for _, row in daily_data.iterrows():
                stock_code = row['code']
                signal = row['signal']
                current_price = row['open']
                hold_days = row['hold_days']
                
                # 卖出条件：收到卖出信号或达到最小持仓天数
                if stock_code in positions:
                    position_info = positions[stock_code]
                    sell_condition = (
                        signal == -1 or 
                        (hold_days >= self.strategy_params['min_position_days'] and 
                         signal != 1)
                    )
                    
                    if sell_condition and position_info['shares'] > 0:
                        # 卖出持仓
                        trade_value = position_info['shares'] * current_price
                        cost = trade_value * self.trans_cost
                        cash += (trade_value - cost)
                        
                        # 记录交易
                        self.trade_log.append({
                            'date': date,
                            'code': stock_code,
                            'action': 'sell',
                            'price': current_price,
                            'shares': position_info['shares'],
                            'value': trade_value,
                            'cost': cost,
                            'hold_days': (date - position_info['entry_date']).days
                        })
                        
                        positions[stock_code]['shares'] = 0.0
            
            # 再处理买入信号
            buy_candidates = daily_data[
                (daily_data['signal'] == 1) & 
                (~daily_data['code'].isin([k for k, v in positions.items() if v['shares'] > 0]))
            ]
            
            if not buy_candidates.empty:
                # 计算可用资金（考虑最大仓位限制）
                available_cash = cash * self.strategy_params['max_position_per_stock']
                
                # 平均分配资金给所有符合条件的股票
                per_stock_cash = available_cash / len(buy_candidates)
                
                for _, row in buy_candidates.iterrows():
                    stock_code = row['code']
                    current_price = row['open']
                    
                    # 计算可买入股数
                    trade_shares = per_stock_cash / current_price
                    cost = trade_shares * current_price * self.trans_cost
                    
                    # 更新持仓和现金
                    positions[stock_code] = {
                        'shares': trade_shares,
                        'entry_date': date
                    }
                    cash -= (trade_shares * current_price + cost)
                    
                    # 记录交易
                    self.trade_log.append({
                        'date': date,
                        'code': stock_code,
                        'action': 'buy',
                        'price': current_price,
                        'shares': trade_shares,
                        'value': trade_shares * current_price,
                        'cost': cost,
                        'hold_days': 0
                    })
            
            # 计算当前总资产
            total_value = cash
            for stock_code, pos_info in positions.items():
                if pos_info['shares'] > 0:
                    # 检查该股票在当天是否有数据
                    stock_data = daily_data[daily_data['code'] == stock_code]
                    if not stock_data.empty:
                        stock_price = stock_data['open'].values[0]
                        total_value += pos_info['shares'] * stock_price
            
            # 更新DataFrame
            for stock_code in daily_data['code'].unique():
                mask = (df.index == date) & (df['code'] == stock_code)
                if stock_code in positions:
                    df.loc[mask, 'position'] = positions[stock_code]['shares']
                df.loc[mask, 'cash'] = cash
                df.loc[mask, 'total'] = total_value
        
        return df

    def analyze_performance(self, df, risk_free_rate=0.0, days_per_year=252):
        """绩效分析"""
        # 按日期去重，确保总资产正确
        daily_totals = df.groupby(df.index)['total'].first()
        
        # 计算日收益率并去除缺失值
        returns = daily_totals.pct_change().dropna()
        
        # 计算夏普比率
        if returns.std() == 0:
            print("Warning: Standard deviation of returns is zero, setting Sharpe Ratio to 0")
            sharpe_ratio = 0
        else:
            # 考虑无风险利率并年化
            excess_return = returns.mean() - risk_free_rate / days_per_year
            sharpe_ratio = excess_return / returns.std() * np.sqrt(days_per_year)
        # 计算累计收益
        cumulative_return = daily_totals.iloc[-1] / self.init_capital - 1
        
        # 年化收益率
        annualized_return = (1 + cumulative_return)**(252/len(daily_totals)) - 1
        
        # 最大回撤
        cummax = daily_totals.cummax()
        drawdown = (cummax - daily_totals) / cummax
        max_drawdown = drawdown.max()
        
        # 交易统计
        trade_df = pd.DataFrame(self.trade_log)
        
        # 计算赢率 - 改进版
        # 改进的胜率计算
        if not trade_df.empty:
            # 按股票代码分组，计算每笔交易的盈亏
            trade_groups = trade_df.groupby('code')
            profitable_trades = 0
            total_paired_trades = 0

            for code, group in trade_groups:
                buys = group[group['action'] == 'buy']
                sells = group[group['action'] == 'sell']
                
                # 确保买入和卖出记录数量匹配
                min_trades = min(len(buys), len(sells))
                if min_trades == 0:
                    continue
                    
                # 计算最近的min_trades笔交易的盈亏
                for i in range(min_trades):
                    buy_value = buys.iloc[i]['value']
                    sell_value = sells.iloc[i]['value']
                    if sell_value > buy_value:
                        profitable_trades += 1
                    total_paired_trades += 1

            win_rate = profitable_trades / total_paired_trades if total_paired_trades > 0 else 0
        else:
            win_rate = 0
        
        performance = {
            'Initial Capital': self.init_capital,
            'Final Value': daily_totals.iloc[-1],
            'Total Return': cumulative_return,
            'Annualized Return': annualized_return,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Win Rate': win_rate,
            'Total Trades': len(self.trade_log),
            'Avg Hold Days': trade_df[trade_df['action'] == 'sell']['hold_days'].mean() if not trade_df.empty else 0
        }
        return performance

    def plot_results(self, df):
        """可视化结果"""
        save_dir = self.base_path / 'shared_pool'
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Get unique daily totals
        daily_totals = df[~df.index.duplicated(keep='first')]['total']
        
        plt.figure(figsize=(14, 7))
        plt.plot(daily_totals.index, daily_totals.values, label='Strategy')
        
        # Calculate and plot benchmark
        grouped = df.groupby('code')
        benchmark = pd.DataFrame(index=df.index.unique().sort_values())
        
        for name, group in grouped:
            benchmark[name] = group['true_price'] / group['true_price'].iloc[0] * (self.init_capital / len(grouped))
        
        benchmark['total'] = benchmark.sum(axis=1)
        plt.plot(benchmark.index, benchmark['total'].values, label='Equal Weight Benchmark')
        
        plt.title('Shared Pool Trading Performance')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(save_dir/'strategy_performance.png', dpi=300)
        plt.close()
        
        # 保存交易日志
        if self.trade_log:
            trade_df = pd.DataFrame(self.trade_log)
            trade_df.to_csv(save_dir/'trade_log.csv', index=False)

    def run(self):
        """执行完整策略测试"""
        try:
            # 加载所有股票数据
            print("Loading prediction data...")
            all_data = self.load_predictions()

            # print(f"数据形状为：{all_data.shape}")  # 使用f-string格式化
            # print("头部数据：")
            # print(all_data.head(30))  # 调用head()方法并单独打印
            # 生成交易信号
            print("Generating trading signals...")
            all_data = self.generate_signals(all_data)
            
            # 执行回测
            print("Running backtest...")
            results = self.backtest_strategy(all_data)
            
            # 保存结果
            save_dir = self.base_path / 'shared_pool'
            save_dir.mkdir(parents=True, exist_ok=True)
            results.to_csv(save_dir/'strategy_results.csv')
            
            # 绩效分析
            print("Analyzing performance...")
            performance = self.analyze_performance(results,risk_free_rate=0.02)

            # 将字典转换为DataFrame再保存
            performance_df = pd.DataFrame([performance])
            performance_df.to_csv(save_dir/'performance.csv', index=False)
            
            # 可视化
            print("Generating plots...")
            self.plot_results(results)
            
            # 打印结果
            print("\n共享资金池策略回测完成，关键指标：")
            for k, v in performance.items():
                if isinstance(v, float):
                    print(f"{k:<20}: {v:.4f}")
                else:
                    print(f"{k:<20}: {v}")
            
            return performance
            
        except Exception as e:
            print(f"Error running strategy: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        strategy = TradingStrategy()
        results = strategy.run()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")