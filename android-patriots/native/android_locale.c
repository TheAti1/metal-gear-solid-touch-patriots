#include "host.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {char *source,*text;} Entry;
static Entry entries[4096];static int count;
static unsigned read32(const unsigned char *p){return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3];}
void patriots_load_locale(void){
    if(!g_cfg.overlay_dir[0])return;char path[1200];snprintf(path,sizeof path,"%s/runtime_text.bin",g_cfg.overlay_dir);long length=0;unsigned char *bytes=vfs_read_all(path,&length);
    if(!bytes||length<12||length>12*1024*1024||memcmp(bytes,"PTXT0001",8)){free(bytes);return;}
    unsigned n=read32(bytes+8),offset=12;if(n>4096){free(bytes);return;}
    for(unsigned i=0;i<n;i++){char *field[2]={0};int valid=1;for(int k=0;k<2;k++){if(offset+4>(unsigned)length){valid=0;break;}unsigned size=read32(bytes+offset);offset+=4;if(size>65536||offset+size>(unsigned)length){valid=0;break;}field[k]=calloc(size+1,1);if(!field[k]){valid=0;break;}memcpy(field[k],bytes+offset,size);offset+=size;}
        if(!valid){free(field[0]);free(field[1]);break;}entries[count++]=(Entry){field[0],field[1]};}
    free(bytes);hlog("Patriots Android locale: %s, %d runtime strings",g_cfg.lang,count);
}
const char *pc_runtime_text(const char *s){
    if(!s)return s;for(int i=0;i<count;i++)if(!strcmp(entries[i].source,s))return entries[i].text;
    if(!strcmp(s,"RETOUCHED"))return "PATRIOTS";
    if(!strcmp(g_cfg.lang,"Turkish")){
        static const char *pairs[][2]={{"Loading...","Yükleniyor..."},{"Loading…","Yükleniyor..."},{"PAUSE","DURAKLATILDI"},{"RESUME","DEVAM ET"},{"QUIT","GÖREVDEN ÇIK"},{"BACK","GERİ"},{"YES","EVET"},{"NO","HAYIR"},{"Quit this mission?","Görevden çıkılsın mı?"},{"Progress in it will be lost.","Bu görevdeki ilerleme kaybolacak."},{"Graphics","Görüntü"},{"Sound","Ses"},{"Controls","Kontroller"},{"Game","Oyun"},{"Extras","Ekstralar"},{"Cheats","Hileler"},{"Full screen","Tam ekran"},{"Language","Dil"},{"Phone","Telefon"},{"On","Açık"},{"Off","Kapalı"},{"Save backup","Kayıt yedeği"}};
        for(unsigned i=0;i<sizeof pairs/sizeof pairs[0];i++)if(!strcmp(s,pairs[i][0]))return pairs[i][1];
    }return s;
}
