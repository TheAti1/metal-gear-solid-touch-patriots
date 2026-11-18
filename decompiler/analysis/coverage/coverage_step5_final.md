# MGSTUS dynamic coverage

Traces: `oracle/reports/campaign_01-04.drcov`, `oracle/reports/campaign_05-08.drcov`, `oracle/reports/campaign_09-12.drcov`, `oracle/reports/campaign_10-12.drcov`, `oracle/reports/campaign_13-16.drcov`, `oracle/reports/campaign_17a.drcov`, `oracle/reports/campaign_17b.drcov`, `oracle/reports/campaign_17c.drcov`, `oracle/reports/campaign_18-20.drcov`, `oracle/reports/campaign_18a.drcov`, `oracle/reports/campaign_18b.drcov`, `oracle/reports/campaign_18c.drcov`, `oracle/reports/coverage_20260928_182438.drcov`, `oracle/reports/coverage_step5_all.drcov`, `oracle/reports/coverage_step5_b.drcov`, `oracle/reports/coverage_step5_c.drcov`
Reference: `oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS` (__TEXT 0x1000-0x69000)

| | |
|---|---|
| raw BB rows | 35088933 |
| unique blocks | 21911 |
| unique blocks outside __TEXT (should be ~0) | 0 |
| functions executed | **1119 / 1388 (80.6%)** |
| __TEXT bytes executed | 231230 / 425984 (54.3%) |

## Per source file (executed / total functions)

| file | executed | total | % |
|---|---:|---:|---:|
| Classes/MGSTAppDelegate.mm | 109 | 161 | 68% |
| Classes/Enemies/EnemyBase.mm | 68 | 86 | 79% |
| Classes/Effect.mm | 64 | 66 | 97% |
| Classes/Player.mm | 56 | 66 | 85% |
| Classes/Enemies/Ray.mm | 45 | 47 | 96% |
| Classes/Enemies/EnemyManager.mm | 33 | 36 | 92% |
| Classes/Enemies/Gekko.mm | 36 | 36 | 100% |
| Classes/Enemies/Mantis.mm | 31 | 36 | 86% |
| Classes/Stage.m | 34 | 36 | 94% |
| Classes/Enemies/SelfDestructionGekko.mm | 33 | 33 | 100% |
| Classes/Enemies/Liquid.mm | 28 | 32 | 88% |
| Classes/DWGraphics.mm | 9 | 31 | 29% |
| Classes/Enemies/DwarfGekko.mm | 29 | 31 | 94% |
| Classes/GResult.mm | 23 | 31 | 74% |
| Classes/../Classes/EAGLView.mm | 20 | 30 | 67% |
| Classes/Enemies/Raven.mm | 21 | 28 | 75% |
| Classes/../Classes/Texture2D.m | 17 | 27 | 63% |
| Classes/Enemies/Octopus.mm | 26 | 27 | 96% |
| Classes/Enemies/Wolf.mm | 22 | 26 | 85% |
| SoundLibrary/SoundService.mm | 18 | 26 | 69% |
| Classes/TextureManager.m | 21 | 25 | 84% |
| Classes/Enemies/HavenSoldierB.mm | 19 | 23 | 83% |
| Classes/Enemies/Canard.mm | 21 | 22 | 95% |
| AudioSupport/GSoundCtrl.mm | 13 | 21 | 62% |
| Classes/Enemies/Doll.mm | 18 | 20 | 90% |
| SoundLibrary/AQSound.mm | 13 | 20 | 65% |
| Classes/Camera.mm | 16 | 18 | 89% |
| SoundLibrary/ALSound.mm | 14 | 18 | 78% |
| Classes/Enemies/PoweredSuit.mm | 13 | 17 | 76% |
| Classes/Enemies/FBomb.mm | 14 | 16 | 88% |
| Classes/StageEffects/FullScreenEffect.mm | 16 | 16 | 100% |
| Classes/Wall.mm | 16 | 16 | 100% |
| SoundLibrary/Sound.mm | 12 | 15 | 80% |
| Classes/DWUtilities.m | 11 | 13 | 85% |
| Classes/Enemies/NPC.mm | 12 | 12 | 100% |
| Classes/Enemies/PMC.mm | 11 | 12 | 92% |
| Classes/Objects/Item.mm | 9 | 12 | 75% |
| SoundLibrary/SoundManager.mm | 10 | 12 | 83% |
| Classes/Enemies/Karambit.mm | 8 | 11 | 73% |
| Classes/Enemies/RavenBomb.mm | 4 | 10 | 40% |
| Classes/Enemies/RavenSlider.mm | 7 | 10 | 70% |
| Classes/GSaveCtrl.mm | 8 | 10 | 80% |
| Classes/menuScroll.m | 10 | 10 | 100% |
| SoundLibrary/SoundResourceManager.mm | 8 | 10 | 80% |
| Classes/Enemies/HavenSoldierA.mm | 9 | 9 | 100% |
| Classes/Objects/ObjectBase.mm | 5 | 9 | 56% |
| Classes/Enemies/Railgun.mm | 7 | 8 | 88% |
| Classes/Enemies/RayMissile.mm | 7 | 8 | 88% |
| Classes/DWWebView.m | 1 | 7 | 14% |
| Classes/Enemies/RayWeapon.mm | 7 | 7 | 100% |
| Classes/Objects/Drum.mm | 4 | 7 | 57% |
| Classes/DebugDisp.mm | 0 | 6 | 0% |
| Classes/FallingObjects.mm | 6 | 6 | 100% |
| Classes/Objects/MimicObject.mm | 6 | 6 | 100% |
| Classes/PlayerMissile.mm | 4 | 6 | 67% |
| Classes/game_msg.mm | 5 | 6 | 83% |
| Classes/DWconnect.m | 4 | 5 | 80% |
| Classes/Enemies/Missile.mm | 5 | 5 | 100% |
| Classes/Enemies/WeaponBase.mm | 1 | 5 | 20% |
| Classes/Objects/BGObject.mm | 5 | 5 | 100% |
| SoundLibrary/SoundLabel.mm | 4 | 5 | 80% |
| SoundLibrary/SoundMisc.mm | 4 | 4 | 100% |
| Classes/Enemies/HavenSoldier.mm | 3 | 3 | 100% |
| Classes/Objects/EffectObject.mm | 3 | 3 | 100% |
| SoundLibrary/SoundThread.mm | 0 | 3 | 0% |
| SoundLibrary/tablereader.mm | 2 | 3 | 67% |
| main.m | 1 | 1 | 100% |
