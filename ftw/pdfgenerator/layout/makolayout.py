from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.pdfgenerator.templating import MakoTemplating


class MakoLayoutBase(BaseLayout, MakoTemplating):
    """A base layout with enabled templating engine.

    When subclassing, define `template_directories` with a list of relative
    paths to your template directories.
    Define the default template by setting `template_name` to the filename.
    The default template should be in one of your template directories.
    """

    template_directories = []
    template_name = None

    def __init__(self, context, request, builder):
        BaseLayout.__init__(self, context, request, builder)
        MakoTemplating.__init__(self)

    def render(self):
        """Renders the template `template_name`, which is in one of the
        defined `template_directories`.
        """

        if self.template_name is None:
            raise ValueError('%s: `template_name` is not defined.' % (
                    self.__class__.__name__))

        return self.render_template(self.template_name,
                                    **self.get_render_arguments())

    def get_render_arguments(self):
        """Returns a dict of arguments passed to the default template.
        """
        return {}
