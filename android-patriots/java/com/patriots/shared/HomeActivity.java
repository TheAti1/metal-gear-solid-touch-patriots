package com.patriots.shared;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public final class HomeActivity extends Activity {
    private SharedPreferences preferences;
    private Updater updater;
    private boolean touch;
    private LinearLayout content;
    private final int background=Color.rgb(12,18,16),panel=Color.rgb(24,34,28),accent=Color.rgb(174,209,113),ink=Color.rgb(235,240,230);
    protected void onCreate(Bundle state){super.onCreate(state);touch=getPackageName().endsWith("mgstouch");preferences=getSharedPreferences("patriots",MODE_PRIVATE);updater=new Updater(this);getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,WindowManager.LayoutParams.FLAG_FULLSCREEN);build();if(preferences.getBoolean("updates",true))updater.check(false);}
    protected void onResume(){super.onResume();if(updater!=null)updater.onResume();}
    String repository(){return touch?"metal-gear-solid-touch-patriots":"metal-gear-solid-mobile-patriots";}
    String apkName(){return touch?"MGS_Touch_Patriots_Android.apk":"MGS_Mobile_Patriots_Android.apk";}
    int versionCode(){try{return (int)getPackageManager().getPackageInfo(getPackageName(),0).getLongVersionCode();}catch(Exception e){return 0;}}
    public static String locale(android.content.Context context){return context.getSharedPreferences("patriots",MODE_PRIVATE).getString("language","tr");}
    String t(String tr,String en){return "tr".equals(locale(this))?tr:en;}
    int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
    private TextView text(String s,int size,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(color);v.setPadding(0,dp(8),0,dp(8));return v;}
    private void button(String label,Runnable action,boolean primary){Button b=new Button(this);b.setText(label);b.setTextSize(15);b.setAllCaps(false);b.setTextColor(primary?background:ink);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(primary?accent:panel));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(58));lp.topMargin=dp(10);content.addView(b,lp);b.setOnClickListener(v->action.run());}
    private void build(){
        ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(background);content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);content.setPadding(dp(28),dp(30),dp(28),dp(32));scroll.addView(content);setContentView(scroll);
        LinearLayout brand=new LinearLayout(this);brand.setGravity(Gravity.CENTER_VERTICAL);
        try{ImageView logo=new ImageView(this);logo.setImageDrawable(android.graphics.drawable.Drawable.createFromStream(getAssets().open("patriots.jpg"),null));brand.addView(logo,new LinearLayout.LayoutParams(dp(54),dp(54)));}catch(Exception ignored){}
        TextView name=text("  PATRIOTS",22,accent);name.setTypeface(null,Typeface.BOLD);brand.addView(name);content.addView(brand);
        content.addView(text("METAL GEAR SOLID\n"+(touch?"TOUCH":"MOBILE"),32,ink));
        content.addView(text(t("Göreve hazır mısın?","Ready for the mission?"),17,accent));
        content.addView(text(t("Dokunmatik ekran ve oyun kumandası desteği.\nKayıtların uygulama güncellemelerinde korunur.","Touchscreen and controller support.\nYour saves are preserved when updating the app."),14,Color.rgb(155,171,158)));
        button(t("OYNA","PLAY"),this::play,true);
        button(t("Dil: ","Language: ")+("tr".equals(locale(this))?"Türkçe":"English"),()->new AlertDialog.Builder(this).setTitle(t("Oyun dili","Game language")).setSingleChoiceItems(new String[]{"Türkçe","English"},"tr".equals(locale(this))?0:1,(d,w)->{preferences.edit().putString("language",w==0?"tr":"en").apply();d.dismiss();build();}).setNegativeButton(t("Kapat","Close"),null).show(),false);
        button(t("Görüntü ve kontroller","Display and controls"),this::settings,false);
        button(t("Güncellemeleri kontrol et","Check for updates"),()->updater.check(true),false);
        Switch updates=new Switch(this);updates.setText(t("Açılışta güncelleme kontrolü","Check for updates at startup"));updates.setTextColor(ink);updates.setPadding(0,dp(20),0,dp(14));updates.setChecked(preferences.getBoolean("updates",true));updates.setOnCheckedChangeListener((b,v)->preferences.edit().putBoolean("updates",v).apply());content.addView(updates);
        content.addView(text(t("Güncelleme yüklerken Android kurulum onayı ister.","Android asks for confirmation before installing an update."),12,Color.rgb(145,160,149)));
        button("Patriots Çeviri ↗",()->startActivity(new Intent(Intent.ACTION_VIEW,android.net.Uri.parse("https://www.patriotsceviri.com.tr/"))),false);
        String version="";try{version=getPackageManager().getPackageInfo(getPackageName(),0).versionName;}catch(Exception ignored){}content.addView(text("ANDROID 9+ · "+version,11,Color.rgb(128,145,132)));
    }
    private void settings(){String[] choices={t("Kalite: Dengeli","Quality: Balanced"),t("Kalite: Yüksek","Quality: High"),touch?t("Titreşim","Vibration"):t("Sanal tuşların görünürlüğü","Touch-button opacity")};new AlertDialog.Builder(this).setTitle(t("Görüntü ve kontroller","Display and controls")).setItems(choices,(d,w)->{
        if(w<2){preferences.edit().putBoolean("high",w==1).apply();message(t("Sonraki oyun açılışına uygulanacak.","Applies on the next game launch."));}
        else if(touch){boolean old=preferences.getBoolean("vibration",true);preferences.edit().putBoolean("vibration",!old).apply();message(!old?t("Titreşim açık","Vibration on"):t("Titreşim kapalı","Vibration off"));}
        else new AlertDialog.Builder(this).setTitle(t("Sanal tuşlar","Touch buttons")).setSingleChoiceItems(new String[]{"40%","60%","80%","100%"},preferences.getInt("opacity",1),(x,i)->{preferences.edit().putInt("opacity",i).apply();x.dismiss();}).setNegativeButton(t("Kapat","Close"),null).show();
    }).setNegativeButton(t("Kapat","Close"),null).show();}
    void message(String value){if(!isFinishing())new AlertDialog.Builder(this).setMessage(value).setPositiveButton(t("Tamam","OK"),null).show();}
    private File mobileRoot(){File root=getExternalFilesDir(null);return root!=null?root:getFilesDir();}
    private static void config(File file,Map<String,String> changes)throws Exception {
        Map<String,String> values=new LinkedHashMap<>();if(file.isFile()){try(java.io.BufferedReader in=new java.io.BufferedReader(new java.io.InputStreamReader(new FileInputStream(file),StandardCharsets.UTF_8))){String line;while((line=in.readLine())!=null){int at=line.indexOf('=');if(at>0&&!line.startsWith("#"))values.put(line.substring(0,at),line.substring(at+1));}}}
        values.putAll(changes);StringBuilder text=new StringBuilder();for(Map.Entry<String,String> pair:values.entrySet())text.append(pair.getKey()).append('=').append(pair.getValue()).append('\n');file.getParentFile().mkdirs();File temp=new File(file+".tmp");try(FileOutputStream out=new FileOutputStream(temp)){out.write(text.toString().getBytes(StandardCharsets.UTF_8));out.getFD().sync();}if(!temp.renameTo(file))throw new java.io.IOException("Cannot save game settings");
    }
    private void prepareMobile()throws Exception {
        File root=mobileRoot(),marker=new File(root,"patriots-assets.version");String current="";if(marker.isFile())try(FileInputStream in=new FileInputStream(marker)){byte[] b=new byte[32];int n=in.read(b);if(n>0)current=new String(b,0,n,StandardCharsets.UTF_8);}
        if(!current.equals(String.valueOf(versionCode()))||!new File(root,"game/mgs_ngi").isFile()){
            String prefix=root.getCanonicalPath()+File.separator;
            try(ZipInputStream zip=new ZipInputStream(getAssets().open("gamepack.zip"))){ZipEntry e;byte[] buffer=new byte[65536];long total=0;while((e=zip.getNextEntry())!=null){File output=new File(root,e.getName());if(!output.getCanonicalPath().startsWith(prefix)||e.getName().contains("..")||e.getName().contains("\\")||e.getName().toLowerCase(java.util.Locale.ROOT).contains("savedata"))throw new SecurityException("Invalid bundled asset path");if(e.isDirectory()){output.mkdirs();continue;}output.getParentFile().mkdirs();File temp=new File(output+".new");try(FileOutputStream out=new FileOutputStream(temp)){int n;while((n=zip.read(buffer))!=-1){total+=n;if(total>256L*1024*1024)throw new java.io.IOException("Bundled assets too large");out.write(buffer,0,n);}}if(!temp.renameTo(output))throw new java.io.IOException("Cannot install bundled game data");}}
            try(FileOutputStream out=new FileOutputStream(marker)){out.write(String.valueOf(versionCode()).getBytes(StandardCharsets.UTF_8));}
        }
        Map<String,String> c=new LinkedHashMap<>();c.put("language",locale(this));c.put("fullscreen","1");c.put("touch_mode","2");c.put("touch_opacity",String.valueOf(40+preferences.getInt("opacity",1)*20));c.put("debug_mode","0");c.put("cheat_infinite_health","0");c.put("cheat_infinite_ammo","0");c.put("dynamic_prompts","1");c.put("crisp_ui","1");c.put("msaa",preferences.getBoolean("high",false)?"4":"0");c.put("supersample","1");c.put("texture_filtering",preferences.getBoolean("high",false)?"1":"0");c.put("native_resolution","0");c.put("skip_intro","1");c.put("custom_textures","0");config(new File(root,"mgs_mobile.ini"),c);
    }
    private void prepareTouch()throws Exception {
        Map<String,String> c=new LinkedHashMap<>();c.put("language","0");c.put("sharp_rendering",preferences.getBoolean("high",false)?"1":"0");c.put("vibration",preferences.getBoolean("vibration",true)?"1":"0");c.put("skip_intro","1");c.put("cheat_infinite_life","0");c.put("cheat_one_hit_kills","0");c.put("cheat_open_all_missions","0");c.put("cheat_open_all_wallpapers","0");config(new File(getFilesDir(),"Documents/retouched.cfg"),c);
    }
    private void play(){
        ProgressDialog progress=ProgressDialog.show(this,"PATRIOTS",t("Oyun hazırlanıyor…","Preparing game…"),true,false);
        new Thread(()->{try{if(touch)prepareTouch();else prepareMobile();runOnUiThread(()->{progress.dismiss();Intent game=new Intent();game.setClassName(this,touch?"com.mgsport.retouched.RetouchedActivity":"org.mgsmobile.port.MGSActivity");game.putExtra("patriots_language",locale(this));startActivity(game);});}
            catch(Exception e){android.util.Log.e("Patriots","Launch preparation failed",e);runOnUiThread(()->{progress.dismiss();message(t("Oyun hazırlanamadı. Yeterli boş alan olduğundan emin olup tekrar dene.","Could not prepare the game. Check available storage and try again."));});}},"Patriots game setup").start();
    }
}
