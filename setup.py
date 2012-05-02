from setuptools import setup, find_packages
import os

version = '1.1.2'

tests_require = [
    'plone.app.testing',
    'ftw.testing',
    ]

setup(name='ftw.pdfgenerator',
      version=version,
      description="A library for generating PDF representations of Plone " + \
          "objects with LaTeX.",
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],

      keywords='ftw pdf generator',
      author='4teamwork GmbH',
      author_email='mailto:info@4temamwork.ch',
      url='http://github.com/4teamwork/ftw.pdfgenerator',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
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
