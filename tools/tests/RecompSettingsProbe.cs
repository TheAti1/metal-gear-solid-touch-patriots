// SPDX-License-Identifier: MIT
// Runs beside an isolated copy of the real launcher; no native game is needed.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;

internal static class RecompSettingsProbe {
    static Dictionary<string,object> Map(object x){return (Dictionary<string,object>)x;}
    static IEnumerable<object> Rows(object x){return ((IEnumerable)x).Cast<object>();}
    static void Require(bool ok,string message){if(!ok)throw new Exception(message);}
    static object Raw(string value){return Files.Json.DeserializeObject(value);}
    static object Get(Dictionary<string,object> doc,string key){object value=doc;foreach(string part in key.Split('/'))value=Map(value)[part];return value;}
    static void Set(Dictionary<string,object> doc,string key,object value){var parts=key.Split('/');for(int i=0;i<parts.Length-1;i++)doc=Map(doc[parts[i]]);doc[parts[parts.Length-1]]=value;}
    static Dictionary<string,string> Ini(string path){return File.ReadAllLines(path).Where(s=>s.Contains("=")).Select(s=>s.Split(new[]{'='},2)).ToDictionary(s=>s[0],s=>s[1]);}
    static void Check(Dictionary<string,object> change){
        var full=Map(Files.Json.DeserializeObject(Files.Json.Serialize(new Preferences())));
        foreach(var pair in change)Set(full,pair.Key,pair.Value);
        Files.Atomic(Path.Combine(Files.Root,"settings.json"),Files.Json.Serialize(full));
        var p=Preferences.Load();p.Save();
        var actual=Map(Files.Json.DeserializeObject(File.ReadAllText(Path.Combine(Files.Root,"settings.json"))));
        foreach(var pair in change)Require(Files.Json.Serialize(Get(actual,pair.Key))==Files.Json.Serialize(pair.Value),"JSON round trip: "+pair.Key);
        var desktop=Ini(Path.Combine(Files.Root,"Oyun","desktop.ini"));
        var native=Ini(Path.Combine(Files.Engine,"retouched.cfg"));
        foreach(var pair in change){
            string key=pair.Key,expected=pair.Value is bool?((bool)pair.Value?"1":"0"):Convert.ToString(pair.Value,System.Globalization.CultureInfo.InvariantCulture);
            if(key=="GameLanguage")Require(desktop["language"]==expected,key);
            else if(key=="Fullscreen")Require(desktop["fullscreen"]==expected,key);
            else if(key=="Vsync")Require(desktop["vsync"]==expected,key);
            else if(key=="Scale")Require(desktop["render_scale"]==expected,key);
            else if(key=="Fill")Require(desktop["fill"]==expected&&native["screen_fill"]==expected,key);
            else if(key=="FpsLimit")Require(desktop["max_fps"]==expected,key);
            else if(key=="Deadzone")Require(Math.Abs(Double.Parse(desktop["deadzone"],System.Globalization.CultureInfo.InvariantCulture)-Convert.ToDouble(pair.Value)/100)<.00001,key);
            else if(key.StartsWith("Keys/"))Require(desktop["key_"+key.Substring(5)]==expected,key);
            else{
                string mapped=key=="Music"?"music_volume":key=="Effects"?"effects_volume":key=="HqAudio"?"hq_resampling":key=="Aim"?"aim_sensitivity":key=="Vibration"?"vibration":key=="Crisp"?"crisp_pixels":key=="AutoPause"?"pause_on_leave":key=="SkipIntro"?"skip_intro":null;
                if(mapped!=null)Require(native[mapped]==expected,key);
            }
        }
    }
    static int Main(string[] args){
        try{
            var profile=Map(Files.Json.DeserializeObject(File.ReadAllText(args[0])));
            // Match the existing Turkish overlay's discovery contract without
            // copying original assets or a real user's save into this test.
            Directory.CreateDirectory(Path.Combine(Files.Root,"Localization"));
            File.WriteAllText(Path.Combine(Files.Root,"Localization","installed_turkish.json"),"{}");
            string table=Path.Combine(Files.Root,"Oyun/languages/tr/Turkish.lproj/Localizable.strings");Directory.CreateDirectory(Path.GetDirectoryName(table));File.WriteAllText(table,"");
            Directory.CreateDirectory(Files.Engine);byte[] save=Enumerable.Range(0,1024).Select(i=>(byte)(i%251)).ToArray();string savedata=Path.Combine(Files.Engine,"SAVE.data");File.WriteAllBytes(savedata,save);
            int cases=0;
            foreach(var row in Rows(profile["settings"]).Select(Map)){
                if(row.ContainsKey("defaults")){Check(Map(row["defaults"]).ToDictionary(p=>p.Key,p=>Raw((string)p.Value)));cases++;}
                if(row.ContainsKey("choices"))foreach(var choice in Rows(row["choices"]).Select(Map)){Check(Map(choice["set"]).ToDictionary(p=>p.Key,p=>Raw((string)p.Value)));cases++;}
                if(row.ContainsKey("slider")){var slider=Map(row["slider"]);foreach(string bound in new[]{"min","max"}){Check(new Dictionary<string,object>{{(string)slider["key"],slider[bound]}});cases++;}}
                if(row.ContainsKey("bindings"))foreach(var binding in Rows(Map(row["bindings"])["actions"]).Select(Map)){Check(new Dictionary<string,object>{{(string)binding["key"],"J"}});cases++;}
            }
            Require(File.ReadAllBytes(savedata).SequenceEqual(save),"Settings changed a save");
            Console.WriteLine("PASS: "+cases+" real Preferences JSON/desktop.ini/retouched.cfg round trips; save bytes unchanged.");return 0;
        }catch(Exception e){Console.Error.WriteLine(e);return 1;}
    }
}
