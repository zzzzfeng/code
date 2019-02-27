#coding:utf8
'''

1、从raw AndroidManifest.xml文件或APK文件中获取暴露组件
2、从raw AndroidManifest.xml文件或APK文件中获取明文AndroidManifest.xml

'''
# 加密zip ChilkatZip


import bytecode

from axmlprinter import AXMLPrinter
from bytecode import SV

import zipfile, StringIO
from struct import pack, unpack
from xml.dom import minidom


class APKCook:
    def __init__(self, filename, single=False, text=False):
        
        self.filename = filename
        self.xml = {}
        self.package = ""
        self.androidversion = {}
        self.raw_manifest = ""

        fd = open(filename, "rb")
        self.__raw = fd.read()
        fd.close()

        if single:
            self.raw_manifest = self.__raw
        else:
            self.zip = zipfile.ZipFile(StringIO.StringIO(self.__raw))
            for i in self.zip.namelist():
                if i == "AndroidManifest.xml":
                    self.raw_manifest = self.zip.read(i)
        if text:
            self.xml = minidom.parseString(self.raw_manifest)
        else:
            self.xml = minidom.parseString(AXMLPrinter(self.raw_manifest).getBuff())

        self.package = self.xml.documentElement.getAttribute("package")
        self.androidversion["Code"] = self.xml.documentElement.getAttribute("android:versionCode")
        self.androidversion["Name"] = self.xml.documentElement.getAttribute("android:versionName")

    def get_package(self):
        return self.package

    def get_androidversion_code(self):
        return self.androidversion["Code"]
    
    def get_androidversion_name(self):
        return self.androidversion["Name"]

    def get_permission(self):
        out = []
        for item in self.xml.getElementsByTagName("permission"):
            name = item.getAttribute("android:name")
            pl = item.getAttribute("android:protectionLevel")
            if pl == "0x00000000":
                name += "@normal"
            elif pl == "0x00000001":
                name += "@dangerous"
            elif pl == "0x00000002":
                name += "@signature"
            elif pl == "0x00000003":
                name += "@signatureOrSystem"

            out.append(name)

        return out;

    def get_element(self, tag_name, attribute):
        for item in self.xml.getElementsByTagName(tag_name):
            value = item.getAttribute(attribute)

            if len(value) > 0:
                return value
        return None

    def get_min_sdk_version(self):
        return self.get_element("uses-sdk", "android:minSdkVersion")
    
    def get_target_sdk_version(self):
        return self.get_element("uses-sdk", "android:targetSdkVersion")

    def get_activities(self):
        out = []
        for item in self.xml.getElementsByTagName("activity"):
            exported = item.getAttribute("android:exported")
            name = ""
            if exported == "true":
                name = item.getAttribute("android:name")
            elif exported != "false":
                #未设置exported属性，则检查是否有intent-filter
                if len(item.getElementsByTagName("intent-filter")) > 0:
                    name = item.getAttribute("android:name")
            
            #未开启
            if item.getAttribute("android:enabled") == "false":
                if name != "":
                    name = "!disabled!"+name

            #要求权限
            if item.getAttribute("android:permission") != "":
                if name != "":
                    name += "@"+item.getAttribute("android:permission")
            
            if name != "":
                out.append(name)

        for item in self.xml.getElementsByTagName("activity-alias"):
            exported = item.getAttribute("android:exported")
            name = ""
            if exported == "true":
                name = item.getAttribute("android:name")
            elif exported != "false":
                #未设置exported属性，则检查是否有intent-filter
                if len(item.getElementsByTagName("intent-filter")) > 0:
                    name = item.getAttribute("android:name")
            
            #未开启
            if item.getAttribute("android:enabled") == "false":
                if name != "":
                    name = "!disabled!"+name

            #要求权限
            if item.getAttribute("android:permission") != "":
                if name != "":
                    name += "@"+item.getAttribute("android:permission")
            
            if name != "":
                out.append(name)

        return out
    
    def get_services(self):
        out = []
        for item in self.xml.getElementsByTagName("service"):
            exported = item.getAttribute("android:exported")
            name = ""
            if exported == "true":
                name = item.getAttribute("android:name")
            elif exported != "false":
                #未设置exported属性，则检查是否有intent-filter
                if len(item.getElementsByTagName("intent-filter")) > 0:
                    name = item.getAttribute("android:name")
            
            #未开启
            if item.getAttribute("android:enabled") == "false":
                if name != "":
                    name = "!disabled!"+name

            #要求权限
            if item.getAttribute("android:permission") != "":
                if name != "":
                    name += "@"+item.getAttribute("android:permission")
            
            if name != "":
                out.append(name)

        return out
    
    def get_receivers(self):
        out = []
        for item in self.xml.getElementsByTagName("receiver"):
            exported = item.getAttribute("android:exported")
            name = ""
            if exported == "true":
                name = item.getAttribute("android:name")
            elif exported != "false":
                #未设置exported属性，则检查是否有intent-filter
                if len(item.getElementsByTagName("intent-filter")) > 0:
                    name = item.getAttribute("android:name")
            
            #未开启
            if item.getAttribute("android:enabled") == "false":
                if name != "":
                    name = "!disabled!"+name

            #要求权限
            if item.getAttribute("android:permission") != "":
                if name != "":
                    name += "@"+item.getAttribute("android:permission")
            
            if name != "":
                out.append(name)

        return out
    
    def get_providers(self):
        out = []
        for item in self.xml.getElementsByTagName("provider"):
            exported = item.getAttribute("android:exported")
            name = ""
            if exported == "true":
                name = item.getAttribute("android:name")
            elif exported != "false":
                #未设置exported属性，则检查是否有intent-filter
                if len(item.getElementsByTagName("intent-filter")) > 0:
                    name = item.getAttribute("android:name")
            
            #未开启
            if item.getAttribute("android:enabled") == "false":
                if name != "":
                    name = "!disabled!"+name

            #要求权限
            if item.getAttribute("android:permission") != "":
                if name != "":
                    name += "@"+item.getAttribute("android:permission")
            
            if name != "":
                out.append(name)
                
        return out
    
    
    
    def show(self):
        print ("===暴露组件===(注意调用权限，动态recevier未检测)")
        print ("Package: "+self.get_package())
        print ("VersionName: "+self.androidversion["Name"]+" VersionCode: "+self.androidversion["Code"])
        print ("Min_sdk: "+self.get_min_sdk_version()+" Target_sdk: "+self.get_target_sdk_version())
        print ("==Activity:\n"+"\n".join(self.get_activities()))
        print ("==Service:\n"+"\n".join(self.get_services()))
        print ("==Receive:\n"+"\n".join(self.get_receivers()))
        print ("==Provider:\n"+"\n".join(self.get_providers()))
        print ("==Permission:\n"+"\n".join(self.get_permission()))

    def output(self):
        print(AXMLPrinter(self.raw_manifest).getBuff())


if __name__ == "__main__":
    apkcook = APKCook('../../oemapp/thememanager.apk')
    apkcook.show()

    # apkcook = APKCook('AndroidManifest.xml' ,True)
    # apkcook.show()
