# -*-coding:utf8;-*-
"""
The MIT License (MIT)

Copyright (c) 2021 sl4awrapper https://github.com/guangrei

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
from androidhelper import Android

native = Android()


def paste():
    return native.getClipboard().result


def copy(msg):
    ret = native.setClipboard(msg)
    native.makeToast('copied!')
    return ret


def toast(msg):
    return native.makeToast(msg)


def notify(title, msg):
    return native.notify(title, msg)


def alert(title, msg, button=('ok',), default=False):
    native.dialogCreateAlert(title, msg)
    bt = (native.dialogSetPositiveButtonText,
          native.dialogSetNegativeButtonText, native.dialogSetNeutralButtonText)
    alias = {'positive': 0, 'negative': 1, 'neutral': 2}
    for k, v in enumerate(button):
        bt[k](v)
    native.dialogShow()
    response = native.dialogGetResponse().result
    if 'which' in response:
        return button[alias[response['which']]]
    else:
        return default


def sprogress_show(title, msg):
    native.dialogCreateSpinnerProgress(title, msg)
    native.dialogShow()


def sprogress_hide():
    native.dialogDismiss()


def hprogress_show(title, msg, amount):
    native.dialogCreateHorizontalProgress(title, msg, amount)
    native.dialogShow()


def hprogress_update(num):
    native.dialogSetCurrentProgress(num)


def hprogress_hide():
    native.dialogDismiss()


def menu(title, item, default=False):
    native.dialogCreateAlert(title)
    native.dialogSetItems(item)
    native.dialogShow()
    result = native.dialogGetResponse().result
    if 'item' not in result:
        return default
    else:
        return result['item']


def checklist(title, item, bt='ok'):
    native.dialogCreateAlert(title)
    native.dialogSetSingleChoiceItems(item)
    native.dialogSetPositiveButtonText(bt)
    native.dialogShow()
    response = native.dialogGetResponse().result
    return response


def multi_checklist(title, item, bt='ok'):
    native.dialogCreateAlert(title)
    native.dialogSetMultiChoiceItems(item, [])
    native.dialogSetPositiveButtonText(bt)
    native.dialogShow()
    response = native.dialogGetResponse().result
    return response


def input(title, msg, default=False):
    text = native.dialogGetInput(str(title), str(msg)).result
    if text is not None:
        return text
    else:
        return default


def vibrate(ms=200):
    return native.vibrate(ms)


def warn(title, msg):
    res = alert(title, msg, ('close', 'speak', 'copy'))
    if res == 'copy':
        copy(msg)
    elif res == 'speak':
        speak(msg)
    else:
        pass


def speak(msg):
    native.ttsSpeak(msg)


def camera(path, mode="picture"):
    if mode == "picture":
        ret = native.cameraInteractiveCapturePicture(path)
    else:
        ret = native.startInteractiveVideoRecording(path)
    if ret.error is None:
        return path
    else:
        return False


def view(p):
    import mimetypes
    return native.view('file://'+p, mimetypes.guess_type(p)[0])


def browser(url):
    return native.view(url)


def audio_record(path, times=5):
    import time
    native.recorderStartMicrophone(path)
    sprogress_show("Recording Audio", path)
    time.sleep(times)
    sprogress_hide()
    native.recorderStop()
    alert("Recording Audio", "recording has been stopped and completed!")
    return path


def video_record(path, times=5):
    native.recorderStartVideo(path, videoSize=4, duration=times)
    native.recorderStop()
    alert("Recording Video", "recording has been stopped and completed!")
    return path


def edit(uri, mime='guess'):
	if mime == 'guess':
		import mimetypes
	
		r = native.startActivityForResult('android.intent.action.EDIT', 'file://'+uri, mimetypes.guess_type(uri)[0])
	else:
		r = native.startActivityForResult('android.intent.action.EDIT', 'file://'+uri, mime)
	return r


def listen(msg="please speak now!", lang="en-Us", model=None):
    while True:
        ret = native.recognizeSpeech(msg, lang, model)
        if ret.result != None:
            break
        else:
            pass
    return ret.result


def speaking(word):
    native.ttsSpeak(word)
    sprogress_show("Speaking", word)
    while native.ttsIsSpeaking().result:
        pass
    sprogress_hide()


def pick(mime='*/*'):
    p = native.startActivityForResult(
        'android.intent.action.GET_CONTENT', None, mime, None)
    if p.result:
        return p.result['data']
    else:
        return False
