// 初始化资金曲线图表
function initCapitalChart() {
    const ctx = document.getElementById('capitalChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '资金曲线',
                data: [],
                borderColor: 'rgba(54, 162, 235, 0.8)', // 增加透明度
                backgroundColor: 'rgba(54, 162, 235, 0.1)', // 添加背景色
                borderWidth: 3, // 加粗线条
                pointRadius: 0,
                tension: 0.2, // 添加轻微曲线张力
                fill: true, // 填充曲线下方
                borderJoinStyle: 'round', // 线条连接处圆角
                borderCapStyle: 'round' // 线条端点圆角
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            elements: {
                line: {
                    cubicInterpolationMode: 'monotone' // 更平滑的曲线
                }
            }
        }
    });
    return chart;
}
// 初始化股票图表
function initStockChart() {
    const ctx = document.getElementById('stockChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '实际价格',
                data: [],
                borderColor: 'rgba(54, 162, 235, 0.8)',
                backgroundColor: 'rgba(54, 162, 235, 0.05)', // 更透明的背景色
                borderWidth: 1.5, // 更细的线条
                tension: 0.1,
                fill: true,
                pointRadius: 0 // 不显示点
            },
            {
                label: '预测价格',
                data: [],
                borderColor: 'rgba(255, 99, 132, 0.8)',
                borderWidth: 1.5, // 更细的线条
                // borderDash: [3, 3], // 更短的虚线样式
                tension: 0.1,
                fill: false,
                pointRadius: 0 // 不显示点
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    return chart;
}

// 更新股票选择器事件
function setupStockSelector() {
    const selector = document.getElementById('stock-selector');
    selector.addEventListener('change', function() {
        const selectedStock = this.value;
        loadStockData(selectedStock); // 当选择股票时加载对应数据
        console.log('Selected stock:', selectedStock);
    });
}

// 更新交易记录表格
function updateTradeLog(trades) {
    const tableBody = document.querySelector('#trade-log tbody');
    tableBody.innerHTML = ''; // 清空现有内容
    
    trades.forEach(trade => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${trade.date}</td>
            <td>${trade.code}</td>
            <td><span class="badge ${trade.action === 'buy' ? 'bg-success' : 'bg-danger'}">${trade.action === 'buy' ? '买入' : '卖出'}</span></td>
            <td>${trade.price.toFixed(2)}</td>
            <td>${trade.shares.toFixed(2)}</td>
            <td>${trade.value.toFixed(2)}</td>
            <td>${trade.hold_days}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// 更新策略指标
function updateStrategyMetrics(metrics) {
    document.getElementById('init-capital').textContent = metrics.init_capital.toLocaleString();
    document.getElementById('final-value').textContent = metrics.final_value.toLocaleString();
    document.getElementById('total-return').textContent = `${(metrics.total_return * 100).toFixed(2)}%`;
    document.getElementById('annual-return').textContent = `${(metrics.annual_return * 100).toFixed(2)}%`;
    document.getElementById('max-drawdown').textContent = `${(metrics.max_drawdown * 100).toFixed(2)}%`;
    document.getElementById('sharpe-ratio-strategy').textContent = metrics.sharpe_ratio.toFixed(2);
    document.getElementById('win-rate').textContent = `${(metrics.win_rate * 100).toFixed(2)}%`;
}

// 从后端获取数据
async function fetchData(endpoint) {
    try {
        const response = await fetch(`http://localhost:5000/${endpoint}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

// 获取仪表盘数据
// 更新资金曲线图表
// 获取仪表盘数据
async function loadDashboardData() {
    const data = await fetchData('api/dashboard');
    if (data) {
        // 确保日期和值是匹配的数组
        const dates = data.capital_dates || [];
        const strategyValues = data.strategy_values || [];
        
        // 如果数据点太多，可以采样显示
        const maxPoints = 100;
        const step = Math.max(1, Math.floor(dates.length / maxPoints));
        const sampledDates = [];
        const sampledStrategy = [];
        
        for (let i = 0; i < dates.length; i += step) {
            sampledDates.push(dates[i]);
            sampledStrategy.push(strategyValues[i]);
        }
        
        // 更新资金曲线图表
        capitalChart.data.labels = sampledDates;
        capitalChart.data.datasets[0].data = sampledStrategy;
        capitalChart.update();
        
        // 更新概览卡片
        document.getElementById('stock-count').textContent = data.stock_count;
        document.getElementById('strategy-return').textContent = `${(data.strategy_return * 100).toFixed(2)}%`;
        document.getElementById('sharpe-ratio').textContent = data.sharpe_ratio.toFixed(2);
    }
}

// 获取股票数据
async function loadStockData(stockCode) {
    const data = await fetchData(`api/stock/${stockCode}`);
    if (data) {
        // 更新股票图表
        stockChart.data.labels = data.dates;
        stockChart.data.datasets[0].data = data.actual_prices;
        stockChart.data.datasets[1].data = data.predicted_prices;
        stockChart.update();
        
        // 更新股票指标
        document.getElementById('accuracy-rate').textContent = `${(data.accuracy * 100).toFixed(2)}%`;
        document.getElementById('avg-return').textContent = `${(data.avg_return * 100).toFixed(2)}%`;
        document.getElementById('volatility').textContent = data.volatility.toFixed(4);
    }
}

// 获取策略数据
async function loadStrategyData() {
    const data = await fetchData('api/strategy');
    if (data) {
        updateStrategyMetrics(data.metrics);
        updateTradeLog(data.trades);
    }
}

// 全局变量声明
let capitalChart;
let stockChart;

// 页面加载完成事件
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    capitalChart = initCapitalChart();
    stockChart = initStockChart();
    
    // 设置股票选择器
    setupStockSelector();
    
    // 加载初始数据
    loadDashboardData().then(() => {
        // 默认加载第一只股票
        const defaultStock = document.getElementById('stock-selector').value;
        loadStockData(defaultStock);
    });
    loadStrategyData();
});