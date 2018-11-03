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

variable_not_found_error = '변수없음'
operator_invalid = '연산자오용'

def error(file: str, ln: int, error_type: str, msg: str):
    print(f'에러 발생:\n  파일 \'{file}\'의 {ln + 1}번 째 줄\n    {datas[ln][:-1]}\n{error_type}: {msg}')
    exit()

var = {}

def just_have(a, b):
    for I in range(len(a)):
        if a[I] not in b:
            return False
    return True

line_number = 0
while line_number < len(datas):
    if datas[line_number] != '\n':
        tokens = []

        function_name = '함수'

        set_to = '설정'
        equals = '같음'
        add = '더하기'
        sub = '빼기'
        times = '곱하기'
        div = '나누기'
        power = '제곱'

        var_name = '변수'
        string = '문자열'
        integer = '정수'
        boolean = '불린'

        true, false = 'True', 'False'

        popup = 'popup'

        now_word = ''
        now_mode = None  # None - var name

        for char in datas[line_number]:
            # print(f'\tln {line_number}\tCHAR\t{[now_word]} {[char]}\tnm {now_mode}\t{tokens}')
            if char in (' ', '\n'):
                if now_word == ':=':
                    tokens.append((set_to,))
                    now_word = ''
                elif now_word == '=':
                    tokens.append((equals,))
                    now_word = ''
                elif now_word == '+':
                    tokens.append((add,))
                    now_word = ''
                elif now_word == '-':
                    tokens.append((sub,))
                    now_word = ''
                elif now_word == '*':
                    tokens.append((times,))
                    now_word = ''
                elif now_word == '/':
                    tokens.append((div,))
                    now_word = ''
                elif now_word == '**':
                    tokens.append((power,))
                    now_word = ''
                elif now_word in (true, false):
                    if now_word == true:
                        tokens.append((boolean, True))
                    else:
                        tokens.append((boolean, False))
                    now_word = ''
                elif now_mode == string:
                    if now_word[-1] == '\'':
                        tokens.append((string, now_word[1:-1]))
                        now_word = ''
                        now_mode = None
                    else:
                        now_word += char
                elif now_mode == integer:
                    tokens.append((integer, int(now_word)))
                    now_mode = None
                    now_word = ''
                else:
                    if now_mode is None and now_word != '':
                        tokens.append((var_name, now_word))
                        now_word = ''
            elif char == '(':
                tokens.append((function_name, now_word))
                now_word = ''
            elif char == ')':
                if now_mode is None and now_word != '':
                    tokens.append((var_name, now_word))
                    now_word = ''
            else:
                if now_word == '' and char == '\'':
                    now_mode = string
                elif now_word == '' and char in '0123456789':
                    now_mode = integer
                now_word += char

        while True:
            print(f'\tln {line_number}\tTOKEN\t{tokens}')
            if len(tokens) >= 3:
                if tokens[-2][0] == equals:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(boolean, var[tokens[-3][1]] == var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(boolean, tokens[-3][1] == tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + string, string + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(boolean, var[tokens[-3][1]] == tokens[-1][1])]
                            continue
                        elif tokens[-3][0] == string:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(boolean, var[tokens[-1][1]] == tokens[-3][1])]
                            continue
                elif tokens[-2][0] == add:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] + var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(integer, tokens[-3][1] + tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + integer, integer + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] + tokens[-1][1])]
                            continue
                        elif tokens[-1][0] == var_name:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-1][1]] + tokens[-3][1])]
                            continue
                    else:
                        error(filename, line_number, operator_invalid, f'{tokens[-3][0]}와(과) {tokens[-1][0]}은(는) {add} 연산(+)을 할 수 없는 변수형입니다.')
                elif tokens[-2][0] == sub:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] - var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(integer, tokens[-3][1] - tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + integer, integer + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] - tokens[-1][1])]
                            continue
                        elif tokens[-1][0] == var_name:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-1][1]] - tokens[-3][1])]
                            continue
                    else:
                        error(filename, line_number, operator_invalid, f'{tokens[-3][0]}와(과) {tokens[-1][0]}은(는) {sub} 연산(-)을 할 수 없는 변수형입니다.')
                elif tokens[-2][0] == times:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] * var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(integer, tokens[-3][1] * tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + integer, integer + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] * tokens[-1][1])]
                            continue
                        elif tokens[-1][0] == var_name:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-1][1]] * tokens[-3][1])]
                            continue
                    else:
                        error(filename, line_number, operator_invalid, f'{tokens[-3][0]}와(과) {tokens[-1][0]}은(는) {times} 연산(*)을 할 수 없는 변수형입니다.')
                elif tokens[-2][0] == div:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] / var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(integer, tokens[-3][1] / tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + integer, integer + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] / tokens[-1][1])]
                            continue
                        elif tokens[-1][0] == var_name:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-1][1]] / tokens[-3][1])]
                            continue
                    else:
                        error(filename, line_number, operator_invalid, f'{tokens[-3][0]}와(과) {tokens[-1][0]}은(는) {div} 연산(/)을 할 수 없는 변수형입니다.')
                elif tokens[-2][0] == power:
                    if tokens[-3][0] == tokens[-1][0]:
                        if tokens[-1][0] == var_name:
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] ** var[tokens[-1][1]])]
                            continue
                        else:
                            tokens = tokens[:-3] + [(integer, tokens[-3][1] ** tokens[-1][1])]
                            continue
                    elif tokens[-3][0] + tokens[-1][0] in (var_name + integer, integer + var_name):
                        if tokens[-3][0] == var_name:
                            if tokens[-3][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-3][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-3][1]] ** tokens[-1][1])]
                            continue
                        elif tokens[-1][0] == var_name:
                            if tokens[-1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[-1][1]}\'을(를) 찾을 수 없습니다.')
                            tokens = tokens[:-3] + [(integer, var[tokens[-1][1]] ** tokens[-3][1])]
                            continue
                    else:
                        error(filename, line_number, operator_invalid, f'{tokens[-3][0]}와(과) {tokens[-1][0]}은(는) {power} 연산(**)을 할 수 없는 변수형입니다.')
                if tokens[0][0] + tokens[1][0] == var_name + set_to:
                    if tokens[2][0] == string:
                        var[tokens[0][1]] = tokens[2][1]
                        break
                    elif tokens[2][0] == integer:
                        var[tokens[0][1]] = tokens[2][1]
                        break
                    elif tokens[2][0] == boolean:
                        var[tokens[0][1]] = tokens[2][1]
                        break
            elif len(tokens) >= 2:
                if tokens[0][0] == function_name:
                    if tokens[0][1] == popup:
                        if tokens[1][0] == var_name:
                            if tokens[1][1] not in var.keys():
                                error(filename, line_number, variable_not_found_error, f'변수 \'{tokens[1][1]}\'을(를) 찾을 수 없습니다.')
                            print(var[tokens[1][1]])
                            break
                        elif tokens[1][0] == string:
                            print(tokens[1][1])
                            break
                        elif tokens[1][0] == integer:
                            print(tokens[1][1])
                            break

        print(f'\tln {line_number}\tVAR\t{var}')

    line_number += 1

print()
print(f'경과시간: {(time.time() - start_time) * 1_000}ms')
