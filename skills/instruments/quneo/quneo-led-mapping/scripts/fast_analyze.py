#!/usr/bin/env python3
"""Fast video analysis for QuNeo LED sweeps — preset-agnostic.

Usage:
  fast_analyze.py --preset 4                    # /tmp/sweep_preset4.mkv etc.
  fast_analyze.py --preset 4 --workdir /tmp     # explicit workdir
  fast_analyze.py --preset 5 --fps 10           # override fps if recording changed

Reads:  <workdir>/sweep_preset<N>.mkv     (recorded by led_sweep.py)
        <workdir>/events_preset<N>.json   (event log from led_sweep.py)
Writes: <workdir>/analysis_preset<N>.json (observed lit events)

Pipeline: one-pass ffmpeg frame extraction (per-frame select= is ~10x too slow)
-> per-event blob diff vs baseline -> classify blobs by calibrated regions ->
print expected-vs-observed comparison against QuNeo.json for slot N.
"""
import sys,os,json,subprocess,argparse
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import led_sweep as L

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--preset',type=int,required=True)
    ap.add_argument('--workdir',default='/tmp')
    ap.add_argument('--fps',type=int,default=10)
    a=ap.parse_args()
    FPS=a.fps
    VID=os.path.join(a.workdir,'sweep_preset%d.mkv'%a.preset)
    EV =os.path.join(a.workdir,'events_preset%d.json'%a.preset)
    OUT=os.path.join(a.workdir,'analysis_preset%d.json'%a.preset)
    for p in (VID,EV):
        if not os.path.exists(p):
            sys.exit('missing input: %s'%p)

    # 1) extract ALL frames once (one ffmpeg pass)
    FRDIR=os.path.join(a.workdir,'frames_preset%d'%a.preset)
    os.makedirs(FRDIR,exist_ok=True)
    for f in os.listdir(FRDIR): os.remove(os.path.join(FRDIR,f))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',VID,
        '-vf','fps=%d'%FPS,os.path.join(FRDIR,'%06d.png')],check=True,timeout=900)
    idx={int(f[:6])-1:f for f in os.listdir(FRDIR)}
    print('frames:',len(idx))

    import numpy as np
    from PIL import Image
    from scipy import ndimage

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

    cache={}
    def get(n):
        if n in idx and n not in cache:
            cache.clear()
            cache[n]=np.array(Image.open(os.path.join(FRDIR,idx[n])).convert('RGB')).astype(int)
        return cache.get(n)

    d=json.load(open(EV))
    report=[]
    for ev in d['events']:
        nb=int(max(ev['t_on']-0.2,0)*FPS); nm=int((ev['t_on']+ev['t_off'])/2*FPS)
        b=get(nb); m=get(nm)
        if b is None or m is None: continue
        bs=blobs(b,m)
        if bs: report.append(dict(event=ev['label'],blobs=bs))
    json.dump(report,open(OUT,'w'),indent=1)
    print('lit events:',len(report),'->',OUT)

    name,cs=L.load_preset_json(a.preset)
    print('comparing against Preset %d: %s'%(a.preset,name))
    exp=L.expected_map(cs)
    L.compare(exp,report)
    print('DONE')

if __name__=='__main__':
    main()
