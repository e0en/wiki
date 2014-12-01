from parserCommon import objParseInline
import wikiObjLinePlugins
from wikiArticleObject import Page 
#import wikiPostProcessors
import cgi

# Core functions of wikiwiki - list, header
class ObjParser:
    def __init__(self, title):
        self.line_plugins = wikiObjLinePlugins.load()
        #self.post_processors = wikiPostProcessors.load()
        self.page = Page(title)

    # this wikiwiki parser scans the document twice.
    def parse(self, raw_text):
        raw_text = raw_text.replace('\r', '')
        raw_text = cgi.escape(raw_text)

        lines = raw_text.split('\n')
       
        parsed = []
        settings = {} 
        p_buffer = ''

        i = 0
    
        # process #1. create xhtmls from text 
        while 1:
            if i >= len(lines):
                break
            if lines[i].strip() == '':
                # make a paragraph
                if p_buffer.strip() != '':
                    self.page.curChapter.add(objParseInline(p_buffer, self.page))
                i += 1
            else:
                did_match = False
                for p in self.line_plugins:
                    if p.test(lines, i):
                        if p_buffer.strip() != '':
                            self.page.curChapter.add(objParseInline(p_buffer,
                                self.page))
                            p_buffer = ''
                        offset = p.parse(lines, i, self.page)
                        did_match = True
                        i += offset
                        break

                if not did_match:
                    # accumulate current line for a paragraph
                    p_buffer += lines[i] + '\n'
                    i += 1
        # flush p_buffer if its content exists
        if p_buffer.strip() != '':
            self.page.curChapter.add(objParseInline(p_buffer, self.page))
        
        return self.page.makeHtml()
        # post_processing step. it makes a list of backlink and stuffs.
