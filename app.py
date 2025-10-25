from flask import Flask, request, jsonify, render_template, Response, session, redirect, url_for
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
                <div class="nav-title">Session</div>
                <a href="#" class="nav-item" onclick="logout()">Logout</a>
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
                        <div class="stat-number">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0</div>
                        <div class="stat-label">Total Leaks</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0</div>
                        <div class="stat-label">Active Sessions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0</div>
                        <div class="stat-label">Leaks Today</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>System Status</h3>
                    </div>
                    <div class="card-body">
                        <p>Admin panel is running successfully.</p>
                        <p>Database functionality disabled on Vercel deployment.</p>
                    </div>
                </div>
            </div>

            <!-- User Management Tab -->
            <div id="users" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>User Management</h3>
                    </div>
                    <div class="card-body">
                        <p>User management requires database access.</p>
                        <p>This feature is disabled in the current deployment.</p>
                    </div>
                </div>
            </div>

            <!-- Content Moderation Tab -->
            <div id="content" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>Content Moderation</h3>
                    </div>
                    <div class="card-body">
                        <p>Content moderation requires database access.</p>
                        <p>This feature is disabled in the current deployment.</p>
                    </div>
                </div>
            </div>

            <!-- Reports & Logs Tab -->
            <div id="reports" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h3>System Information</h3>
                    </div>
                    <div class="card-body">
                        <p>Flask Admin Panel</p>
                        <p>Deployed on Vercel</p>
                        <p>Database: Disabled (Serverless Environment)</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        function logout() {
            if (confirm('Logout from admin panel?')) {
                window.location.href = '/';
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Admin panel loaded');
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'admin.html'), 'w'), 'w') as f:
        f.write(index_html)

# Remove all database-related code and just keep basic routes
@app.route('/')
def index():
    return "DoxBean Admin - System Running"

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/stats')
def admin_stats():
    return jsonify({
        'total_users': 0,
        'total_leaks': 0,
        'active_sessions': 0,
        'today_leaks': 0,
        'cpu_usage': 0,
        'memory_usage': 0,
        'disk_usage': 0
    })

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    create_templates()
    app.run()
