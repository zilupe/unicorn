import datetime as dt
import logging
import os.path
from urllib.parse import parse_qs

from bs4 import BeautifulSoup


log = logging.getLogger(__name__)

source_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'season-pages'))


def parse_team_link(team_link):
    qs = parse_qs(team_link['href'])
    return {
        'id': qs['TeamId'][0],
        'name': ' '.join(w for w in team_link.text.strip().replace('\n', ' ').split(' ') if w),
    }


def parse_season(season_page_path):
    with open(full_source_path) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    title_parts = soup.title.text.strip().split(' - ')
    assert title_parts[0] == 'Basketball'
    assert title_parts[1] == 'Mixed (Angel (City)'
    assert title_parts[2] == 'Thurs'
    assert title_parts[3] == 'Rec)'
    assert title_parts[5] == 'Current Standings'
    season_title = title_parts[4]

    fixtures = []

    standings_table = soup.find('table', class_='STTable')
    for fixtures_table in soup.find_all('table', class_='SpawtzFixtureList'):
        fixture_date = dt.datetime.strptime(
            fixtures_table.find('td', class_='SpawtzDate').text.strip(),
            '%A %d %B %Y',
        )

        fixture_datetime = None
        home_team = None
        away_team = None

        for row in fixtures_table.find_all('tr'):
            if not row.attrs:
                continue

            if 'SpawtzSpaceTime' in row.attrs['class']:
                fixture_time = dt.datetime.strptime(
                    row.find('td').text.strip().split(' ', 1)[0],
                    '%H:%M',
                )
                fixture_datetime = fixture_date.replace(
                    hour=fixture_time.hour,
                    minute=fixture_time.minute,
                )

            else:
                home_team_cell = row.find('td', class_='SpawtzHomeTeam')
                away_team_cell = row.find('td', class_='SpawtzAwayTeam')
                if home_team_cell:
                    home_team = parse_team_link(home_team_cell.find('a'))
                    home_team['score'] = row.find('td', class_='SpawtzHomeTeamScore').text.strip()

                elif away_team_cell:
                    away_team = parse_team_link(away_team_cell.find('a'))
                    away_team['score'] = row.find('td', class_='SpawtzAwayTeamScore').text.strip()
                else:
                    if row.find('td', class_='SpawtzSplitter'):
                        fixtures.append(
                            (fixture_datetime, home_team, away_team)
                        )
                        continue
                    log.warning('Unrecognised row: {}'.format(row))

    return {
        'title': season_title,
        'fixtures': fixtures,
    }


for source_filename in os.listdir(source_dir):
    full_source_path = os.path.join(source_dir, source_filename)
    print(parse_season(full_source_path))

