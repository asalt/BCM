import re
import math

import pandas as pd
import jinja2


jinja_options = dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='<<',
    variable_end_string='>>',
    comment_start_string='<#',
    comment_end_string='#>',
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_data(datafile):

    rank_data, detailed_data = list(), list()

    df = pd.read_csv(datafile).sort_values(by=['last_name', 'first_name'])
    for ix, row in df.iterrows():
        name = '{} {}'.format(row.first_name, row.last_name)
        rank_numbers = []
        detailed_numbers = []

        rank_posters = row.rank_posters
        detailed_posters = row.detailed_posters

        if isinstance(rank_posters, str):
            rank_numbers = [x.strip() for x in rank_posters.split('|')]
        if isinstance(detailed_posters, str):
            detailed_numbers = [int(x.strip()) for x in detailed_posters.split('|')]

        rank_data.append(
            {'name': name,
             'numbers': rank_numbers
            }
        )

        detailed_data.append(
            {'name': name,
             'numbers': detailed_numbers
            }
        )

    return rank_data, detailed_data


def render_latex(data, template, outname):
    environ = jinja2.Environment(**jinja_options)
    out = environ.from_string(open(template, 'r').read()).render(users=data)
    with open(outname, 'w') as f:
        f.write(out)
    print('Wrote', outname)

def main():

    rank_template = './templates/judging_template.tex'
    detailed_template = './templates/detailed_template.tex'

    rank_data, detailed_data = get_data('BMB_Retreat_user.csv')
    render_latex(rank_data, rank_template, 'judging_sheets.tex')
    render_latex(detailed_data, detailed_template, 'detailed_sheets.tex')

if __name__ == '__main__':
    main()
