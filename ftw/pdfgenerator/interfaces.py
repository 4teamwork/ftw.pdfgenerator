# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface, Attribute


class IConfig(Interface):
    """PDFGenerator configuration utility.
    """

    remove_build_directory = Attribute(
        'Boolean attribute. If `True`, the build directory will be removed '
        'after finishing the build.')

    def get_build_directory():
        """Returns the path to a directory, where the PDF should be built. This
        method should not return the same path twice. The directory should
        exist and be writeable.
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


class ILaTeXLayout(Interface):
    """A LaTeX layout defines the head of the LaTeX file and puts the
    parts of the LaTeX code together. It manages the also the packages.

    ILaTeXLayout is a multi-adapter of context and request.
    """

    def __init__(context, request):
        """ILaTeXLayout is adapts context and request.
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

    def get_builder():
        """Returns the builder instance. This should be lazy and create the
        builder on first use.
        """


class ITemplating(Interface):
    """The `ITemplating` interface is used for mixin classes enabling template
    support for any inheriting class.

    It makes it possible to define template directories on every inheriting
    class, so that the templates easily can extend or include each other.

    The `template_directories` list can be set on every inheriting class. If
    the superclass also has set it, it will also be respected when searching a
    template. When searching a template it will walk up the superclasses and
    takes the first template found. This makes it possible to override
    tempaltes defined in superclasses.
    """

    template_directories = Attribute(
        'A list of paths to template directories. The paths in the back are '
        'dominant. The paths may be absolute or relative to the path of the '
        'module where the class is defined.')

    def get_template_directories():
        """Returns a list of absolute paths to template directories. The paths
        in front are dominant: if there are multiple templates with the same
        path in different directories, the ones from the directories in front
        of the list will be taken.
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
