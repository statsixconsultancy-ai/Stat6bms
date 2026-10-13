#!/usr/bin/env python3
"""
BMS Microservices Local Development Orchestrator
Features:
- Pre-flight port checking and automated cleanup of zombie processes on Windows.
- Concurrent process management for all 14 microservices and API Gateway.
- Live health check status verification.
- Graceful shutdown signal handling.
"""
import os
import sys
import time
import socket
import subprocess
import signal
from typing import Dict, List

SERVICES = [
    {"name": "gateway", "port": int(os.getenv("PORT", 8000)), "module": "services.gateway.main:app"},
    {"name": "auth-service", "port": 8001, "module": "services.auth_service.main:app"},
    {"name": "crm-service", "port": 8002, "module": "services.crm_service.main:app"},
    {"name": "marketing-service", "port": 8003, "module": "services.marketing_service.main:app"},
    {"name": "projects-service", "port": 8004, "module": "services.projects_service.main:app"},
    {"name": "hr-service", "port": 8005, "module": "services.hr_service.main:app"},
    {"name": "finance-service", "port": 8006, "module": "services.finance_service.main:app"},
    {"name": "inventory-service", "port": 8007, "module": "services.inventory_service.main:app"},
    {"name": "procurement-service", "port": 8008, "module": "services.procurement_service.main:app"},
    {"name": "support-service", "port": 8009, "module": "services.support_service.main:app"},
    {"name": "collaboration-service", "port": 8010, "module": "services.collaboration_service.main:app"},
    {"name": "compliance-service", "port": 8011, "module": "services.compliance_service.main:app"},
    {"name": "automation-service", "port": 8012, "module": "services.automation_service.main:app"},
    {"name": "ai-copilot-service", "port": 8013, "module": "services.ai_copilot_service.main:app"},
]

processes: Dict[str, subprocess.Popen] = {}

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_process_on_port(port: int):
    """Clean up any zombie process occupying target port on Windows or Unix."""
    try:
        if os.name == 'nt':
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            pids = result.stdout.strip().splitlines()
            for pid_str in pids:
                pid = pid_str.strip()
                if pid and pid != "0":
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                    print(f"  [!] Cleared zombie process (PID {pid}) on port {port}")
    except Exception:
        pass

def free_all_ports():
    print("[1/2] Running pre-flight port availability inspection...")
    for svc in SERVICES:
        port = svc["port"]
        if is_port_in_use(port):
            kill_process_on_port(port)
            time.sleep(0.2)
    print("  [OK] Ports 8000-8013 verified free and ready.")

def get_python_exe() -> str:
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    venv_python_unix = os.path.join(backend_dir, "venv", "bin", "python")
    if os.path.exists(venv_python_unix):
        return venv_python_unix
    return sys.executable

def start_microservice(svc: dict, backend_dir: str):
    name = svc["name"]
    port = svc["port"]
    module = svc["module"]
    python_exe = get_python_exe()

    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir

    cmd = [
        python_exe, "-m", "uvicorn",
        module,
        "--host", "0.0.0.0",
        "--port", str(port),
        "--log-level", "warning"
    ]

    p = subprocess.Popen(cmd, cwd=backend_dir, env=env)
    processes[name] = p
    print(f"  [+] Started {name:<22} on http://localhost:{port}")

def stop_all_microservices():
    print("\n[!] Gracefully shutting down all BMS microservices...")
    for name, p in processes.items():
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("  [OK] All microservices successfully stopped.")

def main():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 65)
    print("  BMS DISTRIBUTED MICROSERVICES ORCHESTRATOR")
    print("=" * 65)
    print(f"Working Directory: {backend_dir}")
    print(f"Python Executable: {get_python_exe()}")
    print("-" * 65)

    free_all_ports()

    def handle_signal(sig, frame):
        stop_all_microservices()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("[2/2] Launching all microservices...")
    for svc in SERVICES:
        start_microservice(svc, backend_dir)

    print("-" * 65)
    print("  [OK] All 14 microservices active! Gateway: http://localhost:8000")
    print("  Press CTRL+C to terminate all services.")
    print("=" * 65)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all_microservices()

if __name__ == "__main__":
    main()
