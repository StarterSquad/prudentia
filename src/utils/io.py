import os


def prudentia_python_dir():
    cwd = os.path.realpath(__file__)
    components = cwd.split(os.sep)
    return str.join(os.sep, components[:components.index("prudentia") + 1])


def xstr(s):
    return '' if s is None else str(s)


def input_string(topic, default_description=None, default_value=None, previous=None, mandatory=True):
    if not previous:
        default = default_description if default_description else default_value
        if default:
            input_msg = 'Specify the %s [default: %s]: ' % (topic, default)
        else:
            input_msg = 'Specify the %s: ' % topic
    else:
        input_msg = 'Specify the %s [previous: %s]: ' % (topic, previous)
    answer = raw_input(input_msg).strip()
    if previous and not len(answer):
        answer = previous
    if mandatory and not len(answer):
        if not default_value:
            raise ValueError("Default value for '%s' not provided." % answer)
        else:
            answer = default_value
    elif not len(answer):
        answer = None
    return answer


def input_value(topic, default_value=None, default_description=None, mandatory=True):
    default = default_description if default_description else default_value
    if default:
        input_msg = 'Specify the %s [default: %s]: ' % (topic, default)
    else:
        input_msg = 'Specify the %s: ' % topic
    answer = raw_input(input_msg).strip()
    if not len(answer):
        if default_value:
            answer = default_value
        else:
            if mandatory:
                raise ValueError('You must give a valid answer because this is mandatory.')
            else:
                answer = None
    else:
        if default_value and type(default_value) == int:
            answer = int(answer)
    return answer


def input_yes_no(topic, default='N'):
    input_msg = 'Do you want to %s? [default: %s]: ' % (topic, default.upper())
    answer = raw_input(input_msg).strip()
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False
