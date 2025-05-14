import pandas as pd
import matplotlib.pyplot as plt
import os

# 设置支持中文的字体（或使用英文标签）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def plot_data(symbol):
    # 设置路径和参数
    data_path = f"bs_1/stock_data/{symbol}/train.csv"
    output_dir = f"bs_1/stock_data/{symbol}/visualization"
    os.makedirs(output_dir, exist_ok=True)

    # 读取数据
    try:
        df = pd.read_csv(data_path)
        print(f"成功加载数据，形状: {df.shape}")
        
        # 基础检查
        if '日期' not in df.columns or '收盘' not in df.columns:
            raise KeyError("数据必须包含date和close列")
        
        # 转换日期格式
        df['日期'] = pd.to_datetime(df['日期'])
        df.set_index('日期', inplace=True)
        
        # 创建可视化
        plt.figure(figsize=(12, 6))
        df['收盘'].plot(title=f'股票{symbol}价格趋势', color='b')
        plt.xlabel('日期')
        plt.ylabel('收盘价')
        plt.grid(True)
        
        # 添加趋势线（使用天数差作为x值）
        x = (df.index - df.index[0]).days.values.reshape(-1, 1)
        y = df['收盘'].values
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(x, y)
        trend_line = model.predict(x)
        plt.plot(df.index, trend_line, 'r--', label='长期趋势线')
        
        plt.legend()
        
        # 保存图像
        output_path = os.path.join(output_dir, "long_term_trend.png")
        plt.savefig(output_path)
        plt.close()  # 关闭图形，避免内存泄漏
        print(f"可视化结果已保存至: {output_path}")
        
        # 显示统计结论
        start_price = df['收盘'].iloc[0]
        end_price = df['收盘'].iloc[-1]
        growth_rate = (end_price - start_price)/start_price * 100
        print(f"\n趋势分析结果:")
        print(f"• 起始价格: {start_price:.2f}")
        print(f"• 结束价格: {end_price:.2f}")
        print(f"• 累计增长率: {growth_rate:.2f}%")
        print(f"• 趋势斜率: {model.coef_[0]:.8f} (正值表示整体上涨)")
        
    except Exception as e:
        print(f"错误发生: {str(e)}")

if __name__ =="__main__":
    symbols = [f.split(".")[0] for f in os.listdir("bs_1/stock_data")]
    for symbol in symbols:
        print(f"\n正在可视化 {symbol}...")
        plot_data(symbol)