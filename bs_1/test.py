from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='Improved Forecasting Model', 
              format='png',
              graph_attr={'rankdir': 'LR', 'dpi': '300', 'splines': 'ortho'},
              node_attr={'shape': 'record', 'fontname': 'Helvetica'})

# 输入层
with dot.subgraph(name='cluster_input') as c:
    c.attr(color='lightgray', style='filled')
    c.node('input', '{Input Layer|(timesteps × features)}')
    c.attr(label='Input Sequence')

# 特征提取层
with dot.subgraph(name='cluster_features') as c:
    c.node('gru', '{Bidirectional GRU|128 units|return_sequences=True}')
    c.node('conv', '{1D Conv|64 filters|kernel=3|ReLU}')
    c.node('bn', 'BatchNorm')
    c.attr(label='Feature Extraction')

# 注意力机制
with dot.subgraph(name='cluster_attention') as c:
    c.node('query', 'Dense(128)')
    c.node('key', 'Dense(128)')
    c.node('dot1', 'Dot[axes=(2,2)]')
    c.node('softmax', 'Softmax')
    c.node('context', 'Context Vector')
    c.attr(label='Attention Mechanism', color='blue')

# 输出层
with dot.subgraph(name='cluster_output') as c:
    c.node('last_step', 'Last Timestep')
    c.node('dense1', 'Dense(64)|ReLU')
    c.node('dropout', 'Dropout(0.2)')
    c.node('output', 'Output(1)')
    c.attr(label='Prediction Head')

# 连接关系
dot.edges([
    ('input', 'gru'),
    ('gru', 'query'), ('gru', 'key'),
    ('query', 'dot1'), ('key', 'dot1'),
    ('dot1', 'softmax'), ('softmax', 'context'),
    ('gru', 'conv'), ('context', 'conv'),
    ('conv', 'bn'), ('bn', 'last_step'),
    ('last_step', 'dense1'), ('dense1', 'dropout'),
    ('dropout', 'output')
])

# 残差连接
dot.edge('gru', 'conv', style='dashed', label='Residual\nConnection')

# 保存文件
dot.render('model_architecture', cleanup=True)
print("Graph saved as model_architecture.png")