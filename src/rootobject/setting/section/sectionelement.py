from rootobject import rootobject
from rootobject.setting.section import section

class SectionElement(rootobject.RootObject):
    section: section.Section

    def destroy(self):
        self.section.elements.remove(self)