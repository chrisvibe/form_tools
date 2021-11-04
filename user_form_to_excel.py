import pandas as pd
from styleframe import Styler, utils, StyleFrame

from cli_user_form import form_to_df
from form_templates import manifest_template
from form_templates import overview_template


# Read event file
#excel_file = 'demo_sommerkurs.ods'
#overview_df = pd.read_excel(excel_file, sheet_field='Oversikt')
#manifest_df = pd.read_excel(excel_file, sheet_field='Manifest')


def transpose_df_and_add_index(df, old_index='index', new_index='_', inplace=False):
    if inplace:
        df.T.reset_index(inplace=True)
        df.refield(columns={old_index: new_index}, inplace=True)
    else:
        df = df.T.reset_index()
        df = df.refield(columns={old_index: new_index})
        return df


def remove_timezone_info(df):
    # why???! excel doesnt support timezone
    for col in df:
        datetime_rows = df[col].apply(lambda x: isinstance(x, pd.Timestamp))
        if datetime_rows.any():
            #df[col][datetime_rows] = df[col][datetime_rows].dt.tz_localize(None)
            df[col][datetime_rows] = df[col][datetime_rows].apply(lambda x: x.replace(tzinfo=None))
    return df


def get_row_heights(sf: StyleFrame):
    height_dict = {}
    row_height = 12
    padding = row_height / 2
    for index, _ in enumerate(sf.data_df.index):
        newlines = max(str(sf.data_df[column].iloc[index]).count('\n') for column in sf.data_df.columns)
        height = (newlines + 1) * row_height + padding
        height_dict[index + 1] = height
    return height_dict


def add_net(df):
    df['Netto'] = df['Inntekt'] - df['Utgift']
    return df


def overview_manifest_event_to_excel():
    # make dataframe based on user input
    overview_df = form_to_df(overview_template, user_input=True, max_width=75)
    manifest_df = form_to_df(manifest_template, iterated_form=True, user_input=True, max_width=75)

    # process df's
    manifest_df = add_net(manifest_df)

    # make styleframes to easily format dataframes
    sf1 = StyleFrame(overview_df)
    sf2 = StyleFrame(manifest_df)

    # define style formatting
    #https://styleframe.readthedocs.io/en/4.0.0/index.html
    base = Styler(
        border_type=utils.borders.thin,
        bg_color=utils.colors.white,
        font_size=12,
        horizontal_alignment=utils.horizontal_alignments.left,
    )
    red_value = base.combine(Styler(
        bg_color=utils.colors.red,
    ))
    header = base.combine(Styler(
        bold=True,
    ))
    float_style = Styler(number_format=utils.number_formats.general_float)
    int_style = Styler(number_format=utils.number_formats.general_integer)

    # apply formatting to styleframes
    sf1.set_column_width('name', 20)
    sf1.set_column_width('entry', 100)
    sf1.apply_column_style(sf1.columns, base)
    sf1.apply_column_style('name', header)
    sf1.set_row_height_dict(get_row_heights(sf1))

    sf2.set_column_width(sf2.columns, 15)
    sf2.apply_column_style(sf2.columns, base,
                           style_header=True,
                           )
    sf2.apply_headers_style(
        styler_obj=header,
    )
    sf2.apply_style_by_indexes(
        indexes_to_style=sf2[sf2['Fravær'] == 'X'],
        cols_to_style=['Fravær'],
        styler_obj=red_value
    )
    sf2.apply_column_style(['Inntekt', 'Utgift', 'Netto'], float_style)
    sf2.apply_column_style(['Alder'], int_style)

    # write dataframes
    ew = StyleFrame.ExcelWriter('demo_sommerkurs.xlsx',
                                # engine_kwargs = {'options': {"constant_memory": True}}
                                )

    sf1.to_excel(ew, index=False, sheet_name='Oversikt', header=False)
    sf2.to_excel(ew, index=False, sheet_name='Manifest')
    ew.save()

    # TODO
    # apply autofilter
    # https://xlsxwriter.readthedocs.io/example_pandas_autofilter.html
    #import openpyxl
    #sheet = ew.sheets['Manifest']
    #from openpyxl.worksheet.filters import FilterColumn
    #filters = [FilterColumn(i) for i in range(len(sf2.columns))]
    #sheet.auto_filter.filterColumn = filters
    #sheet.auto_filter.filterColumn=list(sf2.columns)


if __name__ == '__main__':
    # demo 2
    overview_manifest_event_to_excel()
