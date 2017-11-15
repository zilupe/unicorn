from unicorn.app import run_in_app_context
from unicorn.core.pages import generate_pages, write_page, generate_page
from unicorn.models import Season


def main():
    seasons = Season.get_all()
    generator = generate_pages(
        seasons,
        'season.html',
        item_name='season',
        page_key={
            'name': lambda s: s.name,
            'path': lambda s: 'season_{}.html'.format(s.id),
        },
    )

    pages = []
    for page, content in generator:
        pages.append(page)
        write_page(page.path, content)

    write_page('seasons_all.html', generate_page('seasons_all.html', pages=pages))


if __name__ == '__main__':
    run_in_app_context(main)
