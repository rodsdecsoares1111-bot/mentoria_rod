import json
import os
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from ai.analyzer import AIAnalyzer
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
AI_TIPS = {}
DEMO_MODE = False


class AIConfigurationError(Exception):
    pass


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


def _demo_posts():
    return [
        {
            "id": "demo-ig-1", "platform": "instagram",
            "title": "Bastidores: como nasce uma ideia de conteúdo",
            "url": "", "media_type": "Reel", "thumbnail": "",
            "published_at": "2026-09-25T14:00:00+00:00",
            "views": 4820, "reach": 3610, "likes": 312, "comments": 28,
            "shares": 46, "saves": 73, "clicks": 0,
            "metrics_available": True,
        },
        {
            "id": "demo-ig-2", "platform": "instagram",
            "title": "3 perguntas para destravar sua próxima publicação",
            "url": "", "media_type": "Carrossel", "thumbnail": "",
            "published_at": "2026-09-21T16:30:00+00:00",
            "views": 3270, "reach": 2490, "likes": 204, "comments": 19,
            "shares": 31, "saves": 96, "clicks": 0,
            "metrics_available": True,
        },
        {
            "id": "demo-ig-3", "platform": "instagram",
            "title": "Uma pequena mudança que melhorou nossa rotina",
            "url": "", "media_type": "Post", "thumbnail": "",
            "published_at": "2026-09-16T12:15:00+00:00",
            "views": 2160, "reach": 1780, "likes": 141, "comments": 34,
            "shares": 12, "saves": 22, "clicks": 0,
            "metrics_available": True,
        },
        {
            "id": "demo-li-1", "platform": "linkedin",
            "title": "O que aprendemos ao ouvir nossos clientes de perto",
            "url": "", "media_type": "Publicação", "thumbnail": "",
            "published_at": "2026-09-24T09:00:00+00:00",
            "views": 6840, "reach": 0, "likes": 186, "comments": 42,
            "shares": 29, "saves": 0, "clicks": 58,
            "metrics_available": True,
        },
        {
            "id": "demo-li-2", "platform": "linkedin",
            "title": "Checklist prático para planejar a semana com foco",
            "url": "", "media_type": "Publicação", "thumbnail": "",
            "published_at": "2026-09-19T11:45:00+00:00",
            "views": 5120, "reach": 0, "likes": 143, "comments": 17,
            "shares": 38, "saves": 0, "clicks": 91,
            "metrics_available": True,
        },
        {
            "id": "demo-li-3", "platform": "linkedin",
            "title": "Por que consistência vale mais que publicar todos os dias",
            "url": "", "media_type": "Publicação", "thumbnail": "",
            "published_at": "2026-09-12T10:20:00+00:00",
            "views": 3910, "reach": 0, "likes": 117, "comments": 31,
            "shares": 22, "saves": 0, "clicks": 44,
            "metrics_available": True,
        },
    ]


def load_demo_data():
    global POSTS, UPDATED_AT, PLATFORM_STATUS, DEMO_MODE
    posts = _demo_posts()
    calcular_scores_posts(posts)
    status = {
        platform: {
            "state": "demo",
            "message": "Exemplos fictícios para teste",
            "count": sum(post["platform"] == platform for post in posts),
        }
        for platform in ("instagram", "linkedin")
    }
    with LOCK:
        POSTS = posts
        UPDATED_AT = datetime.now(timezone.utc).isoformat()
        PLATFORM_STATUS = status
        DEMO_MODE = True
        AI_TIPS.clear()
    return get_dashboard_data()


def refresh_social_data():
    global POSTS, UPDATED_AT, PLATFORM_STATUS, DEMO_MODE
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

    DEMO_MODE = not any(credentials.values())
    if DEMO_MODE:
        collected = _demo_posts()
        status = {
            platform: {
                "state": "demo",
                "message": "Exemplos fictícios para teste",
                "count": sum(post["platform"] == platform for post in collected),
            }
            for platform in ("instagram", "linkedin")
        }
    else:
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
            except Exception:
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
        AI_TIPS.clear()
    return get_dashboard_data()


def analyze_social_post(post_id, platform):
    if not os.getenv("OPENAI_API_KEY"):
        raise AIConfigurationError

    with LOCK:
        post = next(
            (
                item for item in POSTS
                if item.get("id") == post_id and item.get("platform") == platform
            ),
            None,
        )
        if post is None:
            raise LookupError("Publicação não encontrada. Atualize os dados e tente novamente.")
        cache_key = (platform, post_id, json.dumps(post, sort_keys=True, ensure_ascii=False))
        cached_tip = AI_TIPS.get(cache_key)
    if cached_tip:
        return {"post_id": post_id, "platform": platform, "tip": cached_tip}

    tip = AIAnalyzer().analisar_post_social(post)
    with LOCK:
        AI_TIPS[cache_key] = tip
    return {"post_id": post_id, "platform": platform, "tip": tip}


def get_dashboard_data():
    with LOCK:
        posts = sorted(POSTS, key=lambda post: post.get("score", 0), reverse=True)
        return {
            "posts": posts,
            "updated_at": UPDATED_AT,
            "platforms": PLATFORM_STATUS,
            "configured": _credentials_status(),
            "demo": DEMO_MODE,
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
        path = urlparse(self.path).path
        if path == "/api/refresh":
            self._send_json(refresh_social_data())
            return
        if path != "/api/analyze":
            self._send_json({"error": "Endpoint não encontrado"}, 404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 8192:
                raise ValueError
            payload = json.loads(self.rfile.read(content_length))
            post_id = payload.get("post_id")
            platform = payload.get("platform")
            if not isinstance(post_id, str) or not isinstance(platform, str):
                raise ValueError
            result = analyze_social_post(post_id, platform)
        except AIConfigurationError:
            self._send_json({
                "error": "Configure OPENAI_API_KEY no .env para ativar as dicas da IA."
            }, 503)
        except LookupError as error:
            self._send_json({"error": str(error)}, 404)
        except (TypeError, ValueError, json.JSONDecodeError):
            self._send_json({"error": "Pedido de análise inválido."}, 400)
        except Exception:
            self._send_json({"error": "A IA não conseguiu analisar esta publicação agora."}, 502)
        else:
            self._send_json(result)

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
    load_demo_data()
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