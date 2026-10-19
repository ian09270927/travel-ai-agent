"""Local, reproducible still-motion travel advertisement. No provider credentials."""
from pathlib import Path
import json, math, shutil, subprocess, wave
import numpy as np

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parent
ASSETS = VIDEO / 'assets_v1'
FINAL = VIDEO / 'final'
FINAL.mkdir(exist_ok=True)
FFMPEG = shutil.which('ffmpeg')
FFPROBE = shutil.which('ffprobe')
if not FFMPEG or not FFPROBE:
    raise RuntimeError('FFmpeg and ffprobe must be available')

def run(args, log_name):
    print('Running:', log_name, flush=True)
    result = subprocess.run([str(x) for x in args], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (HERE / log_name).write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{log_name}: {result.stderr.decode("utf8", "replace")[-2200:]}')

def probe(path):
    return json.loads(subprocess.check_output([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(path)]))

def write_wav(path, audio, sr=48000):
    audio=np.clip(audio,-.98,.98)
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((audio*32767).astype('<i2').tobytes())

def music():
    sr=48000;length=30;audio=np.zeros((sr*length,2),dtype=np.float64)
    def add_note(midi,start,duration,gain,pan=0,kind='piano'):
        a=int(start*sr);n=min(int(duration*sr),len(audio)-a)
        if n<=0:return
        t=np.arange(n)/sr;freq=440*2**((midi-69)/12)
        if kind=='piano':
            attack=1-np.exp(-t*65)
            signal=sum(weight*np.sin(2*np.pi*freq*harm*t)*np.exp(-t*(.52+.16*harm)) for harm,weight in [(1,1),(2,.35),(3,.13),(4,.06),(6,.015)])
            signal*=attack
        elif kind=='pluck':
            signal=sum(np.sin(2*np.pi*freq*h*t)/h**1.8*np.exp(-t*(1.6+.4*h)) for h in range(1,6))*(1-np.exp(-t*150))
        else:
            signal=(np.sin(2*np.pi*freq*t)+.20*np.sin(2*np.pi*freq*1.0015*t))
            signal*=np.sin(np.pi*np.minimum(t/duration,1))**1.5*.42
        signal*=np.minimum((duration-t)/.25,1).clip(0,1)*gain
        left=math.sqrt((1-pan)/2);right=math.sqrt((1+pan)/2)
        audio[a:a+n,0]+=signal*left;audio[a:a+n,1]+=signal*right
    chords=[[48,55,60,64,67],[43,55,59,62,67],[45,57,60,64,67],[41,53,57,60,64],
            [48,55,60,64,67],[43,55,59,62,67],[45,57,60,64,67],[41,53,57,60,64],
            [43,55,59,62,67],[48,55,60,64,67]]
    melody=[(0,76),(.75,79),(1.5,74),(2.25,72),(6,76),(6.75,79),(7.5,81),(8.25,79),
            (12,76),(12.75,79),(13.5,74),(14.25,72),(18,76),(18.75,79),(19.5,81),(20.25,79),
            (24,74),(24.75,71),(25.5,67),(27,72),(27.75,76)]
    for bar,chord in enumerate(chords):
        start=bar*3
        add_note(chord[0],start,3.8,.20,-.1)
        for k,note in enumerate(chord[1:]):
            add_note(note,start+k*.07,3.5,.085,(k-1.5)*.22)
            add_note(note,start,4,.035,(k-1.5)*.18,'pad')
        for step in range(8):
            add_note(chord[1+(step%4)]+12,start+step*.375,1.5,.035,(-1)**step*.35,'pluck')
    for start,note in melody:add_note(note,start,2.4,.10,.12)
    # Small fixed stereo reflections, not a borrowed sample or tune.
    dry=audio.copy()
    for delay,gain in [(.083,.10),(.163,.065),(.271,.045)]:
        off=int(delay*sr);audio[off:]+=dry[:-off,::-1]*gain
    peak=np.max(np.abs(audio));audio*=.68/peak
    fade=np.ones(len(audio));fade[:sr]=np.linspace(0,1,sr)
    fade[-int(1.5*sr):]=np.linspace(1,0,int(1.5*sr))
    audio*=fade[:,None]
    write_wav(ASSETS/'original-instrumental.wav',audio)

def ass_time(t):
    c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def subtitles():
    intro='''[Script Info]
Title: 台灣旅行，從喜歡的事開始
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Subtitle,Microsoft JhengHei,52,&H00F8F3E7,&H00FFFFFF,&H00141D17,&H80000000,-1,0,0,0,100,100,1,0,1,2.2,1,2,100,100,135,1
Style: Head,Microsoft JhengHei,92,&H00E7F3F8,&H00FFFFFF,&H700F2016,&H90000000,-1,0,0,0,100,100,3,0,1,1,2,7,0,0,0,1
Style: Label,Microsoft JhengHei,27,&H00E7F3F8,&H00FFFFFF,&H500D1A12,&H00000000,0,0,0,0,100,100,5,0,1,1,0,7,0,0,0,1
Style: Small,Microsoft JhengHei,24,&H00E7F3F8,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1
Style: CTA,Microsoft JhengHei,67,&H00E7F3F8,&H00FFFFFF,&H5014291D,&H90000000,-1,0,0,0,100,100,1,0,1,1,2,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events=[]
    def e(a,b,style,text,layer=1):events.append(f'Dialogue: {layer},{ass_time(a)},{ass_time(b)},{style},,0,0,0,,{text}')
    e(0,30,'Small',r'{\pos(72,26)}AI 生成示意畫面')
    e(0,30,'Small',r'{\an9\pos(1848,26)}TAIWAN TRAVEL')
    e(.7,7.5,'Label',r'{\pos(126,307)\fad(500,500)}01   親子共學')
    e(.9,7.6,'Head',r'{\pos(120,365)\fad(600,600)}一起探索')
    e(10.7,17.8,'Label',r'{\pos(126,307)\fad(500,500)}02   情侶藝文')
    e(10.9,17.9,'Head',r'{\pos(120,365)\fad(600,600)}共享體驗')
    e(20.7,25.5,'Label',r'{\pos(1130,323)\fad(500,400)}03   熟齡慢遊')
    e(20.9,25.7,'Head',r'{\pos(1120,380)\fad(600,500)}依自己的步調')
    e(26.1,30,'Label',r'{\pos(1035,292)\fad(600,200)}TAIWAN JOURNEYS')
    e(26.3,30,'CTA',r'{\pos(1025,345)\fad(650,200)}台灣旅行，\N從喜歡的事開始')
    e(26.6,30,'Label',r'{\pos(1030,555)\fad(600,200)\fsp2}告訴我們日期與偏好')
    # Split at measured pauses in the actual Windows voice, not draft timing.
    caps=[(1.00,2.77,'帶孩子看看自然，'),(2.82,3.98,'讓好奇心，'),(4.04,6.06,'成為旅行的起點。'),
          (10.80,12.20,'和喜歡的人，'),(12.24,14.03,'走進庭園與文化，'),(14.08,15.38,'留一點時間，'),(15.43,16.81,'好好相處。'),
          (20.50,23.45,'陪家人照自己的步調旅行。'),(24.03,26.23,'告訴我們日期與偏好，'),(26.25,28.05,'一起討論安排。')]
    for a,b,t in caps:e(a,b,'Subtitle',r'{\fad(70,70)}'+t,3)
    (VIDEO/'captions_v1.ass').write_text(intro+'\n'.join(events)+'\n',encoding='utf8')
    def srt_time(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (VIDEO/'captions_v1.srt').write_text('\n\n'.join(f'{i+1}\n{srt_time(a)} --> {srt_time(b)}\n{t}' for i,(a,b,t) in enumerate(caps))+'\n',encoding='utf8')
    return caps

def render():
    music();caps=subtitles()
    for i in range(1,4):
        dst=HERE/f'scene-{i:02}.mp4'
        if dst.exists() and float(probe(dst)['format']['duration'])==10:continue
        filt="scale=3840:2160:flags=lanczos,zoompan=z='1.025+0.00024*on':x='(iw-iw/zoom)*0.5':y='(ih-ih/zoom)*0.48':d=240:s=1920x1080:fps=24,setsar=1,format=yuv420p"
        run([FFMPEG,'-hide_banner','-y','-i',ASSETS/f'scene-{i:02}.png','-vf',filt,'-frames:v','240','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','4',dst],f'render-scene-{i:02}.log')
    (HERE/'concat.txt').write_text("\n".join(f"file 'scene-{i:02}.mp4'" for i in range(1,4))+'\n',encoding='ascii')
    run([FFMPEG,'-hide_banner','-y','-f','concat','-safe','0','-i','concat.txt','-c','copy',HERE/'picture.mp4'],'concat.log')
    # TTS processing and exact, separate 10-second segments. Music lightly ducks under speech.
    mix=';'.join([
      '[0:a]highpass=f=95,lowpass=f=10500,volume=1.6,adelay=800|800,apad,atrim=0:30[v1]',
      '[1:a]highpass=f=95,lowpass=f=10500,volume=1.6,adelay=10800|10800,apad,atrim=0:30[v2]',
      '[2:a]highpass=f=95,lowpass=f=10500,volume=1.6,adelay=20500|20500,apad,atrim=0:30[v3]',
      '[v1][v2][v3]amix=inputs=3:normalize=0,asplit=2[voice][side]',
      '[3:a]volume=0.25[music]',
      '[music][side]sidechaincompress=threshold=0.025:ratio=4:attack=20:release=380:makeup=1[ducked]',
      '[voice][ducked]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,atrim=0:30[out]'])
    run([FFMPEG,'-hide_banner','-y','-i',ASSETS/'vo-01.wav','-i',ASSETS/'vo-02.wav','-i',ASSETS/'vo-03.wav','-i',ASSETS/'original-instrumental.wav','-filter_complex',mix,'-map','[out]','-c:a','pcm_s16le',ASSETS/'mix-30s.wav'],'audio-mix.log')
    filters="drawbox=x=0:y=0:w=iw:h=74:color=0x123E32@0.94:t=fill,drawbox=x=0:y=1006:w=iw:h=74:color=0x123E32@0.94:t=fill,drawbox=x=0:y=880:w=iw:h=126:color=black@0.22:t=fill,drawbox=x=990:y=260:w=850:h=400:color=0x123E32@0.66:t=fill:enable='between(t,26,30)',ass=filename='../captions_v1.ass',fade=t=in:st=0:d=0.5,fade=t=out:st=29.65:d=0.35"
    index=1
    while (FINAL/f'taiwan-travel-30s-v{index:02}.mp4').exists():index+=1
    final=FINAL/f'taiwan-travel-30s-v{index:02}.mp4'
    run([FFMPEG,'-hide_banner','-n','-i',HERE/'picture.mp4','-i',ASSETS/'mix-30s.wav','-vf',filters,'-map','0:v:0','-map','1:a:0','-t','30','-frames:v','720','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-r','24','-threads','4','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',final],'final-render.log')
    data=probe(final)
    validation={'final':str(final),'duration':data['format']['duration'],'streams':[{k:s.get(k) for k in ['codec_name','codec_type','width','height','r_frame_rate','nb_frames','sample_rate','channels']} for s in data['streams']], 'voice':'Microsoft Hanhan Desktop - Chinese (Taiwan)', 'technique':'Three AI-generated still images with FFmpeg camera motion; not generated actor movement','music':'Locally synthesized original instrumental from make-film.py','captions':caps,'human_ear_review':'not performed'}
    (HERE/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
    run([FFMPEG,'-hide_banner','-v','error','-i',final,'-f','null','-'],'decode-check.log')
    previews=HERE/'previews';previews.mkdir(exist_ok=True)
    for sec in [2,5,9,12,15,19,22,25,27.5,29]:
        run([FFMPEG,'-hide_banner','-y','-ss',str(sec),'-i',final,'-frames:v','1',previews/f'frame-{sec:04.1f}.png'],f'preview-{sec}.log')
    print(json.dumps(validation,ensure_ascii=False),flush=True)

if __name__=='__main__':render()
