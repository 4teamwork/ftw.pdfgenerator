from ftw.pdfgenerator.interfaces import ITemplating
from ftw.pdfgenerator.utils import baseclasses
from zope.interface import implements
import inspect
import os


class BaseTemplating(object):
    """For details see `ftw.pdfgenerator.interfaces.ITemplating`
    """
    implements(ITemplating)

    template_directories = []

    def get_template_directories(self):
        dirs = []

        # get baseclasses, but use "self" instead of its class
        # as first item.
        classes = [self]
        classes.extend(baseclasses(self.__class__)[1:])

        for class_or_obj in classes:
            local_paths = getattr(class_or_obj, 'template_directories', None)
            cls = (inspect.isclass(class_or_obj) \
                       and class_or_obj or class_or_obj.__class__)

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

    def render_template(self, filename):
        # render_template should be implemented by a subclass, which will
        # be more specific about the template rendering engine.
        raise NotImplementedError(
            'render_template() is not implemented on BaseTemplating.')
