from ftw.pdfgenerator.interfaces import ITemplating
from ftw.pdfgenerator.utils import baseclasses
from mako.lookup import TemplateLookup
from zope.interface import implements
import inspect
import os
import posixpath
import re


class BaseTemplating(object):
    """For details see `ftw.pdfgenerator.interfaces.ITemplating`
    """
    implements(ITemplating)

    template_directories = []

    def get_template_directories(self):
        dirs = []

        if self.__class__.__module__ == 'Products.Five.metaclass':
            # self is a browser view which is based on a metaclass.
            # We need to get rid of the metaclass so that we know
            # where the class is defined.
            classes = baseclasses(self.__class__)[1:]
        else:
            classes = baseclasses(self.__class__)

        for cls in classes:
            local_paths = getattr(cls, 'template_directories', None)

            if local_paths is None:
                continue

            elif not hasattr(local_paths, '__iter__'):
                classname = cls.__name__
                raise ValueError(classname + '.template_directories '
                                 'should be a list or None.')

            for path in reversed(local_paths):
                if not os.path.isabs(path):
                    path = os.path.join(
                        os.path.dirname(inspect.getsourcefile(cls)), path)

                # Make an acces for checking if it exists. This will raise
                # an OSError if the path does not exist.
                os.listdir(path)

                if path not in dirs:
                    dirs.append(path)

        return dirs

    def get_template(self, filename):
        for directory in self.get_template_directories():
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return open(path, 'rb').read()

        return None

    def render_template(self, filename, **kwargs):
        # render_template should be implemented by a subclass, which will
        # be more specific about the template rendering engine.
        raise NotImplementedError(
            'render_template() is not implemented on BaseTemplating.')


class MakoTemplating(BaseTemplating):
    """Provides a mako templating integration.
    """

    def __init__(self):
        super(MakoTemplating, self).__init__()
        self._mako_template_lookup = None

    @property
    def template_lookup(self):
        """Returns a mako TemplateLookup object, which has all current
        template directories configured.
        """

        if getattr(self, '_mako_template_lookup', None) is None:
            dirs = self.get_template_directories()
            self._mako_template_lookup = TemplateLookup(
                directories=dirs,
                default_filters=['decode.utf8'],
                input_encoding='utf-8')

        return self._mako_template_lookup

    def render_template(self, filename, **kwargs):
        """Renders a mako template. Additional rendering arguments may be
        passed as keyword arguments as if the mako template was called
        directly.
        """

        template = self.template_lookup.get_template(filename)
        kwargs['view'] = self
        return template.render(**kwargs)

    def get_raw_template(self, name):
        """Returns the contents of a template file without parsing it.
        """
        uri = re.sub(r'^\/+', '', name)
        for dir_ in self.template_lookup.directories:
            srcfile = posixpath.normpath(posixpath.join(dir_, uri))
            if os.path.isfile(srcfile):
                return open(srcfile).read()
        return None
