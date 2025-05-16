import os

def collect_metrics_to_shared_pool():
    # 基础路径
    base_dir = "bs_1/pre_results"
    shared_pool_dir = "D:/bs/bs_1/pre_results/shared_pool"
    
    # 确保共享池目录存在
    os.makedirs(shared_pool_dir, exist_ok=True)
    
    # 收集所有股票代码
    symbols = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    # 创建汇总文件路径
    summary_file = os.path.join(shared_pool_dir, "all_metrics_summary.csv")
    
    with open(summary_file, 'w') as f_out:
        # 写入表头
        f_out.write("Symbol,MAE,MSE,RMSE,R2\n")
        
        for symbol in symbols:
            metrics_file = os.path.join(base_dir, symbol, "metrics.txt")
            
            if os.path.exists(metrics_file):
                # 读取metrics.txt内容
                metrics = {}
                with open(metrics_file, 'r') as f_in:
                    for line in f_in:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metrics[key.strip()] = value.strip()
                
                # 写入汇总文件
                f_out.write(f"{symbol},{metrics.get('MAE', '')},{metrics.get('MSE', '')},"
                            f"{metrics.get('RMSE', '')},{metrics.get('R2', '')}\n")
    
    print(f"所有股票的评估指标已汇总保存到: {summary_file}")

if __name__ == "__main__":
    collect_metrics_to_shared_pool()