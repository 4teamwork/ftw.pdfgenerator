from setuptools import setup, find_packages
import os

version = '1.0'

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
        # -*- Extra requirements: -*-
        ],

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
