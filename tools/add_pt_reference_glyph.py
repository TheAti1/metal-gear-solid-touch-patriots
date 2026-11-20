"""Add a drawn reference mark (U+203B) to the bundled Apache-licensed Droid fallback.

Usage: python tools/add_pt_reference_glyph.py input.ttf output.ttf
Requires fonttools. No glyphs are copied from Windows or other proprietary fonts.
"""
from pathlib import Path
import argparse,os
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

def patch(source,output):
    source,output=Path(source),Path(output)
    font=TTFont(source);name='patriots_uni203B';em=font['head'].unitsPerEm;order=list(font.getGlyphOrder())
    if 0x203B in font.getBestCmap():
        if source.resolve()!=output.resolve():output.write_bytes(source.read_bytes())
        return
    pen=TTGlyphPen(None)
    def polygon(points):
        pen.moveTo(tuple(round(v*em) for v in points[0]))
        for point in points[1:]:pen.lineTo(tuple(round(v*em) for v in point))
        pen.closePath()
    # Two diagonal strokes form the reference cross; four diamonds stay legible
    # at the game's small body-text size. All contours use the same winding.
    polygon([(.24,.21),(.29,.16),(.76,.63),(.71,.68)])
    polygon([(.71,.16),(.76,.21),(.29,.68),(.24,.63)])
    for x,y in [(.5,.78),(.5,.06),(.14,.42),(.86,.42)]:
        polygon([(x-.04,y),(x,y+.04),(x+.04,y),(x,y-.04)])
    font['glyf'][name]=pen.glyph();font['hmtx'].metrics[name]=(em,round(.1*em))
    font.setGlyphOrder(order+[name])
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format in (4,12,13):table.cmap[0x203B]=name
    output.parent.mkdir(parents=True,exist_ok=True);temp=output.with_name(output.name+'.new')
    font.save(temp);font.close();os.replace(temp,output)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');a=p.parse_args()
    patch(a.input,a.output)
