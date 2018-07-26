using System;
using System.Collections;
using System.Globalization;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Text;
using Fiddler;
using System.IO;
using System.Diagnostics;
using Microsoft.Win32;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Security.Cryptography;

//app若有接口签名，可以在代理fiddler中添加.net脚本，
//用C:\Users\vuser\Desktop>C:\Windows\Microsoft.NET\Framework\v2.0.50727\csc.exe /target:library /out:out.dll appsign.cs /reference:"C:/Program Files (x86)/Fiddler2/Fiddler.exe"
//编译，然后放在D:\Fiddler2\Scripts目录下即可
//http://www.fiddlerbook.com/Fiddler/dev/ScriptSamples.asp
//工具栏 - 启用
//composer中 重放请求
//右键重放时，修改一次，需要重放两次，第二次才有效
//composer中发送一次 就可以设置或清空变量值
//http请求头中apisecret: example 取消自动签名，工具栏取消启用也可以取消自动签名

 
[assembly: Fiddler.RequiredVersion("2.3.9.0")]
[assembly: AssemblyVersion("1.0.1.0")]
[assembly: AssemblyTitle("APPSign")]
[assembly: AssemblyDescription("app app_sign auotmate")]
[assembly: AssemblyCompany("huafeng.xu")]
[assembly: AssemblyProduct("dy")]
 
public class ApiSign : IAutoTamper2
{
    private bool bEnabled = false;
    private string url = "";
    private string body = "";
    private string path = "";
    private string apisecret = "example";
    private string fsign = "example";
    private System.Windows.Forms.MenuItem miEnabled;
    private System.Windows.Forms.MenuItem mnuApiSign;
 
    public void OnLoad()
    {
        /*
 * NB: You might not get called here until ~after~ one of the AutoTamper methods was called.
 * This is okay for us, because we created our mnuContentBlock in the constructor and its simply not
 * visible anywhere until this method is called and we merge it onto the Fiddler Main menu.
 */
        FiddlerApplication.UI.mnuMain.MenuItems.Add(mnuApiSign);
    }
 
    public void OnBeforeUnload() {  /*noop*/   }

//构造函数
    public ApiSign(){
        this.bEnabled = FiddlerApplication.Prefs.GetBoolPref("extensions.ApiSign.enabled", false);
        InitializeMenu();
    }
 
    private void InitializeMenu()
    {
        this.miEnabled = new System.Windows.Forms.MenuItem("&Enabled");
        this.miEnabled.Index = 0;
        
 
        this.mnuApiSign = new System.Windows.Forms.MenuItem();
        this.mnuApiSign.MenuItems.AddRange(new System.Windows.Forms.MenuItem[] { this.miEnabled});
        this.mnuApiSign.Text = "APPSign";
 
        this.miEnabled.Click += new System.EventHandler(this.miEnabled_Click);
        this.miEnabled.Checked = bEnabled;
 
        
    }
 
    public void miEnabled_Click(object sender, EventArgs e)
    {
        miEnabled.Checked = !miEnabled.Checked;
        bEnabled = miEnabled.Checked;
        FiddlerApplication.Prefs.SetBoolPref("extensions.APPSign.enabled", bEnabled);
        if(bEnabled){
            MessageBox.Show("secret","在http头中添加参数");
        }
        
    }
 

    public void OnPeekAtResponseHeaders(Session oSession) 
    {
        
    }
    public void OnPeekAtRequestHeaders(Session oSession){

    }
    public void AutoTamperRequestBefore(Session oSession) 
    {
        if(oSession.url.IndexOf("auth")==-1||!bEnabled){
            return;
        }
        if(oSession.oRequest["apisecret"] == ""){
            oSession.oRequest["apisecret"] = this.apisecret;
        }else{
            this.apisecret = oSession.oRequest["apisecret"];
        }


        if(bEnabled && "example"!=this.apisecret){
            char[] separator ={'?'};
            char[] separator1 ={'&'};
            char[] separator2 ={'='};
            //oSession.oFlags["x-breakrequest"] = "yup";
            string[] temp = System.Web.HttpUtility.UrlDecode(oSession.url).Split(separator);
            if(temp.Length==2){
                this.url = temp[1];
                this.path = temp[0];
            }
            string pattern = "https?://";
            string replacement = "";
            Regex rgx = new Regex(pattern);
            this.path = rgx.Replace(this.path, replacement);
            string[] ss = this.path.Split(new char[]{'/'});
            this.path = "";
            for(int i=1;i<ss.Length;i++){
                this.path += ss[i]+'/';
            }
            this.path = this.path.TrimEnd('/');

            pattern = "&auth=.{32}";
            rgx = new Regex(pattern);
            this.url = rgx.Replace(this.url, replacement);

            this.body = System.Web.HttpUtility.UrlDecode(oSession.GetRequestBodyAsString());
            string paramss = "";
            
            //decode once
            //this.url = System.Web.HttpUtility.UrlDecode(this.url);
            //this.body = System.Web.HttpUtility.UrlDecode(this.body);

            if(0 != this.url.Length){
                string[] temp1 = this.url.Split(separator1);
                Dictionary<String, String> temp2 = new Dictionary<String, String>();
                ArrayList temp3 = new ArrayList();
                for(int i=0;i<temp1.Length;i++){
                    string[] t = temp1[i].Split(separator2);
                    if(t.Length ==2){
                        temp2.Add(t[0],t[1]);
                        temp3.Add(t[0]);
                    }
                }
                temp3.Sort();
                foreach(object obj in temp3){
                    paramss += (string)obj+'='+temp2[(string)obj]+'&';
                }
            }
            this.url = paramss.TrimEnd('&');
            paramss = "";
            if(0 != this.body.Length){
                string[] temp1 = this.body.Split(separator1);
                Dictionary<String, String> temp2 = new Dictionary<String, String>();
                ArrayList temp3 = new ArrayList();
                for(int i=0;i<temp1.Length;i++){
                    string[] t = temp1[i].Split(separator2);
                    if(t.Length == 2){
                        temp2.Add(t[0],t[1]);
                        temp3.Add(t[0]);
                    }
                }
                temp3.Sort();
                foreach(object obj in temp3){
                    paramss += (string)obj+'='+temp2[(string)obj]+'&';
                }
            }
            this.body = paramss.TrimEnd('&');
            
            string sign;
            sign = EncryptToMD5(this.path+ this.url + this.apisecret+this.body);

            string tt = Regex.Split(oSession.url, "auth=")[0];
            oSession.url = tt+"auth="+sign;
            //oSession.oRequest["body"] = sign+"aa"+paramss;
            this.fsign = sign;

            oSession.oRequest["debug"] = this.path+'?'+this.url+'?'+this.body+'?'+this.apisecret;
        }
    }
    public string EncryptToSHA1(string str)
    {
        SHA1CryptoServiceProvider sha1 = new SHA1CryptoServiceProvider();
        byte[] str1 = Encoding.UTF8.GetBytes(str);
        byte[] str2 = sha1.ComputeHash(str1);
        sha1.Clear();
        StringBuilder sb = new StringBuilder(32); 
        for(int i=0;i<str2.Length;i++){
            sb.Append(str2[i].ToString("x").PadLeft(2, '0'));
        }
        return sb.ToString();
    }
    public string EncryptToMD5(string str)
    {
        MD5 md5 = new MD5CryptoServiceProvider();
        byte[] str1 = Encoding.UTF8.GetBytes(str);
        byte[] str2 = md5.ComputeHash(str1);
        StringBuilder sb = new StringBuilder(32); 
        for(int i=0;i<str2.Length;i++){
            sb.Append(str2[i].ToString("x").PadLeft(2, '0'));
        }
        return sb.ToString();
    }
    public void AutoTamperRequestAfter(Session oSession){
        this.url = "";
        this.body = "";
    }
    public void AutoTamperResponseAfter(Session oSession) {/*noop*/}
    public void AutoTamperResponseBefore(Session oSession) 
    {
        if(bEnabled){
            oSession.oResponse.headers["APISign"] = this.fsign;
            oSession.oResponse.headers["apisecret"] = this.apisecret;
        }
        //oSession.oResponse.headers["body"] = this.body;
    }
    public void OnBeforeReturningError(Session oSession) {/*noop*/}
}
