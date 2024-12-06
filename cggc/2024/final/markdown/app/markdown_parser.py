import re
import html


class MarkdownParser:
    def __init__(self):
        self.rules = [
            # Headers
            (r"^# (.+)$", self._handle_h1),
            (r"^## (.+)$", self._handle_h2),
            (r"^### (.+)$", self._handle_h3),
            # Code Blocks
            (r"```(.*?)```", self._handle_code_block, re.DOTALL),
            # Images
            (r"!\[(.+?)\]\((.+?)\)", self._handle_image),
            # Links
            (r"\[(.+?)\]\((.+?)\)", self._handle_link),
            # Emphasis
            (r"\*\*(.+?)\*\*", self._handle_bold),
            (r"\*(.+?)\*", self._handle_italic),
        ]

    def parse(self, text):
        """parse markdown text to html"""
        text = html.escape(text)
        paragraphs = text.split("\n\n")
        parsed = []

        for p in paragraphs:
            if p.strip():
                parsed.append(self._parse_paragraph(p))

        return "\n".join(parsed)

    def _parse_paragraph(self, text):
        for pattern, handler in self.rules[:3]:
            match = re.match(pattern, text.strip())
            if match:
                inner_content = self._parse_inline(match.group(1))
                return handler(inner_content)

        parsed_content = self._parse_inline(text)
        return f"<p>{parsed_content}</p>"

    def _parse_inline(self, text):
        result = text
        prev_result = None

        while result != prev_result:
            prev_result = result
            for rule in self.rules[3:]:
                pattern = rule[0]
                handler = rule[1]
                flags = rule[2] if len(rule) > 2 else 0

                def replace(match):
                    groups = list(match.groups())
                    if handler != self._handle_code_block:
                        groups = [self._parse_inline(g) if g else g for g in groups]
                    return handler(groups)

                result = re.sub(pattern, replace, result, flags=flags)

        return result

    # handlers
    def _handle_h1(self, content):
        return f"<h1>{content}</h1>"

    def _handle_h2(self, content):
        return f"<h2>{content}</h2>"

    def _handle_h3(self, content):
        return f"<h3>{content}</h3>"

    def _handle_bold(self, groups):
        return f"<strong>{groups[0]}</strong>"

    def _handle_italic(self, groups):
        return f"<em>{groups[0]}</em>"

    def _handle_code_block(self, groups):
        code = groups[0].strip()
        return f"<pre><code>{code}</code></pre>"

    def _handle_image(self, groups):
        alt, src = groups
        return f'<img src="{src}" alt="{alt}">'

    def _handle_link(self, groups):
        text, url = groups
        return f'<a href="{url}">{text}</a>'


def parse_markdown(text):
    parser = MarkdownParser()
    return parser.parse(text)
