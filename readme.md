基于GRU模型的股票预测与量化交易系统
项目概述
本项目是一个完整的股票预测和量化交易系统，使用GRU（门控循环单元）神经网络模型对股票价格进行预测，并基于预测结果实现自动化交易策略。系统包含数据获取、数据处理、模型训练、预测分析、策略回测及可视化展示等完整功能模块，旨在帮助投资者进行数据驱动的投资决策。

系统架构
项目采用前后端分离架构，包含以下核心组件：

数据层：负责股票数据的获取与预处理
模型层：基于GRU神经网络实现股票价格预测
策略层：实现量化交易策略并进行回测
展示层：提供Web界面展示预测结果和策略表现
项目结构
BS/  (项目根文件夹)
├── bs_1/  (主Python项目目录)
│   ├── __pycache__/  (Python缓存目录)
|   ├── compare/  (LSTM与随机森林模型比较代码存放目录)
│   ├── model/  (模型存储目录)
│   ├── pre_results/  (预测结果存储目录)
│   ├── processing_data/  (处理后的数据存储目录)
│   ├── stock_data/  (原始股票数据存储目录)
│   ├── data_get.py  (数据获取脚本)
│   ├── data_processing.py  (数据处理脚本)
│   ├── main.py  (主程序入口)
│   ├── model.py  (模型定义脚本)
│   ├── prediction.py  (预测脚本)
│   ├── stock_list.txt  (股票代码列表)
│   └── Trading_strategy.py  (交易策略脚本)
│   
├── frontend/  (前端目录)
│   ├── css/  (样式表目录)
│   ├── js/  (JavaScript脚本目录)
│   ├── index.html  (前端主页面)
│   └── api.py  (前端API接口)
│
└── readme.md  (项目说明文档)
功能模块详解
1. 数据获取与处理 (data_get.py, data_processing.py)
数据获取：从金融数据源获取指定股票的历史交易数据
数据预处理：处理缺失值、标准化数据、生成时间序列特征
数据分割：将数据集分为训练集、验证集和测试集
数据处理后存放在processing_data目录，便于模型训练和预测使用。

2. 模型定义与训练 (model.py, main.py)
模型架构：基于GRU（门控循环单元）构建的深度学习模型
模型训练：使用处理后的训练数据训练预测模型
模型评估：在验证集上评估模型性能，调整超参数
模型保存：将训练好的模型保存至model目录
3. 股票预测 (prediction.py)
加载模型：加载训练好的GRU模型
生成预测：对测试数据进行预测
评估指标：计算MAE、MSE、RMSE、R²等评估指标
结果可视化：生成预测结果与实际价格的对比图
保存结果：将预测结果保存至pre_results目录
4. 交易策略 (Trading_strategy.py)
信号生成：基于预测价格生成买卖信号
仓位管理：实现动态仓位调整和风险控制
策略回测：对历史数据进行回测，评估策略表现
性能分析：计算收益率、最大回撤、夏普比率等指标
策略特点：

动态阈值调整：根据市场波动性自动调整交易阈值
多维度风险控制：实现止损、止盈、最大持仓天数限制
波动率调整：使用波动率因子调整交易信号强度
5. 模型比较 (compare/)
对比GRU模型与LSTM、随机森林等其他模型的预测性能
分析不同模型的优缺点和适用场景
6. Web界面 (frontend/)
前端界面：基于HTML、CSS、JavaScript构建交互式界面
API接口：使用Flask实现后端数据服务
数据可视化：展示预测结果、资金曲线、交易记录等
使用指南
环境要求
Python 3.8+
TensorFlow 2.x
Keras
NumPy, Pandas, Matplotlib
Flask
Bootstrap 5.x
Chart.js
运行步骤
获取股票数据：

cd bs_1
python data_get.py
数据预处理：

python data_processing.py
训练模型：

python model.py
进行预测：

python prediction.py
回测策略：

python Trading_strategy.py
或者：

python main.py --all 训练预测所有股票

python main.py --symbol [symbol] 指定训练该股票
启动Web服务：

cd ../frontend
python api.py
访问Web界面：
在浏览器中打开 http://localhost:5000

核心技术
深度学习：使用GRU神经网络建模时间序列数据
数据标准化：采用适合金融数据的标准化方法
过拟合防控：实现Dropout和早停等技术防止模型过拟合
量化交易策略：基于预测结果设计交易规则和风险控制
可视化技术：使用Chart.js实现交互式数据可视化
系统评估指标
模型预测指标
MAE (平均绝对误差)：衡量预测值与实际值的平均绝对差异
MSE (均方误差)：衡量预测值与实际值的平均平方差异
RMSE (均方根误差)：MSE的平方根，与原始数据单位一致
R² (决定系数)：表示模型解释的方差比例，越接近1越好
策略绩效指标
总收益率：策略在回测期内的总收益率
年化收益率：收益率的年化表示
最大回撤：策略期间最大的资金下跌幅度
夏普比率：评估风险调整后的收益指标
胜率：盈利交易占总交易的比例
项目特色
完整的量化投资流程：从数据获取到交易决策的端到端解决方案
多模型对比分析：通过compare目录下的代码比较不同模型性能
动态策略参数：根据市场波动性自动调整策略参数
直观的可视化界面：提供丰富的图表展示预测和策略结果
模块化设计：各功能模块相对独立，便于维护和扩展
未来改进方向
增强数据源：接入更多数据源，添加基本面和宏观经济数据
特征工程优化：引入更多技术指标和特征选择方法
集成学习：实现多模型集成预测，提高预测稳定性
策略优化：增加更多交易策略和参数优化方法
实时交易接口：实现与实盘交易系统的对接
注意事项
本系统仅供学习和研究使用，不构成投资建议
金融市场受多种复杂因素影响，模型预测存在一定局限性
回测结果不代表未来表现，实际投资需谨慎评估风险

系统功能
1. 数据获取模块
python
复制
# data_get.py
def fetch_stock_data():
    # 读取股票列表
    with open("bs_1/stock_list.txt", "r") as f:
        symbols = [line.strip() for line in f]
    
    # 日期范围设置
    date_ranges = {
        'train': ('20100101', '20191231'),
        'test': ('20200101', '20241231')
    }
    
    # 批量获取数据
    for symbol in symbols:
        try:
            # 创建个股目录
            stock_dir = f"bs_1/stock_data/{symbol}"
            os.makedirs(stock_dir, exist_ok=True)
            
            # 分别获取训练集和测试集
            for dataset in ['train', 'test']:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=date_ranges[dataset][0],
                    end_date=date_ranges[dataset][1],
                    adjust="hfq"
                )
                # 添加基础波动率特征
                df["volatility"] = df["最高"] - df["最低"]
                df.to_csv(f"{stock_dir}/{dataset}.csv", index=False)
            
            print(f"{symbol} 数据获取成功")
功能说明：

从AKShare获取股票历史数据
自动划分训练集(2010-2019)和测试集(2020-2024)
添加基础波动率特征
支持批量获取多只股票数据
2. 特征工程模块
python
复制
# data_processing.py
def compute_features(df, mode='train'):
    """特征工程（防止数据泄露版本）"""
    # 基础特征
    features = ['开盘', '收盘', '最高', '最低', '成交量', 'volatility']
    
    # 移动平均线
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA10'] = df['收盘'].rolling(10).mean()
    
    # RSI指标
    delta = df['收盘'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (avg_gain / (avg_loss + 1e-8))))
    
    # MACD指标
    ema12 = df['收盘'].ewm(span=12, adjust=False).mean()
    ema26 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    
    # 量价比（成交量/收盘价）
    df['volume_price_ratio'] = df['成交量'] / (df['收盘'] + 1e-8)
功能说明：

计算多种技术指标(MA、RSI、MACD等)
构建时间序列特征
防止数据泄露的特征处理
数据标准化处理
3. 模型构建模块
python
复制
# model.py
def build_improved_model(input_shape):
    inputs = Input(shape=input_shape)
    
    # 双向GRU捕捉前后文信息
    gru_out = Bidirectional(GRU(128, return_sequences=True))(inputs)
    
    # 改进的注意力机制
    query = Dense(128)(gru_out)
    key = Dense(128)(gru_out)
    attention = Dot(axes=[2, 2])([query, key])
    attention = Activation('softmax')(attention)
    context = Dot(axes=[2, 1])([attention, gru_out])
    
    # 加入残差连接
    merged = Concatenate()([gru_out, context])
    
    # 时间序列特征提取
    conv1 = Conv1D(64, 3, activation='relu', padding='same')(merged)
    conv1 = BatchNormalization()(conv1)
    
    # 输出层
    output = Dense(64, activation='relu')(conv1[:, -1, :])
    output = Dropout(0.2)(output)
    output = Dense(1)(output)
    
    model = Model(inputs=inputs, outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), 
                 loss="mse",
                 metrics=[RootMeanSquaredError()])
    return model
功能说明：

改进的GRU神经网络架构
双向GRU层捕捉前后文信息
自定义注意力机制
残差连接和批量归一化
使用Adam优化器和RMSE评估指标
4. 预测评估模块
python
复制
# prediction.py
def calculate_metrics(true, pred):
    """计算量化指标"""
    mae = mean_absolute_error(true, pred)
    mse = mean_squared_error(true, pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(true, pred)
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R2': r2
    }

def predict_stock(symbol):
    # 加载数据
    X_test = np.load(f"{data_path}/X_test.npy")
    y_test = np.load(f"{data_path}/y_test.npy")
    
    # 生成预测
    predictions = model.predict(X_test)
    
    # 反标准化
    dummy = np.zeros((len(predictions), full_scaler.n_features_in_))
    dummy[:, 1] = predictions.flatten()
    pred_prices = full_scaler.inverse_transform(dummy)[:, 1]
    
    # 计算指标
    metrics = calculate_metrics(true_prices, pred_prices)
    
    # 保存结果
    result_df = pd.DataFrame({
        'date': test_dates,
        'open': open_prices,
        'true_price': true_prices,
        'predicted_price': pred_prices
    })
功能说明：

多种评估指标计算(MAE、MSE、RMSE、R²)
预测结果可视化
价格走势对比图表
结果保存为CSV文件
5. 交易策略模块
python
复制
# Trading_strategy.py
def generate_signals(self, df):
    """改进的信号生成函数"""
    # 计算收益率和波动率
    df['return'] = df['true_price'].pct_change()
    df['pred_return'] = df['predicted_price'].pct_change()
    rolling_std = df['return'].rolling(10).std()
    df['volatility'] = rolling_std.bfill()
    
    # 动态调整阈值
    dynamic_threshold = self.strategy_params['hold_threshold'] * (
        1 + self.strategy_params['volatility_factor'] * df['volatility'])
    
    # 信号条件
    buy_condition = (
        (df['pred_return'] > dynamic_threshold) &
        (df['return'].shift(1) <= self.strategy_params['take_profit'])
    )
    
    # 持仓天数计算
    df['hold_days'] = (df['signal'] == 1).groupby(
        (df['signal'] != 1).cumsum()).cumsum()
    
    # 卖出信号
    sell_condition = (
        (df['return'] >= self.strategy_params['take_profit']) |
        (df['return'] <= self.strategy_params['stop_loss']) |
        (df['hold_days'] >= self.strategy_params['max_position_days'])
    )
    
    # 生成信号
    df['signal'] = np.select(
        [buy_condition, sell_condition],
        [1, -1],
        default=0
    )
功能说明：

基于预测信号的交易策略
动态仓位管理
止损止盈机制
波动率调整的交易阈值
绩效分析(夏普比率、最大回撤等)
6. Web可视化界面
python
复制
# app.py
@app.route('/api/stock/<code>')
def stock(code):
    try:
        df = pd.read_csv(f'bs_1/pre_results/{code}/predictions.csv')
        returns = df['true_price'].pct_change().fillna(0)
        
        accuracy = 1 - (df['true_price'] - df['predicted_price']).abs().mean() / df['true_price'].mean()
        
        return jsonify({
            "dates": df['date'].astype(str).tolist(),
            "actual_prices": df['true_price'].astype(float).tolist(),
            "predicted_prices": df['predicted_price'].astype(float).tolist(),
            "accuracy": float(accuracy),
            "avg_return": float(returns.mean()),
            "volatility": float(returns.std())
        })
功能说明：

Flask提供的RESTful API接口
资金曲线展示
股票预测结果对比
交易记录查看
策略绩效指标展示

模型预测量化指标：
Symbol,MAE,MSE,RMSE,R2
000001,97.03270915956564,24083.91548872354,155.18993359339885,0.933238699345387
000002,90.91426564590671,13770.978885011618,117.34981416692409,0.9787867750994936
000300,44.42777613544329,3825.8179132357873,61.85319646740811,0.9897735446786555
000888,2.608914004315721,14.368323963763292,3.7905572101952627,0.8874267002774443
000983,3.1618161162147755,15.688883210130172,3.9609194904883096,0.9687706204767169
601001,1.5685980643779427,3.9246402845724506,1.981070489551659,0.9544187833666962
601088,0.7636989742894751,1.0454421560629668,1.022468657741139,0.992110912827644
601898,0.38273315154506754,0.29938625261323737,0.5471619985097991,0.9717521051891564

回测量化指标：
Initial Capital,Final Value,Total Return,Annualized Return,Max Drawdown,Sharpe Ratio,Win Rate,Total Trades,Avg Hold Days
1000000.0,1387450.1481400637,0.38745014814006384,0.07314310721746797,0.06597161659508395,0.6600423970478723,0.5813953488372093,524,39.593023255813954


另外在有模块单独构建lstm模型和随机森林模型，对沪深300的数据进行了预测，预测结果指标如下：
Model,MSE,RMSE,MAE,MAPE,R2
lstm,14386.798294526974,119.94498028065608,89.45307409806375,2.0073233918557203,0.9615386349210384
rf,29613.60529793094,172.086040392389,91.51387339606552,1.8548034818875856,0.920831608162514
lstm,13112.772058147671,114.51101282473958,84.12226810660962,1.8745885736308,0.9649445899636
rf,29613.60529793097,172.0860403923891,91.51387339606562,1.854803481887588,0.9208316081625136
lstm,9895.734239494515,99.4773051479307,73.77084477656108,1.6624061063143685,0.973544951453558
rf,29613.605297930964,172.08604039238907,91.51387339606558,1.8548034818875871,0.9208316081625136
lstm,33414.548922244125,182.79646857158957,134.40808701917297,2.9393031551423987,0.9106702451277048
rf,29613.605297930964,172.08604039238907,91.51387339606558,1.8548034818875871,0.9208316081625137
