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
    private int windowWidth,windowHeight;
    private boolean launching;
    private View activeRoot;
    private String activePage="home";
    private int background,panel,accent,ink,muted,line;
    protected void onCreate(Bundle state){super.onCreate(state);touch=getPackageName().endsWith("mgstouch");preferences=getSharedPreferences("patriots",MODE_PRIVATE);updater=new Updater(this);readGameSettings();getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,WindowManager.LayoutParams.FLAG_FULLSCREEN);build();if(preferences.getBoolean("updates",true))updater.check(false);}
    protected void onResume(){super.onResume();if(preferences!=null){readGameSettings();build();}if(updater!=null&&!updater.onResume()&&preferences.getBoolean("updates",true))updater.check(false);}
    String repository(){return touch?"metal-gear-solid-touch-patriots":"metal-gear-solid-mobile-patriots";}
    String apkName(){return touch?"MGS_Touch_Patriots_Android.apk":"MGS_Mobile_Patriots_Android.apk";}
    int versionCode(){try{return (int)getPackageManager().getPackageInfo(getPackageName(),0).getLongVersionCode();}catch(Exception e){return 0;}}
    public static String locale(android.content.Context context){String id=context.getSharedPreferences("patriots",MODE_PRIVATE).getString("language","tr");return "tr".equals(id)||"en".equals(id)||"pt-br".equals(id)?id:"en";}
    String t(String tr,String en){return AndroidLocale.text(this,tr,en);}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
    private TextView text(String s,int size,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(color);v.setPadding(0,dp(5),0,dp(5));v.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_HIGH_QUALITY);return v;}
    private android.graphics.drawable.GradientDrawable surface(int color,int stroke,int radius){android.graphics.drawable.GradientDrawable d=new android.graphics.drawable.GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));if(stroke!=0)d.setStroke(dp(1),stroke);return d;}
    private TextView paragraph(String value){TextView v=text(value,13,muted);content.addView(v,new LinearLayout.LayoutParams(-1,-2));return v;}
    private Button action(String label,Runnable run,boolean primary){Button b=new Button(this);b.setText(label);b.setTextSize(13);b.setAllCaps(false);b.setMinHeight(dp(48));b.setPadding(dp(14),dp(10),dp(14),dp(10));b.setTextColor(primary?Color.rgb(24,33,29):ink);b.setBackgroundTintList(null);b.setStateListAnimator(null);b.setBackground(new android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(touch?0x44A6CB70:0x55485925),surface(primary?accent:panel,primary?0:line,4),null));b.setGravity(primary?Gravity.CENTER:Gravity.CENTER_VERTICAL|Gravity.LEFT);b.setOnClickListener(v->run.run());return b;}
    private void button(String label,Runnable run,boolean primary){LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=dp(12);content.addView(action(label,run,primary),lp);}
    private void heading(String title,String description){content.addView(text(title,26,ink));if(!description.isEmpty())paragraph(description);}
    private void choose(String label,String[] options,int selected,java.util.function.IntConsumer changed){button(label+": "+options[selected],()->new AlertDialog.Builder(this).setTitle(label).setSingleChoiceItems(options,selected,(d,i)->{changed.accept(i);d.dismiss();build();}).setNegativeButton(t("Kapat","Close"),null).show(),false);}
    private void toggle(String label,String key,boolean fallback){Switch v=new Switch(this);v.setText(label);v.setTextSize(14);v.setTextColor(ink);v.setMinHeight(dp(58));v.setPadding(0,dp(10),0,dp(10));v.setThumbTintList(new android.content.res.ColorStateList(new int[][]{new int[]{android.R.attr.state_checked},new int[]{}},new int[]{accent,muted}));v.setChecked(preferences.getBoolean(key,fallback));v.setOnCheckedChangeListener((b,on)->preferences.edit().putBoolean(key,on).apply());content.addView(v,new LinearLayout.LayoutParams(-1,-2));}
    private void slider(String title,String key,int low,int high,int fallback){TextView label=text(title+": "+preferences.getInt(key,fallback)+"%",14,ink);content.addView(label);android.widget.SeekBar bar=new android.widget.SeekBar(this);bar.setProgressTintList(android.content.res.ColorStateList.valueOf(accent));bar.setThumbTintList(android.content.res.ColorStateList.valueOf(accent));bar.setMax(high-low);bar.setProgress(Math.max(0,Math.min(high-low,preferences.getInt(key,fallback)-low)));bar.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener(){public void onStartTrackingTouch(android.widget.SeekBar s){}public void onStopTrackingTouch(android.widget.SeekBar s){}public void onProgressChanged(android.widget.SeekBar s,int value,boolean user){if(user){preferences.edit().putInt(key,value+low).apply();label.setText(title+": "+(value+low)+"%");}}});content.addView(bar,new LinearLayout.LayoutParams(-1,dp(40)));}
    private void languages(){final String[] ids={"tr","en","pt-br"};final String[] names={"Türkçe","English","Português (Brasil)"};new AlertDialog.Builder(this).setTitle(t("Oyun dili","Game language")).setSingleChoiceItems(names,java.util.Arrays.asList(ids).indexOf(locale(this)),(d,i)->{preferences.edit().putString("language",ids[i]).apply();d.dismiss();build();}).setNegativeButton(t("Kapat","Close"),null).show();}
    @Override public void onConfigurationChanged(android.content.res.Configuration next){super.onConfigurationChanged(next);windowWidth=windowHeight=0;build();}
    private void build(){
        background=Color.parseColor(touch?"#0C1210":"#EEEFE8");panel=Color.parseColor(touch?"#151C19":"#F7F8F2");accent=Color.parseColor(touch?"#A6CB70":"#D5EB72");ink=Color.parseColor(touch?"#E9ECE7":"#18211D");muted=Color.parseColor(touch?"#929D99":"#6A726B");line=Color.parseColor(touch?"#29332F":"#D0D5CA");
        int width=windowWidth>0?windowWidth:getResources().getDisplayMetrics().widthPixels,height=windowHeight>0?windowHeight:getResources().getDisplayMetrics().heightPixels;
        float density=getResources().getDisplayMetrics().density;boolean wide=AdaptiveLayout.wide((int)(width/density),(int)(height/density));
        final LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(background);root.setFitsSystemWindows(true);
        getWindow().setNavigationBarColor(background);getWindow().getDecorView().setSystemUiVisibility(touch?0:View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        LinearLayout header=new LinearLayout(this);header.setGravity(Gravity.CENTER_VERTICAL);header.setPadding(dp(wide?24:16),dp(12),dp(wide?24:16),dp(12));
        try{ImageView logo=new ImageView(this);logo.setImageDrawable(android.graphics.drawable.Drawable.createFromStream(getAssets().open("patriots.jpg"),null));android.graphics.drawable.GradientDrawable circle=surface(Color.WHITE,0,60);logo.setBackground(circle);logo.setClipToOutline(true);header.addView(logo,new LinearLayout.LayoutParams(dp(42),dp(42)));}catch(Exception ignored){}
        LinearLayout brand=new LinearLayout(this);brand.setOrientation(LinearLayout.VERTICAL);brand.setPadding(dp(10),0,dp(8),0);TextView name=text("PATRIOTS",17,ink);name.setTypeface(null,Typeface.BOLD);brand.addView(name);if(wide)brand.addView(text("METAL GEAR SOLID "+(touch?"TOUCH":"MOBILE")+" / ANDROID EDITION",9,muted));header.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        Button language=action(locale(this).equals("tr")?"Türkçe  ▾":locale(this).equals("pt-br")?"Português (Brasil)  ▾":"English  ▾",this::languages,false);language.setTextSize(12);language.setMaxWidth(dp(wide?195:160));header.addView(language,new LinearLayout.LayoutParams(-2,-2));root.addView(header,new LinearLayout.LayoutParams(-1,-2));
        String[] ids={"home","display","controls","audio","languages","saves","updates"};String[] labels={t("OYUN",touch?"OVERVIEW":"GAME"),t("GÖRÜNTÜ","DISPLAY"),t("KONTROLLER","CONTROLS"),t("SES","AUDIO"),t("DİLLER","LANGUAGES"),t("KAYITLAR","SAVES"),t("GÜNCELLEMELER","UPDATES")};
        LinearLayout navigation=new LinearLayout(this);navigation.setOrientation(touch&&wide?LinearLayout.VERTICAL:LinearLayout.HORIZONTAL);navigation.setPadding(dp(12),dp(8),dp(12),dp(8));
        for(int i=0;i<ids.length;i++){final String page=ids[i];Button tab=action(labels[i],()->{activePage=page;build();},false);tab.setTextSize(11);tab.setGravity(touch&&wide?Gravity.CENTER_VERTICAL|Gravity.LEFT:Gravity.CENTER);tab.setBackgroundTintList(null);tab.setBackground(surface(activePage.equals(page)?(touch?panel:accent):background,activePage.equals(page)?(touch?accent:0):0,3));tab.setTextColor(activePage.equals(page)&&touch?accent:ink);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(touch&&wide?-1:-2,-2);lp.bottomMargin=dp(touch&&wide?5:0);lp.rightMargin=dp(5);navigation.addView(tab,lp);}
        LinearLayout middle=new LinearLayout(this);middle.setOrientation(LinearLayout.HORIZONTAL);
        if(touch&&wide){ScrollView nav=new ScrollView(this);nav.setFillViewport(false);nav.addView(navigation);middle.addView(nav,new LinearLayout.LayoutParams(dp(174),-1));}else{android.widget.HorizontalScrollView nav=new android.widget.HorizontalScrollView(this);nav.setHorizontalScrollBarEnabled(false);nav.addView(navigation);root.addView(nav,new LinearLayout.LayoutParams(-1,-2));}
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);content.setPadding(dp(wide?26:18),dp(12),dp(wide?26:18),dp(26));scroll.addView(content,new ScrollView.LayoutParams(-1,-2));middle.addView(scroll,new LinearLayout.LayoutParams(0,-1,1));root.addView(middle,new LinearLayout.LayoutParams(-1,0,1));
        if(activePage.equals("home")){
            android.widget.FrameLayout hero=new android.widget.FrameLayout(this);try{ImageView image=new ImageView(this);image.setImageDrawable(android.graphics.drawable.Drawable.createFromStream(getAssets().open("hero"),null));image.setScaleType(ImageView.ScaleType.CENTER_CROP);hero.addView(image,new android.widget.FrameLayout.LayoutParams(-1,-1));}catch(Exception ignored){}
            View shade=new View(this);shade.setBackground(new android.graphics.drawable.GradientDrawable(android.graphics.drawable.GradientDrawable.Orientation.LEFT_RIGHT,new int[]{0xEF08120E,0xAA08120E,0x0808120E}));hero.addView(shade,new android.widget.FrameLayout.LayoutParams(-1,-1));
            LinearLayout title=new LinearLayout(this);title.setOrientation(LinearLayout.VERTICAL);title.setPadding(dp(20),dp(14),dp(12),dp(10));title.addView(text((touch?t("TAKTİK DOKUNMATİK AKSİYON","TACTICAL TOUCH ACTION"):"PATRIOTS / "+(locale(this).equals("tr")?"Türkçe":locale(this).equals("pt-br")?"Português (Brasil)":"English")),10,accent));TextView game=text("METAL GEAR SOLID\n"+(touch?"TOUCH":"MOBILE"),wide?32:26,Color.rgb(237,240,234));game.setTypeface(null,Typeface.BOLD);title.addView(game);title.addView(text(t("Göreve hazır mısın?","Ready for the mission?"),14,Color.rgb(210,220,209)));hero.addView(title,new android.widget.FrameLayout.LayoutParams(-1,-1));content.addView(hero,new LinearLayout.LayoutParams(-1,dp(wide?255:210)));
            paragraph(t("Dokunmatik ekran ve oyun kumandası desteği.\nKayıtların uygulama güncellemelerinde korunur.","Touchscreen and controller support.\nYour saves are preserved when updating the app."));
            button(t("Oyun dili","Game language")+": "+(locale(this).equals("tr")?"Türkçe":locale(this).equals("pt-br")?"Português (Brasil)":"English"),()->{activePage="languages";build();},false);
            button(t("Görüntü ve kontroller","Display and controls"),()->{activePage="display";build();},false);
        }else if(activePage.equals("display")){
            heading(t("Görüntü ayarları","Display settings"),t("Görüntü oranı korunur; oyun sahnesi genişletilmez.","The original picture keeps its aspect ratio."));
            choose(t("Kalite","Quality"),new String[]{t("Dengeli","Balanced"),t("Yüksek","High")},preferences.getBoolean("high",false)?1:0,i->preferences.edit().putBoolean("high",i==1).apply());
            if(touch)choose(t("Kenar dolgusu","Border fill"),new String[]{t("Siyah","Black"),t("Bulanık arka plan","Blurred background"),t("Koyu çerçeve","Dark frame")},Math.max(0,Math.min(2,preferences.getInt("fill",1))),i->preferences.edit().putInt("fill",i).apply());
            else toggle(t("Geniş ekran","Widescreen"),"wide",true);
            paragraph(t("Sonraki oyun açılışına uygulanacak.","Applies on the next game launch."));
        }else if(activePage.equals("controls")){
            heading(t("Kontroller","Controls"),t("Dokunmatik ekran ve oyun kumandası","Touchscreen and controller"));
            if(touch){paragraph(t("Sürükle: nişan al. Dokun: ateş et. İki parmak: yakınlaştır / uzaklaştır.","Drag to aim. Tap to fire. Pinch with two fingers to zoom."));slider(t("Nişan hassasiyeti","Aim sensitivity"),"aim",50,200,100);toggle(t("Titreşim","Vibration"),"vibration",true);toggle(t("Odak kaybında duraklat","Pause on focus loss"),"pause",true);}
            else{paragraph(t("Sol yön tuşunun ortası: onayla. Sağ yuvarlak tuş: eylem / ateş.","Centre of the left direction pad: confirm. Right round button: action / fire."));choose(t("Sanal tuşların görünürlüğü","Touch-button opacity"),new String[]{"40%","60%","80%","100%"},Math.max(0,Math.min(3,preferences.getInt("opacity",1))),i->preferences.edit().putInt("opacity",i).apply());}
        }else if(activePage.equals("audio")){
            heading(t("Ses ayarları","Audio settings"),touch?t("Müzik ve efektleri ayrı ayrı ayarla.","Adjust music and sound effects separately."):t("Ses düzeyi için cihazın ses tuşlarını kullanabilirsin.","You can also use the device volume buttons."));
            if(touch){slider(t("Müzik","Music"),"music",0,100,80);slider(t("Ses efektleri","Sound effects"),"effects",0,100,100);toggle(t("Yüksek kaliteli yeniden örnekleme","High quality resampling"),"hq",true);}
            android.media.AudioManager audio=(android.media.AudioManager)getSystemService(AUDIO_SERVICE);if(audio!=null){content.addView(text(t("Cihaz ses düzeyi","Device volume"),14,ink));android.widget.SeekBar bar=new android.widget.SeekBar(this);bar.setMax(audio.getStreamMaxVolume(android.media.AudioManager.STREAM_MUSIC));bar.setProgress(audio.getStreamVolume(android.media.AudioManager.STREAM_MUSIC));bar.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener(){public void onStartTrackingTouch(android.widget.SeekBar s){}public void onStopTrackingTouch(android.widget.SeekBar s){}public void onProgressChanged(android.widget.SeekBar s,int value,boolean user){if(user)audio.setStreamVolume(android.media.AudioManager.STREAM_MUSIC,value,0);}});content.addView(bar,new LinearLayout.LayoutParams(-1,dp(48)));}
        }else if(activePage.equals("languages")){
            heading(t("Diller ve çeviri paketleri","Languages and translation packs"),t("Dil seçimi bir sonraki oyun açılışına uygulanır.","The selected game language applies on the next launch."));
            String[] idsLocale={"tr","en","pt-br"},names={"Türkçe","English","Português (Brasil)"};for(int i=0;i<idsLocale.length;i++){final String id=idsLocale[i];button((locale(this).equals(id)?"●  ":"")+names[i],()->{preferences.edit().putString("language",id).apply();build();},locale(this).equals(id));}
            credits();
        }else if(activePage.equals("saves")){
            heading(t("Kayıt yönetimi","Save management"),t("Kayıtların uygulama güncellemelerinde korunur.","Your saves are preserved when updating the app."));
            paragraph(saveFile().isFile()?t("Oyun kaydı hazır.","A saved game is available."):t("Henüz bir oyun kaydı yok.","No save file yet."));
            button(t("YEDEK AL","BACK UP"),this::exportSave,false);
        }else{
            heading(t("Güncellemeler","Updates"),"METAL GEAR SOLID "+(touch?"TOUCH":"MOBILE")+" · PATRIOTS");
            button(t("Güncellemeleri kontrol et","Check for updates"),()->updater.check(true),true);toggle(t("Açılışta güncelleme kontrolü","Check for updates at startup"),"updates",true);
            paragraph(t("Güncelleme yüklerken Android kurulum onayı ister.","Android asks for confirmation before installing an update."));
            button("Patriots Çeviri ↗",()->startActivity(new Intent(Intent.ACTION_VIEW,android.net.Uri.parse("https://www.patriotsceviri.com.tr/"))),false);credits();
        }
        LinearLayout footer=new LinearLayout(this);footer.setGravity(Gravity.CENTER_VERTICAL);footer.setPadding(dp(18),dp(10),dp(18),dp(10));footer.setBackground(surface(touch?panel:Color.rgb(229,234,220),line,0));String version="";try{version=getPackageManager().getPackageInfo(getPackageName(),0).versionName;}catch(Exception ignored){}TextView status=text(t("● HAZIR","● READY")+"\nANDROID · "+version,11,muted);footer.addView(status,new LinearLayout.LayoutParams(0,-2,1));Button play=action(t("OYNA","PLAY")+"  →",this::play,true);footer.addView(play,new LinearLayout.LayoutParams(dp(wide?185:148),-2));root.addView(footer,new LinearLayout.LayoutParams(-1,-2));
        activeRoot=root;setContentView(root);root.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{int w=r-l,h=b-t;if(w>0&&h>0&&(w!=windowWidth||h!=windowHeight)){windowWidth=w;windowHeight=h;root.post(()->{if(!isFinishing()&&!isDestroyed()&&activeRoot==root)build();});}});
    }
    private void readGameSettings(){
        File file=touch?new File(getFilesDir(),"Documents/retouched.cfg"):new File(mobileRoot(),"mgs_mobile.ini");
        if(!file.isFile()||preferences.getLong("settings_mtime",-1)==file.lastModified())return;
        try(java.io.BufferedReader in=new java.io.BufferedReader(new java.io.InputStreamReader(new FileInputStream(file),StandardCharsets.UTF_8))){
            Map<String,String> values=new LinkedHashMap<>();String row;while((row=in.readLine())!=null){int at=row.indexOf('=');if(at>0)values.put(row.substring(0,at).trim(),row.substring(at+1).trim());}
            SharedPreferences.Editor edit=preferences.edit();
            String[][] keys=touch?new String[][]{{"fill","screen_fill","0","2"},{"aim","aim_sensitivity","50","200"},{"music","music_volume","0","100"},{"effects","effects_volume","0","100"}}:new String[0][];
            for(String[] k:keys)if(values.containsKey(k[1]))try{int n=Integer.parseInt(values.get(k[1]));edit.putInt(k[0],Math.max(Integer.parseInt(k[2]),Math.min(Integer.parseInt(k[3]),n)));}catch(NumberFormatException ignored){}
            String[][] bools=touch?new String[][]{{"high","sharp_rendering"},{"hq","hq_resampling"},{"pause","pause_on_leave"},{"vibration","vibration"}}:new String[][]{{"wide","arbitrary_resolution"}};
            for(String[] k:bools)if(values.containsKey(k[1]))edit.putBoolean(k[0],!values.get(k[1]).equals("0"));
            edit.putLong("settings_mtime",file.lastModified()).apply();
        }catch(Exception e){android.util.Log.w("Patriots","Could not read previous game settings",e);}
    }
    private void credits(){String author=AndroidLocale.author(this);if(!author.isEmpty()){TextView credit=paragraph("Português (Brasil)\n"+author);android.text.util.Linkify.addLinks(credit,android.text.util.Linkify.WEB_URLS);credit.setLinkTextColor(touch?accent:Color.rgb(88,107,50));}}
    private File saveFile(){if(touch)return new File(getFilesDir(),"Documents/SAVE.data");File a=new File(mobileRoot(),"game/data/savedata.i3d"),b=new File(mobileRoot(),"game/data/savedata2.i3d");return b.isFile()&&(!a.isFile()||b.lastModified()>a.lastModified())?b:a;}
    private void exportSave(){if(!saveFile().isFile()){message(t("Kayıt bulunamadı.","No save found."));return;}Intent pick=new Intent(Intent.ACTION_CREATE_DOCUMENT);pick.addCategory(Intent.CATEGORY_OPENABLE);pick.setType("application/octet-stream");pick.putExtra(Intent.EXTRA_TITLE,touch?"MGS_Touch_SAVE.data":"MGS_Mobile_savedata.i3d");startActivityForResult(pick,70);}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==70&&result==RESULT_OK&&data!=null&&data.getData()!=null){try(InputStream in=new FileInputStream(saveFile());java.io.OutputStream out=getContentResolver().openOutputStream(data.getData())){if(out==null)throw new java.io.IOException();byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)out.write(b,0,n);message(t("Yedek oluşturuldu.","Backup created."));}catch(Exception e){message(t("Yedek oluşturulamadı.","Could not create a backup."));}}}
    void message(String value){if(!isFinishing()&&!isDestroyed())new AlertDialog.Builder(this).setMessage(value).setPositiveButton(t("Tamam","OK"),null).show();}

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
        Map<String,String> c=new LinkedHashMap<>();c.put("language",locale(this));if(preferences.contains("wide"))c.put("arbitrary_resolution",preferences.getBoolean("wide",true)?"1":"0");c.put("fullscreen","1");c.put("touch_mode","2");c.put("touch_opacity",String.valueOf(40+preferences.getInt("opacity",1)*20));c.put("debug_mode","0");c.put("cheat_infinite_health","0");c.put("cheat_infinite_ammo","0");c.put("dynamic_prompts","1");c.put("crisp_ui","1");c.put("msaa",preferences.getBoolean("high",false)?"4":"0");c.put("supersample","1");c.put("texture_filtering",preferences.getBoolean("high",false)?"1":"0");c.put("native_resolution","0");c.put("skip_intro","1");c.put("custom_textures","0");config(new File(root,"mgs_mobile.ini"),c);
    }
    private void prepareTouch()throws Exception {
        Map<String,String> c=new LinkedHashMap<>();c.put("language","0");c.put("screen_fill",String.valueOf(preferences.getInt("fill",1)));c.put("sharp_rendering",preferences.getBoolean("high",false)?"1":"0");c.put("vibration",preferences.getBoolean("vibration",true)?"1":"0");c.put("aim_sensitivity",String.valueOf(preferences.getInt("aim",100)));c.put("music_volume",String.valueOf(preferences.getInt("music",80)));c.put("effects_volume",String.valueOf(preferences.getInt("effects",100)));c.put("hq_resampling",preferences.getBoolean("hq",true)?"1":"0");c.put("pause_on_leave",preferences.getBoolean("pause",true)?"1":"0");c.put("skip_intro","1");c.put("cheat_infinite_life","0");c.put("cheat_one_hit_kills","0");c.put("cheat_open_all_missions","0");c.put("cheat_open_all_wallpapers","0");config(new File(getFilesDir(),"Documents/retouched.cfg"),c);
    }
    private void play(){
        if(launching)return;launching=true;
        ProgressDialog progress=ProgressDialog.show(this,"PATRIOTS",t("Oyun hazırlanıyor…","Preparing game…"),true,false);
        new Thread(()->{try{if(touch)prepareTouch();else prepareMobile();runOnUiThread(()->{launching=false;if(isFinishing()||isDestroyed())return;progress.dismiss();Intent game=new Intent();game.setClassName(this,touch?"com.mgsport.retouched.RetouchedActivity":"org.mgsmobile.port.MGSActivity");game.putExtra("patriots_language",locale(this));startActivity(game);});}
            catch(Exception e){android.util.Log.e("Patriots","Launch preparation failed",e);runOnUiThread(()->{launching=false;if(isFinishing()||isDestroyed())return;progress.dismiss();message(t("Oyun hazırlanamadı. Yeterli boş alan olduğundan emin olup tekrar dene.","Could not prepare the game. Check available storage and try again."));});}},"Patriots game setup").start();
    }
}
