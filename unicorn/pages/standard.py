from unicorn.app import run_in_app_context
from unicorn.core.pages import generate_pages, write_page, generate_page
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

        pages = []
        for page, content in generator:
            pages.append(page)
            write_page(page.path, content)

        write_page(
            '{}s_all.html'.format(obj_name),
            generate_page(
                '{}s_all.html'.format(obj_name),
                pages=pages,
                **{'{}s_all'.format(obj_name): all_objects}
            )
        )


if __name__ == '__main__':
    main()
