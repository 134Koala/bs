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
                borderColor: 'rgba(54, 162, 235, 0.8)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderWidth: 3,
                pointRadius: 0,
                tension: 0.2,
                fill: true,
                borderJoinStyle: 'round',
                borderCapStyle: 'round'
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
                    cubicInterpolationMode: 'monotone'
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
                backgroundColor: 'rgba(54, 162, 235, 0.05)',
                borderWidth: 1.5,
                tension: 0.1,
                fill: true,
                pointRadius: 0
            },
            {
                label: '预测价格',
                data: [],
                borderColor: 'rgba(255, 99, 132, 0.8)',
                borderWidth: 1.5,
                tension: 0.1,
                fill: false,
                pointRadius: 0
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

// 获取股票列表
async function fetchStockList() {
    try {
        const response = await fetch('http://localhost:5000/api/stocks');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching stock list:', error);
        return [];
    }
}

// 更新股票选择器
async function updateStockSelector() {
    const selector = document.getElementById('stock-selector');
    selector.innerHTML = '<option value="" disabled selected>请选择股票...</option>';
    
    const stocks = await fetchStockList();
    if (stocks.length > 0) {
        stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.code;
            option.textContent = `${stock.name} (${stock.code})`;
            selector.appendChild(option);
        });
        
        // 默认加载第一只股票
        loadStockData(stocks[0].code);
    } else {
        selector.innerHTML = '<option value="" disabled selected>没有可用的股票数据</option>';
    }
}

// 更新股票选择器事件
function setupStockSelector() {
    const selector = document.getElementById('stock-selector');
    selector.addEventListener('change', function() {
        const selectedStock = this.value;
        if (selectedStock) {
            loadStockData(selectedStock);
        }
    });
}

// 更新交易记录表格
function updateTradeLog(trades) {
    const tableBody = document.querySelector('#trade-log tbody');
    tableBody.innerHTML = '';
    
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
async function loadDashboardData() {
    const data = await fetchData('api/dashboard');
    if (data) {
        const dates = data.capital_dates || [];
        const strategyValues = data.strategy_values || [];
        
        const maxPoints = 100;
        const step = Math.max(1, Math.floor(dates.length / maxPoints));
        const sampledDates = [];
        const sampledStrategy = [];
        
        for (let i = 0; i < dates.length; i += step) {
            sampledDates.push(dates[i]);
            sampledStrategy.push(strategyValues[i]);
        }
        
        capitalChart.data.labels = sampledDates;
        capitalChart.data.datasets[0].data = sampledStrategy;
        capitalChart.update();
        
        document.getElementById('stock-count').textContent = data.stock_count;
        document.getElementById('strategy-return').textContent = `${(data.strategy_return * 100).toFixed(2)}%`;
        document.getElementById('sharpe-ratio').textContent = data.sharpe_ratio.toFixed(2);
    }
}

// 获取股票数据
async function loadStockData(stockCode) {
    const data = await fetchData(`api/stock/${stockCode}`);
    if (data) {
        stockChart.data.labels = data.dates;
        stockChart.data.datasets[0].data = data.actual_prices;
        stockChart.data.datasets[1].data = data.predicted_prices;
        stockChart.update();
        
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
    loadDashboardData();
    updateStockSelector();
    loadStrategyData();
});