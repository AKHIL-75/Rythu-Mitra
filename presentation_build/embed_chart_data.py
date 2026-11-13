"""Attach a workbook snapshot to our new Artifact Tool chart without hard links.

This repairs packaging only. It keeps every displayed chart value and category.
"""
import copy
import io
import posixpath
import zipfile
from pathlib import Path
from lxml import etree
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent
source = ROOT / 'candidate_v3.pptx'
target = ROOT / 'candidate_embedded_v2.pptx'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
ns = {'c': C}
changes = {}
with zipfile.ZipFile(source) as archive:
    charts = [n for n in archive.namelist() if '/charts/' in n and n.endswith('.xml') and '/_rels/' not in n]
    assert len(charts) == 1
    for chart in charts:
        xml = etree.fromstring(archive.read(chart))
        wb = Workbook()
        ws = wb.active
        ws.title = 'ChartData'
        ws.cell(1, 1, 'Model / features')
        numeric_literals = {}
        for i, series in enumerate(xml.findall('.//c:ser', ns)):
            column = i + 2
            letter = chr(65 + column - 1)
            ws.cell(1, column, series.findtext('c:tx/c:v', namespaces=ns))
            for name, literal_tag, ref_tag, cache_tag, col in [
                ('cat', 'strLit', 'strRef', 'strCache', 'A'),
                ('val', 'numLit', 'numRef', 'numCache', letter),
            ]:
                parent = series.find('c:' + name, ns)
                literal = parent.find('c:' + literal_tag, ns)
                points = literal.findall('c:pt', ns)
                for point in points:
                    row = int(point.get('idx')) + 2
                    value = point.findtext('c:v', namespaces=ns)
                    if name == 'cat':
                        ws.cell(row, 1, value)
                    else:
                        ws.cell(row, column, float(value)).number_format = '0.00%'
                        numeric_literals[f'{letter}{row}'] = value
                reference = etree.Element('{' + C + '}' + ref_tag)
                etree.SubElement(reference, '{' + C + '}f').text = f"'ChartData'!${col}$2:${col}${len(points)+1}"
                cache = etree.SubElement(reference, '{' + C + '}' + cache_tag)
                for child in literal:
                    cache.append(copy.deepcopy(child))
                parent.replace(literal, reference)
        data = io.BytesIO()
        wb.save(data)
        workbook = 'ppt/embeddings/rythu-chart-data.xlsx'
        # Preserve the literal decimal spellings instead of binary float expansion.
        exact_workbook = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data.getvalue())) as original_wb, zipfile.ZipFile(exact_workbook, 'w', zipfile.ZIP_DEFLATED) as exact_wb:
            for item in original_wb.infolist():
                content = original_wb.read(item.filename)
                if item.filename == 'xl/worksheets/sheet1.xml':
                    sheet_xml = etree.fromstring(content)
                    xns = {'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    for cell in sheet_xml.findall('.//x:c', xns):
                        if cell.get('r') in numeric_literals:
                            cell.find('x:v', xns).text = numeric_literals[cell.get('r')]
                    content = etree.tostring(sheet_xml, xml_declaration=True, encoding='utf-8')
                exact_wb.writestr(item, content)
        changes[workbook] = exact_workbook.getvalue()
        relation = etree.Element('{' + PKG + '}Relationships', nsmap={None: PKG})
        etree.SubElement(relation, '{' + PKG + '}Relationship', Id='rIdWorkbook',
                         Type=R + '/package', Target=posixpath.relpath(workbook, posixpath.dirname(chart)))
        relation_part = posixpath.dirname(chart) + '/_rels/' + posixpath.basename(chart) + '.rels'
        assert relation_part not in archive.namelist()
        changes[relation_part] = etree.tostring(relation, xml_declaration=True, encoding='utf-8')
        external = etree.SubElement(xml, '{' + C + '}externalData')
        external.set('{' + R + '}id', 'rIdWorkbook')
        etree.SubElement(external, '{' + C + '}autoUpdate', val='0')
        changes[chart] = etree.tostring(xml, xml_declaration=True, encoding='utf-8')
    types = etree.fromstring(archive.read('[Content_Types].xml'))
    etree.SubElement(types, '{' + CT + '}Default', Extension='xlsx',
                     ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    changes['[Content_Types].xml'] = etree.tostring(types, xml_declaration=True, encoding='utf-8')
    # New output only, so a previous draft cannot be overwritten.
    with target.open('xb') as output, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as result:
        for info in archive.infolist():
            result.writestr(info, changes.pop(info.filename, archive.read(info.filename)))
        for name, content in changes.items():
            result.writestr(name, content)
print('Embedded native chart workbook with unchanged categories and cached values.')
