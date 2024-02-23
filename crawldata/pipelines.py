# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#pip install mysql-connector-python
import mysql.connector,re,os,dateparser
from mysql.connector import Error
from crawldata.functions import *
from datetime import datetime,timedelta
from crawldata.settings import IMAGE_FOLDER,CONFIGS
class CrawldataPipeline:
    def open_spider(self,spider):
        self.FIELDS=['KEY_','Product_Name','Brand','Model','Features','Suggested_retail_price','Cheapest_price','Released_date','Display_size_and_technology','Display_Ratio','Display_resolution','Display_refresh_frequency','Display_technology','Pixel_Density','Display_screen_to_body_ratio','Maximum_Brightness__NITS_','Minimum_Brightness__NITS_','Touch_panel_frequency','Touch_panel_capacitive_points','Glass_type','Rear_Camera','Rear_Camera_2','Rear_Camera_3','Rear_Camera_4','Front_Camera','Rear_camera_Video_recording','Front_camera_Video_recording','Android_Version','SoC_Brand','SoC_model','Size_of_SoC','Number_of_cores','System_bandwidth','Core_speed','GPU','RAM__DDR3_','User_Memory','SD_Card','Sim_Card_Slots','Type_of_Sim_Card','Lithium_Battery','Fingerprint_sensor','Face_unlock','Real_Face_Emoji','Schok_VXR_digital_Assistant','Sound_Algorithm','AptX_codec','Sound_Loudspeaker_Voice_DB','Microphones','Headphones_Jack_3_5mm','Type_of_USB','Wifi','GPS','Vibration_function','Radio_FM','Bluetooth','OTG_Ver_2_0_Port','Speaker','G_Sensor','Barometer','Gyroscope___VR_3d_READY_','Compass','Magnetometer','Proximity_Sensor','Light_Sensor','WiFi_Calling','HD_Calling','Voice_control','Hearing_Aid_compatibility','NFC','Built_in_Stylus','Thermal','Thickness','Weight_of_phone','Water_repellent','Body_structure_of_phone','Dimensions','Color','Provider','Type_of_Charger','Wireless_Charging','Antutu_Benchmark','Information_from','4G_LTE_Antennas_available_for_Carrier','Product_URL','image','image_path','DTIME_ENTERED','Master_Key']
        self.Q_STR={"Summer":"05-01","Q2":"05-01","Spring":"02-01","Q1":"02-01","Winter":"10-01","Q4":"10-01","Fall":"08-01","Autumn":"08-01","Q3":"08-01"}
        self.M_STR={"Jan":"01","Feb":"02","Mar":"03","Apl":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
        self.DTIME_CRAWL=(datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')
        self.DATABASE_NAME=CONFIGS['DATABASE_NAME']
        self.HOST=CONFIGS['HOST']
        self.username=CONFIGS['USERNAME']
        self.password=CONFIGS['PASSWORD']
        self.TABLE={}
        self.TABLE_ALL=[]
        spider.TABLES=[]
        try:
            spider.conn = mysql.connector.connect(host=self.HOST,database=self.DATABASE_NAME,user=self.username,password=self.password,charset='utf8')
            if spider.conn.is_connected():
                print('Connected to DB')
                db_Info = spider.conn.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                SQL="SELECT table_name FROM information_schema.tables WHERE table_schema = '"+CONFIGS['DATABASE_NAME']+"'"
                mycursor = spider.conn.cursor()
                mycursor.execute(SQL)
                myresult = mycursor.fetchall()
                for x in myresult:
                    self.TABLE_ALL.append(x[0])
                    if str(x[0]).startswith('scraping_'):
                        self.TABLE[x[0]]=[]
                        SQL="SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME = '"+x[0]+"';"
                        mycursor.execute(SQL)
                        myresult1 = mycursor.fetchall()
                        for x1 in myresult1:
                            if not x1[0] in self.TABLE[x[0]]:
                                self.TABLE[x[0]].append(x1[0])
                        if not 'master' in x[0]:
                            spider.TABLES.append(x[0])
            else:
                print('Not connect to DB')
        except Error as e:
            print("Error while connecting to MySQL", e)
            spider.conn=None
    def close_spider(self,spider):
        cursor = spider.conn.cursor()
        if 'master' in spider.name:
            TABLE='scraping_master'
            SQL="DELETE FROM "+TABLE+" WHERE Date <'"+(datetime.now()-timedelta(1)).strftime('%Y-%m-%d')+"'"
        else:
            TABLE='scraping_'+spider.name
            SQL="DELETE FROM "+TABLE+" WHERE DTIME_ENTERED <'"+(datetime.now()-timedelta(1)).strftime('%Y-%m-%d')+"T23:59:59'"
        try:
            cursor.execute(SQL)
            spider.conn.commit()
        except:
            pass
        if 'master' in spider.name:
            TABLE='scraping_master'
            SQL="INSERT INTO scraping_master_archive(KEY_,Brand,Model,Memory,Price,Date) SELECT CONCAT(KEY_,'_',Date),Brand,Model,Memory,Price,DATE_FORMAT(CURDATE(), \"%Y-%m-%d\") FROM scraping_master WHERE CONCAT(KEY_,'_',Date) NOT IN (SELECT KEY_ FROM scraping_master_archive)"
            cursor.execute(SQL)
            spider.conn.commit()
        if spider.conn.is_connected():
            spider.conn.close()
    def process_item(self, ITEM, spider):
        PROXY=None
        if 'proxy' in ITEM:
            #PROXY=ITEM['proxy']
            PROXY=CONFIGS['CRAWLERA_APIKEY']
            del ITEM['proxy']
        if 'master' in spider.name:
            ITEM['Date']=str(self.DTIME_CRAWL).split('T')[0]
        else:
            ITEM['DTIME_ENTERED']=self.DTIME_CRAWL
        #print('Do with DB')
        # Check and add more field if not existed in data table
        item={}
        if not 'master' in spider.name:
            for k in self.FIELDS:
                item[k]=''
        for K,V in ITEM.items():
            if not 'master' in spider.name:
                if self.Get_Key_String(K) in item:
                    item[self.Get_Key_String(K)]=str(V).replace('\\','').replace("'","\'")
            else:
                item[self.Get_Key_String(K)]=str(V).replace('\\','').replace("'","\'")
        if not 'SHEET' in item.keys():
            if 'master' in spider.name:
                item['SHEET']='scraping_master'
            else:
                item['SHEET']='scraping_'+spider.name
        if 'Released_date' in item:
            if len(item['Released_date'])>=4:
                item['Released_date']=str(item['Released_date']).replace('Released ', '')
                if len(item['Released_date'])==4 and Get_Number(item['Released_date'])==item['Released_date']:
                    item['Released_date']=item['Released_date']+"-01-01"
                else:
                    try:
                        item['Released_date']=dateparser.parse(item['Released_date']).strftime('%Y-%m-%d')
                    except:
                        STR_DATE=str(item['Released_date']).split()
                        #print(STR_DATE)
                        YEAR=''
                        Quarter=''
                        Month=''
                        for rs in STR_DATE:
                            if len(Get_Number(rs))==4:
                                YEAR=Get_Number(rs)
                            if str(rs).title() in self.Q_STR:
                                Quarter=self.Q_STR[str(rs).title()]
                            if str(rs).title()[:3] in self.M_STR:
                                Month=self.M_STR[str(rs).title()[:3]]
                        #print(YEAR,Quarter,Month)
                        if YEAR!='':
                            Date_str=YEAR+"-01-01"
                            if Quarter!="":
                                Date_str=YEAR+"-"+Quarter
                            if Month!="":
                                Date_str=YEAR+"-"+Month+"-01"
                            item['Released_date']=Date_str
                        else:
                            item['Released_date']=''

        if 'Suggested_retail_price' in item:
            if len(Get_Number(item['Suggested_retail_price']))>0:
                STR=str(item['Suggested_retail_price']).split('/')
                item['Suggested_retail_price']=''
                for rs in STR:
                    if '$' in rs:
                        item['Suggested_retail_price']=Get_Number(rs)
                if item['Suggested_retail_price']=='' and len(STR)>0:
                    item['Suggested_retail_price']=Get_Number(STR[0])
        if 'Cheapest_price' in item:
            if len(Get_Number(item['Cheapest_price']))>0:
                STR=str(item['Cheapest_price']).split('/')
                item['Cheapest_price']=''
                for rs in STR:
                    if '$' in rs:
                        item['Cheapest_price']=Get_Number(rs)
                if item['Cheapest_price']=='' and len(STR)>0:
                    item['Cheapest_price']=Get_Number(STR[0])
        if 'master' in spider.name and not 'scraping_master_archive' in self.TABLE_ALL:
            MIT={}
            MIT.update(item)
            #MIT['Master_Key']=''
            MIT['SHEET']='scraping_master_archive'
            self.create_table(spider.conn,MIT['SHEET'],MIT)
            self.TABLE_ALL.append(MIT['SHEET'])
            self.TABLE[MIT['SHEET']]=['KEY_']
            for key in MIT.keys():
                if not key in self.TABLE[MIT['SHEET']] and key!='SHEET':
                    self.TABLE[MIT['SHEET']].append(key)
                    self.add_column_to_db(spider.conn,MIT['SHEET'],key)
        if not item['SHEET'] in self.TABLE:
            self.TABLE[item['SHEET']]=[]
            self.create_table(spider.conn,item['SHEET'],item)
        for key in item.keys():
            if not key in self.TABLE[item['SHEET']] and key!='SHEET':
                self.TABLE[item['SHEET']].append(key)
                self.add_column_to_db(spider.conn,item['SHEET'],key)
        # Mining data
        if not 'master' in spider.name:
            TECH=['LTPS-LCD','AMOLED','AMOLED','pOLED','OLED','WVGA','LED','LCD','TFT','IPS','XDR','FHD','2D','HD','Retina']
            for STR in item.values():
                if 'Hz' in str(STR) and item['Display_refresh_frequency']=='':
                    STRS=str(STR).replace('/',' ').split()
                    for k in range(len(STRS)):
                        rs=STRS[k]
                        if 'Hz' in rs:
                            if len(Get_Number(rs))>0:
                                item['Display_refresh_frequency']=re.sub(r"([^0-9.MGHz])","", str(rs).strip())
                            elif rs=='Hz' and k>0 and len(Get_Number(STRS[k-1]))>0:
                                item['Display_refresh_frequency']=STRS[k-1]+re.sub(r"([^0-9.MGHz])","", str(rs).strip())
                if 'NITS' in str(STR).upper() and (item['Maximum_Brightness__NITS_']=='' or len(item['Maximum_Brightness__NITS_'])>20):
                    STRS=str(STR).upper().split()
                    item['Maximum_Brightness__NITS_']=''
                    for k in range(len(STRS)):
                        rs=STRS[k]
                        if 'NITS' in rs:
                            if len(Get_Number(rs))>0:
                                item['Maximum_Brightness__NITS_']=rs.replace('NITS','')
                            elif rs=='NITS' and k>0 and len(Get_Number(STRS[k-1]))>0:
                                item['Maximum_Brightness__NITS_']=STRS[k-1]
                if 'ppi' in str(STR) and item['Pixel_Density']=='':
                    STRS=str(STR).split()
                    for k in range(len(STRS)):
                        rs=STRS[k]
                        if 'ppi' in rs:
                            if len(Get_Number(rs))>0:
                                item['Pixel_Density']=rs
                            elif rs=='ppi' and k>0 and len(Get_Number(STRS[k-1]))>0:
                                item['Pixel_Density']=STRS[k-1]+' '+rs
                if 'Touch' in str(STR) and item['Touch_panel_frequency']=='':
                    item['Touch_panel_frequency']='Yes'
                if item['Touch_panel_frequency']=='true':
                    item['Touch_panel_frequency']='Yes'
                if ':' in str(STR) and item['Display_Ratio']=="":
                    x = re.findall(r"\d{1,2}[:]\d{1,2}", STR)
                    if len(x)>0 and item['Display_Ratio']=="":
                        item['Display_Ratio']=x[0]
                if '%' in str(STR) and item['Display_screen_to_body_ratio']:
                    x = re.findall(r"\d{1,2}%|\d{1,2}[.]\d{1,2}%", STR)
                    if len(x)>0 and item['Display_screen_to_body_ratio']=="":
                        item['Display_screen_to_body_ratio']=x[0]

            if item['Display_technology']!='':
                STR=item['Display_technology']
                item['Display_technology']=''
                for rs in TECH:
                    if rs in STR and item['Display_technology']=='':
                        item['Display_technology']=rs
            if item['Display_technology']=='':
                STR=item['Display_resolution']
                for rs in TECH:
                    if rs in STR and item['Display_technology']=='':
                        item['Display_technology']=rs
            if item['Display_resolution']!='':
                x = re.findall(r"\d{1,9}[x]\d{1,9}|\d{1,9}[x]\d{1,9}", (str(item['Display_resolution']).replace(' ','')).replace('-by-','x').replace('‑by‑','x'))
                if len(x)>0:
                    item['Display_resolution']=x[0]
                else:
                    item['Display_resolution']=''
            if len(item['Display_screen_to_body_ratio'])>20:
                x = re.findall(r"\d{1,2}%|\d{1,2}[.]\d{1,2}%", item['Display_screen_to_body_ratio'])
                if len(x)>0:
                    item['Display_screen_to_body_ratio']=x[0]
            if len(Get_Number(item['Display_size_and_technology']))>0:
                item['Display_size_and_technology']=Get_Number(item['Display_size_and_technology'])+'"'
            if 'Touch' in item['Touch_panel_frequency']:
                    item['Touch_panel_frequency']='Yes'
        # Insert data to table
        SQL="INSERT INTO "+item['SHEET']
        LIST_FIELDS=''
        VALUES=''
        STR_UPDATE=''
        for key in self.TABLE[item['SHEET']]:
            if LIST_FIELDS=='':
                LIST_FIELDS="`"+key+"`"
            else:
                LIST_FIELDS+=',`'+key+"`"
            if key in item:
                V=str(item[key]).replace("'","''").replace("\\","\\\\")
                if V=='None':
                    V=""
            else:
                V=""
            if VALUES=='':
                VALUES="'"+V+"'"
            else:
                VALUES+=",'"+V+"'"
            if not 'KEY_' in key:
                if STR_UPDATE=="":
                    STR_UPDATE="`"+key+"`='"+V+"'"
                else:
                    STR_UPDATE+=", `"+key+"`='"+V+"'"
        SQL+="("+LIST_FIELDS+") VALUES("+VALUES+") ON DUPLICATE KEY UPDATE "+STR_UPDATE+";"
        cursor = spider.conn.cursor()
        try:
            cursor.execute(SQL)
            spider.conn.commit()
            print('Isnerted to DB')
            if not 'master' in spider.name:
                FOLDER=IMAGE_FOLDER+spider.name
                if not os.path.exists(FOLDER):
                    os.makedirs(FOLDER)
                if 'image' in item and 'image_path' in item and item['image'] and item['image_path'] and len(str(item['image']))>5 and len(str(item['image_path']))>5 and not os.path.exists(FOLDER+'/'+item['image']):
                    #download(item['image_path'], FOLDER+'/'+item['image'],proxy=PROXY)
                    pass
        except:
            print('Error: ',item,'\n',SQL)
        #return item
    def get_DataType(self,strtxt):
        strtxt=str(strtxt).strip()
        if Get_Number(strtxt)==strtxt:
            if '.' in strtxt and str(strtxt).count('.')==1:
                return 'FLOAT'
            elif not '.' in str(strtxt):
                return 'INT'
            else:
                return 'TEXT'
        else:
            return 'TEXT'
    def create_table(self,connection,table_name,item):
        SQL='CREATE TABLE IF NOT EXISTS '+table_name+'('
        KEY=' PRIMARY KEY ('
        i=0
        for K in item.keys():
            if 'KEY_' in K:
                SQL+=K+' VARCHAR(255) NOT NULL, '
                if i==0:
                    KEY+=K
                else:
                    KEY+=', '+K
                i+=1
        KEY+=')'
        SQL+=KEY+');'
        try:
            print('Creating Table:',table_name)
            print(SQL)
            cursor = connection.cursor()
            cursor.execute(SQL)
            connection.commit()
        except:
            print(SQL)
    def add_column_to_db(self,connection,table_name,field):
        SQL="ALTER TABLE "+table_name+" ADD COLUMN `"+field+"` "+self.get_DataType(field)+ " DEFAULT NULL;"
        #SQL="ALTER TABLE "+table_name+" ADD COLUMN "+field+" "+self.get_DataType(field)+ " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL;"
        try:
            print('Adding column name:',field)
            cursor = connection.cursor()
            cursor.execute(SQL)
            connection.commit()
        except:
            print(SQL)
    def Get_Key_String(self,xau):
        KQ=re.sub(r"([^A-Za-z0-9])","_", str(xau).strip())
        return KQ