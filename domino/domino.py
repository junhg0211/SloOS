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

document = []

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

        condition_if = '만약'
        condition_else = '아니면'
        block_starter = '블럭|'

        true, false = 'True', 'False'

        popup = 'popup'

        now_word = ''
        now_mode = None  # None - var name

        for char in datas[line_number]:
            print(f'\tln {line_number + 1}\tCHAR\t{[now_word]} {[char]}\tnm {now_mode}\t{tokens}')
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
                elif now_word == ',':
                    pass
                elif now_word == '?':
                    tokens.append((block_starter,))
                    now_word = ''
                elif now_word == 'if':
                    tokens.append((condition_if, ))
                    now_word = ''
                elif now_word == 'else':
                    tokens.append((condition_else,))
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

        document.append(tokens)
        print(f'\tln {line_number + 1}\tTOKEN\t{tokens}')
    else:
        document.append([])

    line_number += 1

print()
for i in range(len(document)):
    print(f'\tln {i}\tTOKEN\t{document[i]}')
print()

def var_to_value(_tokens):
    for I in range(len(_tokens)):
        if _tokens[I][0] == var_name:
            if _tokens[I][1] in var.keys():
                _tokens[I] = var[_tokens[I][1]]
                print(f'\tln {line_number + 1}\tTOKEN\t{_tokens}')
    return _tokens

line_number = 0
condition_do = None
while line_number < len(document):
    print(f'\tln {line_number + 1}\tTOKEN\t{document[line_number]}')
    
    document[line_number] = var_to_value(document[line_number])

    while True:
        if not document[line_number]:
            break

        if document[line_number][0][0] != block_starter:
            print(f'\tln {line_number + 1}\tTOKEN\t{document[line_number]}\t{condition_do}')

            if len(document[line_number]) >= 3:
                if document[line_number][-2][0] == equals:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(boolean, document[line_number][-3][1] == document[line_number][-1][1])]
                        continue
                elif document[line_number][-2][0] == add:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(integer, document[line_number][-3][1] + document[line_number][-1][1])]
                        continue
                    else:
                        error(filename, line_number, operator_invalid, f'{document[line_number][-3][0]}와(과) {document[line_number][-1][0]}은(는) {add} 연산(+)을 할 수 없는 변수형입니다.')
                elif document[line_number][-2][0] == sub:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(integer, document[line_number][-3][1] - document[line_number][-1][1])]
                        continue
                    else:
                        error(filename, line_number, operator_invalid, f'{document[line_number][-3][0]}와(과) {document[line_number][-1][0]}은(는) {sub} 연산(-)을 할 수 없는 변수형입니다.')
                elif document[line_number][-2][0] == times:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(integer, document[line_number][-3][1] * document[line_number][-1][1])]
                        continue
                    else:
                        error(filename, line_number, operator_invalid, f'{document[line_number][-3][0]}와(과) {document[line_number][-1][0]}은(는) {times} 연산(*)을 할 수 없는 변수형입니다.')
                elif document[line_number][-2][0] == div:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(integer, document[line_number][-3][1] / document[line_number][-1][1])]
                        continue
                    else:
                        error(filename, line_number, operator_invalid, f'{document[line_number][-3][0]}와(과) {document[line_number][-1][0]}은(는) {div} 연산(/)을 할 수 없는 변수형입니다.')
                elif document[line_number][-2][0] == power:
                    if document[line_number][-3][0] == document[line_number][-1][0]:
                        document[line_number] = document[line_number][:-3] + [(integer, document[line_number][-3][1] ** document[line_number][-1][1])]
                        continue
                    else:
                        error(filename, line_number, operator_invalid, f'{document[line_number][-3][0]}와(과) {document[line_number][-1][0]}은(는) {power} 연산(**)을 할 수 없는 변수형입니다.')
                if document[line_number][0][0] + document[line_number][1][0] == var_name + set_to:
                    if document[line_number][2][0] == string:
                        var[document[line_number][0][1]] = (string, document[line_number][2][1])
                        break
                    elif document[line_number][2][0] == integer:
                        var[document[line_number][0][1]] = (integer, document[line_number][2][1])
                        break
                    elif document[line_number][2][0] == boolean:
                        var[document[line_number][0][1]] = (boolean, document[line_number][2][1])
                        break
            elif len(document[line_number]) >= 2:
                if document[line_number][0][0] == function_name:
                    if document[line_number][0][1] == popup:
                        if document[line_number][1][0] in (string, integer, boolean):
                            print(document[line_number][1][1])
                            break
                elif document[line_number][0][0] == condition_if:
                    condition_do = document[line_number][1] == (boolean, True)
                    break
            else:
                if document[line_number][0][0] == condition_else:
                    if condition_do is False:
                        condition_do = True
                        break
                    elif condition_do:
                        condition_do = False
                        break
                    else:
                        error(filename, line_number, None, '으악')
        else:
            if condition_do:
                del document[line_number][0]
            else:
                break

    line_number += 1

    print(f'\tln {line_number + 1}\tVAR\t{var}')

print()
print(f'경과시간: {(time.time() - start_time) * 1_000}ms')
