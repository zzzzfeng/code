#coding:utf8

import os

class Scanner:
    def __init__(self,dir):
        self.vul_rules = {
            # 'JavascriptInterface' : 'Webview-js bridge',
            # 'addJavascriptInterface' : 'Webview-js bridge',
            # 'SslErrorHandler;->proceed':'webview-忽略证书错误',
            # 'WebSettings;->setSaveFormData(':'webview-默认保存表单数据',
            # 'setAllowContentAccess':'webview-Content URL access',
            # 'setAllowFileAccess':'webview-access',
            # 'setAllowFileAccessFromFileURLs':'webview-access',
            # 'setAllowUniversalAccessFromFileURLs':'webview-access',
            # 'setJavaScriptEnabled':'webview-access',

            # 'getAcceptedIssuers':'https-信任所有服务器证书',
            # 'JarEntry;->getCertificates':'升级-获取升级包证书',
            # 'X509Certificate;->getPublicKey':'升级-获取本地公钥',
            # 'Certificate;->verify':'升级-验证包身份',
            # 'vnd.android.package-archive':'升级-启动安装器',

            # 'loadLibrary' : 'native-SO 任意load',
            # 'switchToHeaderInner':'Fragment注入',

            # 'getExternalStoragePublicDirectory' : '权限-公共媒体目录',
            # 'getExternalCacheDir':'权限-外部缓存',
            # 'getExternalFilesDir':'权限-外部存储',
            # 'openOrCreateDatabase':'权限-sqlite, 确认加密和文件权限',
            # 'getSharedPreferences':'权限-xml, 确认加密和文件权限',    
            
            #'registerReceiver':'隐私-动态注册的recevier',
            # 'SmsManager':'隐私-发送短信(接口)',
            # 'content://sms/':'隐私-读取短信(数据库cur.query;registerContentObserver)',
            # 'SmsMessage;->':'隐私-过滤短信(receiver)',
            # 'ContactsContract':'隐私-读取通讯录(phone,email)',
            # 'CallLog$Calls':'隐私-读取通话记录',

            # 'qemu_pipe':'trick-反调试',
            # 'KeyboardView$OnKeyboardActionListener':'trick-自定义键盘',
            # 'onPause()V':'trick-覆盖onPause函数, 清除界面敏感信息',
            # 'RunningTaskInfo;->topActivity':'trick-获取activity栈顶',
            'ParcelFileDescriptor openFile(':'provider 读写文件'
        }

        if os.path.exists(dir):
            self.dir = dir

        self.allfiles = []

    
    def getFiles(self, d):    
        if(d):
            for x in os.listdir(d):
                if os.path.isdir(os.path.join(d, x)):
                    self.getFiles(os.path.join(d, x))
                else:
                    self.allfiles.append(os.path.join(d, x))


    def scan(self):
        self.getFiles(self.dir)
        result = {}
        print("Total file: "+ str(len(self.allfiles)))
        for fs in self.allfiles:            
            with open(fs, 'r') as f:
                content = f.read()
                f.close()
            if content == '':
                continue
            for r in self.vul_rules.keys():
                if content.find(r) != -1:
                    if r in result.keys():
                        result[r].append(fs)
                    else:
                        result[r] = [fs]
        for r in result.keys():
            print("==="+r+"\n"+"\n".join(result[r]))


if __name__ == "__main__":
    scanner = Scanner('../../oemapp/jdjr/sources')
    scanner.scan()