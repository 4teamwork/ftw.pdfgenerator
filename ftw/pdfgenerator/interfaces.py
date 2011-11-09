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
