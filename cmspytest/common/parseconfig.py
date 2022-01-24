import base64
import datetime
import os
import json
import time
from fake_useragent import UserAgent
from configobj import ConfigObj

curpath = os.path.abspath('.')
conf_ini = curpath + "\\conf\\config.ini"
configini = ConfigObj(conf_ini, encoding='UTF8')
env = configini['env']['env']

def inappropriate_keyword(str1,str2):
    """search inappropriate_keyword，contain:1，not contain:0"""
    """str1：input_str
       str2：inappropriate_keyword"""
    str3 = str2.split(',')
    type = 0
    for i in range(len(str3)):
        if str3[i] in str1:
            type = 1
            break
    return type

def base64_encode(filefath):
    """filefath：robotframework：C:/Users/suxiong/Desktop/test002.txt python:r'C:\path' """
    with open(filefath, "rb") as f:
        bs64_str = base64.b64encode(f.read()).decode('utf8')
    return bs64_str

def Throw_exception():
    """Throw_exception"""
    raise Exception(print('Throw_exception'))

def dateupdate(date):
    """Update str to datetime"""
    try:
        time.strptime(date, "%Y-%m-%d")
        sign = 1
    except:
        sign = 0
    if sign == 1:
        b = datetime.datetime.strptime(str(date),"%Y-%m-%d")
    else:
        b = date
    return b

def dict_update_time(filename,a,b="0"):
    """update dict and call[dateupdate] Update str to datetime"""
    """filename:file name(.json)
       a: update dict{}"""
    filedir1 = os.path.abspath('.')
    filedir2 = r'\cms-api-qa\TestCases\Json'
    filedir = filedir1 + '\\' + filedir2
    filedir_t = filedir + '\\' +filename
    # filenames = os.listdir(filedir_t)

    dict = {}
    with open(filedir_t,'rb') as f:
        data = json.load(f)
        for key in a:
            a[key] = dateupdate(a[key])
            for key1 in data:
                data[key1] = dateupdate(data[key1])
            data[key] = a[key]
        dict = data

    if b == "1":
        with open(filedir_t, 'w') as f:
            json.dump(dict,f)
    return dict

def params_split(dict):
    """Split Repeat Parameter(dict) """
    params = ''
    for key in dict:
        if type(dict[key]) == str:
            lenkey = dict[key].split(',')
            for i in range(0, len(lenkey)):
                if params == '':
                    params = params + key + '=' + lenkey[i]
                else:
                    params = params + '&' + key + '=' + lenkey[i]
        else:
            if params == '':
                params = params + key + '=' + str(dict[key])
            else:
                params = params + '&' + key + '=' + str(dict[key])
    return params

def emptyparameter(a):
    """del emptyparameter (type:dict)"""
    dict = {}
    for key in a:
        if a[key] != "":
            dict[key] = a[key]
    return dict

def fileuploadparameter(filename):
    """fileupload file split(return:type)"""
    image = ['jpg','jpeg','png','gif','webp']
    other = ['jpe','jif','jfif','jfi','mpg','mp2','mpe','mpv','ogg','mp4','m4p','m4v','wmv','mov','asf','qt','flv','avchd','m3u8','x-matroska']

    filetype = filename.split('.')[-1]
    if filetype in image:
        type = 'image/' + filetype
    elif filetype == 'txt':
        type = 'text/plain'
    elif filetype == 'pdf':
        type = 'application/pdf'
    elif filetype == 'json':
        type = 'application/json'
    elif filetype == 'webm':
        type = 'video/webm'
    elif filetype == 'mpeg':
        type = 'video/mpeg'
    elif filetype == 'ts':
        type = 'video/mp2t'
    elif filetype == '3gp':
        type = 'video/3gpp'
    elif filetype == 'avi':
        type = 'video/x-msvideo'
    elif filetype == 'swf':
        type = 'application/x-shockwave-flash'
    elif filetype in other:
        type = 'application/octet-stream'
    else:
        type = filetype
    return type

def anyequal(*args):
    """assert equal(*args)"""
    for i in range(1,len(args)):
        assert args[i-1] == args[i],print(args[i-1],args[i])
        pass
    return 0

def updatejson(filename,a,b="0"):
    """a:uodatedict,b=0:not update old jsonfile,b=1 update new jsonfile"""
    filedir1 = os.path.abspath('.')
    filedir2 = r'\cms-api-qa\TestCases\Json'
    filedir = filedir1 + '\\' + filedir2
    filedir_t = filedir + '\\' +filename
    # filenames = os.listdir(filedir_t)

    dict = {}
    with open(filedir_t,'rb') as f:
        data = json.load(f)
        for key in a:
            data[key] = a[key]
        dict = data

    if b == "1":
        with open(filedir_t, 'w') as f:
            json.dump(dict,f)
    return dict

def jsonDifference(a,b):
    dict = {}
    try:
        for i in a:
            for j in b:
                if i not in b:
                    dict[i] = a[i]
                if j not in a:
                    dict[j] = b[j]
    except:
        pass
    return dict

def loadjson(filename):
    filedir1 = os.path.abspath('.')
    filedir2 = r'\cms-api-qa\TestCases\Json'
    filedir = filedir1 + '\\' + filedir2
    # filedir = r'C:\Users\Willy Wang\Desktop\cms-api\cms-api-qa\TestCases\Json'
    filedir_t = filedir + '\\' + filename
    with open(filedir_t,'rb') as f:
        data = json.load(f)
    return data

def browser_useragent():
    "Create useragent for browser,No parameters are required"
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return headers

def dictsmerge(*args):
    """Merge multiple dictionaries"""
    dict = {}
    for i in args:
        dict.update(i)
    return dict

def strfind(str1,str2):
    """str1.count(str2)"""
    num = str1.count(str2)
    return num


def file_name(file_dir):
    """
    file_dir:只填写文件名时，默认搜索本文件同级目录下的该文件，搜索其他目录时，可带路径
    当前目录路径：root
    当前路径下所有子目录：dirs
    当前路径下所有非目录子文件：files
    ## 可循环遍历，当前只遍历文件夹第一层
    """
    for root, dirs, files in os.walk(file_dir):
        return root,dirs,files

