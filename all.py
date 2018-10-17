import base64
import binascii
import hashlib
import hmac
import json
import pickle
import random
import re
import time
from queue import Queue
from urllib.parse import quote

import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import config
from utils import timeout_func, print_red, print_blue

configs = config.configs


def tecent():
    appid = '1251291677'
    bucket = ''
    howlong = 30
    secretid = 'AKIDrfIoAUwbP2Ukokw8YlmbFhx2zpUxRKEx'
    secretkey = 'gEat45GLFxTcZLUUI5lFYeZHnD0d9Tek'
    now = int(time.time())
    rdm = random.randint(0, 999999999)

    text = 'a=' + appid + '&b=' + bucket + '&k=' + secretid + '&e=' + str(now + howlong) + '&t=' + str(
            now) + '&r=' + str(rdm) + '&f='
    hexstring = hmac.new(secretkey.encode('utf-8'), text.encode('utf-8'), hashlib.sha1).hexdigest()
    binstring = binascii.unhexlify(hexstring)

    signed = base64.b64encode(binstring + text.encode('utf-8')).rstrip()

    u = 'http://recognition.image.myqcloud.com/ocr/general'
    headers = {
        'host':          'recognition.image.myqcloud.com',
        'content-type':  'application/json',
        'authorization': signed,
    }

    with open('img/test.png', 'rb') as f:
        code = base64.b64encode(f.read())
        f.close()

    data = {
        'appid': appid,
        'image': bytes.decode(code, 'utf-8')
    }
    c = requests.post(u, data=json.dumps(data), headers=headers).content
    c = c.decode('utf-8')
    c = json.loads(c)
    s = ''
    try:
        for d in c['data']['items']:
            s += d['itemstring']
        return s
    except:
        return s


@timeout_func(1)
def google():
    with open('img/test.png', 'rb') as f:
        data = base64.b64encode(f.read())
        f.close()
    b = bytes.decode(data)

    u = 'https://vision.googleapis.com/v1/images:annotate'
    API_KEY = 'AIzaSyCfWz3cJsTgrZN4jfazFNX-PFyE8pNpwN8'
    u += '?key=' + API_KEY

    r = {
        'requests': [
            {
                'image':    {
                    'content': b,
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION'
                    }
                ]
            }
        ]
    }
    try:
        c = requests.post(u,
                          data=json.dumps(r),
                          proxies={'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'}).content.decode(
                'utf-8')
        c = json.loads(c)
    except Exception as e:
        print('Proxy Error')
        exit(-1)
    try:
        description_ = c['responses'][0]['textAnnotations'][0]['description']
        description_ = description_.replace('\n', '')
        return description_
    except:
        return ''


@timeout_func(1.5)
def google_translate(word, target='en'):
    API_KEY = 'AIzaSyCfWz3cJsTgrZN4jfazFNX-PFyE8pNpwN8'

    u = 'https://translation.googleapis.com/language/translate/v2'

    data = {
        'q':      word,
        'target': target,
        'key':    API_KEY
    }
    p = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
    c = requests.post(u, data=data, proxies=p).content.decode('utf-8')
    c = json.loads(c)
    try:
        text_: str = c['data']['translations'][0]['translatedText']
        text_ = text_.replace('&#39;', "'")
        return text_
    except:
        return ''


def baidu():
    from aip import AipOcr

    """ 你的 APPID AK SK """
    APP_ID = '11782660'
    API_KEY = 'qWXZ11eNO2Wpm9Sub0e7XT6C'
    SECRET_KEY = 'tGapovnxcerTXTP8jG3ADPbrZ2IDjOSA'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    """ 读取图片 """

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = get_file_content('img/test.png')

    # """ 调用通用文字识别, 图片参数为本地图片 """
    # client.basicGeneral(image)

    """ 如果有可选参数 """
    options = {}
    # options["language_type"] = "CHN_ENG"
    # options["detect_direction"] = "true"
    # options["detect_language"] = "true"
    # options["probability"] = "true"

    """ 带参数调用通用文字识别, 图片参数为本地图片 """
    a = client.basicGeneral(image, options)
    result = []
    try:
        for r in a['words_result']:
            result.append(r['words'])
        result = ' '.join(result)
    except:
        result = ''
    return result


def youdao():
    import random
    import base64

    appKey = '01c0ecf37a7cbd94'
    secretKey = 'ygerEwqc1uL2K45LWe3WPQwae9zeU4Yo'

    f = open('img/test.png', 'rb')  # 二进制方式打开图文件
    img = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
    img = bytes.decode(img)
    f.close()

    detectType = '10012'
    imageType = '1'
    langType = 'zh-en'
    salt = random.randint(1, 65536)

    sign = appKey + img + str(salt) + secretKey
    sign = sign.encode('utf-8')
    m1 = hashlib.md5(sign)
    sign = m1.hexdigest()
    data = {
        'appKey':     appKey,
        'img':        img,
        'detectType': detectType,
        'imageType':  imageType,
        'langType':   langType,
        'salt':       str(salt),
        'sign':       sign
    }
    resp = requests.post('http://openapi.youdao.com/ocrapi', data=data)
    try:
        c = resp.content.decode('utf-8')
        c = json.loads(c)
    except:
        s = ''

    s = ''
    try:
        for a in c['Result']['regions'][0]['lines']:
            for aa in a['words']:
                s += aa['word']
    except:
        return '不可识别'
    return s


def tencent_translate(target_text, source='zh', target='en'):
    secretid = 'AKIDrfIoAUwbP2Ukokw8YlmbFhx2zpUxRKEx'
    secretkey = 'gEat45GLFxTcZLUUI5lFYeZHnD0d9Tek'
    now = int(time.time())
    rdm = random.randint(0, 999999999)

    u = 'https://tmt.tencentcloudapi.com/?'
    params = {
        'Action':     'TextTranslate',
        'ProjectId':  '1123265',
        'Source':     source,
        'SourceText': target_text,
        'Target':     target,
        'Region':     'ap-guangzhou',
        'Timestamp':  str(now),
        'SecretId':   secretid,
        'Version':    '2018-03-21',
        'Nonce':      str(rdm),
    }

    params = sorted(params.items(), key=lambda x: x[0])
    first = params[0]
    params = dict(params)

    signed = ''
    for param in params.items():
        if param == first:
            signed += param[0] + '=' + param[1]
        else:
            signed += '&' + param[0] + '=' + param[1]

    signed = 'GET' + 'tmt.tencentcloudapi.com/?' + signed

    hexstring = hmac.new(secretkey.encode('utf-8'), signed.encode('utf-8'), hashlib.sha1).digest()
    signed = base64.b64encode(hexstring)

    s = bytes.decode(signed, 'utf-8')
    s = quote(s)
    params['Signature'] = s
    for param in params.items():
        if param == first:
            u += param[0] + '=' + param[1]
        else:
            u += '&' + param[0] + '=' + param[1]
    c = requests.get(u).content
    c = c.decode('utf-8')
    c = json.loads(c)
    try:
        return c['Response']['TargetText']
    except:
        return ''


def baidu_translate(text, source='zh', target='en'):
    import random

    appid = '20180919000209164'  # 你的appid
    secretKey = 'KWLgg7bDL0wik8eTN8xw'  # 你的密钥

    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    q = text
    fromLang = source
    toLang = target
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        c = requests.get(myurl).content.decode('utf-8')
        c = json.loads(c)
        return c['trans_result'][0]['dst']
    except Exception as e:
        return ''


def youdao_translate(text, source='zh-CHS', target='en'):
    import random

    appKey = '01c0ecf37a7cbd94'
    secretKey = 'ygerEwqc1uL2K45LWe3WPQwae9zeU4Yo'

    toLang = target
    salt = random.randint(1, 65536)

    sign = appKey + text + str(salt) + secretKey
    m1 = hashlib.md5(sign.encode('utf-8'))
    sign = m1.hexdigest()
    myurl = 'http://openapi.youdao.com/api'
    myurl = myurl + '?appKey=' + appKey + '&q=' + quote(
            text) + '&from=' + source + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    resp = requests.get(myurl)
    c = resp.content.decode('utf-8')
    ccc = resp.content.decode('utf-8')

    c = json.loads(c)
    try:
        tanslations = c.get('translation')
        if tanslations is not None:
            r = ''.join(tanslations)
            return r
        else:
            print('有道翻译失败 ' + ccc)
            return ''
    except:
        return ''


def save_cookie(browser):
    browser.get(u)
    username = wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#username')))
    password = wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#password')))
    login_btn = wait2.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'body > div.top-content > div > div > div > div > div.form-bottom > form > button')))

    username.send_keys(user)
    password.send_keys(p)
    login_btn.click()
    try:
        locate_index_flag = wait2.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div > div:nth-child(1) > div > div > ul > li.active > a')))
    except Exception as e:
        print('登陆失败,获取cookie失败')
        return ''
    cookies = browser.get_cookies()
    c_file = open('{}-data.pkl'.format(user_id), 'wb')
    pickle.dump(cookies, c_file, -1)
    c_file.close()

    return cookies


def get_cookie(browser):
    try:
        c_file = open('{}-data.pkl'.format(user_id), 'rb')
        c = pickle.load(c_file)
    except Exception as e:
        cookies = save_cookie(browser)
        c = cookies
    return c


def format_text(text, new_en, old_en):
    if new_en != '' and old_en != '':
        zh = text.replace(new_en, '')
        whole_en = text.replace(zh, old_en)
        ss = new_en
    else:
        ss = text
    new_str, up_str, word_count = format2(ss)

    new_str = new_str.lower()
    if new_en != '' and old_en != '':
        return new_str, up_str.upper(), count_word(whole_en)
    else:
        return new_str, up_str.upper(), word_count


def format2(ss):
    index = ss.rfind('.', len(ss) - 5, len(ss))
    if index < 0:
        ss += '.'
        index = ss.rfind('.')
    while ss[:index][-1] == ' ':
        ss = ss[:index][:-1]
    ss = ss[:index] + '.'
    while ss[0] == ' ':
        ss = ss[1:]
    ss = ss.replace('    ', '   ')
    ss = ss.replace('   ', '  ')
    ss = ss.replace('  ', ' ')
    ss = ss.replace(', ', ',')
    ss = ss.replace(' ,', ',')
    ss = ss.replace('. ', '.')
    ss = ss.replace(' .', '.')
    ss = ss.replace(' :', ':')
    ss = ss.replace(': ', ':')
    ss = ss.replace(' ;', ';')
    ss = ss.replace('; ', ';')
    new_str = ''
    up_str = ''
    index = 0
    word_count = 0
    for s in ss:
        current = s
        if index == 0:
            last = ''
            next = ss[index + 1]
        elif index == len(ss) - 1:
            last = ss[index - 1]
            next = ''
        else:
            last = ss[index - 1]
            next = ss[index + 1]
        # print('-' * 5)
        # print(last)
        # print(current)
        # print(next)
        # print('-' * 5)
        part = current
        up_part = current
        if current == '.':
            if not (last.isdigit() and next.isdigit()):
                if (last.isalpha() or last.isdigit()) and next == '':
                    part = ' {}'.format(current)
                    up_part = '  {}'.format(current)
                    word_count += 1
                else:
                    part = ' {} '.format(current)
                    up_part = '  {}  '.format(current)
                    word_count += 1
            else:
                up_part = ' {} '.format(current)
        elif current == ',':
            if not (last.isalpha() or last.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
                word_count += 1
            else:
                part = ' {} '.format(current)
                up_part = '  {}  '.format(current)
                word_count += 1
        elif current == ':':
            if not (last.isdigit() and next.isdigit()):
                part = ' {} '.format(current)
                up_part = '  {}  '.format(current)
                word_count += 1
            else:
                up_part = ' {} '.format(current)
        elif current == ';':
            part = ' {} '.format(current)
            up_part = '  {}  '.format(current)
            word_count += 1
        elif current == "'":
            if last.isalpha() and next == ' ':
                part = '{}'.format(current)
            elif not (last.isalpha() and next.isalpha()):
                part = ' {} '.format(current)
                word_count += 1
            else:
                up_part = ' {} '.format(current)
                part = current
        elif current == '"':
            if last == '' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            elif next == '' and (last.isalpha() or last.isdigit()):
                part = ' {}'.format(current)
                up_part = '  {}'.format(current)
            elif last == ' ' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            elif next == ' ' and (last.isalpha() or last.isdigit()):
                part = ' {}'.format(current)
                up_part = '  {}'.format(current)
            else:
                part = ' {} '.format(current)
                up_part = '  {}  '.format(current)
        elif current == '(':
            if last == '' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            elif next == '' and (last.isalpha() or last.isdigit()):
                part = ' {}'.format(current)
                up_part = '  {}'.format(current)
            elif last == ' ' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            else:
                part = ' {} '.format(current)
                up_part = '  {}  '.format(current)
        elif current == ')':
            if last == '' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            elif next == '' and (last.isalpha() or last.isdigit()):
                part = ' {}'.format(current)
                up_part = '  {}'.format(current)
            elif last == ' ' and (next.isalpha() or next.isdigit()):
                part = '{} '.format(current)
                up_part = '{}  '.format(current)
            elif next == ' ' and (last.isalpha() or last.isdigit()):
                part = ' {}'.format(current)
                up_part = '  {}'.format(current)
            else:
                part = ' {} '.format(current)
                up_part = '  {}  '.format(current)
        elif current == '/':
            if last == 'm' and next == 's':
                part = '{}'.format(current)
                up_part = ' {} '.format(current)
            elif last.isdigit() and next.isdigit():
                part = '{}'.format(current)
                up_part = ' {} '.format(current)
            else:
                part = ' {} '.format(current)
                word_count += 1
        elif current == '-':
            if last.isalpha() and next.isalpha():
                part = '{}'.format(current)
                up_part = '{} '.format(current)
            else:
                part = ' {} '.format(current)
                word_count += 1
        elif current == '%':
            if last.isdigit():
                part = '{}'.format(current)
                up_part = ' {} '.format(current)
            else:
                part = ' {} '.format(current)
                word_count += 1
        elif current == ' ':
            word_count += 1
            up_part += ' '
        elif current.isalpha():
            up_part += ' '
        new_str += part
        up_str += up_part
        index += 1
    ms_index = new_str.find('m/s')
    if ms_index >= 1:
        if new_str[ms_index - 1].isdigit():
            new_str = new_str.replace('m/s', ' m/s')
            up_str = up_str.replace('m / s', '  m / s')
            word_count += 1
    up_str = up_str.replace('   ', '  ')
    return new_str.lower(), up_str.upper(), word_count


def count_word(text):
    ss = text
    new_str, up_str, word_count = format2(ss)

    return word_count


def is_zh_and_en(text):
    regex_str = '[\u4E00-\u9FA5|\d\w,.;\?\-:]+'
    regex_str = '((?![a-zA-Z]).)*[\u4E00-\u9FA5]((?![a-zA-Z]).)*'

    match_obj = re.match(regex_str, text)
    if match_obj:
        print(match_obj.group(0))
        result = match_obj.group(0)
    else:
        result = ''
    return result


def start_work(c_str):
    global c, a, u
    headers = {
        'cookie': c_str,
    }
    c = requests.get('http://117.78.28.80:8080/sjbz/userInfoFront!findWorkingPro.do?usid={}&state=5'.format(user_id),
                     headers=headers).content
    c = c.decode('utf-8')
    html = etree.HTML(c)
    a = html.xpath('//a')
    if len(a) > 0:
        href = a[0].attrib['href']
        u = 'http://117.78.28.80:8080' + href
        c = requests.get(u, headers=headers).content.decode('utf-8')
        print('自动接任务中....')
        browser.get('http://117.78.28.80:8080/sjbz/userInfoFront!tabs_switch.do?sid={}&state=indexs'.format(user_id))
    else:
        print('没有任务或已经接了任务,去我的工作看看')


user_id = configs.user.id
browser = webdriver.Chrome()
browser.set_window_size(1280, 800)
wait = WebDriverWait(browser, 100000)
wait2 = WebDriverWait(browser, 5)
u = 'http://117.78.28.80:8080/sjbz/'
user = configs.user.username
p = configs.user.password


def get_secondid_and_rework_num(work_id):
    u = 'http://117.78.28.80:8080/sjbz/userInfoFront!findWorkingPro.do?usid={}&state=0'.format(configs.user.id)
    second_id = ''
    rework_num = ''
    try:
        c = requests.get(u, headers={'cookie': c_str})
        c = c.content.decode('utf-8')
        html = etree.HTML(c)
        a_list = html.xpath('/html//a')

        trs = html.xpath('/html//tr')
        for tr in trs:
            href = ''
            a = tr.xpath('td/a')
            if len(a) > 0:
                a = a[0]
                href = a.attrib['href']
            try:
                found_id = re.findall(r'=(\w+)&', href)[0]
            except:
                found_id = ''
            if found_id == work_id:
                second_id = a.text
                td = tr.xpath('td[4]')[0]
                rework_num = td.text
                break
    except:
        pass
    return second_id, rework_num


def submit_to_network(current_url):
    print(current_url)
    print(configs.user.id)
    print(configs.user.worker_name)
    found_ids = re.findall(r'=(\w+)&', current_url)
    if len(found_ids) <= 0:
        found_ids = re.findall(r'=(\w+)', current_url)
    if len(found_ids) <= 0:
        print_red('检查URL里是否有ID 不要乱搞啊兄弟')
        return
    work_id = found_ids[0]
    secondid, rework_num = get_secondid_and_rework_num(work_id)
    u = 'http://{}:{}/'.format(configs.server.address, configs.server.port)
    c = requests.post(u, data={
        'work_id':    work_id,
        'second_id':  secondid,
        'rework_num': rework_num,
        'account_id': configs.user.id,
        'worker':     configs.user.worker_name
    })


c_str = ''
if __name__ == '__main__':
    index_u = 'http://117.78.28.80:8080/sjbz/userInfoFront!tabs_switch.do?sid={}&state=indexs'.format(user_id)

    c = get_cookie(browser)

    cs = {}
    for a in c:
        cs[a['name']] = a['value']
    c_str = ''
    for a in cs:
        c_str += a + '=' + cs[a] + '; '
    browser.get(index_u)
    for i in c:
        browser.add_cookie(i)
    browser.refresh()

    browser.get(
            'http://117.78.28.80:8080/sjbz/userInfoFront!imgBegin.do?id=4028819765a793030165a9e89b451698&sid={}'.format(
                    user_id))

    old_img = None
    while True:
        q = Queue()
        img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#nameDiv > div > img')))
        select_one_result = ''
        select_two_result = ''
        if img != old_img:
            print('识别处理中..')
            s = img.get_attribute('src')

            ir = requests.get(s)
            if ir.status_code == 200:
                open('img/test.png', 'wb').write(ir.content)

            # yp = threading.Thread(target=youdao)
            # bp = threading.Thread(target=baidu)
            # gp = threading.Thread(target=google)
            # tp = threading.Thread(target=tecent)
            youdao_r = ''
            baidu_r = ''
            google_r = ''
            try:
                youdao_r = youdao()
                baidu_r = baidu()
                try:
                    google_r = google()
                except TimeoutError as e:
                    google_r = ''
                    print('谷歌超时')
            except:
                print_red('所有引擎识别失败,请选择 5.自定义 输入')
            # tecent_r = tecent()
            tecent_r = ''
            print_blue('------输入q退出(换题的情况)------')
            print_blue('1.有道 ' + youdao_r)
            print_blue('2.百度 ' + baidu_r)
            print_blue('3.谷歌 ' + google_r)
            print_blue('5. 自定义')
            print_blue('7. 中英混合(格式:语句~~~语言)')
            exit_flag = False
            while True:
                has_zh_en = False
                zh = ''
                en = ''
                select_one = input('请选择识别最好的一个\n')
                if select_one in ['1', '2', '3', '5', '7', 'q']:
                    if select_one == '1':
                        select_one_result = youdao_r
                        break
                    elif select_one == '2':
                        select_one_result = baidu_r
                        break
                    elif select_one == '3':
                        select_one_result = google_r
                        break
                    # elif select_one == '4':
                    #     select_one_result = tecent_r
                    #     break
                    elif select_one == '5':
                        select_one_result = input('请输入自定义语句\n')
                        break
                    elif select_one == 'q':
                        exit_flag = True
                        break
                    elif select_one == '7':
                        while True:
                            is_zh_first = False
                            while True:
                                first = input('请输入\n')
                                l = first.split('~~')
                                if len(l) >= 2:
                                    if l[1][:2] in ['zh', 'en']:
                                        if l[1][:2] == 'zh':
                                            zh = l[0]
                                            en = l[1][2:]
                                            is_zh_first = True
                                        else:
                                            en = l[0]
                                            zh = l[1][2:]
                                            is_zh_first = False
                                        break
                                    else:
                                        print('语言输入不对啊')
                                else:
                                    print('没有输入语言啊!')
                            if zh != '' and en != '':
                                break
                            else:
                                print('没有写~~把语言分隔开吧?重新输入')
                        break
                    else:
                        print('请在以上选项选择!')
            if exit_flag:
                exit_flag = False
                continue
            print('翻译中...')
            youdao_zh_en = ''
            tencent_zh_en = ''
            baidu_zh_en = ''
            google_zh_en = ''
            if zh != '' and en != '':
                has_zh_en = True
                if is_zh_first:
                    select_one_result = zh + en
                else:
                    select_one_result = en + zh
                # en_zh = tencent_translate(en, 'en', 'zh')
                # tencent_zh_en = tencent_translate(zh)
                # r = select_one_result.replace(en, en_zh)
                # translate_tencent = r.replace(zh, tencent_zh_en)
                translate_tencent = ''

                en_zh = baidu_translate(en, 'en', 'zh')
                baidu_zh_en = baidu_translate(zh)
                r = select_one_result.replace(en, en_zh)
                translate_baidu = r.replace(zh, baidu_zh_en)

                en_zh = youdao_translate(en, 'en', 'zh')
                youdao_zh_en = youdao_translate(zh)
                r = select_one_result.replace(en, en_zh)
                translate_youdao = r.replace(zh, youdao_zh_en)

                try:
                    en_zh = google_translate(en, 'zh')
                    google_zh_en = google_translate(zh)
                    r = select_one_result.replace(en, en_zh)
                    translate_google = r.replace(zh, google_zh_en)
                except:
                    pass
            else:
                translate_tencent = ''
                translate_youdao = youdao_translate(select_one_result)
                translate_baidu = baidu_translate(select_one_result)
                try:
                    translate_google = google_translate(select_one_result)
                except:
                    pass
            print('选用识别: ' + select_one_result)
            print_blue('-----------按q退出------')
            print_blue('2.有道 ' + translate_youdao)
            print_blue('3.谷歌 ' + translate_google)
            print_blue('4.百度 ' + translate_baidu)
            print_blue('5. 自定义')

            exit_flag_two = False
            while True:
                zh_en = ''
                select_two = input('请选择翻译最好的一个\n')
                if select_two in ['2', '3', '4', '5', 'q']:
                    # if select_two == '1':
                    #     select_two_result = translate_tencent
                    #     zh_en = tencent_zh_en
                    #     break
                    if select_two == '2':
                        select_two_result = translate_youdao
                        zh_en = youdao_zh_en
                        break
                    elif select_two == '3':
                        select_two_result = translate_google
                        zh_en = google_zh_en
                        break
                    elif select_two == '4':
                        select_two_result = translate_baidu
                        zh_en = baidu_zh_en
                        break
                    elif select_two == '5':
                        select_two_result = input('请输入自定义翻译\n')
                        break
                    elif select_two == 'q':
                        exit_flag_two = True
                        break
                    else:
                        print('请在以上选项选择')
            if exit_flag_two:
                exit_flag_two = False
                continue
            print('选用翻译: ' + select_two_result)
            if has_zh_en:
                xiaoxie, word, word_count = format_text(select_two_result, zh_en, en)
                word = word + '\n' + en_zh
            else:
                xiaoxie, word, word_count = format_text(select_two_result, '', '')
            print_blue('小写:' + xiaoxie)
            print_red('大写:' + word)
            print(word_count)

            textarea = wait2.until(EC.presence_of_element_located((By.ID, 'content')))

            textarea.send_keys(Keys.CONTROL + "a")
            textarea.send_keys(xiaoxie + '\n' + word + '\n' + str(word_count))

            browser.execute_script("document.getElementById('content').style.width = '1200px'")
            browser.execute_script("document.getElementById('content').style.height = '300px'")

            exit_flag_three = False
            while True:
                select_three = input('提交按y,其它情况按q\n')
                if select_three in ['y', 'q']:
                    if select_three == 'y':
                        # --------------------------------
                        btn_submit = browser.find_element_by_css_selector(
                                '#myform > filedset > div:nth-child(4) > div > button.btn.btn-primary')
                        try:
                            submit_to_network(browser.current_url)
                        except:
                            pass
                        btn_submit.click()
                        print('自动提交完成')
                        # --------------------------------
                        start_work(c_str)
                        # --------------------------------
                        # check_new_task()
                        headers = {
                            'cookie': c_str,
                        }
                        tasks_list_url = 'http://117.78.28.80:8080/sjbz/userInfoFront!findWorkingPro.do?usid={}&state=0'.format(
                                user_id)
                        c = requests.get(tasks_list_url, headers=headers).content.decode('utf-8')
                        html = etree.HTML(c)
                        trs = html.xpath('//tr')
                        print('已列出所有题目,选择或按q')
                        index = 0
                        urls = []
                        for tr in trs:
                            tds = tr.xpath('td/text()')
                            id = tr.xpath('td/a/text()')
                            us = tr.xpath('td/a')
                            tds = id + tds
                            item = '---'.join(tds)
                            if index != 0:
                                u = us[0].attrib['href']
                                urls.append(u)
                                print(str(index) + ':' + item)
                            index += 1
                        exit_flag_four = False
                        url = ''
                        while True:
                            select_four = input()
                            iis = []
                            for ii in list(range(1, index)):
                                iis.append(str(ii))
                            if select_four in (iis + ['q']):
                                if select_four != 'q':
                                    i = int(select_four)
                                    url = urls[i - 1]
                                    url = 'http://117.78.28.80:8080' + url
                                    browser.get(url)
                                    exit_flag_four = True
                                    break
                                else:
                                    exit_flag_four = True
                                    break
                            else:
                                print('不要随便选择')
                        if exit_flag_four:
                            exit_flag_four = False
                            exit_flag_three = True
                            break
                        # --------------------------------
                        exit_flag_three = True
                        break
                    elif select_three == 'q':
                        exit_flag_three = True
                        break
                else:
                    print('请输入y或q')

            if exit_flag_three:
                exit_flag_three = False
                continue
            old_img = img
