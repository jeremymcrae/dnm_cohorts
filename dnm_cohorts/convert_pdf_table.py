
import itertools

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextContainer

import pdfminer

TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]

def extract_pages(fp, start=None, end=None):
    """ extracts LTPage objects from a pdf file
    
    slightly modified from: https://euske.github.io/pdfminer/programming.html
    """
    laparams = LAParams()
    
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    
    manager = PDFResourceManager()
    device = PDFPageAggregator(manager, laparams=laparams)
    interpreter = PDFPageInterpreter(manager, device)
    
    for i, page in enumerate(PDFPage.create_pages(document)):
        if start is not None and end is not None and i < start or i >= end:
            continue
        
        interpreter.process_page(page)
        yield device.get_result()

def flatten(lst):
    """Flattens a list of lists"""
    return [subelem for elem in lst for subelem in elem]

def extract_characters(element):
    """
    Recursively extracts individual characters from
    text elements.
    """
    if isinstance(element, pdfminer.layout.LTChar):
        return [element]
    
    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
        return flatten([extract_characters(e) for e in element])
    
    if isinstance(element, list):
        return flatten([extract_characters(l) for l in element])
    
    return []

def group(characters, delta=5, use_h_axis=True):
    """ group characters based on proximity
    
    Args:
        use_h_axis: whether to group characters based on their distance
            horizontally. When False, you group text into lines
    """
    
    groups = []
    for c in characters:
        obj = None
        for obj in groups:
            if use_h_axis:
                if obj.vdistance(c) < delta and obj.hdistance(c) < delta:
                    break
            else:
                if obj.vdistance(c) < delta:
                    break
            obj = None
        
        if obj is None:
            obj = LTTextContainer()
            obj.add(c)
            groups.append(obj)
        else:
            obj.add(c)
    
    return groups

def merge(lines, delta=5):
    """ merge text elements where they should be in a single group
    
    Some text elements might get placed into separate groups if they are are on
    separate lines, and their lines start at different x-positions. This function
    cleans those up.
    """
    
    merged = []
    for line in lines:
        elem = list(line)
        for a, b in itertools.combinations(range(len(elem)), 2):
            if elem[a] is None or elem[b] is None:
                continue
            if elem[a].hdistance(elem[b]) < delta:
                elem[a].extend(elem[b])
                elem[b] = None
        
        line = LTTextContainer()
        line.extend([ x for x in elem if x is not None ])
        merged.append(line)
    
    return merged

def convert_page(page, delta=3):
    characters = extract_characters(list(page))
    words = group(characters, delta)
    lines = group(words, delta, use_h_axis=False)
    lines = merge(lines, delta)
    
    return lines
