import slo
import cursor
import keyboard
import root
from rootobject import rootobject
from rootobject import textformat
from rootobject import alert
from rootobject import pointer
from rootobject.buckerwindow import text
from rootobject.buckerwindow import textarea

import pygame
import math

resize_d = 'R_D'
resize_s = 'R_S'

# V 모든 윈도우(창) 오브젝트
class BuckerWindow(rootobject.RootObject):
    close = pygame.transform.scale(pygame.image.load('./res/image/icon/close.png'), (20, 20)).convert_alpha()
    text_format = rootobject.default_text_format

    def __init__(self, program: str):
        self.program = program

        self.x = 0
        self.y = 0
        self.title_height = 24
        self.width = 150
        self.height = 150
        self.title = 'BuckerWindow'
        self.normal_border_color = slo.bucker['window']['normal_border_color']
        self.highlighted_border_color = slo.bucker['window']['highlighted_border_color']
        self.background_color = slo.bucker['window']['background_color']

        self.exit = False

        if self.title == 'BuckerWindow':
            self.title = self.program.split('/')[-1]
            if '\\' in self.title:
                self.title = self.program.split('//')[-1]

        self.directory = self.program[:-len(self.title) - 1]

        self.elements = []
        try:
            self.build_program(self.program)
        except SyntaxError:
            self.exit = True

        self.highlighted_object = None

        self.width += 2
        self.height += self.title_height + 1

        self.target_x = self.x
        self.target_y = self.y

        self.x_moving = True
        self.y_moving = True

        self.x = cursor.position[0] - self.width / 2
        self.y = cursor.position[1] - self.height / 2

        self.text_format.color = self.background_color

        self.moving = False
        self.original_x = None
        self.original_y = None
        self.start_moving_x = None
        self.start_moving_y = None

        self.window = pygame.Surface((0, 0))
        self.surface = pygame.Surface((self.width - 2, self.height - self.title_height - 1))
        self.surface.fill(self.background_color)

        self.resize_mode = None
        self.original_width = self.width
        self.original_height = self.height
        self.width_target = self.width
        self.height_target = self.height
        self.width_move = False
        self.height_move = False
        
        self.minimum_width = 100
        self.minimum_height = 100

        self.build_surface()

    def tick(self):
        if self.x_moving:
            self.x += (self.target_x - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.x - self.target_x) < 1:
                self.x = self.target_x
                self.x_moving = False

        if self.y_moving:
            self.y += (self.target_y - self.y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.y - self.target_y) < 1:
                self.y = self.target_y
                self.y_moving = False

        if self.exit:
            self.y_moving = True
            self.target_y = root.display.size[1] + 1

            if root.display.size[1] <= self.y:
                self.destroy()

        if self.moving:
            self.target_x = cursor.position[0] - self.start_moving_x + self.original_x
            self.target_y = cursor.position[1] - self.start_moving_y + self.original_y

            self.x_moving = True
            self.y_moving = True

        if keyboard.keydown_key == pygame.K_q and (keyboard.lctrl or keyboard.rctrl) and rootobject.highlighted_object == self:
            self.exit = True

        if cursor.fpressed[0]:
            if self.x <= cursor.position[0] <= self.x + self.width:
                if self.y <= cursor.position[1] <= self.y + self.title_height and rootobject.get_on_cursor_window() == self:
                    self.moving = True
                    self.original_x = self.x
                    self.original_y = self.y
                    self.start_moving_x = cursor.position[0]
                    self.start_moving_y = cursor.position[1]

            if rootobject.get_on_cursor_window() == self:
                self.ahead()

            self.highlighted_object = None

        if cursor.epressed[0]:
            self.moving = False

            if self.x + self.width - self.title_height <= cursor.position[0] <= self.x + self.width and self.y <= cursor.position[1] <= self.y + self.title_height and rootobject.get_on_cursor_window() == self:
                self.exit = True

            self.resize_mode = None

        if rootobject.get_on_cursor_window() == self:
            if self.x + self.width - 6 <= cursor.position[0] and self.y < cursor.position[1] < self.y + self.height:
                pointer.pointer.mode = pointer.resize_width
                if cursor.fpressed[0]:
                    self.resize_mode = resize_d
                    self.original_width = self.width
            elif self.y + self.height - 6 <= cursor.position[1] and self.x < cursor.position[0] < self.x + self.width:
                pointer.pointer.mode = pointer.resize_height
                if cursor.fpressed[0]:
                    self.resize_mode = resize_s
                    self.original_height = self.height
            else:
                pointer.pointer.mode = pointer.normal
        else:
            pointer.pointer.mode = pointer.normal

        if self.resize_mode is not None:
            if self.resize_mode == resize_d:
                self.width_target = self.original_width + (cursor.position[0] - cursor.sposition[0])
                self.width_move = True
                if self.width_target < self.minimum_width:
                    self.width_target = self.minimum_width
            elif self.resize_mode == resize_s:
                self.height_target = self.original_height + (cursor.position[1] - cursor.sposition[1])
                self.height_move = True
                if self.height_target < self.minimum_height:
                    self.height_target = self.minimum_height

        if self.width_move:
            self.width += (self.width_target - self.width) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.width_target - self.width) < 1:
                self.width = self.width_target
                self.width_move = False
                self.build_surface()
        
        if self.height_move:
            self.height += (self.height_target - self.height) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.height_target - self.height) < 1:
                self.height = self.height_target
                self.height_move = False
                self.build_surface()

        if self.resize_mode is not None or self.width_move or self.height_move:
            self.build_surface()

        for element in self.elements:
            element.tick()

    def render(self):
        root.window.blit(self.window, (self.x, self.y))

        self.surface.fill(self.background_color)

        for element in self.elements:
            element.render()

        root.window.blit(self.surface, (1 + self.x, self.title_height + self.y))

    def build_surface(self):
        title_surface = self.text_format.render(self.title)

        border_color = self.highlighted_border_color if rootobject.highlighted_object == self else self.normal_border_color

        self.surface = pygame.Surface((round(self.width - 2), round(self.height - 1 - self.title_height)))

        self.window = pygame.Surface((self.width, self.height))
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, border_color, ((0, 0), (self.width, self.title_height)))
        pygame.draw.line(self.window, border_color, (0, 0), (0, self.height), 1)
        pygame.draw.line(self.window, border_color, (0, self.height), (self.width, self.height), 3)
        pygame.draw.line(self.window, border_color, (self.width, 0), (self.width, self.height), 3)
        self.window.blit(self.close, (self.width - self.close.get_width() - 2, 2))
        self.window.blit(title_surface, (rootobject.center(self.width, title_surface.get_width()), 0))

    def build_program(self, path):
        def exception(message):
            rootobject.add_object(alert.Alert(self.title, f'현재 실행하고 있는 프로그램의 {line_number + 1}번째 줄에 다음과 같은 오류가 발견되었습니다: \n' + str(message)))
            raise SyntaxError(message)

        try:
            code = open(path, 'r').read().split('\n')
        except UnicodeDecodeError:
            code = open(path, 'r', encoding='utf-8').read().split('\n')

        variables = {}

        for line_number in range(len(code)):
            line = code[line_number]

            if '?' in line: line = line[:line.index('?')]
            if len(line) <= 0: continue
            while line[-1] == ' ': line = line[:-1]

            sline = line.split()
            if sline[0] == 'set-raw':
                if len(sline) < 3:
                    exception('set-raw 구문의 변수 이름 또는 변수 값이 지정되어 있지 않습니다.')

                try:
                    variables[sline[1]] = eval(' '.join(sline[2:]))
                except Exception as e:
                    exception(str(e))

            elif sline[0] == 'set':
                if len(sline) < 3:
                    exception('set 구문의 변수 이름 또는 변수 값이 지정되어 있지 않습니다.')

                if sline[1] == 'TextFormat':
                    keys = ('font', 'size', 'color')

                    arguments = {}
                    for key in keys:
                        arguments[key] = None

                    for _i in range(len(sline)):
                        _i += 3
                        try:
                            word = sline[_i]
                        except IndexError:
                            break

                        if _i % 2 == 0:
                            if '_' in word: word = word.replace('_', ' ')
                            if '\\ ' in word: word = word.replace('\\ ', '_')

                            if last_key in keys:
                                if word[0] == '$':
                                    arguments[last_key] = variables[word]
                                else:
                                    arguments[last_key] = eval(word)
                        else:
                            last_key = word

                    arguments['font'] = arguments['font'].replace('|', '/')

                    if arguments['font'][0] == '%':
                        arguments['font'] = self.directory + arguments['font'][1:]

                    variables[sline[2]] = textformat.TextFormat(font=arguments['font'], size=arguments['size'], colour=arguments['color'])

            elif sline[0] == 'window-set':
                # noinspection PyBroadException
                try:
                    if sline[1] == 'x': self.x = eval(' '.join(sline[2:]))
                    elif sline[1] == 'y': self.y = eval(' '.join(sline[2:]))
                    elif sline[1] == 'title_height': self.title_height = eval(' '.join(sline[2:]))
                    elif sline[1] == 'width': self.width = eval(' '.join(sline[2:]))
                    elif sline[1] == 'height': self.height = eval(' '.join(sline[2:]))
                    elif sline[1] == 'title': self.title = eval(' '.join(sline[2:]))
                    elif sline[1] == 'border_color': self.normal_border_color = eval(' '.join(sline[2:]))
                    elif sline[1] == 'background_color': self.background_color = eval(' '.join(sline[2:]))
                    elif sline[1] == 'highlighted_background_color': self.highlighted_border_color = eval(' '.join(sline[2:]))
                except Exception as e:
                    exception(e)

            elif sline[0] == 'window-add':
                if len(sline) < 2:
                    exception('window-add 구문의 변수형이 지정되어 있지 않습니다.')

                arguments = {}
                last_key = ''

                if sline[1] == 'TextArea':
                    keys = ('x', 'y', 'width', 'height', 'value', 'text_format', 'background_color', 'writable')

                    for key in keys:
                        arguments[key] = None

                    for _i in range(len(sline)):
                        _i += 2
                        try:
                            word = sline[_i]
                        except IndexError:
                            break

                        if _i % 2 == 1:
                            if '_' in word: word = word.replace('_', ' ')
                            if '\\ ' in word: word = word.replace('\\ ', '_')

                            if last_key in keys:
                                if word[0] == '$':
                                    arguments[last_key] = variables[word]
                                else:
                                    arguments[last_key] = eval(word)
                        else:
                            last_key = word

                    self.elements.append(textarea.TextArea(x=arguments['x'], y=arguments['y'], width=arguments['width'], height=arguments['height'], value=arguments['value'], text_format=arguments['text_format'], background_color=arguments['background_color'], writable=arguments['writable'], window=self))
                elif sline[1] == 'Text':
                    keys = ('x', 'y', 'text', 'text_format')

                    for key in keys:
                        arguments[key] = None

                    for _i in range(len(sline)):
                        _i += 2
                        try:
                            word = sline[_i]
                        except IndexError:
                            break

                        if _i % 2 == 1:
                            if '_' in word: word = word.replace('_', ' ')
                            if '\\ ' in word: word = word.replace('\\ ', '_')

                            if last_key in keys:
                                if word[0] == '$':
                                    if word not in variables.keys():
                                        exception(f'{word}라는 변수는 지정되지 않았습니다.\n변수 형에 언더바(_)를 사용했을 가능성이 있습니다.')
                                    arguments[last_key] = variables[word]
                                else:
                                    try:
                                        arguments[last_key] = eval(word)
                                    except NameError as e:
                                        exception(f'{e}')
                        else:
                            last_key = word

                    self.elements.append(text.Text(x=arguments['x'], y=arguments['y'], text=arguments['text'], text_format=arguments['text_format'], window=self))
                else:
                    exception(f'변수형 {sline[1]}을(를) 알 수 없습니다.')

            else:
                exception(f'명령어 {sline[0]}을(를) 알 수 없습니다.')

        return False