#
import hashlib,re,requests

__version__ = '0.1.2'
class TrackerBase(object):
    def on_start(self, response):
        pass

    def on_chunk(self, chunk):
        pass

    def on_finish(self):
        pass

class ProgressTracker(TrackerBase):
    def __init__(self, progressbar):
        self.progressbar = progressbar
        self.recvd = 0

    def on_start(self, response):
        max_value = None
        if 'content-length' in response.headers:
            max_value = int(response.headers['content-length'])
        self.progressbar.start(max_value=max_value)
        self.recvd = 0

    def on_chunk(self, chunk):
        self.recvd += len(chunk)
        try:
            self.progressbar.update(self.recvd)
        except ValueError:
            # Probably the HTTP headers lied.
            pass

    def on_finish(self):
        self.progressbar.finish()

class HashTracker(TrackerBase):
    def __init__(self, hashobj):
        self.hashobj = hashobj

    def on_chunk(self, chunk):
        self.hashobj.update(chunk)

def download(url, target, proxy=None , headers=None, trackers=()):
    if headers is None:
        headers = {}
    headers.setdefault('user-agent', 'requests_download/'+__version__)
    if proxy is None:
        r = requests.get(url, headers=headers, stream=True)
    else:
        proxies={'http':'http://'+proxy+':@proxy.crawlera.com:8011','https':'http://'+proxy+':@proxy.crawlera.com:8011'}
        r = requests.get(url, proxies=proxies, headers=headers, stream=True, verify=False, timeout=20)
    r.raise_for_status()
    for t in trackers:
        t.on_start(r)
    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                for t in trackers:
                    t.on_chunk(chunk)

    for t in trackers:
        t.on_finish()
def translate(text,fromlag,tolang):
    data = {'text': text,'gfrom': fromlag,'gto': tolang}
    response = requests.post('https://www.webtran.eu/gtranslate/', data=data)
    return(response.text)
def Get_Number(xau):
    KQ=re.sub(r"([^0-9.])","", str(xau).strip())
    return KQ
def Get_PPI(xau):
    KQ=re.sub(r"([^0-9~])","", str(xau).strip())
    return KQ
def Get_PPIS(xau):
    KQ=re.sub(r"([^0-9~a-zA-Z])","", str(xau).strip())
    return KQ
def Get_String(xau):
    KQ=re.sub(r"([^A-Za-z_])","", str(xau).strip())
    return KQ
def Get_String_Key(xau):
    KQ=re.sub(r"([^A-Za-z_])","-", str(xau).strip())
    return KQ
def cleanhtml(raw_html):
    if raw_html:
        raw_html=str(raw_html).replace('</',' ^</')
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        cleantext=(' '.join(cleantext.split())).strip()
        cleantext=str(cleantext).replace(' ^','^').replace('^ ','^')
        while '^^' in cleantext:
            cleantext=str(cleantext).replace('^^','^')
        cleantext=str(cleantext).replace('^',' \n ')
        return cleantext.strip()
    else:
        return ''
def kill_space(xau):
    xau=str(xau).replace('\t','').replace('\r','').replace('\n',', ')
    xau=(' '.join(xau.split())).strip()
    return xau
def key_MD5(xau):
    xau=(xau.upper()).strip()
    KQ=hashlib.md5(xau.encode('utf-8')).hexdigest()
    return KQ
def RUN_SQL(conn,SQL):
    cur = conn.cursor()
    cur.execute(SQL)
    conn.commit()
def get_data_from_sql(conn,SQL):
    cur = conn.cursor()
    cur.execute(SQL)
    columns = [col[0] for col in cur.description]
    DATA=[dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return DATA
def get_item_from_json(result,item,space):
    if isinstance(item,dict):
        for k,v in item.items():
            if isinstance(v,dict) or isinstance(v,list):
                if space=='':
                    get_item_from_json(result,v,k)
                else:
                    get_item_from_json(result,v,space+'.'+k)
            else:
                if space=='':
                    result[k]=v
                else:
                    result[space+'.'+k]=v
    else:
        for i in range(len(item)):
            k=str(i)
            v=item[i]
            if isinstance(v,dict) or isinstance(v,list):
                if space=='':
                    get_item_from_json(result,v,k)
                else:
                    get_item_from_json(result,v,space+'.'+k)
            else:
                if space=='':
                    result[k]=v
                else:
                    result[space+'.'+k]=v
    return result
# HUNG ADD
def push(obj: object = None, key: str = None) -> dict:
    source = dict()
    if obj:
        source.setdefault(key, obj.group(0))
    else:
        source.setdefault(key, "")
    return source
def handle_dp(params: list = None) -> dict:
    rets = dict()
    params = ' '.join(params)
    params = params.split("\n")
    params = params[0].replace('”', "")
    # print(params)

    gls = re.search('([a-zA-Z]+\s+){2}Glass', params)
    sizes = re.search('([0-9]+).([0-9]+)', params)
    ratio = re.search('([0-9]+):([0-9]+)', params)
    reso = re.search('(\S+?) resolution', params.lower())

    rets = {**push(gls, "Glass"), **push(sizes, "Sizes"),
            **push(ratio, "Ratio"), **push(reso, "Resolution")}

    if rets.get('Ratio'):
        tech = params[:params.index(rets.get('Ratio'))]
        rets.setdefault("Tech", tech)
    else:
        rets.setdefault("Tech", "")

    # print({name: rets})
    # print('-------------------------------')
    return rets


def handle_cam(params: list = None) -> dict:
    rets = dict()
    params = ' '.join(params).split("\n")
    params = ' '.join(params).split(" ")
    # print(params)
    for item in params:
        for sign in ('Rear:', 'Front:', 'Main:'):
            if sign in item:
                value = params[params.index(sign)+1]
                if sign == 'Main:':
                    sign = 'Rear:'
                rets.setdefault(sign.replace(":", ""), value)
    # print(rets)
    # print('-------------------------------')
    return {'Rear': '', 'Front': ''} if len(rets) == 0 else rets


def handle_pro(params: list = None) -> dict:
    # print({name: {"Processor": ', '.join(params)}})
    # print('-------------------------------')
    params = ' '.join(params).split("\n")
    params = ' '.join(params)
    if params:
        if 'LCD' in params or 'RAM' in params:
            return {"Processor": ""}
        else:
            return {"Processor": params}
    else:
        return {"Processor": ""}


def handle_4g(params: list = None) -> dict:
    if params:
        params = ' '.join(params).replace(":", "").split("\n")[0]
        if '3G' in params:
            # print({name: {'4G': params[params.index('4G'): params.index('3G')-1]}})
            # print('-------------------------------')
            return {'4G': params[params.index('4G'): params.index('3G')-1]}
        else:
            # print({name: {'4G': params[params.index('4G'): ]}})
            # print('-------------------------------')
            return {'4G': params[params.index('4G'):]}
    else:
        return {'4G': ""}


def handle_con(params: list = None) -> dict:
    rets = dict()
    params = ' '.join(params).replace(":", "").replace(
        "-", "").replace("Headset", "headset").split("\n")[0]
    # print(params)

    headset = re.search(f'(\S+?)mm', params)
    blue = re.search('Bluetooth ([0-9]+).([0-9]+)', params)
    rets = {**push(headset, "Headset"), **push(blue, "Bluetooth"), }
    wifi = params.replace(rets.get('Bluetooth'), "").replace(
        rets.get('Headset') + ' headset jack', "").strip()

    rets.setdefault('Wifi', wifi)
    # print('-------------------------------')
    return rets


def handle_mem(params: list = None) -> dict:
    params = ' '.join(params).replace('\n', '')
    # print(params)
    rets = re.findall(r'\d+', params)
    if len(rets) == 0:
        rets = ("", "", "")
    if len(rets) == 2:
        rets.insert(0, "")
    rets = dict(zip(('RAM', 'ROM', 'SD'), rets))

    # print(rets)
    # print('-------------------------------')
    return rets


def handle_os(params: list = None) -> dict:
    params = ' '.join(params).replace("™", "")
    # print({name: {"OS": params}})
    # print('-------------------------------')
    return {"OS": params}

# END HUNG ADD
