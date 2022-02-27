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
import time
import os
import sys

try:
    import sl4a
except ImportError:
    import androidhelper as sl4a

print('Welcome to Qpython CMD v1.0, type "exit" to close this program and "?" for help!')

droid = sl4a.Android()
process = Popen(
    ['sh'],
    shell=True,
    stdin=PIPE,
    stdout=PIPE,
    universal_newlines=True,
    bufsize=0)
process.stdin.write('cd /sdcard/qpython/\n')
process.stdin.flush()


def dialog_input():
    u = droid.dialogGetInput('Qpy CMD', "Input command:").result
    if u is not None:
        return u.strip()
    else:
        return ""


def dialog_page(uri, title, msg):
    title = title
    message = (msg)
    droid.dialogCreateAlert(title, message)
    droid.dialogSetPositiveButtonText('Yes')
    droid.dialogSetNegativeButtonText('No')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if (response['which'] == 'positive'):
        droid.view(uri)


def output_cmd():
    for out in process.stdout:
        if out != "<#eol#>\n":
            print("[<]:", out.strip())
        else:
            break


def commander(com):
    com = com.split()
    if (com[0] == "python"):  # python
        com[0] = sys.executable
        return " ".join(com)
    elif (com[0] == "pip"):  # pip
        com[0] = sys.executable + " -m pip"
        return " ".join(com)
    elif (com[0] == "pydoc"):  # pydoc
        com[0] = sys.executable + " -m pydoc"
        return " ".join(com)
    else:
        return com


while True:
    i = input("[>]: ")
    i = i.replace("$QPD", "/sdcard/qpython/")  # shortcut for qpython dir
    i = i.replace("$QPS", sys.prefix)  # shortcut for qpypthon sys dir
    if (i == ""):  # handle empty input
        process.stdin.write('echo "<#eol#>"\n')
        process.stdin.flush()
    elif (i == "exit"):  # exit
        os._exit(0)
    elif (i == "cmd2"):  # cmd2
        break
    elif (i == "?"):  # help
        print("For more info and support please open https://github.com/guangrei/Qpy-CMD")
        dialog_page(
            "https://github.com/guangrei/Qpy-CMD",
            "Qpy CMD",
            "do you want to open page https://github.com/guangrei/Qpy-CMD ?")
    # limit interactive shell programs
    elif (i in ["python", "sh", "ipython", "bash", "python3", "python2"]):
        print("don't run interactive shell programs here, please type: \"cmd2\" to open native terminal!")
    elif(i.split()[0] in ["vim", "vi", "nano", "cat", "echo", "ssh"]):  # block unsupported programs
        print(
            i.split()[0] +
            " isn't compatible here, please type: \"cmd2\" to open native terminal!")
    elif ("&&" in i.split()):
        print("command && isn't compatible here, please type: \"cmd2\" to open native terminal!")
    elif(i == "x" or i == "X"):
        i = dialog_input()
        i = commander(i)
        txcmd = 'cmd="' + i + '"; $cmd; echo "<#eol#>"\n'
        process.stdin.write(txcmd)
        process.stdin.flush()
        output_cmd()
    else:
        i = commander(i)
        txcmd = 'cmd="' + i + '"; $cmd; echo "<#eol#>"\n'
        process.stdin.write(txcmd)
        process.stdin.flush()
        output_cmd()

process.stdin.close()
process.wait()


# second Qpy CMD, this program can be launched with type: cmd2

print("Welcome to second Qpy CMD, this is just native terminal!\npython bin: " +
      sys.executable.split("/")[-1])

os.system("sh")
