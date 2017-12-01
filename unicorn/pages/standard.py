import os.path

from unicorn.app import run_in_app_context
from unicorn.core.apps import current_app
from unicorn.core.pages import generate_pages, write_page, generate_page, generate_page_inside_container, \
    unicorn_build_dir
from unicorn.models import Season, Team, Game, Franchise
from unicorn.v2.power_rankings import PowerRankings


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

    # Power Rankings

    # CSV file for Excel investigations
    columns = ['Time']
    columns.extend(f.name for f in current_app.franchises.values())

    # import csv
    # with open(os.path.join(unicorn_build_dir, 'power_rankings.csv'), 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(columns)
    #
    #     pr = PowerRankings()
    #     for game, current in pr.advance():
    #         row = [game.starts_at.strftime('%Y-%m-%d %H:%M:%S')]
    #         row.extend(current[f_id].int_value for f_id in current_app.franchises.keys())
    #         writer.writerow(row)

    # JSON file for charts on site
    power_rankings_for_json = []
    for f_id, f in current_app.franchises.items():
        power_rankings_for_json.append({
            'label': f.name,
            'data': [{'x': game.starts_at.strftime('%Y-%m-%d'), 'y': rating} for game, rating in current_app.power_rankings.change_log[f_id]],
            'type': 'line',
            'pointRadius': 1,
            'fill': False,
            'lineTension': 0,
            'borderWidth': 1,
            'borderColor': f.color2,
            'backgroundColor': f.color2,
            'pointBorderColor': f.color1,
        })
    import json
    with open(os.path.join(unicorn_build_dir, 'power_rankings.js'), 'w') as f:
        f.write('power_rankings = ')
        f.write(json.dumps(power_rankings_for_json, sort_keys=True, indent=4))
        f.write(';\n')

    # Actual HTML page
    write_page(
        'power_rankings.html',
        generate_page_inside_container(
            'power_rankings.html',
            power_rankings=current_app.power_rankings,
        )
    )


if __name__ == '__main__':
    main()
