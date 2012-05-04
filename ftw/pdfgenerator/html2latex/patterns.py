# -*- coding: latin-1 -*-

from ftw.pdfgenerator import interfaces


MODE_REPLACE = interfaces.HTML2LATEX_MODE_REPLACE
MODE_REGEXP = interfaces.HTML2LATEX_MODE_REGEXP
MODE_REGEXP_FUNCTION = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION
BACKSLASH_MARKER = 'THISISABACKSLASH' * 2


DEFAULT_PATTERNS = ([
        (MODE_REPLACE,  '\\',                      BACKSLASH_MARKER),
        # remove ASCII non breaking space:
        (MODE_REPLACE,  '\xc2\xa0',                ' '),
        interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP,

        # special characters
        (MODE_REPLACE,  '{',                       '\\{'),
        (MODE_REPLACE,  '}',                       '\\}'),
        interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER,
        (MODE_REPLACE,  '&nbsp;',                  ' '),
        (MODE_REGEXP,   '',                    '--'),
        (MODE_REGEXP,   '',                      ''),

        # generally remove empty no-singleton-tags
        (MODE_REGEXP,  r'<(?P<tag>[\w]{0,})>[\s]{0,}</(?P=tag)?>',
         r'',         (interfaces.HTML2LATEX_REPEAT_MODIFIER)),

        # we use only \n for carriage return, remove all \r
        (MODE_REPLACE,  '\r\n',                    ' '),
        (MODE_REPLACE,  '\r',                      ' '),
        (MODE_REPLACE,  '\n',                      ' '),

        # remove "blacklisted" tags (with its contents)
        (MODE_REGEXP,   r'<style.*?>.*?</style>',   r''),

        # headings
        (MODE_REGEXP,   r'<span>(.*?)</span>',     r'\g<1>'),
        (MODE_REGEXP,   r'<h1.*?>(.*?)</h1>',      r'\\section{\g<1>}\n'),
        (MODE_REGEXP,   r'<h2.*?>(.*?)</h2>',      r'\\subsection{\g<1>}\n'),
        (MODE_REGEXP,   r'<h3.*?>(.*?)</h3>',
         r'\\subsubsection{\g<1>}\n'),

        (MODE_REGEXP,   r'<h5.*?class="glossar">(.*?)</h5>',
         r'\\minisec{\g<1>}\n'),
        (MODE_REGEXP,   r'<span.*?class="paragraphHeading".*?>(.*?)</span>',
         r'\\subparagraph{\g<1>}\n'),

        # font style and text decoration
        (MODE_REGEXP,   r'<p[^>]*?class="callout"[^>]*?>(.*?)</p>',
         r'\\begin{quote}\n\g<1>\n\\end{quote}\n'),
        (MODE_REGEXP,   r'([^ ])<(b|strong|em|u|i)> ',
         r'\g<1> <\g<2>>'),
        (MODE_REGEXP,   r'<b>(.*?)</b>',
         r'{\\bf \g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),
        (MODE_REGEXP,   r'<b .*?>(.*?)</b>',
         r'{\\bf \g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),
        (MODE_REGEXP,   r'<strong.*?>(.*?)</strong>',
         r'{\\bf \g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),

        (MODE_REGEXP,   r'<span .*?style="font-weight: bold.*?">(.*?)</span>',
         r'{\\bf \g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),

        # <em> / <u> -> {\em}
        (MODE_REGEXP,   r'<(em|u)(>| [^>]*>)([^<\1]*)</(\1)>([^\s])',
         r'{\\em \g<3>}\/\g<5>'),
        (MODE_REGEXP,   r'<(em|u)(>| [^>]*>)([^<\1]*)</(\1)>',
         r'{\\em \g<3>}'),
        # <i> -> {\it}
        (MODE_REGEXP,   r'<(i)(>| [^>]*>)([^<\1]*)</(\1)>([^\s])',
         r'{\\it \g<3>}\/\g<5>'),
        (MODE_REGEXP,   r'<(i)(>| [^>]*>)([^<\1]*)</(\1)>',
         r'{\\it \g<3>}'),

        (MODE_REGEXP,   r'<sup.*?>(.*?)</sup>',
         r'\\textsuperscript{\g<1>}'),

        # quotes
        (MODE_REGEXP,   r'\&quot;',                 '"'),
        (MODE_REGEXP,   r'"(\w)',                   '"`\g<1>'),
        (MODE_REGEXP,   r'(\S)"',                   '\g<1>"\''),

        # paragraphs and white space
        (MODE_REGEXP,   r'<p.*?>(.*?)[\r\n ]{0,}</p>',
         r'\g<1>\n\n'),
        (MODE_REGEXP,   r'[\r\n]{0,}<br[ \W]{0,}>\s*<br[ \W]{0,}>[\n]{0,1}',
         r'\n\n'),
        (MODE_REGEXP,   r'[\r\n]{0,}<br[ \W]{0,}>\n',
         r'\n'),
        (MODE_REGEXP,   r'[\r\n]{0,}<br[ \W]{0,}>',
         r'\n'),

        (MODE_REGEXP,   r'[\n]{2,}',               r'\n\n'),
        (MODE_REGEXP,   r'^\s*(.*?)\s*$',          r'\g<1>'),           # trim
        (MODE_REGEXP,   r'\n([^\n])',              r'\\\\\n\g<1>'),
        (MODE_REGEXP,   r'([^}])\n\n',             r'\g<1>\\\\\n\n'),
        (MODE_REGEXP,   r'({\\[\w]*? )\\\\\W(.*?})',
         r'\1\2'),

        # special characters
        (MODE_REPLACE,  '%',                       '\\%'),
        (MODE_REGEXP,   r'(\d) \\%',               r'\1\,\\%'),
        (MODE_REPLACE,  '_',                       '\\_'),
        (MODE_REPLACE,  '$',                       '\\$'),
        (MODE_REGEXP,    '§',                       '\\S'),
        (MODE_REPLACE,  '#',                       '\\#'),
        (MODE_REGEXP,    '&szlig;',                 'ß'),
        (MODE_REPLACE,  '&euro;',                  '\\euro{}'),
        (MODE_REPLACE,  '&sect;',                  '\\S'),
        (MODE_REPLACE,  '&amp;',                   '&'),

        (MODE_REPLACE,  '&lsquo;',                 '‘'),
        (MODE_REPLACE,  '&rsquo;',                 '’'),
        (MODE_REPLACE,  '&rsquo;',                 '’'),
        (MODE_REPLACE,  '&ldquo;',                 '“'),
        (MODE_REPLACE,  '&rdquo;',                 '”'),
        (MODE_REPLACE,  '&ndash;',                 '–'),
        (MODE_REPLACE,  '&mdash;',                 '—'),
        (MODE_REPLACE,  '&iexcl;',                 '¡'),
        (MODE_REPLACE,  '&cent;',                  '\\cent{}'),
        (MODE_REPLACE,  '&pound;',                 '£'),
        (MODE_REPLACE,  '&curren;',                '\\currency{}'),
        (MODE_REPLACE,  '&sect;',                  '§'),

        (MODE_REPLACE,  '&uml;',                   '¨'),
        (MODE_REPLACE,  '&copy;',                  '©'),
        (MODE_REPLACE,  '&ordf;',                  'ª'),
        (MODE_REPLACE,  '&laquo;',                 '«'),
        (MODE_REPLACE,  '&not;',                   '¬'),
        (MODE_REPLACE,  '&reg;',                   '®'),
        (MODE_REPLACE,  '&macr;',                  '¯'),
        (MODE_REPLACE,  '&deg;',                   '°'),
        (MODE_REPLACE,  '&plusmn;',                '±'),

        (MODE_REPLACE,  '&sup2;',                  '²'),
        (MODE_REPLACE,  '&sup3;',                  '³'),
        (MODE_REPLACE,  '&acute;',                 '´'),
        (MODE_REPLACE,  '&micro;',                 'µ'),
        (MODE_REPLACE,  '&para;',                  '¶'),
        (MODE_REPLACE,  '&middot;',                '·'),
        (MODE_REPLACE,  '&cedil;',                 '¸'),

        (MODE_REPLACE,  '&sup1;',                  '¹'),
        (MODE_REPLACE,  '&ordm;',                  'º'),
        (MODE_REPLACE,  '&raquo;',                 '»'),
        (MODE_REPLACE,  '&frac14;',                '¼'),
        (MODE_REPLACE,  '&frac12;',                '½'),
        (MODE_REPLACE,  '&frac34;',                '¾'),

        (MODE_REPLACE,  '&iquest;',                '¿'),
        (MODE_REPLACE,  '&times;',                 '×'),
        (MODE_REPLACE,  '&divide;',                '÷'),
        (MODE_REPLACE,  '&sbquo;',                 '‚'),
        (MODE_REPLACE,  '&bdquo;',                 '„'),
        (MODE_REPLACE,  '&hellip;',                '…'),

        (MODE_REPLACE,  '&trade;',                 '™'),
        (MODE_REPLACE,  '&bull;',                  '•'),
        (MODE_REPLACE,  '&rarr;',                  '→'),
        (MODE_REPLACE,  '&rArr;',                  '⇒'),
        (MODE_REPLACE,  '&hArr;',                  '⇔'),
        (MODE_REPLACE,  '&asymp;',                 '≈'),
        (MODE_REPLACE,  '‑',                       '-'),
        (MODE_REPLACE,  '^',                       '\\^{}'),
        (MODE_REPLACE,  '~',                       '\\~{}'),

        # Various abbreviation replacements...
        # TODO: make regexp patterns or subconverter
        (MODE_REGEXP,   r'\\S[ ]{0,1}(\d)',         r'\S\,\1'),
        (MODE_REPLACE,  'e.g.',                    'e.\,g.'),
        (MODE_REPLACE,  'e. g.',                   'e.\,g.'),
        (MODE_REPLACE,  'i.d.r',                   'i.\,d.\,r.'),
        (MODE_REPLACE,  'i. d. r.',                'i.\,d.\,r.'),
        (MODE_REPLACE,  'z.B.',                    'z.\,B.'),
        (MODE_REPLACE,  'z. B.',                   'z.\,B.'),
        (MODE_REPLACE,  'lic.iur.',                'lic.\,iur.'),
        (MODE_REPLACE,  'Dr.iur.',                 'Dr.\,iur.'),

        # date replacements: we use nonbreakable spaces
        # TODO: make regexp patterns or subconverter
        ] + [
        (MODE_REGEXP,    r'(\d)\.\W{0,1}(' + month + ')',
         r'\1.~\2')
        for month in ['Jan', 'Feb', 'Mar', 'Mär', 'Apr', 'Mai', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Okt', 'Oct', 'Nov', 'Dez', 'Dec']
        ] + [

        # NOT SUPPORTED!!
        (MODE_REPLACE,  '&yen;',                   ''),
        (MODE_REPLACE,  '&brvbar;',                ''),
        (MODE_REPLACE,  '‛',                       ''),
        (MODE_REPLACE,  '&diams;',                 ''),
        (MODE_REPLACE,  '►',                       ''),

        # misc
        (MODE_REGEXP,   r'([a-zA-Z])-',            r'\1"='),
        # - at the end of a word should not disable hyphenation

        #    (MODE_REGEXP,   r'([a-zA-Z].)*',           r'U\1U'),
        # abbreviation should contain short whitespace (\,)

        # cleanup
        # strip html tags
        (MODE_REGEXP,   r'<([^>]*?)>',             r''),
        # remove all line endings (\\) before \sub*
        (MODE_REGEXP,   r'\\\\\s*(\n\\sub)',       r'\g<1>'),
        # remove all line endings (\\) which finish a empty line
        (MODE_REGEXP,   r'(\n|^)[ ]{0,}\\\\',      r'\g<1>'),
        # remove all line endings (\\) after a } (latex command)
        (MODE_REGEXP,   r'}[\t ]{0,}\\\\',         r'}'),

        # special characters
        (MODE_REPLACE,  '&lt;',                    '<'),
        (MODE_REPLACE,  '&gt;',                    '>'),
        (MODE_REPLACE,  '&',                       '\\&'),
        interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM,
        (MODE_REPLACE,  interfaces.HTML2LATEX_PREVENT_CHARACTER,         ''),
        (MODE_REPLACE,  BACKSLASH_MARKER,
         '\\\\'),
        ])
