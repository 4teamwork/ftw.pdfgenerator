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
