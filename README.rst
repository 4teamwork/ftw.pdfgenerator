Introduction
============

``ftw.pdfgenerator`` is meant to be used for generating PDFs from structured
data using predefined `LaTeX`_ views. It is not useful for converting
full HTML pages into `LaTeX`_ / PDFs, although it is able to convert small HTML
chunks into `LaTeX`_.

.. figure:: http://onegov.ch/approved.png/image
   :align: right
   :target: http://onegov.ch/community/zertifizierte-module/ftw.pdfgenerator

   Certified: 01/2013


Requirements
============

``ftw.pdfgenerator`` requires a TeX distribution with a ``pdflatex`` executable to be installed.

These TeX distributions are recommended:

- Mac OS: `MacTeX`_
- Linux / Unix: `TeX Live`_
- Windows: `MiKTeX`_

The package is compatible with `Plone`_ 4.3 and 5.1.


Installing
==========

Add ``ftw.pdfgenerator`` to your buildout configuration:

::

  [instance]
  eggs =
    ftw.pdfgenerator

Usage
=====

The pdfgenerator uses LaTeX for generating the PDF. You need to provide a
layout and a view for your context for being able to create a PDF.


Real world examples
-------------------

Some packages using ``ftw.pdfgenerator``:

- ``ftw.meeting`` has a PDF export of the meeting minutes:
  https://github.com/4teamwork/ftw.meeting/tree/master/ftw/meeting/latex
- ``ftw.book`` produces a PDF of the book recursively:
  https://github.com/4teamwork/ftw.book/tree/master/ftw/book/latex


Defining a layout
-----------------

A layout is a multi adapter addapting ``context, request, builder``. You can
easily define a new layout using the `mako`_ templating engine
(example: ``layout.py``):

::

    >>> from example.conference.session import ISession
    >>> from ftw.pdfgenerator.interfaces import IBuilder
    >>> from ftw.pdfgenerator.interfaces import ICustomizableLayout
    >>> from ftw.pdfgenerator.layout.customizable import CustomizableLayout
    >>> from zope.component import adapts
    >>> from zope.interface import Interface
    >>> from zope.interface import implements

    >>> class SessionLayout(MakoLayoutBase):
    ...     adapts(ISession, Interface, IBuilder)
    ...     implements(ICustomizableLayout)
    ...
    ...     template_directories = ['session_templates']
    ...     template_name = 'layout.tex'
    ...
    ...     def before_render_hook(self):
    ...         self.use_babel()
    ...         self.use_package('inputenc', options='utf8')
    ...         self.use_package('fontenc', options='T1')


Register the layout with zcml (example: ``configure.zcml``):

::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser">

        <adapter factory=".layout.SessionLayout"
                 provides="ftw.pdfgenerator.interfaces.ILaTeXLayout" />

    </configure>


Create a template as defined in ``SessionLayout.template_name``
(example: ``session_templates/layout.tex``):

::

    <%block name="documentclass">
    \documentclass[a4paper,10pt]{article}
    </%block>

    <%block name="usePackages">
      ${packages}
    </%block>

    <%block name="beneathPackages">
    </%block>


    <%block name="aboveDocument">
    </%block>

    \begin{document}

    <%block name="documentTop">
      % if logo:
        ${logo}
      % endif
    </%block>

    ${content}

    <%block name="documentBottom">
    </%block>

    \end{document}


There are more methods on the layout, see the definition in
``ftw.pdfgenerator.interfaces.ILaTeXLayout``.


Defining a LaTeX view
---------------------

For every context for which a PDF is generated a LaTeX view (``ILaTeXView``)
is rendered. The view is a multi adapter adapting ``context, request, layout``.
There is a view based on the `mako`_ templating engine which can be extended
(example: ``views.py``):

::

    >>> from example.conference.session import ISession
    >>> from ftw.pdfgenerator.interfaces import ILaTeXLayout
    >>> from ftw.pdfgenerator.interfaces import ILaTeXView
    >>> from ftw.pdfgenerator.view import MakoLaTeXView
    >>> from zope.component import adapts
    >>> from zope.interface import Interface
    >>> from zope.interface import implements

    >>> class SessionLaTeXView(MakoLaTeXView):
    ...     adapts(ISession, Interface, ILaTeXLayout)
    ...     implements(ILaTeXView)
    ...
    ...     template_directories = ['session_templates']
    ...     template_name = 'view.tex'
    ...
    ...     def get_render_arguments(self):
    ...         return {'title': self.convert(self.context.Title()),
    ...                 'description': self.convert(self.context.description),
    ...                 'details': self.convert(self.context.details)}


Register the view with zcml (example: ``configure.zcml``):

::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser">

        <adapter factory=".views.SessionLaTeXView"
                 provides="ftw.pdfgenerator.interfaces.ILaTeXView" />

    </configure>


Create a template with the name defined in the class
(example: ``session_templates/view.tex``):

::

    \section*{${title}}
    % if description:
      \small ${description}
    % endif
    \normalsize ${details}


Generating a PDF
----------------

When a layout and a view for the context are registered the PDF can be
generated by simply calling the view ``@@export_pdf`` on the context.


Recursive views
---------------

When extending from ``ftw.pdfgenerator.view.RecursiveLaTeXView`` and inserting
the variable ``latex_content`` in your template, the view automatically renders
all children for which a ``ILaTeXView`` is found.


HTML to LaTeX conversion
------------------------

``ftw.pdfgenerator`` comes with a simple but powerful HTML to LaTeX converter
which is optimized for the common WYSIWYG-Editors used in Plone.

The converter can be used:

- in views, using ``self.convert(html)``
- in layouts, using ``self.get_converter().convert(html)``

It uses regular expressions for the simple conversions and python
subconverters for the more complicated conversions. The converter is heavily
customizable.

Custom subconverters
********************

Footnote
++++++++

Generate a footnote by wrapping any text in a ``span`` with the
class ``footnote``. Specify the footnote text in the ``data-footnote`` attribute.
Example:

::

    <span class="footnote" data-footnote="text in footnote">text on the page</span>

Customizable layouts
--------------------

When using multiple, independent addon packages using ``ftw.pdfgenerator``,
every package may implement a new, specific layout. This can be painful if
there is a need to customize all layouts and add a logo image for example.

For making this easier all customizable layouts can be customized with one
single adapter. This only works for layouts subclassing
``ftw.pdfgenerator.layout.customizable.CustomizableLayout``. Those layouts
need to follow certain concepts and provide inheritable blocks in the `mako`_
template. Ensure you follow the standards by subclassing and running the
tests from
``ftw.pdfgenerator.tests.test_customizable_layout.TestCustomizableLayout``.

Implementing customization adapter is very simple when customizable layouts
are used. For example we change the logo image (assume the logo is at
``custom/mylogo.png``):

::

    >>> from ftw.pdfgenerator.customization import LayoutCustomization
    >>> from ftw.pdfgenerator.interfaces import ILayoutCustomization
    >>> from zope.interface import implements
    >>>
    >>> class MyCustomization(LayoutCustomization):
    ...     implements(ILayoutCustomization)
    ...
    ...     template_directories = ['custom']
    ...     template_name = 'layout_customization.tex'
    ...
    ...     def before_render_hook(self):
    ...         self.add_raw_template_file('mylogo.png')
    ...         self.layout.use_package('graphicx')
    ...
    ...     def get_render_arguments(self, args):
    ...         args['logo'] = r'\includegraphics{mylogo.png}'
    ...         return args

It is also possible to change the template and fill predefined slots
(example: ``custom/layout_customization.tex``):

::

    <%inherit file="original_layout" />
    <%block name="documentTop">
      my branding
    </%block>

The layout customization adapter adapts ``context``, ``request`` and the original
``layout``.


Tables
======

``ftw.pdfgenerator`` is able to convert HTML-Tables to LaTeX. Since HTML and LaTeX
have completely different presentation concepts the convertion is limitted.

For getting the best results theese rules should be followed:

- Define the width of every column. The table will be streched to the text width in
  the defined proportions. Without defining the widths LaTeX is unable to insert
  newlines dynamically.

- Use relative widths (%).

- Define table headings using ``<thead>`` for long tables which may be splitted over
  multiple pages.

CSS classes:

``page-break`` (<table>)
  Force the ``longtable`` environment, allowing LaTeX to split up the table over
  multiple pages.

``no-page-break`` (<table>)
  Force the ``tabular`` environment, prohibiting LaTeX from splitting the table up
  over multiple pages. If the table is longer than the page it is truncated - content
  may be missing in this case.

``border-grid`` / ``listing`` (<table>)
  Display the table in a grid: every cell has a border on every side.

``notListed`` (<table>)
  When using a ``<caption>``, do not list the table in the list of tables.

``border-left`` (<td>, <th>)
  Display a border on the left side of the cell.

``border-right`` (<td>, <th>)
  Display a border on the right side of the cell.

``border-top`` (<td>, <th>)
  Display a border on the top side of the cell.

``border-bottom`` (<td>, <th>)
  Display a border on the bottom side of the cell.

``right`` (<td>, <th>)
  Right align the content of the cell.

``left`` (<td>, <th>)
  Left align the content of the cell.

``center`` (<td>, <th>)
  Center the content of the cell.

``indent2`` (<td>, <th>)
  Indent the content by 0.2 cm.

``indent10`` (<td>, <th>)
  Indent the content by 1 cm.

``bold`` (<td>, <th>)
  Display cell contents in bold font.

``grey`` (<td>, <th>)
  Display cell content with grey text color.

``footnotesize`` (<td>, <th>)
  Display cell content with smaller font size (``\footnotesize``).

``scriptsize`` (<td>, <th>)
  Display cell content with smaller font size (``\scriptsize``).



Links
=====

- Github: https://github.com/4teamwork/ftw.pdfgenerator
- Issues: https://github.com/4teamwork/ftw.pdfgenerator/issues
- Pypi: http://pypi.python.org/pypi/ftw.pdfgenerator
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.pdfgenerator

Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.pdfgenerator`` is licensed under GNU General Public License, version 2.


.. _LaTeX: http://www.latex-project.org/
.. _Plone: http://www.plone.org/
.. _MacTeX: http://www.tug.org/mactex/2011/
.. _Tex Live: http://www.tug.org/texlive/
.. _MiKTeX: http://www.miktex.org/
.. _mako: http://www.makotemplates.org/
