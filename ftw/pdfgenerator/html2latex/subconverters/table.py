from BeautifulSoup import BeautifulSoup
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.interfaces import HTML2LATEX_MODE_REGEXP
from ftw.pdfgenerator.utils import html2xmlentities
from xml.dom import minidom
import re



class TableConverter(subconverter.SubConverter):
    """The TableConverter converts <table>-Tags to latex.
    """

    pattern = r'<table(.*?)>(.*?)</table>'

    def __init__(self, *args, **kwargs):
        super(TableConverter, self).__init__(*args, **kwargs)
        self.columnAmount = 0
        self.LatexColumn = LatexColumn

    def __call__(self):
        html = self.get_html()
        # cleanup html with BeautifulSoup

        html = str(BeautifulSoup(html))
        # minidom hates htmlentities, but loves xmlentities -.-

        html = html2xmlentities(html)

        # parse DOM
        self.dom = minidom.parseString(html)
        self.parseDom()

        # render table
        latex = self.render()

        # replace with latex
        self.replace_and_lock(latex)

        # register packages
        self.converter.converter.layout.use_package('longtable')
        self.converter.converter.layout.use_package('multirow')
        self.converter.converter.layout.use_package('multicol')

    def getCssClasses(self):
        if '_css_classes' not in dir(self):
            self._css_classes = []
            domTable = self.dom.getElementsByTagName('table')[0]
            try:
                classes = domTable.getAttribute('class').strip()
                self._css_classes = classes.split(' ')
            except:
                pass
        return self._css_classes

    def getBorder(self):
        domTable = self.dom.getElementsByTagName('table')[0]
        if (domTable.hasAttribute('border')):
            return int(domTable.getAttribute('border'))>0
        return False

    def hasTableParts(self):
        """
        If the HTML table has thead / tbody, it returns True,
        otherwise False
        """
        if '_has_table_parts' not in dir(self):
            thead = self.dom.getElementsByTagName('thead')
            tbody = self.dom.getElementsByTagName('tbody')
            if len(thead)>0 or len(tbody)>0:
                self._has_table_parts = True
            else:
                self._has_table_parts = False
        return self._has_table_parts

    def render(self):
        hline=self.getBorder() and '\n\\hline' or ''
        latex = '\\begin{longtable}{%s}%s\n' % (self.getTableFormat(),hline)
        captionCommand, insertCaptionAtTop = self.renderCaption()
        if captionCommand and insertCaptionAtTop:
            latex += captionCommand
        latex += self.renderRows()
        if captionCommand and not insertCaptionAtTop:
            latex += captionCommand
        latex += '\\end{longtable}\n'
        return latex

    def renderRows(self):
        headRows = []
        bodyRows = []
        for row in self.rows:
            rowLatex = row.render()
            if row.containsHeadCells():
                headRows.append(rowLatex)
            else:
                bodyRows.append(rowLatex)
        headLatex = ''
        if len(headRows)>0:
            headLatex = ''.join(headRows)
        bodyLatex = ''
        if len(bodyRows)>0:
            bodyLatex = ''.join(bodyRows)
        if len(headRows)>0:
            return '%s\\endhead\n%s' % (headLatex, bodyLatex)
        else:
            return bodyLatex

    def renderCaption(self):
        """
        If the HTML-Table contains a <caption>-Tag, this method
        returns the LaTeX-Command for the caption and weather the
        command should be inserted at the top or at the bottom of
        the table.

        Example:
        captionCommand, insertAtTop = self.renderCaption()
        captionCommand : \caption{My Table}
        insertAtTop : True

        If there is no command, it will return
        None, False
        """
        caption = self.dom.getElementsByTagName('caption')
        if len(caption)>0:
            captionTag = caption[0]
            siblings = captionTag.parentNode.childNodes
            insertAtTop = len(siblings)/float(2) > (siblings.index(captionTag) + 1)
            content = ''.join([child.toxml() for child in caption[0].childNodes])
            content = content.encode('utf8')
            latexContent = self.converter.convert(content)
            return '\\caption%s{%s} \\\\\n' % (
                ('notListed' in self.getCssClasses() and '*' or ''),
                latexContent,
            ), insertAtTop
        else:
            return None, False

    def getTableFormat(self):
        columnFormat = []
        for col in self.columns:
            columnFormat.append(col.getFormat())
        return ''.join(columnFormat)

    def parseDom(self):
        # create colum objects
        self.columns = []
        domColList = self.dom.getElementsByTagName('col')
        amount = self.getAmountOfColumns()
        amount = amount>len(domColList) and amount or len(domColList)
        for c in range(amount):
            col = self.createLatexColumn()
            if len(domColList)>c:
                col.setDomCol(domColList[c])
            self.columns.append(col)
        # create rows / cells
        self.rows = []
        multiRowCache = {
            # columnIndex : [Cell, DecrementingRowspan],
        }
        for domTr in self.dom.getElementsByTagName('tr'):
            row = self.createLatexRow(domTr=domTr)
            self.rows.append(row)
            # .. cells
            cells = domTr.getElementsByTagName('th')
            cells += domTr.getElementsByTagName('td')
            # sorting
            cells.sort(lambda a,b:cmp(a.parentNode.childNodes.index(a),
                    b.parentNode.childNodes.index(b)))
            columnIndex = 0
            cellIndex = 0
            while len(cells)>cellIndex:
                if columnIndex in multiRowCache.keys():
                    multiRowCache[columnIndex][0].registerRow(row)
                    multiRowCache[columnIndex][1] -= 1
                    if multiRowCache[columnIndex][1]==0:
                        del multiRowCache[columnIndex]
                    columnIndex += 1
                else:
                    domCell = cells[cellIndex]
                    cellIndex += 1
                    cell = self.createLatexCell(domCell=domCell, row=row)
                    # rowspan?
                    if cell.getRowspan()>1:
                        multiRowCache[columnIndex] = [cell,
                                                      cell.getRowspan()-1]

                    # colspan / find and register columns
                    # find and register columns
                    try:
                        colspan = int(domCell.getAttribute('colspan'))
                    except:
                        colspan = 1
                    for cid in range(columnIndex, columnIndex + colspan):
                        while len(self.columns)<=cid:
                            col = self.createLatexColumn()
                            self.columns.append(col)
                        cell.registerColumn(self.columns[cid])
                    # move columnIndex to right
                    columnIndex += colspan
            antiEndlessLoopCounter = 1000
            while len(multiRowCache)>0:
                if columnIndex in multiRowCache.keys():
                    multiRowCache[columnIndex][0].registerRow(row)
                    multiRowCache[columnIndex][1] -= 1
                    if multiRowCache[columnIndex][1]==0:
                        del multiRowCache[columnIndex]
                columnIndex += 1
                antiEndlessLoopCounter -= 1
                if antiEndlessLoopCounter<0:
                    break

    def getAmountOfColumns(self):
        columns = 0
        # by <colgroup>-Tag
        colgroups = self.dom.getElementsByTagName('colgroup')
        if len(colgroups)>0:
            colgroup = colgroups[0]
            for col in colgroup.getElementsByTagName('col'):
                try:
                    columns += col.getAttribute('colspan')
                except:
                    columns += 1
        # by <td>- and <th>-Tags
        for tr in self.dom.getElementsByTagName('tr'):
            trColumns = 0
            cells = tr.getElementsByTagName('td') + \
                    tr.getElementsByTagName('th')
            for cell in cells:
                try:
                    trColumns += cell.getAttribute('colspan')
                except:
                    trColumns += 1
            if trColumns > columns:
                columns = trColumns
        return columns

    def createLatexColumn(self, *args, **kwargs):
        return LatexColumn(self.converter, self, *args, **kwargs)

    def createLatexRow(self, *args, **kwargs):
        return LatexRow(self.converter, self, *args, **kwargs)

    def createLatexCell(self, *args, **kwargs):
        return LatexCell(self.converter, self, *args, **kwargs)


class LatexColumn(object):
    """
    Represents a table column (col)
    """

    converter = None
    tableConverter = None
    domCol = None
    cells = []

    def __init__(self, converter, tableConverter):
        self.converter = converter
        self.domCol = None
        self.tableConverter = tableConverter
        self.cells = []

    def setDomCol(self, domCol):
        self.domCol = domCol

    def registerCell(self, cell):
        self.cells.append(cell)

    def getWidth(self):
        if '_width' not in dir(self):
            self._width = None
            # use <col> definition, if existing
            if self.domCol:
                try:
                    self._width = LatexWidth.convert(
                        self.domCol.getAttribute('width'))
                except:
                    pass
            # .. otherwise try to get width of a cell
            if not self._width:
                for cell in self.cells:
                    w = cell.getWidth()
                    if cell.getColspan()==1 and w:
                        self._width = w
                        break
        return self._width

    def getAlign(self):
        if '_align' not in dir(self):
            try:
                self._align = self.domCol.getAttribute('align')
            except:
                self._align = None
        return self._align

    def getFormat(self):
        format = ''
        if self.getWidth():
            format = 'p{%s}' % str(self.getWidth())
        elif self.getAlign():
            mapping = {
                'left' : 'l',
                'right' : 'r',
                'center' : 'c',
            }
            format = mapping[self.getAlign()]
        else:
            format = 'l'
        if self.tableConverter.getBorder():
            if self.tableConverter.columns.index(self) == 0:
                format = '|' + format
            format += '|'
        return format


class LatexRow(object):
    """
    Represents a table row (tr)
    """

    converter = None
    tableConverter = None
    domTr = None
    cells = []

    def __init__(self, converter, tableConverter, domTr):
        self.converter = converter
        self.tableConverter = tableConverter
        self.domTr = domTr
        self.cells = []

    def registerCell(self, cell):
        self.cells.append(cell)

    def containsHeadCells(self):
        for cell in self.cells:
            if cell.isCellWithinThead():
                return True
        return False

    def render(self):
        hline=self.tableConverter.getBorder() and '\n\\hline' or ''
        latexCells = []
        for cell in self.cells:
            tex = cell.render(self)
            if tex:
                latexCells.append(tex)
            else:
                latexCells.append('')
        return '%s \\\\%s\n' % (' & '.join(latexCells),hline)


class LatexCell(object):
    """
    Represents a table cell (td, th)
    """

    converter = None
    tableConverter = None
    domCell = None
    rows = []
    columns = []

    def __init__(self, converter, tableConverter, domCell, row):
        self.converter = converter
        self.tableConverter = tableConverter
        self.domCell = domCell
        self.rows = []
        self.columns = []
        self.registerRow(row)

    def registerRow(self, row):
        row.registerCell(self)
        self.rows.append(row)

    def registerColumn(self, column):
        self.columns.append(column)
        column.registerCell(self)

    def render(self, row):
        # only render it in first occuring row (if rowspan > 1)
        if self.getRowspan()>1 and self.rows.index(row)>0:
            return None
        # render it
        if self.getRowspan()>1:
            span = str(self.getRowspan())
            latex = '\\multirow{%s}{%s}{%s}' % (
                span,
                str(self.getCalculatedWidth()).replace(r'\linewidth',
                                                       r'\textwidth'),
                self.renderContent(),
            )
        else:
            span = str(self.getColspan())
            latex = '\\multicolumn{%s}{%s}{%s}' % (
                span,
                self.getFormat(),
                self.renderContent(),
            )
        return latex

    def renderContent(self):
        content = ''.join([child.toxml() for child
                           in self.domCell.childNodes])

        # carriage returns are not allowed in table cells with multicolumn
        custom_patterns = (
            (HTML2LATEX_MODE_REGEXP, '<br[ \W]{0,}>', ''),
        )
        content = content.encode('utf8')
        latex = self.converter.convert(content,
                                       custom_patterns=custom_patterns)

        if self.getCalculatedWidth() and self.getAlign():
            # if a width and align is defined, we need to set
            # aligenement in content part with a command
            mapping = {
                'left' : r'\raggedright ',
                'right' : r'\raggedleft ',
                'center' : r'\center\vspace{-1.5em}',
            }
            if self.getAlign() in mapping.keys():
                latex = mapping[self.getAlign()] + latex
        return latex

    def isHeadCell(self):
        if 'thead' in [p.tagName.lower() for p in self.getParentNodes()]:
            # cell is within a <thead>
            return True
        if self.domCell.tagName.lower()=='th':
            # cell is a <th>
            return True
        else:
            # not a head cell
            return False

    def isCellWithinThead(self):
        """
        Returns True if the cell is within a <thead> tag.
        """
        return 'thead' in [p.tagName.lower() for p in self.getParentNodes()]

    def getParentNodes(self):
        """
        Returns a list of all parent nodes (and their parent nodes etc).
        """
        if '_parentNodes' not in dir(self):
            self._parentNodes = []
            node = self.domCell
            while node.parentNode and node.parentNode.__class__!=minidom.Document:
                node = node.parentNode
                self._parentNodes.append(node)
        return self._parentNodes

    def getWidth(self):
        if '_width' not in dir(self):
            try:
                self._width = LatexWidth.convert(self.domCell.getAttribute('width'))
            except:
                self._width = None
        return self._width

    def getColspan(self):
        if '_colspan' not in dir(self):
            try:
                self._colspan = int(self.domCell.getAttribute('colspan'))
            except:
                self._colspan = 1
        return self._colspan

    def getRowspan(self):
        if '_rowspan' not in dir(self):
            try:
                self._rowspan = int(self.domCell.getAttribute('rowspan'))
            except:
                self._rowspan = 1
        return self._rowspan

    def getCalculatedWidth(self):
        if self.getWidth():
            return self.getWidth()
        elif self.getColspan()==1:
            return self.columns[0].getWidth()
        elif self.getColspan()>1:
            width = self.columns[0].getWidth()
            for i in range(1, len(self.columns)):
                try:
                    width += self.columns[i].getWidth()
                except:
                    # one of the columns has no or invalid width (not addable)
                    return None
            return width
        return None

    def getAlign(self):
        if '_align':
            self._align = None
            try:
                self._align = self.domCell.getAttribute('align')
            except:
                if self.getColspan()==1:
                    self._align = self.columns[0].getAlign()
        return self._align

    def getFormat(self):
        format = 'l'
        if self.getCalculatedWidth():
            format='p{%s}' % str(self.getCalculatedWidth())
        elif self.getAlign():
            mapping = {
                'left' : 'l',
                'right' : 'r',
                'center' : 'c',
            }
            format = mapping[self.getAlign()]
        # use column definition
        elif self.getColspan()==1:
            format = self.columns[0].getFormat()
        if self.tableConverter.getBorder():
            format += '|'
            if self.columns[0]==self.tableConverter.columns[0]:
                format = '|%s'%format
        return format

    def getCssClasses(self):
        if '_css_classes' not in dir(self):
            self._css_classes = []
            try:
                classes = self.domCell.getAttribute('class').strip()
                self._css_classes = classes.split(' ')
            except:
                pass
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

    width = 0
    type = None
    unit = ''

    def convert(cls, width):
        """
        creates a LatexWidth object by a HTML width-Attribute
        """
        obj = cls()
        # absolute
        for unit in cls.VALID_ABSOLUTE_UNITS:
            match = re.compile('^([0-9,\.]{1,})(%s)$' % unit).match(width)
            if match:
                w, u = match.groups()
                w = w.replace(',','.')
                obj.width = float(w)
                obj.type = LatexWidth.TYPE_ABSOLUTE
                obj.unit = u
                return obj
        # relative
        unit = '%'
        match = re.compile('^([0-9,\.]{1,})(%s)$' % unit).match(width)
        if match:
            w, u = match.groups()
            w = w.replace(',','.')
            obj.width = float(w) / 100
            obj.type = LatexWidth.TYPE_RELATIVE
            obj.unit = None
            return obj
        # without unit -> use 'em'
        match = re.compile('^([0-9,\.])$').match(width)
        if match:
            w = width.replace(',','.')
            obj.width = float(w)
            obj.type = LatexWidth.TYPE_ABSOLUTE
            obj.unit = 'em'
            return obj
        raise Exception('Could not convert string "%s" to valid LatexWidth' % width)
    convert = classmethod(convert)

    def get(self):
        if self.type==LatexWidth.TYPE_ABSOLUTE:
            return '%s%s' % (str(self.width), self.unit)
        elif self.type==LatexWidth.TYPE_RELATIVE:
            return '%s\\linewidth' % str(self.width)

    def __str__(self):
        return self.get()

    def __add__(self, b):
        if not isinstance(b, LatexWidth):
            raise AttributeError('Expected LatexWidth instance as first attribute')
        if self.type!=b.type:
            raise AttributeError('Cant sum LatexWidths with different ' + \
                'types (%s, %s)' % (self.type, b.type))
        if self.unit!=b.unit:
            raise AttributeError('Cant sum LatexWidths with different ' + \
                'units (%s, %s)' % (self.unit, b.unit))
        sum = LatexWidth()
        sum.type = self.type
        sum.unit = self.unit
        sum.width = (self.width + b.width)
        return sum

