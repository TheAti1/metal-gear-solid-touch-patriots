# MGSTUS dynamic coverage

Traces: `oracle/reports/coverage_20260928_182438.drcov`
Reference: `oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS` (__TEXT 0x1000-0x69000)

| | |
|---|---|
| raw BB rows | 225949 |
| unique blocks | 8225 |
| unique blocks outside __TEXT (should be ~0) | 0 |
| functions executed | **550 / 1388 (39.6%)** |
| __TEXT bytes executed | 97652 / 425984 (22.9%) |

## Per source file (executed / total functions)

| file | executed | total | % |
|---|---:|---:|---:|
| Classes/MGSTAppDelegate.mm | 90 | 161 | 56% |
| Classes/Enemies/EnemyBase.mm | 45 | 86 | 52% |
| Classes/Effect.mm | 44 | 66 | 67% |
| Classes/Player.mm | 35 | 66 | 53% |
| Classes/Enemies/Ray.mm | 0 | 47 | 0% |
| Classes/Enemies/EnemyManager.mm | 26 | 36 | 72% |
| Classes/Enemies/Gekko.mm | 0 | 36 | 0% |
| Classes/Enemies/Mantis.mm | 0 | 36 | 0% |
| Classes/Stage.m | 24 | 36 | 67% |
| Classes/Enemies/SelfDestructionGekko.mm | 0 | 33 | 0% |
| Classes/Enemies/Liquid.mm | 0 | 32 | 0% |
| Classes/DWGraphics.mm | 9 | 31 | 29% |
| Classes/Enemies/DwarfGekko.mm | 0 | 31 | 0% |
| Classes/GResult.mm | 5 | 31 | 16% |
| Classes/../Classes/EAGLView.mm | 19 | 30 | 63% |
| Classes/Enemies/Raven.mm | 0 | 28 | 0% |
| Classes/../Classes/Texture2D.m | 16 | 27 | 59% |
| Classes/Enemies/Octopus.mm | 0 | 27 | 0% |
| Classes/Enemies/Wolf.mm | 0 | 26 | 0% |
| SoundLibrary/SoundService.mm | 15 | 26 | 58% |
| Classes/TextureManager.m | 21 | 25 | 84% |
| Classes/Enemies/HavenSoldierB.mm | 0 | 23 | 0% |
| Classes/Enemies/Canard.mm | 0 | 22 | 0% |
| AudioSupport/GSoundCtrl.mm | 11 | 21 | 52% |
| Classes/Enemies/Doll.mm | 0 | 20 | 0% |
| SoundLibrary/AQSound.mm | 13 | 20 | 65% |
| Classes/Camera.mm | 15 | 18 | 83% |
| SoundLibrary/ALSound.mm | 13 | 18 | 72% |
| Classes/Enemies/PoweredSuit.mm | 0 | 17 | 0% |
| Classes/Enemies/FBomb.mm | 0 | 16 | 0% |
| Classes/StageEffects/FullScreenEffect.mm | 11 | 16 | 69% |
| Classes/Wall.mm | 13 | 16 | 81% |
| SoundLibrary/Sound.mm | 12 | 15 | 80% |
| Classes/DWUtilities.m | 10 | 13 | 77% |
| Classes/Enemies/NPC.mm | 7 | 12 | 58% |
| Classes/Enemies/PMC.mm | 8 | 12 | 67% |
| Classes/Objects/Item.mm | 9 | 12 | 75% |
| SoundLibrary/SoundManager.mm | 9 | 12 | 75% |
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
| Classes/DWconnect.m | 3 | 5 | 60% |
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
