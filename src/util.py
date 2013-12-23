def xstr(s):
    return '' if s is None else str(s)


def input_string(topic, default_desc=None, previous=None, mandatory=True):
    if not previous:
        if default_desc:
            input_play = 'Specify the %s [%s]: ' % (topic, default_desc)
        else:
            input_play = 'Specify the %s: ' % topic
    else:
        input_play = 'Specify the %s [%s]: ' % (topic, previous)
    string = raw_input(input_play).strip()
    if previous and not len(string):
        string = previous
    if mandatory and not len(string):
        raise ValueError("'%s' not valid." % string)
    elif not len(string):
        string = None
    return string
