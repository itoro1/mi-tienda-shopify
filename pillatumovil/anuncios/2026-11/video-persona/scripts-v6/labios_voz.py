"""Desfase labios-voz por plano (23/11): correlación entre la apertura de la boca (puntos 62-66 / alto de la cara) y la
   envolvente de la voz (300-3000 Hz, un valor por fotograma). lag +d = la boca va d fotogramas por delante de la voz.
   Compara con clip-intone.mp4 con su propio audio. python3 labios_voz.py [FINAL.mp4] [caras_final.npz]"""
import subprocess, sys, numpy as np, scipy.signal as ss
VP='/home/user/mi-tienda-shopify/pillatumovil/anuncios/2026-11/video-persona'
D='/tmp/claude-0/-home-user-mi-tienda-shopify/684840b5-c1b1-582f-bcd6-bf822ef2e72f/scratchpad/dep/v6/final'
def audio(f):
    p=subprocess.run(['ffmpeg','-v','error','-i',f,'-map','0:a','-ac','1','-ar','48000','-f','f32le','-'],capture_output=True)
    return np.frombuffer(p.stdout,np.float32).astype(np.float64)
def env(x, fps=24):
    b,a=ss.butter(4,[300,3000],btype='band',fs=48000); y=ss.filtfilt(b,a,x)
    n=int(len(y)/48000*fps); hop=48000//fps
    return np.array([20*np.log10(np.sqrt(np.mean(y[i*hop:(i+1)*hop]**2))+1e-9) for i in range(n)])
def ap(lm): return np.linalg.norm(lm[:,66]-lm[:,62],axis=1)/(lm[:,8,1]-lm[:,27,1])
def lags(m,e,a,b,rng=8):
    out=[]
    for d in range(-rng,rng+1):
        # d>0: mouth ahead of voice (mouth at n correlates with voice at n+d)
        x=m[a:b]; y=e[a+d:b+d]
        out.append(np.corrcoef(np.nan_to_num(x),y)[0,1])
    out=np.array(out); k=int(np.argmax(out)); return k-rng, out[k], out[rng]
fin=sys.argv[1] if len(sys.argv)>1 else D+'/dependienta_v6_1080.mp4'
car=sys.argv[2] if len(sys.argv)>2 else D+'/datos/caras_final.npz'
eF=env(audio(fin)); eI=env(audio(VP+'/clip-intone.mp4'))
mF=ap(np.load(car)['lm']); mI=ap(np.load(D+'/datos/caras_intone.npz')['lm'])
segs=[('1',8,117),('3',298,358),('4w',366,491),('4c',504,584),('6',672,704)]
if len(sys.argv)>3: segs=eval(sys.argv[3])
for n,a,b in segs:
    print(n,a,b,'final: lag %+d r %.2f (r0 %.2f)'%lags(mF,eF,a,b), ' | intone own:', 'lag %+d r %.2f (r0 %.2f)'%lags(mI,eI,a,b) if b<len(mI)-8 else '-')
