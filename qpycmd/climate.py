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
import os

logo = """

   ___  ___       ___ __  __ ___  
  / _ \| _ \_  _ / __|  \/  |   \ 
 | (_) |  _/ || | (__| |\/| | |) |
  \__\_\_|  \_, |\___|_|  |_|___/ 
            |__/                  

"""
shtemp_old = """#!/system/bin/sh

DIR=${0%/*}
if [ $# -eq 0 ]; then
    . $DIR/init.sh && $DIR/python $DIR/qcmd && $DIR/end.sh
    exit 0 
fi
. $DIR/init.sh && $DIR/python "$@" && $DIR/end.sh
"""

shtemp_new = """#!/system/bin/sh
DIR=${0%/*}
    
if [ -z "$1" ]; then

    . $DIR/init.sh && $DIR/qcmd && $DIR/bend.sh

else

    is_web=`grep "#qpy:webapp" $1`
    is_qapp1=`grep "#qpy:qpyapp" $1`
    is_qapp2=`grep "#qpy:qpysrv" $1`

    if [ -z "${is_web}" ]  && [ -z "${is_qapp1}" ] && [ -z "${is_qapp2}" ]; then

        . $DIR/init.sh && $DIR/python3-android5 "$@" && $DIR/bend.sh

    else

        . $DIR/init.sh && $DIR/python3-android5 "$@" && $DIR/send.sh

    fi

fi
"""

class Styled(object):
    
    ansicode = {'okblue': '\x1b[94m', 'okgreen': '\x1b[92m', 'bold': '\x1b[1m', 'header': '\x1b[95m',  'warning': '\x1b[93m', 'okcyan': '\x1b[96m', 'fail': '\x1b[91m', 'underline': '\x1b[4m'}
    ansiclose = '\x1b[0m'
    
    def __init__(self,text):
        self.text = str(text);
        self.ls = []
        
    def out(self):
        ret = self.text
        for i in self.ls:
            ret = "{0}{1}{2}".format(self.ansicode[i],ret, self.ansiclose)
        return ret
    def __str__(self):
        ret = self.text
        for i in self.ls:
            ret = "{0}{1}{2}".format(self.ansicode[i],ret, self.ansiclose)
        return ret
    
    def __getattr__(self, name):
        if name in self.ansicode:
            self.ls.append(name)
        return self

def get_contents(url,encoding="utf-8", device="pc"):
    ua_mobile = "Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.61 Mobile Safari/537.36"
    ua_pc = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    if device == "mobile":
        UA = ua_mobile
    else:
        UA = ua_pc
    try:
        import ssl
        import urllib.request
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url) as response:
            if encoding is not None:
                return response.read().decode(encoding)
            else:
                return response.read()
    except:
        try:
            import requests
            headers = requests.utils.default_headers()
            headers.update({'User-Agent': UA})
            
            response = requests.get(url, headers=headers)
            if encoding is not None:
                return response.text
            else:
                return response.content
        except:
            return False

class Qpyutil(object):
    
    def is_qpy():
        return os.getenv("IS_QPY3") is not None
        
    def is_old_qpy():
        if Qpyutil.is_qpy():
            file = os.getenv("PYTHONHOME")+"/bin/qpython.sh"
            with open(file, "r") as f:
                f = f.read()
            test = "only android" in f.lower()
            return not test
        else:
            raise ValueError
        
    def qpy_version():
        if Qpyutil.is_qpy():
            return [2,3][int(os.getenv("IS_QPY3")) == 1]
        else:
            raise ValueError
            
    def update_terminal():
        if Qpyutil.is_old_qpy:
           file = os.getenv("PYTHONHOME")+"/bin/qpython.sh"
           print("updating",file,"..")
           with open(file, "w") as f:
               f.write(shtemp_old)
           print("sucess updating",file)
           os.system("chmod 755 {}".format(file))
           os.system("chmod 755 {}".format(os.getenv("PYTHONHOME")+"/bin/qcmd"))
        else:
           file = os.getenv("PYTHONHOME")+"/bin/qpython3-android5.sh" 
           print("updating",file,"..")
           with open(file, "w") as f:
               f.write(shtemp_old)
           print("sucess updating",file)
           os.system("chmod 755 {}".format(file))
           os.system("chmod 755 {}".format(os.getenv("PYTHONHOME")+"/bin/qcmd"))