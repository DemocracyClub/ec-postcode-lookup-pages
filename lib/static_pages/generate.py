import os
from contextlib import contextmanager
from multiprocessing import Process
from pathlib import Path
from random import randrange
from urllib.parse import urljoin

import httpx
import uvicorn


@contextmanager
def uvicorn_context():
    cwd = os.path.abspath(".")

    port = randrange(8010, 8100)
    proc = Process(
        target=uvicorn.run,
        args=("postcode_lookup.app:app",),
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "workers": 1,
            "access_log": False,
            "log_level": "critical",
            "app_dir": cwd,
        },
    )
    try:
        proc.start()
        import time

        time.sleep(1)
        yield f"http://localhost:{port}"
    finally:
        proc.kill()


STATIC_URLS = [
    "/i-am-a/voter/your-election-information",
    "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
]

root_path = Path(__file__).parent.absolute() / "build/"

host = os.environ.get("FQDN", "www.electoralcommission.org.uk")
request_headers = {
    "HOST": host,
    "X-Forwarded-Host": os.environ.get("X_FORWARDED_HOST", host),
    "X-Forwarded-Proto": "https",
}

with uvicorn_context() as root_url:
    for page in STATIC_URLS:
        url = urljoin(root_url, page)
        path = root_path / page.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            content = httpx.get(url, headers=request_headers).text
            content = content + """<!-- Static page content -->"""
            file.write(content)
