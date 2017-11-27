"""
Simple python class for analyzing the output xmi format for the Clamp toolkit
Just for a linear structure, one document per xmi
For CLAMP: clinicalnlptool.com/index.php
For any further questions contact: Yang.Xiang@uth.tmc.edu 
"""

import string
import os
import re
# you should install the 3rd party package lxml using pip install or the develop kit
from lxml import etree as ET

class ClampXmi:
    """
    Convert from clamp xmi to sentences, tokens, name entities, and relationships
    """
    def __init__(self, XML_PATH):
        # read and parse the xml tree
        tree = ET.parse(XML_PATH)
        self.root = tree.getroot()
        self.namespace = self.root.nsmap
        # public variables
        self.doc_str = ''
        self.sentences = []
        self.tokens = []
        self.NEs = []
        # call functions you needed
        self.find_doc()
        self.find_sentences()
        self.find_NEs()
        self.find_tokens()
       
    # find the document string for a single document xml
    def find_doc(self):
        doc_xml = self.root.find('cas:Sofa', self.namespace)
        self.doc_str = doc_xml.get('sofaString')
    
    # find all sentences with spans
    def find_sentences(self):
        sentences_xmi = self.root.findall('textspan:Sentence', self.namespace)
        sentences = []
        for sentence_xmi in sentences_xmi:
            begin_pos = int(sentence_xmi.get('begin'))
            end_pos = int(sentence_xmi.get('end'))
            sentence_no = sentence_xmi.get('sentenceNumber')
            sentence_str = self.doc_str[begin_pos:end_pos]
            sentence = {'sentence_no': sentence_no,
                        'begin_pos': begin_pos,
                        'end_pos': end_pos,
                        'sen_str': sentence_str}
            sentences.append(sentence)
        self.sentences = sentences
    
    # find all the tokenized words with POS taggs
    def find_tokens(self):
        tokens_xmi = self.root.findall('syntax:BaseToken', self.namespace)
        tokens = []
        for token_xmi in tokens_xmi:
            begin_pos = int(token_xmi.get('begin'))
            end_pos = int(token_xmi.get('end'))
            POS_tag = token_xmi.get('partOfSpeech')
            token_no = token_xmi.get('tokenNumber')
            token_str = self.doc_str[begin_pos:end_pos]
            # assign NE tag to the token
            token_NE = 'O'
            for NE in self.NEs:
                pos_b = NE['begin_pos']
                pos_e = NE['end_pos']
                if begin_pos >= pos_b and end_pos <= pos_e:
                    if begin_pos == pos_b:
                        if end_pos == pos_e:
                            NE_type = 'S-' + NE['semantic']
                        else:
                            NE_type = 'B-' + NE['semantic']
                    #elif end_pos == pos_e:
                    #    NE_type = 'E-' + NE['semantic']
                    else:
                        NE_type = 'I-' + NE['semantic']
                    token_NE = NE_type
                    break

            token = {'token_no': token_no,
                     'begin_pos': begin_pos,
                     'end_pos': end_pos,
                     'token_str': token_str,
                     'POS_tag': POS_tag,
                     'NE_tag': token_NE}

            tokens.append(token)
        self.tokens = tokens
     
    # find all name entities
    def find_NEs(self):
        NEs_xmi = self.root.findall('typesystem:ClampNameEntityUIMA', self.namespace)
        NEs = []
        for NE_xmi in NEs_xmi:
            NE_id = NE_xmi.get('xmi:id', self.namespace)
            begin_pos = int(NE_xmi.get('begin'))
            end_pos = int(NE_xmi.get('end'))
            semantic = NE_xmi.get('semanticTag')
            cui = NE_xmi.get('cui')
            attribute = NE_xmi.get('attribute')
            NE_str = self.doc_str[begin_pos:end_pos]
            NE = {'NE_id': NE_id,
                  'begin_pos': begin_pos,
                  'end_pos': end_pos,
                  'semantic': semantic,
                  'cui': cui,
                  'attribute': attribute,
                  'NE_str': NE_str}
            NEs.append(NE)
        self.NEs = NEs

     # Define functions you needed below as those above
     
     #def find_relations(self):
     
     #def find_dependencies(self):
     
     #def find_chunks(self):
        
# traverse the directory and get all the file paths        
def walk_dir(DIR):
    li = []
    for i in os.walk(DIR):
        for j in i[2]:
            li.append(DIR + j)
    return li

# demo call function
# read the outputs of the clamp dir and generate BIO form files
def readClampDir(INPUT_DIR, OUTPUT_DIR):
    ord_docs = []
    input_li = walk_dir(INPUT_DIR)
    for PATH in input_li:
        if PATH.find('xmi') > 0:
            print PATH
            cx = ClampXmi(PATH)

# main process
def main(INPUT_DIR):
    readClampDir(INPUT_DIR)


if __name__ == '__main__':
    DIR = 'YOUR DIR FOR STORING CLAMP RESULT IN XMI FORMAT'
    main(DIR)
