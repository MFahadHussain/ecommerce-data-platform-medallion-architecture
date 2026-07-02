// E-Commerce Medallion Architecture Portal Client Application

let activeTab = 'categories';
let categoryData = [];
let segmentData = [];
let customerData = [];

// Chart References
let categoryChart = null;
let priceSegmentChart = null;
let customerChart = null;

// Format Utilities
const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
};

const formatDecimal = (val) => {
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(val);
};

const formatInt = (val) => {
    return new Intl.NumberFormat('en-US').format(val);
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();

    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchDashboardData();
    });
});

async function fetchDashboardData() {
    try {
        showTableLoading(true);

        // Fetch Global KPIs
        const kpiResponse = await fetch('/api/kpis');
        const kpis = await kpiResponse.json();
        updateKPICards(kpis);

        // Fetch Category performance
        const catResponse = await fetch('/api/categories');
        categoryData = await catResponse.json();
        renderCategoryChart();

        // Fetch Price Segmentation
        const segResponse = await fetch('/api/price-segments');
        segmentData = await segResponse.json();
        renderPriceSegmentChart();

        // Fetch Top Customers
        const custResponse = await fetch('/api/top-customers');
        customerData = await custResponse.json();
        renderCustomerChart();

        // Populate Current Active Table Tab
        populateTable();
        showTableLoading(false);
    } catch (err) {
        console.error("Failed to load dashboard statistics:", err);
        showTableLoading(false);
    }
}

function updateKPICards(kpis) {
    document.querySelector('#kpi-revenue .kpi-value').textContent = formatCurrency(kpis.total_revenue);
    document.querySelector('#kpi-orders .kpi-value').textContent = formatInt(kpis.total_orders);
    document.querySelector('#kpi-aov .kpi-value').textContent = formatCurrency(kpis.average_order_value);
    document.querySelector('#kpi-products .kpi-value').textContent = formatInt(kpis.total_products);
}

// Chart.js Implementations
function renderCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    const labels = categoryData.map(c => c.category_name);
    const revenues = categoryData.map(c => c.total_revenue);
    const counts = categoryData.map(c => c.product_count);

    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Revenue ($)',
                    data: revenues,
                    backgroundColor: 'rgba(99, 102, 241, 0.75)',
                    borderColor: '#6366f1',
                    borderWidth: 1.5,
                    borderRadius: 8,
                    yAxisID: 'y'
                },
                {
                    label: 'Product Count',
                    data: counts,
                    type: 'line',
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#a855f7',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans', weight: '600' } }
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 25, 0.9)',
                    titleFont: { family: 'Plus Jakarta Sans' },
                    bodyFont: { family: 'Plus Jakarta Sans' },
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans' } }
                },
                y: {
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#9ca3af', 
                        font: { family: 'Plus Jakarta Sans' },
                        callback: function(value) { return '$' + formatInt(value); }
                    }
                },
                y1: {
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans' } }
                }
            }
        }
    });
}

function renderPriceSegmentChart() {
    const ctx = document.getElementById('priceSegmentChart').getContext('2d');
    
    const labels = segmentData.map(s => s.price_segment);
    const productCounts = segmentData.map(s => s.product_count);

    if (priceSegmentChart) {
        priceSegmentChart.destroy();
    }

    priceSegmentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: productCounts,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.75)', // Budget - Emerald
                    'rgba(99, 102, 241, 0.75)', // Mid-Range - Primary Blue
                    'rgba(244, 63, 94, 0.75)'   // Premium - Rose
                ],
                borderColor: [
                    '#10b981',
                    '#6366f1',
                    '#f43f5e'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans', weight: '600' } }
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 25, 0.9)',
                    titleFont: { family: 'Plus Jakarta Sans' },
                    bodyFont: { family: 'Plus Jakarta Sans' },
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            cutout: '65%'
        }
    });
}

function renderCustomerChart() {
    const ctx = document.getElementById('customerChart').getContext('2d');
    
    // Pick top 10 customers
    const sortedCustomers = [...customerData].sort((a,b) => b.total_spent - a.total_spent).slice(0, 10);
    
    const names = sortedCustomers.map(c => c.customer_name);
    const spends = sortedCustomers.map(c => c.total_spent);

    if (customerChart) {
        customerChart.destroy();
    }

    customerChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                label: 'Total Spend ($)',
                data: spends,
                backgroundColor: 'rgba(139, 92, 246, 0.75)', // Violet
                borderColor: '#8b5cf6',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 25, 0.9)',
                    titleFont: { family: 'Plus Jakarta Sans' },
                    bodyFont: { family: 'Plus Jakarta Sans' },
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#9ca3af', 
                        font: { family: 'Plus Jakarta Sans' },
                        callback: function(value) { return '$' + formatInt(value); }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans', weight: '600' } }
                }
            }
        }
    });
}

// Table Tab Switching
function switchTab(tabId) {
    activeTab = tabId;
    
    // Update Tab Buttons UI
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const clickedBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.textContent.toLowerCase().includes(tabId.substring(0, 4)));
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }

    populateTable();
}

function showTableLoading(isLoading) {
    const spinner = document.getElementById('loading-table');
    const table = document.getElementById('explorer-table');
    if (isLoading) {
        spinner.style.display = 'flex';
        table.style.display = 'none';
    } else {
        spinner.style.display = 'none';
        table.style.display = 'table';
    }
}

function populateTable() {
    const head = document.getElementById('table-head');
    const body = document.getElementById('table-body');
    
    head.innerHTML = '';
    body.innerHTML = '';

    if (activeTab === 'categories') {
        head.innerHTML = `
            <tr>
                <th>Category ID</th>
                <th>Category Name</th>
                <th class="text-right">Products Count</th>
                <th class="text-right">Average Price</th>
                <th class="text-right">Quantity Sold</th>
                <th class="text-right">Total Revenue</th>
            </tr>
        `;
        
        categoryData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${row.category_id}</td>
                <td style="font-weight: 600;">${row.category_name}</td>
                <td class="text-right">${formatInt(row.product_count)}</td>
                <td class="text-right">${formatCurrency(row.average_price)}</td>
                <td class="text-right">${formatInt(row.total_quantity_sold)}</td>
                <td class="text-right" style="color: var(--emerald); font-weight: 700;">${formatCurrency(row.total_revenue)}</td>
            `;
            body.appendChild(tr);
        });
    } 
    else if (activeTab === 'segments') {
        head.innerHTML = `
            <tr>
                <th>Price Segment</th>
                <th class="text-right">Product Volume</th>
                <th class="text-right">Average Price</th>
                <th class="text-right">Aggregate Spend</th>
            </tr>
        `;
        
        segmentData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 600;">${row.price_segment}</td>
                <td class="text-right">${formatInt(row.product_count)}</td>
                <td class="text-right">${formatCurrency(row.average_price)}</td>
                <td class="text-right" style="color: var(--emerald); font-weight: 700;">${formatCurrency(row.total_revenue)}</td>
            `;
            body.appendChild(tr);
        });
    } 
    else if (activeTab === 'customers') {
        head.innerHTML = `
            <tr>
                <th>Customer Name</th>
                <th>Role</th>
                <th>Email Address</th>
                <th class="text-right">Orders Count</th>
                <th class="text-right">Average Order Value</th>
                <th class="text-right">Total Spent</th>
            </tr>
        `;
        
        customerData.forEach(row => {
            const tr = document.createElement('tr');
            // Role colors
            const roleClass = row.role === 'admin' ? 'role-badge admin' : 'role-badge';
            
            // Random default avatar placeholder matching role
            const userAvatar = row.avatar_url ? row.avatar_url : `https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80`;

            tr.innerHTML = `
                <td>
                    <div class="user-cell">
                        <img class="user-avatar" src="${userAvatar}" alt="${row.customer_name}" onerror="this.src='https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80'">
                        <div style="font-weight: 600;">${row.customer_name}</div>
                    </div>
                </td>
                <td><span class="${roleClass}">${row.role}</span></td>
                <td style="color: var(--text-muted);">${row.email}</td>
                <td class="text-right">${formatInt(row.total_orders)}</td>
                <td class="text-right">${formatCurrency(row.average_order_value)}</td>
                <td class="text-right" style="color: var(--emerald); font-weight: 700;">${formatCurrency(row.total_spent)}</td>
            `;
            body.appendChild(tr);
        });
    }
}
