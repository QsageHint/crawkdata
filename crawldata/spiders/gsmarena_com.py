#
import scrapy,json,os
from crawldata.functions import *
from crawldata.settings import KEY,CONFIGS
class CrawlerSpider(scrapy.Spider):
    name = 'gsmarena_com'
    domain='https://www.gsmarena.com'
    start_urls=['https://www.gsmarena.com/makers.php3']
    PROXY='http://'+CONFIGS['CRAWLERA_APIKEY']+':@proxy.crawlera.com:8011'
    REQUESTS=0
    def parse(self, response):
        Data=response.xpath('//div[@id="body"]//div[@class="st-text"]//td')
        for row in Data:
            BRAND_NAME=str(row.xpath('./a/text()').get()).title()
            LINK=self.domain+'/'+row.xpath('./a/@href').get()
            BRAND={'BRAND_NAME':BRAND_NAME,'BRAND_URL':LINK}
            yield scrapy.Request(LINK,callback=self.parse_list,meta={'BRAND':BRAND,'proxy':self.PROXY})
    def parse_list(self,response):
        BRAND=response.meta['BRAND']
        Data=response.xpath('//div[@id="review-body"]//li')
        for row in Data:
            if self.REQUESTS<4000:
                self.REQUESTS+=1
                MODEL={}
                MODEL.update(BRAND)
                MODEL['MODEL_NAME']=row.xpath('./a/strong/span/text()').get()
                MODEL['MODEL_URL']=self.domain +'/'+ row.xpath('./a/@href').get()
                MODEL['MODEL_TITLE']=row.xpath('./a/img/title/text()').get()
                yield scrapy.Request(MODEL['MODEL_URL'],callback=self.parse_content,meta={'MODEL':MODEL,'proxy':self.PROXY})
    def parse_content(self,response):
        MODEL=response.meta['MODEL']
        item={}
        item['KEY_']=key_MD5(os.path.basename(response.url))
        for k in KEY:
            item[k]=''
        item['image_path']=response.xpath('//div[@class="specs-photo-main"]//img/@src').get()
        item['image']=os.path.basename(str(item['image_path']).split('?')[0])
        Data=response.xpath('//ul[@class="specs-spotlight-features"]/li[not(i) and not(strong) and not(a)]/span')
        for row in Data:
            Title=row.xpath('./i/@class').get()
            if Title:
                Title=(str(Title).strip()).split()
                Title=Title[len(Title)-1]
                TXT=row.xpath('./span/text()').get()
                MODEL[Title]=TXT
        Data=response.xpath('//ul[@class="specs-spotlight-features"]/li[i and strong]')
        for row in Data:
            Title=row.xpath('./i/@class').get()
            if Title:
                Title=(str(Title).strip()).split()
                Title=str(Title[len(Title)-1]).split('-')[1]
                MODEL[Title]={}
                VAL=cleanhtml(row.xpath('./strong').get())
                MODEL[Title]['strong']=str(VAL).replace(' \n ', ' ')
                VAL=cleanhtml(row.xpath('./div').get())
                MODEL[Title]['div']=VAL
        MODEL['DETAILS']={}
        DATA=response.xpath('//div[@id="specs-list"]/table')
        for ROW in DATA:
            TITLE=ROW.xpath('.//tr[1]/th/text()').get()
            MODEL['DETAILS'][TITLE]={}
            Data=ROW.xpath('.//tr')
            Title=''
            for row in Data:
                Title1=row.xpath('./td[1]//text()').get()
                if TITLE=='Main Camera':
                    Val_str=row.xpath('./td[2]//text()').getall()
                    Val=str('; '.join(Val_str)).replace('\r', '').replace('\n', '')
                else:
                    Val=str(row.xpath('./td[2]//text()').get()).replace('\r', '').replace('\n', '')
                if str(Title1).strip()=='':
                    if Title=='':
                        Title=TITLE
                        MODEL['DETAILS'][TITLE][Title]=Val
                    else:
                        MODEL['DETAILS'][TITLE][Title]+=str('; '+Val)
                else:
                    Title=Title1
                    MODEL['DETAILS'][TITLE][Title]=Val
        # Mining data to item
        item['Features']=MODEL['MODEL_NAME']
        item['Model']=MODEL['MODEL_NAME']
        try:
            item['Suggested retail price']=MODEL['DETAILS']['Misc']['Price']
        except:
            pass
        if 'icon-launched' in MODEL:
            item['Released date']=MODEL['icon-launched']
        try:
            item['Display size and technology']=MODEL['touch']['strong']
        except:
            pass
        try:
            Ratio=str(MODEL['DETAILS']['Display']['Resolution']).split()
        except:
            Ratio=[]
        for txt in Ratio:
            if ':' in txt:
                item['Display Ratio']=txt
        try:
            item['Display resolution']=MODEL['touch']['div']
        except:
            pass
        try:
            item['Display technology']=MODEL['DETAILS']['Display']['Type']
        except:
            pass
        try:
            if '(' in str(MODEL['DETAILS']['Display']['Resolution']) and 'pii' in str(MODEL['DETAILS']['Display']['Resolution']):
                item['Pixel Density']=str(str(MODEL['DETAILS']['Display']['Resolution'])).split('(')[1].split(')')[0]
        except:
            pass
        item['Rear Camera 2']=''
        item['Rear Camera 3']=''
        item['Rear Camera 4']=''
        if 'Selfie camera' in MODEL['DETAILS']:
            if 'Video' in MODEL['DETAILS']['Selfie camera']:
                item['Front camera Video recording']=MODEL['DETAILS']['Selfie camera']['Video']
                del MODEL['DETAILS']['Selfie camera']['Video']
            CAMERA=[]
            for k,v in (MODEL['DETAILS']['Selfie camera']).items():
                TXT=k+': '+v
                CAMERA.append(TXT)
            item['Front Camera']='; '.join(CAMERA)
        if 'Main Camera' in MODEL['DETAILS']:
            if 'Video' in MODEL['DETAILS']['Main Camera']:
                item['Rear camera Video recording']=MODEL['DETAILS']['Main Camera']['Video']
                del MODEL['DETAILS']['Main Camera']['Video']
            if 'Single' in MODEL['DETAILS']['Main Camera']:
                item['Rear Camera']=MODEL['DETAILS']['Main Camera']['Single']
            elif 'Dual' in MODEL['DETAILS']['Main Camera']:
                CAMERA=str(MODEL['DETAILS']['Main Camera']['Dual']).split('; ')
                if len(CAMERA)>0:
                    item['Rear Camera']=CAMERA[0]
                    if len(CAMERA)>1:
                        item['Rear Camera 2']=CAMERA[1]
            elif 'Triple' in MODEL['DETAILS']['Main Camera']:
                CAMERA=str(MODEL['DETAILS']['Main Camera']['Triple']).split('; ')
                if len(CAMERA)>0:
                    item['Rear Camera']=CAMERA[0]
                    if len(CAMERA)>1:
                        item['Rear Camera 2']=CAMERA[1]
                        if len(CAMERA)>2:
                            item['Rear Camera 3']=CAMERA[2]
            elif 'Quad' in MODEL['DETAILS']['Main Camera']:
                CAMERA=str(MODEL['DETAILS']['Main Camera']['Quad']).split('; ')
                if len(CAMERA)>0:
                    item['Rear Camera']=CAMERA[0]
                    if len(CAMERA)>1:
                        item['Rear Camera 2']=CAMERA[1]
                        if len(CAMERA)>2:
                            item['Rear Camera 3']=CAMERA[2]
                            if len(CAMERA)>3:
                                item['Rear Camera 4']=CAMERA[3]
            else:
                CAMERA=[]
                for k,v in (MODEL['DETAILS']['Main Camera']).items():
                    TXT=k+': '+v
                    CAMERA.append(TXT)
                item['Rear Camera']='; '.join(CAMERA)
        try:
            item['Android Version']=MODEL['DETAILS']['Platform']['OS']
        except:
            pass
        item['Brand']=MODEL['BRAND_NAME']
        try:
            item['SoC model']=MODEL['DETAILS']['Platform']['Chipset']
            if '(' in item['SoC model']:
                SoC=str(item['SoC model']).split('(')
                SoC=SoC[len(SoC)-1]
                item['Size of SoC']=SoC.split(')')[0]
        except:
            pass
        try:
            item['Number of cores']=MODEL['DETAILS']['Platform']['CPU']
        except:
            pass
        try:
            item['GPU']=MODEL['DETAILS']['Platform']['GPU']
        except:
            pass
        try:
            item['RAM (DDR3)']=MODEL['DETAILS']['Memory']['Internal']
        except:
            pass
        try:
            item['User Memory']=MODEL['icon-sd-card-0']
        except:
            pass
        try:
            item['SD Card']=MODEL['DETAILS']['Memory']['Card slot']
        except:
            pass
        try:
            item['Sim Card Slots']=MODEL['DETAILS']['Body']['SIM']
            if '(' in item['Sim Card Slots']:
                item['Type of Sim Card']=str(item['Sim Card Slots']).split('(')[1].split(')')[0]
        except:
            pass
        try:
            item['Lithium Battery']=MODEL['battery']['strong']
        except:
            pass
        if 'Features' in MODEL['DETAILS']:
            if 'Sensors' in MODEL['DETAILS']['Features']:
                item['G-Sensor']='Yes'
                if 'fingerprint' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Fingerprint sensor']='Yes'
                if 'Face ID' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Face unlock']='Yes'
                if 'aptx' in str(MODEL['DETAILS']['Comms']['Bluetooth']).lower():
                    item['AptX codec']='Yes'
                if 'barometer' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Barometer']='Yes'
                if 'gyro' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Gyroscope  (VR 3d READY)']='Yes'
                if 'compass' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Compass']='Yes'
                if 'magnetometer' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Magnetometer']=''
                if 'proximity' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Proximity Sensor']=''
                if 'light' in str(MODEL['DETAILS']['Features']['Sensors']).lower():
                    item['Light Sensor']=''
        try:
            item['Headphones Jack 3.5mm']=MODEL['DETAILS']['Sound']['3.5mm jack']
        except:
            pass
        try:
            item['Type of USB']=MODEL['DETAILS']['Comms']['USB']
        except:
            pass
        try:
            item['Wifi']=MODEL['DETAILS']['Comms']['WLAN']
        except:
            pass
        try:
            item['GPS']=MODEL['DETAILS']['Comms']['GPS']
        except:
            pass
        try:
            item['Radio FM']=MODEL['DETAILS']['Comms']['Radio']
        except:
            pass
        try:
            item['Bluetooth']=MODEL['DETAILS']['Comms']['Bluetooth']
        except:
            pass
        try:
            item['Speaker']=MODEL['DETAILS']['Sound']['Loudspeaker']
        except:
            pass
        try:
            item['NFC']=MODEL['DETAILS']['Comms']['NFC']
        except:
            pass
        if 'icon-mobile2' in MODEL:
            Thickness=str(MODEL['icon-mobile2']).split(', ')
            for rs in Thickness:
                if 'thickness' in rs:
                    item['Thickness']=rs
        try:
            item['Weight of phone']=MODEL['DETAILS']['Body']['Weight']
        except:
            pass
        try:
            Water=str(MODEL['DETAILS']['Body']['SIM']).split('; ')
            for rs in Water:
                if 'water' in str(rs).lower():
                    item['Water repellent']=rs
        except:
            pass
        if 'Body' in MODEL['DETAILS']:
            if 'Build' in MODEL['DETAILS']['Body']:
                item['Body structure of phone']=MODEL['DETAILS']['Body']['Build']
                GLASS=str(MODEL['DETAILS']['Body']['Build']).split(',')
                for rs in GLASS:
                    if 'glass' in str(rs).lower():
                        item['Glass type']=rs
        try:
            item['Type of Charger']=MODEL['DETAILS']['Battery']['Charging']
        except:
            pass
        if 'wireless' in str(item['Type of Charger']).lower():
            item['Wireless Charging']='Yes'
        if 'Tests' in MODEL['DETAILS']:
            if 'Performance' in MODEL['DETAILS']['Tests']:
                if 'AnTuTu' in MODEL['DETAILS']['Tests']['Performance']:
                    item['Antutu Benchmark']=MODEL['DETAILS']['Tests']['Performance']
        if 'Network' in MODEL['DETAILS']:
            LTE=[]
            for k,v in (MODEL['DETAILS']['Network']).items():
                TXT=k+': '+v
                LTE.append(TXT)
            item['4G/LTE Antennas available for Carrier']=('; '.join(LTE))
        item['Product URL']=response.url
        if str(item['RAM (DDR3)'])=='' or str(item['RAM (DDR3)'])=='None':
            item['Product Name']=item['Brand']+' '+item['Features']
        else:
            item['Product Name']=item['Brand']+' '+item['Features']+' - '+item['RAM (DDR3)']
        TMP=['Features','Weight of phone','Thickness','Android Version','User Memory']
        TXT=item['Features']
        for rs in TMP:
            if str(item[rs])!='' and str(item[rs])!='None':
                TXT+='; '+rs
        item['Features']=TXT
        item['proxy']=CONFIGS['CRAWLERA_APIKEY']
        yield(item)