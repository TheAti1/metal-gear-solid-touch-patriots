from pathlib import Path
root=Path(__file__).resolve().parent
p=root/"TouchLauncher.cs"
s=p.read_text(encoding="utf-8")
s=s.replace('{"screenshot","F12"},{"aim_up","W"}', '{"screenshot","F12"},{"cover","Space"},{"aim_up","W"}')
s=s.replace('{"shake",3}};', '{"shake",3},{"cover",7}};')
s=s.replace('p.Keys.Count!=11||p.Pad.Count!=6', 'p.Keys.Count!=12||p.Pad.Count!=7')
if 'case "cover":return' not in s:
    s=s.replace('case "press":return', 'case "cover":return L("Siper al (basılı tut)","Take cover (hold)");case "press":return')
s=s.replace('new DiscordPresence(game.Id,settings.Language)', 'new DiscordPresence(game.Id,settings.GameLanguage)')
s=s.replace('Fare: sol tuş dokunma ve sürükleme; tekerlek veya sağ tuş silah yakınlaştırma. WASD / yön tuşları imleci hareket ettirir. Enter veya Space dokunur.',
    'Oynanış: fareyle nişan al, sol tuşla ateş et; sağ tuş veya Space ile siper al. Tekerlek ya da Q/E ile silah değiştir. Menülerde sol tıkla seçim yap. Gamepad: sağ analog nişan, RT ateş, LT siper.')
s=s.replace('Mouse: left click and drag to touch; wheel or right click to change weapon zoom. WASD / arrows move the cursor. Enter or Space touches.',
    'Gameplay: move the mouse to aim, left click to fire, hold right click or Space for cover. Wheel or Q/E changes weapon. Left click selects menus. Controller: right stick aims, RT fires, LT takes cover.')
assert '{"cover","Space"}' in s and '{"cover",7}' in s
p.write_text(s,encoding="utf-8")
p=root/"windows_main.c"
s=p.read_text(encoding="utf-8").replace('host_accel(2,0,-1);host_accel(-2,0,-1);','host_accel(3.5,0,-1);host_accel(-3.5,0,-1);')
p.write_text(s,encoding="utf-8")
print("Updated native/launcher control bindings")
