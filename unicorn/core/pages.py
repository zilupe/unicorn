import datetime as dt
import os.path

from jinja2 import Environment, PackageLoader, select_autoescape

from unicorn import unicorn_root_dir
from unicorn.core import markup
from unicorn.core.apps import current_app

env = Environment(
    loader=PackageLoader('unicorn', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


unicorn_build_dir = os.path.join(unicorn_root_dir, 'build')

identity_func = lambda x: x

stories_dir = os.path.join(unicorn_root_dir, 'unicorn/data')


class _AttrDict(dict):
    def __getattr__(self, item):
        return self[item]


def generate_dict_from_dict_of_lambdas(context, dict_of_lambdas):
    if not dict_of_lambdas:
        return None
    return dict(
        (k, v(context) if callable(v) else v)
        for k, v in dict_of_lambdas.items()
    )


def generate_pages(
        items, template, *,
        item_name=None,
        item_context_extras=None,
        page_key=identity_func,
        **context_extras
    ):
    """
    :param items:
    :param template:
    :param item_context_extras:
        dictionary of lambdas to calculate for each item and add to the item context
    :param item_name:
        the name used to refer to item in template i.e. "season" if in template "season.name" is used.
        Required when item is not a dictionary.
    :param page_key:
        a function or a dictionary of functions to calculate for each item and yield as page key
        instead of item.
    :param context_extras:
        additional context to pass to all templates
    """

    template_obj = env.get_template(template)

    for item in items:
        template_context = {}

        if context_extras:
            template_context.update(context_extras)

        if item_context_extras:
            template_context.update(generate_dict_from_dict_of_lambdas(item, item_context_extras))

        if item_name:
            template_context[item_name] = item
        else:
            template_context.update(item)

        # Check if a custom story exists for the item
        for story_type in ('alert', 'history', 'report'):
            story_text = None
            story_filename = os.path.join(
                stories_dir,
                '{}_story/{}_{}.md'.format(story_type, item_name, item.id),
            )
            if os.path.isfile(story_filename):
                with open(story_filename) as f:
                    story_text = markup.process(f.read())
            template_context['{}_story'.format(story_type)] = story_text

        if callable(page_key):
            output_key = page_key(item)
        else:
            output_key = _AttrDict((k, v(item)) for k, v in page_key.items())

        yield output_key, template_obj.render(**template_context)


def generate_page(template, **context_extras):
    template_obj = env.get_template(template)
    context_extras['generation_time'] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    return template_obj.render(app=current_app, **context_extras)


def generate_page_inside_container(template, **context_extras):
    template_obj = env.get_template(template)
    container_template = env.get_template('components/container.html')
    return container_template.render(
        app=current_app,
        main_content=template_obj.render(app=current_app, **context_extras)
    )


def write_page(path, content):
    full_path = os.path.join(unicorn_build_dir, path)
    with open(full_path, 'w') as f:
        f.write(content)
