#!/usr/bin/env python3
"""Build GitHub-themed profile cards from a real ASCII portrait.

Use --photo PATH to regenerate the character grid from the supplied portrait.
The default build needs only the committed text grid and profile JSON.
"""
from pathlib import Path
from html import escape
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
COLS, ROWS = 68, 46

def convert_photo(path):
    from PIL import Image, ImageOps, ImageFilter, ImageDraw
    photo = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    # Coordinates are normalized to the upright reference, 1368 x 1824.
    photo = photo.resize((1368, 1824), Image.Resampling.LANCZOS)
    crop = (270, 380, 1210, 1370)
    gray = ImageOps.grayscale(photo).crop(crop)
    sample = gray.filter(ImageFilter.UnsharpMask(radius=12, percent=110, threshold=4))
    sample = sample.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    # Follow the outer silhouette to exclude the room without altering the face.
    outline = [(315,1365),(412,1290),(485,1255),(388,1230),(338,1130),
        (325,1010),(340,900),(327,790),(366,660),(398,566),(451,501),
        (544,451),(650,419),(728,430),(786,424),(903,445),(1002,481),
        (1083,552),(1131,647),(1144,754),(1174,863),(1139,926),
        (1170,1030),(1104,1151),(1060,1242),(1001,1260),(1133,1310),(1209,1369)]
    mask = Image.new('L',(940,990))
    ImageDraw.Draw(mask).polygon([(x-crop[0],y-crop[1]) for x,y in outline],fill=255)
    mask = mask.resize((COLS,ROWS),Image.Resampling.LANCZOS)
    ramp = " .,:;irsXA253hMHGS#9B&@"
    for theme in ('dark', 'light'):
        lines=[]
        for y in range(ROWS):
            row=''
            for x in range(COLS):
                if mask.getpixel((x,y)) < 100:
                    row+=' '
                else:
                    # Light backgrounds need dense dark characters in shadows.
                    value=max(0, min(1, (sample.getpixel((x,y))-25)/185))
                    value=(value if theme == "dark" else 1-value)**1.1
                    row+=ramp[round(value*(len(ramp)-1))]
            lines.append(row)
        (ASSETS/f'portrait-{theme}.txt').write_text('\n'.join(lines)+'\n')

def portrait_row(line, theme):
    """Use neutral gray ink to recover tonal depth on white backgrounds."""
    if theme == 'dark':
        return escape(line).replace(' ', '&#160;')
    ramp = " .,:;irsXA253hMHGS#9B&@"
    parts = []
    for char in line:
        density = ramp.index(char)/(len(ramp)-1)
        ink = round(225*(1-density)**0.8)
        color = f'#{ink:02x}{ink:02x}{ink:02x}'
        encoded = escape(char).replace(' ', '&#160;')
        weight = 700 if density >= 0.72 else 400
        parts.append(f'<tspan fill="{color}" font-weight="{weight}">{encoded}</tspan>')
    return ''.join(parts)

THEMES = {
    'dark': {'ink':'#ffffff', 'text':'#f0f6fc', 'key':'#ffa657',
             'value':'#a5d6ff', 'heading':'#3fb950', 'muted':'#6e7681'},
    'light': {'ink':'#000000', 'text':'#1f2328', 'key':'#953800',
              'value':'#0550ae', 'heading':'#1a7f37', 'muted':'#8c959f'},
}

def build(lines, profile, mobile=False, theme="dark"):
    colors = THEMES[theme]
    w,h = (440,1500) if mobile else (1080,530)
    px,py = (25,50) if mobile else (20,60)
    tx,ty = (24,510) if mobile else (440,33)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
      '<title id="title">Gabriele Monni | Software engineer</title>',
      '<desc id="desc">A monochrome ASCII portrait alongside Gabriele Monni\'s skills, work and contact information in a Neofetch terminal layout.</desc>',
      f'<g fill="{colors["text"]}" font-family="Menlo,Consolas,monospace" style="font-variant-ligatures:none">',
      f'<g fill="{colors["ink"]}" font-size="9.7" xml:space="preserve" style="white-space:pre">']
    for i,line in enumerate(lines):
        encoded=portrait_row(line, theme)
        parts.append(f'<text x="{px}" y="{py+i*9.1:.1f}" textLength="390" lengthAdjust="spacingAndGlyphs">{encoded}</text>')
    parts.append('</g>')
    mobile_y = ty
    def row(index, label, value=None):
        nonlocal mobile_y
        if mobile:
            if value is None:
                mobile_y += 23 if index else 0
                chunks = [label]
            else:
                chunks = [label + ':', value]
            for j,chunk in enumerate(chunks):
                color = colors['heading'] if value is None else colors['key' if j==0 else 'value']
                parts.append(f'<text x="{tx}" y="{mobile_y}" fill="{color}" font-size="16">{escape(chunk)}</text>')
                mobile_y += 22
            mobile_y += 11
            return
        y = ty+index*21
        def segment(x, content, color, anchor='start'):
            encoded=escape(content).replace(' ', '&#160;')
            parts.append(f'<text x="{x:.2f}" y="{y}" fill="{color}" font-size="14" text-anchor="{anchor}">{encoded}</text>')
        cell=8.43
        if value is None:
            segment(tx, label, colors['heading'])
            count=int((600-(len(label)+2)*cell)/cell)
            segment(tx+(len(label)+2)*cell, '-'*count, colors['muted'])
        else:
            segment(tx, label+':', colors['key'])
            count=max(0, int(600/cell)-len(label)-len(value)-4)
            segment(tx+(len(label)+2)*cell, '.'*count, colors['muted'])
            segment(tx+600, value, colors['value'], 'end')
    row(0,'gabriele@zer0codestuff')
    row(2,'Name',profile['name'])
    row(3,'Role',profile['role'])
    row(4,'Location',profile['location'])
    row(5,'Work','IT Technical Officer')
    row(6,'Building',' / '.join(profile['building']))
    row(7,'Languages.Code','Python, TypeScript, Swift, SQL')
    row(8,'Languages.Spoken','Italian, English')
    row(10,'Focus.AI','Multimodal systems, local inference')
    row(11,'Focus.Product','Native macOS apps, data products')
    row(13,'Contact')
    row(14,'Website',profile['website'])
    row(15,'Email',profile['email'])
    row(16,'LinkedIn','in/hire-gabriele-monni')
    row(18,'Selected work')
    row(19,'MUVAD','Explainable video anomaly detection')
    row(20,'AI Capability Signals','Frontier-model research')
    row(21,'Video Edit Checker','Local video & audio analysis')
    parts.extend(['</g>','</svg>'])
    return '\n'.join(parts)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--photo',type=Path)
    parser.add_argument('--classic', action='store_true', help='Build the earlier profile without radar')
    args=parser.parse_args()
    if args.photo: convert_photo(args.photo)
    if not args.classic:
        from build_profile import main as build_profile
        build_profile()
        return
    profile=json.loads((ROOT/'profile.json').read_text())
    for theme in THEMES:
        lines=(ASSETS/f'portrait-{theme}.txt').read_text().splitlines()
        assert len(lines)==ROWS and all(len(line)==COLS for line in lines)
        assert all(32<=ord(char)<=126 for line in lines for char in line)
        for mobile in (False,True):
            suffix='-mobile' if mobile else ''
            output=ASSETS/f'profile-{theme}{suffix}.svg'
            output.write_text(build(lines,profile,mobile,theme))
            print(output.relative_to(ROOT))

if __name__=='__main__': main()
