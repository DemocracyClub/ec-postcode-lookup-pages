import typing
from os import PathLike
from pathlib import Path

import babel
import dateparser
import jinja2
from babel.support import Translations
from jinja2 import ChainableUndefined
from starlette.datastructures import URL, Headers
from starlette.requests import Request
from starlette.templating import Jinja2Templates


def is_welsh(path: str) -> bool:
    """
    Returns True if the URL should be in welsh
    """
    return path.lstrip("/").startswith("cy")


def get_loader(request: Request) -> Jinja2Templates:
    if is_welsh(request.url.path):
        return cy_templates
    return en_templates


def date_format(value):
    date_obj = dateparser.parse(value)
    format = "EEEE dd MMMM y"
    return babel.dates.format_datetime(date_obj, format)


def translated_url(request: Request, name: str) -> URL:
    url = request.url_for(name, **request.scope["path_params"])
    if query_string := request.query_params:
        return url.include_query_params(**query_string)
    return url


class _i18nJinja2Templates(Jinja2Templates):
    locale = None

    def _create_env(
        self, directory: typing.Union[str, PathLike], **env_options: typing.Any
    ) -> jinja2.Environment:
        env_options["extensions"] = [
            "jinja2.ext.i18n",
        ]
        env_options["undefined"] = ChainableUndefined
        env = super()._create_env(directory, **env_options)
        env.filters["date_filter"] = date_format
        env.policies["ext.i18n.trimmed"] = True
        env.globals["translated_url"] = translated_url

        locale_dir = Path(__file__).parent / "locale"
        list_of_desired_locales = [self.locale]

        translations = Translations.load(locale_dir, list_of_desired_locales)

        env.install_gettext_translations(translations)

        return env


class en_i18nJinja2Templates(_i18nJinja2Templates):
    locale = "en"


class cy_i18nJinja2Templates(_i18nJinja2Templates):
    locale = "cy"


root = Path(__file__).parent
en_templates = en_i18nJinja2Templates(directory=root / "templates")
cy_templates = cy_i18nJinja2Templates(directory=root / "templates")


class i18nMiddleware:
    def __init__(
        self,
        app,
    ):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        if "path" in scope:
            if is_welsh(scope["path"]):
                scope["base_template"] = "base_cy.html"
                scope["current_language"] = "cy"
            else:
                scope["base_template"] = "base.html"
                scope["current_language"] = "en"

        return await self.app(scope, receive, send)


class ForwardedForMiddleware:
    def __init__(
        self,
        app,
    ):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            forwarded_for = (
                headers.get("x-forwarded-host", "").split(":")[0].encode()
            )
            if forwarded_for:
                for i, header in enumerate(scope["headers"]):
                    if header[0] == b"host":
                        scope["headers"].pop(i)
                scope["headers"].append((b"host", forwarded_for))
        await self.app(scope, receive, send)
