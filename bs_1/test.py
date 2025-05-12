import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv('bs_1/stock_data/601225.csv')
    plt.hist(df['收盘'], bins=30)
    plt.title("601225收盘价分布直方图")
    plt.show()  # Add this to display the plot
if __name__ == '__main__':
    main()