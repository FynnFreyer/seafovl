"""
Set default options for code elements via the ``code-format`` metadata option.

Highlight unmarked code blocks with a default language,
specified via string in ``code-format.lang``.

Do automatic line numbering by setting ``code-format.number-lines`` to true.
Anchor lines by setting ``code-format.line-anchors`` to true.

Mark blocks that should not be highlighted with ``bare``.

MIT License

Copyright (c) 2024 Fynn Freyer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from functools import cache
from subprocess import run, CalledProcessError
from typing import Any

from panflute import run_filter, Doc, Element, Code, CodeBlock


@cache
def get_defined_langs() -> frozenset[str] | None:
    """Get set of langs that pandoc supports for syntax highlighting."""
    try:
        
        # ask pandoc what languages it can highlight
        proc = run(["pandoc", "--list-highlight-languages"], check=True, capture_output=True, text=True)
        output = proc.stdout.strip()

        # for code marked bare no highlighting should place,
        # so we add "bare" to the defined languages
        langs = ["bare", *output.splitlines()]

        return frozenset(langs)
    except CalledProcessError:
        return None


def is_code(elem: Element) -> bool:
    """Check if an element is of type ``Code`` or ``CodeBlock``."""
    return isinstance(elem, CodeBlock) or isinstance(elem, Code)


def get_meta(doc: Doc | NameError, key: str, default = None) -> Any | None:
    """Wrapper around ``doc.get_metadata``, in case no document is available."""
    if doc is None:
        return default
    return doc.get_metadata(key, default)


def add_lang(code: Code | CodeBlock, doc: Doc | None = None) -> None:
    """
    Add a language attribute to a code element,
    if a default is defined and the element doesn't have one set already.
    """
    lang = get_meta(doc, 'code-format.lang')
    # don't act if no default language is set
    if lang is None:
        return

    langs = get_defined_langs()
    has_lang = any([klass in langs for klass in code.classes])
    if has_lang:
        return  # if code element already has a language, we bail

    code.classes.append(lang)


def add_numbers(code: Code | CodeBlock, doc: Doc | None = None) -> None:
    """Add the ``number-lines`` class to code blocks, if the option is set."""
    number_lines = get_meta(doc, 'code-format.numbering', False)
    if number_lines:
        code.classes.append("number-lines")


def add_anchors(code: Code | CodeBlock, doc: Doc | None = None) -> None:
    """Add the ``line-anchors`` class to code blocks, if the option is set."""
    number_lines = get_meta(doc, 'code-format.anchors', False)
    if number_lines:
        code.classes.append("line-anchors")


def action(elem: Element, doc: Doc | None = None):
    if is_code(elem):
        add_lang(elem, doc)
        add_numbers(elem, doc)


if __name__ == "__main__":
    run_filter(action)
