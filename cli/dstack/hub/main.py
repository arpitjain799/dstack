import os
import time

import pkg_resources
from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from dstack.hub.background import start_background_tasks
from dstack.hub.db.migrate import migrate
from dstack.hub.db.models import User
from dstack.hub.repository.users import UserManager
from dstack.hub.routers import (
    artifacts,
    backends,
    jobs,
    link,
    logs,
    projects,
    repos,
    runners,
    runs,
    secrets,
    storage,
    tags,
    users,
    workflows,
)
from dstack.hub.utils import logging

logging.configure_root_logger()
logger = logging.get_logger(__name__)


app = FastAPI(docs_url="/api/docs")
app.include_router(users.router)
app.include_router(backends.router)
app.include_router(projects.router)
app.include_router(runs.router)
app.include_router(jobs.router)
app.include_router(runners.router)
app.include_router(secrets.router)
app.include_router(logs.router)
app.include_router(artifacts.router)
app.include_router(storage.router)
app.include_router(tags.router)
app.include_router(repos.router)
app.include_router(link.router)
app.include_router(workflows.router)


@app.on_event("startup")
async def startup_event():
    await migrate()
    admin_user = await update_admin_user()
    start_background_tasks()
    url = f"http://{os.getenv('DSTACK_HUB_HOST')}:{os.getenv('DSTACK_HUB_PORT')}?token={admin_user.token}"
    print(f"The hub is available at {url}")


@app.middleware("http")
async def app_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    path = request.url.path
    request_dict = {"method": request.method, "path": path}
    if path.startswith("/api/"):
        logger.info(
            {
                "request": request_dict,
                "process_time": process_time,
            }
        )
    return response


async def update_admin_user() -> User:
    admin_user = await UserManager.get_user_by_name("admin")
    if admin_user is None:
        admin_user = await UserManager.create_admin()
    elif os.getenv("DSTACK_HUB_ADMIN_TOKEN") is not None and admin_user.token != os.getenv(
        "DSTACK_HUB_ADMIN_TOKEN"
    ):
        admin_user.token = os.getenv("DSTACK_HUB_ADMIN_TOKEN")
        await UserManager.save(admin_user)
    return admin_user


app.mount("/", StaticFiles(packages=["dstack.hub"], html=True), name="static")


# noinspection PyUnusedLocal
@app.exception_handler(404)
async def custom_http_exception_handler(request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": exc.detail}, status_code=404)
    else:
        return HTMLResponse(pkg_resources.resource_string(__name__, "statics/index.html"))
