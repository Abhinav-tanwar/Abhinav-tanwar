"""Render the profile's slow orbital GIF. Requires Pillow; no network calls."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
# Override these paths when generating on another operating system.
SANS_PATH = FONT_DIR / 'Arial.ttf'
SERIF_PATH = FONT_DIR / 'Georgia Italic.ttf'
W, H, FRAMES = 1200, 460, 120
SIZE = (960, 368)
BG = (21, 21, 16)
AMBER = (230, 183, 117)
INK = (238, 233, 220)


def tracked(draw, xy, text, size, color, spacing=0, serif=False):
    font = ImageFont.truetype(str(SERIF_PATH if serif else SANS_PATH), size)
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=font, fill=color, anchor='ls')
        x += draw.textlength(character, font=font) + spacing


def blend(color, alpha):
    return tuple(round(b + (c-b)*alpha) for b,c in zip(BG,color))


base = Image.new('RGB', (W,H), BG)
draw = ImageDraw.Draw(base)
# A static glow avoids flicker in the GIF palette.
for r in range(250, 0, -3):
    alpha=.09*(1-r/250)**2
    draw.ellipse((940-r,224-r,940+r,224+r),fill=blend((145,100,45),alpha))
tracked(draw,(50,46),'ABHINAV TANWAR · AI ENGINEER',12,(200,194,177),2.4)
draw.line((50,68,1150,68),fill=(59,58,48))
tracked(draw,(48,166),'Intelligence,',74,INK,-4)
tracked(draw,(48,247),'built for',74,INK,-4)
tracked(draw,(48,332),'the real world.',79,AMBER,-3,True)
tracked(draw,(50,408),'GENERATIVE AI / RETRIEVAL / AGENTS',11,(185,173,150),2)
tracked(draw,(830,408),'CONTEXT → REASONING → APPLICATION',9,(185,173,150),.8)
points=[]
for i in range(120):
    angle=i*math.pi*(3-math.sqrt(5));y=1-2*(i+.5)/120
    radius=math.sqrt(1-y*y)
    points.append((math.cos(angle)*radius,y,math.sin(angle)*radius))
edges=[]
for i,p in enumerate(points):
    for j in range(i+1,len(points)):
        q=points[j];distance=sum((p[k]-q[k])**2 for k in range(3))
        if distance<.18:edges.append((i,j,distance))
frames=[]
palette=None
for frame in range(FRAMES):
    phase=2*math.pi*frame/FRAMES
    image=base.copy();draw=ImageDraw.Draw(image)
    projected=[]
    for x,y,z in points:
        xx=x*math.cos(phase+.5)+z*math.sin(phase+.5)
        zz=z*math.cos(phase+.5)-x*math.sin(phase+.5)
        projected.append((940+xx*166,224+y*166,zz))
    for i,j,distance in edges:
        a,b=projected[i],projected[j]
        alpha=(.10+(a[2]+b[2]+2)*.025)*(1-distance/.3)
        draw.line((a[0],a[1],b[0],b[1]),fill=blend(AMBER,alpha),width=1)
    for angle in (0,60,120):
        rotation=math.radians(angle)
        orbit=[]
        for step in range(121):
            theta=2*math.pi*step/120
            x,y=205*math.cos(theta),78*math.sin(theta)
            orbit.append((940+x*math.cos(rotation)-y*math.sin(rotation),224+x*math.sin(rotation)+y*math.cos(rotation)))
        draw.line(orbit,fill=blend(AMBER,.23),width=1)
        theta=phase+rotation
        x,y=205*math.cos(theta),78*math.sin(theta)
        x,y=940+x*math.cos(rotation)-y*math.sin(rotation),224+x*math.sin(rotation)+y*math.cos(rotation)
        draw.ellipse((x-2.5,y-2.5,x+2.5,y+2.5),fill=AMBER)
    for x,y,z in projected:
        radius=1.2+(z+1)*.6
        draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=blend(AMBER,.3+(z+1)*.28))
    draw.ellipse((937,221,943,227),fill=AMBER)
    image=image.resize(SIZE,Image.Resampling.LANCZOS)
    if palette is None:
        palette=image.quantize(colors=128,method=Image.Quantize.MEDIANCUT)
    frames.append(image.quantize(palette=palette,dither=Image.Dither.NONE))
output=ROOT/'assets/header.gif'
frames[0].save(output,save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True,disposal=1)
# Structural validation prevents accidentally publishing a flattened animation.
with Image.open(output) as check:
    assert check.n_frames == FRAMES
    assert check.size == SIZE
    assert check.info['loop'] == 0
    assert check.info['duration'] == 100
assert output.stat().st_size < 5*1024*1024
print(f'{output.name}: {FRAMES} frames, 12-second loop, {output.stat().st_size/1024:.0f} KB')
