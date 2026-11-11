import sys, glob
from PIL import Image
d=sys.argv[1]; fs=sorted(glob.glob(d+'/f_*.png'))
for k in range(0,len(fs),8):
    ims=[Image.open(f).resize((640,360)) for f in fs[k:k+8]]
    sheet=Image.new('RGB',(1280,360*4))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*640,(i//2)*360))
    sheet.save(d+'/sheet%d.png'%(k//8))
