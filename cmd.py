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
import sys
import os
import shlex
from urllib import parse


class QPyCMD(object):
    def __init__(self):
        self.__version__ = "v1.0"
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

    def set_command(self, fun_name, fun):
        if callable(fun):
            self.commander[fun_name] = fun
        else:
            raise Exception(type(fun) + " isn't callable")

    def __check_update(self):
        print("[<]: checking for update")
        try:
            import requests
            tx = requests.get(
                "https://raw.githubusercontent.com/guangrei/Qpy-CMD/main/version.txt",
                verify=False).text
            if tx != self.__version__:
                return True
            else:
                print("you already use version " + tx)
                return False
        except BaseException:
            print("failed to checks update!")
            return False

    def __update(self, cmd):
        if(self.__check_update()):
            print("updating..")
            path = os.path.dirname(sys.argv[0]) + "/cmd.py"
            try:
                import requests
                tx = requests.get(
                    "https://raw.githubusercontent.com/guangrei/Qpy-CMD/main/cmd.py").text
                with open(path, "w") as f:
                    f.write(tx)
                    f.close()
                    print("update completed! please re-run " + path)
            except BaseException:
                print("update failed!")
        return False

    def __cmd2(self, cmd):
        print("###\nWelcome to second Qpy CMD, this is just native terminal! type \"exit\" for back to QPy CMD.\npython bin: " +
              sys.executable.split("/")[-1] + "\n###")
        os.system("sh")
        return False

    def __shell(self, txcmd):
        cmd = shlex.split(txcmd)
        if txcmd.strip() == "":
            return False
        elif (txcmd.strip() in ["python", "sh", "ipython", "bash", "python3", "python2"]):
            print(
                "don't run interactive shell programs here, please type: \"cmd2\" to open native terminal!")
            return False
        elif (cmd[0] in ["vim", "vi", "nano", "cat", "echo", "ssh"]):
            print(
                cmd[0] +
                " isn't compatible here, please type: \"cmd2\" to open native terminal!")
            return False
        elif ("&&" in cmd):
            print(
                "command && isn't compatible here, please type: \"cmd2\" to open native terminal!")
            return False
        elif cmd[0] in self.commander:
            return self.commander[cmd[0]](cmd)
        else:
            return txcmd

    def __cmdIn(self, com):
        txcmd = 'cmd="' + com + '"; $cmd; echo "<#eol#>"\n'
        self.process.stdin.write(txcmd)
        self.process.stdin.flush()
        self.__cmdOut()

    def __cmdOut(self):
        for out in self.process.stdout:
            if out != "<#eol#>\n":
                print("[<]:", out.strip())
            else:
                break

    def __python(self, cmd):
        cmd[0] = sys.executable
        return " ".join(cmd)

    def __urlencode(self, cmd):
        try:
            print("[<]: " + parse.quote_plus(cmd[1]))
        except IndexError:
            print("Usage: urlencode string")

    def __urldecode(self, cmd):
        try:
            print("[<]: " + parse.unquote(cmd[1]))
        except IndexError:
            print("Usage: urldecode string")

    def __help(self, cmd):
        print("QPy CMD " + self.__version__ + " by guangrei.")
        print("For more info and support please open https://github.com/guangrei/Qpy-CMD")
        return False

    def __pip(self, com):
        com[0] = sys.executable + " -m pip"
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

    def mainloop(self):
        print(
            'Welcome to QPy CMD ' +
            self.__version__ +
            ' by guangrei, type "exit" to close this program and "?" for help!')
        self.set_command("update", self.__update)
        self.set_command("python", self.__python)
        self.set_command("pip", self.__pip)
        self.set_command("pydoc", self.__pydoc)
        self.set_command("cmd2", self.__cmd2)
        self.set_command("exit", self.__quit)
        self.set_command("x", self.__input)
        self.set_command("urlencode", self.__urlencode)
        self.set_command("urldecode", self.__urldecode)
        self.set_command("?", self.__help)
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
