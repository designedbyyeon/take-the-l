#!/usr/bin/env python3
"""audio.mp4, assets/logo.svg, assets/hand-sm.webp를 takethel.js 안에 내장하고, index.html 로고도 갱신한다. macOS afconvert 필요.

    python3 build.py [음원 파일=audio.mp4] [비트레이트=56000]
"""
import base64, os, re, subprocess, sys, tempfile, zipfile

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'audio.mp4'))
bitrate = sys.argv[2] if len(sys.argv) > 2 else '56000'

with tempfile.TemporaryDirectory() as tmp:
    wav, m4a = os.path.join(tmp, 'mono.wav'), os.path.join(tmp, 'out.m4a')
    subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16', '-c', '1', '--mix', src, wav], check=True)
    subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', bitrate, wav, m4a], check=True)
    audio = base64.b64encode(open(m4a, 'rb').read()).decode()

logo = open(os.path.join(here, 'assets', 'logo.svg'), encoding='utf-8').read().strip().replace("'", '"')
hand = base64.b64encode(open(os.path.join(here, 'assets', 'hand-sm.webp'), 'rb').read()).decode()

js = os.path.join(here, 'takethel.js')
code = open(js, encoding='utf-8').read()
for name, value in (('AUDIO_B64', audio), ('LOGO_SVG', logo), ('HAND_B64', hand)):
    code, n = re.subn(r"var %s = '[^']*';" % name, lambda _: "var %s = '%s';" % (name, value), code)
    if n != 1:
        sys.exit('takethel.js에서 %s 줄을 찾지 못했어요' % name)
open(js, 'w', encoding='utf-8').write(code)
# 설치 페이지 히어로 로고도 같은 logo.svg로 갱신
page = os.path.join(here, 'index.html')
html = open(page, encoding='utf-8').read()
hero = logo.replace('<svg ', '<svg class="logo" ', 1)
html, n = re.subn(r'<!--logo-->.*?<!--/logo-->', lambda _: '<!--logo-->' + hero + '<!--/logo-->', html, flags=re.S)
if n == 1:
    open(page, 'w', encoding='utf-8').write(html)

# 크롬 확장 배포용 zip (설치 페이지에서 내려받는다)
with zipfile.ZipFile(os.path.join(here, 'take-the-l-extension.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for f in ['manifest.json', 'background.js', 'takethel.js'] + ['assets/icon-%d.png' % n for n in (16, 32, 48, 128)]:
        z.write(os.path.join(here, f), os.path.join('take-the-l', f))

print('audio %d KB, logo %d B, hand %d KB → takethel.js' % (len(audio) // 1024, len(logo), len(hand) // 1024))
