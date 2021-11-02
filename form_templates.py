from pandas import Timestamp
'''
Tested field types:
- numeric fields = [float, int]
- time fields = [Timestamp]
- normal fields = [str]
'''

# Note the template is not formatted perfectly on purpose, as it is re-formatted by clean_string function.
overview_template = list()
overview_template.append({'name': 'Arrangement',
                      'entry': 'sommerkurs for voksne',
                      'fmt': str})
overview_template.append({'name': 'Fra',
                      'entry': '20/10/2021 18:00',
                      'fmt': Timestamp,
                      'datetime_fmt': '%d/%m/%Y %H:%M'})
overview_template.append({'name': 'Til',
                      'entry': '20/10/2021 20:00',
                      'fmt': Timestamp,
                      'datetime_fmt': '%d/%m/%Y %H:%M'})
overview_template.append({'name': 'Sted',
                      'entry': 'ila parken',
                      'fmt': str})
overview_template.append({'name': 'Info',
                      'entry': 'dette sommerkurset var ment for voksne mellom 20 til 50. \n \
                      kurset hadde fokus på utforskende bevegelse og parkoursyn.',
                      'fmt': str})
overview_template.append({'name': 'Notater',
                      'entry': 'det var for få trenere. det var mange som besvimte idag pågrunn av varmen, vi bør ta med vann til neste arrangement! \n \
                      overraskende nokk kom det en 90åring! Kanskje vi bør ha et kurs for gamle med fokus på falling...',
                      'fmt': str})

manifest_template = list()
manifest_template.append({'name': 'Fornavn',
                          'entry': 'Ino',
                          'fmt': str})
manifest_template.append({'name': 'Etternavn',
                          'entry': 'Showup',
                          'fmt': str})
manifest_template.append({'name': 'Rolle',
                          'entry': 'D',
                          'fmt': str})
manifest_template.append({'name': 'Alder',
                          'entry': '45',
                          'fmt': int})
manifest_template.append({'name': 'Fravær',
                          'entry': 'x',
                          'fmt': str})
manifest_template.append({'name': 'Inntekt',
                          'entry': '400',
                          'fmt': float})
manifest_template.append({'name': 'Utgift',
                          'entry': '500',
                          'fmt': float})
