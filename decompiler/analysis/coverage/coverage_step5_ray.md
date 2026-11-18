# MGSTUS dynamic coverage

Traces: `oracle/reports/coverage_step5_c.drcov`
Reference: `oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS` (__TEXT 0x1000-0x69000)

| | |
|---|---|
| raw BB rows | 818149 |
| unique blocks | 10074 |
| unique blocks outside __TEXT (should be ~0) | 0 |
| functions executed | **574 / 1388 (41.4%)** |
| __TEXT bytes executed | 111846 / 425984 (26.3%) |

## Per source file (executed / total functions)

| file | executed | total | % |
|---|---:|---:|---:|
| Classes/MGSTAppDelegate.mm | 85 | 161 | 53% |
| Classes/Enemies/EnemyBase.mm | 31 | 86 | 36% |
| Classes/Effect.mm | 49 | 66 | 74% |
| Classes/Player.mm | 35 | 66 | 53% |
| Classes/Enemies/Ray.mm | 44 | 47 | 94% |
| Classes/Enemies/EnemyManager.mm | 22 | 36 | 61% |
| Classes/Enemies/Gekko.mm | 0 | 36 | 0% |
| Classes/Enemies/Mantis.mm | 0 | 36 | 0% |
| Classes/Stage.m | 32 | 36 | 89% |
| Classes/Enemies/SelfDestructionGekko.mm | 0 | 33 | 0% |
| Classes/Enemies/Liquid.mm | 0 | 32 | 0% |
| Classes/DWGraphics.mm | 9 | 31 | 29% |
| Classes/Enemies/DwarfGekko.mm | 0 | 31 | 0% |
| Classes/GResult.mm | 17 | 31 | 55% |
| Classes/../Classes/EAGLView.mm | 18 | 30 | 60% |
| Classes/Enemies/Raven.mm | 0 | 28 | 0% |
| Classes/../Classes/Texture2D.m | 16 | 27 | 59% |
| Classes/Enemies/Octopus.mm | 0 | 27 | 0% |
| Classes/Enemies/Wolf.mm | 0 | 26 | 0% |
| SoundLibrary/SoundService.mm | 14 | 26 | 54% |
| Classes/TextureManager.m | 21 | 25 | 84% |
| Classes/Enemies/HavenSoldierB.mm | 0 | 23 | 0% |
| Classes/Enemies/Canard.mm | 0 | 22 | 0% |
| AudioSupport/GSoundCtrl.mm | 10 | 21 | 48% |
| Classes/Enemies/Doll.mm | 0 | 20 | 0% |
| SoundLibrary/AQSound.mm | 13 | 20 | 65% |
| Classes/Camera.mm | 10 | 18 | 56% |
| SoundLibrary/ALSound.mm | 14 | 18 | 78% |
| Classes/Enemies/PoweredSuit.mm | 0 | 17 | 0% |
| Classes/Enemies/FBomb.mm | 0 | 16 | 0% |
| Classes/StageEffects/FullScreenEffect.mm | 10 | 16 | 62% |
| Classes/Wall.mm | 7 | 16 | 44% |
| SoundLibrary/Sound.mm | 12 | 15 | 80% |
| Classes/DWUtilities.m | 10 | 13 | 77% |
| Classes/Enemies/NPC.mm | 8 | 12 | 67% |
| Classes/Enemies/PMC.mm | 0 | 12 | 0% |
| Classes/Objects/Item.mm | 7 | 12 | 58% |
| SoundLibrary/SoundManager.mm | 8 | 12 | 67% |
| Classes/Enemies/Karambit.mm | 0 | 11 | 0% |
| Classes/Enemies/RavenBomb.mm | 0 | 10 | 0% |
| Classes/Enemies/RavenSlider.mm | 0 | 10 | 0% |
| Classes/GSaveCtrl.mm | 4 | 10 | 40% |
| Classes/menuScroll.m | 10 | 10 | 100% |
| SoundLibrary/SoundResourceManager.mm | 6 | 10 | 60% |
| Classes/Enemies/HavenSoldierA.mm | 0 | 9 | 0% |
| Classes/Objects/ObjectBase.mm | 5 | 9 | 56% |
| Classes/Enemies/Railgun.mm | 0 | 8 | 0% |
| Classes/Enemies/RayMissile.mm | 7 | 8 | 88% |
| Classes/DWWebView.m | 1 | 7 | 14% |
| Classes/Enemies/RayWeapon.mm | 7 | 7 | 100% |
| Classes/Objects/Drum.mm | 0 | 7 | 0% |
| Classes/DebugDisp.mm | 0 | 6 | 0% |
| Classes/FallingObjects.mm | 4 | 6 | 67% |
| Classes/Objects/MimicObject.mm | 0 | 6 | 0% |
| Classes/PlayerMissile.mm | 4 | 6 | 67% |
| Classes/game_msg.mm | 2 | 6 | 33% |
| Classes/DWconnect.m | 3 | 5 | 60% |
| Classes/Enemies/Missile.mm | 0 | 5 | 0% |
| Classes/Enemies/WeaponBase.mm | 1 | 5 | 20% |
| Classes/Objects/BGObject.mm | 5 | 5 | 100% |
| SoundLibrary/SoundLabel.mm | 3 | 5 | 60% |
| SoundLibrary/SoundMisc.mm | 4 | 4 | 100% |
| Classes/Enemies/HavenSoldier.mm | 0 | 3 | 0% |
| Classes/Objects/EffectObject.mm | 3 | 3 | 100% |
| SoundLibrary/SoundThread.mm | 0 | 3 | 0% |
| SoundLibrary/tablereader.mm | 2 | 3 | 67% |
| main.m | 1 | 1 | 100% |
