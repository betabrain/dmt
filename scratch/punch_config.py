__config_version__ = 1

GLOBALS = {
    'serializer': '{{year}}.{{month}}.{{day}}.{{build}}',
}

FILES = []

VERSION = ['year', 'month', 'day', 'build']

VERSION = [
    {
        'name': 'year',
        'type': 'date',
        'fmt': '%Y',
    },
    {
        'name': 'month',
        'type': 'date',
        'fmt': '%m',
    },
    {
        'name': 'day',
        'type': 'date',
        'fmt': '%d'
    },
    {
        'name': 'build',
        'type': 'integer',
        'start_value': 0
    },
]

VCS = {
    'name': 'git',
    'commit_message': (
        "Version updated from {{ current_version }}",
        " to {{ new_version }}"),
}

