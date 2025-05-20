# retrain_low_r2_models.py
import os
import argparse
from model import train_model
from prediction import predict_stock

def check_r2_and_retrain():
    # 设置目录路径
    pre_results_dir = "bs_1/pre_results"
    log_file = "retrain_log.txt"
    
    # 初始化日志文件
    with open(log_file, 'w') as f:
        f.write("模型重训练日志\n")
        f.write("="*30 + "\n")
    
    # 获取所有股票代码目录
    stock_dirs = [d for d in os.listdir(pre_results_dir) 
                 if os.path.isdir(os.path.join(pre_results_dir, d))]
    
    # 记录最终结果
    results = {
        'passed': [],
        'failed_after_retries': [],
        'skipped': []
    }
    
    # 遍历每个股票目录
    for stock in stock_dirs:
        metrics_file = os.path.join(pre_results_dir, stock, "metrics.txt")
        
        # 检查metrics.txt文件是否存在
        if not os.path.exists(metrics_file):
            log_message = f"{stock}: 没有metrics.txt文件,将重新训练模型\n"
            print(log_message)
            with open(log_file, 'a') as f:
                f.write(log_message)
            results['skipped'].append(stock)
            continue
        
        # 读取并解析metrics.txt文件
        try:
            with open(metrics_file, 'r') as f:
                lines = f.readlines()
                r2_line = [line for line in lines if line.startswith("R2:")]
                
                if not r2_line:
                    log_message = f"{stock}: metrics.txt中没有找到R2指标,将重新训练模型\n"
                    print(log_message)
                    with open(log_file, 'a') as f:
                        f.write(log_message)
                    results['skipped'].append(stock)
                    continue
                
                r2_value = float(r2_line[0].split(":")[1].strip())
                print(f"{stock} 的R2值为: {r2_value}")
                
                # 检查R2是否小于0.9
                if r2_value >= 0.9:
                    results['passed'].append(stock)
                    continue
                
                # 开始重试循环
                max_retries = 5
                retry_count = 0
                improved = False
                
                log_message = f"{stock}: R2值 {r2_value} 低于阈值0.9,开始重训练(最多{max_retries}次)\n"
                print(log_message)
                with open(log_file, 'a') as f:
                    f.write(log_message)
                
                while retry_count < max_retries and not improved:
                    retry_count += 1
                    try:
                        # 1. 重新训练模型
                        print(f"第{retry_count}次重训练 {stock}...")
                        train_model(stock)
                        
                        # 2. 立即进行预测以生成新的metrics.txt
                        print(f"第{retry_count}次预测 {stock}...")
                        predict_stock(stock)
                        
                        # 3. 检查新的R2值
                        if os.path.exists(metrics_file):
                            with open(metrics_file, 'r') as f:
                                lines = f.readlines()
                                r2_line = [line for line in lines if line.startswith("R2:")]
                                if r2_line:
                                    new_r2 = float(r2_line[0].split(":")[1].strip())
                                    print(f"第{retry_count}次重训练后R2值: {new_r2}")
                                    
                                    if new_r2 >= 0.93:
                                        improved = True
                                        results['passed'].append(stock)
                                        log_message = f"{stock}: 第{retry_count}次重训练后R2达标({new_r2})\n"
                                        print(log_message)
                                        with open(log_file, 'a') as f:
                                            f.write(log_message)
                    
                    except Exception as e:
                        log_message = f"{stock}: 第{retry_count}次重训练失败: {str(e)}\n"
                        print(log_message)
                        with open(log_file, 'a') as f:
                            f.write(log_message)
                
                # 检查是否达到最大重试次数仍未改善
                if not improved and retry_count >= max_retries:
                    results['failed_after_retries'].append(stock)
                    log_message = f"{stock}: 经过{max_retries}次重训练后R2仍未达标,跳过该股票\n"
                    print(log_message)
                    with open(log_file, 'a') as f:
                        f.write(log_message)
                    
        except Exception as e:
            log_message = f"{stock}: 处理metrics.txt时出错: {str(e)}\n"
            print(log_message)
            with open(log_file, 'a') as f:
                f.write(log_message)
            results['skipped'].append(stock)
    
    # 打印最终统计结果
    print("\n" + "="*30)
    print("重训练结果统计:")
    print(f"达标模型数量: {len(results['passed'])}")
    print(f"重试后仍不达标数量: {len(results['failed_after_retries'])}")
    print(f"跳过数量: {len(results['skipped'])}")
    print("="*30)
    
    # 将统计结果写入日志
    with open(log_file, 'a') as f:
        f.write("\n" + "="*30 + "\n")
        f.write("重训练结果统计:\n")
        f.write(f"达标模型数量: {len(results['passed'])}\n")
        f.write(f"重试后仍不达标数量: {len(results['failed_after_retries'])}\n")
        f.write(f"跳过数量: {len(results['skipped'])}\n")
        f.write("="*30 + "\n")
        
        if results['failed_after_retries']:
            f.write("\n重试后仍不达标的股票:\n")
            for stock in results['failed_after_retries']:
                f.write(f"{stock}\n")
        
        if results['skipped']:
            f.write("\n跳过的股票:\n")
            for stock in results['skipped']:
                f.write(f"{stock}\n")

def main():
    parser = argparse.ArgumentParser(description="根据R2指标重新训练模型并预测(最多重试3次)")
    args = parser.parse_args()
    
    print("开始检查模型R2指标...")
    check_r2_and_retrain()

if __name__ == "__main__":
    main()