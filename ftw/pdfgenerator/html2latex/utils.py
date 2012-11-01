from ftw.pdfgenerator import _
from zope.component.hooks import getSite
from zope.i18n import translate


ENVIRONMENTS = {
    'table': {
        'label': _(u'enviroment_table', default=u'Table'),
        'index': 'lot',
        'counter': 'table'},

    'figure': {
        'label': _(u'enviroment_figure', default=u'Figure'),
        'index': 'lof',
        'counter': 'figure'}}


def generate_manual_caption(caption, environment, show_in_index=True):
    """In LaTeX, captions are used within floating environmonts (such as
    "table" or "figure").
    Since we generate LaTeX automatically we are usually not using floating
    environments so that LaTeX does not reposition images and tables.
    Because of that we cannot use the standard \caption command, we need
    to do it manually.

    This helper function generates the LaTeX code for placing a caption
    outside a floating environment.

    Arguments:
    caption -- The caption text as LaTeX.
    enviroment -- The type of environment (either "table" or "figure").
    """

    if not caption:
        return ''

    if environment not in ENVIRONMENTS.keys():
        raise ValueError('Environment must be one of "%s". Got "%s".' % (
                '", "'.join(ENVIRONMENTS.keys()), environment))

    env = ENVIRONMENTS[environment]
    label = translate(env['label'], context=getSite().REQUEST).encode('utf-8')

    latex = [r'\begin{center}']

    if show_in_index:
        latex.extend([
                r'\addtocounter{%s}{1}' % env['counter'],

                r'\addcontentsline{%s}{%s}{' % (
                    env['index'], env['counter']) +
                r'\protect\numberline ' +
                r'{\thechapter.\arabic{%s}}' % env['counter'] +
                r'{\ignorespaces %s}' % caption +
                r'}',

                r'%s \thechapter.\arabic{%s}: %s' % (
                    label, env['counter'], caption),
                ])

    else:
        latex.append(caption)

    latex.extend([
            r'\end{center}',
            r'',
            ])

    return '\n'.join(latex)
