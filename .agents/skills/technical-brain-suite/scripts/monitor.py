import requests
import os
import sys
from dotenv import load_dotenv

# Cargar .env desde el directorio de la suite o el raíz
load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOKEN = os.getenv('GITHUB_TOKEN')
REPOS = [
    ('quant-ozkr/agente-hostinger', 'tesis-brainstem'),
    ('quant-ozkr/tesis-calculadora-fiscal', 'tesis-logic-mcp'),
    ('quant-ozkr/agencia-mkt-aut', 'tesis-backend')
]

def get_status(repo, branch='main'):
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1&branch={branch}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
    try:
        r = requests.get(url, headers=headers).json()
        if r.get("workflow_runs"):
            run = r["workflow_runs"][0]
            return run['status'], run['conclusion'], run['html_url']
    except:
        pass
    return "unknown", "unknown", "N/A"

def run():
    print(f"{'REPOSITORIO':<40} | {'BRANCH':<10} | {'STATUS':<12} | {'CONCLUSION'}")
    print("-" * 85)
    for repo, service in REPOS:
        for branch in ['main', 'staging']:
            status, conclusion, url = get_status(repo, branch)
            symbol = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"
            print(f"{repo:<40} | {branch:<10} | {status:<12} | {symbol} {conclusion}")

if __name__ == "__main__":
    run()
