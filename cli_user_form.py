import copy
import re
import sys
import textwrap
from datetime import datetime
from itertools import chain

import pandas as pd

from form_templates import *


def get_response(form, i):
    field = form[i]
    n_tries = 2
    while n_tries:
        if 'datetime_fmt' in field:
            example_datetime = pd.to_datetime(datetime.today()).strftime(field['datetime_fmt'])
            hint = 'f.eks: ' + example_datetime
            response = input('{} - [{}] ({}):\n~ '.format(i, field['name'], hint))
        else:
            response = input('{} - [{}]:\n~ '.format(i, field['name']))
        if response:
            break
        else:
            response = NA
        n_tries -= 1
    return response


def print_form(form, print_=True):
    form_str = ''
    for i in range(len(form)):
        field = form[i]
        empty = field['entry'] in [NAN, NO_ENTRY]
        entry = '' if empty else field['entry']
        form_str += '{} - [{}]:\n~ {}\n'.format(i, field['name'], entry)
    return pretty_print(form_str[:-1], print_=print_)


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
"f" - ferdig: med utfylling av skjema/rad, og lager checkpoint fil
"g" - gå: til en del i skjemaet (feks del 3 "g3")
"q" - quit: lukk programmet
"e" - eksempel: vis et utfylt eksempel
"s" - status: vis det vi har fylt ut
"r" - read: les en checkpoint fil
"w" - write: skriv en checkpoint fil
"h" - hjelp: vis disse instruksene
"ENTER"x2 for å la et felt være blankt'''
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
        if str(field['entry']).upper() != NO_ENTRY:
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
        elif field['fmt'] == float:
            field['entry'] = NAN
        elif field['fmt'] == int:  # Cant be np.nan as its a float
            field['entry'] = field['default']
    return form


def field_navigation_helper(form, current_index, check_empty=True):
    error_flag = False
    if check_empty:
        rotated_range = chain(range(current_index, len(form)),  range(current_index))
        for i in rotated_range:
            field = form[i]
            if field['entry'] is NO_ENTRY:
                return i, error_flag
    try:
        convert_form_datatypes(form)
        nav_msg = '''\
Alle deler av skjemaet er utfylt!
"f" - ferdig: med utfylling (eller rad i større skjema)
"s" - status: vis det vi har fylt ut'''
        pretty_print(nav_msg)
        return current_index, error_flag
    except FormTypeException as e:
        error_flag = True
        print(e.field_hint)
        return e.index, error_flag


def write_checkpoint(form, file='.checkpoint'):
    with open(file, 'w') as file:
        file.write(print_form(form, print_=False))


def read_checkpoint(form, file='.checkpoint'):
    with open(file, 'r') as file:
        _ = file.readline()
        _ = file.readline()
        for i in range(len(form)):
            section = form[i]
            _ = file.readline()
            section['entry'] = file.readline()[2:]
    return form


def fill_form(form, template_form, user_input=True, max_width=100):
    i, _ = field_navigation_helper(form, 0)
    n = len(form)
    while i < n:
        field = form[i]
        if user_input:
            response = get_response(form, i)
        else:  # direct input from template
            if i + 1 == n:  # break loop (flush first)
                n = i
            response = template_form[i]['entry']
        jump = re.search(r'^g\d', response)
        if jump:
            i = int(jump.group()[1:])
        elif response == 'f':
            i, error = field_navigation_helper(form, i, check_empty=False)
            if not error:
                break
        elif response == 'q':
            sys.exit()
        elif response == 'e':
            print_form(template_form)
        elif response == 'h':
            hello()
        elif response == 's':
            print_form(form)
        elif response == 'r':
            form = read_checkpoint(form)
        elif response == 'w':
            write_checkpoint(form)
        else:
            response = clean_string(response, max_width=max_width)
            field['entry'] = response
            i, _ = field_navigation_helper(form, i)
    return form


def get_empty_form(template_form):
    form = copy.deepcopy(template_form)
    for field in form:
        field['entry'] = NO_ENTRY
    return form


def walkthrough_form(form, template_form, user_input=None, max_width=100):
    hello()
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
                promt = '''\
"f"     - hvis du er ferding med å fylle ut rader
"ENTER" - for å legge til flere rader'''
                response = input(pretty_print(promt, print_=False) + '\n')
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
    # demo 1
    form_to_df(overview_template)

    # Run with template as user input
    #form_to_df(overview_template, user_input=False)
    #form_to_df(manifest_template, iterated_form=True, user_input=False)

    # Test checkpoints (manually)
    #form = get_empty_form(overview_template)
    #form = fill_form(form, None, user_input=True)
    #print_form(read_checkpoint(form))
