# form_tools 

# Verktøy for:
* manual innsamling av data via skjema
* statestikk og sammendrag

# Data flow
1. user_input.py samler data i et skjema fra en mal i form_templates.py
2. dataen er samlet i en pandas dataframe
3. Andre programmer bruker dataen f.eks user_form_to_excel.py som lager sammendrag i excel.

# Install
pip3 install -r requirements.txt
or
pip3 install -U pandas XlsxWriter odfpy styleframe

# Demo1 - fyll et skjema
python3 cli_user_form.py
1. Følg instruksene for å fylle et skjema
2. Skjemaet er nå tilgjengelig som et pandas dataframe

# Demo2 - automatisk excel ark 
python3 user_form_to_excel.py
1. Følg instruksene for å fylle et skjema om et arrangement.
2. Fyll et nytt skjema med oversikt over deltakere (1 skjema per deltaker)
3. Sjekk resultatet i demo_sommerkurs.xlsx
