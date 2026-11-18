from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
REPO=Path(r"D:\Patriots_MGS_Touch_PC\mgs-retouched")
shutil.copy2(HERE/"patriots_pc.c",REPO/"android-retouched/rt/patriots_pc.c")
shutil.copy2(HERE/"patriots_fields.c",REPO/"android-retouched/rt/game/patriots_fields.c")
path=REPO/"android-retouched/rt/rtx.c"
original=(HERE.parents[1]/"upstream/mgs-retouched/android-retouched/rt/rtx.c").read_text(encoding="utf-8")
original=original.replace('H_SETDAMAGE, H_FRIENDFIRE, H_SUBDAMAGE, H_COUNT','H_SETDAMAGE, H_FRIENDFIRE, H_SUBDAMAGE, H_PC_CONTROLLER, H_PC_FLICK, H_COUNT')
original=original.replace('"setDamage:::", "friendFire:", "subDamage:"','"setDamage:::", "friendFire:", "subDamage:", "private_UpdateController"')
# Preserve the upstream selectors exactly; the following insertion is tied to H_COUNT.
start=original.index('static const char *hook_names[H_COUNT]')
end=original.index('};',start)
if 'private_UpdateController' not in original[start:end]:
    original=original[:end].rstrip()+', "private_UpdateController" '+original[end:]
end=original.index('};',start)
original=original[:end].rstrip()+', "getTouchFrip::" '+original[end:]
original=original.replace('int rtx_pre(u32 self,', 'void patriots_pc_before_controller(void);\nint rtx_pre(u32 self,')
original=original.replace('void patriots_pc_before_controller(void);', 'void patriots_pc_before_controller(void);\nvoid patriots_pc_before_scene(void);')
original=original.replace('void patriots_pc_before_scene(void);','void patriots_pc_before_scene(void);\nint patriots_pc_flick(const u32 *args,u64 *result);')
original=original.replace('    switch (which(sel)) {\n    case H_DRAWBAR:', '    switch (which(sel)) {\n    case H_PC_CONTROLLER: patriots_pc_before_controller(); return 0;\n    case H_DRAWBAR:',1)
original=original.replace('    case H_GAMESCENE:\n', '    case H_GAMESCENE:\n        patriots_pc_before_scene();\n',1)
original=original.replace('    case H_PC_CONTROLLER:', '    case H_PC_FLICK: return patriots_pc_flick(a,ret);\n    case H_PC_CONTROLLER:',1)
original=original.replace('str_new_utf8("RETOUCHED")', 'str_new_utf8("PATRIOTS")')
path.write_text(original,encoding="utf-8")
assert 'case H_PC_CONTROLLER:' in original
print("Installed typed PC controller bridge")
