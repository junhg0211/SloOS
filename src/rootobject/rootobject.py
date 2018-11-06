import slo
import cursor
import color
from rootobject import textformat

objects = []

highlighted_object = None

def remove_object_by_type(_type):
    for OBJ in objects:
        if type(OBJ) == _type:
            OBJ.destroy()

def add_object(_obj):
    objects.append(_obj)

highlight = None

# V 모든 화면 오브젝트의 부모 클래스 RootObject
class RootObject(object):
    def tick(self):
        pass

    def render(self):
        pass

    def destroy(self):
        objects.remove(self)

    def ahead(self):
        objects.remove(self)
        objects.append(self)

default_text_format = textformat.TextFormat(slo.slo['appearance']['font'], 18, color.text)

def center(x, y):
    return (x - y) / 2

# V 커서가 가르키고 있는 윈도우를 출력함.
def get_on_cursor_window():
    banned_areas = []  # [(x, y, width, height)]
    for I in range(len(objects))[::-1]:
        this_object = objects[I]

        try:
            (this_object.y, this_object.width)
        except AttributeError:
            continue

        banned = False

        if this_object.x <= cursor.position[0] <= this_object.x + this_object.width and this_object.y <= cursor.position[1] <= this_object.y + this_object.height:
            for banned_area in banned_areas:
                if banned_area[0] <= cursor.position[0] <= banned_area[0] + banned_area[2] and banned_area[1] <= cursor.position[1] <= banned_area[1] + banned_area[3]:
                    banned = True
                    break

            if not banned:
                return this_object

        banned_areas.append((this_object.x, this_object.y, this_object.width, this_object.height))