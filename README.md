# CloudLoan

##项目结构

- chezhibao：车置宝项目单接口用例
- czb_tp：车置宝项目业务流程用例
- kkd_*：卡卡贷项目各业务流程用例
- ddq_*：豆豆钱项目各业务流程用例
- cfq_*：橙分期项目各业务流程用例
- jfx_*：金服侠-牙医贷项目流程与接口必填项校验的用例
- rmkj_*：任买医美项目流程与接口必填项校验的用例
- jqh_*：借去花项目各业务流程用例
- nqh_*：拿去花项目各业务流程用例
- yzf_*：翼支付项目各业务流程用例
- syj_*：随意借项目各业务流程用例


- data:存放了各种json文件，网络上爬下的数据，接口用例所用到数据
- common：封装了用例中需要调用的请求、redis连接、数据库连接、读取Excel/json文件等
- config：配置文件以及配置文件操作相关
- drivers：存放了selenium需要调用到的浏览器驱动
- HtmlReport：测试报告
- log：日志相关的封装
- test_report：测试报告输出文件

- run_all_case：执行文件


**执行方式**

        python3 run_all_case.py [case_file] [mac/linux/windows] [enviroment] [businessType]