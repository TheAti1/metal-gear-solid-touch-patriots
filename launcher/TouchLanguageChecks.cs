// SPDX-License-Identifier: MIT
using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;

internal static class TouchLanguageChecks {
    static void Require(bool ok,string message){if(!ok)throw new Exception("Language-pack check: "+message);}
    static string Save(string name,TouchLanguageDocument doc){string path=Path.Combine(Files.Root,name);File.WriteAllText(path,Files.Json.Serialize(doc),new UTF8Encoding(false));return path;}
    static void Header(TouchLanguageDocument d){d.language="pt-qa";d.native_name="Português (teste)";d.culture="pt-BR";d.author="Isolated test fixture";}
    static void Reject(Action action){try{action();}catch(InvalidDataException){return;}throw new Exception("Invalid language pack was accepted");}
    public static int Run(bool worker){
        if(!worker){string temp=Path.Combine(Path.GetTempPath(),"Patriots-Touch-Languages-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(temp);try{string exe=Path.Combine(temp,"Metal Gear Solid Touch.exe");File.Copy(AssemblyPath(),exe);using(var process=Process.Start(new ProcessStartInfo(exe,"--test-language-packs-worker"){UseShellExecute=false,CreateNoWindow=true})){if(!process.WaitForExit(60000)){process.Kill();throw new Exception("Language test timed out");}Require(process.ExitCode==0,"isolated worker failed");}string qa=Path.Combine(Files.Root,"QA");Directory.CreateDirectory(qa);File.Copy(Path.Combine(temp,"result.json"),Path.Combine(qa,"language-packs.json"),true);return 0;}finally{string full=Path.GetFullPath(temp),prefix=Path.GetFullPath(Path.GetTempPath()).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;if(full.StartsWith(prefix,StringComparison.OrdinalIgnoreCase)&&Path.GetFileName(full).StartsWith("Patriots-Touch-Languages-"))Directory.Delete(full,true);}}
        var ui=TouchLanguagePacks.Template("launcher");Header(ui);ui.entries.First(e=>e.source=="DISPLAY").text="VÍDEO";
        TouchLanguagePacks.Import(Save("launcher.json",ui));Loc.Language="pt-qa";Require(Loc.L("GÖRÜNTÜ","DISPLAY")=="VÍDEO","Unicode launcher text");Require(TouchLanguagePacks.ResolveGame("pt-qa")=="en","launcher-only English game fallback");
        var game=TouchLanguagePacks.Template("game");Header(game);game.entries.First(e=>e.category=="game_localization"&&e.source=="START").text="INICIAR Çãõ";game.entries.First(e=>e.source=="Move the R stick left and right").text="Mova o analógico direito para os lados";
        var token=game.entries.First(e=>e.required_tokens.Length>0);token.text=token.source;
        TouchLanguagePacks.Import(Save("game.json",game));Require(TouchLanguagePacks.ResolveGame("pt-qa")=="pt-qa","compiled community game active");Require(TouchLanguagePacks.GameString("1","START","pt-qa")=="INICIAR Çãõ","Discord/game title lookup");
        string table=Path.Combine(TouchLanguagePacks.NativeRoot,"pt-qa","English.lproj","Localizable.strings");byte[] original=File.ReadAllBytes(table);Require(Encoding.ASCII.GetString(original,0,8)=="bplist00","game binary plist");Require(File.Exists(Path.Combine(TouchLanguagePacks.NativeRoot,"pt-qa","runtime_text.bin")),"native UTF-8 catalogue");
        var bad=TouchLanguagePacks.Template("game");Header(bad);bad.entries.First(e=>e.required_tokens.Length>0).text="lost token";Reject(()=>TouchLanguagePacks.Import(Save("bad.json",bad)));
        bad=TouchLanguagePacks.Template("game");Header(bad);bad.entries[0].source="Changed";Reject(()=>TouchLanguagePacks.Import(Save("bad.json",bad)));
        bad=TouchLanguagePacks.Template("game");Header(bad);bad.entries.Add(bad.entries[0]);Reject(()=>TouchLanguagePacks.Import(Save("bad.json",bad)));
        bad=TouchLanguagePacks.Template("game");Header(bad);bad.entries.Add(new TouchLanguageEntry{id="0",source="Helvetica-Bold",text="Changed font",category="game_localization",record_id="0",required_tokens=new string[0]});Reject(()=>TouchLanguagePacks.Import(Save("bad.json",bad)));
        var core=TouchLanguagePacks.Template("launcher");Header(core);core.language="en";Reject(()=>TouchLanguagePacks.Import(Save("core.json",core)));core.language="../bad";Reject(()=>TouchLanguagePacks.Import(Save("core.json",core)));
        string zip=Path.Combine(Files.Root,"bad.zip");using(var archive=ZipFile.Open(zip,ZipArchiveMode.Create))using(var writer=new StreamWriter(archive.CreateEntry("../escape.json").Open()))writer.Write("{}");Reject(()=>TouchLanguagePacks.Import(zip));
        bad=TouchLanguagePacks.Template("game");Header(bad);bad.entries.First(e=>e.id=="hud_life").text="VIDA";try{TouchLanguagePacks.Import(Save("missing-font.json",bad));throw new Exception("Missing HUD dependency accepted");}catch(FileNotFoundException){}Require(File.ReadAllBytes(table).SequenceEqual(original),"failed compilation preserves installed game");
        ui.entries.First(e=>e.source=="DISPLAY").text="Tela";TouchLanguagePacks.Import(Save("updated.json",ui));Require(Loc.L("GÖRÜNTÜ","DISPLAY")=="Tela","cache reloaded");Require(File.ReadAllBytes(table).SequenceEqual(original),"launcher component preserves game");
        zip=Path.Combine(Files.Root,"bundle.zip");using(var archive=ZipFile.Open(zip,ZipArchiveMode.Create)){foreach(var pair in new[]{Tuple.Create("launcher.json",ui),Tuple.Create("game.json",game)})using(var writer=new StreamWriter(archive.CreateEntry(pair.Item1).Open(),new UTF8Encoding(false)))writer.Write(Files.Json.Serialize(pair.Item2));}TouchLanguagePacks.Import(zip);
        Require(TouchLanguagePacks.Available().Count==3,"community locale discovered");TouchLanguagePacks.Export(Path.Combine(Files.Root,"Export"));Require(File.Exists(Path.Combine(Files.Root,"Export","launcher","pt-BR.launcher.json")),"template export");
        string broken=Path.Combine(TouchLanguagePacks.MetaRoot,"pt-bad");Directory.CreateDirectory(broken);File.WriteAllText(Path.Combine(broken,"launcher.json"),"broken");Require(TouchLanguagePacks.Translate("DISPLAY","pt-bad")=="DISPLAY","corrupt installed UI fallback");
        File.WriteAllText(Path.Combine(Files.Root,"result.json"),Files.Json.Serialize(new{passed=true,isolated=true,unicode_launcher=true,binary_plist=true,independent_components=true,english_fallback=true,tokens_protected=true,font_ids_protected=true,path_validation=true,compile_rollback=true,cache_reload=true,combined_zip=true,template_export=true,game_titles=true}),new UTF8Encoding(false));return 0;
    }
    static string AssemblyPath(){return System.Reflection.Assembly.GetExecutingAssembly().Location;}
}
