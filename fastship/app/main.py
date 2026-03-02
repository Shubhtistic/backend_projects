from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from fastapi.responses import HTMLResponse

from contextlib import asynccontextmanager
from app.api_routes import shipment, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="FastSHIP API", lifespan=lifespan)
app.include_router(shipment.router, tags=["Shipments"])
app.include_router(auth.router, tags=["auth"])


@app.get("/scalar")
def scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Fastship")


@app.get("/", response_class=HTMLResponse)
async def main():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastShip - Backend Learning Project</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0a0a0a;
            --bg-secondary: #111111;
            --card-bg: rgba(26, 26, 26, 0.6);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --border-color: rgba(255, 255, 255, 0.1);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            position: relative;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.12) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.08) 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 640px;
            width: 100%;
            animation: fadeInUp 0.8s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 3.5rem 3rem;
            box-shadow: 
                0 20px 50px rgba(0, 0, 0, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.05) inset;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 
                0 24px 60px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.08) inset;
        }

        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
        }

        .subtitle {
            font-size: 1.125rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            font-weight: 400;
            line-height: 1.6;
        }

        .description {
            font-size: 1rem;
            color: var(--text-secondary);
            line-height: 1.8;
            margin-bottom: 3rem;
            max-width: 540px;
        }

        .section-title {
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-secondary);
            margin-bottom: 1.25rem;
        }

        .links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .link-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.875rem 2rem;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            color: var(--accent-hover);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9375rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .link-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(59, 130, 246, 0.2), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .link-button:hover::before {
            opacity: 1;
        }

        .link-button:hover {
            background: rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.5);
            color: var(--text-primary);
            transform: translateY(-2px);
            box-shadow: 
                0 8px 24px rgba(59, 130, 246, 0.2),
                0 0 0 1px rgba(59, 130, 246, 0.1) inset;
        }

        .link-button:active {
            transform: translateY(0);
        }

        @media (max-width: 640px) {
            body {
                padding: 1.5rem;
            }

            .card {
                padding: 2.5rem 2rem;
                border-radius: 20px;
            }

            h1 {
                font-size: 2.5rem;
            }

            .subtitle {
                font-size: 1rem;
            }

            .description {
                font-size: 0.9375rem;
            }

            .links {
                flex-direction: column;
            }

            .link-button {
                width: 100%;
            }
        }

        @media (max-width: 480px) {
            h1 {
                font-size: 2rem;
            }

            .card {
                padding: 2rem 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>FastShip</h1>
            <p class="subtitle">A backend learning project built by Shubham Pawar</p>
            <p class="description">
                A hands-on exploration of backend engineering principles, focusing on building robust APIs, 
                managing databases, implementing authentication systems, and deploying scalable cloud infrastructure. 
                This project serves as a practical foundation for understanding server-side architecture and modern 
                development workflows.
            </p>
            <div class="connect-section">
                <h2 class="section-title">Connect</h2>
                <div class="links">
                    <a href="https://github.com/Shubhtistic/backend_projects" class="link-button" target="_blank" rel="noopener noreferrer">GitHub</a>
                    <a href="https://www.linkedin.com/in/shubhtistic/" class="link-button" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
