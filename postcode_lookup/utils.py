import typing
from datetime import date
from os import PathLike
from pathlib import Path

import babel
import dateparser
import jinja2
from babel.support import Translations
from jinja2 import ChainableUndefined
from jinja2.filters import do_mark_safe
from markupsafe import Markup, escape
from response_builder.v1.models.base import Ballot, CancellationReason
from starlette.datastructures import URL, Headers
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette_babel import get_locale
from starlette_babel import gettext_lazy as _


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
    if not value:
        return ""
    date_obj = value if isinstance(value, date) else dateparser.parse(value)
    format = "EEEE dd MMMM y"
    return babel.dates.format_datetime(date_obj, format, locale=get_locale())


def nl2br(value):
    return Markup("<br>\n".join([escape(line) for line in value.splitlines()]))


def translated_url(request: Request, name: str) -> URL:
    url = request.url_for(name, **request.scope["path_params"])
    if query_string := request.query_params:
        return url.include_query_params(**query_string)
    return url


def additional_ballot_link(request, ballot) -> str:
    url, label = None, None
    if any(
        part in ballot.ballot_paper_id
        for part in ("mayor.london", "gla.a", "gla.c")
    ):
        url = "https://www.londonelects.org.uk/im-voter"
        label = "London Elects"
    if "pcc." in ballot.ballot_paper_id:
        url = f"https://choosemypcc.org.uk/search/postcode?postcode={request.query_params.get('postcode-search', request.path_params.get('postcode'))}"
        label = "'Choose My PCC'"

    if not all((url, label)):
        return ""

    return do_mark_safe(
        f"""<p><a href="{url}" class="o-external-link">Find out more about this election at {label}</a></p>"""
    )


def apnumber(value):
    """
    For numbers 1-9, return the number spelled out. Otherwise, return the
    number. This follows Associated Press style.
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    if not 0 < value < 10:
        return value
    return (
        _("one"),
        _("two"),
        _("three"),
        _("four"),
        _("five"),
        _("six"),
        _("seven"),
        _("eight"),
        _("nine"),
    )[value - 1]


def pluralize(value, arg="s"):
    """
    Return a plural suffix if the value is not 1, '1', or an object of
    length 1. By default, use 's' as the suffix:

    * If value is 0, vote{{ value|pluralize }} display "votes".
    * If value is 1, vote{{ value|pluralize }} display "vote".
    * If value is 2, vote{{ value|pluralize }} display "votes".

    If an argument is provided, use that string instead:

    * If value is 0, class{{ value|pluralize:"es" }} display "classes".
    * If value is 1, class{{ value|pluralize:"es" }} display "class".
    * If value is 2, class{{ value|pluralize:"es" }} display "classes".

    If the provided argument contains a comma, use the text before the comma
    for the singular case and the text after the comma for the plural case:

    * If value is 0, cand{{ value|pluralize:"y,ies" }} display "candies".
    * If value is 1, cand{{ value|pluralize:"y,ies" }} display "candy".
    * If value is 2, cand{{ value|pluralize:"y,ies" }} display "candies".
    """
    if "," not in arg:
        arg = "," + arg
    bits = arg.split(",")
    if len(bits) > 2:
        return ""
    singular_suffix, plural_suffix = bits[:2]

    try:
        return singular_suffix if float(value) == 1 else plural_suffix
    except ValueError:  # Invalid string that's not a number.
        pass
    except TypeError:  # Value isn't a string or a number; maybe it's a list?
        try:
            return singular_suffix if len(value) == 1 else plural_suffix
        except TypeError:  # len() of unsized object.
            pass
    return ""


def ballot_cancellation_suffix(ballot: Ballot) -> str:
    # Used when a ballot is 'cancelled' and we want to label
    # it wit the right wording. This is normally 'postponed' but sometimes
    # 'cancelled' or some other text.
    if not ballot.cancelled:
        return ""
    if not ballot.cancellation_reason:
        # We don't really know what's going on here
        # so let's assume it's postponed.
        return _(" (postponed)")

    if is_postponed(ballot.cancellation_reason):
        return _(" (postponed)")

    if is_uncontested(ballot.cancellation_reason):
        return _(" (uncontested)")

    # If we've got here we don't really know what's going on. Return nothing
    # to be safe.
    return ""


def is_postponed(cancellation_reason: CancellationReason) -> bool:
    return cancellation_reason in [
        CancellationReason.NO_CANDIDATES,
        CancellationReason.CANDIDATE_DEATH,
        CancellationReason.UNDER_CONTESTED,
    ]


def is_uncontested(cancellation_reason: CancellationReason) -> bool:
    return cancellation_reason == CancellationReason.EQUAL_CANDIDATES


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
        env.filters["apnumber"] = apnumber
        env.filters["pluralize"] = pluralize
        env.filters["nl2br"] = nl2br
        env.policies["ext.i18n.trimmed"] = True
        env.globals["translated_url"] = translated_url
        env.globals["additional_ballot_link"] = additional_ballot_link
        env.filters["ballot_cancellation_suffix"] = ballot_cancellation_suffix

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
