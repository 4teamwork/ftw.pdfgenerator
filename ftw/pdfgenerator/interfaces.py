# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface, Attribute


DEBUG_MODE_SESSION_KEY = 'pdfgenerator-debug-mode'


class IPDFAssembler(Interface):
    """The PDF assembler assembles the PDF. It puts together all LaTeX parts,
    merges them with the layout and builds it with the builder.
    """

    def __init__(context, request):
        """The PDF assembler is a multi-adapter adapting context and request.
        """

    def build_pdf(layout=None, builder=None, request=None):
        """Builds the LaTeX and converts it to a PDF. The pdf data is
        returned as string. If `request` is passed, it will send it writes
        it to the response using the ID of the current context as filename
        base.

        Arguments:
        layout -- Use a custom layout for this build.
        request -- Write the resulting PDF to the request.
        """

    def build_latex(layout=None, builder=None, request=None):
        """Builds the LaTeX and returns it as string without converting it to
        a PDF.

        Arguments:
        layout -- Use a custom layout for this build.
        request -- Not relevant here, but the signature should match
        `build_pdf`.
        """

    def build_zip(layout=None, builder=None, request=None):
        """Builds the LaTeX and converts it to a PDF like `build_pdf` does,
        but returns a ZIP bundle of all used files (.tex-files, images,
        resources, the resulting .pdf, etc). If `request` is passed,
        it will write the file directly to the request.

        Arguments:
        layout -- Use a custom layout for this build.
        request -- Write the resulting ZIP to the request.
        """


class IConfig(Interface):
    """PDFGenerator configuration utility.
    """

    remove_build_directory = Attribute(
        'Boolean attribute. If `True`, the build directory will be removed '
        'after finishing the build.')

    def get_build_directory():
        """Returns the path to a directory, where the PDF should be built.
        This method should not return the same path twice. The directory
        should exist and be writeable.
        """


class IBuilderFactory(Interface):
    """Factory creating a new IBuilder.
    """


class IBuilder(Interface):
    """Converts LaTeX to PDF using `pdflatex`.
    """

    def add_file(filename, data):
        """Adds a file to the build directory.
        """

    def build(latex):
        """Builds and returns the PDF.
        """

    def build_zip(latex):
        """Builds the PDF and returns the a ZIP bundle, containing the build
        directory.
        """

    def cleanup():
        """Cleanup the temporary directory. This is necessary when the
        builder was requested but nothing was built.
        """


class ILaTeXLayout(Interface):
    """A LaTeX layout defines the head of the LaTeX file and puts the
    parts of the LaTeX code together. It manages the also the packages.

    ILaTeXLayout is a multi-adapter of context, request and builder.
    """

    def __init__(context, request, builder):
        """ILaTeXLayout adapts context, request and the builder.
        """

    def use_package(packagename, options=None, append_options=True,
                    insert_after=None):
        """This will add a `\usepackage{packagname}[options]'
        command to the LaTeX code, where the options part is optionally.

        Arguments:
        `packagename` -- Name of the LaTeX package.
        `options` -- LaTeX `\usepackage` options.
        `append_options` -- If `True`, `options` will be added to existing
        options, seperated by comma (defaults to `True`). Duplicate options
        will be removed.
        `insert_after` -- Inserts the package after the package with the
        name `insert_after'.
        """

    def remove_package(packagename):
        """Removes a single package. When `packagename` is '*', all packages
        are removed.

        Arguments:
        `packagename` -- Name of the LaTeX package.
        """

    def get_packages_latex():
        """Returns the LaTeX code of the `\usepackage` commands.
        """

    def use_babel(options=None, append_options=False, **kwargs):
        """Use the "babel" package. This adds a use_package with the
        language option for this context.
        By default, the language option is guessed from the context (if
        linguaplone is used) or from the preferred language of the user.
        This behavior can be changed by passing the `options` argument,
        with either the language option as string or a list of language
        options, where the first option is the primary language.
        """

    def render_latex(content_latex):
        """Renders the layout with the `content_latex` embedded.

        Arguments:
        `content_latex` -- LaTeX code of the rendered view.
        """

    def get_builder():
        """Returns the builder instance.
        """

    def get_converter():
        """Returns the current instance of the IHTML2LaTeXConverter.
        """

    def get_views_for(obj):
        """Returns a list of `ILaTeXView`s for `obj`. If no views are
        registered for the passed object it will return an empty list.
        """

    def render_latex_for(obj):
        """Renders the LaTeX views registered for `obj`.
        """


class ICustomizableLayout(ILaTeXLayout):
    """Marks a mako layout as customizable. The template of a customizable
    layout has to insert ``${logo}`` somewhere, which may contain a
    ``\includegraphics{}`` command.
    It also has to define some mako blocks which can be filled by a
    layout customization adapter:

    ``documentclass``: contains the document class definition
    ``usePackages``: contains the use_packages statements (usually
    contains ${packages})
    ``beneathPackages``: empty block beneath ``usePackages```
    ``aboveDocument``: empty block right before ``\begin{document)``
    ``documentTop``: empty block right after ``\begin{document}``
    ``documentBottom``: empty block at the end of the document,
    before ``\end{document}``
    """


class ITemplating(Interface):
    """The `ITemplating` interface is used for mixin classes enabling
    template support for any inheriting class.

    It makes it possible to define template directories on every inheriting
    class, so that the templates easily can extend or include each other.

    The `template_directories` list can be set on every inheriting class. If
    the superclass also has set it, it will also be respected when searching
    a template. When searching a template it will walk up the superclasses
    and takes the first template found. This makes it possible to override
    tempaltes defined in superclasses.
    """

    template_directories = Attribute(
        'A list of paths to template directories. The paths in the back are '
        'dominant. The paths may be absolute or relative to the path of the '
        'module where the class is defined.')

    def get_template_directories():
        """Returns a list of absolute paths to template directories.
        The paths in front are dominant: if there are multiple templates
        with the same path in different directories, the ones from the
        directories in front of the list will be taken.
        """

    def get_template(filename):
        """Returns the contents of a template with the name `filename`
        which is found in one of the directories of
        `get_template_directories` or returns `None` if no template with
        such name was found.
        """

    def render_template(filename, **kwargs):
        """Renders a template and returns the result.
        """


class ILayoutCustomization(ITemplating):
    """Adapter interface for multi adapters adapting
    ``context, request, layout``. This adapter allows us to customize
    multiple distinct layouts defined by multiple packages without
    customizing every single layout.

    The adapter implements the ``ITemplating`` interface and has to inherit
    from ``original_layout``, which is an alias for the original layout
    template name.
    """

    def before_render_hook():
        """This hook is called before rendering the template and can be used
        for defining additional ``self.use_package()`` statements or other
        customizations.
        """

    def get_render_arguments(args):
        """With this method it is possible to add additional arguments passed
        to the template. The ``args`` argument is a dict containing the
        template arguments defined by the original layout template and my be
        extended. The method should return the modified ``args`` dict.
        """


class ILaTeXView(Interface):
    """A LaTeX view is an adapter of context, request and layout. It renders
    the object in LaTeX.
    """

    def __init__(context, request, layout):
        """A LaTeX view is a multi-adapter of context, request and layout.
        """

    def render():
        """Renders the object in LaTeX and returns the LaTeX code as string.
        """

    def convert(*args, **kwargs):
        """Convert HTML to LaTeX using the IHTML2LaTeXConverter.
        See the IHTML2LaTeXConverter.convert documentation.
        """

    def convert_plain(*args, **kwargs):
        """Convert HTML to LaTeX using the IHTML2LaTeXConverter.
        See the IHTML2LaTeXConverter.convert_plain documentation.
        """


class IRecursiveLaTeXView(ILaTeXView):
    """A recursive LaTeX view walks down the tree and renders subcontent of
    a folder too.
    """


class IHTML2LaTeXConverter(Interface):
    """A `IHTML2LatexConverter` converts HTML to LaTeX. It is a multi adapter
    of (context, request, layout, builder).

    The converter runs a list of replace statements on the HTML. Each
    statement can be either a direct replacement, a regular expression or
    a subconverter.
    """

    default_patterns = Attribute('List of default patterns.')

    def __init__(context, request, layout):
        """
        """

    def get_default_subconverters():
        """Returns the default list of subconverters.
        """

    def register_patterns(patterns):
        """Registers a list of custom patterns.
        """

    def register_subconverters(subconverters):
        """Registers a list of converters.
        """

    def get_subconverter_by_pattern(pattern):
        """Returns the currently active subconverter for the passed pattern.
        """

    def convert(html, custom_patterns=None, custom_subconverters=None,
                trim=True):
        """Converts HTML to LaTeX.

        Arguments:
        html -- HTML as string.
        custom_map -- A list of custom patterns.
        custom_converters -- A list of custom subconverters, which will be
        merged into the custom_map.
        trim -- Strip the HTML before converting to LaTeX. (Default: `True`).
        """

    def quoted_umlauts(text):
        """Replaces umlauts in text with the LaTeX's quotet umlaut notation.
        E.g. "a "o "u

        Arguments:
        text -- Text to convert
        """

    def convert_plain(text, **kwargs):
        """Converts a text to HTML and then to LaTeX.

        Arguments:
        text -- The text to convert as string.
        **kwargs -- Arguments passed to `convert()`.
        """


class IHTML2LaTeXConvertRunner(Interface):
    """A kind of fork of `IHTML2LatexConverter`, which does the actual
    converting. It is passed to sub converters, so that the can update the
    current HTML / LaTeX code.
    """

    def __init__(converter, patterns, html, trim=True):
        """
        """

    def lock_chars(startPos, endPos):
        """
        Locks a specific part of the html. Other Patterns will not match this
        part of html anymore. This is generally used by SubConverters, if
        they replaced the HTML with latex.
        See replaceAndLock()
        """

    def replace(startPos, endPos, text):
        """
        Replaces a specific part in the HTML with [text] (e.g. latex code).
        The new text will be replaced by further patterns! Please use
        lockChars() or replaceAndLock() if you don't want further patterns
        to match and replace
        """

    def replace_and_lock(startPos, endPos, text):
        """
        Replaces a spefic part in the HTML with [text] and locks it with
        lockChars() after replacing.
        See replace() and lockChars()
        """

    def convert(html, custom_patterns=None, custom_subconverters=None,
                trim=True):
        """Convert a sub-part of the HTML. This initializes another
        runner and converts returns the results. This is necessary for
        converting HTML parts matched in subconverters.
        """

    def runner_convert():
        """This method does the actual converting. It should never by called
        directly, but through HTML2LatexConverter.convert()
        """

    def quoted_umlauts(text):
        """Replaces umlauts in text with the LaTeX's quotet umlaut notation.
        E.g. "a "o "u

        Arguments:
        text -- Text to convert
        """


class ISubConverter(Interface):
    """A SubConverter converts specific, advanced parts of a HTML to LaTeX.
    """

    pattern = Attribute('Regex pattern as string.')
    placeholder = Attribute(
        'The subconverter will be registered at the point of the '
        'placeholder in the patterns list.')

    def __init__(converter, match, html):
        """
        Arguments:
        converter -- Reference to the IHTML2LaTeXConverter
        match -- regex match object
        html -- full html
        """

    def __call__():
        """Initiates the converting.
        """

    def get_html():
        """Return the matched html.
        """

    def replace_and_lock(latex):
        """Sends the `latex` back to the main converter and locks it so that
        no subsequent patterns will match / replace.
        The original match area will be replaced by `latex`.
        """

    def replace(latex):
        """Sends the `latex` back to the main converter, the original match
        area will be replaced.
        Subsequent patterns may match the latex.
        """


HTML2LATEX_MODE_REPLACE = 'replace'
HTML2LATEX_MODE_REGEXP = 'regexp'
HTML2LATEX_MODE_REGEXP_FUNCTION = 'regexp function'

HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER = 'placeholder for custom patterns'
HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP = \
    'top placeholder for custom patterns'
HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM = \
    'bottom placeholder for custom patterns'

HTML2LATEX_REPEAT_MODIFIER = 'repeat pattern'
HTML2LATEX_PREVENT_CHARACTER = chr(7)
