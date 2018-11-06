import slo
import color
from rootobject import textformat
from rootobject.buckerwindow import buckerwindowelement

class Text(buckerwindowelement.BuckerWindowElement):
    def __init__(self, x=None, y=None, text=None, text_format=None, window=None):
        super().__init__(window)

        self.x = x
        self.y = y
        self.text = text
        self.text_format = text_format

        if self.x is None:
            self.x = 0
        if self.y is None:
            self.y = 0
        if self.text is None:
            self.text = ''
        if self.text_format is None:
            self.text_format = textformat.TextFormat(slo.slo['appearance']['font'], 18, color.background)

        self.surface = self.text_format.render(self.text)