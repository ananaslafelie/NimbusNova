"""
QA DNA - Dashboard Wave Futurist
Design modern cu wave curves, gradienturi, glassmorphism
Integrat cu sistemul functional (master.py)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import uvicorn
import json

app = FastAPI()

MASTER_URL = "http://localhost:8003"

class TaskRequest(BaseModel):
    items: list
    filename: str = "upload.json"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return '''<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA DNA - Distributed Processing</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --accent: #ec4899;
            --dark: #0f172a;
            --darker: #020617;
            --glass: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--darker);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Animated Wave Background */
        .wave-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
        }
        
        .wave {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(180deg, transparent 0%, rgba(99, 102, 241, 0.1) 100%);
        }
        
        .wave svg {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: auto;
        }
        
        .glow-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.5;
            animation: float 20s infinite ease-in-out;
            z-index: 0;
        }
        
        .glow-orb:nth-child(1) {
            width: 600px;
            height: 600px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            top: -200px;
            right: -100px;
            animation-delay: 0s;
        }
        
        .glow-orb:nth-child(2) {
            width: 400px;
            height: 400px;
            background: linear-gradient(135deg, var(--accent), var(--secondary));
            bottom: -100px;
            left: -100px;
            animation-delay: -5s;
        }
        
        .glow-orb:nth-child(3) {
            width: 300px;
            height: 300px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            top: 50%;
            left: 30%;
            animation-delay: -10s;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -30px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.95); }
        }
        
        .app {
            display: flex;
            position: relative;
            z-index: 1;
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            width: 300px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--glass-border);
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            z-index: 100;
        }
        
        .sidebar-header {
            padding: 32px 28px;
            border-bottom: 1px solid var(--glass-border);
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        
        .brand-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 22px;
            box-shadow: 0 10px 40px rgba(99, 102, 241, 0.4);
        }
        
        .brand-text {
            font-weight: 800;
            font-size: 24px;
            background: linear-gradient(135deg, white, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .sidebar-nav {
            flex: 1;
            padding: 28px 20px;
        }
        
        .nav-section {
            margin-bottom: 32px;
        }
        
        .nav-title {
            font-size: 11px;
            font-weight: 700;
            color: #a5b4fc;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 0 12px;
            margin-bottom: 12px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 18px;
            border-radius: 12px;
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            margin-bottom: 6px;
            position: relative;
        }
        
        .nav-item:hover {
            background: rgba(99, 102, 241, 0.1);
            color: white;
            transform: translateX(4px);
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1));
            color: white;
        }
        
        .nav-item.active::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 24px;
            background: linear-gradient(180deg, var(--primary), var(--secondary));
            border-radius: 3px;
        }
        
        .nav-icon {
            width: 22px;
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .sidebar-footer {
            padding: 24px;
            border-top: 1px solid var(--glass-border);
        }
        
        .user-card {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 16px;
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            transition: all 0.3s;
        }
        
        .user-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .user-avatar {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 15px;
        }
        
        .user-role {
            font-size: 12px;
            color: #a5b4fc;
        }
        
        /* Main Content */
        .main {
            flex: 1;
            margin-left: 300px;
            padding: 40px 48px;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 48px;
        }
        
        .header-title {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, white, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header-subtitle {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 6px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 14px 28px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.5);
        }
        
        .btn-secondary {
            background: var(--glass);
            color: white;
            border: 1px solid var(--glass-border);
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            margin-bottom: 48px;
        }
        
        .stat-card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 28px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-6px);
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-icon {
            width: 56px;
            height: 56px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        
        .stat-label {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 40px;
            font-weight: 800;
            background: linear-gradient(135deg, white, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-change {
            font-size: 13px;
            color: #a5b4fc;
            margin-top: 8px;
        }
        
        /* Cards */
        .card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            overflow: hidden;
            transition: all 0.4s;
        }
        
        .card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            padding: 28px 32px;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .card-title {
            font-size: 20px;
            font-weight: 700;
        }
        
        .card-body {
            padding: 32px;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }
        
        /* Upload Zone */
        .upload-zone {
            border: 2px dashed rgba(99, 102, 241, 0.3);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            transition: all 0.4s;
            cursor: pointer;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05));
            position: relative;
            overflow: hidden;
        }
        
        .upload-zone::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s;
        }
        
        .upload-zone:hover {
            border-color: var(--primary);
            transform: translateY(-4px);
        }
        
        .upload-zone:hover::before {
            opacity: 1;
        }
        
        .upload-zone.dragover {
            border-color: var(--accent);
            background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(99, 102, 241, 0.1));
        }
        
        .upload-icon {
            width: 88px;
            height: 88px;
            border-radius: 24px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            margin: 0 auto 28px;
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.4);
            position: relative;
            z-index: 1;
        }
        
        .upload-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        
        .upload-subtitle {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
            position: relative;
            z-index: 1;
        }
        
        .upload-formats {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            position: relative;
            z-index: 1;
        }
        
        .format-badge {
            padding: 6px 14px;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        /* Workers List */
        .worker-item {
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            margin-bottom: 12px;
            transition: all 0.3s;
        }
        
        .worker-item:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateX(4px);
        }
        
        .worker-icon {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        
        .worker-info {
            flex: 1;
        }
        
        .worker-name {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 4px;
        }
        
        .worker-meta {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .worker-status {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }
        
        /* Progress Bar */
        .progress-container {
            margin-top: 20px;
        }
        
        .progress-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 4px;
            transition: width 0.3s;
        }
        
        .progress-text {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 8px;
        }
        
        /* Page */
        .page {
            display: none;
            animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .page.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 40px;
        }
        
        .empty-state-icon {
            width: 80px;
            height: 80px;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 24px;
            border: 1px solid var(--glass-border);
        }
        
        .empty-state h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .empty-state p {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
        }
        
        /* Toast */
        .toast-container {
            position: fixed;
            top: 100px;
            right: 40px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .toast {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 18px 24px;
            display: flex;
            align-items: center;
            gap: 14px;
            min-width: 320px;
            animation: slideIn 0.4s ease;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .toast.success { border-left: 3px solid #34d399; }
        .toast.error { border-left: 3px solid #f87171; }
        
        /* Logs */
        .log-item {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 16px 20px;
            border-bottom: 1px solid var(--glass-border);
            transition: all 0.2s;
        }
        
        .log-item:hover {
            background: rgba(99, 102, 241, 0.05);
        }
        
        .log-badge {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-top: 6px;
            flex-shrink: 0;
        }
        
        .log-badge.success { background: #34d399; }
        .log-badge.info { background: var(--primary); }
        .log-badge.warning { background: #fbbf24; }
        .log-badge.error { background: #f87171; }
        
        .log-content {
            flex: 1;
        }
        
        .log-message {
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .log-meta {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
        }
        
        /* Responsive */
        @media (max-width: 1200px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; padding: 24px; }
            .stats-grid { grid-template-columns: 1fr; }
            .grid-2 { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Background Effects -->
    <div class="glow-orb"></div>
    <div class="glow-orb"></div>
    <div class="glow-orb"></div>
    
    <div class="toast-container" id="toastContainer"></div>
    
    <div class="app">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="brand">
                    <div class="brand-icon">Q</div>
                    <span class="brand-text">QA DNA</span>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <div class="nav-title">Principal</div>
                    <a href="#" class="nav-item active" onclick="showPage(\'dashboard\', this)">
                        <span class="nav-icon">◆</span>
                        Dashboard
                    </a>
                    <a href="#" class="nav-item" onclick="showPage(\'upload\', this)">
                        <span class="nav-icon">↑</span>
                        Upload
                    </a>
                    <a href="#" class="nav-item" onclick="showPage(\'logs\', this)">
                        <span class="nav-icon">◈</span>
                        Logs
                    </a>
                </div>
                
                <div class="nav-section">
                    <div class="nav-title">Sistem</div>
                    <a href="#" class="nav-item" onclick="showPage(\'workers\', this)">
                        <span class="nav-icon">◉</span>
                        Workeri
                    </a>
                    <a href="#" class="nav-item" onclick="showPage(\'tasks\', this)">
                        <span class="nav-icon">⚡</span>
                        Taskuri
                    </a>
                </div>
            </nav>
            
            <div class="sidebar-footer">
                <div class="user-card">
                    <div class="user-avatar">G</div>
                    <div>
                        <div class="user-name">Guest</div>
                        <div class="user-role">Administrator</div>
                    </div>
                </div>
            </div>
        </aside>
        
        <!-- Main Content -->
        <main class="main">
            <!-- Dashboard Page -->
            <div class="page active" id="dashboardPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Dashboard</h1>
                        <p class="header-subtitle">Monitorizează sistemul distribuit în timp real</p>
                    </div>
                    <div>
                        <button class="btn btn-secondary" onclick="refreshData()">↻ Refresh</button>
                        <button class="btn btn-primary" style="margin-left: 12px;" onclick="showPage(\'upload\', null)">+ Upload Nou</button>
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">◉</div>
                        <div class="stat-label">Workeri Activi</div>
                        <div class="stat-value" id="statWorkers">0</div>
                        <div class="stat-change">Online acum</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">◈</div>
                        <div class="stat-label">Taskuri în Coadă</div>
                        <div class="stat-value" id="statQueue">0</div>
                        <div class="stat-change">În așteptare</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">✓</div>
                        <div class="stat-label">Completate</div>
                        <div class="stat-value" id="statCompleted">0</div>
                        <div class="stat-change">100% succes</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-label">CPU Mediu</div>
                        <div class="stat-value" id="statCpu">0%</div>
                        <div class="stat-change">Utilizare cluster</div>
                    </div>
                </div>
                
                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">📁 Upload Fișier</h3>
                        </div>
                        <div class="card-body">
                            <div class="upload-zone" id="uploadZone" onclick="document.getElementById(\'fileInput\').click()">
                                <div class="upload-icon">↑</div>
                                <div class="upload-title">Trage fișierul aici</div>
                                <div class="upload-subtitle">sau click pentru a selecta</div>
                                <div class="upload-formats">
                                    <span class="format-badge">JSON</span>
                                    <span class="format-badge">CSV</span>
                                    <span class="format-badge">TXT</span>
                                </div>
                            </div>
                            <input type="file" id="fileInput" style="display: none;" accept=".json,.csv,.txt" onchange="handleFileSelect(event)">
                            <div class="progress-container" id="uploadProgress" style="display: none;">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="progressFill" style="width: 0%;"></div>
                                </div>
                                <div class="progress-text" id="progressText">Se procesează...</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">🖥️ Workeri Conectați</h3>
                        </div>
                        <div class="card-body" id="workersListContainer">
                            <div class="empty-state">
                                <div class="empty-state-icon">◉</div>
                                <h3>Niciun worker conectat</h3>
                                <p>Pornește workeri pentru a-i vedea aici</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Upload Page -->
            <div class="page" id="uploadPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Upload</h1>
                        <p class="header-subtitle">Încarcă fișiere pentru procesare distribuită</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <div class="upload-zone" id="uploadZoneFull" onclick="document.getElementById(\'fileInput2\').click()">
                            <div class="upload-icon">↑</div>
                            <div class="upload-title">Selectează fișierul</div>
                            <div class="upload-subtitle">Suportă fișiere până la 100MB</div>
                            <div class="upload-formats">
                                <span class="format-badge">JSON</span>
                                <span class="format-badge">CSV</span>
                                <span class="format-badge">TXT</span>
                            </div>
                        </div>
                        <input type="file" id="fileInput2" style="display: none;" accept=".json,.csv,.txt" onchange="handleFileSelect(event)">
                    </div>
                </div>
            </div>
            
            <!-- Logs Page -->
            <div class="page" id="logsPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Logs</h1>
                        <p class="header-subtitle">Istoric activitate și procese</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body" id="logsList">
                        <div class="empty-state">
                            <div class="empty-state-icon">◈</div>
                            <h3>Nicio activitate înregistrată</h3>
                            <p>Logurile vor apărea aici când începi să procesezi taskuri</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Workers Page -->
            <div class="page" id="workersPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Workeri</h1>
                        <p class="header-subtitle">Noduri de procesare în cluster</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body" id="workersListFull">
                        <div class="empty-state">
                            <div class="empty-state-icon">◉</div>
                            <h3>Niciun worker conectat</h3>
                            <p>Pornește workeri pentru a-i vedea aici</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tasks Page -->
            <div class="page" id="tasksPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Taskuri</h1>
                        <p class="header-subtitle">Sarcini în procesare</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body" id="tasksList">
                        <div class="empty-state">
                            <div class="empty-state-icon">⚡</div>
                            <h3>Nicio sarcină activă</h3>
                            <p>Taskurile vor apărea aici</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        // State
        let currentTaskId = null;
        let pollInterval = null;
        
        // Navigation
        function showPage(pageName, element) {
            document.querySelectorAll(\'.page\').forEach(p => p.classList.remove(\'active\'));
            document.querySelectorAll(\'.nav-item\').forEach(n => n.classList.remove(\'active\'));
            
            document.getElementById(pageName + \'Page\').classList.add(\'active\');
            if (element) element.classList.add(\'active\');
            
            // Load data
            if (pageName === \'workers\' || pageName === \'dashboard\') loadWorkers();
            if (pageName === \'logs\') loadLogs();
            if (pageName === \'tasks\') loadTasks();
        }
        
        // Drag & Drop
        const uploadZones = [\'uploadZone\', \'uploadZoneFull\'];
        uploadZones.forEach(id => {
            const zone = document.getElementById(id);
            if (zone) {
                zone.addEventListener(\'dragover\', (e) => {
                    e.preventDefault();
                    zone.classList.add(\'dragover\');
                });
                
                zone.addEventListener(\'dragleave\', () => {
                    zone.classList.remove(\'dragover\');
                });
                
                zone.addEventListener(\'drop\', (e) => {
                    e.preventDefault();
                    zone.classList.remove(\'dragover\');
                    const files = e.dataTransfer.files;
                    if (files.length > 0) uploadFile(files[0]);
                });
            }
        });
        
        // File Select
        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) uploadFile(file);
        }
        
        // Upload File
        async function uploadFile(file) {
            showToast(\'Se citește fișierul...\', \'info\');
            
            try {
                const text = await file.text();
                let items = [];
                
                try {
                    const data = JSON.parse(text);
                    items = Array.isArray(data) ? data : [data];
                } catch (e) {
                    items = [{ content: text, filename: file.name }];
                }
                
                showToast(`Se trimit ${items.length} iteme...`, \'info\');
                
                const res = await fetch(\'/api/submit-task\', {
                    method: \'POST\',
                    headers: { \'Content-Type\': \'application/json\' },
                    body: JSON.stringify({ items, filename: file.name })
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || \'Eroare\');
                
                currentTaskId = data.task_id;
                showToast(`Task ${data.task_id} creat!`, \'success\');
                
                // Show progress
                document.getElementById(\'uploadProgress\').style.display = \'block\';
                document.getElementById(\'progressFill\').style.width = \'10%\';
                
                // Poll for results
                pollTaskStatus(data.task_id);
                
            } catch (err) {
                showToast(err.message, \'error\');
            }
        }
        
        // Poll Task Status
        async function pollTaskStatus(taskId) {
            if (pollInterval) clearInterval(pollInterval);
            
            pollInterval = setInterval(async () => {
                try {
                    const res = await fetch(`/api/task-status/${taskId}`);
                    const data = await res.json();
                    
                    const pct = data.total_chunks > 0 
                        ? (data.done_chunks / data.total_chunks) * 100 
                        : 0;
                    
                    document.getElementById(\'progressFill\').style.width = pct + \'%\';
                    document.getElementById(\'progressText\').textContent = 
                        `[${data.done_chunks}/${data.total_chunks}] ${Math.round(pct)}% - ${data.status}`;
                    
                    if (data.status === \'COMPLETED\') {
                        clearInterval(pollInterval);
                        showToast(\'Task completat!\', \'success\');
                        document.getElementById(\'uploadProgress\').style.display = \'none\';
                        refreshData();
                    } else if (data.status === \'FAILED\') {
                        clearInterval(pollInterval);
                        showToast(\'Task eșuat!\', \'error\');
                        document.getElementById(\'uploadProgress\').style.display = \'none\';
                    }
                } catch (err) {
                    console.error(err);
                }
            }, 1000);
        }
        
        // Load Workers
        async function loadWorkers() {
            try {
                const res = await fetch(\'/api/master-status\');
                const data = await res.json();
                
                document.getElementById(\'statWorkers\').textContent = data.workers?.length || 0;
                document.getElementById(\'statQueue\').textContent = data.queue_len || 0;
                
                const completed = data.tasks?.filter(t => t[1] === \'COMPLETED\').length || 0;
                document.getElementById(\'statCompleted\').textContent = completed;
                
                // Render workers
                const container = document.getElementById(\'workersListContainer\');
                const fullContainer = document.getElementById(\'workersListFull\');
                
                if (data.workers?.length > 0) {
                    const workersHtml = data.workers.map(w => `
                        <div class="worker-item">
                            <div class="worker-icon">W</div>
                            <div class="worker-info">
                                <div class="worker-name">${w.id}</div>
                                <div class="worker-meta">CPU: ${w.cpu?.toFixed(1) || 0}% | Chunks: ${w.chunks_done || 0}</div>
                            </div>
                            <span class="worker-status">${w.status}</span>
                        </div>
                    `).join(\'\');
                    
                    if (container) container.innerHTML = workersHtml;
                    if (fullContainer) fullContainer.innerHTML = workersHtml;
                }
                
            } catch (err) {
                console.error(\'Eroare load workers:\', err);
            }
        }
        
        // Load Logs
        async function loadLogs() {
            // Implementare logs
        }
        
        // Load Tasks
        async function loadTasks() {
            // Implementare tasks
        }
        
        // Refresh Data
        async function refreshData() {
            showToast(\'Se actualizează datele...\', \'info\');
            await loadWorkers();
        }
        
        // Toast
        function showToast(message, type = \'info\') {
            const container = document.getElementById(\'toastContainer\');
            const toast = document.createElement(\'div\');
            toast.className = `toast ${type}`;
            
            const icons = { success: \'✓\', error: \'✗\', info: \'i\' };
            toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
            
            container.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        // Init
        document.addEventListener(\'DOMContentLoaded\', () => {
            loadWorkers();
            setInterval(loadWorkers, 5000);
            showToast(\'Bun venit la QA DNA!\', \'success\');
        });
    </script>
</body>
</html>'''

# API Endpoints pentru integrare cu Master
@app.post("/api/submit-task")
async def submit_task(task: TaskRequest):
    """Trimite task la Master"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{MASTER_URL}/submit-task",
                json={"items": task.items},
                timeout=30.0
            )
            return r.json()
    except Exception as e:
        raise HTTPException(500, f"Eroare conexiune Master: {e}")

@app.get("/api/task-status/{task_id}")
async def task_status(task_id: str):
    """Verifică status task"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
            return r.json()
    except Exception as e:
        raise HTTPException(500, f"Eroare: {e}")

@app.get("/api/master-status")
async def master_status():
    """Preia status de la Master"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
            return r.json()
    except Exception as e:
        return {"online": False, "error": str(e), "workers": [], "queue_len": 0, "tasks": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
