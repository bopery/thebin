from flask import Flask, request, jsonify, render_template, Response, session, redirect, url_for
import sqlite3
import uuid
import hashlib
import time
import os
from functools import wraps
from datetime import datetime
import re
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

ADMIN_USERNAME = "ikucanseethisurnotsomebigguyforthis"
ADMIN_PASSWORD_HASH = hashlib.sha256("because?itisatest".encode()).hexdigest()

request_log = defaultdict(list)

def rate_limit(max_requests=10, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            request_log[ip] = [req_time for req_time in request_log[ip] if now - req_time < window]
            if len(request_log[ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            request_log[ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_templates():
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>DoxBean - Administration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #0a0a0a;
            min-height: 100vh;
            padding: 0;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 250px;
            background: #1a1a1a;
            border-right: 1px solid #333;
            padding: 20px 0;
        }
        .main-content {
            flex: 1;
            padding: 20px;
            background: #0f0f0f;
            overflow-y: auto;
        }
        .logo {
            padding: 0 20px 20px;
            border-bottom: 1px solid #333;
            margin-bottom: 20px;
        }
        .logo h1 {
            color: #ff4444;
            font-size: 1.4em;
            font-weight: 300;
        }
        .nav-section {
            margin-bottom: 30px;
        }
        .nav-title {
            color: #666;
            font-size: 0.8em;
            text-transform: uppercase;
            padding: 0 20px 10px;
            letter-spacing: 1px;
        }
        .nav-item {
            display: block;
            padding: 12px 20px;
            color: #ccc;
            text-decoration: none;
            border-left: 3px solid transparent;
            transition: all 0.3s;
            font-size: 0.9em;
        }
        .nav-item:hover {
            background: #252525;
            color: #fff;
            border-left-color: #ff4444;
        }
        .nav-item.active {
            background: #252525;
            color: #ff4444;
            border-left-color: #ff4444;
        }
        .header {
            background: #1a1a1a;
            padding: 20px;
            border-bottom: 1px solid #333;
            margin: -20px -20px 20px;
        }
        .header h2 {
            color: #fff;
            font-weight: 300;
            margin-bottom: 5px;
        }
        .header p {
            color: #666;
            font-size: 0.9em;
        }
        .card {
            background: #1a1a1a;
            border: 1px solid #333;
            margin-bottom: 20px;
        }
        .card-header {
            padding: 15px 20px;
            border-bottom: 1px solid #333;
            background: #252525;
        }
        .card-header h3 {
            color: #fff;
            font-weight: 400;
            font-size: 1.1em;
        }
        .card-body {
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #252525;
            padding: 20px;
            border: 1px solid #333;
        }
        .stat-number {
            font-size: 2em;
            color: #ff4444;
            font-weight: 300;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #999;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        .table th {
            background: #252525;
            color: #fff;
            padding: 12px 15px;
            text-align: left;
            font-weight: 400;
            border-bottom: 1px solid #333;
            font-size: 0.9em;
        }
        .table td {
            padding: 12px 15px;
            border-bottom: 1px solid #333;
            color: #ccc;
            font-size: 0.9em;
        }
        .table tr:hover {
            background: #252525;
        }
        .btn {
            padding: 8px 16px;
            border: 1px solid #333;
            background: #252525;
            color: #ccc;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #333;
            color: #fff;
        }
        .btn-danger {
            border-color: #ff4444;
            color: #ff4444;
        }
        .btn-danger:hover {
            background: #ff4444;
            color: #fff;
        }
        .btn-success {
            border-color: #44ff44;
            color: #44ff44;
        }
        .btn-success:hover {
            background: #44ff44;
            color: #000;
        }
        .btn-warning {
            border-color: #ffaa44;
            color: #ffaa44;
        }
        .btn-warning:hover {
            background: #ffaa44;
            color: #000;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-label {
            display: block;
            margin-bottom: 5px;
            color: #ccc;
            font-size: 0.9em;
        }
        .form-control {
            width: 100%;
            padding: 10px;
            background: #252525;
            border: 1px solid #333;
            color: #fff;
            font-size: 0.9em;
        }
        .form-control:focus {
            outline: none;
            border-color: #ff4444;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            background: #333;
            color: #ccc;
            border-radius: 2px;
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .badge-success {
            background: #224422;
            color: #44ff44;
        }
        .badge-danger {
            background: #442222;
            color: #ff4444;
        }
        .badge-warning {
            background: #443322;
            color: #ffaa44;
        }
        .user-status {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-online { background: #44ff44; }
        .status-offline { background: #666; }
        .status-banned { background: #ff4444; }
        .search-box {
            background: #252525;
            padding: 20px;
            border: 1px solid #333;
            margin-bottom: 20px;
        }
        .action-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a1a;
            border: 1px solid #333;
            width: 90%;
            max-width: 500px;
        }
        .modal-header {
            padding: 15px 20px;
            border-bottom: 1px solid #333;
            background: #252525;
        }
        .modal-body {
            padding: 20px;
        }
        .modal-footer {
            padding: 15px 20px;
            border-top: 1px solid #333;
            background: #252525;
            text-align: right;
        }
        .log-entry {
            padding: 10px 15px;
            border-bottom: 1px solid #333;
            font-family: monospace;
            font-size: 0.8em;
        }
        .log-entry:last-child {
            border-bottom: none;
        }
        .log-time {
            color: #666;
            margin-right: 10px;
        }
        .log-info { color: #44ff44; }
        .log-warning { color: #ffaa44; }
        .log-error { color: #ff4444; }
        .pagination {
            display: flex;
            gap: 5px;
            margin-top: 20px;
        }
        .page-item {
            padding: 8px 12px;
            background: #252525;
            border: 1px solid #333;
            color: #ccc;
            cursor: pointer;
            font-size: 0.8em;
        }
        .page-item.active {
            background: #ff4444;
            color: #fff;
            border-color: #ff4444;
        }
        .filter-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">
                <h1>DoxBean Admin</h1>
            </div>
            
            <div class="nav-section">
                <div class="nav-title">Main</div>
                <a href="#" class="nav-item active" onclick="showTab('dashboard')">Dashboard</a>
                <a href="#" class="nav-item" onclick="showTab('users')">User Management</a>
                <a href="#" class="nav-item" onclick="showTab('content')">Content Moderation</a>
                <a href="#" class="nav-item" onclick="showTab('reports')">Reports & Logs</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-title">System</div>
                <a href="#" class="nav-item" onclick="showTab('settings')">System Settings</a>
                <a href="#" class="nav-item" onclick="showTab('security')">Security</a>
                <a href="#" class="nav-item" onclick="showTab('backup')">Backup & Restore</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-title">Session</div>
                <a href="#" class="nav-item" onclick="logout()">Logout</a>
                <a href="#" class="nav-item" onclick="shutdown()">Shutdown System</a>
            </div>
        </div>

        <div class="main-content">
            <div class="header">
                <h2>Administration Panel</h2>
                <p>Welcome back, Administrator. System status: <span class="badge badge-success">Operational</span></p>
            </div>

            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="total-users">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="total-leaks">0</div>
                        <div class="stat-label">Total Leaks</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="active-sessions">0</div>
                        <div class="stat-label">Active Sessions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="today-leaks">0</div>
                        <div class="stat-label">Leaks Today</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>Recent Activity</h3>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>User</th>
                                        <th>Action</th>
                                        <th>IP Address</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody id="recent-activity">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>System Health</h3>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">CPU Usage</label>
                            <div style="background: #252525; height: 20px; border: 1px solid #333;">
                                <div id="cpu-usage" style="background: #ff4444; height: 100%; width: 0%;"></div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Memory Usage</label>
                            <div style="background: #252525; height: 20px; border: 1px solid #333;">
                                <div id="memory-usage" style="background: #44ff44; height: 100%; width: 0%;"></div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Disk Usage</label>
                            <div style="background: #252525; height: 20px; border: 1px solid #333;">
                                <div id="disk-usage" style="background: #ffaa44; height: 100%; width: 0%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- User Management Tab -->
            <div id="users" class="tab-content">
                <div class="action-bar">
                    <input type="text" id="user-search" class="form-control" placeholder="Search users..." style="width: 300px;">
                    <button class="btn" onclick="searchUsers()">Search</button>
                    <button class="btn btn-success" onclick="showCreateUserModal()">Create User</button>
                    <button class="btn btn-warning" onclick="exportUsers()">Export Users</button>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>User Management</h3>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Username</th>
                                        <th>Status</th>
                                        <th>Registration</th>
                                        <th>Last Active</th>
                                        <th>Leaks</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table">
                                </tbody>
                            </table>
                        </div>
                        <div class="pagination" id="users-pagination"></div>
                    </div>
                </div>
            </div>

            <!-- Content Moderation Tab -->
            <div id="content" class="tab-content">
                <div class="filter-bar">
                    <select id="content-filter" class="form-control" style="width: 200px;">
                        <option value="all">All Content</option>
                        <option value="public">Public Only</option>
                        <option value="private">Private Only</option>
                        <option value="reported">Reported</option>
                    </select>
                    <input type="text" id="content-search" class="form-control" placeholder="Search content..." style="width: 300px;">
                    <button class="btn" onclick="loadContent()">Filter</button>
                    <button class="btn btn-danger" onclick="bulkDeleteContent()">Bulk Delete</button>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>Content Moderation</h3>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th><input type="checkbox" id="select-all-content"></th>
                                        <th>ID</th>
                                        <th>Title</th>
                                        <th>Author</th>
                                        <th>Category</th>
                                        <th>Visibility</th>
                                        <th>Created</th>
                                        <th>Views</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="content-table">
                                </tbody>
                            </table>
                        </div>
                        <div class="pagination" id="content-pagination"></div>
                    </div>
                </div>
            </div>

            <!-- Reports & Logs Tab -->
            <div id="reports" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>System Logs</h3>
                    </div>
                    <div class="card-body">
                        <div style="max-height: 400px; overflow-y: auto; background: #000; border: 1px solid #333;">
                            <div id="system-logs">
                            </div>
                        </div>
                        <div class="action-bar" style="margin-top: 15px;">
                            <button class="btn" onclick="refreshLogs()">Refresh Logs</button>
                            <button class="btn btn-warning" onclick="clearLogs()">Clear Logs</button>
                            <button class="btn btn-success" onclick="exportLogs()">Export Logs</button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>Security Reports</h3>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Event Type</th>
                                        <th>IP Address</th>
                                        <th>User Agent</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody id="security-reports">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Settings Tab -->
            <div id="settings" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>Application Settings</h3>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">Site Name</label>
                            <input type="text" id="site-name" class="form-control" value="DoxBean">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Registration</label>
                            <select id="registration-enabled" class="form-control">
                                <option value="true">Enabled</option>
                                <option value="false">Disabled</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Max File Size (MB)</label>
                            <input type="number" id="max-file-size" class="form-control" value="10">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Rate Limiting</label>
                            <select id="rate-limiting" class="form-control">
                                <option value="true">Enabled</option>
                                <option value="false">Disabled</option>
                            </select>
                        </div>
                        <button class="btn btn-success" onclick="saveSettings()">Save Settings</button>
                    </div>
                </div>
            </div>

            <!-- Security Tab -->
            <div id="security" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>Security Settings</h3>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">Admin Session Timeout (minutes)</label>
                            <input type="number" id="session-timeout" class="form-control" value="60">
                        </div>
                        <div class="form-group">
                            <label class="form-label">IP Whitelist</label>
                            <textarea id="ip-whitelist" class="form-control" rows="5" placeholder="Enter one IP per line"></textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">IP Blacklist</label>
                            <textarea id="ip-blacklist" class="form-control" rows="5" placeholder="Enter one IP per line"></textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Two-Factor Authentication</label>
                            <select id="2fa-enabled" class="form-control">
                                <option value="true">Enabled</option>
                                <option value="false">Disabled</option>
                            </select>
                        </div>
                        <button class="btn btn-success" onclick="saveSecuritySettings()">Save Security Settings</button>
                    </div>
                </div>
            </div>

            <!-- Backup Tab -->
            <div id="backup" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>Backup & Restore</h3>
                    </div>
                    <div class="card-body">
                        <div class="action-bar">
                            <button class="btn btn-success" onclick="createBackup()">Create Backup</button>
                            <button class="btn btn-warning" onclick="restoreBackup()">Restore Backup</button>
                            <button class="btn btn-danger" onclick="wipeDatabase()">Wipe Database</button>
                        </div>
                        
                        <div class="card" style="margin-top: 20px;">
                            <div class="card-header">
                                <h3>Available Backups</h3>
                            </div>
                            <div class="card-body">
                                <div id="backup-list">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modals -->
    <div id="createUserModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Create New User</h3>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" id="new-username" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" id="new-password" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label">Admin Privileges</label>
                    <select id="new-user-admin" class="form-control">
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" onclick="closeModal('createUserModal')">Cancel</button>
                <button class="btn btn-success" onclick="createUser()">Create User</button>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'dashboard';
        let currentUserPage = 1;
        let currentContentPage = 1;

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            currentTab = tabName;
            
            if (tabName === 'dashboard') {
                loadDashboard();
            } else if (tabName === 'users') {
                loadUsers();
            } else if (tabName === 'content') {
                loadContent();
            } else if (tabName === 'reports') {
                loadReports();
            } else if (tabName === 'backup') {
                loadBackups();
            }
        }

        function showModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        function showCreateUserModal() {
            document.getElementById('new-username').value = '';
            document.getElementById('new-password').value = '';
            document.getElementById('new-user-admin').value = 'false';
            showModal('createUserModal');
        }

        async function apiCall(endpoint, options = {}) {
            try {
                const response = await fetch(endpoint, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    credentials: 'include',
                    ...options
                });
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                return null;
            }
        }

        async function loadDashboard() {
            const stats = await apiCall('/admin/stats');
            if (stats) {
                document.getElementById('total-users').textContent = stats.total_users || 0;
                document.getElementById('total-leaks').textContent = stats.total_leaks || 0;
                document.getElementById('active-sessions').textContent = stats.active_sessions || 0;
                document.getElementById('today-leaks').textContent = stats.today_leaks || 0;
                
                document.getElementById('cpu-usage').style.width = (stats.cpu_usage || 0) + '%';
                document.getElementById('memory-usage').style.width = (stats.memory_usage || 0) + '%';
                document.getElementById('disk-usage').style.width = (stats.disk_usage || 0) + '%';
            }

            const activity = await apiCall('/admin/activity');
            if (activity && activity.recent_activity) {
                const tbody = document.getElementById('recent-activity');
                tbody.innerHTML = activity.recent_activity.map(item => `
                    <tr>
                        <td>${new Date(item.timestamp * 1000).toLocaleString()}</td>
                        <td>${item.username || 'System'}</td>
                        <td>${item.action}</td>
                        <td>${item.ip_address}</td>
                        <td>${item.details}</td>
                    </tr>
                `).join('');
            }
        }

        async function loadUsers(page = 1) {
            const users = await apiCall(`/admin/users?page=${page}`);
            if (users && users.users) {
                const tbody = document.getElementById('users-table');
                tbody.innerHTML = users.users.map(user => `
                    <tr>
                        <td>${user.id}</td>
                        <td>
                            <span class="user-status ${user.status === 'online' ? 'status-online' : user.status === 'banned' ? 'status-banned' : 'status-offline'}"></span>
                            ${user.username}
                            ${user.is_admin ? '<span class="badge badge-warning">Admin</span>' : ''}
                        </td>
                        <td><span class="badge ${user.status === 'online' ? 'badge-success' : user.status === 'banned' ? 'badge-danger' : ''}">${user.status}</span></td>
                        <td>${new Date(user.registered_at * 1000).toLocaleDateString()}</td>
                        <td>${user.last_active ? new Date(user.last_active * 1000).toLocaleString() : 'Never'}</td>
                        <td>${user.leak_count || 0}</td>
                        <td>
                            <button class="btn btn-danger" onclick="banUser('${user.id}')">Ban</button>
                            <button class="btn btn-warning" onclick="resetPassword('${user.id}')">Reset Pass</button>
                            ${!user.is_admin ? `<button class="btn btn-success" onclick="makeAdmin('${user.id}')">Make Admin</button>` : ''}
                        </td>
                    </tr>
                `).join('');

                updatePagination('users-pagination', users.total_pages, page, loadUsers);
            }
        }

        async function loadContent(page = 1) {
            const filter = document.getElementById('content-filter').value;
            const search = document.getElementById('content-search').value;
            
            const content = await apiCall('/admin/content', {
                method: 'POST',
                body: JSON.stringify({
                    page: page,
                    filter: filter,
                    search: search
                })
            });

            if (content && content.content) {
                const tbody = document.getElementById('content-table');
                tbody.innerHTML = content.content.map(item => `
                    <tr>
                        <td><input type="checkbox" value="${item.id}" class="content-checkbox"></td>
                        <td>${item.id}</td>
                        <td>${item.title}</td>
                        <td>${item.author || 'Anonymous'}</td>
                        <td>${item.category}</td>
                        <td><span class="badge ${item.is_public ? 'badge-success' : 'badge-warning'}">${item.is_public ? 'Public' : 'Private'}</span></td>
                        <td>${new Date(item.created_at * 1000).toLocaleString()}</td>
                        <td>${item.views}</td>
                        <td>
                            <button class="btn" onclick="viewContent('${item.id}')">View</button>
                            <button class="btn btn-danger" onclick="deleteContent('${item.id}')">Delete</button>
                            <button class="btn btn-warning" onclick="togglePin('${item.id}')">${item.pinned ? 'Unpin' : 'Pin'}</button>
                        </td>
                    </tr>
                `).join('');

                updatePagination('content-pagination', content.total_pages, page, loadContent);
            }
        }

        async function loadReports() {
            const logs = await apiCall('/admin/logs');
            if (logs && logs.system_logs) {
                const container = document.getElementById('system-logs');
                container.innerHTML = logs.system_logs.map(log => `
                    <div class="log-entry">
                        <span class="log-time">[${new Date(log.timestamp * 1000).toLocaleString()}]</span>
                        <span class="log-${log.level}">${log.message}</span>
                    </div>
                `).join('');
                container.scrollTop = container.scrollHeight;
            }

            const reports = await apiCall('/admin/security-reports');
            if (reports && reports.security_reports) {
                const tbody = document.getElementById('security-reports');
                tbody.innerHTML = reports.security_reports.map(report => `
                    <tr>
                        <td>${new Date(report.timestamp * 1000).toLocaleString()}</td>
                        <td><span class="badge badge-${report.level}">${report.event_type}</span></td>
                        <td>${report.ip_address}</td>
                        <td title="${report.user_agent}">${report.user_agent.substring(0, 50)}...</td>
                        <td>${report.details}</td>
                    </tr>
                `).join('');
            }
        }

        async function loadBackups() {
            const backups = await apiCall('/admin/backups');
            if (backups && backups.backups) {
                const container = document.getElementById('backup-list');
                container.innerHTML = backups.backups.map(backup => `
                    <div class="card" style="margin-bottom: 10px;">
                        <div class="card-body">
                            <strong>${backup.filename}</strong>
                            <div style="color: #666; font-size: 0.8em;">
                                Created: ${new Date(backup.created_at * 1000).toLocaleString()} | 
                                Size: ${backup.size}
                            </div>
                            <div class="action-bar" style="margin-top: 10px;">
                                <button class="btn btn-success" onclick="downloadBackup('${backup.filename}')">Download</button>
                                <button class="btn btn-danger" onclick="deleteBackup('${backup.filename}')">Delete</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }

        function updatePagination(containerId, totalPages, currentPage, callback) {
            const container = document.getElementById(containerId);
            if (totalPages <= 1) {
                container.innerHTML = '';
                return;
            }

            let pagination = '';
            for (let i = 1; i <= totalPages; i++) {
                pagination += `<div class="page-item ${i === currentPage ? 'active' : ''}" onclick="callback(${i})">${i}</div>`;
            }
            container.innerHTML = pagination;
        }

        async function createUser() {
            const username = document.getElementById('new-username').value;
            const password = document.getElementById('new-password').value;
            const isAdmin = document.getElementById('new-user-admin').value === 'true';

            const result = await apiCall('/admin/users', {
                method: 'POST',
                body: JSON.stringify({ username, password, is_admin: isAdmin })
            });

            if (result && !result.error) {
                closeModal('createUserModal');
                loadUsers();
            } else {
                alert('Failed to create user: ' + (result?.error || 'Unknown error'));
            }
        }

        async function banUser(userId) {
            if (confirm('Are you sure you want to ban this user?')) {
                const result = await apiCall(`/admin/users/${userId}/ban`, { method: 'POST' });
                if (result && !result.error) {
                    loadUsers();
                }
            }
        }

        async function makeAdmin(userId) {
            if (confirm('Grant admin privileges to this user?')) {
                const result = await apiCall(`/admin/users/${userId}/make-admin`, { method: 'POST' });
                if (result && !result.error) {
                    loadUsers();
                }
            }
        }

        async function deleteContent(contentId) {
            if (confirm('Permanently delete this content?')) {
                const result = await apiCall(`/admin/content/${contentId}`, { method: 'DELETE' });
                if (result && !result.error) {
                    loadContent();
                }
            }
        }

        async function bulkDeleteContent() {
            const checkboxes = document.querySelectorAll('.content-checkbox:checked');
            const ids = Array.from(checkboxes).map(cb => cb.value);
            
            if (ids.length === 0) {
                alert('Please select content to delete');
                return;
            }

            if (confirm(`Permanently delete ${ids.length} items?`)) {
                const result = await apiCall('/admin/content/bulk-delete', {
                    method: 'POST',
                    body: JSON.stringify({ ids })
                });
                if (result && !result.error) {
                    loadContent();
                }
            }
        }

        async function createBackup() {
            const result = await apiCall('/admin/backup', { method: 'POST' });
            if (result && !result.error) {
                alert('Backup created successfully');
                loadBackups();
            }
        }

        async function logout() {
            const result = await apiCall('/admin/logout', { method: 'POST' });
            if (result && !result.error) {
                window.location.href = '/';
            }
        }

        async function shutdown() {
            if (confirm('Are you sure you want to shutdown the system?')) {
                const result = await apiCall('/admin/shutdown', { method: 'POST' });
                if (result && !result.error) {
                    alert('System shutdown initiated');
                }
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            setInterval(loadDashboard, 30000); // Refresh every 30 seconds
        });

        // Select all content checkbox
        document.getElementById('select-all-content')?.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.content-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'admin.html'), 'w') as f:
        f.write(index_html)

def init_db():
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    # Existing tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at INTEGER,
            is_admin BOOLEAN DEFAULT FALSE,
            is_banned BOOLEAN DEFAULT FALSE,
            last_active INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pastes (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            content TEXT,
            category TEXT DEFAULT 'other',
            is_public BOOLEAN DEFAULT TRUE,
            is_anonymous BOOLEAN DEFAULT FALSE,
            is_pinned BOOLEAN DEFAULT FALSE,
            views INTEGER DEFAULT 0,
            created_at INTEGER,
            modified_at INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Admin system tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT,
            ip_address TEXT,
            details TEXT,
            timestamp INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id TEXT PRIMARY KEY,
            level TEXT,
            message TEXT,
            timestamp INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS security_reports (
            id TEXT PRIMARY KEY,
            event_type TEXT,
            ip_address TEXT,
            user_agent TEXT,
            details TEXT,
            level TEXT,
            timestamp INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id TEXT PRIMARY KEY,
            filename TEXT,
            created_at INTEGER,
            size INTEGER
        )
    ''')
    
    # Create admin user
    c.execute('SELECT COUNT(*) FROM users WHERE username = ?', (ADMIN_USERNAME,))
    if c.fetchone()[0] == 0:
        admin_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO users (id, username, password_hash, created_at, is_admin) VALUES (?, ?, ?, ?, ?)',
            (admin_id, ADMIN_USERNAME, ADMIN_PASSWORD_HASH, int(time.time()), True)
        )
    
    # Default settings
    default_settings = [
        ('site_name', 'DoxBean'),
        ('registration_enabled', 'true'),
        ('max_file_size', '10'),
        ('rate_limiting', 'true'),
        ('session_timeout', '60'),
        ('2fa_enabled', 'false')
    ]
    
    for key, value in default_settings:
        c.execute('INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)', (key, value))
    
    conn.commit()
    conn.close()

# Admin routes
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    return render_template('admin.html')

@app.route('/admin/stats')
@require_login
def admin_stats():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM pastes')
    total_leaks = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM users WHERE last_active > ?', (int(time.time()) - 3600,))
    active_sessions = c.fetchone()[0]
    
    today_start = int(time.time()) - 86400
    c.execute('SELECT COUNT(*) FROM pastes WHERE created_at > ?', (today_start,))
    today_leaks = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_users': total_users,
        'total_leaks': total_leaks,
        'active_sessions': active_sessions,
        'today_leaks': today_leaks,
        'cpu_usage': 45,  # Mock data
        'memory_usage': 68,  # Mock data
        'disk_usage': 23   # Mock data
    })

@app.route('/admin/activity')
@require_login
def admin_activity():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        SELECT al.action, al.ip_address, al.details, al.timestamp, u.username 
        FROM admin_logs al 
        LEFT JOIN users u ON al.user_id = u.id 
        ORDER BY al.timestamp DESC 
        LIMIT 50
    ''')
    activity = c.fetchall()
    conn.close()
    
    return jsonify({
        'recent_activity': [
            {
                'action': row[0],
                'ip_address': row[1],
                'details': row[2],
                'timestamp': row[3],
                'username': row[4]
            }
            for row in activity
        ]
    })

@app.route('/admin/users')
@require_login
def admin_users():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    total_pages = (total_users + limit - 1) // limit
    
    c.execute('''
        SELECT u.id, u.username, u.is_admin, u.is_banned, u.created_at, u.last_active,
               (SELECT COUNT(*) FROM pastes p WHERE p.user_id = u.id) as leak_count
        FROM users u 
        ORDER BY u.created_at DESC 
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    users = c.fetchall()
    conn.close()
    
    return jsonify({
        'users': [
            {
                'id': row[0],
                'username': row[1],
                'is_admin': bool(row[2]),
                'status': 'banned' if row[3] else ('online' if row[5] and row[5] > time.time() - 3600 else 'offline'),
                'registered_at': row[4],
                'last_active': row[5],
                'leak_count': row[6]
            }
            for row in users
        ],
        'total_pages': total_pages,
        'current_page': page
    })

@app.route('/admin/content', methods=['POST'])
@require_login
def admin_content():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    page = data.get('page', 1)
    filter_type = data.get('filter', 'all')
    search = data.get('search', '')
    
    limit = 20
    offset = (page - 1) * limit
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    query = '''
        SELECT p.id, p.title, p.content, p.category, p.is_public, p.is_anonymous, 
               p.created_at, p.views, p.is_pinned, u.username
        FROM pastes p 
        LEFT JOIN users u ON p.user_id = u.id 
        WHERE 1=1
    '''
    params = []
    
    if filter_type == 'public':
        query += ' AND p.is_public = TRUE'
    elif filter_type == 'private':
        query += ' AND p.is_public = FALSE'
    elif filter_type == 'reported':
        query += ' AND p.id IN (SELECT paste_id FROM reports)'
    
    if search:
        query += ' AND (p.title LIKE ? OR p.content LIKE ? OR u.username LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY p.created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    c.execute(query, params)
    content = c.fetchall()
    
    c.execute('SELECT COUNT(*) FROM pastes')
    total_content = c.fetchone()[0]
    total_pages = (total_content + limit - 1) // limit
    
    conn.close()
    
    return jsonify({
        'content': [
            {
                'id': row[0],
                'title': row[1],
                'content_preview': row[2][:100] + ('...' if len(row[2]) > 100 else ''),
                'category': row[3],
                'is_public': bool(row[4]),
                'anonymous': bool(row[5]),
                'created_at': row[6],
                'views': row[7],
                'pinned': bool(row[8]),
                'author': row[9] if not row[5] else None
            }
            for row in content
        ],
        'total_pages': total_pages,
        'current_page': page
    })

@app.route('/admin/logs')
@require_login
def admin_logs():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT level, message, timestamp FROM system_logs ORDER BY timestamp DESC LIMIT 100')
    logs = c.fetchall()
    conn.close()
    
    return jsonify({
        'system_logs': [
            {
                'level': row[0],
                'message': row[1],
                'timestamp': row[2]
            }
            for row in logs
        ]
    })

@app.route('/admin/security-reports')
@require_login
def security_reports():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT event_type, ip_address, user_agent, details, level, timestamp FROM security_reports ORDER BY timestamp DESC LIMIT 50')
    reports = c.fetchall()
    conn.close()
    
    return jsonify({
        'security_reports': [
            {
                'event_type': row[0],
                'ip_address': row[1],
                'user_agent': row[2],
                'details': row[3],
                'level': row[4],
                'timestamp': row[5]
            }
            for row in reports
        ]
    })

@app.route('/admin/users', methods=['POST'])
@require_login
def admin_create_user():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    try:
        c.execute(
            'INSERT INTO users (id, username, password_hash, created_at, is_admin) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, password_hash, int(time.time()), is_admin)
        )
        
        # Log the action
        log_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            (log_id, get_current_user_id(), 'CREATE_USER', request.remote_addr, f'Created user: {username}', int(time.time()))
        )
        
        conn.commit()
        return jsonify({'message': 'User created successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/admin/users/<user_id>/ban', methods=['POST'])
@require_login
def admin_ban_user(user_id):
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    c.execute('UPDATE users SET is_banned = TRUE WHERE id = ?', (user_id,))
    
    # Log the action
    log_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (log_id, get_current_user_id(), 'BAN_USER', request.remote_addr, f'Banned user: {user[0]}', int(time.time()))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User banned successfully'})

@app.route('/admin/users/<user_id>/make-admin', methods=['POST'])
@require_login
def admin_make_admin(user_id):
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    c.execute('UPDATE users SET is_admin = TRUE WHERE id = ?', (user_id,))
    
    # Log the action
    log_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (log_id, get_current_user_id(), 'MAKE_ADMIN', request.remote_addr, f'Made user admin: {user[0]}', int(time.time()))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User granted admin privileges'})

@app.route('/admin/content/<content_id>', methods=['DELETE'])
@require_login
def admin_delete_content(content_id):
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT title FROM pastes WHERE id = ?', (content_id,))
    paste = c.fetchone()
    
    if not paste:
        conn.close()
        return jsonify({'error': 'Content not found'}), 404
    
    c.execute('DELETE FROM pastes WHERE id = ?', (content_id,))
    
    # Log the action
    log_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (log_id, get_current_user_id(), 'DELETE_CONTENT', request.remote_addr, f'Deleted content: {paste[0]}', int(time.time()))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Content deleted successfully'})

@app.route('/admin/content/bulk-delete', methods=['POST'])
@require_login
def admin_bulk_delete_content():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    content_ids = data.get('ids', [])
    
    if not content_ids:
        return jsonify({'error': 'No content selected'}), 400
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    placeholders = ','.join(['?'] * len(content_ids))
    c.execute(f'DELETE FROM pastes WHERE id IN ({placeholders})', content_ids)
    
    # Log the action
    log_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (log_id, get_current_user_id(), 'BULK_DELETE', request.remote_addr, f'Deleted {len(content_ids)} items', int(time.time()))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': f'Deleted {len(content_ids)} items successfully'})

@app.route('/admin/backup', methods=['POST'])
@require_login
def admin_create_backup():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    # In a real implementation, this would create a database backup
    # For now, we'll just log the action
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    
    backup_id = str(uuid.uuid4())
    filename = f'backup_{int(time.time())}.db'
    
    c.execute(
        'INSERT INTO backups (id, filename, created_at, size) VALUES (?, ?, ?, ?)',
        (backup_id, filename, int(time.time()), 1024000)  # Mock size
    )
    
    # Log the action
    log_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO admin_logs (id, user_id, action, ip_address, details, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (log_id, get_current_user_id(), 'CREATE_BACKUP', request.remote_addr, f'Created backup: {filename}', int(time.time()))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Backup created successfully'})

@app.route('/admin/backups')
@require_login
def admin_backups():
    if not is_admin_user():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('doxbin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT filename, created_at, size FROM backups ORDER BY created_at DESC')
    backups = c.fetchall()
    conn.close()
    
    return jsonify({
        'backups': [
            {
                'filename': row[0],
                'created_at': row[1],
                'size': f'{row[2] / 1024 / 1024:.1f} MB'
            }
            for row in backups
        ]
    })

@app.route('/admin/logout', methods=['POST'])
@require_login
def admin_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    create_templates()
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
