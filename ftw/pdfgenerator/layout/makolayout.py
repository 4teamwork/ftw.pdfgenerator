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

    def render_latex(self, content_latex):
        """Renders the template `template_name`, which is in one of the
        defined `template_directories`.
        """

        if self.template_name is None:
            raise ValueError('%s: `template_name` is not defined.' % (
                    self.__class__.__name__))

        self.before_render_hook()

        args = self.get_render_arguments()
        args['content'] = content_latex
        args['packages'] = self.get_packages_latex()

        return self.render_layout_template(args)

    def render_layout_template(self, args):
        return self.render_template(self.template_name, **args)

    def get_render_arguments(self):
        """Returns a dict of arguments passed to the default template.
        """
        return {}

    def before_render_hook(self):
        """This method is called before rendering and may register
        required packages (`use_package`).
        """
        pass

    def add_raw_template_file(self, name):
        """Adds the contents of a file to the builder without parsing it.
        """
        self.builder.add_file(name, data=self.get_raw_template(name))
