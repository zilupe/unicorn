from unicorn.app import run_in_app_context
from unicorn.core.apps import current_app
from unicorn.core.pages import generate_pages, write_page, generate_page, generate_page_inside_container
from unicorn.models import Season, Team, Game, Franchise


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
    write_page(
        'power_rankings.html',
        generate_page_inside_container(
            'power_rankings.html',
            power_rankings=current_app.power_rankings,
        )
    )


if __name__ == '__main__':
    main()
