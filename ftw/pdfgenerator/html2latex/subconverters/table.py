from BeautifulSoup import BeautifulSoup
from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.html2latex import wrapper
from ftw.pdfgenerator.utils import html2xmlentities
from xml.dom import minidom
import re


_marker = object()


MODE_REPLACE = interfaces.HTML2LATEX_MODE_REPLACE
MODE_REGEXP = interfaces.HTML2LATEX_MODE_REGEXP
PLACEHOLDER_BOTTOM = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM
PREVENT_CHARACTER = interfaces.HTML2LATEX_PREVENT_CHARACTER
LONGTABLE_ROWS_THRESHOLD = 15


class TableConverter(subconverter.SubConverter):
    """The TableConverter converts <table>-Tags to latex.
    """

    pattern = r'<table(.*?)>(.*?)</table>'

    def __init__(self, *args, **kwargs):
        super(TableConverter, self).__init__(*args, **kwargs)
        self.columnAmount = 0
        self.LatexColumn = LatexColumn
        self.dom = None
        self.rows = []
        self.columns = []
        self._css_classes = None
        self._environment = None

    def __call__(self):
        html = self.get_html()
        # cleanup html with BeautifulSoup

        html = str(BeautifulSoup(html))
        # minidom hates htmlentities, but loves xmlentities -.-

        html = html2xmlentities(html)

        # parse DOM
        self.dom = minidom.parseString(html)
        self.parse_dom()

        # render table
        latex = self.render()

        # replace with latex
        self.replace_and_lock(latex)

        # register packages
        if self.environment == 'longtable':
            self.converter.converter.layout.use_package('longtable')
        self.converter.converter.layout.use_package('multirow')
        self.converter.converter.layout.use_package('multicol')

    @property
    def environment(self):
        if getattr(self, '_environment', None) is None:
            if 'page-break' in self.get_css_classes():
                self._environment = 'longtable'
            elif 'no-page-break' in self.get_css_classes():
                self._environment = 'tabular'
            elif len(self.rows) > LONGTABLE_ROWS_THRESHOLD:
                self._environment = 'longtable'
            else:
                self._environment = 'tabular'

        return self._environment

    def get_css_classes(self):
        if self._css_classes is None:
            self._css_classes = []
            domTable = self.dom.getElementsByTagName('table')[0]
            classes = domTable.getAttribute('class').strip()
            self._css_classes = classes.split(' ')
        return self._css_classes

    def get_border(self):
        domTable = self.dom.getElementsByTagName('table')[0]

        border = domTable.hasAttribute('border')
        if border and int(border) > 0:
            return True

        elif 'border-grid' in self.get_css_classes() or \
                'listing' in self.get_css_classes():
            return True

        else:
            return False

    def render(self):
        latex = '\\begin{%s}{%s}\n' % (
            self.environment, self.get_table_format())
        caption_command, insert_caption_at_top = self.render_caption()
        if caption_command and insert_caption_at_top:
            latex += caption_command

        latex += self.render_rows()
        if caption_command and not insert_caption_at_top:
            latex += caption_command
        latex += '\\end{%s}\n' % self.environment
        return latex

    def render_rows(self):
        head_rows = []
        body_rows = []

        for row in self.rows:
            rowLatex = row.render()
            if row.contains_head_cells():
                head_rows.append(rowLatex)
            else:
                body_rows.append(rowLatex)

        head_latex = ''
        if len(head_rows) > 0:
            head_latex = ''.join(head_rows)
        body_latex = ''

        if len(body_rows) > 0:
            body_latex = ''.join(body_rows)

        if len(head_rows) > 0 and self.environment == 'longtable':
            return '%s\\endhead\n%s' % (head_latex, body_latex)
        elif len(head_rows) > 0:
            return head_latex + body_latex
        else:
            return body_latex

    def render_caption(self):
        """
        If the HTML-Table contains a <caption>-Tag, this method
        returns the LaTeX-Command for the caption and weather the
        command should be inserted at the top or at the bottom of
        the table.

        Example:
        caption_command, insert_at_top = self.render_caption()
        caption_command : \caption{My Table}
        insert_at_top : True

        If there is no command, it will return
        None, False
        """

        caption = self.dom.getElementsByTagName('caption')
        if len(caption) > 0:
            caption_tag = caption[0]
            siblings = caption_tag.parentNode.childNodes
            insert_at_top = len(siblings) / float(2) > (
                siblings.index(caption_tag) + 1)

            content = ''.join([child.toxml() for child
                               in caption[0].childNodes])

            content = content.encode('utf8')
            latexContent = self.converter.convert(content)

            return '\\caption%s{%s} \\\\\n' % (
                ('notListed' in self.get_css_classes() and '*' or ''),
                latexContent,
                ), insert_at_top
        else:
            return None, False

    def get_table_format(self):
        column_format = []
        for col in self.columns:
            column_format.append(col.get_format())
        return ''.join(column_format)

    def parse_dom(self):
        # create colum objects
        dom_col_list = self.dom.getElementsByTagName('col')
        amount = self.get_amount_of_columns()
        amount = amount > len(dom_col_list) and amount or len(dom_col_list)

        for c in range(amount):
            col = self.create_latex_column()
            if len(dom_col_list) > c:
                col.set_dom_col(dom_col_list[c])
            self.columns.append(col)

        # create rows / cells
        multi_row_cache = {
            # columnIndex : [Cell, DecrementingRowspan],
            }

        for domTr in self.dom.getElementsByTagName('tr'):
            self._parse_tr_dom(domTr, multi_row_cache)

    def _parse_tr_dom(self, domTr, multi_row_cache):
        row = self.create_latex_row(domTr=domTr)
        self.rows.append(row)

        # .. cells
        cells = domTr.getElementsByTagName('th')
        cells += domTr.getElementsByTagName('td')

        # sorting
        cells.sort(lambda a, b: cmp(a.parentNode.childNodes.index(a),
                                    b.parentNode.childNodes.index(b)))
        columnIndex = 0
        cell_index = 0

        while len(cells) > cell_index:
            if columnIndex in multi_row_cache.keys():
                multi_row_cache[columnIndex][0].register_row(row)
                multi_row_cache[columnIndex][1] -= 1
                if multi_row_cache[columnIndex][1] == 0:
                    del multi_row_cache[columnIndex]
                columnIndex += 1

            else:
                dom_cell = cells[cell_index]
                cell_index += 1
                cell = self.create_latex_cell(dom_cell=dom_cell, row=row)
                # rowspan?
                if cell.get_rowspan() > 1:
                    multi_row_cache[columnIndex] = [
                        cell,
                        cell.get_rowspan() - 1]

                # colspan / find and register columns
                # find and register columns
                try:
                    colspan = int(dom_cell.getAttribute('colspan'))
                except ValueError:
                    colspan = 1

                for cid in range(columnIndex, columnIndex + colspan):
                    while len(self.columns) <= cid:
                        col = self.create_latex_column()
                        self.columns.append(col)
                    cell.register_column(self.columns[cid])
                # move columnIndex to right
                columnIndex += colspan

        return row, columnIndex

    def get_amount_of_columns(self):
        columns = 0
        # by <colgroup>-Tag
        colgroups = self.dom.getElementsByTagName('colgroup')
        if len(colgroups) > 0:
            colgroup = colgroups[0]
            for col in colgroup.getElementsByTagName('col'):
                try:
                    columns += int(col.getAttribute('colspan'))
                except (ValueError, TypeError):
                    columns += 1

        # by <td>- and <th>-Tags
        for tr in self.dom.getElementsByTagName('tr'):
            tr_columns = 0
            cells = tr.getElementsByTagName('td') + \
                tr.getElementsByTagName('th')
            for cell in cells:
                try:
                    tr_columns += int(cell.getAttribute('colspan'))
                except (ValueError, TypeError):
                    tr_columns += 1
            if tr_columns > columns:
                columns = tr_columns
        return columns

    def create_latex_column(self, *args, **kwargs):
        return LatexColumn(self.converter, self, *args, **kwargs)

    def create_latex_row(self, *args, **kwargs):
        return LatexRow(self.converter, self, *args, **kwargs)

    def create_latex_cell(self, *args, **kwargs):
        return LatexCell(self.converter, self, *args, **kwargs)


class LatexColumn(object):
    """
    Represents a table column (col)
    """

    converter = None
    table_converter = None
    dom_col = None
    cells = []

    def __init__(self, converter, table_converter):
        self.converter = converter
        self.dom_col = None
        self.table_converter = table_converter
        self.cells = []
        self._width = _marker
        self._align = _marker

    def set_dom_col(self, dom_col):
        self.dom_col = dom_col

    def register_cell(self, cell):
        self.cells.append(cell)

    def get_width(self):
        if self._width == _marker:
            self._width = None
            # use <col> definition, if existing
            if self.dom_col:
                try:
                    self._width = LatexWidth.convert(
                        self.dom_col.getAttribute('width'))
                except ValueError:
                    pass

            # .. otherwise try to get width of a cell
            if not self._width:
                for cell in self.cells:
                    w = cell.get_width()
                    if cell.get_colspan() == 1 and w:
                        self._width = w
                        break
        return self._width

    def get_align(self):
        if self._align == _marker:
            if self.dom_col:
                self._align = get_alignment(self.dom_col)
            else:
                self._align = None
        return self._align

    def get_format(self):
        format_ = ''
        if self.get_width():
            format_ = 'p{%s}' % str(self.get_width())

        elif self.get_align():
            mapping = {
                'left': 'l',
                'right': 'r',
                'center': 'c',
                }
            format_ = mapping[self.get_align()]

        else:
            format_ = 'l'

        format_ = apply_borders_to_format(self, format_)
        return format_

    def has_left_border(self):
        return self.table_converter.get_border()

    def has_right_border(self):
        if self.table_converter.get_border() and self.is_last_column():
            return True

        return False

    def is_last_column(self):
        columns = self.table_converter.columns
        return columns[-1] == self


class LatexRow(object):
    """
    Represents a table row (tr)
    """

    converter = None
    table_converter = None
    domTr = None
    cells = []

    def __init__(self, converter, table_converter, domTr):
        self.converter = converter
        self.table_converter = table_converter
        self.domTr = domTr
        self.cells = []

    def register_cell(self, cell):
        self.cells.append(cell)

    def contains_head_cells(self):
        for cell in self.cells:
            if cell.is_head_cell():
                return True
        return False

    def is_first_row(self):
        return self.table_converter.rows.index(self) == 0

    def get_next_row(self):
        rows = self.table_converter.rows
        next_row_index = rows.index(self)
        try:
            return rows[next_row_index]
        except IndexError:
            return None

    def render(self):
        latex = []

        if self.is_first_row():
            line_latex = self.get_horizontal_line_latex([], self)
            if line_latex:
                latex.append(line_latex)

        latex_cells = []
        for cell in self.cells:
            tex = cell.render(self)
            if tex:
                latex_cells.append(tex)
            else:
                latex_cells.append('')

        latex.append('%s \\\\' % ' & '.join(latex_cells))
        line_latex = self.get_horizontal_line_latex(self, self.get_next_row())
        if line_latex:
            latex.append(line_latex)

        return '\n'.join(latex) + '\n'

    def get_horizontal_line_latex(self, top_row, bottom_row):
        lined_column_indexes = set()

        if top_row:
            index = 1
            for cell in top_row.cells:
                if cell.has_bottom_border_in_row(top_row):
                    for i in range(index, index + cell.get_colspan()):
                        lined_column_indexes.add(i)
                index += cell.get_colspan()

        if bottom_row:
            index = 1
            for cell in bottom_row.cells:
                if cell.has_top_border_in_row(bottom_row):
                    for i in range(index, index + cell.get_colspan()):
                        lined_column_indexes.add(i)
                index += cell.get_colspan()

        if len(lined_column_indexes) == len(self.table_converter.columns):
            return r'\hline'

        latex = []
        start = -1
        end = -1
        for index in sorted(lined_column_indexes):
            if start == -1:
                start = end = index
            elif end + 1 < index:
                latex.append(r'\cline{%s-%s}' % (start, end))
                start = end = index
            else:
                end = index

        if start != -1:
            latex.append(r'\cline{%s-%s}' % (start, end))

        return ''.join(latex)


class LatexCell(object):
    """
    Represents a table cell (td, th)
    """

    converter = None
    table_converter = None
    dom_cell = None
    rows = []
    columns = []

    def __init__(self, converter, table_converter, dom_cell, row):
        self.converter = converter
        self.table_converter = table_converter
        self.dom_cell = dom_cell
        self.rows = []
        self.columns = []
        self._parentNodes = None
        self._width = _marker
        self._colspan = None
        self._rowspan = None
        self._align = _marker
        self._css_classes = None
        self.register_row(row)

    def register_row(self, row):
        row.register_cell(self)
        self.rows.append(row)

    def register_column(self, column):
        self.columns.append(column)
        column.register_cell(self)

    def render(self, row):
        # only render it in first occuring row (if rowspan > 1)
        if self.get_rowspan() > 1 and self.rows.index(row) > 0:
            return None
        # render it
        if self.get_rowspan() > 1:
            span = str(self.get_rowspan())
            latex = '\\multirow{%s}{%s}{%s}' % (
                span,
                str(self.get_calculated_width()).replace(r'\linewidth',
                                                       r'\textwidth'),
                self.render_content(),
                )
        else:
            span = str(self.get_colspan())
            latex = '\\multicolumn{%s}{%s}{%s}' % (
                span,
                self.get_format(),
                self.render_content(),
                )
        return latex

    def render_content(self):
        content = ''.join([child.toxml() for child
                           in self.dom_cell.childNodes])

        # Carriage returns are not allowed in table cells with multicolumn.
        # We use \newline instead, which only creates a newline if the cell
        # width is defined, but does not fail otherwise.
        custom_patterns = [
            (MODE_REGEXP, r'<br[ \W]{0,}>\n*',
             r'\%snewline ' % PREVENT_CHARACTER),

            (wrapper.CustomPatternAtPlaceholderWrapper(
                    MODE_REPLACE, PLACEHOLDER_BOTTOM), '\n', r'\newline '),

            ]

        content = content.encode('utf8')
        latex = self.converter.convert(content,
                                       custom_patterns=custom_patterns)

        if self.get_calculated_width() and self.get_align():
            # if a width and align is defined, we need to set
            # aligenement in content part with a command
            mapping = {
                'left': r'\raggedright ',
                'right': r'\raggedleft ',
                'center': r'\center\vspace{-1.5em}',
                }

            if self.get_align() in mapping.keys():
                latex = mapping[self.get_align()] + latex
        return latex

    def is_head_cell(self):
        if 'thead' in [p.tagName.lower() for p in self.get_parent_nodes()]:
            # cell is within a <thead>
            return True
        if self.dom_cell.tagName.lower() == 'th':
            # cell is a <th>
            return True
        else:
            # not a head cell
            return False

    def get_parent_nodes(self):
        """
        Returns a list of all parent nodes (and their parent nodes etc).
        """
        if self._parentNodes is None:
            self._parentNodes = []
            node = self.dom_cell

            while node.parentNode and \
                    node.parentNode.__class__ != minidom.Document:
                node = node.parentNode
                self._parentNodes.append(node)
        return self._parentNodes

    def get_width(self):
        if self._width == _marker:
            try:
                self._width = LatexWidth.convert(
                    self.dom_cell.getAttribute('width'))
            except ValueError:
                self._width = None
        return self._width

    def get_colspan(self):
        if self._colspan is None:
            try:
                self._colspan = int(self.dom_cell.getAttribute('colspan'))
            except (AttributeError, ValueError):
                self._colspan = 1
        return self._colspan

    def get_rowspan(self):
        if self._rowspan is None:
            try:
                self._rowspan = int(self.dom_cell.getAttribute('rowspan'))
            except (AttributeError, ValueError):
                self._rowspan = 1
        return self._rowspan

    def get_calculated_width(self):
        if self.get_width():
            return self.get_width()

        elif self.get_colspan() == 1:
            return self.columns[0].get_width()

        elif self.get_colspan() > 1:
            width = self.columns[0].get_width()
            for i in range(1, len(self.columns)):
                try:
                    width += self.columns[i].get_width()
                except ValueError:
                    # one of the columns has no or invalid width (not addable)
                    return None
            return width

    def get_align(self):
        if self._align == _marker:
            self._align = None

            if self.dom_cell:
                self._align = get_alignment(self.dom_cell)

            if not self._align and self.get_colspan() == 1:
                self._align = self.columns[0].get_align()
        return self._align

    def has_left_border(self):
        if self.columns[0].has_left_border():
            return True

        if 'border-left' in self.get_css_classes():
            return True

        left_cell = self.get_left_cell()
        if left_cell and left_cell.get_rowspan() > 1 and \
                left_cell.has_right_border():
            return True

        return False

    def has_right_border(self):
        if self.columns[-1].has_right_border():
            return True

        if 'border-right' in self.get_css_classes():
            return True

        right_cell = self.get_right_cell()
        if right_cell and right_cell.get_rowspan() > 1 and \
                right_cell.has_left_border():
            return True

        return False

    def get_left_cell(self, row_index=0):
        """Get the next cell at the left side of this cell or None.
        """
        row_cells = self.rows[row_index].cells
        left_cell_index = row_cells.index(self) - 1
        try:
            return row_cells[left_cell_index]
        except IndexError:
            return None

    def has_bottom_border_in_row(self, row):
        if self.rows[-1] != row:
            return False

        if self.table_converter.get_border():
            return True

        if 'border-bottom' in self.get_css_classes():
            return True

        return False

    def has_top_border_in_row(self, row):
        if self.rows[0] != row:
            return False

        if self.table_converter.get_border():
            return True

        if 'border-top' in self.get_css_classes():
            return True

        return False

    def get_right_cell(self, row_index=0):
        """Get the next cell at the right side of this cell or None.
        """
        row_cells = self.rows[row_index].cells
        right_cell_index = row_cells.index(self) + 1
        try:
            return row_cells[right_cell_index]
        except IndexError:
            return None

    def get_format(self):
        format_ = 'l'
        if self.get_calculated_width():
            format_ = 'p{%s}' % str(self.get_calculated_width())

        elif self.get_align():
            mapping = {
                'left': 'l',
                'right': 'r',
                'center': 'c',
                }
            format_ = mapping[self.get_align()]

        # use column definition
        elif self.get_colspan() == 1:
            format_ = self.columns[0].get_format()

        format_ = apply_borders_to_format(self, format_)
        return format_

    def get_css_classes(self):
        if self._css_classes is None:
            if self.dom_cell:
                classes = self.dom_cell.getAttribute('class').strip()
                self._css_classes = classes.split(' ')

            else:
                self._css_classes = []

        return self._css_classes


class LatexWidth(object):
    """
    Converts HTML-width to latex width
    """

    TYPE_ABSOLUTE = 'absolute width (px, em, ..)'
    TYPE_RELATIVE = 'relative width (% of linewidth, ..)'
    VALID_ABSOLUTE_UNITS = [
        'cm',
        'mm',
        'em',
        ]

    def __init__(self, width=0, type_=None, unit=''):
        self.width = width
        self.type = type_
        self.unit = unit

    @classmethod
    def convert(cls, width):
        """
        creates a LatexWidth object by a HTML width-Attribute
        """

        # absolute
        for unit in cls.VALID_ABSOLUTE_UNITS:
            match = re.compile('^([0-9,\.]{1,})(%s)$' % unit).match(width)
            if match:
                w, u = match.groups()
                w = w.replace(',', '.')
                return cls(width=float(w),
                           type_=LatexWidth.TYPE_ABSOLUTE,
                           unit=u)

        # relative
        unit = '%'
        match = re.compile('^([0-9,\.]{1,})(%s)$' % unit).match(width)
        if match:
            w, u = match.groups()
            w = w.replace(',', '.')
            return cls(width=float(w) / 100,
                       type_=LatexWidth.TYPE_RELATIVE,
                       unit=None)

        # without unit -> use 'em'
        match = re.compile('^([0-9,\.]*)$').match(width)
        if match:
            w = width.replace(',', '.')
            return cls(width=float(w),
                       type_=LatexWidth.TYPE_ABSOLUTE,
                       unit='em')

        raise ValueError(
            'Could not convert string "%s" to valid LatexWidth' % width)

    def get(self):
        if self.type == LatexWidth.TYPE_ABSOLUTE:
            return '%s%s' % (str(self.width), self.unit)
        elif self.type == LatexWidth.TYPE_RELATIVE:
            return '%s\\linewidth' % str(self.width)

    def __str__(self):
        return self.get()

    def __add__(self, b):
        if not isinstance(b, LatexWidth):
            raise ValueError(
                'Cannot accumulate LatexWidth with %s' % (
                    type(b).__name__))

        a, b = self.__class__.harmonize_units(self, b)

        if a.type != b.type:
            raise ValueError(
                'Cannot accumulate relative and absolute widths.')

        if a.unit != b.unit:
            raise ValueError(
                'Cannot accumulate LatexWidths with different ' + \
                    'units (%s, %s)' % (a.unit, b.unit))

        return LatexWidth(width=(a.width + b.width),
                          type_=a.type,
                          unit=a.unit)

    @staticmethod
    def harmonize_units(a, b):
        """If possible, converts the units of a and b so that they are
        the same.
        """

        if a.type != b.type or a.unit == b.unit:
            return a, b

        elif a.unit == 'mm' and b.unit == 'cm':
            b2 = LatexWidth(width=b.width * 10,
                            type_=b.type,
                            unit='mm')
            return a, b2

        elif a.unit == 'cm' and b.unit == 'mm':
            a2 = LatexWidth(width=a.width * 10,
                            type_=a.type,
                            unit='mm')
            return a2, b

        else:
            return a, b


def apply_borders_to_format(element, format_):
    """Apply the border information to a column / cell format if necessary
    and return the new format.

    Arguments:
    `element` -- Cell or column object.
    `format_` -- LaTeX format definiton.
    """

    if element.has_left_border() and not format_.startswith('|'):
        format_ = '|%s' % format_

    if element.has_right_border() and not format_.endswith('|'):
        format_ = '%s|' % format_

    return format_


def get_alignment(node):
    """Returns the alignment of a XML node.
    """

    alignment_classes = ('left', 'right', 'center')
    classes = node.getAttribute('class').strip().split(' ')

    for cls in alignment_classes:
        if cls in classes:
            return cls

    return node.getAttribute('align')
