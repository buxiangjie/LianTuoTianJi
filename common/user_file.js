// noinspection JSCheckFunctionSignatures,JSCheckFunctionSignatures,JSCheckFunctionSignatures,JSCheckFunctionSignatures,JSCheckFunctionSignatures,JSCheckFunctionSignatures

function getIdNo() {
	let coefficientArray = ["7", "9", "10", "5", "8", "4", "2", "1", "6", "3", "7", "9", "10", "5", "8", "4", "2"]; // 加权因子
	let lastNumberArray = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]; // 校验码
	let address = "420101"; // 住址

	let birthday = "" + (parseInt(20 * Math.random()) + 1970) + "0" + (parseInt(9 * Math.random()) + 1) + (parseInt(20 * Math.random()) + 10); // 生日
	let s = Math.floor(Math.random() * 10).toString() + Math.floor(Math.random() * 10).toString() + Math.floor(Math.random() * 10).toString();
	let array = (address + birthday + s).split("");
	let total = 0;
	for (let i = 0; i < array.length; i++) {
		total = total + parseInt(array[i]) * parseInt(coefficientArray[i]);
	}
	let lastNumber = lastNumberArray[parseInt(total % 11)];
	return address + birthday + s + lastNumber;
}

// 生成随机姓名
function getName() {
	let familyNames = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空丌官司寇仉督子车颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁晋楚闫法汝鄢涂钦段干百里东郭南门呼延归海羊舌微生岳帅缑亢况郈有琴梁丘左丘东门西门商牟佘佴伯赏南宫墨哈谯笪年爱阳佟";
	let givenNames = "子璇淼国栋夫子瑞堂甜敏尚国贤贺祥晨涛昊轩易轩辰益帆冉瑾春瑾昆春齐杨文昊东雄霖浩晨熙涵溶溶冰枫欣宜豪欣慧建政美欣淑慧文轩杰欣源忠林榕润欣汝慧嘉新建建林亦菲林冰洁佳欣涵涵禹辰淳美泽惠伟洋涵越润丽翔淑华晶莹凌晶苒溪雨涵嘉怡佳毅子辰佳琪紫轩瑞辰昕蕊萌明远欣宜泽远欣怡佳怡佳惠晨茜晨璐运昊汝鑫淑君晶滢润莎榕汕佳钰佳玉晓庆一鸣语晨添池添昊雨泽雅晗雅涵清妍诗悦嘉乐晨涵天赫玥傲佳昊天昊萌萌若萌测试身份证号大全和名由程序随机组合而成所有信息均为虚构生成不会泄密真实公民隐私信息也非现实生活中真实的身份证号码和真实名身份证号码所属年龄均为岁以上均已通过校验身份证号码和名仅供测试或用在必须输入身份证号码和名的网站上请不要将身份证号码和名用于任何非法用途且自行承担使用本工具的任何后果和责任";

	let i = parseInt(familyNames.length * Math.random());
	let familyName = familyNames.substr(i, 1);
	let len = givenNames.length;
	let j = parseInt(len * Math.random());
	let k = parseInt(len * Math.random());
	let givenName = givenNames.substr(j, 1) + givenNames.substr(k, 1);
	return familyName + givenName;
}

//生成随机银行卡号
function getBankAccount() {

	// let bank_no = document.getElementById("bank_no_select").value;
	let bank_no = '0308';
	let prefix = "";
	switch (bank_no) {
		case "0102":
			prefix = "622202";
			break;
		case "0103":
			prefix = "622848";
			break;
		case "0105":
			prefix = "622700";
			break;
		case "0301":
			prefix = "622262";
			break;
		case "104":
			prefix = "621661";
			break;
		case "0303":
			prefix = "622666";
			break;
		case "305":
			prefix = "622622";
			break;
		case "0306":
			prefix = "622556";
			break;
		case "0308":
			prefix = "622588";
			break;
		case "0410":
			prefix = "622155";
			break;
		case "302":
			prefix = "622689";
			break;
		case "304":
			prefix = "622630";
			break;
		case "309":
			prefix = "622908";
			break;
		case "310":
			prefix = "621717";
			break;
		case "315":
			prefix = "622323";
			break;
		case "316":
			prefix = "622309";
			break;
		default:
	}

	for (let j = 0; j < 10; j++) {
		prefix = prefix + Math.floor(Math.random() * 10);
	}
	return prefix;
}

// document.getElementById("id").innerText = getIdNo();
// document.getElementById("name").innerText = getName();
// document.getElementById("card").innerText = getBankAccount();