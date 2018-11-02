# coding=utf-8

import sys
import time

if len(sys.argv) <= 1:
    exit()

start_time = time.time()

filepath = sys.argv[1]
filename = filepath.split('\\')[-1].split('/')[-1]

data = open(filepath, 'r').read()

datas = data.split('\n')

for i in range(len(datas)):
    if ';' in datas[i]:
        if '\'' in datas[i]:
            pass
        else:
            datas[i] = datas[i][:datas[i].index(';')]

    datas[i] += '\n'

def error(file: str, ln: int, msg: str):
    print(f'에러 발생:\n  파일 \'{file}\'의 {ln}번 째 줄\n    {datas[ln][:-1]}\n{msg}')
    exit()

var = {}

line_number = 0
while line_number < len(datas):
    if datas[line_number] != '\n':
        tokens = []

        var_name = 'var name'
        function_name = 'function name'

        function_parameters = 'function parameters'

        set_to = 'set to'
        equals = 'equals'

        string = 'string'
        boolean = 'boolean'
        true, false = 'True', 'False'

        now_word = ''
        now_mode = None  # None - var name

        for char in datas[line_number]:
            # print(f'\tln {line_number}\tCHAR\t{[now_word]} {[char]}')
            if char in (' ', '\n'):
                if now_word == ':=':
                    tokens.append((set_to,))
                    now_word = ''
                elif now_word == '=':
                    tokens.append((equals,))
                    now_word = ''
                elif now_word in (true, false):
                    if now_word == true:
                        tokens.append((boolean, True))
                    else:
                        tokens.append((boolean, False))
                    now_word = ''
                elif now_mode == 'string':
                    if now_word[-1] == '\'':
                        tokens.append((string, now_word[1:-1]))
                        now_word = ''
                    else:
                        now_word += char
                else:
                    tokens.append((var_name, now_word))
                    now_word = ''
            elif char == '(':
                tokens.append((function_name, now_word))
                now_mode = function_parameters
                now_word = ''
            elif char == ')':
                if now_mode is None:
                    tokens.append((var_name, now_word))
                    now_word = ''
            else:
                if now_word == '' and char == '\'':
                    now_mode = string
                now_word += char

        while True:
            # print(f'\tln {line_number}\tTOKEN\t{tokens}')
            if len(tokens) >= 2:
                if tokens[0][0] + tokens[1][0] == function_name + var_name:
                    if tokens[1][1] not in var.keys():
                        error(filename, line_number, f'변수 \'{tokens[1][1]}\'을(를) 찾을 수 없습니다.')
                    print(var[tokens[1][1]])
                    break
                if tokens[0][0] + tokens[1][0] == function_name + string:
                    print(tokens[1][1])
                    break
            if len(tokens) >= 3:
                if tokens[0][0] + tokens[1][0] == var_name + set_to:
                    if len(tokens) >= 5:
                        if tokens[-2][0] == equals:
                            if tokens[-3][0] == tokens[-1][0] and tokens[-1][0] != var_name:
                                tokens = tokens[:-3] + [(boolean, tokens[-3][1] == tokens[-1][1])]
                            elif tokens[-3][0] + tokens[-1][0] in (var_name + string, string + var_name):
                                if tokens[-3][0] == var_name:
                                    if tokens[-3][1] not in var.keys():
                                        error(filename, line_number, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                                    tokens = tokens[:-3] + [(boolean, var[tokens[-3][1]] == tokens[-1][1])]
                                elif tokens[-3][0] == string:
                                    if tokens[-1][1] not in var.keys():
                                        error(filename, line_number, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                                    tokens = tokens[:-3] + [(boolean, var[tokens[-1][1]] == tokens[-3][1])]
                    else:
                        if tokens[2][0] == string:
                            var[tokens[0][1]] = tokens[2][1]
                            break
                        if tokens[2][0] == boolean:
                            var[tokens[0][1]] = tokens[2][1]
                            break
        # print(f'\tln {line_number}\tHANDLE\t{var}')

    line_number += 1

print()
print(f'경과시간: {(time.time() - start_time) * 1_000}ms')
