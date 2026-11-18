# MGSTUS dynamic coverage

Traces: `oracle/reports/coverage_step5_all.drcov`, `oracle/reports/coverage_step5_b.drcov`, `oracle/reports/coverage_20260928_182438.drcov`
Reference: `oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS` (__TEXT 0x1000-0x69000)

| | |
|---|---|
| raw BB rows | 249816 |
| unique blocks | 10084 |
| unique blocks outside __TEXT (should be ~0) | 0 |
| functions executed | **620 / 1388 (44.7%)** |
| __TEXT bytes executed | 116838 / 425984 (27.4%) |

## Per source file (executed / total functions)

| file | executed | total | % |
|---|---:|---:|---:|
| Classes/MGSTAppDelegate.mm | 97 | 161 | 60% |
| Classes/Enemies/EnemyBase.mm | 46 | 86 | 53% |
| Classes/Effect.mm | 49 | 66 | 74% |
| Classes/Player.mm | 40 | 66 | 61% |
| Classes/Enemies/Ray.mm | 0 | 47 | 0% |
| Classes/Enemies/EnemyManager.mm | 26 | 36 | 72% |
| Classes/Enemies/Gekko.mm | 0 | 36 | 0% |
| Classes/Enemies/Mantis.mm | 0 | 36 | 0% |
| Classes/Stage.m | 24 | 36 | 67% |
| Classes/Enemies/SelfDestructionGekko.mm | 0 | 33 | 0% |
| Classes/Enemies/Liquid.mm | 28 | 32 | 88% |
| Classes/DWGraphics.mm | 9 | 31 | 29% |
| Classes/Enemies/DwarfGekko.mm | 0 | 31 | 0% |
| Classes/GResult.mm | 7 | 31 | 23% |
| Classes/../Classes/EAGLView.mm | 20 | 30 | 67% |
| Classes/Enemies/Raven.mm | 0 | 28 | 0% |
| Classes/../Classes/Texture2D.m | 17 | 27 | 63% |
| Classes/Enemies/Octopus.mm | 0 | 27 | 0% |
| Classes/Enemies/Wolf.mm | 0 | 26 | 0% |
| SoundLibrary/SoundService.mm | 18 | 26 | 69% |
| Classes/TextureManager.m | 21 | 25 | 84% |
| Classes/Enemies/HavenSoldierB.mm | 0 | 23 | 0% |
| Classes/Enemies/Canard.mm | 6 | 22 | 27% |
| AudioSupport/GSoundCtrl.mm | 12 | 21 | 57% |
| Classes/Enemies/Doll.mm | 0 | 20 | 0% |
| SoundLibrary/AQSound.mm | 13 | 20 | 65% |
| Classes/Camera.mm | 16 | 18 | 89% |
| SoundLibrary/ALSound.mm | 13 | 18 | 72% |
| Classes/Enemies/PoweredSuit.mm | 0 | 17 | 0% |
| Classes/Enemies/FBomb.mm | 0 | 16 | 0% |
| Classes/StageEffects/FullScreenEffect.mm | 13 | 16 | 81% |
| Classes/Wall.mm | 13 | 16 | 81% |
| SoundLibrary/Sound.mm | 12 | 15 | 80% |
| Classes/DWUtilities.m | 11 | 13 | 85% |
| Classes/Enemies/NPC.mm | 11 | 12 | 92% |
| Classes/Enemies/PMC.mm | 8 | 12 | 67% |
| Classes/Objects/Item.mm | 9 | 12 | 75% |
| SoundLibrary/SoundManager.mm | 10 | 12 | 83% |
| Classes/Enemies/Karambit.mm | 0 | 11 | 0% |
| Classes/Enemies/RavenBomb.mm | 0 | 10 | 0% |
| Classes/Enemies/RavenSlider.mm | 0 | 10 | 0% |
| Classes/GSaveCtrl.mm | 6 | 10 | 60% |
| Classes/menuScroll.m | 10 | 10 | 100% |
| SoundLibrary/SoundResourceManager.mm | 8 | 10 | 80% |
| Classes/Enemies/HavenSoldierA.mm | 0 | 9 | 0% |
| Classes/Objects/ObjectBase.mm | 4 | 9 | 44% |
| Classes/Enemies/Railgun.mm | 0 | 8 | 0% |
| Classes/Enemies/RayMissile.mm | 0 | 8 | 0% |
| Classes/DWWebView.m | 1 | 7 | 14% |
| Classes/Enemies/RayWeapon.mm | 1 | 7 | 14% |
| Classes/Objects/Drum.mm | 4 | 7 | 57% |
| Classes/DebugDisp.mm | 0 | 6 | 0% |
| Classes/FallingObjects.mm | 6 | 6 | 100% |
| Classes/Objects/MimicObject.mm | 0 | 6 | 0% |
| Classes/PlayerMissile.mm | 2 | 6 | 33% |
| Classes/game_msg.mm | 2 | 6 | 33% |
| Classes/DWconnect.m | 4 | 5 | 80% |
| Classes/Enemies/Missile.mm | 4 | 5 | 80% |
| Classes/Enemies/WeaponBase.mm | 1 | 5 | 20% |
| Classes/Objects/BGObject.mm | 4 | 5 | 80% |
| SoundLibrary/SoundLabel.mm | 4 | 5 | 80% |
| SoundLibrary/SoundMisc.mm | 4 | 4 | 100% |
| Classes/Enemies/HavenSoldier.mm | 0 | 3 | 0% |
| Classes/Objects/EffectObject.mm | 3 | 3 | 100% |
| SoundLibrary/SoundThread.mm | 0 | 3 | 0% |
| SoundLibrary/tablereader.mm | 2 | 3 | 67% |
| main.m | 1 | 1 | 100% |
