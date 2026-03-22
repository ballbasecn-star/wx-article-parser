"""
FastAPI应用入口
"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routes import router

# 路径配置
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# 创建FastAPI应用
app = FastAPI(
    title="wx-article-parser",
    description="微信公众号文章解析服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 模板配置
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 注册API路由
app.include_router(router)


@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root(request: Request):
    """首页 - 前端页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/parse", response_class=HTMLResponse, tags=["root"])
async def parse_page(request: Request):
    """解析页面 - 支持URL参数"""
    return templates.TemplateResponse("index.html", {"request": request})