// SPDX-License-Identifier: MIT
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;

public sealed partial class TouchWindow {
    void Home(){
        body.Children.Add(Text("01 / PATRIOTS PC EDITION",11,accent));
        var hero=new Grid{Height=310,Background=Brush("#151F19")};
        string art=Path.Combine(Files.Root,"Arayuz","hero.png");
        if(File.Exists(art))hero.Children.Add(new Image{Source=new BitmapImage(new Uri(art)),Width=390,HorizontalAlignment=HorizontalAlignment.Right,Stretch=Stretch.UniformToFill});
        var shade=new System.Windows.Shapes.Rectangle{Fill=new LinearGradientBrush(new GradientStopCollection{
            new GradientStop(Color.FromRgb(17,27,20),0),new GradientStop(Color.FromRgb(17,27,20),.42),
            new GradientStop(Color.FromArgb(165,17,27,20),.67),new GradientStop(Color.FromArgb(20,17,27,20),1)},new Point(0,0),new Point(1,0))};
        hero.Children.Add(shade);
        var copy=new StackPanel{Margin=new Thickness(28,31,24,20),Width=470,HorizontalAlignment=HorizontalAlignment.Left};
        copy.Children.Add(Text(Loc.E("TACTICAL TOUCH ACTION"),11,accent));
        var title=Text("METAL GEAR SOLID\nTOUCH",40);title.FontFamily=new FontFamily("Bahnschrift SemiBold");title.LineHeight=46;title.Margin=new Thickness(0,16,0,14);copy.Children.Add(title);
        var subtitle=Text(L("Old Snake’in son görevi.\nPC’de, kendi kontrolünle.","Old Snake’s final mission.\nOn PC. Under your control."),15,muted);subtitle.LineHeight=23;copy.Children.Add(subtitle);
        var edition=Text("WINDOWS  /  "+TouchLanguagePacks.Info(settings.GameLanguage).name.ToUpperInvariant(),11,accent);edition.Margin=new Thickness(0,24,0,0);copy.Children.Add(edition);hero.Children.Add(copy);
        body.Children.Add(new Border{Child=hero,CornerRadius=new CornerRadius(7),ClipToBounds=true,Margin=new Thickness(0,15,0,12),BorderBrush=line,BorderThickness=new Thickness(1)});
        Note(L("Fare, klavye ve gamepad desteği. Görüntü oranını koruyan tam ekran. Görev takibiyle Discord Rich Presence.","Mouse, keyboard and controller support. Fullscreen with the original aspect ratio. Mission-aware Discord Rich Presence."));
        Row(L("Tek tıkla başlat","Direct play"),L("EXE doğrudan oyunu açar. Ayarlar için --settings kullan.","Open the game directly. Use --settings to return here."),Toggle(settings.DirectPlay,v=>settings.DirectPlay=v));
        Row(L("Giriş logolarını atla","Skip introduction logos"),L("Sonraki oyun açılışına uygulanır.","Applies on the next launch."),Toggle(settings.SkipIntro,v=>settings.SkipIntro=v));
        var actions=new StackPanel{Orientation=Orientation.Horizontal,Margin=new Thickness(0,20,0,0)};
        actions.Children.Add(Button(L("OYUN KLASÖRÜ","GAME FOLDER"),()=>Files.Open(Files.Root)));
        actions.Children.Add(Button("PATRIOTS ÇEVİRİ ↗",()=>Files.Open("https://www.patriotsceviri.com.tr/")));
        body.Children.Add(actions);
    }
}
