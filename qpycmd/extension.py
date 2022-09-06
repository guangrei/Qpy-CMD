# -*-coding:utf8;-*-
"""
The MIT License (MIT)

Copyright (c) 2022 Qpy-CMD https://github.com/guangrei/Qpy-CMD

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from subprocess import Popen, PIPE, call
import os
import sys
from .climate import get_contents, Styled
import shlex
import json


class Extension(object):
    def __init__(self):
        path = os.getenv("QEXTPATH")
        if path == None:
            path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/.ext/"
        if not os.path.isdir(path):
            os.mkdir(path)
        self.__path = path
        self.process_list = {}
        self.__py = sys.executable
        self.__meta = "https://raw.githubusercontent.com/guangrei/Qpy-EXT/main/meta.json"

    def __install(self, pkg):
        v = self.__path+pkg+"/"
        if not os.path.isdir(v):
            req = get_contents(self.__meta)
            if not req:
                print("failed connect to server!")
            else:
                data = json.loads(req)
                if self.__verify(data, pkg):
                    print("installing %s" % pkg)
                    d2 = data[pkg]
                    os.mkdir(v)
                    success = True
                    if len(d2["require"]) > 0:
                        self.__pip__installer(d2["require"])
                    for k in d2["files"]:
                        uri = data["META"]["prefix"]+pkg+"/"+k
                        print("downloading %s... " % uri, end="")
                        cf = get_contents(uri)
                        if cf != False:
                            print("done!")
                            self.__insert(v, k, cf)
                        else:
                            print("failed!")
                            success = False
                            self.__uninstall(pkg)
                            break
                    if success:
                        print("success installing extension %s" % pkg)
                    else:
                        print("extension isn't installed!")
                else:
                    print("extension %s isn't found!" % pkg)
        else:
            print("extension %s is already installed!" % pkg)

    def __upgrade(self, pkg):
        v = self.__path+pkg+"/"
        if os.path.isdir(v):
            req = get_contents(self.__meta)
            if not req:
                print("failed connect to server!")
            else:
                data = json.loads(req)
                if self.__verify(data, pkg):
                    d2 = data[pkg]
                    if self.__need_upgrade(v+".version", d2["version"]):
                        print("upgrading %s" % pkg)
                        success = True
                        if len(d2["require"]) > 0:
                            self.__pip__installer(d2["require"])
                        for k in d2["files"]:
                            uri = data["META"]["prefix"]+pkg+"/"+k
                            print("downloading %s ... " % uri, end="")
                            cf = get_contents(uri)
                            if cf != False:
                                print("done!")
                                self.__insert(v, k, cf)
                            else:
                                print("failed!")
                                success = False
                                break
                        if success:
                            print("success upgrading extension %s" % pkg)
                        else:
                            print("upgrading extension isn't completed!")
                    else:
                        print("you have newer %s version!" % pkg)
                else:
                    print("extension %s isn't found!" % pkg)
        else:
            print("extension %s isn't installed!" % pkg)

    def __insert(self, path, nama, content):
        with open(path+nama, "w") as f:
            f.write(content)

    def __verify(self, d, k):
        try:
            check = d[k]
            return True
        except KeyError:
            return False

    def __update_check(self):
        ls = os.listdir(self.__path)
        pref = "https://raw.githubusercontent.com/guangrei/Qpy-EXT/main/pkg/"
        no_update = True
        for i in ls:
            with open(self.__path+i+"/.version", "r") as f:
                local = f.read()
            remote = get_contents(pref+i+"/.version")
            print("Checking %s ... " % i, end="")
            if remote != False:
                if local != remote:
                    print("done!")
                    print("---")
                    print(
                        "Update {0} version {1} available!".format(i, remote))
                    print(
                        "Please upgrade with command: ext upgrade {0}".format(i))
                    print("---")
                    no_update = False
                else:
                    print("done!")

            else:
                print("failed!")
        if len(ls) == 0:
            print("you have 0 installed extension!")
        if no_update:
            print("---")
            print("All Extensions is UP-TO-DATE!")

    def __need_upgrade(self, path, version):
        with open(path, "r") as f:
            return f.read() != version

    def __uninstall(self, pkg):
        v = self.__path+"/"+pkg+"/"
        if os.path.isdir(v):
            print("uninstalling %s... " % pkg, end="")
            shutil.rmtree(v)
            print("done!")
        else:
            print("extension %s isn't installed!" % pkg)

    def __pip_installer(self, pkgs):
        for pkg in pkgs:
            print("installing dependency %s ..." % pkg)
            com = "{0} install {1}".format(self.__py+" -m pip", pkg)
            os.system(com)

    def is_exists(self, pkg):
        return os.path.isdir(self.__path+pkg)

    def get_bin(self):
        return os.listdir(self.__path)

    def __list(self):
        ls = os.listdir(self.__path)
        myls = []
        for i in ls:
            with open(self.__path+i+"/.version", "r") as f:
                myls.append("{0} {1}".format(i, f.read()))
        print("\n".join(myls))

    def CMD(self, argv):
        if len(argv) >= 2:
            alias = {"rm": "uninstall", "i": "install",
                     "ls": "list", "U": "upgrade", "up": "update"}
            if argv[1] in alias:
                argv[1] = alias[argv[1]]
        try:
            if argv[1] == "install":
                if len(argv) == 3:
                    self.__install(argv[-1])
                else:
                    print("Usage: ext install <ext-name>")
            elif argv[1] == "uninstall":
                if len(argv) == 3:
                    self.__uninstall(argv[-1])
                else:
                    print("Usage: ext uninstall <ext-name>")
            elif argv[1] == "upgrade":
                if len(argv) == 3:
                    self.__upgrade(argv[-1])
                else:
                    print("Usage: ext upgrade <ext-name>")
            elif argv[1] == "list":
                print("list installed extensions:\n---")
                self.__list()
            elif argv[1] == "update":
                self.__update_check()
            else:
                print("Usage: ext <command>")
                print("---\nAvailable Command:")
                print("install    : install extension.")
                print("uninstall  : uninstall extension.")
                print("upgrade    : upgrade extension.")
                print("update     : Check Available Extension update.")
                print("list       : list installed extension.")
        except IndexError:
            print("Usage: ext <command>")
            print("---\nAvailable Command:")
            print("install    : install extension.")
            print("uninstall  : uninstall extension.")
            print("upgrade    : upgrade extension.")
            print("update     : Check Available Extension update.")
            print("list       : list installed extension.")

    def run(self, wd, argv):
        os.chdir(wd)
        os.environ["EXT_DIR"] = self.__path+argv[0]
        argv[0] = self.__path+argv[0]+"/main.py"
        com = "{0} {1}".format(self.__py, " ".join(argv))
        os.system(com)

    def bg_run(self, wd, argv):
        cm = " ".join(argv)
        exp = os.environ.copy()
        exp["EXT_DIR"] = self.__path+argv[0]
        argv[0] = self.__path+argv[0]+"/main.py"
        com = "{0} {1}".format(self.__py, " ".join(argv))
        p = Popen(shlex.split(com), cwd=wd, env=exp)
        print("pid: %d" % int(p.pid))
        self.process_list[p.pid] = {}
        self.process_list[p.pid]["program"] = cm
        self.process_list[p.pid]["obj"] = p
