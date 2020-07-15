# House_Crawl
使用scrapy对链家二手房数据进行爬取
提供两类数据的爬取：二手房在售信息与已成交二手房信息

## Usage
+ 前往配置文件LianJiaConfig.cfg，参照提示填写配置信息
+ 切换工作目录到House_Crawl\LianJia_Crawl
+ 调用命令scrapy crawl SecondhandOnSaleSpider或者scrapy crawl SecondhandDealSpider执行二手房在售、成交信息爬取
+ 爬取结果以csv格式保存在House_Crawl\LianJia_Crawl\data

## 反爬取
链家网具有反爬取措施  
猜测是同一IP地址高频访问会触发人机验证 ，使用Random UserAgent以及关闭cookies均未能奏效(使用代理IP应该可以，但麻烦些)
这里采取的方式是在settings.py文件中设置DOWNLOAD_DELAY，此延时会降低爬取速度
爬取数据量较小时建议选择删除该行(DEFAULT = 0)或者调小该值从而提高速度  
调整可能触发链家网人机验证中止爬取
