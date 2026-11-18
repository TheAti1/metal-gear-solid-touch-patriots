// SPDX-License-Identifier: GPL-3.0-or-later
// Discord's documented desktop IPC protocol. No bot, token, OAuth or account-file access.
using System;
using System.IO;
using System.IO.Pipes;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using Microsoft.Win32.SafeHandles;

public sealed class DiscordPresence : IDisposable
{
    public const string ApplicationId="1572290325937004574";
    private readonly string gameLanguage;private readonly int pid; private readonly ManualResetEvent stop=new ManualResetEvent(false);
    private readonly Thread worker; private readonly JavaScriptSerializer json=new JavaScriptSerializer();
    private NamedPipeClientStream pipe; private bool ready,published,withoutArt; private long nonce;
    private readonly long started=(long)(DateTime.UtcNow-new DateTime(1970,1,1)).TotalSeconds;
    private string lastActivity="",lastStatus=""; private DateTime nextSend=DateTime.MinValue;
    [DllImport("kernel32.dll",SetLastError=true)]private static extern bool PeekNamedPipe(SafePipeHandle h,IntPtr buffer,uint size,IntPtr read,out uint available,IntPtr left);
    public DiscordPresence(int processId,string language){gameLanguage=Loc.Normalize(language);pid=processId;worker=new Thread(Run){IsBackground=true,Name="Patriots Discord Presence"};worker.Start();}
    private void Status(string value){if(lastStatus==value)return;lastStatus=value;Files.Log("DISCORD "+value);try{Files.Atomic(Path.Combine(Files.Engine,"discord_durum.json"),json.Serialize(new {status=value,application_id=ApplicationId,pid=pid,utc=DateTime.UtcNow.ToString("o")}));}catch{}}
    private void Frame(uint op,string payload){byte[] b=Encoding.UTF8.GetBytes(payload);byte[] header=new byte[8];Array.Copy(BitConverter.GetBytes(op),header,4);Array.Copy(BitConverter.GetBytes(b.Length),0,header,4,4);pipe.Write(header,0,8);pipe.Write(b,0,b.Length);pipe.Flush();}
    private byte[] ReadExact(int length,int timeout){var b=new byte[length];int pos=0;var timer=Stopwatch.StartNew();while(pos<length){if(stop.WaitOne(0)||timer.ElapsedMilliseconds>timeout)throw new TimeoutException();uint available;if(!PeekNamedPipe(pipe.SafePipeHandle,IntPtr.Zero,0,IntPtr.Zero,out available,IntPtr.Zero))throw new IOException("Discord disconnected");if(available==0){stop.WaitOne(10);continue;}int n=pipe.Read(b,pos,Math.Min(length-pos,(int)available));if(n==0)throw new IOException("Discord disconnected");pos+=n;}return b;}
    private bool Receive(int timeout){
        uint available;if(!PeekNamedPipe(pipe.SafePipeHandle,IntPtr.Zero,0,IntPtr.Zero,out available,IntPtr.Zero))throw new IOException("Discord disconnected");
        if(available==0&&timeout==0)return false;
        byte[] h=ReadExact(8,Math.Max(timeout,500));uint op=BitConverter.ToUInt32(h,0);int size=BitConverter.ToInt32(h,4);if(size<0||size>1024*1024)throw new IOException("Invalid IPC frame");string payload=Encoding.UTF8.GetString(ReadExact(size,1000));
        if(op==3){Frame(4,payload);return true;}if(op==2)throw new IOException("Discord closed IPC");if(op!=1)return true;
        var response=json.Deserialize<Dictionary<string,object>>(payload);string evt=response.ContainsKey("evt")?Convert.ToString(response["evt"]):"";
        string cmd=response.ContainsKey("cmd")?Convert.ToString(response["cmd"]):"";
        if(evt=="READY"){ready=true;Status(Loc.T("Bağlandı"));}
        else if(evt=="ERROR"){
            var data=response.ContainsKey("data")?response["data"] as Dictionary<string,object>:null;
            string message=data!=null&&data.ContainsKey("message")?Convert.ToString(data["message"]):Loc.T("RPC hatası");
            Status(Loc.T("Discord hatası: ")+message);
            if(cmd=="SET_ACTIVITY"&&!withoutArt){withoutArt=true;lastActivity="";nextSend=DateTime.UtcNow.AddSeconds(5);} // text presence survives an asset rejection
        }else if(cmd=="SET_ACTIVITY"){
            Status(published?Loc.T("Etkinlik yayında"):Loc.T("Etkinlik temizlendi"));
            var data=response.ContainsKey("data")?response["data"] as Dictionary<string,object>:null;
            if(data!=null){var safe=new Dictionary<string,object>();foreach(string k in new[]{"name","application_id","details","state","assets","timestamps"})if(data.ContainsKey(k))safe[k]=data[k];Files.Atomic(Path.Combine(Files.Engine,"discord_yayindaki_etkinlik.json"),json.Serialize(safe));}
        }
        return true;
    }
    private void Connect(){for(int i=0;i<10;i++){var p=new NamedPipeClientStream(".",(Environment.GetEnvironmentVariable("PATRIOTS_RPC_TEST_PIPE")??("discord-ipc-"+i)),PipeDirection.InOut,PipeOptions.None);try{p.Connect(30);pipe=p;ready=false;Frame(0,"{\"v\":1,\"client_id\":\""+ApplicationId+"\"}");var time=Stopwatch.StartNew();while(!ready&&time.ElapsedMilliseconds<1500&&!stop.WaitOne(0))Receive(200);if(ready){lastActivity="";nextSend=DateTime.MinValue;return;}throw new IOException("Discord handshake timed out");}catch{p.Dispose();pipe=null;}}Status(Loc.T("Discord masaüstü uygulaması bekleniyor"));}
    private Dictionary<string,string> gameTexts;
    private string GameText(string key,string fallback){
        if(gameTexts==null){
            gameTexts=new Dictionary<string,string>();
            try{
                string name=gameLanguage=="tr"?"installed_turkish.json":"metal_gear_solid_touch_english.json";
                var doc=json.Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(Files.Root,"Localization",name),Encoding.UTF8));
                foreach(object item in (System.Collections.IEnumerable)doc["entries"]){var row=item as Dictionary<string,object>;if(row!=null)gameTexts[Convert.ToString(row["id"])]=Convert.ToString(row["text"]);}
            }catch{}
        }
        string value;return gameTexts.TryGetValue(key,out value)?value.Trim(' ','-','\r','\n'):fallback;
    }
    private string Activity(Preferences settings){
        bool en=gameLanguage=="en";
        string state=en?"Starting game":"Oyun başlatılıyor",details="Metal Gear Solid Touch · Patriots";
        try{
            string file=Path.Combine(Files.Engine,"patriots_state.json");
            if((DateTime.UtcNow-File.GetLastWriteTimeUtc(file)).TotalSeconds<8){
                var d=json.Deserialize<Dictionary<string,object>>(File.ReadAllText(file,Encoding.UTF8));
                if(Convert.ToInt32(d["pid"])==pid){
                    int flags=Convert.ToInt32(d["flags"]),mission=Convert.ToInt32(d["mission"]),scene=Convert.ToInt32(d["scene"]);
                    state=(flags&2)!=0?(en?"Paused":"Duraklatıldı"):(flags&1)!=0?(en?"In mission":"Görevde"):(flags&8)!=0?(en?"Main menu":"Ana menü"):scene==6?(en?"Reading story":"Hikâye"):scene==5?(en?"Mission select":"Görev seçimi"):scene==17?(en?"Controls guide":"Kontrol kılavuzu"):(en?"Loading…":"Yükleniyor…");
                    if(settings.DiscordRoom&&(flags&3)!=0&&mission>=1&&mission<=20){
                        var stages=json.Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(Files.Root,"Localization","stages.json"),Encoding.UTF8));
                        var stage=stages[mission.ToString()] as Dictionary<string,object>;
                        string title=GameText((385+8*(mission-1)).ToString(),stage==null?"":Convert.ToString(stage["title"]));
                        details=(en?"Mission ":"Görev ")+mission+" / 20 · "+title;
                    }
                }
            }
        }catch{}
        var a=new Dictionary<string,object>{{"type",0},{"details",details},{"state",state},{"timestamps",new {start=started}},{"instance",false}};
        if(!withoutArt)a["assets"]=new Dictionary<string,string>{{"large_image","https://www.patriotsceviri.com.tr/logo.jpg"},{"large_text","Metal Gear Solid Touch · Patriots PC"}};
        a["buttons"]=new[]{new{label="Patriots Çeviri",url="https://www.patriotsceviri.com.tr/"}};
        return json.Serialize(a);
    }
    private void SetActivity(string activity){if(Environment.GetEnvironmentVariable("MGS_RPC_TRACE")=="1")File.AppendAllText(Path.Combine(Files.Engine,"discord_test_kayitlari.jsonl"),activity+Environment.NewLine,Encoding.UTF8);Frame(1,"{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":"+pid+",\"activity\":"+activity+"},\"nonce\":\"patriots-"+(++nonce)+"\"}");published=activity!="null";}
    private void Run(){try{while(!stop.WaitOne(0)){
        try{if(pipe!=null&&ready){for(int i=0;i<8&&Receive(0);i++){}}var settings=Preferences.Load();if(!settings.DiscordPresence){if(pipe!=null&&ready&&published){SetActivity("null");lastActivity="";nextSend=DateTime.MinValue;}Status(Loc.T("Kapalı"));}
        else{if(pipe==null)Connect();if(pipe!=null&&ready){string activity=Activity(settings);if(activity!=lastActivity&&DateTime.UtcNow>=nextSend){SetActivity(activity);lastActivity=activity;nextSend=DateTime.UtcNow.AddSeconds(5);}}}
        }catch{if(pipe!=null)pipe.Dispose();pipe=null;ready=false;published=false;Status(Loc.T("Bağlantı yeniden deneniyor"));}
        stop.WaitOne(pipe==null?2000:250);
    }}finally{try{if(pipe!=null&&ready&&published)SetActivity("null");}catch{}if(pipe!=null)pipe.Dispose();Status(Loc.T("Oyun kapandı · etkinlik temizlendi"));}}
    public void Dispose(){stop.Set();if(!worker.Join(2000)){try{if(pipe!=null)pipe.Dispose();}catch{}worker.Join(1000);}stop.Dispose();}
}
