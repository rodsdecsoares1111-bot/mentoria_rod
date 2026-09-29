import json
import os
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from collectors.instagram import get_instagram_media
from collectors.linkedin import get_linkedin_posts
from processor.social_score import calcular_scores_posts


load_dotenv()
ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
LOCK = threading.Lock()
POSTS = []
UPDATED_AT = None
PLATFORM_STATUS = {}


def _credentials_status():
    return {
        "instagram": bool(
            os.getenv("INSTAGRAM_ACCESS_TOKEN") and os.getenv("INSTAGRAM_USER_ID")
        ),
        "linkedin": bool(
            os.getenv("LINKEDIN_ACCESS_TOKEN")
            and os.getenv("LINKEDIN_ORGANIZATION_ID")
        ),
    }


def refresh_social_data():
    global POSTS, UPDATED_AT, PLATFORM_STATUS
    credentials = _credentials_status()
    collected = []
    status = {}

    sources = (
        (
            "instagram",
            credentials["instagram"],
            lambda: get_instagram_media(
                os.getenv("INSTAGRAM_ACCESS_TOKEN"),
                os.getenv("INSTAGRAM_USER_ID"),
                os.getenv("INSTAGRAM_API_VERSION", "v22.0"),
            ),
        ),
        (
            "linkedin",
            credentials["linkedin"],
            lambda: get_linkedin_posts(
                os.getenv("LINKEDIN_ACCESS_TOKEN"),
                os.getenv("LINKEDIN_ORGANIZATION_ID"),
                os.getenv("LINKEDIN_API_VERSION", "202601"),
            ),
        ),
    )

    # Uma rede sem credenciais não impede a atualização da outra.
    for platform, configured, collect in sources:
        if not configured:
            status[platform] = {
                "state": "not_configured",
                "message": "Credenciais não configuradas",
                "count": 0,
            }
            continue
        try:
            posts = collect()
            collected.extend(posts)
            no_metrics = sum(not post.get("metrics_available", False) for post in posts)
            status[platform] = {
                "state": "ok",
                "message": (
                    f"{no_metrics} publicação(ões) sem métricas liberadas pela API"
                    if no_metrics else "Dados atualizados"
                ),
                "count": len(posts),
            }
        except Exception as error:
            # Não devolve detalhes da exceção, que podem conter URLs ou credenciais.
            status[platform] = {
                "state": "error",
                "message": "Falha ao consultar a API. Verifique token e permissões.",
                "count": 0,
            }

    calcular_scores_posts(collected)
    with LOCK:
        POSTS = collected
        UPDATED_AT = datetime.now(timezone.utc).isoformat()
        PLATFORM_STATUS = status
    return get_dashboard_data()


def get_dashboard_data():
    with LOCK:
        posts = sorted(POSTS, key=lambda post: post.get("score", 0), reverse=True)
        return {
            "posts": posts,
            "updated_at": UPDATED_AT,
            "platforms": PLATFORM_STATUS,
            "configured": _credentials_status(),
        }


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if urlparse(self.path).path == "/api/posts":
            self._send_json(get_dashboard_data())
            return
        if urlparse(self.path).path.startswith("/api/"):
            self._send_json({"error": "Endpoint não encontrado"}, 404)
            return
        if urlparse(self.path).path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/refresh":
            self._send_json({"error": "Endpoint não encontrado"}, 404)
            return
        self._send_json(refresh_social_data())

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if not urlparse(self.path).path.startswith("/api/"):
            super().log_message(format, *args)


def run_server():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    address = f"http://{host}:{port}"
    print(f"Mentoria Social está disponível em {address}")
    threading.Timer(0.8, webbrowser.open, args=(address,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()