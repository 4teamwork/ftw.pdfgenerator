from setuptools import setup, find_packages
import os

version = '1.6.5'

tests_require = [
    'unittest2',
    'mocker',
    'plone.mocktestcase',
    'ftw.testing',
    'plone.testing',

    'zope.annotation',
    'zope.component',
    'zope.i18n',
    'zope.interface',
    'zope.publisher',
    ]

setup(name='ftw.pdfgenerator',
      version=version,
      description="A library for generating PDF representations of Plone " + \
          "objects with LaTeX.",
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      classifiers=[
        "Environment :: Web Environment",
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw pdf generator',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.pdfgenerator',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',

        # Zope
        'Zope2',
        'zope.annotation',
        'zope.component',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',

        # Plone
        'Products.Archetypes',
        'Products.CMFCore',

        'Mako',
        'BeautifulSoup!=4.0b',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
