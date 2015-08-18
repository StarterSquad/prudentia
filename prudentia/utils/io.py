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
        print '\nPlease enter values for the following settings ' \
              '(a default value could be suggested in brackets \'[ ]\', press \'Enter\' to use it).'
        first_time_input.show = False
first_time_input.show = True


def _input(msg):
    first_time_input()
    return raw_input(msg)


def _hidden_input(msg):
    first_time_input()
    return getpass(msg)


def input_value(topic, default_value=None, default_description=None, mandatory=True, hidden=False, prompt_fn=_input,
                hidden_prompt_fn=_hidden_input):
    default = default_description if default_description else default_value
    if default:
        input_msg = 'Specify the %s [default: %s]: ' % (topic, default)
    else:
        input_msg = 'Specify the %s: ' % topic
    if not hidden:
        answer = prompt_fn(input_msg)
    else:
        answer = hidden_prompt_fn(input_msg)
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


def input_path(topic, default_value=None, default_description=None, mandatory=True, is_file=True, prompt_fn=_input,
               retries=3):
    times = 0
    while times < retries:
        path = os.path.realpath(os.path.expanduser(
            input_value(topic, default_value, default_description, mandatory, False, prompt_fn)
        ))
        if not os.path.exists(path):
            print 'The %s you entered does NOT exist.' % topic
        elif is_file and not os.path.isfile(path):
            print 'The %s you entered is NOT a file.' % topic
        elif not is_file and not os.path.isdir(path):
            print 'The %s you entered is NOT a directory.' % topic
        else:
            return path
        times += 1
    raise ValueError('Reached max retries: {0}.'.format(retries))


def input_yes_no(topic, default='n', prompt_fn=_input):
    input_msg = 'Do you want to %s? [default: %s]: ' % (topic, default.upper())
    answer = prompt_fn(input_msg).strip()
    if not len(answer):
        answer = default
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False


def input_choice(topic, default=None, choices=None, prompt_fn=_input, retries=3):
    if not isinstance(choices, list):
        raise ValueError('Choices must be a list: \'{0}\'.'.format(choices))
    elif not len(choices):
        raise ValueError('Choices are empty.')
    elif default and default not in choices:
        raise ValueError('Default value \'{0}\' is not part of provided choices: \'{1}\'.'.format(default, choices))
    else:
        times = 0
        while times < retries:
            if default:
                input_msg = 'Specify the %s [default: %s]: ' % (topic, default)
            else:
                input_msg = 'Specify the %s: ' % topic
            answer = prompt_fn(input_msg).strip()
            if not len(answer):
                if default:
                    answer = default
            if answer not in choices:
                print '\nPlease enter one of the following choices: {0}'.format(', '.join(choices))
                times += 1
            else:
                return answer
        raise ValueError('Reached max retries: {0}.'.format(retries))
