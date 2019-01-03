# -*- coding: latin-1 -*-

from ftw.pdfgenerator import interfaces


MODE_REPLACE = interfaces.HTML2LATEX_MODE_REPLACE
MODE_REGEXP = interfaces.HTML2LATEX_MODE_REGEXP
MODE_REGEXP_FUNCTION = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION
BACKSLASH_MARKER = 'THISISABACKSLASH' * 2

DASH = '\xe2\x80\x93'  # &ndash;


DEFAULT_PATTERNS = ([
        (MODE_REPLACE,  '\\',                      BACKSLASH_MARKER),
        # remove ASCII non breaking space:
        (MODE_REPLACE,  '\xc2\xa0',                ' '),
        # remove ASCII vertical tab control character
        (MODE_REPLACE,  '\x0b',                ' '),
        # remove ASCII form feed control character
        (MODE_REPLACE,  '\x0c',                ' '),
        interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP,

        # special characters
        (MODE_REPLACE,  '{',                       '\\{'),
        (MODE_REPLACE,  '}',                       '\\}'),
        interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER,
        (MODE_REPLACE,  '&nbsp;',                  ' '),
        (MODE_REGEXP,   '',                    '--'),
        (MODE_REGEXP,   '',                      ''),

        # remove comments
        (MODE_REGEXP,  r'<!--(?:(?!-->).)*-->',    ''),

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
         r'\\textbf{\g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),
        (MODE_REGEXP,   r'<b .*?>(.*?)</b>',
         r'\\textbf{\g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),
        (MODE_REGEXP,   r'<strong.*?>(.*?)</strong>',
         r'\\textbf{\g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),

        (MODE_REGEXP,   r'<span .*?style="font-weight: bold.*?">(.*?)</span>',
         r'\\textbf{\g<1>}' + interfaces.HTML2LATEX_PREVENT_CHARACTER),

        # <em> / <u> -> \emph{X}
        (MODE_REGEXP,   r'<(em|u)(>| [^>]*>)(.*?)</(\1)>',
         r'\\emph{\g<3>}'),
        # <i> -> \textit{X}
        (MODE_REGEXP,   r'<(i)(>| [^>]*>)(.*?)</(\1)>',
         r'\\textit{\g<3>}'),

        (MODE_REGEXP,   r'<sup.*?>(.*?)</sup>',
         r'\\textsuperscript{\g<1>}'),

        # quotes
        (MODE_REGEXP,   r'\&quot;',                 '"'),
        (MODE_REGEXP,   r'"([\w\{\\])',             '"`\g<1>'),
        (MODE_REGEXP,   r'([^ \t\n\r\f\v\{])"(?!`)',     '\g<1>"\''),

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
        (MODE_REGEXP,   r'(\\[\w]*?{)\\\\\W(.*?})',
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
        (MODE_REPLACE,  '*',                       r'$\ast$'),

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
        (MODE_REPLACE,  '&not;',                   r'\ensuremath{\lnot}'),
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

        # additional hypthenation character
        (MODE_REPLACE,  '\xc2\xad',                '"-'),
        (MODE_REPLACE,  '&shy;',                   '"-'),

        # utf8 math characters
        (MODE_REPLACE,  '\xe2\x8a\xa5',            r'$\perp$'),
        (MODE_REPLACE,  '\xe2\x89\xa4',            r'$\leq$'),
        (MODE_REPLACE,  '\xe2\x88\x96',            r'$\setminus$'),
        (MODE_REPLACE,  '\xe2\x8a\x83',            r'$\supset$'),
        (MODE_REPLACE,  '\xe2\x84\x9c',            r'$\Re$'),
        (MODE_REPLACE,  '\xe2\x86\x97',            r'$\nearrow$'),
        (MODE_REPLACE,  '\xe2\x88\x9a',            r'$\surd$'),
        (MODE_REPLACE,  '\xc2\xbd',                r'$\frac12$'),
        (MODE_REPLACE,  '\xe2\x85\x93',            r'$\frac13$'),
        (MODE_REPLACE,  '\xc2\xbc',                r'$\frac14$'),
        (MODE_REPLACE,  '\xe2\x85\x95',            r'$\frac15$'),
        (MODE_REPLACE,  '\xe2\x85\x99',            r'$\frac16$'),
        (MODE_REPLACE,  '\xe2\x85\x9b',            r'$\frac18$'),
        (MODE_REPLACE,  '\xe2\x88\xa9',            r'$\cap$'),
        (MODE_REPLACE,  '\xce\xa3',                r'$\Sigma$'),
        (MODE_REPLACE,  '\xce\xa8',                r'$\Psi$'),
        (MODE_REPLACE,  '\xce\xa9',                r'$\Omega$'),
        (MODE_REPLACE,  '\xe2\x88\x85',            r'$\emptyset$'),
        (MODE_REPLACE,  '\xe2\x8b\x83',            r'$\bigcup$'),
        (MODE_REPLACE,  '\xe2\x86\x90',            r'$\leftarrow$'),
        (MODE_REPLACE,  '\xe2\x89\xba',            r'$\prec$'),
        (MODE_REPLACE,  '\xe2\x8a\x97',            r'$\otimes$'),
        (MODE_REPLACE,  '\xe2\x84\xb5',            r'$\aleph$'),
        (MODE_REPLACE,  '\xe2\x8b\xaf',            r'$\cdots$'),
        (MODE_REPLACE,  '\xe2\x89\x85',            r'$\cong$'),
        (MODE_REPLACE,  '\xe2\x89\xa1',            r'$\equiv$'),
        (MODE_REPLACE,  '\xe2\x89\xaa',            r'$\ll$'),
        (MODE_REPLACE,  '\xe2\x8b\x86',            r'$\star$'),
        (MODE_REPLACE,  '\xe2\x89\xa0',            r'$\neq$'),
        (MODE_REPLACE,  '\xce\xb1',                r'$\alpha$'),
        (MODE_REPLACE,  '\xe2\x88\x90',            r'$\amalg$'),
        (MODE_REPLACE,  '\xe2\x8a\x8e',            r'$\uplus$'),
        (MODE_REPLACE,  '\xce\xba',                r'$\kappa$'),
        (MODE_REPLACE,  '\xcf\x83',                r'$\sigma$'),
        (MODE_REPLACE,  '\xce\x9b',                r'$\Lambda$'),
        (MODE_REPLACE,  '\xe2\x88\xaa',            r'$\cup$'),
        (MODE_REPLACE,  '\xce\xbb',                r'$\lambda$'),
        (MODE_REPLACE,  '\xce\x98',                r'$\Theta$'),
        (MODE_REPLACE,  '\xe2\x88\x9c',            r'$\sqrt4$'),
        (MODE_REPLACE,  '\xe2\x89\x80',            r'$\wr$'),
        (MODE_REPLACE,  '\xe2\x84\x98',            r'$\wp$'),
        (MODE_REPLACE,  '\xe2\x88\x9b',            r'$\sqrt3$'),
        (MODE_REPLACE,  '\xc2\xac',                r'\ensuremath{\lnot}'),
        (MODE_REPLACE,  '\xe2\x8a\x93',            r'$\sqcap$'),
        (MODE_REPLACE,  '\xcf\xb1',                r'$\varrho$'),
        (MODE_REPLACE,  '\xce\xb2',                r'$\beta$'),
        (MODE_REPLACE,  '\xe2\x8a\xa3',            r'$\dashv$'),
        (MODE_REPLACE,  '\xe2\x89\xa5',            r'$\geq$'),
        (MODE_REPLACE,  '\xe2\x86\x99',            r'$\searrow$'),
        (MODE_REPLACE,  '\xe2\x99\xa4',            r'$\spadesuit$'),
        (MODE_REPLACE,  '\xe2\x80\xa1',            r'$\ddag$'),
        (MODE_REPLACE,  '\xe2\x88\x8f',            r'$\prod$'),
        (MODE_REPLACE,  '\xe2\x85\x96',            r'$\frac25$'),
        (MODE_REPLACE,  '\xe2\x85\x94',            r'$\frac23$'),
        (MODE_REPLACE,  '\xe2\x8a\xa4',            r'$\bot$'),
        (MODE_REPLACE,  '\xe2\x87\x91',            r'$\Uparrow$'),
        (MODE_REPLACE,  '\xe2\x86\x94',            r'$\leftrightarrow$'),
        (MODE_REPLACE,  '\xcf\x88',                r'$\psi$'),
        (MODE_REPLACE,  '\xe2\x87\x80',            r'$\rightharpoonup$'),
        (MODE_REPLACE,  '\xe2\x88\x99',            r'$\bullet$'),
        (MODE_REPLACE,  '\xcf\x95',                r'$\varphi$'),
        (MODE_REPLACE,  '\xcf\x9b',                r'$\varsigma$'),
        (MODE_REPLACE,  '\xe2\x8a\x84',            r'$\not\subset$'),
        (MODE_REPLACE,  '\xe2\x88\x86',            r'$\Delta$'),
        (MODE_REPLACE,  '\xc2\xb0',                r'$\circ$'),
        (MODE_REPLACE,  '\xcf\x85',                r'$\upsilon$'),
        (MODE_REPLACE,  '\xcf\x87',                r'$\chi$'),
        (MODE_REPLACE,  '\xe2\x89\x90',            r'$\doteq$'),
        (MODE_REPLACE,  '\xe2\x86\x91',            r'$\uparrow$'),
        (MODE_REPLACE,  '\xe2\x88\xad',            r'$\iiint$'),
        (MODE_REPLACE,  '\xe2\x99\xad',            r'$\flat$'),
        (MODE_REPLACE,  '\xce\xa6',                r'$\Phi$'),
        (MODE_REPLACE,  '\xcf\xb5',                r'$\epsilon$'),
        (MODE_REPLACE,  '\xcf\x96',                r'$\varpi$'),
        (MODE_REPLACE,  '\xe2\x8b\x82',            r'$\bigcap$'),
        (MODE_REPLACE,  '\xce\xa0',                r'$\Pi$'),
        (MODE_REPLACE,  '\xe2\x80\xa0',            r'$\dag$'),
        (MODE_REPLACE,  '\xe2\x88\x97',            r'$\ast$'),
        (MODE_REPLACE,  '\xe2\x86\xa6',            r'$\mapsto$'),
        (MODE_REPLACE,  '\xce\xb8',                r'$\theta$'),
        (MODE_REPLACE,  '\xe2\x88\xae',            r'$\oint$'),
        (MODE_REPLACE,  '\xe2\x8a\x95',            r'$\oplus$'),
        (MODE_REPLACE,  '\xe2\x8b\x84',            r'$\diamond$'),
        (MODE_REPLACE,  '\xe2\x84\x93',            r'$\ell$'),
        (MODE_REPLACE,  '\xe2\x88\x93',            r'$\mp$'),
        (MODE_REPLACE,  '\xe2\x88\x87',            r'$\nabla$'),
        (MODE_REPLACE,  '\xe2\x88\x8c',            r'$\not\ni$'),
        (MODE_REPLACE,  '\xe2\x8a\x98',            r'$\oslash$'),
        (MODE_REPLACE,  '\xe2\x88\xac',            r'$\iint$'),
        (MODE_REPLACE,  '\xe2\x8b\x85',            r'$\cdot$'),
        (MODE_REPLACE,  '\xe2\x84\x91',            r'$\Im$'),
        (MODE_REPLACE,  '\xc2\xb1',                r'$\pm$'),
        (MODE_REPLACE,  '\xcf\x80',                r'$\pi$'),
        (MODE_REPLACE,  '\xe2\x8a\x87',            r'$\supseteq$'),
        (MODE_REPLACE,  '\xce\x93',                r'$\Gamma$'),
        (MODE_REPLACE,  '\xcf\x84',                r'$\tau$'),
        (MODE_REPLACE,  '\xe2\x8a\x99',            r'$\odot$'),
        (MODE_REPLACE,  '\xe2\x86\xaa',            r'$\hookrightarrow$'),
        (MODE_REPLACE,  '\xe2\x8a\x94',            r'$\sqcup$'),
        (MODE_REPLACE,  '\xe2\x8a\xa8',            r'$\models$'),
        (MODE_REPLACE,  '\xe2\x87\x92',            r'$\Rightarrow$'),
        (MODE_REPLACE,  '\xe2\x8b\x80',            r'$\bigwedge$'),
        (MODE_REPLACE,  '\xcf\x89',                r'$\omega$'),
        (MODE_REPLACE,  '\xe2\x85\x9c',            r'$\frac38$'),
        (MODE_REPLACE,  '\xe2\x88\x9d',            r'$\propto$'),
        (MODE_REPLACE,  '\xe2\x99\xaf',            r'$\sharp$'),
        (MODE_REPLACE,  '\xce\xbc',                r'$\mu$'),
        (MODE_REPLACE,  '\xe2\x85\x97',            r'$\frac35$'),
        (MODE_REPLACE,  '\xc2\xbe',                r'$\frac34$'),
        (MODE_REPLACE,  '\xe2\x88\x8a',            r'$\in$'),
        (MODE_REPLACE,  '\xce\xb5',                r'$\varepsilon$'),
        (MODE_REPLACE,  '\xce\xb6',                r'$\zeta$'),
        (MODE_REPLACE,  '\xce\xb7',                r'$\eta$'),
        (MODE_REPLACE,  '\xe2\x89\x84',            r'$\not\simeq$'),
        (MODE_REPLACE,  '\xe2\x85\x98',            r'$\frac45$'),
        (MODE_REPLACE,  '\xe2\x88\x80',            r'$\forall$'),
        (MODE_REPLACE,  '\xc3\x97',                r'$\times$'),
        (MODE_REPLACE,  '\xe2\x80\xa6',            r'$\dots$'),
        (MODE_REPLACE,  '\xe2\x89\xa2',            r'$\not\equiv$'),
        (MODE_REPLACE,  '\xe2\x86\x96',            r'$\nwarrow$'),
        (MODE_REPLACE,  '\xe2\x88\xa7',            r'$\wedge$'),
        (MODE_REPLACE,  '\xcf\x81',                r'$\rho$'),
        (MODE_REPLACE,  '\xe2\x99\xa6',            r'$\diamondsuit$'),
        (MODE_REPLACE,  '\xe2\x88\x8d',            r'$\ni$'),
        (MODE_REPLACE,  '\xe2\x86\x92',            r'$\rightarrow$'),
        (MODE_REPLACE,  '\xce\x9e',                r'$\Xi$'),
        (MODE_REPLACE,  '\xce\xb9',                r'$\iota$'),
        (MODE_REPLACE,  '\xce\xbd',                r'$\nu$'),
        (MODE_REPLACE,  '\xc3\xb7',                r'$\div$'),
        (MODE_REPLACE,  '\xc2\xa7',                r'\S'),
        (MODE_REPLACE,  '\xcf\x91',                r'$\vartheta$'),
        (MODE_REPLACE,  '\xcf\x86',                r'$\phi$'),
        (MODE_REPLACE,  '\xe2\x8a\xa2',            r'$\vdash$'),
        (MODE_REPLACE,  '\xe2\x88\x89',            r'$\notin$'),
        (MODE_REPLACE,  '\xe2\x8a\x96',            r'$\ominus$'),
        (MODE_REPLACE,  '\xe2\x84\x8f',            r'$\hbar$'),
        (MODE_REPLACE,  '\xe2\x88\xa0',            r'$\angle$'),
        (MODE_REPLACE,  '\xe2\x89\xbb',            r'$\succ$'),
        (MODE_REPLACE,  '\xe2\x88\x9e',            r'$\infty$'),
        (MODE_REPLACE,  '\xce\xbe',                r'$\xi$'),
        (MODE_REPLACE,  '\xe2\x99\xa5',            r'$\heartsuit$'),
        (MODE_REPLACE,  '\xe2\x89\x89',            r'$\not\approx$'),
        (MODE_REPLACE,  '\xc2\xb6',                r'\P'),
        (MODE_REPLACE,  '\xe2\x87\x90',            r'$\Leftarrow$'),
        (MODE_REPLACE,  '\xe2\x88\xa8',            r'$\vee$'),
        (MODE_REPLACE,  '\xce\xb3',                r'$\gamma$'),
        (MODE_REPLACE,  '\xe2\x86\x95',            r'$\updownarrow$'),
        (MODE_REPLACE,  '\xe2\x89\x8d',            r'$\asymp$'),
        (MODE_REPLACE,  '\xe2\x88\xab',            r'$\int$'),
        (MODE_REPLACE,  '\xe2\x88\xbc',            r'$\sim$'),
        (MODE_REPLACE,  '\xe2\x99\xa7',            r'$\clubsuit$'),
        (MODE_REPLACE,  '\xe2\x85\x9e',            r'$\frac78$'),
        (MODE_REPLACE,  '\xe2\x86\xa9',            r'$\hookleftarrow$'),
        (MODE_REPLACE,  '\xe2\x86\x93',            r'$\downarrow$'),
        (MODE_REPLACE,  '\xe2\x89\xab',            r'$\gg$'),
        (MODE_REPLACE,  '\xe2\x8b\x81',            r'$\bigvee$'),
        (MODE_REPLACE,  '\xe2\x89\xad',            r'$\not\asymp$'),
        (MODE_REPLACE,  '\xe2\x87\x95',            r'$\Updownarrow$'),
        (MODE_REPLACE,  '\xce\xb4',                r'$\delta$'),
        (MODE_REPLACE,  '\xe2\x86\xbc',            r'$\leftharpoonup$'),
        (MODE_REPLACE,  '\xe2\x89\x83',            r'$\simeq$'),
        (MODE_REPLACE,  '\xe2\x88\xa5',            r'$\parallel$'),
        (MODE_REPLACE,  '\xe2\x85\x9d',            r'$\frac58$'),
        (MODE_REPLACE,  '\xe2\x85\x9a',            r'$\frac56$'),
        (MODE_REPLACE,  '\xe2\x89\x88',            r'$\approx$'),
        (MODE_REPLACE,  '\xe2\x87\x81',            r'$\rightharpoondown$'),
        (MODE_REPLACE,  '\xe2\x88\x82',            r'$\partial$'),
        (MODE_REPLACE,  '\xe2\x8a\x86',            r'$\subseteq$'),
        (MODE_REPLACE,  '\xe2\x87\x8c',            r'$\rightleftharpoons$'),
        (MODE_REPLACE,  '\xe2\x88\xa3',            r'$\mid$'),
        (MODE_REPLACE,  '\xe2\x85\x9f',            r'$\frac14$'),
        (MODE_REPLACE,  '\xe2\x86\xbd',            r'$\leftharpoondown$'),
        (MODE_REPLACE,  '\xe2\x87\x93',            r'$\Downarrow$'),
        (MODE_REPLACE,  '\xe2\x8b\x88',            r'$\bowtie$'),
        (MODE_REPLACE,  '\xe2\x99\xae',            r'$\natural$'),
        (MODE_REPLACE,  '\xe2\x8b\xae',            r'$\vdots$'),
        (MODE_REPLACE,  '\xe2\x88\x91',            r'$\sum$'),
        (MODE_REPLACE,  '\xe2\x8a\x85',            r'$\not\supset$'),
        (MODE_REPLACE,  '\xe2\x8a\x82',            r'$\subset$'),

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

        (MODE_REGEXP,   r'S\. (\d+)',             r'S.~\1'),
        (MODE_REGEXP,   r'Abs\. (\d+)',           r'Abs.~\1'),
        (MODE_REGEXP,   r'(\d+) m2',              r'\1~m2'),
        (MODE_REGEXP,   r'Art\. (\d+)',           r'Art.~\1'),
        (MODE_REGEXP,   r'SR (\d+)',              r'SR~\1'),

        # Use dashes and non breaking space in swiss currencies
        (MODE_REGEXP, r'Fr\.[ ~](\d{1,})\.(%s|-{1,2})' % DASH,
                      r'Fr.~\1.--'),


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
        (MODE_REGEXP,   r'([a-zA-Z])-,',           r'\1"~,'),
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
         r'\textbackslash '),
        ])
