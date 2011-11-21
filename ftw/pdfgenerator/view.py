from ftw.pdfgenerator.interfaces import ILaTeXLayout, ILaTeXView
from ftw.pdfgenerator.templating import MakoTemplating
from zope.interface import implements, Interface
from zope.component import adapts


class MakoLaTeXView(MakoTemplating):
    """A LaTeXView with Mako templating enabled.
    """

    implements(ILaTeXView)
    adapts(Interface, Interface, ILaTeXLayout)

    template_directories = []
    template_name = None

    def __init__(self, context, request, layout):
        self.context = context
        self.request = request
        self.layout = layout

    def register_template_file(self, filename, render=False, **kwargs):
        """Registers a file from the template directories to the builder.
        This copies the file in the directory where the latex will be built.

        Arguments:
        filename -- Name of the file stored in a known template directory.
        render -- Render the template first (default: `False`).
        **kwargs -- Arguments passed to the renderer, if render is `True`.
        """

        if render:
            data = self.render_template(filename, **kwargs)

        else:
            data = self.get_template(filename)

        self.layout.get_builder().add_file(filename, data)

    def get_render_arguments(self):
        """The returned dict of this function will be passed to the template
        when its rendered. This makes it easy to pass additional values.
        """
        return {}

    def render(self):
        """By default, the template `template_name`, which is in one of
        the directories defined in `template_directories`, is rendered
        and returned.
        """

        if self.template_name is None:
            raise ValueError('%s: `template_name` is not defined.' % (
                    self.__class__.__name__))

        return self.render_template(self.template_name,
                                    **self.get_render_arguments())