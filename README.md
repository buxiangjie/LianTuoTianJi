# I-G

##项目结构


- 51：51信用卡项目单接口用例
- 51_tp：51信用卡项目业务流程用例
- chezhibao：车置宝项目单接口用例
- czb_tp：车置宝项目业务流程用例
- data:存放了各种json文件，网络上爬下的数据，接口用例所用到数据


- common：封装了用例中需要调用的请求、redis连接、数据库连接、读取Excel/json文件等其它小动作
- config：配置文件以及配置文件操作相关
- drivers：存放了selenium需要调用到的浏览器驱动
- HtmlReport：H5测试报告的模板文件
- log：日志相关的封装
- test_report：测试报告输出文件


- run_all_case：shell命令执行的文件