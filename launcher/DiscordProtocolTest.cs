// SPDX-License-Identifier: MIT
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

internal static class DiscordProtocolTest {
    static byte[] Exact(Stream s,int n){byte[] b=new byte[n];int p=0;while(p<n){int k=s.Read(b,p,n-p);if(k==0)throw new EndOfStreamException();p+=k;}return b;}
    static Tuple<uint,string> Read(Stream s){var h=Exact(s,8);int n=BitConverter.ToInt32(h,4);if(n<0||n>1000000)throw new InvalidDataException();return Tuple.Create(BitConverter.ToUInt32(h,0),Encoding.UTF8.GetString(Exact(s,n)));}
    static void Send(Stream s,uint op,string text){byte[] b=Encoding.UTF8.GetBytes(text);s.Write(BitConverter.GetBytes(op),0,4);s.Write(BitConverter.GetBytes(b.Length),0,4);s.Write(b,0,b.Length);s.Flush();}
    public static int Run(){
        string testLanguage=Environment.GetEnvironmentVariable("PATRIOTS_RPC_TEST_LANGUAGE")??"en";
        string pipeName="patriots-touch-test-"+Process.GetCurrentProcess().Id,statePath=Path.Combine(Files.Engine,"patriots_state.json");
        string settingsPath=Path.Combine(Files.Root,"settings.json");
        byte[] priorState=File.Exists(statePath)?File.ReadAllBytes(statePath):null,priorSettings=File.Exists(settingsPath)?File.ReadAllBytes(settingsPath):null;
        Directory.CreateDirectory(Files.Engine);
        try{
            var prefs=Preferences.Load();prefs.DiscordPresence=true;prefs.DiscordRoom=true;prefs.Save();
            Files.Atomic(statePath,Files.Json.Serialize(new{pid=Process.GetCurrentProcess().Id,flags=1,scene=8,mission=1,phase=0}));
            Environment.SetEnvironmentVariable("PATRIOTS_RPC_TEST_PIPE",pipeName);
            var observed=new List<string>();
            using(var server=new NamedPipeServerStream(pipeName,PipeDirection.InOut,1,PipeTransmissionMode.Byte,PipeOptions.Asynchronous,65536,65536)){
                var task=Task.Run(()=>{
                    server.WaitForConnection();var handshake=Read(server);
                    if(handshake.Item1!=0||!handshake.Item2.Contains("1572290325937004574"))throw new Exception("Wrong Discord application ID");
                    observed.Add("handshake");Files.Log("RPC TEST handshake received");Send(server,1,"{\"evt\":\"READY\",\"data\":{}}");
                    Send(server,3,"heartbeat-test");
                    bool activity=false,heartbeat=false,cleared=false;
                    while(!cleared){var frame=Read(server);Files.Log("RPC TEST frame opcode="+frame.Item1+" payload="+frame.Item2);if(frame.Item1==4){heartbeat=frame.Item2=="heartbeat-test";observed.Add("heartbeat");continue;}
                        if(frame.Item1!=1)continue;
                        var d=Files.Json.Deserialize<Dictionary<string,object>>(frame.Item2);
                        if(Convert.ToString(d["cmd"])!="SET_ACTIVITY")continue;
                        var a=d["args"] as Dictionary<string,object>;
                        if(a["activity"]==null){cleared=true;observed.Add("cleared");}
                        else{var data=a["activity"] as Dictionary<string,object>;string detail=Convert.ToString(data["details"]);if(!detail.Contains(TouchLanguagePacks.GameL("Görev ","Mission ",testLanguage)+"1 / 20")||Convert.ToString(data["state"])!=TouchLanguagePacks.GameL("Görevde","In mission",testLanguage))throw new Exception("Mission activity missing");activity=true;observed.Add("mission");}
                        if(!cleared)Send(server,1,"{\"cmd\":\"SET_ACTIVITY\",\"evt\":null,\"data\":{}}");
                    }
                    if(!activity||!heartbeat)throw new Exception("Missing activity or heartbeat");
                });
                using(var presence=new DiscordPresence(Process.GetCurrentProcess().Id,testLanguage)){
                    var timer=Stopwatch.StartNew();while(timer.ElapsedMilliseconds<5000){lock(observed){if(observed.Contains("mission")&&observed.Contains("heartbeat"))break;}Thread.Sleep(25);}
                }
                if(!task.Wait(6000))throw new TimeoutException("Discord protocol test timed out");
            }
            string qa=Path.Combine(Files.Root,"QA");Directory.CreateDirectory(qa);Files.Atomic(Path.Combine(qa,"discord_protocol_test.json"),Files.Json.Serialize(new{passed=true,application_id="1572290325937004574",checks=observed.ToArray()}));
            return 0;
        }finally{
            Environment.SetEnvironmentVariable("PATRIOTS_RPC_TEST_PIPE",null);
            if(priorState==null){if(File.Exists(statePath))File.Delete(statePath);}else File.WriteAllBytes(statePath,priorState);
            if(priorSettings==null){if(File.Exists(settingsPath))File.Delete(settingsPath);}else File.WriteAllBytes(settingsPath,priorSettings);
        }
    }
}
