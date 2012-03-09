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
        dirs = self.layout.get_template_directories()
        dirs += super(LayoutCustomization, self).get_template_directories()
        return dirs
