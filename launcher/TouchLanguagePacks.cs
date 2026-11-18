// SPDX-License-Identifier: MIT
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Drawing.Text;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

public sealed class TouchLanguageEntry {
    public string id{get;set;} public string source{get;set;} public string text{get;set;}
    public string category{get;set;} public string record_id{get;set;} public string[] required_tokens{get;set;}
}
public sealed class TouchLanguageDocument {
    public string format{get;set;} public int template_version{get;set;} public string source_sha256{get;set;}
    public string language{get;set;} public string native_name{get;set;} public string culture{get;set;} public string author{get;set;}
    public string[] instructions{get;set;} public List<TouchLanguageEntry> entries{get;set;}
}
public sealed class TouchLanguageInfo {
    public string id,name,culture;public bool launcher,game;public int uiCount,gameCount;
    public override string ToString(){return name;}
}
public static class TouchLanguagePacks {
    public const string UIFormat="mgs-touch-launcher-language-v1",GameFormat="mgs-touch-game-language-v1";
    public static string MetaRoot{get{return Path.Combine(Files.Root,"Localization","Languages");}}
    public static string NativeRoot{get{return Path.Combine(Files.Root,"Oyun","languages");}}
    static readonly Dictionary<string,Dictionary<string,string>> uiCache=new Dictionary<string,Dictionary<string,string>>(),gameCache=new Dictionary<string,Dictionary<string,string>>();
    public static string Id(string source){using(var hash=SHA256.Create())return "ui_"+BitConverter.ToString(hash.ComputeHash(Encoding.UTF8.GetBytes(source))).Replace("-","").Substring(0,20).ToLowerInvariant();}
    public static string Canonical(string value){if(String.IsNullOrWhiteSpace(value))return null;string id=value.Trim().ToLowerInvariant();return id.Length<=35&&Regex.IsMatch(id,@"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")&&!Regex.IsMatch(id,@"^(con|prn|aux|nul|com[1-9]|lpt[1-9])$")?id:null;}
    public static bool Installed(string value){string id=Canonical(value);return id!=null&&(File.Exists(Path.Combine(MetaRoot,id,"launcher.json"))||File.Exists(Path.Combine(MetaRoot,id,"game.json")));}
    public static bool HasGame(string value){string id=Canonical(value);if(id=="en")return true;if(id=="tr")return File.Exists(Path.Combine(Files.Root,"Localization","installed_turkish.json"))&&File.Exists(Path.Combine(NativeRoot,"tr","Turkish.lproj","Localizable.strings"));return id!=null&&File.Exists(Path.Combine(MetaRoot,id,"game.json"))&&File.Exists(Path.Combine(NativeRoot,id,"English.lproj","Localizable.strings"));}
    public static string ResolveGame(string value){string id=Canonical(value);return HasGame(id)?id:"en";}
    public static string Normalize(string value){string id=Canonical(value);return id=="en"||id=="tr"||Installed(id)?id:"tr";}
    public static TouchLanguageInfo Info(string value){string id=Canonical(value)??"en";if(id=="tr"||id=="en")return new TouchLanguageInfo{id=id,name=id=="tr"?"Türkçe":"English",culture=id=="tr"?"tr-TR":"en-US",launcher=true,game=HasGame(id)};var ui=Load(Path.Combine(MetaRoot,id,"launcher.json"));var game=Load(Path.Combine(MetaRoot,id,"game.json"));var d=ui??game;if(d==null)throw new InvalidDataException("Language pack not found");return new TouchLanguageInfo{id=id,name=d.native_name,culture=d.culture,launcher=ui!=null,game=HasGame(id),uiCount=ui==null?0:ui.entries.Count(e=>!String.IsNullOrEmpty(e.text)),gameCount=game==null?0:game.entries.Count(e=>!String.IsNullOrEmpty(e.text))};}
    public static List<TouchLanguageInfo> Available(bool gameOnly=false){var list=new List<TouchLanguageInfo>{Info("tr"),Info("en")};if(Directory.Exists(MetaRoot))foreach(string folder in Directory.GetDirectories(MetaRoot)){string id=Canonical(Path.GetFileName(folder));if(id==null||id=="tr"||id=="en")continue;try{list.Add(Info(id));}catch{}}return gameOnly?list.Where(l=>l.game).ToList():list;}
    public static TouchLanguageDocument Template(string component){using(var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("Patriots.touch."+component+".json")){if(stream==null)throw new InvalidDataException("Missing translation template");using(var reader=new StreamReader(stream,Encoding.UTF8))return Parse(reader.ReadToEnd());}}
    public static Dictionary<string,object> Original(){using(var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("Patriots.touch.source.json"))using(var reader=new StreamReader(stream,Encoding.UTF8))return Files.Json.Deserialize<Dictionary<string,object>>(reader.ReadToEnd());}
    static TouchLanguageDocument Parse(string json){if(Encoding.UTF8.GetByteCount(json)>12*1024*1024)throw new InvalidDataException("Language JSON is too large");var d=Files.Json.Deserialize<TouchLanguageDocument>(json.TrimStart('\ufeff'));if(d==null||d.entries==null)throw new InvalidDataException("Invalid language JSON");return d;}
    static TouchLanguageDocument Load(string path){return File.Exists(path)?Parse(File.ReadAllText(path,Encoding.UTF8)):null;}
    public static string[] Tokens(string s){return Regex.Matches(s??"",@"\{[^{}]+\}|%(?:\d+\$)?[-+#0 .\d]*(?:@|[sdifuoxX])|%%").Cast<Match>().Select(m=>m.Value).OrderBy(x=>x,StringComparer.Ordinal).ToArray();}
    public static string Translate(string source,string locale,bool game=false){string id=Canonical(locale);if(id=="en"||id=="tr"||id==null)return source;var cache=game?gameCache:uiCache;lock(cache){Dictionary<string,string> map;if(!cache.TryGetValue(id,out map)){map=new Dictionary<string,string>();try{var d=Load(Path.Combine(MetaRoot,id,game?"game.json":"launcher.json"));if(d!=null)foreach(var row in d.entries)if(row!=null&&!String.IsNullOrEmpty(row.text))map[row.source]=row.text;}catch{}cache[id]=map;}string value;return map.TryGetValue(source,out value)?value:source;}}
    public static string GameL(string tr,string en,string language){return language=="tr"?tr:Translate(en,language,true);}
    public static string GameString(string id,string fallback,string language){try{if(language=="tr"||language=="en")return fallback;var doc=Load(Path.Combine(MetaRoot,Canonical(language),"game.json"));var row=doc.entries.FirstOrDefault(e=>e.category=="game_localization"&&e.record_id==id);return row==null?fallback:String.IsNullOrEmpty(row.text)?row.source:row.text;}catch{return fallback;}}
    static void Validate(TouchLanguageDocument doc,string component){
        string id=Canonical(doc.language);if(id==null||id=="en"||id=="tr")throw new InvalidDataException(Loc.L("Yerleşik dillerin üzerine yazılamaz; farklı bir dil kodu kullan.","Built-in languages cannot be overwritten; use a different language code."));
        var template=Template(component);if(doc.format!=template.format||doc.template_version!=1||doc.source_sha256!=template.source_sha256||doc.entries.Count>10000)throw new InvalidDataException(Loc.L("Dil paketi biçimi veya oyun sürümü uyuşmuyor.","Language-pack format or game version does not match."));
        if(String.IsNullOrWhiteSpace(doc.native_name)||doc.native_name.Length>80||doc.native_name.Any(Char.IsControl))throw new InvalidDataException(Loc.L("Dilin görünen adı geçersiz.","Invalid language display name."));
        try{CultureInfo.GetCultureInfo(doc.culture);}catch{throw new InvalidDataException(Loc.L("Dil kültür kodu geçersiz.","Invalid language culture code."));}
        var expected=template.entries.ToDictionary(e=>e.id);var seen=new HashSet<string>();
        foreach(var row in doc.entries){TouchLanguageEntry original;if(row==null||row.id==null||!seen.Add(row.id)||!expected.TryGetValue(row.id,out original))throw new InvalidDataException(Loc.L("Bilinmeyen veya yinelenen metin kimliği.","Unknown or duplicate text ID."));
            if(row.source!=original.source||row.category!=original.category||row.record_id!=original.record_id||!Enumerable.SequenceEqual(row.required_tokens??new string[0],original.required_tokens??new string[0]))throw new InvalidDataException(Loc.L("Kaynak metin veya korunan alan değişmiş: ","Source text or protected metadata changed: ")+row.id);
            string text=row.text??"";if(text.IndexOf('\0')>=0||Encoding.UTF8.GetByteCount(text)>8192)throw new InvalidDataException(Loc.L("Geçersiz veya çok uzun metin: ","Invalid or overly long text: ")+row.id);
            if(text.Length>0&&!Enumerable.SequenceEqual(Tokens(text),Tokens(row.source)))throw new InvalidDataException(Loc.L("Korunan metin işaretleri değişmiş: ","Protected text tokens changed: ")+row.id);
        }
        doc.language=id;doc.author=doc.author??"";
    }
    public static void EnsureStopped(){foreach(var process in System.Diagnostics.Process.GetProcessesByName("mgs_touch"))using(process)try{if(String.Equals(Path.GetDirectoryName(process.MainModule.FileName),Path.Combine(Files.Root,"Oyun"),StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException(Loc.L("Dil paketi kurmadan önce oyunu kapat.","Close the game before installing a language pack."));}catch(System.ComponentModel.Win32Exception){} }
    static void CopyTree(string from,string to){if(!Directory.Exists(from))return;foreach(string file in Directory.GetFiles(from,"*",SearchOption.AllDirectories)){string dest=Path.Combine(to,file.Substring(from.Length).TrimStart(Path.DirectorySeparatorChar));Directory.CreateDirectory(Path.GetDirectoryName(dest));File.Copy(file,dest,true);}}
    static void DeleteOwned(string path,string root){string full=Path.GetFullPath(path),prefix=Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;if(!full.StartsWith(prefix,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Invalid language path");if(Directory.Exists(full))Directory.Delete(full,true);}
    public static string Import(string path){
        EnsureStopped();TouchLanguageDocument ui=null,game=null;
        if(Path.GetExtension(path).Equals(".zip",StringComparison.OrdinalIgnoreCase))using(var archive=ZipFile.OpenRead(path)){
            long total=0;if(archive.Entries.Count>8)throw new InvalidDataException("Too many language files");
            foreach(var entry in archive.Entries){if(entry.FullName.EndsWith("/"))continue;if(entry.FullName!="launcher.json"&&entry.FullName!="game.json")throw new InvalidDataException(Loc.L("Dil paketinde izin verilmeyen dosya: ","Disallowed language-pack file: ")+entry.FullName);total+=entry.Length;if(entry.Length>12*1024*1024||total>24*1024*1024)throw new InvalidDataException("Language ZIP too large");using(var input=entry.Open())using(var bytes=new MemoryStream()){byte[] buffer=new byte[16384];int n;while((n=input.Read(buffer,0,buffer.Length))>0){if(bytes.Length+n>entry.Length)throw new InvalidDataException("Invalid ZIP length");bytes.Write(buffer,0,n);}if(bytes.Length!=entry.Length)throw new InvalidDataException("Truncated ZIP");var doc=Parse(Encoding.UTF8.GetString(bytes.ToArray()));if(entry.FullName=="launcher.json"&&ui==null)ui=doc;else if(entry.FullName=="game.json"&&game==null)game=doc;else throw new InvalidDataException("Duplicate language component");}}
        }else{var doc=Parse(File.ReadAllText(path,Encoding.UTF8));if(doc.format==UIFormat)ui=doc;else if(doc.format==GameFormat)game=doc;else throw new InvalidDataException(Loc.L("Desteklenmeyen dil dosyası.","Unsupported language file."));}
        if(ui==null&&game==null)throw new InvalidDataException("Empty language pack");if(ui!=null)Validate(ui,"launcher");if(game!=null)Validate(game,"game");string id=(ui??game).language;
        if(ui!=null&&game!=null&&ui.language!=game.language)throw new InvalidDataException(Loc.L("Launcher ve oyun dil kodları aynı olmalı.","Launcher and game language codes must match."));
        string suffix=Guid.NewGuid().ToString("N"),meta=Path.Combine(MetaRoot,id),native=Path.Combine(NativeRoot,id),stageMeta=Path.Combine(MetaRoot,".stage-"+suffix),stageNative=Path.Combine(NativeRoot,".stage-"+suffix),oldMeta=meta+".old-"+suffix,oldNative=native+".old-"+suffix;bool didMeta=false,didNative=false;
        try{
            Directory.CreateDirectory(stageMeta);Directory.CreateDirectory(stageNative);CopyTree(meta,stageMeta);CopyTree(native,stageNative);
            if(ui!=null)File.WriteAllText(Path.Combine(stageMeta,"launcher.json"),Files.Json.Serialize(ui),new UTF8Encoding(false));
            if(game!=null){BuildGame(game,stageNative);File.WriteAllText(Path.Combine(stageMeta,"game.json"),Files.Json.Serialize(game),new UTF8Encoding(false));}
            WriteRuntime(Load(Path.Combine(stageMeta,"launcher.json")),Load(Path.Combine(stageMeta,"game.json")),stageNative);
            if(Directory.Exists(native))Directory.Move(native,oldNative);Directory.Move(stageNative,native);didNative=true;
            if(Directory.Exists(meta))Directory.Move(meta,oldMeta);Directory.Move(stageMeta,meta);didMeta=true;
            lock(uiCache)uiCache.Remove(id);lock(gameCache)gameCache.Remove(id);return id;
        }catch{if(didMeta)DeleteOwned(meta,MetaRoot);if(Directory.Exists(oldMeta))Directory.Move(oldMeta,meta);if(didNative)DeleteOwned(native,NativeRoot);if(Directory.Exists(oldNative))Directory.Move(oldNative,native);throw;}
        finally{DeleteOwned(stageMeta,MetaRoot);DeleteOwned(stageNative,NativeRoot);if(didMeta&&didNative){DeleteOwned(oldMeta,MetaRoot);DeleteOwned(oldNative,NativeRoot);}}
    }
    static string Text(TouchLanguageEntry e){return String.IsNullOrEmpty(e.text)?e.source:e.text;}
    static void BuildGame(TouchLanguageDocument doc,string folder){
        var original=Original();var rows=((System.Collections.IEnumerable)original["entries"]).Cast<Dictionary<string,object>>();var changes=doc.entries.Where(e=>e.category=="game_localization").ToDictionary(e=>e.record_id,e=>Text(e));var pairs=rows.Select(r=>{string id=Convert.ToString(r["id"]),value;return new KeyValuePair<string,string>(id,changes.TryGetValue(id,out value)?value:Convert.ToString(r["source"]));}).ToList();
        string strings=Path.Combine(folder,"English.lproj","Localizable.strings");Directory.CreateDirectory(Path.GetDirectoryName(strings));File.WriteAllBytes(strings,TranslationImport.Plist(pairs));
        var life=doc.entries.FirstOrDefault(e=>e.category=="hud"&&e.id=="hud_life");if(life!=null)foreach(var image in new[]{"general_0.png","ipd_general_0.png"}){string output=Path.Combine(folder,"English.lproj",image);if(!String.IsNullOrEmpty(life.text)&&life.text!=life.source)RenderLife(life.text,image,output);else if(File.Exists(output))File.Delete(output);}
    }
    static void RenderLife(string value,string image,string output){
        string original=Path.Combine(NativeRoot,"en","English.lproj",image),font=Path.Combine(Files.Root,"Oyun","Assets","fonts","LiberationSans-Bold.ttf");if(!File.Exists(original)||!File.Exists(font))throw new FileNotFoundException(Loc.L("HUD çevirisi için özgün atlas veya font eksik.","Original atlas or font missing for HUD translation."));
        int k=image.StartsWith("ipd_")?2:1;var box=new Rectangle(46*k,116*k,54*k,8*k);
        using(var bitmap=new Bitmap(original))using(var graphics=Graphics.FromImage(bitmap))using(var collection=new PrivateFontCollection())using(var path=new GraphicsPath()){
            collection.AddFontFile(font);path.AddString(value,collection.Families[0],0,11*k,PointF.Empty,StringFormat.GenericTypographic);var bounds=path.GetBounds();float scale=Math.Min(1,Math.Min((box.Width-1)/Math.Max(1,bounds.Width),box.Height/Math.Max(1,bounds.Height)));
            using(var matrix=new Matrix(scale,0,0,scale,box.X-bounds.X*scale,box.Y-bounds.Y*scale))path.Transform(matrix);
            graphics.SetClip(box);graphics.CompositingMode=CompositingMode.SourceCopy;graphics.FillRectangle(Brushes.Transparent,box);graphics.CompositingMode=CompositingMode.SourceOver;graphics.SmoothingMode=SmoothingMode.AntiAlias;graphics.FillPath(Brushes.Black,path);bitmap.Save(output,ImageFormat.Png);
        }
    }
    static void Be(Stream s,uint n){for(int i=3;i>=0;i--)s.WriteByte((byte)(n>>(8*i)));}
    static void WriteRuntime(TouchLanguageDocument ui,TouchLanguageDocument game,string folder){var map=new Dictionary<string,string>();if(ui!=null)foreach(var e in ui.entries.Where(e=>!String.IsNullOrEmpty(e.text)))map[e.source]=e.text;if(game!=null)foreach(var e in game.entries.Where(e=>e.category!="hud"&&!String.IsNullOrEmpty(e.text)))map[e.source]=e.text;using(var file=File.Create(Path.Combine(folder,"runtime_text.bin"))){byte[] magic=Encoding.ASCII.GetBytes("PTXT0001");file.Write(magic,0,magic.Length);Be(file,(uint)map.Count);foreach(var p in map)foreach(string value in new[]{p.Key,p.Value}){byte[] bytes=Encoding.UTF8.GetBytes(value);Be(file,(uint)bytes.Length);file.Write(bytes,0,bytes.Length);}}}
    public static void Export(string folder){foreach(string component in new[]{"launcher","game"}){var doc=Template(component);doc.language="pt-BR";doc.native_name="Português (Brasil)";doc.culture="pt-BR";doc.author="";foreach(var row in doc.entries)row.text="";string dest=Path.Combine(folder,component,"pt-BR."+component+".json");Directory.CreateDirectory(Path.GetDirectoryName(dest));File.WriteAllText(dest,Files.Json.Serialize(doc),new UTF8Encoding(false));}}
}
