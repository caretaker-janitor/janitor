import pytest

from janitor.site.ansi import ansi_to_html


@pytest.mark.parametrize(
    "line,html",
    [
        ("", ""),
        ("a <b> & c\n", "a &lt;b&gt; &amp; c"),
        (
            "\x1b[1;38;2;255;165;0mTo fix, try:\x1b[0m\n",
            '<span style="font-weight: bold; color: #ffa500">To fix, try:</span>',
        ),
        ("\x1b[1mb\x1b[22mn", '<span style="font-weight: bold">b</span>n'),
        ("\x1b[31mr\x1b[39mn", '<span style="color: #cd0000">r</span>n'),
        ("\x1b[92mg\x1b[mn", '<span style="color: #00ff00">g</span>n'),
        ("\x1b[44mb\x1b[49mn", '<span style="background-color: #0000ee">b</span>n'),
        ("\x1b[101mr", '<span style="background-color: #ff0000">r</span>'),
        ("\x1b[38;5;3my", '<span style="color: #cdcd00">y</span>'),
        ("\x1b[38;5;12mb", '<span style="color: #5c5cff">b</span>'),
        ("\x1b[38;5;208mo", '<span style="color: #ff8700">o</span>'),
        ("\x1b[48;5;244mg", '<span style="background-color: #808080">g</span>'),
        ("\x1b[48;2;1;2;3mk", '<span style="background-color: #010203">k</span>'),
        ("\x1b[5mblink", "blink"),
        ("\x1b[38;5mx", "x"),
        ("\x1b[38;5;256mx", "x"),
        ("\x1b[38;2;1;2mx", "x"),
        ("\x1b[38;2;300;0;0mx", "x"),
        ("\x1b[38;9;31mx", "x"),
        ("\x1b[38:2::255:0:0mx", "x"),
        ("\x1b[2Kdone\x1b[?25l\x1b(B", "done"),
        ("\x1b]8;;https://example.com/\x07link\x1b]8;;\x1b\\", "link"),
    ],
)
def test_ansi_to_html(line, html):
    assert ansi_to_html([line]) == [html]


def test_ansi_to_html_carries_style_to_next_line():
    assert ansi_to_html(["\x1b[3;4mstart\n", "still\x1b[23;24m end\n"]) == [
        '<span style="font-style: italic; text-decoration: underline">start</span>',
        '<span style="font-style: italic; text-decoration: underline">still</span> end',
    ]


def test_ansi_to_html_no_lines():
    assert ansi_to_html([]) == []
