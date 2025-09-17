// 全局变量
let usageChart;
let powerGaugeChart;
let currentChartType = 'hourly';
let meterData = {
    name: '2759弄18号402阳台',
    number: '18100071580',
    remainingPower: 14.84,
    remainingAmount: 14.84,
    unitPrice: 1.000,
    currentPower: 0.85,
    isOnline: true,
    lastUpdate: new Date()
};

// 数据源配置
let useRealData = true; // 是否使用真实数据
let realDataCache = null; // 缓存真实数据
let lastDataUpdate = 0; // 上次数据更新时间

// 加载真实数据
async function loadRealData() {
    try {
        const response = await fetch('./meter_data.json?t=' + Date.now());
        if (!response.ok) {
            throw new Error('数据文件加载失败');
        }
        const data = await response.json();
        realDataCache = data;
        lastDataUpdate = Date.now();
        console.log('真实数据加载成功:', data.meter_name);
        return data;
    } catch (error) {
        console.warn('加载真实数据失败，使用模拟数据:', error.message);
        useRealData = false;
        return null;
    }
}

// 更新当前数据
function updateCurrentDataFromReal(realData) {
    if (!realData) return;
    
    currentData.meterName = realData.meter_name || currentData.meterName;
    currentData.meterId = realData.meter_id || currentData.meterId;
    currentData.remainingPower = realData.remaining_power || currentData.remainingPower;
    currentData.remainingAmount = realData.remaining_amount || currentData.remainingAmount;
    currentData.unitPrice = realData.unit_price || currentData.unitPrice;
    currentData.currentPower = realData.current_power || currentData.currentPower;
    currentData.isOnline = realData.status === 'online';
    
    // 计算今日统计
    if (realData.hourly_usage && realData.hourly_usage.length > 0) {
        currentData.todayUsage = realData.hourly_usage.reduce((sum, hour) => sum + hour.usage, 0);
        currentData.todayCost = currentData.todayUsage * currentData.unitPrice;
        
        const powers = realData.hourly_usage.map(h => h.power || 0);
        currentData.avgPower = powers.reduce((sum, p) => sum + p, 0) / powers.length;
        currentData.peakPower = Math.max(...powers);
    }
}

// 模拟数据生成
function generateHourlyData() {
    const data = [];
    const labels = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
        labels.push(hour.getHours() + ':00');
        
        // 模拟用电量：夜间较低，白天较高，晚上最高
        let usage;
        const h = hour.getHours();
        if (h >= 0 && h < 6) {
            usage = Math.random() * 0.5 + 0.2; // 夜间 0.2-0.7
        } else if (h >= 6 && h < 18) {
            usage = Math.random() * 1.5 + 0.5; // 白天 0.5-2.0
        } else {
            usage = Math.random() * 2.5 + 1.0; // 晚上 1.0-3.5
        }
        data.push(parseFloat(usage.toFixed(2)));
    }
    
    return { labels, data };
}

function generateDailyData() {
    const data = [];
    const labels = [];
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push((date.getMonth() + 1) + '/' + date.getDate());
        
        // 模拟每日用电量 8-25 kWh
        const usage = Math.random() * 17 + 8;
        data.push(parseFloat(usage.toFixed(1)));
    }
    
    return { labels, data };
}

function generateWeeklyData() {
    const data = [];
    const labels = [];
    
    for (let i = 3; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i * 7);
        const weekStart = new Date(date.getTime() - date.getDay() * 24 * 60 * 60 * 1000);
        labels.push((weekStart.getMonth() + 1) + '/' + weekStart.getDate() + '-' + 
                   (weekStart.getMonth() + 1) + '/' + (weekStart.getDate() + 6));
        
        // 模拟每周用电量 50-150 kWh
        const usage = Math.random() * 100 + 50;
        data.push(parseFloat(usage.toFixed(1)));
    }
    
    return { labels, data };
}

// 获取图表数据
function getChartData(type = 'hourly') {
    if (useRealData && realDataCache) {
        if (type === 'hourly' && realDataCache.hourly_usage) {
            return {
                labels: realDataCache.hourly_usage.map(item => item.hour),
                data: realDataCache.hourly_usage.map(item => item.usage)
            };
        } else if (type === 'daily' && realDataCache.daily_usage) {
            return {
                labels: realDataCache.daily_usage.map(item => item.date.substring(5)),
                data: realDataCache.daily_usage.map(item => item.usage)
            };
        }
    }
    
    // 使用模拟数据
    if (type === 'hourly') {
        return generateHourlyData();
    } else if (type === 'daily') {
        return generateDailyData();
    } else if (type === 'weekly') {
        return generateWeeklyData();
    }
}

// 初始化图表
function initCharts() {
    // 初始化用电趋势图
    const ctx = document.getElementById('usageChart').getContext('2d');
    const hourlyData = getChartData('hourly');
    
    usageChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyData.labels,
            datasets: [{
                label: '用电量 (kWh)',
                data: hourlyData.data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            },
            elements: {
                point: {
                    hoverRadius: 8
                }
            }
        }
    });
    
    // 初始化功率仪表盘
    initPowerGauge();
}

// 功率仪表盘
function initPowerGauge() {
    const canvas = document.getElementById('powerGauge');
    const ctx = canvas.getContext('2d');
    
    function drawGauge(power) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height - 20;
        const radius = 80;
        const maxPower = 5; // 最大功率 5kW
        
        // 绘制背景弧
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 0);
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 8;
        ctx.stroke();
        
        // 绘制功率弧
        const angle = Math.PI * (power / maxPower);
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, Math.PI + angle);
        
        // 根据功率设置颜色
        if (power < 1) {
            ctx.strokeStyle = '#27ae60';
        } else if (power < 3) {
            ctx.strokeStyle = '#f39c12';
        } else {
            ctx.strokeStyle = '#e74c3c';
        }
        
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // 绘制刻度
        for (let i = 0; i <= 5; i++) {
            const tickAngle = Math.PI + (Math.PI * i / 5);
            const x1 = centerX + Math.cos(tickAngle) * (radius - 15);
            const y1 = centerY + Math.sin(tickAngle) * (radius - 15);
            const x2 = centerX + Math.cos(tickAngle) * (radius - 5);
            const y2 = centerY + Math.sin(tickAngle) * (radius - 5);
            
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // 刻度标签
            const labelX = centerX + Math.cos(tickAngle) * (radius - 25);
            const labelY = centerY + Math.sin(tickAngle) * (radius - 25);
            ctx.fillStyle = '#666';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(i.toString(), labelX, labelY + 4);
        }
    }
    
    drawGauge(meterData.currentPower);
    
    // 定期更新仪表盘
    setInterval(() => {
        drawGauge(meterData.currentPower);
    }, 1000);
}

// 切换图表类型
function switchChart(type) {
    currentChartType = type;
    
    // 更新按钮状态
    document.querySelectorAll('.chart-controls .btn-small').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    let chartData;
    let label;
    
    switch (type) {
        case 'hourly':
            chartData = generateHourlyData();
            label = '用电量 (kWh)';
            break;
        case 'daily':
            chartData = generateDailyData();
            label = '日用电量 (kWh)';
            break;
        case 'weekly':
            chartData = generateWeeklyData();
            label = '周用电量 (kWh)';
            break;
    }
    
    usageChart.data.labels = chartData.labels;
    usageChart.data.datasets[0].data = chartData.data;
    usageChart.data.datasets[0].label = label;
    usageChart.update();
}

// 更新实时数据
function updateRealTimeData() {
    // 模拟功率变化
    const variation = (Math.random() - 0.5) * 0.3;
    meterData.currentPower = Math.max(0, Math.min(5, meterData.currentPower + variation));
    
    // 模拟电量消耗
    const consumption = meterData.currentPower / 3600; // 每秒消耗
    meterData.remainingPower = Math.max(0, meterData.remainingPower - consumption);
    meterData.remainingAmount = meterData.remainingPower * meterData.unitPrice;
    
    // 更新显示
    document.getElementById('currentPower').textContent = meterData.currentPower.toFixed(2);
    document.getElementById('remainingPower').textContent = meterData.remainingPower.toFixed(2) + ' kWh';
    document.getElementById('remainingAmount').textContent = '¥' + meterData.remainingAmount.toFixed(2);
    
    // 更新最后更新时间
    meterData.lastUpdate = new Date();
    document.getElementById('lastUpdate').textContent = formatTime(meterData.lastUpdate);
    
    // 检查预警
    checkAlerts();
}

// 更新今日统计
function updateDailyStats() {
    const hourlyData = generateHourlyData();
    const todayUsage = hourlyData.data.reduce((sum, usage) => sum + usage, 0);
    const todayCost = todayUsage * meterData.unitPrice;
    const avgPower = todayUsage / 24;
    const peakPower = Math.max(...hourlyData.data) * 1.2; // 模拟峰值功率
    
    document.getElementById('todayUsage').textContent = todayUsage.toFixed(1);
    document.getElementById('todayCost').textContent = '¥' + todayCost.toFixed(2);
    document.getElementById('avgPower').textContent = avgPower.toFixed(2);
    document.getElementById('peakPower').textContent = peakPower.toFixed(1);
}

// 更新历史记录表格
function updateHistoryTable() {
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';
    
    // 生成最近7天的数据
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        const usage = Math.random() * 17 + 8; // 8-25 kWh
        const cost = usage * meterData.unitPrice;
        const avgPower = usage / 24;
        
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${formatDate(date)}</td>
            <td>${usage.toFixed(1)}</td>
            <td>¥${cost.toFixed(2)}</td>
            <td>${avgPower.toFixed(2)}</td>
        `;
    }
}

// 检查预警
function checkAlerts() {
    const balanceAlert = parseFloat(document.getElementById('balanceAlert').value);
    const powerAlert = parseFloat(document.getElementById('powerAlert').value);
    const dailyAlert = parseFloat(document.getElementById('dailyAlert').value);
    
    let alertMessage = '';
    
    if (meterData.remainingAmount <= balanceAlert) {
        alertMessage = `余额不足！当前余额：¥${meterData.remainingAmount.toFixed(2)}`;
    } else if (meterData.currentPower >= powerAlert) {
        alertMessage = `功率过高！当前功率：${meterData.currentPower.toFixed(2)}kW`;
    }
    
    if (alertMessage) {
        showAlert(alertMessage);
    }
}

// 显示预警
function showAlert(message) {
    const alertDiv = document.getElementById('alertNotification');
    const messageSpan = document.getElementById('alertMessage');
    
    messageSpan.textContent = message;
    alertDiv.style.display = 'block';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 3000);
}

// 关闭预警
function closeAlert() {
    document.getElementById('alertNotification').style.display = 'none';
}

// 保存预警设置
function saveAlertSettings() {
    const settings = {
        balanceAlert: document.getElementById('balanceAlert').value,
        powerAlert: document.getElementById('powerAlert').value,
        dailyAlert: document.getElementById('dailyAlert').value
    };
    
    localStorage.setItem('alertSettings', JSON.stringify(settings));
    showAlert('预警设置已保存！');
}

// 加载预警设置
function loadAlertSettings() {
    const settings = localStorage.getItem('alertSettings');
    if (settings) {
        const parsed = JSON.parse(settings);
        document.getElementById('balanceAlert').value = parsed.balanceAlert || 10;
        document.getElementById('powerAlert').value = parsed.powerAlert || 3;
        document.getElementById('dailyAlert').value = parsed.dailyAlert || 20;
    }
}

// 导出数据
function exportData() {
    const data = {
        meterInfo: meterData,
        exportTime: new Date().toISOString(),
        dailyData: generateDailyData(),
        hourlyData: generateHourlyData()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `电费数据_${formatDate(new Date()).replace(/\//g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showAlert('数据导出成功！');
}

// 格式化时间
function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) {
        return '刚刚';
    } else if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
    } else if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
    } else {
        return formatDate(date);
    }
}

function formatDate(date) {
    return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`;
}

// 更新当前时间
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('currentTime').textContent = timeString;
}

// 确保Chart.js加载完成后再初始化
function waitForChart() {
    if (typeof Chart !== 'undefined') {
        initializeApp();
    } else {
        console.log('等待Chart.js加载...');
        setTimeout(waitForChart, 100);
    }
}

function initializeApp() {
    // 初始化图表
    initCharts();
    
    // 加载预警设置
    loadAlertSettings();
    
    // 初始化数据
    updateDailyStats();
    updateHistoryTable();
    
    // 设置定时器
    setInterval(updateRealTimeData, 2000); // 每2秒更新实时数据
    setInterval(updateCurrentTime, 1000); // 每秒更新时间
    setInterval(updateDailyStats, 60000); // 每分钟更新统计数据
    setInterval(() => {
        if (currentChartType === 'hourly') {
            const hourlyData = generateHourlyData();
            usageChart.data.labels = hourlyData.labels;
            usageChart.data.datasets[0].data = hourlyData.data;
            usageChart.update();
        }
    }, 30000); // 每30秒更新图表数据
    
    // 初始化时间显示
    updateCurrentTime();
    
    console.log('电费监控系统初始化完成');
}

// 页面加载完成后等待Chart.js
document.addEventListener('DOMContentLoaded', function() {
    waitForChart();
});

// 模拟网络状态变化
setInterval(() => {
    // 偶尔模拟离线状态
    if (Math.random() < 0.02) { // 2%概率
        meterData.isOnline = false;
        document.getElementById('meterStatus').className = 'status-indicator offline';
        document.getElementById('meterStatus').innerHTML = '<span class="status-dot"></span>离线';
        
        setTimeout(() => {
            meterData.isOnline = true;
            document.getElementById('meterStatus').className = 'status-indicator online';
            document.getElementById('meterStatus').innerHTML = '<span class="status-dot"></span>在线';
        }, 5000 + Math.random() * 10000); // 5-15秒后恢复
    }
}, 10000); // 每10秒检查一次