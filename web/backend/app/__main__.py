"""
AI教师Agent Web后端 - 启动入口
"""

if __name__ == "__main__":
    import sys
    import os

    # 添加项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 禁用 uvicorn 的自动重载
    os.environ["UVICORN_RELOAD"] = "true"

    # 直接导入 app
    import uvicorn
    from app.main import app as fastapi_app

    # 运行

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8100,
        reload=True,  # 关闭 reload 以避免多进程问题
        log_level="info",
        access_log=True,
    )
