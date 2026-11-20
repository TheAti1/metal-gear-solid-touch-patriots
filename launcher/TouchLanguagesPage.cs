// SPDX-License-Identifier: MIT
using System;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;

public sealed partial class TouchWindow {
    void Translation(){
        Heading("05 / LOCALIZATION",L("Diller ve çeviri paketleri","Languages and translation packs"),L("Launcher ve oyun dilini ayrı seç; çevirileri JSON veya ZIP olarak kur.","Choose launcher and game languages independently; install translations as JSON or ZIP."));
        var games=TouchLanguagePacks.Available(true);int index=games.FindIndex(l=>l.id==settings.GameLanguage);
        Row(L("Oyun dili","Game language"),L("Dil seçimi bir sonraki oyun açılışına uygulanır.","The selected game language applies on the next launch."),Choice(games.Select(l=>l.name).ToArray(),index<0?0:index,i=>settings.GameLanguage=games[i].id));
        var actions=new WrapPanel();actions.Children.Add(Button(L("DİL PAKETİ İÇE AKTAR","IMPORT LANGUAGE PACK"),ImportLanguage,true));
        actions.Children.Add(Button(L("ŞABLONLARI DIŞA AKTAR","EXPORT TEMPLATES"),ExportLanguages));
        actions.Children.Add(Button(L("ÇEVİRİ KLASÖRÜ","TRANSLATION FOLDER"),()=>{string folder=Path.Combine(Files.Root,"Translations");Directory.CreateDirectory(folder);Files.Open(folder);}));body.Children.Add(actions);
        Note(L("İki JSON yeterli: launcher ve oyun. Yalnızca text alanlarını çevir; kimlikleri ve işaretleri koru. Boş metinlerde İngilizce kullanılır. Eski Türkçe JSON biçimi de desteklenir.","Two JSONs are enough: launcher and game. Translate only text fields; preserve IDs and tokens. Blank text falls back to English. The original Turkish JSON format is also supported."));
        foreach(var info in TouchLanguagePacks.Available()){
            string details=(info.id=="en"||info.id=="tr"||info.id=="pt-br"?L("Resmî","Official"):L("Topluluk","Community"))+" · "+L("Launcher","Launcher")+": "+(info.launcher?L("Kurulu","Installed"):L("İngilizce yedek dil","English fallback"))+" · "+L("Oyun","Game")+": "+(info.game?L("Kurulu","Installed"):L("İngilizce yedek dil","English fallback"));
            if(info.id!="en"&&info.id!="tr")details+=" · "+info.uiCount+" / "+TouchLanguagePacks.Template("launcher").entries.Count+" + "+info.gameCount+" / "+TouchLanguagePacks.Template("game").entries.Count;
            if(!String.IsNullOrWhiteSpace(info.author))details+="\n"+info.author;
            Row(info.name+" ("+info.id+")",details,new TextBlock());
        }
    }
    void ImportLanguage(){
        EnsureStopped();TouchLanguagePacks.EnsureStopped();var dialog=new OpenFileDialog{Filter=L("Dil paketleri|*.json;*.zip","Language packs|*.json;*.zip")};if(dialog.ShowDialog(this)!=true)return;
        string id;
        if(Path.GetExtension(dialog.FileName).Equals(".json",StringComparison.OrdinalIgnoreCase)&&File.ReadAllText(dialog.FileName).Contains("patriots.mgs-touch.localization.v1")){TranslationImport.Import(dialog.FileName);id="tr";settings.GameLanguage=id;}
        else{id=TouchLanguagePacks.Import(dialog.FileName);var info=TouchLanguagePacks.Info(id);if(info.launcher)settings.Language=id;if(info.game)settings.GameLanguage=id;}
        Loc.Language=settings.Language;settings.Save();Build();status.Text=L("Dil paketi kuruldu.","Language pack installed.");
    }
    void ExportLanguages(){var dialog=new SaveFileDialog{FileName="MGS_Touch_Translation_Templates",Filter=L("Klasör konumu|*.folder","Folder location|*.folder")};if(dialog.ShowDialog(this)!=true)return;string folder=Path.Combine(Path.GetDirectoryName(dialog.FileName),Path.GetFileNameWithoutExtension(dialog.FileName));TouchLanguagePacks.Export(folder);Files.Open(folder);status.Text=L("Çeviri şablonları dışa aktarıldı.","Translation templates exported.");}
}
