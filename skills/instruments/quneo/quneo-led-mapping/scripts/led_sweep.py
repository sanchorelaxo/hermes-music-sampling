#!/usr/bin/env python3
"""QuNeo LED mapper — JSON-driven, preset-agnostic.

Usage:
  led_sweep.py --preset 4              # sweep preset slot 4 (must be active on device)
  led_sweep.py --preset 4 --sweep-only # skip JSON expectations, raw sweep
  led_sweep.py --expected-only --preset 4   # just print the JSON-derived map

Pipeline:
  1. Ingest Content/Presets/QuNeo.json -> extract expected LED map for slot N
     (pad corner notes + padChannel, button outNotes + channels, slider CCs).
  2. Record webcam video while sweeping notes 0-127 and CCs 0-31 on ch 0-2
     (configurable range), clearing state between events.
  3. Whole-frame diff analysis per event -> lit blobs, classified by color.
  4. Map blob centroids to physical components (calibrated grid regions).
  5. Compare observed vs expected, print report + JSON artifacts.
"""
import os,time,subprocess,json,argparse,sys

QUENO_JSON=os.path.expanduser('~/Documents/git/quneo-qt6-editor/Content/Presets/QuNeo.json')
MIDI='/dev/snd/midiC1D0'
# 540p calibrated regions (video is scaled to 960x540)
COLS=[(362,437),(457,535),(557,636),(658,737)]
ROWS=[(36,104),(121,193),(212,287),(307,384)]
# non-pad regions: left column zones (540p) — coarse zones, refined empirically
BUTTON_ZONES={
  'transport':  (330,470, 30,110),   # x0,x1,y0,y1
  'updown':     (330,470,140,240),
  'rhombus':    (330,470,250,330),
  'vsliders':   (60,200,  40,470),
  'rotaries':   (230,320, 60,430),
  'hsliders':   (400,700, 390,470),
  'longslider': (400,700, 470,540),
}

def load_preset_json(slot):
    d=json.load(open(QUENO_JSON))['QuNeo Presets']['Preset %d'%slot]
    return d['presetName'], d['ComponentSettings']

def expected_map(cs):
    """Derive LED-relevant expectations from ComponentSettings."""
    exp={}
    pads=cs['Pads']
    chan=pads['Pad0']['padChannel']
    for n in range(16):
        p=pads['Pad%d'%n]
        for corner in ('SW','SE','NW','NE'):
            note=p['outGmNote%s'%corner]
            if note>=0:
                exp.setdefault('pad%d'%(n+1),{})[corner]=dict(ch=chan,note=note)
        if p.get('outDmNote',-1)>=0:
            exp.setdefault('pad%d'%(n+1),{})['drum']=dict(ch=pads.get('padDrumInChannel',0),note=p['outDmNote'])
    # buttons: outNote drives LED (per official protocol: note on = LED)
    for comp,elems,pat in [
        ('TransportButtons',3,'transportOutNote'),
        ('UpDownButtons',2,'updownUOutNote'),
        ('UpDownButtons',2,'updownDOutNote'),
        ('LeftRightButtons',4,'leftrightLOutNote'),
        ('LeftRightButtons',4,'leftrightROutNote'),
        ('RhombusButtons',1,'rhombusOutNote'),
    ]:
        for i in range(elems):
            e=cs[comp]['%s%d'%(comp[:-1],i)]
            chkey=[k for k in e if k.endswith('Channel')]
            ch=e[chkey[0]] if chkey else 0
            note=e.get(pat,-1)
            if note>=0:
                exp.setdefault(comp.lower(),{})['%s%d'%(pat,i)]=dict(ch=ch,note=note)
    # sliders/rotaries: outLocation CC drives LED position
    for comp,elem,loc in [('Rotaries','Rotary0','rB1outLocation'),
                          ('HSliders','HSlider0','hB1outLocation'),
                          ('VSliders','VSlider0','vB1outLocation'),
                          ('LongSliders','LongSlider0','lB1outLocation')]:
        base=cs[comp]
        for k in sorted(base):
            if not isinstance(base[k],dict): continue
            for b in ('1','2','3','4'):
                cc=base[k].get('%s%s'%(loc[:-9]+'outLocation',b), base[k].get(loc,-1))
                # field names: rB1outLocation etc
                f='%s%s'%(loc[:3],b)+loc[3:]  # e.g. rB1outLocation
                cc=base[k].get(f,-1)
                if cc and cc>=0:
                    exp.setdefault(comp.lower(),{})['%s_%s'%(k,b)]=dict(ch=base[k].get(loc[:3]+b+'Channel',0),cc=cc)
    return exp

def midi(*b):
    fd=os.open(MIDI,os.O_WRONLY|os.O_NONBLOCK); os.write(fd,bytes(b)); os.close(fd)

def clear(maxnote=128,maxcc=32):
    for ch in range(3):
        for n in range(maxnote): midi(0x90|ch,n,0)
        for c in range(maxcc):  midi(0xB0|ch,c,0)

def run_sweep(vidpath,events_path,notes=range(128),ccs=range(32),channels=(0,1,2)):
    rec=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','v4l2','-input_format','mjpeg','-framerate','30','-s','1920x1080',
        '-i','/dev/video2','-vf','scale=960:540,fps=10',
        '-c:v','libx264','-preset','ultrafast','-crf','25',vidpath],stderr=subprocess.PIPE)
    time.sleep(1.5); t0=time.time()
    clear(); time.sleep(0.4)
    events=[]
    for ch in channels:
        for n in notes:
            t=time.time(); midi(0x90|ch,n,127); time.sleep(0.45)
            t_off=time.time(); midi(0x90|ch,n,0)
            events.append(dict(label='ch%d_note%d'%(ch,n),ch=ch,kind='note',num=n,t_on=t-t0,t_off=t_off-t0))
            time.sleep(0.15); clear(); time.sleep(0.1)
        for c in ccs:
            t=time.time(); midi(0xB0|ch,c,127); time.sleep(0.45)
            t_off=time.time(); midi(0xB0|ch,c,0)
            events.append(dict(label='ch%d_cc%d'%(ch,c),ch=ch,kind='cc',num=c,t_on=t-t0,t_off=t_off-t0))
            time.sleep(0.15); clear(); time.sleep(0.1)
    clear(); time.sleep(0.5)
    rec.terminate(); rec.wait()
    with open(events_path,'w') as f: json.dump(dict(events=events),f)
    return len(events)

def analyze(vidpath,events_path,out_path,fps=10):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    def frame_at(t):
        n=int(t*fps); p='/tmp/qs_fr.png'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',vidpath,
            '-vf','select=eq(n\\,%d)'%n,'-frames:v','1','-y',p],capture_output=True)
        if not os.path.exists(p): return None
        im=np.array(Image.open(p).convert('RGB')).astype(int); os.remove(p); return im
    def blobs(base,dur):
        diff=dur-base
        m=diff.max(axis=2)>60
        if m.sum()<40: return []
        lab,n=ndimage.label(m); out=[]
        for i in range(1,n+1):
            ys,xs=np.where(lab==i)
            if len(xs)<40: continue
            cell=diff[ys,xs]
            grn=((cell[:,1]>cell[:,0]+20)*(cell[:,1]>cell[:,2]+20)).sum()
            red=((cell[:,0]>cell[:,1]+25)*(cell[:,0]>cell[:,2]+25)).sum()
            org=((cell[:,0]>cell[:,1]+10)*(cell[:,1]>cell[:,2]+15)).sum()
            col='green' if grn>=max(red,org) else ('red' if red>=org else 'orange')
            out.append(dict(x=int(xs.mean()),y=int(ys.mean()),px=int(len(xs)),color=col))
        return out
    d=json.load(open(events_path)); report=[]
    for ev in d['events']:
        tb=frame_at(max(ev['t_on']-0.2,0)); tm=frame_at((ev['t_on']+ev['t_off'])/2)
        if tb is None or tm is None: continue
        bs=blobs(tb,tm)
        if bs: report.append(dict(event=ev['label'],blobs=bs))
    json.dump(report,open(out_path,'w'),indent=1)
    return report

def classify(blob):
    x,y=blob['x'],blob['y']
    for r,(y0,y1) in enumerate(ROWS):
        if y0<=y<=y1:
            for c,(x0,x1) in enumerate(COLS):
                if x0<=x<=x1:
                    return 'pad%d'%((3-r)*4+c+1)
    for name,(x0,x1,y0,y1) in BUTTON_ZONES.items():
        if x0<=x<=x1 and y0<=y<=y1: return name
    return None

def compare(exp,observed):
    print('\n=== EXPECTED (from QuNeo.json) vs OBSERVED (video) ===')
    for comp,entries in sorted(exp.items()):
        for k,v in entries.items():
            key='ch%d_%s%d'%(v['ch'],v.get('note') is not None and 'note' or 'cc',v.get('note',v.get('cc')))
            hits=[b for ev in observed if ev['event']==key for b in ev['blobs']]
            named=[classify(b) for b in hits]
            named=[n for n in named if n]
            status='MATCH' if comp in named else ('near' if any(comp[:4] in str(n) for n in named) else 'MISS')
            print('%-18s %-14s %-28s -> %s %s'%(comp,k,key,sorted(set(named)) or '-',status))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--preset',type=int,required=True)
    ap.add_argument('--sweep-only',action='store_true')
    ap.add_argument('--expected-only',action='store_true')
    ap.add_argument('--workdir',default='/tmp')
    a=ap.parse_args()
    name,cs=load_preset_json(a.preset)
    print('Preset %d: %s'%(a.preset,name))
    exp=expected_map(cs)
    if a.expected_only:
        print(json.dumps(exp,indent=1)); return
    w=a.workdir
    vid=os.path.join(w,'sweep_preset%d.mkv'%a.preset)
    ev=os.path.join(w,'events_preset%d.json'%a.preset)
    out=os.path.join(w,'analysis_preset%d.json'%a.preset)
    n=run_sweep(vid,ev)
    print('swept %d events, video %s (%d bytes)'%(n,vid,os.path.getsize(vid)))
    observed=analyze(vid,ev,out)
    print('observed %d lit events -> %s'%(len(observed),out))
    if not a.sweep_only:
        compare(exp,observed)

if __name__=='__main__':
    main()
