from jinja2 import Environment, PackageLoader, select_autoescape

import unicorn.db.connection
from unicorn.models import Season


env = Environment(
    loader=PackageLoader('unicorn', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


template = env.get_template('season.html')

for season in Season.get_all():
    print(template.render(season=season))
