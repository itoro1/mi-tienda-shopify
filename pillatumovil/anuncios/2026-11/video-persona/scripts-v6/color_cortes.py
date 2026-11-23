import subprocess, sys, numpy as np, cv2
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__))); from caras import ses
TPL=np.array([[0.37691676,0.46864664],[0.62285697,0.46912813],[0.50123859,0.61331904],[0.39308822,0.72541100],[0.61150205,0.72490465]],np.float32)
def frames(F,ns):
    sel='+'.join(f'eq(n\\,{n})' for n in ns)
    p=subprocess.run(['ffmpeg','-v','error','-i',F,'-vf',f"select='{sel}',scale=1080:1920:in_color_matrix=bt709,format=rgb24",'-vsync','0','-f','rawvideo','-'],capture_output=True)
    return dict(zip(sorted(ns),np.frombuffer(p.stdout,np.uint8).reshape(-1,1920,1080,3)))
def piel(im,l):
    p5=np.array([l[36:42].mean(0),l[42:48].mean(0),l[30],l[48],l[54]],np.float32)
    M,_=cv2.estimateAffinePartial2D(p5,TPL*512,method=cv2.LMEDS); cr=cv2.warpAffine(im,M,(512,512),flags=cv2.INTER_AREA)
    x=(cr.astype(np.float32)/255-np.array([0.485,0.456,0.406],np.float32))/np.array([0.229,0.224,0.225],np.float32)
    o=ses('bisenet_resnet_34').run(None,{'input':x.transpose(2,0,1)[None].copy()})[0][0].argmax(0)
    lab=cv2.cvtColor(cr.astype(np.float32)/255,cv2.COLOR_RGB2LAB)[o==1]; return np.median(lab,0)
def medir(F,car,cortes):
    LM=np.load(car)['lm']; ns=sorted({n for c in cortes for n in (c-3,c-2,c-1,c,c+1,c+2)}); fr=frames(F,ns); out=[]
    for c in cortes:
        a=np.mean([piel(fr[n],LM[n]) for n in (c-3,c-2,c-1)],0); b=np.mean([piel(fr[n],LM[n]) for n in (c,c+1,c+2)],0)
        out.append((c,a,b,float(np.linalg.norm(a-b))))
    return out
for nom,F,car,cortes in (('antes (piezas sin igualar, cortes de la v5)','base1080.mp4','caras_base.npz',[117,165,283,584,670]),
                         ('v6 (igualado)',sys.argv[1],sys.argv[2],[117,165,298,584,670])):
    print(nom)
    for c,a,b,de in medir(F,car,cortes):
        print(f'  corte {c}: piel Lab antes del corte {a[0]:.1f}/{a[1]:.1f}/{a[2]:.1f} -> después {b[0]:.1f}/{b[1]:.1f}/{b[2]:.1f}   dE {de:.1f}')
