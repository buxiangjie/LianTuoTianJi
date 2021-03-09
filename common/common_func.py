#!/usr/bin/env python3# -*- coding: UTF-8 -*-import datetimeimport randomimport requestsimport osimport redisimport jsonimport timeimport sysimport base64import allureimport yamlfrom Crypto.Cipher import PKCS1_v1_5from Crypto.Signature import pkcs1_15from faker import Fakerfrom Crypto.Hash import SHA1from Crypto.PublicKey import RSAfrom dateutil.relativedelta import relativedeltafrom config.configer import Configfrom log.ulog import Ulogfrom typing import Optionalsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))class Common:	"""封装接口请求"""	@staticmethod	@allure.step("接口请求")	def response(			faceaddr: str,			headers: dict,			product: str,			environment: str,			data: Optional[str] = None,			param: Optional[str] = None,			method: Optional[str] = 'post',			prod_type: Optional[str] = None	):		"""		:return: requests Object		"""		urls = Common.get_json_data("config", "url.json")		if any(des in faceaddr for des in ["upload", "sign", "confirm"]):			url = str(urls[product][environment]).replace("/busi-api", "") + faceaddr		else:			url = urls[product][environment] + faceaddr		new_data = json.loads(data)		if any(fa in faceaddr for fa in ["/contract/query", "/contract/sign"]):			new_data['content'] = "太长隐藏了~~"		if "/sign/confirm" in faceaddr:			new_data['authLetter'] = "太长隐藏了~~"		if method == 'post':			if product == "gateway":				try:					headers['X-TBC-SIGN'] = Common.rsa_with_sha1(						data=json.dumps(data, ensure_ascii=False),						product_type=prod_type					)					Ulog.info(f"请求地址:{url}\n请求参数头:{headers}\n请求参数:{json.dumps(new_data, ensure_ascii=False)}")					if headers["X-TBC-SKIP-ENCRYPT"] != "true":						if prod_type in ['wxjk', 'jkjr']:							datas = Common.encrypt_params(new_data)						else:							datas = json.dumps(json.loads(data), ensure_ascii=False).encode("utf-8")					else:						datas = json.dumps(json.loads(data), ensure_ascii=False).encode("utf-8")					rep = requests.post(						url,						headers=headers,						params=param,						data=datas					)					rep.raise_for_status()					if headers["X-TBC-SKIP-ENCRYPT"] != "true":						if prod_type in ['wxjk', 'jkjr']:							reps = json.loads(Common.dencrypt_response(rep.text, prod_type))						else:							reps = json.loads(rep.text)					else:						reps = json.loads(rep.text)					if "/contract/query" in faceaddr:						reps['content'] = "太长隐藏了~~"					Ulog.info(f"返回信息:{reps}")					Common.get_rep_text(reps)					return reps				except Exception as e:					raise e			else:				try:					Ulog.info(f"请求地址:{url}\n请求参数头:{headers}\n请求参数:{json.dumps(new_data, ensure_ascii=False)}")					#ddt框架使用时解除注释					# print(json.dumps(new_data, ensure_ascii=False))					rep = requests.post(						url,						headers=headers,						params=param,						data=json.dumps(json.loads(data), ensure_ascii=False).encode("utf-8")					)					rep.raise_for_status()					reps = json.loads(rep.text)					if "/contract/query" in faceaddr:						reps['content'] = "太长隐藏了~~"					Ulog.info(f"返回信息:{reps}")					# ddt框架使用时解除注释					# print(reps)					Common.get_rep_text(reps)					return reps				except Exception as e:					raise e		elif method == 'get':			urls = Common.get_json_data("config", "url.json")			url = urls[product][environment] + faceaddr			try:				Ulog.info(f"请求地址:{url}\n请求参数头:{headers}\n请求参数:{data}")				rep = requests.get(url, headers=headers, data=json.dumps(data).encode("utf-8"))				rep.raise_for_status()				reps = json.loads(rep.text)				Ulog.info(f"返回信息:{reps}")				Common.get_rep_text(reps)				return reps			except Exception as e:				raise e	@staticmethod	@allure.step("私钥签名:{data}")	def rsa_with_sha1(data: str, product_type: str):		"""rsa with sha-1 私钥签名"""		file = ''		me = ''		if product_type in ("wxjk", "rmkj"):			file = os.path.dirname(os.path.abspath(__file__)) + "/key/wxjk_privateKey.pem"			me = "tbc_zhtb_wxjk"		elif product_type == "jkjr":			file = os.path.dirname(os.path.abspath(__file__)) + "/key/jkjr_privateKey.pem"			me = "tbc_zhtb_jkjr"		elif product_type == "pintec":			file = os.path.dirname(os.path.abspath(__file__)) + "/key/pintec_privateKey.pem"			me = "tbc_zhtb_pintec"		with open(file, "rb") as f:			key = f.read()		mes = (me + data)		digest = SHA1.new()		digest.update(bytes(mes, encoding='utf-8'))		# 读取私钥		private_key = RSA.import_key(key)		# 对HASH值使用私钥进行签名。所谓签名，本质就是使用私钥对HASH值进行加密		signature = pkcs1_15.new(private_key).sign(digest)		return base64.b64encode(signature)	@staticmethod	def verify(message: str, signature):		"""公钥验签"""		file = os.path.dirname(os.path.abspath(__file__)) + "/jkjr_publicKey.pem"		with open(file, "rb") as f:			key = f.read()		dada = json.dumps(message, ensure_ascii=False)		mes = "tbc_zhtb_wxjk" + dada		digest = SHA1.new(bytes(mes, encoding='utf-8'))		public_key = RSA.import_key(key)		return pkcs1_15.new(public_key).verify(digest, base64.b64decode(signature))	@staticmethod	@allure.step("公钥加密:{params}")	def encrypt_params(params):		"""请求参数公钥加密"""		file = os.path.dirname(os.path.abspath(__file__)) + "/key/CloudPublicKey.pem"		with open(file, "rb") as f:			key = f.read()		msg = json.dumps(params, ensure_ascii=False).encode()		length = len(msg)		default_length = 117		pubobj = PKCS1_v1_5.new(RSA.importKey(key))		# 长度不用分段		if length < default_length:			bdata = base64.b64encode(pubobj.encrypt(msg))			return bdata		# 需要分段		offset = 0		res = []		while length - offset > 0:			if length - offset > default_length:				res.append(pubobj.encrypt(msg[offset:offset + default_length]))			else:				res.append(pubobj.encrypt(msg[offset:]))			offset += default_length		byte_data = b''.join(res)		return base64.b64encode(byte_data).decode("utf-8")	@staticmethod	def dencrypt_response(response: str, product_type: str):		"""合作方私钥解密"""		file = ''		if product_type == "wxjk":			file = os.path.dirname(os.path.abspath(__file__)) + "/key/wxjk_privateKey.pem"		elif product_type == "jkjr":			file = os.path.dirname(os.path.abspath(__file__)) + "/key/jkjr_privateKey.pem"		with open(file, "rb") as f:			key = f.read()		msg = base64.b64decode(response)		length = len(msg)		default_length = 128		pubobj = PKCS1_v1_5.new(RSA.importKey(key))		# 长度不用分段		if length <= default_length:			bdata = b''.join(pubobj.decrypt(msg, 'error'))			return bdata.decode("utf-8")		# 需要分段		offset = 0		res = []		while length - offset > 0:			if length - offset > default_length:				res.append(pubobj.decrypt(msg[offset:offset + default_length], 'error'))			else:				res.append(pubobj.decrypt(msg[offset:], 'error'))			offset += default_length		byte_data = b''.join(res)		return byte_data.decode("utf-8")	@staticmethod	def get_json_data(file: str, filename: str) -> dict:		"""获取json文件的数据"""		try:			file = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + f'''/{file}/'''			with open(file + filename, 'rb') as f:				data = json.loads(f.read())			return data		except Exception as e:			raise e	@staticmethod	def get_yaml_data(file: str, filename: str) -> dict:		"""读取yaml文件数据"""		try:			file = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + f'''/{file}/'''			with open(file + filename, 'rb') as f:				data = f.read()			datas = yaml.load(data, Loader=yaml.FullLoader)			return datas		except Exception as e:			raise e	@staticmethod	def conn_redis(environment: str):		"""连接redis"""		host, port, pwd, db = '', '', '', ''		if environment == 'test':			host = Config().get_item('test_Redis', 'host')			port = Config().get_item('test_Redis', 'port')			pwd = Config().get_item('test_Redis', 'password')			db = Config().get_item('test_Redis', 'db')		elif environment == 'qa':			host = Config().get_item('qa_Redis', 'host')			port = Config().get_item('qa_Redis', 'port')			pwd = Config().get_item('qa_Redis', 'password')			db = Config().get_item('qa_Redis', 'db')		try:			pool = redis.ConnectionPool(host=host, port=port, password=pwd, db=db, decode_responses=True)			r = redis.Redis(connection_pool=pool)			Ulog.info("连接redis:%s,port:%s,pwd=%s,db=%s" % (host, port, pwd, db))			return r		except Exception as e:			raise e	@staticmethod	def js_detail() -> str:		"""读取js文件"""		try:			with open(os.path.dirname(os.path.abspath(__file__)) + "/user_file.js", encoding='utf-8') as f:				return f.read()		except Exception as e:			raise e	@staticmethod	@allure.step("获取随机姓名身份证号手机号")	def p2p_get_userinfo(project: str, environment: str) -> str:		"""获取姓名身份证号手机号"""		try:			# js = Common.js_detail()			# card_id = execjs.compile(js).call("getIdNo")			# name = execjs.compile(js).call("getName")			# card = execjs.compile(js).call("getBankAccount")			# parm = Common.get_json_data("config", "project.json")			# Common.conn_redis(environment).mset(			# 	{			# 		parm[project]['id']: card_id,			# 		parm[project]['name']: name,			# 		parm[project]['card']: card			# 	}			# )			f = Faker(locale='zh_CN')			name = f.name()			card_id = f.ssn()			card = f.credit_card_number()			parm = Common.get_json_data("config", "project.json")			Common.conn_redis(environment).mset(				{					parm[project]['id']: card_id,					parm[project]['name']: name,					parm[project]['card']: card				}			)		except Exception as e:			raise e	@staticmethod	@allure.step("获取随机姓名身份证号手机号")	def get_userinfo() -> dict:		"""获取姓名身份证号手机号:不存redis"""		try:			f = Faker(locale='zh_CN')			name = f.name()			card_id = f.ssn()			card = f.credit_card_number()			datas = {				"id": card_id,				"name": name,				"card": card			}			return datas		except Exception as e:			raise e	@staticmethod	def get_random(types: str) -> str:		"""生成随机数的id"""		if types == "userid":			return str(random.randint(1, 99999))		elif types == "transactionId":			return str(random.randint(1, 9999999999999999999))		elif types == "serviceSn":			return str(random.randint(1, 9999999999))		elif types == 'phone':			return '155' + str(random.randint(10000000, 99999999))		elif types == 'sourceProjectId':			return str(random.randint(1, 999999))		elif types == 'requestNum':			reqn = ''			for i in range(32):				reqn += random.choice('0123456789')			return reqn		elif types == 'businessLicenseNo':			reqn = ''			for i in range(15):				reqn += random.choice('0123456789')			return reqn		else:			return "不支持更多类型"	@staticmethod	def get_time(types: str = '-') -> str:		"""获取格式化后的当前时间		:rtype:		"""		if types == '-':			return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())		elif types == 'null':			return time.strftime("%Y%m%d%H%M%S", time.localtime())		elif types == 'day':			return time.strftime("%Y-%m-%d", time.localtime())	@staticmethod	def get_repaydate(period: int = 3) -> list:		"""获取还款计划时间"""		plantime = []		for t in range(1, int(period) + 1):			repaytime = str(datetime.datetime.now() + relativedelta(months=+t)).split(" ")[0] + " 00:00:00"			plantime.append(repaytime)		return plantime	@staticmethod	def get_new_time(when: str, what: str, num: int) -> str:		"""		:param when: before or after		:param what: days,minutes,seconds,hours,weeks		:param num: how long time		:return: for example 2020-07-28 11:11:11		"""		times = datetime.datetime.now()		new_times = ''		if when == "after":			if what == "days":				new_times = times + datetime.timedelta(days=num)			elif what == "hours":				new_times = times + datetime.timedelta(hours=num)			elif what == "seconds":				new_times = times + datetime.timedelta(seconds=num)			elif what == "minutes":				new_times = times + datetime.timedelta(minutes=num)			elif what == "weeks":				new_times = times + datetime.timedelta(weeks=num)		elif when == "before":			if what == "days":				new_times = times - datetime.timedelta(days=num)			elif what == "hours":				new_times = times - datetime.timedelta(hours=num)			elif what == "seconds":				new_times = times - datetime.timedelta(seconds=num)			elif what == "minutes":				new_times = times - datetime.timedelta(minutes=num)			elif what == "weeks":				new_times = times - datetime.timedelta(weeks=num)		return str(new_times).split(".")[0]	@staticmethod	@allure.step("执行定时任务{job_name}")	def trigger_task(job_name: str, env: str, productcode: Optional[str] = None):		"""		执行job		creditReparationJob:授信补偿		projectReparationJob:进件补偿		projectLoanReparationJob:放款补偿		projectExpirationCheckJob:放款失败检查		overdueForCloudloanJob:逾期计算		romaOverdueJob:罗马逾期		romaV2OverdueJob:新罗马逾期		romaRepurchaseJob: 罗马债转		assetSwapJob:债转		"""		urls = Common.get_json_data("config", "url.json")		try:			if productcode:				url = urls["job"][env] + job_name + '/' + productcode			else:				url = urls["job"][env] + job_name			requests.post(url, timeout=15)			Ulog.info(f"执行定时任务:任务名称:{job_name};环境:{env};产品code:{productcode}")		except Exception as e:			Ulog.error(e)			pass	@staticmethod	@allure.step("返回信息")	def get_rep_text(rep):		"""获取请求结果输出报告"""		pass