import os.path

from unicorn.app import run_in_app_context
from unicorn.core.apps import current_app
from unicorn.core.pages import (generate_page, generate_page_inside_container,
                                generate_pages, unicorn_build_dir, write_page)
from unicorn.models import Franchise, Game, Season, Team
from unicorn.v2.team_ratings import TeamRatings


@run_in_app_context
def main():
    object_types = (
        ('franchise', Franchise),
        ('season', Season),
        ('team', Team),
        ('game', Game),
    )

    for obj_name, obj_class in object_types:
        all_objects = obj_class.get_all()

        generator = generate_pages(
            items=all_objects,
            template='{}.html'.format(obj_name),
            item_name=obj_name,
            page_key={
                'path': lambda obj, n=obj_name: '{}_{}.html'.format(n, obj.id),
            }
        )

        for page, content in generator:
            write_page(
                page.path,
                generate_page(
                    'components/container.html',
                    main_content=content,
                ),
            )

        write_page(
            '{}s_all.html'.format(obj_name),
            generate_page(
                'components/container.html',
                main_content=generate_page(
                    '{}s_all.html'.format(obj_name),
                    **{'{}s_all'.format(obj_name): all_objects}
                )
            )
        )

    # Style Sheet
    write_page('style.css', generate_page(
        'components/style.css.jinja',
        franchises=current_app.franchises.values(),
    ))

    # Home page
    write_page('index.html', generate_page_inside_container('home.html'))

    # Team Ratings

    # CSV file for Excel investigations
    columns = ['Time']
    columns.extend(f.name for f in current_app.franchises.values())

    # import csv
    # with open(os.path.join(unicorn_build_dir, 'team_ratings.csv'), 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(columns)
    #
    #     pr = TeamRatings()
    #     for game, current in pr.advance():
    #         row = [game.starts_at.strftime('%Y-%m-%d %H:%M:%S')]
    #         row.extend(current[f_id].int_value for f_id in current_app.franchises.keys())
    #         writer.writerow(row)

    # JSON file for charts on site
    team_ratings_for_json = []
    for f_id, f in current_app.franchises.items():
        team_ratings_for_json.append({
            'label': f.name,
            'data': [{'x': game.starts_at.strftime('%Y-%m-%d'), 'y': rating} for game, rating in current_app.team_ratings.change_log[f_id]],
            'type': 'line',
            'pointRadius': 1,
            'fill': False,
            'lineTension': 0,
            'borderWidth': 2,
            'borderColor': f.color2,
            'backgroundColor': f.color2,
            'pointBorderColor': f.color1,
        })
    import json
    with open(os.path.join(unicorn_build_dir, 'team_ratings.js'), 'w') as f:
        f.write('team_ratings = ')
        f.write(json.dumps(team_ratings_for_json, sort_keys=True, indent=4))
        f.write(';\n')

    # Actual HTML page
    write_page(
        'team_ratings.html',
        generate_page_inside_container(
            'team_ratings.html',
            team_ratings=current_app.team_ratings,
        )
    )


if __name__ == '__main__':
    main()
