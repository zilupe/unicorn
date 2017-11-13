import logging.config


LOGGING = {
    'version': 1,
    'formatters': {
        'console': {
            'format': (
                '[%(asctime)s][%(levelname)s] %(name)s '
                '%(filename)s:%(funcName)s:%(lineno)d | %(message)s'
            ),
            'datefmt': '%H:%M:%S',
        },
        'simple': {
            'format': '%(asctime)s  [%(levelname)s] - %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'unicorn': {
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

logging.config.dictConfig(LOGGING)
