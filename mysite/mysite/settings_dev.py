DEBUG = True
ALLOWED_HOSTS = []


DJANGO_LOG_LEVEL=DEBUG
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'debugfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'infofile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'info.log',
            'formatter': 'simple',
        },
        'warningfile': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'warning.log',
            'formatter': 'simple',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['debugfile','infofile','warningfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.core.mail': {
            'handlers': ['debugfile','infofile','warningfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'pfx': {
            'handlers': ['debugfile','infofile','warningfile','console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'csvimport': {
            'handlers': ['debugfile','infofile','warningfile','console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'py': {
            'handlers': ['debugfile','infofile','warningfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },

    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
}
