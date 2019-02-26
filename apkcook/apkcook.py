#!/usr/bin/env python
#coding:utf8
'''

1、获取APK暴露组件
2、扫描反编译源码目录（动态recevier；）

'''

import argparse
import apk

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Android apk tools")
    parser.add_argument("-f", dest="file", help="path to AndroidManifest.xml")
    parser.add_argument("-p", dest="package", help="path to APK")
    parser.add_argument("-a", dest="all", action='store_true', help="print AndroidManifest.xml")

    parser.add_argument("-s", dest="scan", help="source path to scan")
    
    args = parser.parse_args()
    if args.package:
        apkcook = apk.APKCook(args.package)
        if args.all:
            apkcook.output()
        else:
            apkcook.show()
    elif args.file:
        apkcook = apk.APKCook(args.file, True)
        if args.all:
            apkcook.output()
        else:
            apkcook.show()
    elif args.scan:
        import scanner
        sc = scanner.Scanner(args.scan)
        sc.scan()
        
    else:
        parser.print_help()
