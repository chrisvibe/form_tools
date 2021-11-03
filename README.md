# pk_data

# Verktøy for:
* manual innsamling av data via skjema
* statestikk og sammendrag

# Data flow
1. user_input.py samler data i et skjema fra en mal i form_templates.py
2. dataen er samlet i en pandas dataframe
3. Andre programmer bruker dataen f.eks pk_event_logger.py som lager sammendrag i excel.

# install
pip3 install -r requirements.txt
or
pip3 install -U pandas XlsxWriter odfpy styleframe
