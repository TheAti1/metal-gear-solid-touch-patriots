// SPDX-License-Identifier: MIT
using System.Collections.Generic;
internal static class TouchLocale {
    static readonly Dictionary<string,string> English=new Dictionary<string,string>{
        {"Bağlandı","Connected"},{"RPC hatası","RPC error"},{"Discord hatası: ","Discord error: "},
        {"Etkinlik yayında","Activity published"},{"Etkinlik temizlendi","Activity cleared"},
        {"Discord masaüstü uygulaması bekleniyor","Waiting for Discord desktop"},{"Kapalı","Off"},
        {"Bağlantı yeniden deneniyor","Reconnecting"},{"Oyun kapandı · etkinlik temizlendi","Game closed · activity cleared"}
    };
    public static string Translate(string value,string language){string result;if(language!="tr"){string source=English.TryGetValue(value,out result)?result:value;return language=="en"?source:TouchLanguagePacks.Translate(source,language);}foreach(var pair in English)if(pair.Value==value)return pair.Key;return value;}
}
