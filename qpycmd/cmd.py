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
from subprocess import Popen, PIPE, call, STDOUT
import sys
import os
import shlex
import json
import shutil
from .climate import logo, get_contents, Styled
from .extension import Extension
import qpycmd
import re


class QPyCMD(object):
    def __init__(self):
        self.__version__ = qpycmd.__version__
        self.last_output = ""
        self.__ext = Extension()
        self.process = Popen(
            ['sh'],
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
            bufsize=0)
        if os.getenv("QCWD") is not None:
            self.process.stdin.write('cd {}\n'.format(os.getenv("QCWD")))
            self.process.stdin.flush()
        elif "qpython" in os.environ["PATH"]:
            self.process.stdin.write('cd /sdcard/qpython/\n')
            self.process.stdin.flush()
        else:
            home = os.path.abspath(os.path.dirname(sys.argv[0]))
            self.process.stdin.write('cd '+home+'\n')
            self.process.stdin.flush()
        self.commander = {}
        self.normalizer = {}

    def get_bin(self):
        ls = []
        m = dict(self.commander, **self.normalizer)
        for k, v in m.items():
            if k != "cd":
                ls.append(k)
        return ls+self.__ext.get_bin()

    def __dump_path(self, cmd):
        print("QPyCMD executable:")
        print("-"*len("QPyCMD executable:"))
        for i in self.get_bin():
            print("[<]:", i)
        sy = os.environ["PATH"].split(":")
        for i in sy:
            print("\n%s executable:" % i)
            print("-"*len(i+" executable:"))
            for j in os.listdir(i):
                print("[<]:", j)
                pr = Styled("CAUTION!!")
        print("\n{}".format(pr.bold.warning.out()))
        print("-"*len("CAUTION!!"))
        print(
            "\n"+Styled.ansicode["bold"]+"* some executable may not compatible in QpyCMD, so you can run it in sh."+Styled.ansiclose)
        print(Styled.ansicode["bold"] +
              "** some executable may need root permission"+Styled.ansiclose)
        print(Styled.ansicode["bold"] +
              "*** some executable could make your device crashed, so make sure you know what you do!"+Styled.ansiclose)

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
            "https://raw.githubusercontent.com/guangrei/QPy-CMD/main/setup.py")
        if rs != False:
            search = re.search('version="(.*)"', rs)
            if search.group(1).strip() != self.__version__:
                return True
            else:
                print("you already use version " + search.group(1))
                return False
        else:
            print(Styled.ansicode["fail"] +
                  "failed to checks update!"+Styled.ansiclose)
            return False

    def __update(self, cmd, upath=None):
        if(self.__check_update()):
            print("updating..")
            self.__shell(
                "pip install https://github.com/guangrei/Qpy-CMD/archive/main.zip --upgrade")

    def __shell(self, txcmd):
        cmd = shlex.split(txcmd)
        if txcmd.strip() == "" or txcmd in [".", "..", "qcmd"]:
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
                com = [txcmd]
            if os.path.isdir(self.last_output):
                call(com, cwd=self.last_output, shell=True)
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
                    reg = "<stdin>\[\d\]\:\s"
                    outp = out.strip()
                    if re.search(reg, outp):
                        print(Styled.ansicode['fail'] +
                              re.sub(reg, "", outp)+Styled.ansiclose)
                    else:
                        print(outp)
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
        com = " ".join(com)
        self.__cmdIn('pwd', output=False)
        com = "cd {0} && {1}".format(self.last_output, com)
        os.system(com)

    def __nohup(self, com):
        del com[0]
        if len(com) == 0:
            print("Usage:\n------")
            print("- nohup [ext-name] [args: optional]")
            print("- nohup kill [pid]")
            print("- nohup list")
        else:
            if self.__ext.is_exists(com[0]):
                self.__cmdIn('pwd', output=False)
                if os.path.isdir(self.last_output):
                    self.__ext.bg_run(self.last_output, com)
            elif com[0] == "list":
                print("-"*24)
                print("|No  | pid   | program |")
                print("-"*24)
                n = 1
                for k, v in self.__ext.process_list.items():
                    print(" {0}.    {1}   {2}".format(n, k, v["program"]))
                    n = n+1
            elif com[0] == "kill":
                if len(com) == 2:
                    pd = int(com[1])
                    if pd in self.__ext.process_list:
                        p = self.__ext.process_list[pd]["obj"]
                        if p.poll() is None:
                            p.kill()
                            del self.__ext.process_list[pd]
                            print("success!")
                        else:
                            del self.__ext.process_list[pd]
                            print("* success!")
                    else:
                        print("no process with pid: %d!" % pd)
                else:
                    print("Usage: nohup kill [pid]")
            else:
                print("ext %s isn't installed!" % com[0])

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
        import androidhelper
        droid = androidhelper.Android()
        u = droid.dialogGetInput('Qpy CMD', "Input command:").result
        if u is not None:
            print("[>]: " + u.strip())
            return self.__shell(u)
        else:
            return False

    def api(self, cmd, print_out=True):
        cmd = self.__shell(str(cmd))
        if isinstance(cmd, str):
            self.__cmdIn(cmd, output=print_out)

    def mainloop(self, cmd_name="QPyCMD"):
        pr = Styled(logo)
        pr = pr.header.out()
        print(pr)
        pr = Styled('Welcome to  ' + cmd_name + ' ' +
                    self.__version__ +
                    ' by guangrei, type "exit" to close this program and "?" for help!')
        print(pr.okgreen.bold.out())
        self.set_command("update", self.__update)
        self.set_normalizer("python", self.__python)
        self.set_normalizer("py", self.__python)
        self.set_command("pip", self.__pip)
        self.set_normalizer("pydoc", self.__pydoc)
        self.set_command("ext", self.__ext.CMD)
        self.set_command("exit", self.__quit)
        self.set_command("x", self.__input)
        self.set_command("dump_path", self.__dump_path)
        self.set_normalizer("easy_install", self.__easy_install)
        self.set_command("?", self.__help)
        self.set_command("cd", self.__cd)
        self.set_command("nohup", self.__nohup)
        while True:
            i = input("[>]: ")
            i = self.__shell(i)
            if isinstance(i, str):
                self.__cmdIn(i)


if __name__ == "__main__":
    pass
