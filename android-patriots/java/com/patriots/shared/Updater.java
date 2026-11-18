package com.patriots.shared;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.net.Uri;
import android.provider.Settings;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.RandomAccessFile;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicBoolean;

public final class Updater {
    private final HomeActivity activity;
    private final AtomicBoolean busy=new AtomicBoolean();
    private boolean pendingInstall;
    Updater(HomeActivity a){activity=a;}
    static HttpURLConnection connect(String value)throws Exception {return connect(value,null);}
    static HttpURLConnection connect(String value,String range)throws Exception {
        URL url=new URL(value);if(!"https".equals(url.getProtocol()))throw new SecurityException("HTTPS required");
        HttpURLConnection c=(HttpURLConnection)url.openConnection();c.setConnectTimeout(12000);c.setReadTimeout(30000);c.setRequestProperty("User-Agent","Patriots-Android-Updater");c.setRequestProperty("Accept","application/vnd.github+json");
        if(range!=null){c.setRequestProperty("Range",range);c.setRequestProperty("Accept","application/octet-stream");}
        if(c.getResponseCode()!=(range==null?200:206)){int code=c.getResponseCode();c.disconnect();throw new java.io.IOException("HTTP "+code);}
        if(!"https".equals(c.getURL().getProtocol())){c.disconnect();throw new SecurityException("Unsafe redirect");}return c;
    }
    static byte[] bytes(String url,int limit)throws Exception {HttpURLConnection c=connect(url);try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1){if(out.size()+n>limit)throw new java.io.IOException("Response too large");out.write(b,0,n);}return out.toByteArray();}finally{c.disconnect();}}
    void check(boolean manual){if(!busy.compareAndSet(false,true))return;new Thread(()->{
        try{
            JSONArray releases=new JSONArray(new String(bytes("https://api.github.com/repos/TheAti1/"+activity.repository()+"/releases?per_page=100",4*1024*1024),"UTF-8"));
            JSONObject selected=null,asset=null;int version=activity.versionCode();
            for(int i=0;i<releases.length();i++){
                JSONObject r=releases.getJSONObject(i);if(r.optBoolean("draft")||r.optBoolean("prerelease"))continue;
                int code=UpdatePolicy.versionCode(r.optString("tag_name"));if(code<=version)continue;
                JSONArray assets=r.getJSONArray("assets");for(int j=0;j<assets.length();j++){JSONObject a=assets.getJSONObject(j);if(activity.apkName().equals(a.optString("name"))&&"uploaded".equals(a.optString("state"))&&UpdatePolicy.assetUrl(a.optString("browser_download_url"),activity.repository(),activity.apkName())){version=code;selected=r;asset=a;break;}}
            }
            if(selected==null){if(manual)activity.runOnUiThread(()->activity.message(activity.t("Güncel sürümü kullanıyorsun.","You are up to date.")));return;}
            final JSONObject release=selected,download=asset;final int code=version;
            activity.runOnUiThread(()->{if(activity.isFinishing())return;new AlertDialog.Builder(activity).setTitle(activity.t("Güncelleme hazır","Update available")).setMessage(release.optString("tag_name")+"\n\n"+activity.t("Oyun kayıtların ve ayarların korunur. İndirmek ister misin?","Your saves and settings will be kept. Download the update?"))
                .setPositiveButton(activity.t("İndir","Download"),(d,w)->download(release,download,code)).setNegativeButton(activity.t("Daha sonra","Later"),null).show();});
        }catch(Exception e){android.util.Log.w("PatriotsUpdate","Update check: "+e);if(manual)activity.runOnUiThread(()->activity.message(activity.t("Güncelleme kontrol edilemedi. İnternet bağlantını kontrol edip tekrar dene.","Could not check for updates. Check your connection and try again.")));}
        finally{busy.set(false);}
    },"Patriots update check").start();}
    private void download(JSONObject release,JSONObject asset,int expectedVersion){if(!busy.compareAndSet(false,true))return;
        ProgressDialog progress=new ProgressDialog(activity);progress.setTitle(activity.t("Güncelleme indiriliyor","Downloading update"));progress.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);progress.setMax(100);progress.setCancelable(false);progress.show();
        new Thread(()->{File part=new File(activity.getCacheDir(),"patriots-update.part");
            try{
                long size=asset.getLong("size");if(size<100000||size>1024L*1024*1024)throw new SecurityException("Invalid APK size");
                String expected=asset.optString("digest","");if(expected.startsWith("sha256:"))expected=expected.substring(7);else{
                    String sidecar=null;JSONArray list=release.getJSONArray("assets");for(int i=0;i<list.length();i++){JSONObject a=list.getJSONObject(i);if((activity.apkName()+".sha256").equals(a.optString("name"))&&UpdatePolicy.assetUrl(a.optString("browser_download_url"),activity.repository(),activity.apkName()+".sha256"))sidecar=a.getString("browser_download_url");}
                    if(sidecar==null)throw new SecurityException("Missing release checksum");expected=new String(bytes(sidecar,4096),"UTF-8").trim().split("\\s+")[0];
                }
                if(!UpdatePolicy.digest(expected))throw new SecurityException("Invalid checksum");
                String url=asset.getString("browser_download_url");if(!UpdatePolicy.assetUrl(url,activity.repository(),activity.apkName()))throw new SecurityException("Wrong update source");
                long total=0;int previous=-1;
                if(part.exists()&&!part.delete())throw new java.io.IOException("Cannot reset update cache");
                try(RandomAccessFile out=new RandomAccessFile(part,"rw")){
                    while(total<size){
                        boolean complete=false;
                        for(int attempt=0;attempt<4&&!complete;attempt++){
                            long start=total,end=Math.min(size-1,start+4L*1024*1024-1);HttpURLConnection c=null;
                            try{
                                c=connect(url,"bytes="+start+"-"+end);
                                String range="bytes "+start+"-"+end+"/"+size;
                                if(!range.equals(c.getHeaderField("Content-Range")))throw new SecurityException("Invalid update range");
                                out.seek(start);
                                try(InputStream in=c.getInputStream()){
                                    byte[] b=new byte[65536];int n;
                                    while((n=in.read(b))!=-1){if(total+n>end+1)throw new SecurityException("Unexpected range size");out.write(b,0,n);total+=n;int percent=(int)(total*100/size);if(percent!=previous){previous=percent;activity.runOnUiThread(()->progress.setProgress(percent));}}
                                }
                                if(total!=end+1)throw new java.io.IOException("Incomplete update range");
                                complete=true;
                            }catch(java.io.IOException e){if(attempt==3)throw e;android.util.Log.w("PatriotsUpdate","Retrying APK download at "+total,e);}
                            finally{if(c!=null)c.disconnect();}
                        }
                    }
                    out.getFD().sync();
                }
                activity.runOnUiThread(()->progress.setTitle(activity.t("Güncelleme doğrulanıyor","Verifying update")));
                MessageDigest hash=MessageDigest.getInstance("SHA-256");
                try(InputStream in=new FileInputStream(part)){byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)hash.update(b,0,n);}
                if(total!=size||!hex(hash.digest()).equalsIgnoreCase(expected))throw new SecurityException("Update checksum mismatch");
                verify(part,expectedVersion);
                File ready=new File(activity.getCacheDir(),"patriots-update.apk");if(ready.exists()&&!ready.delete())throw new java.io.IOException("Cannot replace update cache");if(!part.renameTo(ready))throw new java.io.IOException("Cannot store verified update");
                activity.runOnUiThread(()->{progress.dismiss();install();});
            }catch(Exception e){part.delete();android.util.Log.e("PatriotsUpdate","Download failed",e);activity.runOnUiThread(()->{progress.dismiss();activity.message(activity.t("Güncelleme indirilemedi veya doğrulanamadı. Mevcut oyun korunuyor; tekrar deneyebilirsin.","The update could not be downloaded or verified. Your current game is unchanged; you can try again."));});}
            finally{busy.set(false);}
        },"Patriots APK download").start();
    }
    static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format("%02x",v&255));return s.toString();}
    private void verify(File file,int expectedVersion)throws Exception {
        PackageManager pm=activity.getPackageManager();PackageInfo old=pm.getPackageInfo(activity.getPackageName(),PackageManager.GET_SIGNING_CERTIFICATES),next=pm.getPackageArchiveInfo(file.getPath(),PackageManager.GET_SIGNING_CERTIFICATES);
        if(next==null||!activity.getPackageName().equals(next.packageName)||next.getLongVersionCode()!=expectedVersion||next.getLongVersionCode()<=old.getLongVersionCode())throw new SecurityException("Wrong app/version");
        if(old.signingInfo==null||next.signingInfo==null)throw new SecurityException("Missing APK signatures");
        Signature[] a=old.signingInfo.getApkContentsSigners(),b=next.signingInfo.getApkContentsSigners();if(a.length!=b.length)throw new SecurityException("Signing identity changed");
        for(Signature signature:a){boolean found=false;for(Signature candidate:b)found|=Arrays.equals(signature.toByteArray(),candidate.toByteArray());if(!found)throw new SecurityException("Update signed by another key");}
    }
    private void install(){
        if(!activity.getPackageManager().canRequestPackageInstalls()){
            pendingInstall=true;new AlertDialog.Builder(activity).setTitle(activity.t("Kurulum izni","Installation permission")).setMessage(activity.t("Android, bu oyunun güncelleme kurabilmesi için bir kez izin istiyor. Açılan ekranda izin verip geri dön.","Android needs permission once to install updates from this app. Allow it on the next screen, then return."))
                .setPositiveButton(activity.t("Ayarları aç","Open settings"),(d,w)->activity.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+activity.getPackageName())))).setNegativeButton(activity.t("İptal","Cancel"),(d,w)->pendingInstall=false).show();return;
        }
        pendingInstall=false;Uri uri=Uri.parse("content://"+activity.getPackageName()+".updates/update.apk");Intent intent=new Intent(Intent.ACTION_VIEW).setDataAndType(uri,"application/vnd.android.package-archive").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);activity.startActivity(intent);
    }
    void onResume(){if(pendingInstall&&activity.getPackageManager().canRequestPackageInstalls())install();}
}
