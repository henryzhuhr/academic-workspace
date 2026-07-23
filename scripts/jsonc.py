"""Small standard-library JSONC reader for workspace metadata.

JSONC is a superset of JSON. This reader accepts line comments, block
comments, and trailing commas while keeping strings untouched. Writers should
continue emitting strict JSON so files remain consumable by generic tools.
"""

import json
from pathlib import Path
from typing import Any, Optional


def _without_comments(text: str) -> str:
    output = []
    index = 0
    in_string = False
    escaped = False
    length = len(text)
    while index < length:
        character = text[index]
        if in_string:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue

        if character == '"':
            in_string = True
            output.append(character)
            index += 1
        elif character == "/" and index + 1 < length and text[index + 1] == "/":
            index += 2
            while index < length and text[index] not in "\r\n":
                index += 1
        elif character == "/" and index + 1 < length and text[index + 1] == "*":
            index += 2
            while index + 1 < length and not (
                text[index] == "*" and text[index + 1] == "/"
            ):
                if text[index] in "\r\n":
                    output.append(text[index])
                index += 1
            if index + 1 >= length:
                raise ValueError("未闭合的 JSONC 块注释")
            index += 2
        else:
            output.append(character)
            index += 1
    if in_string:
        raise ValueError("未闭合的 JSON 字符串")
    return "".join(output)


def _without_trailing_commas(text: str) -> str:
    output = []
    index = 0
    in_string = False
    escaped = False
    length = len(text)
    while index < length:
        character = text[index]
        if in_string:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue

        if character == '"':
            in_string = True
            output.append(character)
            index += 1
            continue
        if character == ",":
            lookahead = index + 1
            while lookahead < length and text[lookahead].isspace():
                lookahead += 1
            if lookahead < length and text[lookahead] in "]}":
                index += 1
                continue
        output.append(character)
        index += 1
    return "".join(output)


def loads(text: str, source: Optional[str] = None) -> Any:
    """Parse JSON or JSONC text using the standard ``json`` decoder."""

    cleaned = _without_trailing_commas(_without_comments(text))
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        location = " in {}".format(source) if source else ""
        raise ValueError("JSONC 无效{}：{}".format(location, exc)) from exc


def load(path: Path) -> Any:
    """Read and parse a UTF-8 JSON or JSONC file."""

    return loads(path.read_text(encoding="utf-8"), str(path))
