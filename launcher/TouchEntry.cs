// SPDX-License-Identifier: MIT
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Windows;

internal static class TouchEntry {
    [System.Runtime.InteropServices.DllImport("user32.dll",CharSet=System.Runtime.InteropServices.CharSet.Unicode)]static extern IntPtr FindWindow(string c,string title);
    [System.Runtime.InteropServices.DllImport("user32.dll")]static extern bool ShowWindow(IntPtr h,int command);
    [System.Runtime.InteropServices.DllImport("user32.dll")]static extern bool SetForegroundWindow(IntPtr h);
    [STAThread]static int Main(string[] args){
        try{
            int import=Array.IndexOf(args,"--import-json");
            if(import>=0&&import+1<args.Length){TranslationImport.Import(args[import+1]);var prefs=Preferences.Load();prefs.GameLanguage="tr";prefs.Save();return 0;}
            if(args.Contains("--test-launcher")){
                var p=new Preferences();if(p.Keys.Count!=12||p.Pad.Count!=7)throw new Exception("Invalid bindings");
                string qa=Path.Combine(Files.Root,"QA");Directory.CreateDirectory(qa);
                File.WriteAllBytes(Path.Combine(qa,"unicode-plist.bin"),TranslationImport.Plist(new[]{new System.Collections.Generic.KeyValuePair<string,string>("1","ÇçĞğİıÖöŞşÜü\nİkinci satır")}));
                return 0;
            }
            if(args.Contains("--test-discord"))return DiscordProtocolTest.Run();
            if(args.Contains("--validate")){
                foreach(string file in new[]{"Oyun/mgs_touch.exe","Oyun/SDL3.dll","Oyun/Assets/MGSTUS.app/Info.plist","Oyun/Assets/fonts/LiberationSans-Regular.ttf","Localization/metal_gear_solid_touch_english.json","Arayuz/TouchTheme.xaml"})
                    if(!File.Exists(Path.Combine(Files.Root,file.Replace('/',Path.DirectorySeparatorChar))))throw new FileNotFoundException(file);
                return 0;
            }
            string id;using(var sha=SHA256.Create())id=BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(Files.Root.ToLowerInvariant()))).Replace("-","").Substring(0,20);
            bool owner;
            using(var mutex=new Mutex(true,@"Local\PatriotsMGSTouch_"+id,out owner)){
                if(!owner&&!args.Contains("--render-ui")){IntPtr other=FindWindow(null,"METAL GEAR SOLID TOUCH | Patriots");if(other==IntPtr.Zero)other=FindWindow(null,"METAL GEAR SOLID TOUCH · Patriots");if(other!=IntPtr.Zero){ShowWindow(other,9);SetForegroundWindow(other);}return 0;}
                var app=new Application();return app.Run(new TouchWindow(args));
            }
        }catch(Exception e){Files.Log(e.ToString());if(args.Length==0)MessageBox.Show(e.Message,"Patriots · MGS Touch",MessageBoxButton.OK,MessageBoxImage.Error);return 1;}
    }
}
