"""
This code is extracted from the entangled-filters project and has been lightly
modified. The original source code and license can be found at
https://github.com/entangled/filters/

Copyright 2019 Johannes Hidding and contributors.
"""

from collections import defaultdict
from pathlib import Path
from typing import Optional


from panflute import (
    Span,
    Str,
    Para,
    Code,
    CodeBlock,
    Div,
    SmallCaps,
    Doc,
    run_filter,
    RawInline,
    RawBlock,
    Space,
)


def get_name(elem) -> Optional[str]:
    if elem.identifier:
        return elem.identifier

    if "file" in elem.attributes:
        return elem.attributes["file"]

    return None


def prepare(doc):
    doc.code_count = defaultdict(lambda: 0)


# TODO: prevent breaks between headings and blocks
# nopagebreak[arg] discourages page breaks, arg is a priority in [1-4]
# we could use this to avoid seperation of headings and blocks
# nobreak = RawBlock(r"\nopagebreak[4]", "tex")


def action(elem, doc):
    if isinstance(elem, CodeBlock):
        name = get_name(elem)
        if name is None:
            return
        
        prefix = SmallCaps(Str("Block-ID:"))

        q_open = Code("«")
        q_close = Code("»")

        is_path = Path(name).exists()

        id_string = Code(name) if is_path else Str(name)
        Span(id_string)
        
        label_parts = [prefix, Space, q_open, id_string, q_close]

        count = doc.code_count[name] + 1
        if count > 1:
            label_parts.extend([Space, Str(f"[{count}]")])
        doc.code_count[name] += 1

        # hfill moves the header to the right edge of the page
        fill = RawInline(r"\hfill", "tex")
        label = Para(fill, Span(*label_parts))
        annotated_block = Div(label, elem, classes=["annotated-code"])

        return annotated_block


if __name__ == "__main__":
    run_filter(action, prepare=prepare)
