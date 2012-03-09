from ftw.pdfgenerator.interfaces import ICustomizableLayout
from ftw.pdfgenerator.interfaces import ILayoutCustomization
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from zope.component import queryMultiAdapter
from zope.interface import implements


class CustomizableLayout(MakoLayoutBase):
    """For documententation see ``ICustomizableLayout``.
    When subclassing, inherit and run the testcase
    ``ftw.pdfgenerator.tests.test_customizable_layout.TestCustomizableLayout``
    """

    implements(ICustomizableLayout)

    def render_layout_template(self, args):
        customization = queryMultiAdapter(
            (self.context, self.request, self), ILayoutCustomization)

        if customization is None:
            return self.render_template(self.template_name, **args)

        customization.before_render_hook()

        # we need to re-generate the packages, since the before_render_hook
        # may have changed the packages.
        args['packages'] = self.get_packages_latex()
        args = customization.get_render_arguments(args)

        if not customization.template_name:
            return self.render_template(self.template_name, **args)
        else:
            return customization.render_template(
                customization.template_name, **args)
