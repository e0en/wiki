class WikiElem:

    def __init__(self, eType, value=None):
        self.t = eType
        self.v = value


class WikiChapter:

    def __init__(self, title=''):
        self.title = title
        self.anchorText = ''
        self.subChapters = []
        self.intro = []

    def add(self, l):
        self.intro += l


class WikiImage:

    def __init__(self):
        self.src = ''
        self.num = ''
        self.dim = (0, 0)
        self.anchorTxt = ''


class Page:

    def __init__(self, title):
        self.title = []
        self.chapters = [WikiChapter()]
        # flash, equation, Code, quotation, etc..
        self.curChapter = self.chapters[-1]
        self.intraLinks = []

    def makeHtml(self):
        return ''
