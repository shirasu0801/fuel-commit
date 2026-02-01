/**
 * FuelCommit - チャート描画モジュール
 */

/**
 * PFCバランス円グラフを初期化
 * @param {string} canvasId - Canvas要素のID
 * @param {Object} data - PFCデータ {protein: number, fat: number, carbs: number}
 */
function initPFCChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // データがすべて0の場合はグレーの円を表示
    const total = data.protein + data.fat + data.carbs;
    const chartData = total === 0
        ? [1]
        : [data.protein, data.fat, data.carbs];
    const chartColors = total === 0
        ? ['#e9ecef']
        : ['#dc3545', '#ffc107', '#198754'];
    const chartLabels = total === 0
        ? ['データなし']
        : ['タンパク質', '脂質', '炭水化物'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartLabels,
            datasets: [{
                data: chartData,
                backgroundColor: chartColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (total === 0) return 'データがありません';
                            return `${context.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

/**
 * 週間カロリー折れ線グラフを初期化
 * @param {string} canvasId - Canvas要素のID
 * @param {Array} data - 週間データ [{date, label, calories}, ...]
 * @param {number|null} tdee - 目標カロリー（オプション）
 */
function initWeeklyChart(canvasId, data, tdee) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = data.map(d => d.label);
    const calories = data.map(d => d.calories);

    const datasets = [{
        label: '摂取カロリー',
        data: calories,
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7
    }];

    // 目標カロリーのラインを追加
    if (tdee) {
        datasets.push({
            label: '目標カロリー',
            data: Array(7).fill(tdee),
            borderColor: '#dc3545',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
        });
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} kcal`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'カロリー (kcal)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日付'
                    }
                }
            }
        }
    });
}

/**
 * 栄養素の推移グラフを初期化（将来の拡張用）
 * @param {string} canvasId - Canvas要素のID
 * @param {Array} data - 栄養素データ
 */
function initNutritionTrendChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.label),
            datasets: [
                {
                    label: 'タンパク質',
                    data: data.map(d => d.protein),
                    backgroundColor: '#dc3545'
                },
                {
                    label: '脂質',
                    data: data.map(d => d.fat),
                    backgroundColor: '#ffc107'
                },
                {
                    label: '炭水化物',
                    data: data.map(d => d.carbs),
                    backgroundColor: '#198754'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'グラム (g)'
                    }
                }
            }
        }
    });
}
