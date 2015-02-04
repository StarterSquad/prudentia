import os
from getpass import getpass


def prudentia_python_dir():
    cwd = os.path.realpath(__file__)
    components = cwd.split(os.sep)
    last_prudentia_index = len(components) - components[::-1].index("prudentia")
    return str.join(os.sep, components[:last_prudentia_index])


def xstr(s):
    return '' if s is None else str(s)


def first_time_input():
    if first_time_input.show:
        print '\nPlease enter values for the following settings, ' \
              'press \'Enter\' to accept the default value (if its given in brackets).\n'
        first_time_input.show = False
first_time_input.show = True


def input_value(topic, default_value=None, default_description=None, mandatory=True, hidden=False):
    first_time_input()
    default = default_description if default_description else default_value
    if default:
        input_msg = 'Specify the %s [default: %s]: ' % (topic, default)
    else:
        input_msg = 'Specify the %s: ' % topic
    if not hidden:
        answer = raw_input(input_msg)
    else:
        answer = getpass(input_msg)
    answer = answer.strip()
    if not len(answer):
        if default_value:
            answer = default_value
        else:
            if mandatory:
                raise ValueError('You must enter a valid %s.' % topic)
            else:
                answer = None
    else:
        if default_value and type(default_value) == int:
            answer = int(answer)
    return answer


def input_path(topic, default_value=None, default_description=None, mandatory=True, hidden=False, is_file=True):
    path = input_value(topic, default_value, default_description, mandatory, hidden)
    if not os.path.exists(path):
        raise ValueError('The %s you entered does NOT exist.' % topic)
    elif not os.path.isabs(path):
        raise ValueError('The %s you entered is NOT absolute.' % topic)
    elif is_file and not os.path.isfile(path):
        raise ValueError('The %s you entered is NOT a file.' % topic)
    elif not is_file and not os.path.isdir(path):
        raise ValueError('The %s you entered is NOT a directory.' % topic)
    else:
        return path


def input_yes_no(topic, default='n'):
    first_time_input()
    input_msg = 'Do you want to %s? [default: %s]: ' % (topic, default.upper())
    answer = raw_input(input_msg).strip()
    if not len(answer):
        answer = default
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False
