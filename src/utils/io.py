import os


def prudentia_python_dir():
    cwd = os.path.realpath(__file__)
    components = cwd.split(os.sep)
    return str.join(os.sep, components[:components.index("prudentia") + 1])


def xstr(s):
    return '' if s is None else str(s)


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


def input_yes_no(topic, default='n'):
    input_msg = 'Do you want to %s? [default: %s]: ' % (topic, default.upper())
    answer = raw_input(input_msg).strip()
    if not len(answer):
        answer = default
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False
