from ftw.pdfgenerator.exceptions import ConflictingUsePackageOrder
from ftw.pdfgenerator.interfaces import IBuilderFactory
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements, Interface


class BaseLayout(object):
    """BaseLayout is abstract base class for all layouts. Layouts adapt
    context and request.
    """

    implements(ILaTeXLayout)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._packages = []
        self._builder = None

    def use_package(self, packagename, options=None, append_options=True,
                    insert_after=None):
        """Documentation in ILaTeXLayout.use_package.
        """

        self._validate_package_name(packagename)

        if options == '':
            options = []

        elif type(options) in (str, unicode):
            options = [options]

        if insert_after is not None:
            self._validate_package_name(insert_after)
            self._use_package_circular_order_validator(
                packagename, insert_after)

        package = self._get_package(packagename)
        if package is None:
            package = {'packagename': packagename,
                       'options': options,
                       'insert_after': insert_after}
            self._packages.append(package)

        else:
            package['insert_after'] = insert_after

            if options is not None and append_options:
                for opt in options:
                    if opt not in package['options']:
                        package['options'].append(opt)

            elif options is not None and not append_options:
                package['options'] = options

    def remove_package(self, packagename):
        """Documentation in ILaTeXLayout.remove_package.
        """

        self._validate_package_name(packagename)

        if packagename == '*':
            self._packages = []

        else:
            package = self._get_package(packagename)
            if package is not None:
                self._packages.remove(package)

    def get_packages_latex(self):
        """Documentation in ILaTeXLayout.get_packages_latex.
        """
        latex = []

        for package in self._get_ordered_packages():
            pkg_latex = r'\usepackage'

            if package['options']:
                pkg_latex += '[%s]' % ', '.join(package['options'])

            pkg_latex += '{%s}\n' % package['packagename']
            latex.append(pkg_latex)

        return ''.join(latex)

    def get_builder(self):
        """Documentation in ILaTeXLayout.get_builder
        """

        if getattr(self, '_builder', None) is None:
            self._builder = getUtility(IBuilderFactory)()
        return self._builder

    def _validate_package_name(self, packagename):
        """Validates the type of a package. It should be string or unicode.
        """
        if isinstance(packagename, unicode):
            packagename = packagename.encode('utf-8')

        elif not isinstance(packagename, str):
            raise ValueError(
                'Package name should be a string, got %s (%s)' % (
                    str(packagename), type(packagename).__name__))

    def _use_package_circular_order_validator(self, packagename,
                                              dependent_packagename):
        """Test if ..
        - packagename has insert_after to itself
        - there are any insert_after loops.
        """

        if packagename == dependent_packagename:
            raise ConflictingUsePackageOrder(
                'Cannot insert "%s" after itself (insert_after="%s").' % (
                    packagename, dependent_packagename))

        path = [packagename]
        package = self._get_package(dependent_packagename)

        while package is not None:
            path.append(package['packagename'])
            if package['insert_after'] in path:
                raise ConflictingUsePackageOrder(
                    'Conflicting order: %s.' % (
                        ' after '.join(path + [package['insert_after']])))

            else:
                package = self._get_package(package['insert_after'])

        return True

    def _get_package(self, packagename):
        """Returns a package from the package configuration or None if it is
        not registered yet.
        """

        if packagename is None:
            return None

        for package in self._packages:
            if package['packagename'] == packagename:
                return package

        return None

    def _get_ordered_packages(self):
        """Returns the packages ordered by the insert_after
        definitions.
        """

        order = []

        for package in self._packages:
            if package['insert_after']:
                order.append(package['insert_after'])

        for package in self._packages:
            if package['packagename'] not in order:
                order.append(package['packagename'])

        packages = self._packages[:]
        packages.sort(lambda a, b: cmp(order.index(a['packagename']),
                                       order.index(b['packagename'])))

        return packages
