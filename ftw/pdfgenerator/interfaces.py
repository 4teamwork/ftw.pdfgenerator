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
