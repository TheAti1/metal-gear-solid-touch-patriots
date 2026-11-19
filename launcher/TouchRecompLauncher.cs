// SPDX-License-Identifier: MIT
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;

// Shares the existing native process/configuration path with the WPF launcher.
internal static class TouchGameProcess {
    public static void Validate(){
        foreach(string file in new[]{"Oyun/mgs_touch.exe","Oyun/SDL3.dll","Oyun/Assets/MGSTUS.app/Info.plist","Oyun/Assets/fonts/LiberationSans-Regular.ttf","Localization/metal_gear_solid_touch_english.json","Arayuz/TouchTheme.xaml"})
            if(!File.Exists(Path.Combine(Files.Root,file.Replace('/',Path.DirectorySeparatorChar))))throw new FileNotFoundException(file);
    }
    public static ProcessStartInfo Create(Preferences settings){
        string exe=Path.Combine(Files.Root,"Oyun","mgs_touch.exe");
        if(!File.Exists(exe))throw new FileNotFoundException(Loc.L("Oyun çalıştırıcısı bulunamadı.","The game executable is missing."),exe);
        settings.GameLanguage=TouchLanguagePacks.ResolveGame(settings.GameLanguage);
        settings.Save();
        return new ProcessStartInfo(exe){WorkingDirectory=Path.GetDirectoryName(exe),UseShellExecute=false,CreateNoWindow=true};
    }
}

internal static class TouchRecompLauncher {
    public static int Run(string[] args){
        // No WPF Application/window is created in this explicitly requested mode.
        if(args.Any(a=>a!="--recomplauncher"))return Error(21,"Unsupported launch argument. Update the RecompLauncher profile and try again.");
        try{
            TouchGameProcess.Validate();
            bool firstStart=!File.Exists(Path.Combine(Files.Root,"settings.json"));
            var settings=Preferences.Load();
            string mode=Environment.GetEnvironmentVariable("RECOMPLAUNCHER_MODE");
            if(firstStart&&(mode=="bigpicture"||mode=="desktop"))settings.Fullscreen=mode=="bigpicture";
            Loc.Language=settings.Language;
            var start=TouchGameProcess.Create(settings);
            Files.Log("RECOMPLAUNCHER mode="+(mode??"unspecified")+" pad="+(Environment.GetEnvironmentVariable("RECOMPLAUNCHER_PAD")??"auto")+"; native SDL controller detection retained");
            using(var game=Process.Start(start))using(var discord=new DiscordPresence(game.Id,settings.GameLanguage)){
                Files.Log("RECOMPLAUNCHER START pid="+game.Id);
                game.WaitForExit();
                Files.Log("RECOMPLAUNCHER EXIT "+game.ExitCode);
                // The process stays alive until the native game has flushed and
                // exited, so external save backups cannot race a live game.
                return game.ExitCode;
            }
        }catch(FileNotFoundException e){return Error(20,"The prepared Touch PC package is incomplete. Install this support update over the complete Patriots PC package. Missing: "+e.Message);}
        catch(Exception e){return Error(23,"Touch could not start. Extract the full package to a writable folder and check Saves/launcher.log. "+e.Message);}
    }
    static int Error(int code,string text){Console.Error.WriteLine(text);Files.Log("RECOMPLAUNCHER ERROR "+code+" "+text);return code;}
}
