- 前言

1、互联网业务经常会有送券、领红包等活动，通常礼品发放是基于单个用户ID只发放一次原则，同时还会结合是否新用户、是否非常客(熟客不给优惠)等策略。

羊毛党薅羊毛场景：1、编写领礼品（券和红包统称礼品）脚本；2、导入批量用户cookie或手机号，导入批量网络代理(绕基于IP的风控)；3、脚本开启，不出意外可以掌握大量的券和红包，接着转卖或代购

互联网厂商对抗羊毛党：1、要求输入图形验证码；2、要求输入短信验证码

然而，图形验证码可以接入云打码平台或者使用基于机器学习的图像识别技术；短信验证码也可以自动通过代码接收到

所以厂商都会有个风控措施，生成客户端的唯一dev_ID（dev_ID不可伪造，一般通过混淆算法来防止伪造，且及时更新算法，且同一设备(android,chrome)访问生成的dev_ID唯一)，(dev_ID,Phone)构成唯一用户ID。羊毛党若不能破解dev_ID的生成算法，就无法通过脚本批量薅羊毛

2、网站都有注册、登录等发短信功能，为防止短信接口被刷，一般加上图形验证码，这样用户体验相对较差。结合dev_ID,phone,ip等“身份信息”，在触发风险后要求输入图形验证码，用户体验会好得多

所以互联网厂商都应该设计自己的dev_ID用来改善用户体验，对抗刷量

（基于用户前后行为关联的风控措施更有效  但无法做到通用；也不知是否有更高端玩法）

本文分析数美科技提供的js版dev_ID生成算法https://fp.fengkongcloud.com/v2/web/profile?callback=smCB_1536454623693&organization=&smdata=&os=web&version=2.0.0&_=1536454623693，顺便学习了混淆代码的常见姿势，以及js怪异的语法

1、斗鱼-单点登录页面集成了相关功能(可以用来调试js)，

抓包获取相关js https://static.fengkongcloud.com/fpv2.js，

反混淆版 code/fpv2_de.js at master · zzzzfeng/code · GitHub

2、下载的js文件经过压缩和混淆操作，首先要格式化js使之可读性变强

使用现成工具在线代码格式化或JS Beautify and Minify - Online格式化，后者会对hex字符串进行转码

下面这段python代码也可以将js文件中的hex字符串进行转码

```
import re

ct = ''
with open('fpv2.js') as f:
	ct = f.read()

if ct != '':
	#\x23类似hex 转换成字符串
	#由于中文hex编码会多于一个字节：\x23\x23\x34，所以不能单个字节进行解码，需要连续解码
	#首先找到hex进制字符串
	matches = re.findall(r"((\\x.{2})+)", ct, re.MULTILINE)

	targets = [m[0] for m in matches]
	targets = list(set(targets))#去重
	#按长度排序，降序；
	#防止替换出错\xaa,\xaa\xbb这种情况会导致\xaa\xbb无法被完整替换
	target = sorted(targets, key=lambda i:len(i), reverse=True)

	for t in target:
		#不解码null
		if t.find(r'\x00') != -1 or t.find(r'\x0a') != -1 or t.find(r'\x0d') != -1:
			continue
		tt = t.replace(r'\x', '')
		ct = ct.replace(t, tt.decode('hex'))

	with open('fpv2_de.js', 'w') as f:
		f.write(ct)
    
 ```
 
 3、格式化后的代码整体上分三块，如图
 ![image](https://user-images.githubusercontent.com/8851007/181175424-5eeed5c4-1626-428c-9b86-d9b023be638f.png)
第一部分：存储base64格式函数名的数组，及将数组倒置的自执行函数

第二部分：根据索引从数组中获取并解码得到函数名的函数，注意该函数声明接收两个参数，但后续代码中调用全部只传一个参数，这种语法在js中成立

第三部分：一个自执行函数，关键逻辑在该函数。该函数形参、实参数目相等，便于分析，以下是分析过程

①参数数目有749个，要将实参对应到形参（不可能一个个数下去）借助以下python脚本，根据形参的index，获取对应index实参的值
```
pp = '''p1, p2, p3'''#形参列表
pp = pp.split(', ')#注意空格
print(len(pp))
index = pp.index('_0x54961a')#目标形参名称及其索引
print(index)

ps = '''s1, s2, s3'''#实参列表
ps = ps.split(', ')#避免参数里面含有逗号，所以加上空格
print(len(ps))
print(ps[index])#根据形参索引，获得对应实参的值
```
使用脚本获取实参


②代码中多次调用第二部分的函数_0xa1c1，所以为了方便，将第一部分和第二部分代码放在chrome控制台执行，借助浏览器的执行环境，直接执行解出混淆之前的字符串，如下图
![image](https://user-images.githubusercontent.com/8851007/181175730-d1dcb4a1-2b1a-47fa-bc97-3276354d3491.png)


另外代码中定义了很多函数对象，以及独立的小函数 都可以借助浏览器执行环境
![image](https://user-images.githubusercontent.com/8851007/181175847-9c954a9f-93c1-42be-88bc-538e937fc2c7.png)

主函数逻辑如下，执行6个case即可，case之间有依赖关系（按4，6，0，3，1，5，2顺序执行）
![image](https://user-images.githubusercontent.com/8851007/181175952-5d65a19a-93e5-4f68-ba33-74e9f18efd98.png)

③case 1和case 5中对arguments进行了变换，所以在case 2中分析时，需要将实参进行对调，

（将arguments赋值给_0x3ab64f，对_0x3ab64f进行变换，会导致形参名对应的实参变化？JS代码确实会变化 控制台执行(function(a,b,c){var aa = arguments;aa[1]=4;console.log(aa);console.log(arguments)})(1,2,3)）

如下对实参位置进行部分调换，得到如果是字符串还需要反转( 控制台'strings'['split']('')['reverse']()['join']('') 进行反转)
```
ps = ps.split(', ')
print(len(ps))
print(ps[index])

for x in range(0, 739/2):
	t = ps[x]
	ps[x] = ps[739 - x -1]
	ps[739 - x -1] = t

print(ps[index])
```

④case 2代码3000多行，所以借助以下脚本将case 2代码中的形参替换为实参
```
#第一部分的逻辑
_0x1c1a = ['eEZE', 'R2xS']
#反转部分
for x in range(1,355):
	_0x1c1a.append(_0x1c1a.pop(0))

ct = ''
with open('case2') as f:
	ct = f.read()
#形参实参替换, 得到的字符串需要反转
for i in range(0, len(pp)):
	ss = pp[i]
	rr = ''
	if ps[i].find('_0xa1c1') != -1:
		#_0xa1c1函数,base64解码后反转
		matches = re.findall(r"\(\'([0-9A-Za-z]+)\'\)", ps[i])
		ind = int(matches[0][2:], 16)
		rr = "'"+base64.b64decode(_0x1c1a[ind])[::-1]+"'"
	elif ps[i].find("'") != -1:
		#字符串反转
		rr = ps[i][::-1]
	else:
		rr = ps[i]

	ct = ct.replace(ss, rr)
#_0xa1c1函数调用替换
matches = re.findall(r"(_0xa1c1\(\'([0-9A-Za-z]+)\'\))", ct, re.MULTILINE)
for m in matches:
	ss = m[0]
	ind = int(m[1][2:], 16)
	rr = "'"+base64.b64decode(_0x1c1a[ind])+"'"
	ct = ct.replace(ss, rr)
```
经过上述处理，代码稍微变得直观了，但函数内部仍然有许多混淆的措施


⑤结合抓包，确定先从smdata的生成算法入手分析



organization为调用方配置



搜到发去网络请求的函数_0x3e4b16()，根据预置的sign和从设备收集的各类信息调用函数_0x5f1db4生成smdata



sign从函数_0x3d7e21中返回，其值根据形参_0x3d899c得到 为null  (确定了几遍，确实为null，也经过调试验证)



设备各类信息包括如下，在函数_0x2ddd6b中处理
![image](https://user-images.githubusercontent.com/8851007/181176693-57e83745-af7b-49ca-ace0-3a98b1ecc8ef.png)



函数_0x5f1db4(sign, dev_feature)生成smdata，且sign值会被函数_0x17f011处理下，dev_feature处理成p1=v1&p2=v2形式

调试获取的dev_feature

"channel=&deviceId=20180824104925b27f7db87b737eb26c9dab74b6c740d9000ccac85abccfbd0&plugins=ChromePDFPluginPortableDocumentFormatinternal-pdf-viewer1%2CChromePDFViewermhjfbmdgcfjbbpaeojofohoefgiehjai1%2CNativeClientinternal-nacl-plugin2%2CWidevineContentDecryptionModuleEnablesWidevinelicensesforplaybackofHTMLaudio%2Fvideocontent.(version%3A1.4.9.1076)widevinecdmadapter.dll1&ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F66.0.3359.117%20Safari%2F537.36&canvas=ed07ea27&timezone=-480&time=7&platform=Win32&url=https%3A%2F%2Fpassport.douyu.com%2Findex%2Flogin&referer=&res=1920_1080_24&status=0010&clientSize=0_0_1903_485_1920_1080_1920_1040&appCodeName=Mozilla&appName=Netscape&oscpu=&area=-1_-1&sid=1535097051043-1197838&version=2.0.0&sdl=0_1_8_0_16_0"

⑥代码逻辑理顺，然后开启chrome调试工具

在chrome开发者工具source栏下找到fpv2.js文件，点击文件预览下方的{}（下图红色箭头位置），对代码格式化显示，在case 2处设置断点，然后刷新页面，等待一会儿就可以开始调试js代码



调试工具条，依次为停止调试，跳至下一调用（函数内部），单步调用，跳出当前函数，到下一断点，取消断点，捕获异常



case2最外层只是一个函数调用，谨慎使用“跳至下一调用（函数内部）”，“跳出当前函数”工具。且调试过程经常出现浏览器崩溃

调试小技巧，在关键函数位置设置断点，然后尽管使用“跳出当前函数”（由于混淆代码各种包装，会有很多函数跳转）

⑦调试过程发现，由于sign值为null，smdata最终由catch块返回，如下图红色箭头



变量_0x115cdb由形参_0x5bb864决定，此处为'W'

_0x7cc569函数catch块中函数_0x574b17(key,dev_feature,1)处理后 接着被_0x17199f(base64)函数处理，拼接上时间戳，然后返回的就是smdata



时间戳在case2 变量_0x514c7f中，固定值"1487577677129"，key为SMshumei如下图



⑧故smdata=‘W'+base64(_0x574b17('SMshumei',dev_feature,1))+'1487577677129'

浏览器控制台执行‘W'+_0x17199f(_0x574b17('SMshumei',dev_feature,1))+'1487577677129'即可得到smdata

（dev_feature中包含的deviceId参数为浏览器端生成，猜测数美服务器端通过对比dev_feature中收集到其他设备特征信息，来判断是否为同一设备，如果特征信息风险校验通过，则该devicId可以使用）



- 从中学习到的混淆技巧：

》字符串及函数名使用16进制表示、base64编码、反转

》从数组中查找字符串

》使用超长函数参数

》数组进行部分倒置

》使用统一格式的名称，难于区分

》加减乘除使用自定义函数多层包装，且使用多个函数实现同一功能

》从函数对象中查找函数定义



》使用while循环替代顺序执行



》使用catch改变执行流程

PS：结合反混淆的过程得出一个混淆好方法，变量名混淆成_0xaaa, _0xaaab，_0xaaac变量之间有重叠部分，反混淆时替换(字符串匹配)形参到实参时会出现异常情况

反混淆后的js代码https://github.com/zzzzfeng/code/blob/master/fpv2_de.js
