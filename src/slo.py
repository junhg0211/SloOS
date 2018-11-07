import configparser
import codecs
import os

os.chdir('\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1]))

slo = None
bucker = None
lastest = None
lockscreen = None
surfer = None
setting = None

def configparser_parse(path: str):
    config = configparser.ConfigParser()
    try:
        config.read_file(codecs.open(path, 'r', encoding='utf-8'))
    except UnicodeDecodeError:
        config.read_file(codecs.open(path, 'r'))

    result = {}

    for section in config.sections():
        result[section] = {}
        for key in config[section].keys():
            result[section][key] = eval(config[section][key])

    return result

def configparser_write(path, value: dict):
    cfgfile = open(path, 'w', encoding='utf-8')
    config = configparser.ConfigParser()

    for key in value.keys():
        config.add_section(key)
        for name in value[key].keys():
            if type(value[key][name]) == str:
                config.set(key, name, f'\'{value[key][name]}\'')
            else:
                config.set(key, name, str(value[key][name]))

    config.write(cfgfile)
    cfgfile.close()

def load():
    global slo
    global bucker
    global lastest
    global lockscreen
    global surfer
    global setting

    slo = configparser_parse('./slo/slo.ini')
    bucker = configparser_parse('./slo/bucker.ini')
    lastest = configparser_parse('./slo/lastest.ini')
    lockscreen = configparser_parse('./slo/lockscreen.ini')
    surfer = configparser_parse('./slo/surfer.ini')
    setting = configparser_parse('./slo/setting.ini')

def save():
    configparser_write('./slo/slo.ini', slo)
    configparser_write('./slo/bucker.ini', bucker)
    configparser_write('./slo/lastest.ini', lastest)
    configparser_write('./slo/lockscreen.ini', lockscreen)
    configparser_write('./slo/surfer.ini', surfer)
    configparser_write('./slo/setting.ini', setting)

load()
