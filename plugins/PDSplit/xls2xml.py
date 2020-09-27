#!/usr/bin/python
from xml.etree import ElementTree as ET
import argparse,xlrd,string,sys


def indent(elem,level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

def create_node(tag, property, content):
    element = ET.Element(tag, property)
    element.text = content
    return element

def get_point(xCoord,yCoord,name):
    pdPoint = ET.Element(name)
    pdPoint.append(create_node('Coordinate X',{},str(xCoord)))
    pdPoint.append(create_node('Coordinate Y',{},str(yCoord)))
    return pdPoint

def get_points(data,name,filename):
    pdPoints = ET.Element(name)
    for element in data:
        xCoord = element[0]
        yCoord = element[1]
        pdPoints.append(get_point(xCoord,yCoord,'pdPoint'))
    indent(pdPoints)
    f = open(filename.split('.')[0]+".xml",'w')
    temp = sys.stdout
    sys.stdout = f
    ET.dump(pdPoints)
    sys.stdout = temp
    f.close()

def xls_analyze(filename):
    xls = xlrd.open_workbook(filename)
    table = xls.sheet_by_name('Sheet1')
    rowCount = table.nrows
    data = []
    for row in range(0,rowCount):
        sheetData = []
        xCoord = int(table.cell_value(row,0))
        yCoord = int(table.cell_value(row,1))
        sheetData.append(xCoord)
        sheetData.append(yCoord)
        data.append(sheetData)
    return data

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    return parser.parse_args().filename

def main(filename):
    data = xls_analyze(filename)
    get_points(data,'pdPoints',filename)

if __name__ == '__main__':
    filename = parse_arg()
    main(filename)