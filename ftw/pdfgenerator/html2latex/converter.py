from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import wrapper
from ftw.pdfgenerator.html2latex.patterns import DEFAULT_PATTERNS
from ftw.pdfgenerator.html2latex.subconverters import footnote
from ftw.pdfgenerator.html2latex.subconverters import htmlentities
from ftw.pdfgenerator.html2latex.subconverters import hyperlink
from ftw.pdfgenerator.html2latex.subconverters import listing
from ftw.pdfgenerator.html2latex.subconverters import table
from ftw.pdfgenerator.html2latex.subconverters import textformatting
from ftw.pdfgenerator.html2latex.subconverters import url
from ftw.pdfgenerator.utils import encode_htmlentities
from ftw.pdfgenerator.utils import xml2htmlentities
from random import choice
from zope.component import adapts
from zope.interface import implements, Interface
import re
import unicodedata


PLACEHOLDERS = (
    interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER,
    interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP,
    interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM,
    )

DEFAULT_PLACEHOLDER = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER

DEFAULT_SUBCONVERTERS = (
    table.TableConverter,
    listing.ListConverter,
    htmlentities.HtmlentitiesConverter,
    hyperlink.HyperlinkConverter,
    url.URLConverter,
    textformatting.Textformatting,
    footnote.FootnoteConverter,
    )


class BasePatternAware(object):
    """Base class providing some functions for handling a local patterns
    list.
    """

    default_patterns = None

    def __init__(self, patterns):
        self.patterns = patterns

    def register_patterns(self, patterns):
        for pattern in patterns:
            self._insert_custom_pattern(pattern)

    def register_subconverters(self, subconverters):
        for converter in subconverters:
            self._register_converter(converter)

    def get_subconverter_by_pattern(self, pattern):
        for ptn in self.patterns:
            if ptn[0] == interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION and \
                    ptn[1] == pattern:
                return ptn[2]

        return None

    def _insert_custom_pattern(self, pattern,
                               placeholder=DEFAULT_PLACEHOLDER,
                               replace=True):
        """Insert a custom pattern to the pattern list. If the search term
        of the pattern already exists, the existing pattern will is updated.
        """

        if isinstance(pattern[0], wrapper.CustomPatternAtPlaceholderWrapper):
            pattern = list(pattern)
            modeObject = pattern[0]
            pattern[0] = modeObject.mode
            placeholder = modeObject.placeholder
            replace = False

        found = False
        if replace:
            for i in range(0, len(self.patterns)):
                if self.patterns[i] in PLACEHOLDERS:
                    continue

                if pattern[1] == self.patterns[i][1]:
                    # overwrite existing pattern
                    self.patterns[i] = pattern
                    found = True

        if not found:
            # pattern will be inserted at the configured placeholder
            self.patterns.insert(self.patterns.index(placeholder), pattern)

    def _register_converter(self, converter_class):
        """
        Generates a pattern with a SubConverter class.
        """
        self._insert_custom_pattern(
            pattern=(interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION,
                     converter_class.pattern,
                     converter_class),
            placeholder=converter_class.placeholder)


class HTML2LatexConverter(BasePatternAware):
    implements(interfaces.IHTML2LaTeXConverter)
    adapts(Interface, Interface, interfaces.ILaTeXLayout)

    default_patterns = DEFAULT_PATTERNS

    def __init__(self, context, request, layout):
        self.context = context
        self.request = request
        self.layout = layout

        super(HTML2LatexConverter, self).__init__(
            patterns=self.__class__.default_patterns[:])
        self.register_subconverters(self.get_default_subconverters())

    def get_default_subconverters(self):
        return DEFAULT_SUBCONVERTERS

    def convert(self, html, custom_patterns=None, custom_subconverters=None,
                trim=True):

        runner = HTML2LatexConvertRunner(
            converter=self,
            patterns=self.patterns[:],
            html=html,
            trim=trim)

        if custom_patterns is not None:
            runner.register_patterns(custom_patterns)

        if custom_subconverters is not None:
            runner.register_subconverters(custom_subconverters)

        return runner.runner_convert()

    def convert_plain(self, text, **kwargs):
        html = encode_htmlentities(text)
        return self.convert(html, **kwargs)

    def quoted_umlauts(self, text):
        if isinstance(text, str):
            text = text.decode('utf-8')

        text = unicodedata.normalize('NFD', text)
        text = re.sub(ur'(.)\u0308', '"\g<1>', text, re.UNICODE)
        text = unicodedata.normalize('NFC', text)

        return text.encode('utf-8')


class HTML2LatexConvertRunner(BasePatternAware):
    implements(interfaces.IHTML2LaTeXConvertRunner)

    def __init__(self, converter, patterns, html, trim=True):
        """
        Creates a instance for converting html to latex.
        Attention: this instance should only be used ONCE for converting,
        because of the lockers and html instance attributes.
        You can use convert() on this instance, it will be proxied to the
        HTML2LatexConverter instance.
        """
        BasePatternAware.__init__(self, patterns)

        if not interfaces.IHTML2LaTeXConverter.providedBy(converter):
            raise ValueError(
                'converter should by a IHTML2LaTeXConverter')
        else:
            self.converter = converter

        self.lockers = {}
        self.html = ''
        self.patterns = patterns
        self._convert_started = False

        # we use utf8
        if type(html) == unicode:
            html = html.encode('utf8')

        # we do not use xmlentities, but htmlentities
        self.html = xml2htmlentities(html)

        # trim ?
        if trim:
            self.html = self.html.strip()

    def lock_chars(self, startPos, endPos):
        """
        Locks a specific part of the html. Other Patterns will not match this
        part of html anymore. This is generally used by SubConverters, if
        they replaced the HTML with latex.
        See replaceAndLock()
        """
        # generate new id with same length
        id_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        stop = False
        id_ = ''
        length = endPos - startPos

        # use keys with a length of at least 10 chars for making them
        # unique enought. otherwise the key generation may loop.
        if length < 10:
            length = 10

        while not stop:
            id_ = ''.join([choice(id_chars) for _i in range(length)])
            if id_ not in self.lockers.keys() and id_ not in self.html:
                stop = True

        # lock html (replace with id)
        self.lockers[id_] = self.html[startPos:endPos]
        self.html = self.html[:startPos] + id_ + self.html[endPos:]
        return id_

    def replace(self, startPos, endPos, text):
        """
        Replaces a specific part in the HTML with [text] (e.g. latex code).
        The new text will be replaced by further patterns! Please use
        lockChars() or replaceAndLock() if you don't want further patterns
        to match and replace
        """
        self.html = self.html[:startPos] + text + self.html[endPos:]
        return self.html

    def replace_and_lock(self, startPos, endPos, text):
        """
        Replaces a spefic part in the HTML with [text] and locks it with
        lockChars() after replacing.
        See replace() and lockChars()
        """
        newEndPos = startPos + len(text)
        # replace html
        self.replace(startPos, endPos, text)
        # lock chars
        return self.lock_chars(startPos, newEndPos)

    def _unlock_chars(self):
        """
        Unlocks previously locked HTML (see lockChars()). This method is
        automatically called by _convert() after converting HTML to Latex.
        """
        html_before = self.html

        for id_ in self.lockers.keys():
            value = self.lockers[id_]
            self.html = self.html.replace(id_, value)

        if html_before != self.html:
            self._unlock_chars()

    def convert(self, html, custom_patterns=None, custom_subconverters=None,
                trim=True):
        """Convert a sub-part of the HTML. This initializes another
        runner and converts returns the results. This is necessary for
        converting HTML parts matched in subconverters.
        """

        runner = HTML2LatexConvertRunner(
            converter=self.converter,
            patterns=self.patterns[:],
            html=html,
            trim=trim)

        if custom_patterns is not None:
            runner.register_patterns(custom_patterns)

        if custom_subconverters is not None:
            runner.register_subconverters(custom_subconverters)

        return runner.runner_convert()

    def runner_convert(self):
        """This method does the actual converting. It should never by called
        directly, but through HTML2LatexConverter.convert()
        """

        if self._convert_started:
            raise RuntimeError(
                'runner_convert() should not be called twice!')
        else:
            self._convert_started = True

        for pattern in self.patterns:
            if pattern in PLACEHOLDERS:
                continue

            mode = pattern[0]
            search = pattern[1]
            replace = pattern[2]
            modifiers = ()

            if len(pattern) == 4:
                modifiers = pattern[3]

            # replace
            if mode == interfaces.HTML2LATEX_MODE_REPLACE:
                self.html = self.html.replace(search, replace)

            # regexp replace
            elif mode == interfaces.HTML2LATEX_MODE_REGEXP:
                self._replace_regexp(search, replace, modifiers)

            # regexp function
            elif mode == interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION:
                self._replace_regexp_function(search, replace)

        self._unlock_chars()
        return self.html

    def quoted_umlauts(self, text):
        return self.converter.quoted_umlauts(text)

    def _replace_regexp(self, search, replace, modifiers):
        xpr = re.compile(search, re.DOTALL)
        previous_html = ''
        if interfaces.HTML2LATEX_REPEAT_MODIFIER in modifiers:
            previous_html = ''

            while previous_html != self.html:
                previous_html = self.html
                self.html = xpr.sub(replace, self.html)

        else:
            self.html = xpr.sub(replace, self.html)

    def _replace_regexp_function(self, search, replace_fun):
        xpr = re.compile(search, re.DOTALL)
        skipStartPos = []
        startLimit = 0
        search = True

        while search:
            previous_html = self.html
            match = xpr.search(self.html, startLimit)

            if match and match.start() not in skipStartPos:
                skipStartPos.append(match.start())
                obj = replace_fun(self, match, self.html)
                if callable(obj):
                    obj()

            elif match and match.start() in skipStartPos:
                startLimit = match.start() + 1

            else:
                search = False

            if self.html != previous_html:
                skipStartPos = []
                startLimit = 0
