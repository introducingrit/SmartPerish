
// ============================================
// SMARTPERISH - COMPLETE DASHBOARD JAVASCRIPT
// ============================================

const API = {
    health: "/api/health",
    overview: "/api/overview",
    forecast: "/api/forecast",
    inventory: "/api/inventory",
    distribution: "/api/distribution",
    carbon: "/api/carbon"
};

// Chart instances
let forecastChartInstance = null;
let distributionChartInstance = null;
let carbonChartInstance = null;


// ============================================
// HELPER FUNCTIONS
// ============================================

async function fetchData(url) {

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`API error ${response.status}: ${url}`);
    }

    return await response.json();
}


function formatNumber(value) {

    return Number(value || 0).toLocaleString("en-IN", {
        maximumFractionDigits: 2
    });
}


function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}


function createTable(records, columns) {

    if (!records || records.length === 0) {
        return "<p>No records available.</p>";
    }

    const headings = columns.map(column =>
        `<th>${escapeHTML(column.label)}</th>`
    ).join("");

    const rows = records.map(record => `
        <tr>
            ${columns.map(column =>
                `<td>${escapeHTML(record[column.key])}</td>`
            ).join("")}
        </tr>
    `).join("");

    return `
        <div class="table-wrapper">
            <table class="data-table">
                <thead><tr>${headings}</tr></thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;
}


// Find a numeric value inside a JSON object
function findNumber(object, keyMatcher) {

    if (!object || typeof object !== "object") {
        return null;
    }

    for (const [key, value] of Object.entries(object)) {

        if (
            keyMatcher(key.toLowerCase()) &&
            typeof value === "number" &&
            Number.isFinite(value)
        ) {
            return value;
        }

        if (value && typeof value === "object") {

            const result = findNumber(value, keyMatcher);

            if (result !== null) {
                return result;
            }
        }
    }

    return null;
}


// ============================================
// 1. HEALTH STATUS
// ============================================

async function loadHealth() {

    const status = document.getElementById("connection-status");

    try {

        const data = await fetchData(API.health);

        status.textContent =
            data.status === "running"
                ? "Connected"
                : "Unavailable";

    } catch (error) {

        status.textContent = "Connection failed";

        console.error("Health API:", error);
    }
}


// ============================================
// 2. OVERVIEW
// ============================================

async function loadOverview() {

    try {

        const data = await fetchData(API.overview);

        const cards = document.querySelectorAll(".stat-card h2");

        const values = [
            `${formatNumber(data.forecast_wape)}%`,
            formatNumber(data.warehouse_stock),
            formatNumber(data.vehicles_required),
            `${formatNumber(data.carbon_emissions)} kg`
        ];

        cards.forEach((card, index) => {

            if (values[index] !== undefined) {
                card.textContent = values[index];
            }

        });

    } catch (error) {

        console.error("Overview loading failed:", error);
    }
}


// ============================================
// 3. FORECAST CHART
// ============================================

function renderForecastChart(data) {

    const canvas = document.getElementById("forecastChart");

    if (!canvas || typeof Chart === "undefined") {
        console.error("Forecast chart unavailable.");
        return;
    }

    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    forecastChartInstance = new Chart(canvas, {

        type: "line",

        data: {

            labels: data.map(item => item.date),

            datasets: [{

                label: "Predicted Sales",

                data: data.map(item =>
                    Number(item.total_predicted_sales)
                ),

                borderColor: "#29966a",
                backgroundColor: "rgba(41,150,106,0.12)",

                borderWidth: 3,
                fill: true,
                tension: 0.35,

                pointRadius: 4,
                pointHoverRadius: 7

            }]
        },

        options: {

            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: "bottom"
                }
            },

            scales: {

                y: {
                    beginAtZero: true,

                    title: {
                        display: true,
                        text: "Predicted Sales"
                    }
                },

                x: {
                    title: {
                        display: true,
                        text: "Date"
                    }
                }
            }
        }
    });
}


async function loadForecast() {

    const container = document.getElementById("forecast-content");

    try {

        const data = await fetchData(API.forecast);

        renderForecastChart(data);

        container.innerHTML = createTable(data, [
            { key: "date", label: "Forecast Date" },
            {
                key: "total_predicted_sales",
                label: "Predicted Sales"
            }
        ]);

    } catch (error) {

        container.textContent = "Unable to load forecast data.";

        console.error("Forecast API:", error);
    }
}


// ============================================
// 4. INVENTORY
// ============================================

async function loadInventory() {

    const container = document.getElementById("inventory-content");

    try {

        const data = await fetchData(API.inventory);

        const summary = data.summary;

        container.innerHTML = `

            <div class="data-summary">

                <div class="mini-card">
                    <span>Total Stock</span>
                    <strong>${formatNumber(summary.total_stock_units)}</strong>
                </div>

                <div class="mini-card">
                    <span>Critical Expiry Batches</span>
                    <strong>${formatNumber(summary.critical_expiry_batches)}</strong>
                </div>

                <div class="mini-card">
                    <span>Warning Batches</span>
                    <strong>${formatNumber(summary.warning_expiry_batches)}</strong>
                </div>

                <div class="mini-card">
                    <span>Recommended Reorder Units</span>
                    <strong>${formatNumber(summary.total_recommended_reorder_units)}</strong>
                </div>

            </div>

            <h3>Expiry Alerts</h3>

            ${createTable(data.expiry_alerts, [
                { key: "batch_id", label: "Batch" },
                { key: "store_nbr", label: "Store" },
                { key: "family", label: "Product Family" },
                { key: "quantity_units", label: "Stock" },
                { key: "expiry_date", label: "Expiry Date" },
                { key: "expiry_status", label: "Status" }
            ])}

            <h3>Replenishment Recommendations</h3>

            ${createTable(data.replenishment, [
                { key: "store_nbr", label: "Store" },
                { key: "family", label: "Product Family" },
                { key: "current_stock", label: "Current Stock" },
                {
                    key: "recommended_order_quantity",
                    label: "Order Quantity"
                },
                { key: "status", label: "Status" }
            ])}

        `;

    } catch (error) {

        container.textContent = "Unable to load inventory data.";

        console.error("Inventory API:", error);
    }
}


// ============================================
// 5. DISTRIBUTION
// ============================================

function renderDistributionChart(records) {

    const canvas = document.getElementById("distributionChart");

    if (!canvas || typeof Chart === "undefined") {
        console.error("Distribution chart unavailable.");
        return;
    }

    if (distributionChartInstance) {
        distributionChartInstance.destroy();
    }

    distributionChartInstance = new Chart(canvas, {

        type: "bar",

        data: {

            labels: records.map(item => item.store),

            datasets: [

                {
                    label: "Delivered Units",

                    data: records.map(item =>
                        Number(item.delivered_units)
                    ),

                    backgroundColor: "#29966a"
                },

                {
                    label: "Unmet Demand",

                    data: records.map(item =>
                        Number(item.unmet_units)
                    ),

                    backgroundColor: "#e5a14a"
                }

            ]
        },

        options: {

            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: "bottom"
                }
            },

            scales: {
                y: {
                    beginAtZero: true,

                    title: {
                        display: true,
                        text: "Units"
                    }
                }
            }
        }
    });
}


async function loadDistribution() {

    const container = document.getElementById("distribution-content");

    try {

        const data = await fetchData(API.distribution);

        renderDistributionChart(data.distribution);

        container.innerHTML = `

            <div class="data-summary">

                <div class="mini-card">
                    <span>Delivered Units</span>
                    <strong>${formatNumber(data.summary.total_delivered_units)}</strong>
                </div>

                <div class="mini-card">
                    <span>Unmet Demand</span>
                    <strong>${formatNumber(data.summary.total_unmet_units)}</strong>
                </div>

                <div class="mini-card">
                    <span>Vehicles Required</span>
                    <strong>${formatNumber(data.summary.total_vehicles)}</strong>
                </div>

            </div>

            <h3>Store-wise Distribution Plan</h3>

            ${createTable(data.distribution, [
                { key: "store", label: "Store" },
                { key: "required_units", label: "Required Units" },
                { key: "delivered_units", label: "Delivered Units" },
                { key: "unmet_units", label: "Unmet Units" },
                { key: "vehicles_required", label: "Vehicles" },
                { key: "transport_cost", label: "Transport Cost" }
            ])}

        `;

    } catch (error) {

        container.textContent = "Unable to load distribution data.";

        console.error("Distribution API:", error);
    }
}


// ============================================
// 6. CARBON ANALYTICS
// ============================================

function renderCarbonChart(baseline, optimized) {

    const canvas = document.getElementById("carbonChart");

    if (!canvas || typeof Chart === "undefined") {
        console.error("Carbon chart unavailable.");
        return;
    }

    if (baseline === null || optimized === null) {
        console.warn("Carbon emission values are unavailable.");
        return;
    }

    if (carbonChartInstance) {
        carbonChartInstance.destroy();
    }

    carbonChartInstance = new Chart(canvas, {

        type: "bar",

        data: {

            labels: ["Baseline", "Optimized"],

            datasets: [{

                label: "CO2 Emissions (kg)",

                data: [baseline, optimized],

                backgroundColor: ["#d99b54", "#29966a"],

                borderRadius: 7

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

                    title: {
                        display: true,
                        text: "CO2 equivalent (kg)"
                    }
                }
            }
        }
    });
}


async function loadCarbon() {

    const container = document.getElementById("carbon-content");

    try {

        const data = await fetchData(API.carbon);

        const baseline = findNumber(
            data.baseline,
            key => key.includes("baseline") &&
                  key.includes("emission")
        );

        const optimized =
            findNumber(
                data.optimized,
                key => key.includes("carbon_emissions")
            ) ??
            findNumber(
                data.baseline,
                key => key.includes("optimized") &&
                      key.includes("emission")
            );

        const reduction =
            findNumber(
                data.baseline,
                key => key.includes("reduction") &&
                      (key.includes("percentage") ||
                       key.includes("percent"))
            );

        const carbonCost = findNumber(
            data.optimized,
            key => key === "carbon_cost_inr"
        );

        renderCarbonChart(baseline, optimized);

        container.innerHTML = `

            <div class="data-summary">

                <div class="mini-card">
                    <span>Baseline Emissions</span>
                    <strong>
                        ${baseline === null
                            ? "Unavailable"
                            : formatNumber(baseline) + " kg"}
                    </strong>
                </div>

                <div class="mini-card">
                    <span>Optimized Emissions</span>
                    <strong>
                        ${optimized === null
                            ? "Unavailable"
                            : formatNumber(optimized) + " kg"}
                    </strong>
                </div>

                <div class="mini-card">
                    <span>Emission Reduction</span>
                    <strong>
                        ${reduction === null
                            ? "Unavailable"
                            : formatNumber(reduction) + "%"}
                    </strong>
                </div>

                <div class="mini-card">
                    <span>Carbon Cost</span>
                    <strong>
                        ${carbonCost === null
                            ? "Unavailable"
                            : "₹" + formatNumber(carbonCost)}
                    </strong>
                </div>

            </div>

            <p class="data-note">
                Carbon estimates are based on the simulated
                distribution network.
            </p>

        `;

    } catch (error) {

        container.textContent = "Unable to load carbon data.";

        console.error("Carbon API:", error);
    }
}


// ============================================
// 7. DASHBOARD NAVIGATION
// ============================================

function setupNavigation() {

    const links = document.querySelectorAll(
        "#sidebar-navigation a"
    );

    links.forEach(link => {

        link.addEventListener("click", () => {

            links.forEach(item =>
                item.classList.remove("active")
            );

            link.classList.add("active");

        });

    });
}


// ============================================
// 8. LOAD COMPLETE DASHBOARD
// ============================================

async function loadDashboard() {

    console.log("Loading SmartPerish dashboard...");

    await Promise.all([
        loadHealth(),
        loadOverview(),
        loadForecast(),
        loadInventory(),
        loadDistribution(),
        loadCarbon()
    ]);

    const updated = document.getElementById("last-updated");

    if (updated) {
        updated.textContent =
            "Last updated: " +
            new Date().toLocaleString("en-IN");
    }

    console.log("SmartPerish dashboard loading completed.");
}


// ============================================
// 9. MANUAL REFRESH
// ============================================

async function refreshDashboard() {

    const button = document.getElementById("refresh-btn");

    if (button) {
        button.disabled = true;
        button.textContent = "Refreshing...";
    }

    try {

        await loadDashboard();

    } finally {

        if (button) {
            button.disabled = false;
            button.textContent = "↻ Refresh Data";
        }
    }
}


// ============================================
// 10. INITIALIZE DASHBOARD
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    setupNavigation();

    loadDashboard();

    // Refresh automatically every 60 seconds
    setInterval(loadDashboard, 60000);

});
