from types import SimpleNamespace

import pytest
from utils import candidates_groupby_party_list, nl2br

nl2br_testcases = [
    ["abc", "abc"],
    ["abc\ndef", "abc<br>\ndef"],
    ["abc\r\ndef", "abc<br>\ndef"],
    ["abc\n\ndef", "abc<br>\n<br>\ndef"],
    [
        '<script>alert("xss")</script>',
        "&lt;script&gt;alert(&#34;xss&#34;)&lt;/script&gt;",
    ],
]


@pytest.mark.parametrize("testcase", nl2br_testcases)
def test_nl2br(testcase):
    input_, expected = testcase
    assert nl2br(input_) == expected


def make_candidate(name, party):
    return SimpleNamespace(
        person=SimpleNamespace(name=name),
        party=SimpleNamespace(party_name=party),
    )


def test_candidates_groupby_party_list():
    candidates = [
        make_candidate("Bob", "Conservative Party"),
        make_candidate("Al", "Labour Party"),
        make_candidate("Zoe", "Independent"),
        make_candidate("Amy", "Independent"),
        make_candidate("Ben", "Conservative Party"),
    ]

    result = candidates_groupby_party_list(candidates)

    expected = (
        '<ol class="candidate-list">'
        "<li>Conservative Party (2 candidates)</li>"
        "<li>Labour Party (1 candidate)</li>"
        "<li>Independent: Amy</li>"
        "<li>Independent: Zoe</li>"
        "</ol>"
    )

    assert str(result) == expected


def test_candidates_groupby_party_list_xss():
    candidates = [
        make_candidate("Bob", '<script>alert("xss")</script>'),
    ]

    result = candidates_groupby_party_list(candidates)

    expected = (
        '<ol class="candidate-list">'
        "<li>&lt;script&gt;alert(&#34;xss&#34;)&lt;/script&gt; (1 candidate)</li>"
        "</ol>"
    )

    assert str(result) == expected
