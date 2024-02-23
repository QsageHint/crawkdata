# Scrapy settings for crawldata project
#
import re
BOT_NAME = 'crawldata'

SPIDER_MODULES = ['crawldata.spiders']
NEWSPIDER_MODULE = 'crawldata.spiders'
KEY=['Product Name','Brand','Model','Features','Suggested retail price','Cheapest price','Released date','Display size and technology','Display Ratio','Display resolution','Display refresh frequency','Display technology','Pixel Density','Display screen to body ratio','Maximum Brightness (NITS)','Minimum Brightness (NITS)','Touch panel frequency','Touch panel capacitive points','Glass type','Rear Camera','Rear Camera 2','Rear Camera 3','Rear Camera 4','Front Camera','Rear camera Video recording','Front camera Video recording','Android Version','SoC Brand','SoC model','Size of SoC','Number of cores','System bandwidth','Core speed','GPU','RAM (DDR3)','User Memory','SD Card','Sim Card Slots','Type of Sim Card','Lithium Battery','Fingerprint sensor','Face unlock','Real Face Emoji','Schok VXR digital Assistant','Sound Algorithm','AptX codec','Sound Loudspeaker Voice DB','Microphones','Headphones Jack 3.5mm','Type of USB','Wifi','GPS','Vibration function','Radio FM','Bluetooth','OTG Ver 2.0 Port','Speaker','G-Sensor','Barometer','Gyroscope  (VR 3d READY)','Compass','Magnetometer','Proximity Sensor','Light Sensor','WiFi Calling','HD Calling','Voice control','Hearing Aid compatibility','NFC','Built-in Stylus','Thermal','Thickness','Weight of phone','Water repellent','Body structure of phone','Dimensions','Color','Provider','Type of Charger','Wireless Charging','Antutu Benchmark','Information from','4G/LTE Antennas available for Carrier','Product URL','image','image_path']
URLLENGTH_LIMIT = 50000
ROBOTSTXT_OBEY = False
HTTPERROR_ALLOW_ALL=True
TELNETCONSOLE_ENABLED = False
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.5',
    'content-type': 'text/plain',
    'Connection': 'keep-alive',
    'TE': 'trailers',
}
ITEM_PIPELINES = {'crawldata.pipelines.CrawldataPipeline': 300,}
CONFIG=re.split('\r\n|\n', open('config.txt').read())
CONFIGS={}
for rcs in CONFIG:
    rcs=str(rcs).strip()
    if '=' in rcs and not str(rcs).startswith('#'):
        rs=str(rcs).split('=')
        CONFIGS[rs[0]]=rs[1]
IMAGE_FOLDER=CONFIGS['IMAGE_FOLDER']