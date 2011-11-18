

class BuildTerminated(Exception):
    """Raised when trying to run actions (such as add_file) on a closed
    builder.
    """


class PDFBuildFailed(Exception):
    """Raised when pdflatex could not build the PDF for some reason.
    The "message" of the exception should be the stdout of the build
    process.
    """


class ConflictingUsePackageOrder(Exception):
    """The package order is conflicting in the `ILaTeXLayout`.
    """
