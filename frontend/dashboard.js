// XSS Assistant Dashboard JavaScript

const API_BASE = 'http://localhost:8000/api/v1';

// Auto-refresh interval (30 seconds)
let autoRefreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 XSS Assistant Dashboard loaded');
    refreshAll();
    startAutoRefresh();
});

// Start auto-refresh
function startAutoRefresh() {
    autoRefreshInterval = setInterval(refreshAll, 30000);
}

// Refresh all data
async function refreshAll() {
    console.log('Refreshing dashboard...');
    await Promise.all([
        loadTargets(),
        loadSessions(),
        loadMetrics()
    ]);
}

// Load metrics
async function loadMetrics() {
    try {
        const [targets, sessions] = await Promise.all([
            fetch(`${API_BASE}/targets/`).then(r => r.json()),
            fetch(`${API_BASE}/sessions/`).then(r => r.json())
        ]);

        document.getElementById('totalTargets').textContent = targets.length;
        document.getElementById('totalSessions').textContent = sessions.length;

        const activeScans = sessions.filter(s =>
            s.status === 'running' || s.status === 'pending'
        ).length;
        document.getElementById('activeScans').textContent = activeScans;

        // Load total findings from recent sessions
        let totalFindings = 0;
        for (const session of sessions.slice(0, 10)) {
            try {
                const report = await fetch(`${API_BASE}/reports/sessions/${session.id}`).then(r => r.json());
                totalFindings += report.findings_count || 0;
            } catch (e) {}
        }
        document.getElementById('totalFindings').textContent = totalFindings;

        updateStatus('Connected', true);
    } catch (error) {
        console.error('Metrics load error:', error);
        updateStatus('Connection Error', false);
    }
}

// Update connection status
function updateStatus(text, isConnected) {
    const statusText = document.getElementById('statusText');
    const statusDot = statusText.previousElementSibling;

    statusText.textContent = text;
    statusDot.className = `fas fa-circle text-${isConnected ? 'success' : 'danger'}`;
}

// Load targets
async function loadTargets() {
    try {
        const response = await fetch(`${API_BASE}/targets/`);
        const targets = await response.json();

        const tbody = document.getElementById('targetsTable');
        tbody.innerHTML = '';

        if (targets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No targets yet</td></tr>';
            return;
        }

        targets.forEach(target => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${target.id}</td>
                <td><strong>${target.name}</strong></td>
                <td><a href="${target.url}" target="_blank">${target.url}</a></td>
                <td>
                    <span class="badge bg-${target.is_active ? 'success' : 'secondary'}">
                        ${target.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>${formatDate(target.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="startScan(${target.id}, '${target.name}')">
                        <i class="fas fa-play"></i> Scan
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Targets load error:', error);
    }
}

// Load sessions
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE}/sessions/`);
        const sessions = await response.json();

        const tbody = document.getElementById('sessionsTable');
        tbody.innerHTML = '';

        if (sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No sessions yet</td></tr>';
            return;
        }

        sessions.sort((a, b) => b.id - a.id).forEach(session => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${session.id}</td>
                <td>${session.name}</td>
                <td>Target #${session.target_id}</td>
                <td><span class="status-${session.status}">${session.status.toUpperCase()}</span></td>
                <td>${session.duration_seconds || 0}s</td>
                <td>${formatDate(session.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewReport(${session.id})">
                        <i class="fas fa-file-alt"></i> Report
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Sessions load error:', error);
    }
}

// View report
async function viewReport(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/reports/sessions/${sessionId}`);
        const report = await response.json();

        // Show findings tab
        document.getElementById('findings-tab').click();

        // Display report
        const container = document.getElementById('findingsContainer');
        container.innerHTML = `
            <div class="mb-4">
                <h4>${report.session_name}</h4>
                <p class="text-muted">
                    Target: ${report.target_url}<br>
                    Duration: ${report.duration_seconds}s |
                    Findings: ${report.findings_count}
                </p>
            </div>
        `;

        if (report.findings_count === 0) {
            container.innerHTML += '<div class="alert alert-success">No vulnerabilities found!</div>';
            return;
        }

        report.findings.forEach(finding => {
            const severityClass = `severity-${finding.severity}`;
            const card = document.createElement('div');
            card.className = 'card mb-3';
            card.innerHTML = `
                <div class="card-header bg-light">
                    <h5 class="${severityClass}">
                        <i class="fas fa-bug"></i> ${finding.title}
                    </h5>
                    <small class="text-muted">
                        ${finding.finding_type.replace('_', ' ').toUpperCase()} |
                        Severity: <span class="${severityClass}">${finding.severity.toUpperCase()}</span>
                    </small>
                </div>
                <div class="card-body">
                    <p><strong>Endpoint:</strong> <code>${finding.endpoint}</code></p>
                    <p><strong>Parameter:</strong> <code>${finding.parameter}</code></p>
                    <p><strong>Description:</strong> ${finding.description}</p>

                    <div class="mt-3">
                        <strong>Payload:</strong>
                        <pre class="bg-dark text-light p-2 rounded"><code>${finding.evidence.payload}</code></pre>
                    </div>

                    <div class="mt-3">
                        <strong>Evidence:</strong>
                        <pre class="bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;"><code>${finding.evidence.response_snippet}</code></pre>
                    </div>

                    <div class="alert alert-warning mt-3">
                        <strong><i class="fas fa-shield-alt"></i> Remediation:</strong><br>
                        ${finding.remediation}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Report load error:', error);
        alert('Error loading report: ' + error.message);
    }
}

// Start scan
async function startScan(targetId, targetName) {
    if (!confirm(`Start scan on "${targetName}"?`)) return;

    try {
        const response = await fetch(`${API_BASE}/sessions/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                target_id: targetId,
                name: `Auto Scan - ${targetName}`,
                description: `Automated scan from dashboard`
            })
        });

        if (!response.ok) throw new Error('Scan start failed');

        const session = await response.json();
        alert(`Scan started! Session ID: ${session.id}`);

        // Switch to sessions tab
        document.getElementById('sessions-tab').click();
        await loadSessions();
    } catch (error) {
        console.error('Scan start error:', error);
        alert('Error starting scan: ' + error.message);
    }
}

// Show add target modal
function showAddTargetModal() {
    const modal = new bootstrap.Modal(document.getElementById('addTargetModal'));
    modal.show();
}

// Add target
async function addTarget() {
    const name = document.getElementById('targetName').value;
    const url = document.getElementById('targetUrl').value;
    const description = document.getElementById('targetDescription').value;

    if (!name || !url) {
        alert('Name and URL are required');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/targets/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, url, description })
        });

        if (!response.ok) throw new Error('Target creation failed');

        alert('Target added successfully!');

        // Hide modal and refresh
        bootstrap.Modal.getInstance(document.getElementById('addTargetModal')).hide();
        document.getElementById('addTargetForm').reset();
        await loadTargets();
    } catch (error) {
        console.error('Target add error:', error);
        alert('Error adding target: ' + error.message);
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
