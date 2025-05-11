from keras.models import Model
from keras.layers import Input, GRU, Dense, Multiply, Attention
from keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import os
from keras.layers import Bidirectional, Conv1D, BatchNormalization, Dropout
from keras.layers import Dot, Concatenate, Activation  # 用于自定义注意力机制
from keras.optimizers import Adam  # 替换原有优化器
from keras.metrics import RootMeanSquaredError  # 新增评估指标
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

def train_model(symbol):
    # 加载数据
    path = f"processing_data/{symbol}/"
    X_train = np.load(f"{path}X_train.npy")
    y_train = np.load(f"{path}y_train.npy")
    X_val = np.load(f"{path}X_val.npy")
    y_val = np.load(f"{path}y_val.npy")
    
    # 模型参数
    input_shape = (X_train.shape[1], X_train.shape[2])
    model = build_improved_model(input_shape)
    
    # 训练配置
    callbacks = [
        EarlyStopping(patience=10, restore_best_weights=True),
        ModelCheckpoint(f"model/{symbol}_best.h5", save_best_only=True)
    ]
    
    # 训练模型
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=2
    )

if __name__ == "__main__":
    symbols = os.listdir("processing_data")
    os.makedirs("model", exist_ok=True)
    for symbol in symbols:
        train_model(symbol)