from injector import Injector, inject
_injector = Injector()

import re


class StringUtils():
    def hex_pairs(self, s: str) -> list[str]:
        """Split a hex string into a list of 2-character byte strings: 'AABBCC' → ['AA', 'BB', 'CC'].
        PERF: replaces textwrap.wrap(s, 2) which invoked the full paragraph-wrap machinery on every call."""
        return [s[i:i+2] for i in range(0, len(s), 2)]

    def beautify_output(self, output):
        l = []
        m = 0
        for line in output.splitlines():
            s = line.split("//")
            m = max(m, len(s[0]))
            l.append(s)

        m = min(m, 27)
        l2 = []
        for line in l:
            if len(line) == 1:
                l2.append(line[0].strip())
            elif not line[0]:
                l2.append("// " + line[1].strip())
            else:
                l2.append(line[0].strip().ljust(m) + "// " + line[1].strip())

        r = '\n'.join(l2)

        r = re.sub("\n([0-9a-fA-F]{6})", r"\n\n\1", r)

        return r
    
    
string_utils = _injector.get(StringUtils)