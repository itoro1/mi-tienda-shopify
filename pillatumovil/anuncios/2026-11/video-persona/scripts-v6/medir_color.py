"""Color de piel (bisenet), saturación, nitidez y grano por plano: python3 medir_color.py VIDEO caras.npz"""
import subprocess, sys, numpy as np, cv2, json
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__))); from caras import ses
F=sys.argv[1]; d=np.load(sys.argv[2]); LM=d['lm']
TPL=np.array([[0.37691676,0.46864664],[0.62285697,0.46912813],[0.50123859,0.61331904],[0.39308822,0.72541100],[0.61150205,0.72490465]],np.float32)
def cinco(l): return np.array([l[36:42].mean(0),l[42:48].mean(0),l[30],l[48],l[54]],np.float32)
def frames(ns):
    sel='+'.join(f'eq(n\\,{n})' for n in ns)
    p=subprocess.run(['ffmpeg','-v','error','-i',F,'-vf',f"select='{sel}',scale=1080:1920:in_color_matrix=bt709,format=rgb24",'-vsync','0','-f','rawvideo','-'],capture_output=True)
    return np.frombuffer(p.stdout,np.uint8).reshape(-1,1920,1080,3)
def parse(crop_rgb):
    x=crop_rgb.astype(np.float32)/255; x=(x-np.array([0.485,0.456,0.406],np.float32))/np.array([0.229,0.224,0.225],np.float32)
    o=ses('bisenet_resnet_34').run(None,{'input':x.transpose(2,0,1)[None].copy()})[0][0]; o=o-o.max(0,keepdims=True); e=np.exp(o); return e/e.sum(0,keepdims=True)
def lab(rgb): return cv2.cvtColor(rgb.astype(np.float32)/255,cv2.COLOR_RGB2LAB)
PL={'1':range(96,117,4),'2a':range(117,165,8),'2b':list(range(165,215,8))+list(range(222,283,10)),'3':range(283,358,12),'4w':range(400,497,16),'4c':range(504,584,12),'5':range(584,670,10),'6':range(670,706,7)}
res={}
for nom,ns in PL.items():
    ns=list(ns); fr=frames(ns); acc=[]
    for k,n in enumerate(ns):
        im=fr[k]; M,_=cv2.estimateAffinePartial2D(cinco(LM[n]),TPL*512,method=cv2.LMEDS)
        cr=cv2.warpAffine(im,M,(512,512),flags=cv2.INTER_AREA,borderMode=cv2.BORDER_REPLICATE)
        pr=parse(cr); sk=(pr[1]>0.85)
        L=lab(cr)[sk]; 
        g=cv2.cvtColor(cr,cv2.COLOR_RGB2GRAY).astype(np.float32)
        lap=cv2.Laplacian(g,cv2.CV_32F)[cv2.erode(sk.astype(np.uint8),np.ones((9,9)))>0]
        hp=g-cv2.GaussianBlur(g,(0,0),1.0); grano=hp[cv2.erode(sk.astype(np.uint8),np.ones((9,9)))>0]
        hsv=cv2.cvtColor(im,cv2.COLOR_RGB2HSV)
        acc.append([*np.median(L,0), lap.var(), grano.std(), hsv[...,1].mean(), *im.reshape(-1,3).mean(0), *np.median(cr[sk],0)])
    a=np.array(acc).mean(0); res[nom]=a.tolist()
    print(f'{nom:3s} piel Lab {a[0]:5.1f} {a[1]:5.1f} {a[2]:5.1f} | piel RGB {a[9]:4.0f} {a[10]:4.0f} {a[11]:4.0f} | lapl {a[3]:6.1f} grano {a[4]:4.2f} | sat {a[5]:5.1f} | media RGB {a[6]:4.0f} {a[7]:4.0f} {a[8]:4.0f}')
json.dump(res,open('color_'+F.split('/')[-1]+'.json','w'))
