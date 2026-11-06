# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

"""Parsing a json formatted dictionary."""

try:
    import simplejson as json
except ImportError:
    import json

from plover.dictionary.helpers import StenoNormalizer
from plover.steno_dictionary import StenoDictionary
from plover.steno import steno_to_sort_key


class JsonDictionary(StenoDictionary):
    def _parse(self, contents):
        return json.loads(contents)

    def _load(self, filename):
        with open(filename, "rb") as fp:
            contents = fp.read()
        for encoding in ("utf-8", "latin-1"):
            try:
                contents = contents.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                break
        else:
            raise ValueError("'%s' encoding could not be determined" % (filename,))
        d = dict(self._parse(contents))
        with StenoNormalizer(filename) as normalize_steno:
            self.update((normalize_steno(x[0]), x[1]) for x in d.items())

    def _save(self, filename):
        mappings = [("/".join(k), v) for k, v in self.items()]
        mappings.sort(key=lambda i: steno_to_sort_key(i[0], strict=False))
        with open(filename, "w", encoding="utf-8", newline="\n") as fp:
            json.dump(
                dict(mappings), fp, ensure_ascii=False, indent=0, separators=(",", ": ")
            )
            fp.write("\n")


def _strip_jsonc(contents, comments=None):
    """Remove JSONC comments and trailing commas outside strings."""
    result = []
    i = 0
    in_string = False
    escaped = False
    while i < len(contents):
        char = contents[i]
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
        elif char == '"':
            in_string = True
            result.append(char)
            i += 1
        elif char == "/" and i + 1 < len(contents) and contents[i + 1] == "/":
            start = i
            while i < len(contents) and contents[i] not in "\r\n":
                result.append(" ")
                i += 1
            if comments is not None:
                comments.append(contents[start:i])
        elif char == "/" and i + 1 < len(contents) and contents[i + 1] == "*":
            start = i
            result.extend("  ")
            i += 2
            while i < len(contents) and contents[i : i + 2] != "*/":
                result.append(contents[i] if contents[i] in "\r\n" else " ")
                i += 1
            if i == len(contents):
                raise ValueError("unterminated JSONC block comment")
            result.extend("  ")
            i += 2
            if comments is not None:
                comments.append(contents[start:i])
        else:
            result.append(char)
            i += 1

    contents = "".join(result)
    result = []
    in_string = False
    escaped = False
    i = 0
    while i < len(contents):
        char = contents[i]
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
        elif char == '"':
            in_string = True
            result.append(char)
            i += 1
        elif char == ",":
            next_char = i + 1
            while next_char < len(contents) and contents[next_char].isspace():
                next_char += 1
            if next_char == len(contents) or contents[next_char] not in "}]":
                result.append(char)
            i += 1
        else:
            result.append(char)
            i += 1
    return "".join(result)


class JsoncDictionary(JsonDictionary):
    def __init__(self):
        super().__init__()
        self._comments = []

    def _parse(self, contents):
        self._comments = []
        return json.loads(_strip_jsonc(contents, self._comments))

    def _save(self, filename):
        mappings = [("/".join(k), v) for k, v in self.items()]
        mappings.sort(key=lambda i: steno_to_sort_key(i[0], strict=False))
        with open(filename, "w", encoding="utf-8", newline="\n") as fp:
            if self._comments:
                fp.write("\n".join(self._comments))
                fp.write("\n")
            json.dump(
                dict(mappings), fp, ensure_ascii=False, indent=0, separators=(",", ": ")
            )
            fp.write("\n")
