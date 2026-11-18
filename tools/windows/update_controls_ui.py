from pathlib import Path
p=Path(__file__).with_name("TouchLauncher.cs")
s=p.read_text(encoding="utf-8")
changes={
    'AssemblyVersion("1.0.1.0")':'AssemblyVersion("1.0.2.0")',
    'L("Duraklat / geri","Pause / back")':'L("Duraklat / devam","Pause / resume")',
    'case "back":return L("Geri","Back")':'case "back":return L("Geri / iptal","Back / cancel")',
    'Row(L("İmleç hızı","Cursor speed")':'Row(L("Kontrolcü hızı","Controller speed")',
    'Menülerde sol tıkla seçim yap. Gamepad: sağ analog nişan, RT ateş, LT siper.':'Menülerde sol analog / yön tuşlarıyla seç, onay tuşuyla ilerle, geri tuşuyla iptal et. Start duraklatır veya devam eder. Gamepad: sağ analog nişan, RT ateş, LT siper.',
    'Left click selects menus. Controller: right stick aims, RT fires, LT takes cover.':'In menus, use the left stick / D-pad to select, confirm to proceed, back to cancel. Start pauses or resumes. Controller: right stick aims, RT fires, LT takes cover.',
}
for old,new in changes.items():
    assert old in s,old
    s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
