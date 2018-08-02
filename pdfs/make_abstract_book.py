import re
import math

import pandas as pd
import jinja2
from nameparser import HumanName


# _italics = re.compile(r'(?<=\<em\>)(.*)(?=\<\/em\>)', re.DOTALL)

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

def get_delim(auths):
    if ';' in auths:
        return ';'
    elif ',' in auths:
        return ','
    else:
        return ','

def get_authors(row):
    # first_auth = str(HumanName(row.user))

    delim = get_delim(row.authors)

    auths = [x for x in row.authors.replace(' and', delim).replace(' &', delim).split(delim)
             if bool(x.strip())]
    # pi = str(HumanName(auths[-1]))
    first_auth = str(HumanName(auths[0]))
    # if pi == first_auth:
    #     pi = ''
    # others = [str(HumanName(x)) for x in auths[1:-1]]
    return [str(HumanName(x)) for x in auths]

    # auth_info = dict(first_auth=first_auth,
    #                  other_auths = ', '.join(others),y
    #                     pi=pi
    # )
    # return auth_info

def format_abstract(abstract):

    # lines = list()
    # for line in abstract.split('. '):

        # txt = re.sub(r'\/(.*)\/', r'\\textit{\1}', line)
        # txt = re.sub(r'\*(.*)\*', r'\\textbf{\1}', txt)
        # fmt = txt.replace('%', '\%')
        # lines.append(fmt)

    # return '. '.join(lines)
    return abstract.replace('%', '\%').replace('>', '$>$').replace('~', r'$\approx$')



def get_data(datafile):

    data = list()
    TOC = dict()

    df = pd.read_csv(datafile).sort_values(by='user')
    cols = ['authors', 'title', 'authors']
    data = list()
    for ix, row in df.iterrows():

        presenter = row.presenter
        other_authors = get_authors(row)
        final_author = row.final_author
        authors = {'first_auth': presenter,
                   'other_auths': ', '.join(other_authors),
                   'pi' : final_author
        }
        title = row.title
        abstract = format_abstract(row.abstract)
        poster_number = row.poster_number


        if math.isfinite(poster_number):
            poster_number = int(poster_number)
        else:
            poster_number = ''


        TOC[authors['first_auth']] = '{} {}'.format(row.presentation.capitalize(), poster_number)

        data.append(
            dict(title=title,
                 poster_number=poster_number,
                 auths=authors,
                 paragraphs=abstract)
            )

    return data, TOC

def render_latex(data, TOC, template):
    environ = jinja2.Environment(**jinja_options)
    out = environ.from_string(open(template, 'r').read()).render(abstracts=data,
                                                                 TOC=TOC)
    with open('abstract_book_formatted.tex', 'w') as f:
        f.write(out)

def main():
    template = './templates/template.tex'

    data, TOC = get_data('BMB_Retreat_submission.csv')
    print('Found {} abstracts.'.format(len(data)))
    render_latex(data, TOC, template)

if __name__ == '__main__':
    main()
