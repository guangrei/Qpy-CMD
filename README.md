Qpy CMD is terminal helper for qpython user to run terminal operation like:
- execute python script directly (e.g:  `python path/to/script.py arg1 arg2` )
- run  `pip` command.
- run installed package binary ( `pycodestyle` ,  `autopep8` ,  `mypy`  etc)
- run basic command ( `ls` ,  `mkdir` ,  `cd`  etc)
- auto  `cd`  to  `/sdcard/qpython` when launched.

special input:
 -  `x` : prompt gui input.
 -  `cmd2`: native terminal launcher.
 -  `?`: show help.
 -  `exit`: terminate program.
 -  `update`: self-update program.

![Screenshot](screenshot.jpg)

## Extend

you extend  `cmd.py`  and add your own command, e.g:  `mycmd.py` 
```python
from cmd import QPyCMD

def bar(cmd):
    print("[<]: "+cmd[0]+" bar")
    return False
q = QPyCMD()
q.setCom("foo",bar)
q.mainLoop()
```

## Limitation

currently Qpy CMD not compatible with interactive shell programs and some commands like `echo` ,  `cat` ,  `&&`  doesn't work properly, so you can switch to native terminal by type: `cmd2`.