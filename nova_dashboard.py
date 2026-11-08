"""
NOVA - Distributed Processing Dashboard
Design futurist cu wave curves, glassmorphism
Cu Invite System - trimite link, devine worker automat
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import uvicorn
import json
import uuid
import os

app = FastAPI(title="NOVA Dashboard")

MASTER_URL = "http://localhost:8003"

# Storage in memorie pentru invites
_invites = {}  # invite_code -> {team_name, master_ip, created_at}

class TaskRequest(BaseModel):
    items: list
    filename: str = "upload.json"

class InviteRequest(BaseModel):
    team_name: str
    master_ip: str = "localhost"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return '''<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOVA - Distributed Processing</title>
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
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -30px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.95); }
        }
        
        .app { display: flex; position: relative; z-index: 1; }
        
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
        
        .sidebar-nav { flex: 1; padding: 28px 20px; }
        
        .nav-section { margin-bottom: 32px; }
        
        .nav-title {
            font-size: 11px;
            font-weight: 700;
            color: #a5b4fc;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 0 12px;
            margin-bottom: 14px;
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
            transition: all 0.3s;
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
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1));
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
        
        .user-name { font-weight: 600; font-size: 15px; }
        .user-role { font-size: 12px; color: #a5b4fc; }
        
        /* Main */
        .main { flex: 1; margin-left: 300px; padding: 40px 48px; }
        
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
            transition: all 0.3s;
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
        }
        
        /* Cards */
        .card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            overflow: hidden;
            transition: all 0.4s;
            margin-bottom: 24px;
        }
        
        .card:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .card-header {
            padding: 28px 32px;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .card-title { font-size: 20px; font-weight: 700; }
        .card-body { padding: 32px; }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }
        
        /* Upload */
        .upload-zone {
            border: 2px dashed rgba(99, 102, 241, 0.3);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            transition: all 0.4s;
            cursor: pointer;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05));
        }
        
        .upload-zone:hover {
            border-color: var(--primary);
            transform: translateY(-4px);
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
        }
        
        .upload-title { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
        .upload-subtitle { font-size: 14px; color: rgba(255, 255, 255, 0.6); }
        
        /* Invite System */
        .invite-box {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
            border: 2px dashed var(--accent);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
        }
        
        .invite-link {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 16px;
            font-family: monospace;
            font-size: 14px;
            color: var(--accent);
            margin: 16px 0;
            cursor: pointer;
            user-select: all;
        }
        
        .invite-link:hover {
            border-color: var(--accent);
        }
        
        .copy-btn {
            background: var(--accent);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        
        .copy-btn:hover {
            transform: scale(1.05);
        }
        
        /* Page */
        .page { display: none; animation: fadeIn 0.5s; }
        .page.active { display: block; }
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
        
        .empty-state h3 { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
        .empty-state p { font-size: 14px; color: rgba(255, 255, 255, 0.6); }
        
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
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Input */
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-label {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 8px;
            display: block;
        }
        
        .input-field {
            width: 100%;
            padding: 14px 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            color: white;
            font-size: 15px;
            transition: all 0.3s;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; padding: 24px; }
            .grid-2 { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="glow-orb"></div>
    <div class="glow-orb"></div>
    <div class="toast-container" id="toastContainer"></div>
    
    <div class="app">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="brand">
                    <div class="brand-icon">N</div>
                    <span class="brand-text">NOVA</span>
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
                    <a href="#" class="nav-item" onclick="showPage(\'workers\', this)">
                        <span class="nav-icon">◉</span>
                        Workeri
                    </a>
                </div>
                
                <div class="nav-section">
                    <div class="nav-title">Echipa</div>
                    <a href="#" class="nav-item" onclick="showPage(\'invite\', this)">
                        <span class="nav-icon">+</span>
                        Invită în echipă
                    </a>
                </div>
            </nav>
            
            <div class="sidebar-footer">
                <div class="user-card">
                    <div class="user-avatar">A</div>
                    <div>
                        <div class="user-name">Admin</div>
                        <div class="user-role">Team Owner</div>
                    </div>
                </div>
            </div>
        </aside>
        
        <main class="main">
            <!-- Dashboard -->
            <div class="page active" id="dashboardPage">
                <div class="header">
                    <div>
                        <h1 class="header-title">Dashboard</h1>
                        <p class="header-subtitle">Monitorizează sistemul distribuit</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="showPage(\'invite\', null)">+ Invită în echipă</button>
                    </div>
                </div>
                
                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">📁 Upload</h3>
                        </div>
                        <div class="card-body">
                            <div class="upload-zone" onclick="document.getElementById(\'fileInput\').click()">
                                <div class="upload-icon">↑</div>
                                <div class="upload-title">Trage fișierul aici</div>
                                <div class="upload-subtitle">sau click pentru a selecta JSON, CSV, TXT</div>
                            </div>
                            <input type="file" id="fileInput" style="display: none;" accept=".json,.csv,.txt">
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">🖥️ Workeri</h3>
                        </div>
                        <div class="card-body">
                            <div class="empty-state">
                                <div class="empty-state-icon">◉</div>
                                <h3>Niciun worker</h3>
                                <p>Folosește "Invită în echipă" pentru a adăuga laptopuri</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Upload -->
            <div class="page" id="uploadPage">
                <div class="header">
                    <h1 class="header-title">Upload</h1>
                </div>
                <div class="card">
                    <div class="card-body">
                        <div class="upload-zone">
                            <div class="upload-icon">↑</div>
                            <div class="upload-title">Selectează fișierul</div>
                            <div class="upload-subtitle">Maxim 100MB</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Workers -->
            <div class="page" id="workersPage">
                <div class="header">
                    <h1 class="header-title">Workeri</h1>
                </div>
                <div class="card">
                    <div class="card-body">
                        <div class="empty-state">
                            <div class="empty-state-icon">◉</div>
                            <h3>Niciun worker conectat</h3>
                            <p>Invită membri în echipă pentru a procesa taskuri</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Invite System -->
            <div class="page" id="invitePage">
                <div class="header">
                    <h1 class="header-title">Invită în Echipă</h1>
                    <p class="header-subtitle">Trimite un link pentru ca alții să devină workeri</p>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <div class="input-group">
                            <label class="input-label">Numele echipei</label>
                            <input type="text" class="input-field" id="teamName" placeholder="Ex: QA DNA Team" value="Team NOVA">
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label">IP Public / Tailscale IP</label>
                            <input type="text" class="input-field" id="masterIp" placeholder="Ex: 100.x.x.x sau 192.168.x.x" value="localhost">
                        </div>
                        
                        <button class="btn btn-primary" onclick="generateInvite()" style="width: 100%;">Generează Link de Invitație</button>
                        
                        <div id="inviteResult" style="display: none; margin-top: 32px;">
                            <div class="invite-box">
                                <h3 style="margin-bottom: 16px;">🎉 Link generat!</h3>
                                <p style="color: rgba(255,255,255,0.7); margin-bottom: 16px;">Trimite acest link prietenului tău. Când accesează linkul:</p>
                                <ul style="color: rgba(255,255,255,0.7); margin-bottom: 20px; padding-left: 20px;">
                                    <li>Descarcă automat aplicația de worker</li>
                                    <li>Se conectează automat la echipa ta</li>
                                    <li>Începe să proceseze taskuri</li>
                                </ul>
                                
                                <div class="invite-link" id="inviteLink" onclick="copyInvite()">
                                    http://localhost:8090/join/ABC123
                                </div>
                                
                                <button class="copy-btn" onclick="copyInvite()">Copiază Link</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        function showPage(pageName, element) {
            document.querySelectorAll(\'.page\').forEach(p => p.classList.remove(\'active\'));
            document.querySelectorAll(\'.nav-item\').forEach(n => n.classList.remove(\'active\'));
            document.getElementById(pageName + \'Page\').classList.add(\'active\');
            if (element) element.classList.add(\'active\');
        }
        
        async function generateInvite() {
            const teamName = document.getElementById(\'teamName\').value;
            const masterIp = document.getElementById(\'masterIp\').value;
            
            if (!teamName || !masterIp) {
                showToast(\'Completează toate câmpurile\', \'error\');
                return;
            }
            
            try {
                const res = await fetch(\'/api/create-invite\', {
                    method: \'POST\',
                    headers: { \'Content-Type\': \'application/json\' },
                    body: JSON.stringify({ team_name: teamName, master_ip: masterIp })
                });
                
                const data = await res.json();
                if (res.ok) {
                    document.getElementById(\'inviteLink\').textContent = data.invite_url;
                    document.getElementById(\'inviteResult\').style.display = \'block\';
                    showToast(\'Link generat! Trimite-l prietenului tău.\', \'success\');
                }
            } catch (err) {
                showToast(\'Eroare la generare link\', \'error\');
            }
        }
        
        function copyInvite() {
            const link = document.getElementById(\'inviteLink\').textContent;
            navigator.clipboard.writeText(link).then(() => {
                showToast(\'Link copiat în clipboard!\', \'success\');
            });
        }
        
        function showToast(message, type = \'info\') {
            const container = document.getElementById(\'toastContainer\');
            const toast = document.createElement(\'div\');
            toast.className = \'toast \' + type;
            toast.innerHTML = `<span>${type === \'success\' ? \'✓\' : \'✗\'}</span><span>${message}</span>`;
            container.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    </script>
</body>
</html>'''

@app.post("/api/create-invite")
async def create_invite(invite: InviteRequest):
    """Creează un invite link pentru echipă"""
    try:
        invite_code = str(uuid.uuid4())[:8].upper()
        
        _invites[invite_code] = {
            "team_name": invite.team_name,
            "master_ip": invite.master_ip,
            "created_at": str(uuid.uuid1())
        }
        
        invite_url = f"http://localhost:8090/join/{invite_code}"
        
        return {
            "invite_code": invite_code,
            "invite_url": invite_url,
            "team_name": invite.team_name,
            "master_ip": invite.master_ip
        }
    except Exception as e:
        raise HTTPException(500, f"Eroare: {e}")

@app.get("/join/{invite_code}", response_class=HTMLResponse)
def join_team(invite_code: str):
    """Pagina pentru a primi invite și descărca worker"""
    invite = _invites.get(invite_code)
    if not invite:
        return '''<!DOCTYPE html>
<html><body style="font-family: Arial; text-align: center; padding: 100px;">
<h1>❌ Invitație invalidă</h1>
<p>Acest link a expirat sau nu există.</p>
</body></html>'''
    
    master_ip = invite.get("master_ip", "localhost")
    team_name = invite.get("team_name", "NOVA Team")
    
    return f'''<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alătură-te echipei {team_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 24px;
            padding: 48px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25);
        }}
        .logo {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #6366f1, #ec4899);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: 800;
            color: white;
            margin: 0 auto 24px;
        }}
        h1 {{ font-size: 28px; margin-bottom: 12px; color: #1a1a2e; }}
        .team {{ color: #6366f1; font-weight: 600; margin-bottom: 24px; }}
        p {{ color: #6b7280; margin-bottom: 32px; line-height: 1.6; }}
        .steps {{
            background: #f3f4f6;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 32px;
            text-align: left;
        }}
        .step {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .step:last-child {{ margin-bottom: 0; }}
        .step-num {{
            width: 32px;
            height: 32px;
            background: #6366f1;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }}
        .btn {{
            display: block;
            width: 100%;
            padding: 18px 32px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
        }}
        .ip-info {{
            background: #e0e7ff;
            border: 1px solid #6366f1;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 24px;
            font-family: monospace;
            font-size: 14px;
            color: #1e40af;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">N</div>
        <h1>Alătură-te echipei</h1>
        <div class="team">{team_name}</div>
        
        <p>Devino worker în sistemul distribuit NOVA. Laptopul tău va procesa taskuri automat.</p>
        
        <div class="ip-info">
            Se va conecta la: {master_ip}:8003
        </div>
        
        <div class="steps">
            <div class="step">
                <div class="step-num">1</div>
                <div>Descarcă aplicația de worker</div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div>Rulează și conectează-te automat</div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div>Începe să procesezi taskuri</div>
            </div>
        </div>
        
        <button class="btn" onclick="downloadWorker()">⬇️ Descarcă Worker</button>
    </div>
    
    <script>
        function downloadWorker() {{
            // Generăm scriptul de worker configurat automat
            const masterIp = "{master_ip}";
            const inviteCode = "{invite_code}";
            
            const workerScript = `# NOVA Worker Auto-Config
# Se conectează automat la: ${{masterIp}}

import requests
import time
import json
import platform

MASTER_URL = "http://${{masterIp}}:8003"
WORKER_ID = "worker-" + platform.node().lower().replace(" ", "-")

def register():
    try:
        r = requests.post(f"{{{{MASTER_URL}}}}/register", 
            json={{{{"worker_id": WORKER_ID, "ip": "127.0.0.1"}}}},
            timeout=10
        )
        print(f"Înregistrat: {{{{r.json()}}}}")
        return True
    except Exception as e:
        print(f"Eroare înregistrare: {{{{e}}}}")
        return False

def get_task():
    try:
        r = requests.get(f"{{{{MASTER_URL}}}}/get-task", 
            params={{{{"worker_id": WORKER_ID, "cpu_percent": 10, "ram_free_mb": 4000}}}},
            timeout=30
        )
        return r.json().get("chunk")
    except:
        return None

def process_chunk(chunk):
    # Procesare simplă - sortare
    data = chunk.get("data", [])
    results = [dict(item, **{{{{"processed": True, "by": WORKER_ID}}}}) for item in data]
    return results

def submit_result(chunk_id, results):
    try:
        r = requests.post(f"{{{{MASTER_URL}}}}/submit-result",
            json={{{{"worker_id": WORKER_ID, "chunk_id": chunk_id, "results": results}}}},
            timeout=30
        )
        return r.json()
    except Exception as e:
        print(f"Eroare submit: {{{{e}}}}")
        return None

def main():
    print("="*60)
    print("  NOVA Worker")
    print("="*60)
    print(f"Worker ID: {{{{WORKER_ID}}}}")
    print(f"Master: {{{{MASTER_URL}}}}")
    print("="*60)
    
    if not register():
        print("Nu m-am putut înregistra. Verifică conexiunea.")
        return
    
    print("✓ Înregistrat cu succes!")
    print("Aștept taskuri...")
    
    while True:
        chunk = get_task()
        if chunk:
            print(f"Primit chunk: {{{{chunk['id']}}}}")
            results = process_chunk(chunk)
            submit_result(chunk["id"], results)
            print(f"✓ Completat: {{{{chunk['id']}}}}")
        else:
            time.sleep(1)

if __name__ == "__main__":
    main()
`;
            
            // Descarcă fișierul
            const blob = new Blob([workerScript], {{ type: 'text/x-python' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'nova_worker.py';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            alert('✓ Worker descărcat!\\n\\n1. Salvează fișierul nova_worker.py\\n2. Instalează: pip install requests\\n3. Rulează: python nova_worker.py\\n\\nSe va conecta automat la {master_ip}');
        }}
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
    print("="*60)
    print("  NOVA Dashboard")
    print("="*60)
    print("  http://localhost:8090")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8090)
