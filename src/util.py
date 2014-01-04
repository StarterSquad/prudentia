import os


def xstr(s):
    return '' if s is None else str(s)


def input_string(topic, default_description=None, default_value=None, previous=None, mandatory=True):
    if not previous:
        default = default_description if default_description else default_value
        if default:
            input_play = 'Specify the %s [default: %s]: ' % (topic, default)
        else:
            input_play = 'Specify the %s: ' % topic
    else:
        input_play = 'Specify the %s [previous: %s]: ' % (topic, previous)
    string = raw_input(input_play).strip()
    if previous and not len(string):
        string = previous
    if mandatory and not len(string):
        if not default_value:
            raise ValueError("Default value for '%s' not provided." % string)
        else:
            string = default_value
    elif not len(string):
        string = None
    return string


def prudentia_python_dir():
    cwd = os.path.realpath(__file__)
    components = cwd.split(os.sep)
    return str.join(os.sep, components[:components.index("prudentia") + 1])