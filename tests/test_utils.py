import pytest
from utils import nl2br

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
