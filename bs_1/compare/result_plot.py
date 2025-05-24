"""
Model Metrics Comparison Visualization Script with Enhanced Labels and Legends
File: D:\bs\bs_1\compare\result_plot.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.ticker import FormatStrFormatter

# 设置文件路径
data_path = r"D:\bs\bs_1\compare\pre_result\model_metrics.csv"
output_dir = r"D:\bs\bs_1\compare"
output_file = os.path.join(output_dir, "model_metrics_comparison_enhanced.png")

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

def load_and_prepare_data(filepath):
    """从CSV文件加载数据并进行预处理"""
    try:
        df = pd.read_csv(filepath)
        print("数据加载成功！前5行数据预览:")
        print(df.head())
        
        # 添加模型全名映射（用于图例）
        df['Model_Full'] = df['Model'].map({'lstm': 'LSTM Neural Network', 
                                           'rf': 'Random Forest'})
        return df
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return None

def create_enhanced_visualization(df, save_path):
    """创建并保存带有详细标签的可视化图表"""
    # 设置图形样式
    sns.set(style="whitegrid", palette="muted")
    plt.figure(figsize=(18, 12))
    
    # 创建子图
    metrics = ['MSE', 'RMSE', 'MAE', 'MAPE', 'R2']
    titles = ['Mean Squared Error (MSE)', 'Root Mean Squared Error (RMSE)', 
              'Mean Absolute Error (MAE)', 'Mean Absolute Percentage Error (MAPE)', 
              'R-squared (R²)']
    units = ['(units²)', '(units)', '(units)', '(%)', '']
    
    for i, (metric, title, unit) in enumerate(zip(metrics, titles, units), 1):
        ax = plt.subplot(2, 3, i)
        
        # 创建带有详细标签的箱线图
        sns.boxplot(x='Model_Full', y=metric, data=df, 
                   width=0.6, linewidth=2, 
                   hue='Model_Full', dodge=False,
                   legend=False if i != 1 else True)
        
        # 设置标题和标签
        plt.title(f'{title}\n{unit}', fontsize=12, pad=12)
        plt.xlabel('Model Type', fontsize=11, labelpad=10)
        plt.ylabel(metric + ' ' + unit, fontsize=11, labelpad=10)
        
        # 格式化y轴刻度
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        # 为R2添加特殊格式
        if metric == 'R2':
            plt.axhline(y=1, color='darkred', linestyle=':', alpha=0.7, linewidth=2)
            plt.ylim(0.85, 1.05)
            ax.annotate('Perfect Fit (R²=1)', xy=(0.5, 1.01), 
                       xycoords=('axes fraction', 'data'),
                       ha='center', color='darkred', fontsize=10)
        
        # 添加数据点标记
        sns.stripplot(x='Model_Full', y=metric, data=df, 
                     color='black', size=6, alpha=0.5, 
                     jitter=True, linewidth=1)
        
        # 旋转x轴标签
        plt.xticks(rotation=15 if i == 5 else 0)
    
    # 添加整体图例
    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, loc='lower center', 
                 ncol=2, bbox_to_anchor=(0.5, -0.05),
                 fontsize=12, title='Model Types:')
    
    # 添加整体标题和调整布局
    plt.suptitle('Comparative Analysis of Model Performance Metrics\nLSTM vs Random Forest', 
                y=1.02, fontsize=16, weight='bold')
    plt.tight_layout(pad=3, h_pad=2, w_pad=2)
    
    # 保存图表
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"增强版可视化图表已保存至: {save_path}")
    
    # 显示图表
    plt.show()

def main():
    """主函数"""
    print("=== 模型指标比较可视化脚本 (增强版) ===")
    
    # 加载数据
    df = load_and_prepare_data(data_path)
    if df is None:
        return
    
    # 创建并保存可视化
    create_enhanced_visualization(df, output_file)

if __name__ == "__main__":
    main()