import copy
from datetime import datetime
import re
import sys
from itertools import chain
import dateutil.parser
import pandas as pd
import textwrap


def get_response(form, i):
    field = form[i]
    n_tries = 2
    while n_tries:
        if 'datetime_fmt' in field:
            example_datetime = pd.to_datetime(datetime.today()).strftime(field['datetime_fmt'])
            hint = 'f.eks: ' + example_datetime
            response = input('{} - [{}] ({}):\n~ '.format(i, field['name'], hint))
        else:
            response = input('{} - [{}] ({}):\n~ '.format(i, field['name'], field['fmt']))
        if response:
            break
        else:
            response = 'N/A'
        n_tries -= 1
    return response


def print_form(form):
    form_str = ''
    for i in range(len(form)):
        form_str += '{} - [{}]:\n~ {}\n'.format(i, form[i]['name'], form[i]['entry'])
    pretty_print(form_str[:-1])


def remove_spaces(old_string, sentence_enders):
    string = old_string
    string = re.sub(r'[ \t][ \t]+', ' ', string)  # remove repeated spaces
    string = re.sub(r'([{0}]+)[ \t]+([{0}]+)'.format(sentence_enders), r'\1\2',
                    string)  # remove spaces between sentence enders
    string = re.sub(r'[ \t]*\n[ \t]*', '\n', string)  # remove spaces before and after new lines
    if string == old_string:
        return string
    else:
        return remove_spaces(string, sentence_enders)


def clean_string(string, max_width=1000):
    sentence_enders = '.!?\n'
    numeric = string.replace('.', '', 1).isdigit()
    if not numeric:
        # Make sentences capitalized and remove excessive spaces
        new_string = ''
        substring = ''
        for char in string:  # TODO avoid appending approach?
            substring += char
            if char in sentence_enders:
                substring = re.sub(r'^[ \t]+|[ \t]+$', '', substring)
                new_string += substring.capitalize() + ' '
                substring = ''
        if substring:  # if string doesnt end with a sentence ender
            substring = re.sub(r'^[ \t]+|[ \t]+$', '', substring)
            new_string += substring.capitalize()
        if new_string:
            string = new_string
        else:
            string = string.capitalize()
    string = remove_spaces(string, sentence_enders)
    string = textwrap.fill(string, max_width)
    return string


def hello():
    intro = '''\
Følg instruksene nøye for å fylle ut skjemaet.
"f" - ferdig: med utfylling (eller rad i større skjema)
"g" - gå: til en del i skjemaet (feks del 3 "g3")
"q" - quit: lukk programmet
"e" - eksempel: vis et utfylt eksempel
"s" - status: vis det vi har fylt ut
"h" - hjelp: vis disse instruksene'''
    pretty_print(intro)
    pretty_print('Fyll ut skjemaet')

def goodbye(form):
    print_form(form)
    pretty_print('Se over for det utfylte skjemaet')


def pretty_print(string, print_=True, width=77):
    top = '\n' + '#' * width
    bottom = '-' * width
    string = top + '\n' + string + '\n' + bottom
    if print_:
        print(string)
    return string


class FormTypeException(TypeError):
    def __init__(self, field_hint, index):
        self.index = index
        self.field_hint = field_hint


def handle_exception(i, field, example):
        error_msg = '''\
Feil format i felt {} -> [{}]
   Du skrev:    "{}"
   Et eksempel: "{}"'''\
            .format(i,
            field['name'],
            field['entry'],
            example)
        error_msg = pretty_print(error_msg, print_=False)
        raise FormTypeException(error_msg, i)


def convert_form_datatypes(form):
    for i in range(len(form)):
        field = form[i]
        if str(field['entry']).upper() != 'N/A':
            formatted_response = field['entry']
            if field['fmt'] == pd.Timestamp:
                try:
                    formatted_response = pd.to_datetime(field['entry'], format=field['datetime_fmt'])
                except Exception:  # TODO narrow the scope
                    example_datetime = pd.to_datetime(datetime.today()).strftime(field['datetime_fmt'])
                    handle_exception(i, field, example_datetime)
            elif field['fmt'] == float:
                try:
                    formatted_response = float(field['entry'])
                except ValueError:
                    example_float = 3.14
                    handle_exception(i, field, example_float)
            elif field['fmt'] == int:
                try:
                    formatted_response = int(field['entry'])
                except ValueError:
                    example_int = 7
                    handle_exception(i, field, example_int)
            field['entry'] = formatted_response
    return form


def field_navigation_helper(form, current_index):
    rotated_range = chain(range(current_index, len(form)),  range(current_index))
    for i in rotated_range:
        field = form[i]
        if field['entry'] == '':
            return i
    try:
        convert_form_datatypes(form)
        nav_msg = '''\
Alle deler av skjemaet er utfylt!
"f" - ferdig: med utfylling (eller rad i større skjema)
"s" - status: vis det vi har fylt ut'''
        pretty_print(nav_msg)
        return current_index
    except FormTypeException as e:
        print(e.field_hint)
        return e.index


def write_checkpoint(form, file='.temp'):
    with open(file, 'w') as file:
        for i in range(len(form)):
            section = form[i]
            file.write("{} - [{}] ({}):\n~ {}\n".format(i, section['name'], section['fmt'].__name__, section['entry']))


def read_checkpoint(form, file='.temp'):
    with open(file, 'r') as file:
        for i in range(len(form)):
            section = form[i]
            _ = file.readline()
            section['entry'] = file.readline()[2:]
    return form


def fill_form(form, template_form, user_input=True, max_width=100):
    i, n = field_navigation_helper(form, 0), len(form)
    while i < n:
        field = form[i]
        if user_input:
            response = get_response(form, i)
        else:  # direct input from template
            if i + 1 == n:  # break loop
                n = i
            response = template_form[i]['entry']
        jump = re.search(r'^g\d', response)
        if jump:
            i = int(jump.group()[1:])
        elif response == 'f':
            write_checkpoint(form)  # TODO add checkpoint name
            break
        elif response == 'q':
            sys.exit()
        elif response == 'e':
            print_form(template_form)
        elif response == 'h':
            hello()
        elif response == 's':
            print_form(form)
        else:
            response = clean_string(response, max_width=max_width)
            field['entry'] = response
            i = field_navigation_helper(form, i)
    return form


def get_empty_form(template_form):
    form = copy.deepcopy(template_form)
    for field in form:
        field['entry'] = ''
    return form


def walkthrough_form(form, template_form, user_input=None, max_width=100):
    hello()
    # TODO add checkpoint start
    form = fill_form(form, template_form, user_input=user_input, max_width=max_width)
    goodbye(form)
    return form


def form_to_df(template_form, iterated_form=False, user_input=True, max_width=100):
    for field in template_form:
        field['entry'] = clean_string(field['entry'])
    if iterated_form:
        dtypes = dict([(field['name'], field['fmt']) for field in template_form])
        entries = []
        while True:
            form = get_empty_form(template_form)
            form = walkthrough_form(form, template_form, user_input=user_input, max_width=max_width)
            entry = {field['name']: field['entry'] for field in form}
            entries.append(entry)
            if user_input:
                promt = '''
"f" hvis du er ferding med å fylle ut rader
alt annet for å legge til flere rader\n'''
                response = input(pretty_print(promt, print_=False))
            else:
                df = pd.DataFrame(entries)
                return df.astype(dtypes)
            if response == 'f':
                break
        return pd.DataFrame(entries).astype(dtypes)
    else:
        form = get_empty_form(template_form)
        form = walkthrough_form(form, template_form, user_input=user_input, max_width=max_width)
        return pd.DataFrame(form)[['name', 'entry']]


if __name__ == '__main__':
    from form_templates import *
    #form_to_df(overview_template, user_input=False)
    #form_to_df(manifest_template, iterated_form=True, user_input=False)

    #form_to_df(overview_template)
    #form_to_df(manifest_template, iterated_form=True)

    # checkpoints
    #form = get_empty_form(overview_template)
    #form = fill_form(form, None, user_input=True)
    #print_form(read_checkpoint(form))
