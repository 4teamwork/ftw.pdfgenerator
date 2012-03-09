from ftw.pdfgenerator.interfaces import ICustomizableLayout
from ftw.pdfgenerator.interfaces import ILayoutCustomization
from ftw.pdfgenerator.templating import MakoTemplating
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements


class LayoutCustomization(MakoTemplating):
    """For documententation see ``ILayoutCustomization``.
    When subclassing, inherit and run the testcase
    ``ftw.pdfgenerator.tests.test_customization.TestLayoutCustomization``.
    """

    implements(ILayoutCustomization)
    adapts(Interface, Interface, ICustomizableLayout)

    template_directories = []
    template_name = None

    def __init__(self, context, request, layout):
        super(LayoutCustomization, self).__init__()
        self.context = context
        self.request = request
        self.layout = layout

    def before_render_hook(self):
        pass

    def get_render_arguments(self, args):
        return args

    def get_template_directories(self):
        dirs = super(LayoutCustomization, self).get_template_directories()
        dirs += self.layout.get_template_directories()
        return dirs

    @property
    def template_lookup(self):
        if getattr(self, '_mako_template_lookup', None) is None:
            lookup = super(LayoutCustomization, self).template_lookup
            lookup.put_template(
                'original_layout',
                lookup.get_template(self.layout.template_name))

        return super(LayoutCustomization, self).template_lookup

    def add_raw_template_file(self, name):
        """Adds the contents of a file to the builder without parsing it.
        """
        self.layout.builder.add_file(name, data=self.get_raw_template(name))
