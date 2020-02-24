#!/usr/bin/python

import sys
import os
import time
import shutil
import pyexcel
import xlrd
import PyPDF2
import logging

class ReadFile():
    def __init__(self):
        pass

    # function to read pdf file, return glob content
    def parsePDF(self, pdfFile):
        pdfDoc = PyPDF2.PdfFileReader(file(pdfFile, "rb"))
        content = ''
        for i in range(0, pdfDoc.getNumPages()):
            content += pdfDoc.getPage(i).extractText() + "\n"
        return content

    # function to read scanned pdf file (mostly images).
    def parseScannedPDF(self, pdfFile):
        print(('zbFile.py/parseScannedPDF: Remainder: This function can only ' +
            'be used if pypdfocr and tesseract-ocr are installed. ' +
            'To install, run "pip install pypdfocr" and "apt-get install tesseract-ocr".'))
        outputFilePath = self._ocrReportPath(pdfFile)
        output = os.popen('pypdfocr \"' + pdfFile +"\"").readlines()
        for _ in range(8):
            time.sleep(15)
            if os.path.exists(outputFilePath):
                content = self.parsePDF(outputFilePath).encode('utf-8')
                os.remove(outputFilePath)
                return content.replace('\r', '').replace('\n', ' ')
        print(('zbFile.py/parseScannedPDF: Not able to parse scanned pdf. Error: {}'.format(output)))
        return ''

    def _ocrReportPath(self, originalPath):
        extensionPos = originalPath.find('.pdf')
        outputFilePath = originalPath[:extensionPos] + '_ocr' + originalPath[extensionPos:]
        return outputFilePath

    # function to read xls file, return glob content
    def parseExcel(self, xlsFile):
        colnames = []
        content = []
        xl_workbook = xlrd.open_workbook(xlsFile)
        sheet_names = xl_workbook.sheet_names()
        for sheet in sheet_names:
            xl_sheet = xl_workbook.sheet_by_name(sheet)
            num_cols = xl_sheet.ncols

            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(0, col_idx)  # Get cell object by row, col
                colnames.append(str(cell_obj.value).encode('ascii','ignore'))
            
            for row_idx in range(1, xl_sheet.nrows):    # Iterate through rows
                item = {}
                for col_idx in range(0, num_cols):  # Iterate through columns
                    cell_obj = xl_sheet.cell(row_idx, col_idx)
                    item[colnames[col_idx]] = str(cell_obj.value).encode('ascii','ignore')
                content.append(item)
        return content

    #parseExcel modified to use for parsing report logs in CSV format
    #parse_excel_report can be used for any general CSV parsing as all it does is return list of every value found in CSV file
    def parse_excel_report(self, xls_file):
        content = []
        xl_workbook = xlrd.open_workbook(xls_file)
        sheet_names = xl_workbook.sheet_names()
        
        for sheet in sheet_names:
            #include title of CSV tab/sheet
            content.append(str(sheet).lower().replace(' ', ''))
            
            xl_sheet = xl_workbook.sheet_by_name(sheet)
            num_cols = xl_sheet.ncols
            
            for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
                for col_idx in range(0, num_cols):  # Iterate through columns
                    cell_value = str(xl_sheet.cell(row_idx, col_idx).value).lower().replace(' ', '')
                    cell_value and content.append(cell_value)
        #content unordered array of non-empty values found in every cell of every tab in csv file
        return content


# test
'''
reader = ReadFile()
content = reader.parsePDF("./lib/common/test.pdf")
print(content)
# for pcap in pcaps:
#     print (pcap)
'''
