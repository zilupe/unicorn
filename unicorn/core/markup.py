import re

import markdown2

from unicorn.core.apps import current_app


def generate_franchise_link(match):
    franchise_id = int(match.group(1))
    return current_app.franchises[franchise_id].simple_link


def generate_team_link(match):
    team_id = match.group(1)
    team = current_app.teams[team_id]
    return '<a href="{}">{}<sup>{}</sup></a>'.format(
        team.simple_url,
        team.name,
        team.season.short_name,
    )


link_patterns = [
    (re.compile(r'\[F:(\d+)\]'), generate_franchise_link),
    (re.compile(r'\[T:(\d+\.\d+)\]'), generate_team_link),
]


def _process_links(text):
    # Used markdown2.py _do_link_patterns code as main source,
    # but allow replacing the link label too.
    for regex, repl in link_patterns:
        replacements = []
        for match in regex.finditer(text):
            replacements.append((match.span(), repl(match)))
        for (start, end), link in reversed(replacements):
            text = text[:start] + link + text[end:]
    return text


def process(text):
    return markdown2.markdown(_process_links(text))
