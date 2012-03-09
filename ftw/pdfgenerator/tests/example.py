from ftw.pdfgenerator.customization import LayoutCustomization
from ftw.pdfgenerator.layout.customizable import CustomizableLayout
import os.path


testdata_basedir = os.path.join(os.path.dirname(__file__),
                                'templates')
templates_bar = os.path.join(testdata_basedir, 'bar')
templates_baz = os.path.join(testdata_basedir, 'baz')


class ExampleCustomizableLayout(CustomizableLayout):
    template_directories = [templates_baz]
    template_name = 'example_layout.tex'


class ExampleCustomization(LayoutCustomization):
    template_directories = [templates_bar]
    template_name = 'example_customization.tex'
