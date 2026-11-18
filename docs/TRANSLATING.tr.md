# Touch için çeviri teslimi

Çevirmene yalnızca şu iki dosyayı gönder:

- [Launcher JSON'u — 161 metin](../localization/launcher/pt-BR.launcher.json)
- [Oyun JSON'u — 549 metin](../localization/game/pt-BR.game.json)

Oyun dosyası menü/diyalog metinleri, 52 mevcut sabit metin adayı, PC kontrol yardımları, boss ipuçları, Discord durumları ve LIFE göstergesini içerir. Teknik/font kayıtları çıkarıldı; bu iki dosyadaki tüm kayıtların **`text` alanları çevrilebilir**.

`source` İngilizce referanstır. Yalnızca `text` çevrilir. Kimlikler, teknik alanlar, `%s`, `%d`, `%@`, `{0}` gibi işaretler ve satır sonları korunur. Aynen kalacak özel isimlerde kaynak metin `text` alanına kopyalanır. Dil bilgileri Brezilya Portekizcesi için hazırdır; çevirmen `author` alanına adını yazabilir.

Bitince iki JSON'u geri göndersin. Dosyalar **DİLLER → DİL PAKETİ İÇE AKTAR** üzerinden ayrı ayrı kurulabilir. İstenirse ZIP'in kökünde `launcher.json` ve `game.json` adlarıyla birlikte verilebilir. Launcher ve oyun dili bağımsız seçilir. Boş metinlerde İngilizce kullanılır; kayıtlar, kontrol atamaları, boss hareketleri ve Discord korunur.

Henüz hazır bir Portekizce çeviri yayımlanmıyor. Gelen gerçek çeviri fontlar, taşmalar, kontrol yardımları ve oyun içinde incelendikten sonra üçüncü resmî dil olarak paketlenecek. Bazı özgün açıklama/isim görselleri ayrıca gözden geçirilmelidir; font adlarını çevirmek bu görselleri değiştirmez.

Yeni sürümlerde bitmiş çeviriyi kaybetmeden şablonu güncellemek için `tools/refresh_language_json.py` kullanılabilir. Ayrıntılar ve komutlar [İngilizce rehberde](TRANSLATING.md).
