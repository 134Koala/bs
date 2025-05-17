基于GRU模型的股票价格预测系统

项目概述
本项目是一个基于深度学习的股票价格预测系统，使用GRU（门控循环单元）神经网络模型对股票价格进行预测，并结合量化交易策略进行回测验证。系统包含完整的数据获取、特征工程、模型训练、预测评估和交易策略实现流程。

系统功能
​数据获取模块​
从AKShare获取股票历史数据
自动划分训练集和测试集
支持批量获取多只股票数据
​特征工程模块​
技术指标计算（MA、RSI、MACD等）
时间序列特征构建
数据标准化处理
防止数据泄露的特征处理
​模型构建模块​
改进的GRU神经网络架构
双向GRU层捕捉前后文信息
自定义注意力机制
残差连接和批量归一化
​预测评估模块​
多种评估指标计算（MAE、MSE、RMSE、R²）
预测结果可视化
价格走势对比图表
​交易策略模块​
基于预测信号的交易策略
动态仓位管理
止损止盈机制
绩效分析（夏普比率、最大回撤等）
​可视化界面​
资金曲线展示
股票预测结果对比
交易记录查看
策略绩效指标展示
技术栈
​编程语言: Python
​深度学习框架: Keras
​数据处理: Pandas, NumPy
​数据获取: AKShare
​特征工程: Scikit-learn
​可视化: Matplotlib, Chart.js
​Web界面: Flask, Bootstrap

项目结构
markdown
BS/  (项目根文件夹)
├── bs_1/  (主Python项目目录)
│   ├── __pycache__/  (Python缓存目录)
|   ├── compare(lstm与随机森林模型比较代码存放目录)
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
使用方法
​数据准备​
在stock_list.txt中配置需要预测的股票代码
运行data_get.py获取历史数据
​特征工程​
运行data_processing.py进行特征提取和标准化
​模型训练​
运行model.py训练GRU预测模型
​预测评估​
运行prediction.py生成预测结果和评估指标
​策略回测​
运行Trading_strategy.py进行策略回测
​启动Web界面​
运行app.py启动Flask服务
访问http://localhost:5000查看可视化界面
创新点
​改进的GRU架构​：结合双向GRU和注意力机制，提升模型对时间序列特征的捕捉能力
​防数据泄露设计​：严格区分训练集和测试集的特征处理流程
​动态交易策略​：基于波动率调整仓位和交易阈值
​完整系统集成​：从数据获取到策略回测的端到端解决方案
未来改进方向
加入更多基本面因子
实现多时间尺度预测
优化交易策略参数
增加实时数据更新功能
开发更丰富的可视化分析功能
学术引用
本项目参考了以下领域的研究成果：

深度学习在金融时间序列预测中的应用
注意力机制在序列建模中的改进
量化交易策略设计与评估方法
请在这份readme文档中添加我的部分代码以明确功能
基于GRU模型的股票价格预测系统
项目概述
本项目是一个基于深度学习的股票价格预测系统，使用GRU（门控循环单元）神经网络模型对股票价格进行预测，并结合量化交易策略进行回测验证。系统包含完整的数据获取、特征工程、模型训练、预测评估和交易策略实现流程。

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
