import soundfile as sf, numpy as np, glob, os, csv, re
from scipy.signal import resample_poly
from config import R, work
OUT=R+"/WIN_Mandarin"
SR=44100; LEAD=1.36; TAIL=1.58; BAB_DBFS=-37.1; FADE=0.005
LADDER=[12,9,6,3,0,-3,-6]   # dB S/B, 5 words per level (WIN structure)
rng=np.random.default_rng(20261117)
def rms(v): return np.sqrt(np.mean(v**2))
# --- babble pool: Mandarin 4-talker babble from BKB (B set, right channel) ---
pieces=[]
for f in sorted(glob.glob(R+"/BKBSIN_Mandarin_B_Quiet/*/*.wav")):
    x,sr=sf.read(f); b=x[:,1]; pieces.append(b/rms(b))
xf=int(0.05*SR); ramp=np.linspace(0,1,xf)
pool=pieces[0]
for p in pieces[1:]:
    pool=np.concatenate([pool[:-xf], pool[-xf:]*(1-ramp)+p[:xf]*ramp, p[xf:]])
pool=pool/rms(pool)
print("babble pool s",len(pool)/SR)
# --- transcript map ---
mp={}
with open(R+"/msp_disyllables/rename_mapping.csv",encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        m=re.search(r"List(\d+)_Word(\d+)_",r["新文件名"]); mp[(int(m.group(1)),int(m.group(2)))]=(r["词语"].strip(),r["拼音"].strip())
def trim(w,sr):
    hop=int(sr*0.005); fr=np.array([rms(w[i:i+hop]) for i in range(0,len(w)-hop,hop)])
    db=20*np.log10(fr+1e-12); act=np.where(db>db.max()-40)[0]
    a=max(0,act[0]*hop-hop); b=min(len(w),(act[-1]+2)*hop); return w[a:b]
rows=[]; peaks=[]; meas=[]
for L in range(1,11):
    d=f"{OUT}/WIN_Mandarin_List{L}"; os.makedirs(d,exist_ok=True)
    lines=[]
    for n in range(1,36):
        src=glob.glob(R+f"/msp_disyllables/MSPDi_List{L}/MSPDi_List{L}_Word{n}_*.wav")[0]
        han,py=mp[(L,n)]
        w,sr=sf.read(src)
        if w.ndim>1: w=w.mean(1)
        w=resample_poly(w,SR,sr) if sr!=SR else w
        w=trim(w,SR)
        snr=LADDER[(n-1)//5]
        bab_rms=10**(BAB_DBFS/20)
        w=w/rms(w)*bab_rms*10**(snr/20)
        N=int(round((LEAD+TAIL)*SR))+len(w)
        st=rng.integers(0,len(pool)-N); bab=pool[st:st+N]; bab=bab/rms(bab)*bab_rms
        y=bab.copy(); i0=int(LEAD*SR); y[i0:i0+len(w)]+=w
        fl=int(FADE*SR); y[:fl]*=np.linspace(0,1,fl); y[-fl:]*=np.linspace(1,0,fl)
        peaks.append(np.abs(y).max())
        meas.append(snr-20*np.log10(rms(y[i0:i0+len(w)]-bab[i0:i0+len(w)])/rms(bab))*-1 if False else 20*np.log10(rms(w)/rms(bab))-snr)
        fn=f"WIN_Mandarin_L{L}_Word{n}_{py}.wav"
        sf.write(f"{d}/{fn}",y,SR,subtype="PCM_16")
        rows.append(dict(List=L,Word=n,File=f"WIN_Mandarin_List{L}/{fn}",SNR_dB=snr,Hanzi=han,Pinyin=py,
                         Fu2017_equivalent_list="yes" if L not in (2,3) else "no",Source=os.path.basename(src)))
        lines.append(f"{n}\t{snr:+d} dB".replace("+0 ","0 ")+f"\t{han}\t{py}")
    with open(f"{d}/WIN_Mandarin_List{L}.txt","w",encoding="utf-8") as f:
        f.write("Word\tSNR\tHanzi\tPinyin\n"+"\n".join(lines)+"\n")
with open(f"{OUT}/WIN_Mandarin_transcripts.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("files",len(rows),"max peak",round(max(peaks),3),"snr err max",round(max(np.abs(meas)),3))
