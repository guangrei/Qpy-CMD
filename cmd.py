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
from subprocess import Popen, PIPE
import androidhelper as sl4a
import time
import sys
import os
import shlex
import json
import shutil


def get_contents(url):
    try:
        import ssl
        import urllib.request
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except:
        try:
            import requests
            response = requests.get(url, verify=False)
            return response.text
        except:
            return False


class Extension(object):
    def __init__(self):
        path = os.path.dirname(sys.argv[0]) + "/.ext/"
        if not os.path.isdir(path):
            os.mkdir(path)
        self.__path = path
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
            else:
                print("Usage: ext <command>")
                print("---\nAvailable Command:")
                print("install    : install extension.\nuninstall  : uninstall extension.\nupgrade    : upgrade extension.\nlist       : list installed extension.")
        except IndexError:
            print("Usage: ext <command>")
            print("---\nAvailable Command:\n")
            print("install    : install extension.\nuninstall  : uninstall extension.\nupgrade    : upgrade extension.\nlist       : list installed extension.")

    def run(self, wd, argv):
        exp = 'export EXT_DIR="%s"' % self.__path+argv[0]
        argv[0] = self.__path+argv[0]+"/main.py"
        com = "{0} {1}".format(self.__py, " ".join(argv))
        f = "{0} && cd {1} && {2}".format(exp, wd, com)
        os.system(f)


class QPyCMD(object):
    def __init__(self):
        self.__version__ = "v2.0"
        self.last_output = ""
        self.__ext = Extension()
        self.process = Popen(
            ['sh'],
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            universal_newlines=True,
            bufsize=0)
        self.process.stdin.write('cd /sdcard/qpython/\n')
        self.process.stdin.flush()
        self.commander = {}
        self.droid = sl4a.Android()
        self.normalizer = {}

    def get_bin(self):
        ls = []
        m = dict(self.commander, **self.normalizer)
        for k, v in m.items():
            if k != "cd":
                ls.append(k)
        return ls+self.__ext.get_bin()

    def __dump_path(self, cmd):
        print("QPy CMD executable:")
        print("---")
        for i in self.get_bin():
            print("[<]:", i)
        sy = os.environ["PATH"].split(":")
        for i in sy:
            print("\n%s executable:" % i)
            print("---")
            for j in os.listdir(i):
                print("[<]:", j)
        print("\n----------\nCAUTION!!\n----------")
        print(
            "\n* some executable may not compatible in Qpy CMD, so you can run it in cmd2.")
        print("** some executable may need root permission")
        print("*** some executable could make your device crashed, so make sure you know what you do!")

    def set_normalizer(self, fun_name, fun):
        if callable(fun):
            self.normalizer[fun_name] = fun
        else:
            raise Exception(type(fun) + " isn't callable")

    def set_command(self, fun_name, fun):
        if callable(fun):
            self.commander[fun_name] = fun
        else:
            raise Exception(type(fun) + " isn't callable")

    def __check_update(self):
        print("[<]: checking for update")
        rs = get_contents(
            "https://raw.githubusercontent.com/guangrei/Qpy-CMD/main/version.txt")
        if rs != False:
            if rs != self.__version__:
                return True
            else:
                print("you already use version " + tx)
                return False
        else:
            print("failed to checks update!")
            return False

    def __update(self, cmd):
        if(self.__check_update()):
            print("updating..")
            path = os.path.dirname(sys.argv[0]) + "/cmd.py"
            rs = get_contents(
                "https://raw.githubusercontent.com/guangrei/Qpy-CMD/main/cmd.py")
            if rs != False:
                import requests
                with open(path, "w") as f:
                    f.write(rs)
                    f.close()
                    print("update completed! please re-run " + path)
            else:
                print("update failed!")
        return False

    def __shell(self, txcmd):
        cmd = shlex.split(txcmd)
        if txcmd.strip() == "":
            return False
        elif ("&&" in cmd):
            for i in txcmd.split("&&"):
                self.__shell(i.strip())
        elif cmd[0] in self.commander:
            return self.commander[cmd[0]](cmd)
        elif self.__ext.is_exists(cmd[0]):
            self.__cmdIn('pwd', output=False)
            if os.path.isdir(self.last_output):
                self.__ext.run(self.last_output, cmd)
        else:
            self.__cmdIn('pwd', output=False)
            if cmd[0] in self.normalizer:
                com = self.normalizer[cmd[0]](cmd)
            else:
                com = txcmd
            fc = "cd {dir} && {com}".format(dir=self.last_output, com=com)
            if os.path.isdir(self.last_output):
                os.system(fc)
            else:
                return False

    def __cmdIn(self, com, output=True):
        txcmd = 'cmd="' + com + '"; $cmd; echo "<#eol#>"\n'
        self.process.stdin.write(txcmd)
        self.process.stdin.flush()
        self.__cmdOut(cout=output)

    def __cmdOut(self, cout=True):
        for out in self.process.stdout:
            if out != "<#eol#>\n":
                if cout:
                    print("[<]:", out.strip())
                else:
                    self.last_output = out.strip()
            else:
                break

    def __python(self, cmd):
        cmd[0] = sys.executable
        return " ".join(cmd)

    def __help(self, cmd):
        print("QPy CMD " + self.__version__ + " by guangrei.")
        print("For more info and support please open https://github.com/guangrei/Qpy-CMD")
        return False

    def __pip(self, com):
        com[0] = sys.executable + " -m pip"
        return " ".join(com)

    def __cd(self, argv):
        return " ".join(argv)

    def __easy_install(self, com):
        com[0] = sys.executable + " -m easy_install"
        return " ".join(com)

    def __pydoc(self, com):
        com[0] = sys.executable + " -m pydoc"
        return " ".join(com)

    def __quit(self, cmd):
        os._exit(0)

    def __input(self, cmd):
        u = self.droid.dialogGetInput('Qpy CMD', "Input command:").result
        if u is not None:
            print("[>]: " + u.strip())
            return self.__shell(u)
        else:
            return False

    def api(self, cmd, print_out=True):
        cmd = self.__shell(str(cmd))
        if isinstance(cmd, str):
            self.__cmdIn(cmd, output=print_out)

    def mainloop(self):
        print(
            'Welcome to QPy CMD ' +
            self.__version__ +
            ' by guangrei, type "exit" to close this program and "?" for help!')
        self.set_command("update", self.__update)
        self.set_normalizer("python", self.__python)
        self.set_normalizer("pip", self.__pip)
        self.set_normalizer("pydoc", self.__pydoc)
        self.set_command("ext", self.__ext.CMD)
        self.set_command("exit", self.__quit)
        self.set_command("x", self.__input)
        self.set_command("dump_path", self.__dump_path)
        self.set_normalizer("easy_install", self.__easy_install)
        self.set_command("?", self.__help)
        self.set_command("cd", self.__cd)
        while True:
            try:
                i = input("[>]: ")
                i = self.__shell(i)
                if isinstance(i, str):
                    self.__cmdIn(i)
            except KeyboardInterrupt:
                print('please type "exit" for quit!')


if __name__ == "__main__":
    q = QPyCMD()
    q.mainloop()
