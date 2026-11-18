/* SPDX-License-Identifier: MIT
 * Patriots Windows/SDL3 host for the locally recovered MGS Touch game.
 */
#define SDL_MAIN_HANDLED
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <windows.h>
#include <direct.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "host.h"
#include "rtx_host.h"

static SDL_Window *window;
static SDL_AudioStream *audio;
static SDL_Gamepad *pad;
static volatile LONG64 mixed_frames,audible_buffers;
static FILE *logfile;
static int running = 1, fullscreen, focused = 1, started;
static int mouse_down, pinch_down, key_down, controller_down;
static float mx = 160, my = 240;
static int game_state;
static int qa_mode;
static int game_scene;
static int game_mission;
static int game_case;
static int game_landscape;
static int game_weapon,qa_early_retry;
static int doll_stick_side;
static double doll_stick_at,doll_shaken_at,doll_hint_start;
static int boss_dodge_armed;
static int input_device,hints_manual=-1,hints_visible;
static double hints_until;
static void control_draw_focus(void);
static void control_refresh(void);
static int qa_axes;
static float qa_ax,qa_ay;
static float qa_ry;
static int qa_hidden;
static void (*base_overlay)(int,int,int,int);
void pc_ui_begin_window(int w,int h);
static int pc_active,mouse_cover,key_cover,pad_cover,trigger_fire;
static int pc_ready,ready_pending;
static double ready_release;
static double pad_last_time,next_fire;
static int last_mission_rotation;
static double last_status_write;
static double stop_after, capture_at = 5;
static char capture_file[1024];
static char base_dir[1024], save_dir[1024], font_dir[1024];
static int vsync = 1, max_fps = 120, fill_mode = 1, scale = 3;
static float deadzone = 0.18f;
static char test_script[1024];
static struct {double at;char verb[32],args[1024];} test_steps[256];
static int test_count,test_index,pending_tap;
static double tap_release_at;
static float tap_x,tap_y;
enum {ACT_PRESS,ACT_PAUSE,ACT_ZOOM_IN,ACT_ZOOM_OUT,ACT_SHAKE,ACT_FULLSCREEN,ACT_SCREENSHOT,ACT_COVER,ACT_UP,ACT_DOWN,ACT_LEFT,ACT_RIGHT,ACT_COUNT};
enum {ACT_BACK=100};
static struct {const char *name,*default_key;SDL_Scancode key;} bindings[ACT_COUNT]={
    {"press","Return",0},{"pause","Escape",0},{"zoom_in","E",0},{"zoom_out","Q",0},{"shake","F",0},
    {"fullscreen","F11",0},{"screenshot","F12",0},{"cover","Space",0},{"aim_up","W",0},{"aim_down","S",0},{"aim_left","A",0},{"aim_right","D",0}};
static struct {const char *name;int action,button;} pad_bindings[]={
    {"press",ACT_PRESS,0},{"pause",ACT_PAUSE,6},{"back",ACT_BACK,1},{"zoom_in",ACT_ZOOM_IN,10},{"zoom_out",ACT_ZOOM_OUT,9},{"shake",ACT_SHAKE,3},{"cover",ACT_COVER,7}};
static int action_for_pad(int button){for(unsigned i=0;i<sizeof pad_bindings/sizeof pad_bindings[0];i++)if(pad_bindings[i].button==button)return pad_bindings[i].action;return -1;}
static int action_for_key(SDL_Scancode key){for(int i=0;i<ACT_COUNT;i++)if(bindings[i].key==key)return i;return -1;}
typedef struct {char *source,*text;} RuntimeText;
static RuntimeText runtime_texts[512];static int runtime_text_count;
static uint32_t file_be32(FILE *f){uint8_t b[4];return fread(b,1,4,f)==4?((uint32_t)b[0]<<24|b[1]<<16|b[2]<<8|b[3]):0;}
static void load_runtime_texts(void){
    if(strcmp(g_cfg.lang,"Turkish"))return;
    char path[1200];snprintf(path,sizeof path,"%s/runtime_text.bin",g_cfg.overlay_dir);FILE *f=fopen(path,"rb");if(!f)return;
    char magic[8];if(fread(magic,1,8,f)!=8||memcmp(magic,"PTXT0001",8)){fclose(f);return;}
    uint32_t count=file_be32(f);if(count>512){fclose(f);return;}
    for(uint32_t i=0;i<count;i++){
        char *fields[2]={0};int ok=1;
        for(int k=0;k<2;k++){uint32_t n=file_be32(f);if(!n||n>65536){ok=0;break;}fields[k]=calloc(n+1,1);if(!fields[k]||fread(fields[k],1,n,f)!=n){ok=0;break;}}
        if(!ok){free(fields[0]);free(fields[1]);break;}
        runtime_texts[runtime_text_count++]=(RuntimeText){fields[0],fields[1]};
    }fclose(f);hlog("Runtime text overrides: %d",runtime_text_count);
}
const char *pc_runtime_text(const char *s){
    for(int i=0;i<runtime_text_count;i++)if(!strcmp(runtime_texts[i].source,s))return runtime_texts[i].text;
    if(!strcmp(s,"RETOUCHED"))return "PATRIOTS";
    if(!strcmp(g_cfg.lang,"Turkish")){
        static const char *pairs[][2]={{"Loading...","Yükleniyor..."},{"Loading…","Yükleniyor..."},{"PAUSE","DURAKLATILDI"},{"RESUME","DEVAM ET"},{"QUIT","GÖREVDEN ÇIK"},{"BACK","GERİ"},{"YES","EVET"},{"NO","HAYIR"},{"Quit this mission?","Görevden çıkılsın mı?"},{"Progress in it will be lost.","Bu görevdeki ilerleme kaybolacak."}};
        for(unsigned i=0;i<sizeof pairs/sizeof pairs[0];i++)if(!strcmp(s,pairs[i][0]))return pairs[i][1];
    }
    return s;
}
static void seen_device(int device){if(input_device!=device){input_device=device;hints_until=host_now()+5;}}
static const char *pad_label(int button){
    static const char *xbox[]={"A","B","X","Y","Back","Guide","Start","LS","RS","LB","RB","Up","Down","Left","Right"};
    static const char *ps[]={"Cross","Circle","Square","Triangle","Share","PS","Options","L3","R3","L1","R1","Up","Down","Left","Right"};
    static const char *nintendo[]={"B","A","Y","X","Minus","Home","Plus","L Stick","R Stick","L","R","Up","Down","Left","Right"};
    if(button<0||button>=15)return "Button";SDL_GamepadType type=pad?SDL_GetGamepadType(pad):SDL_GAMEPAD_TYPE_STANDARD;
    if(type==SDL_GAMEPAD_TYPE_PS3||type==SDL_GAMEPAD_TYPE_PS4||type==SDL_GAMEPAD_TYPE_PS5)return ps[button];
    if(type>=SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO&&type<=SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_PAIR)return nintendo[button];
    return xbox[button];
}
static const char *bound_pad(int action){for(unsigned i=0;i<sizeof pad_bindings/sizeof pad_bindings[0];i++)if(pad_bindings[i].action==action)return pad_label(pad_bindings[i].button);return "-";}
static void ui_disc(float x,float y,float r,Col color){
    for(float row=-r;row<r;row+=2){float half=sqrtf(fmaxf(0,r*r-(row+1)*(row+1)));ui_fill(x-half,y+row,2*half,2,color);}
}
static void draw_doll_prompt(int ww,int by,int bh){
    if(!pc_active||game_weapon!=6)return;
    double now=host_now();int tr=!strcmp(g_cfg.lang,"Turkish");
    float fade=fminf(1,(float)(now-doll_hint_start)*4),pulse=.7f+.3f*sinf((float)now*5);
    float width=fminf(520,(float)ww-32),x=(ww-width)/2,y=fmaxf(12,by+bh-175);
    Col green={.68f,.9f,.46f,fade},white={.94f,.96f,.92f,fade};
    ui_fill(x,y,width,94,(Col){.025f,.045f,.035f,.94f*fade});
    ui_fill(x,y,3,94,(Col){.68f,.9f,.46f,fade*pulse});
    float cx=x+56,cy=y+46,offset=input_device?sinf((float)now*7)*14:0;
    ui_disc(cx,cy,26,(Col){.22f,.29f,.23f,fade});
    ui_disc(cx,cy,23,(Col){.055f,.085f,.065f,fade});
    ui_text("<",x+10,y+35,20,1,0,green,20);ui_text(">",x+89,y+35,20,1,0,green,20);
    ui_disc(cx+offset,cy,15,green);
    ui_text(input_device?"R":SDL_GetScancodeName(bindings[ACT_SHAKE].key),cx+offset,cy-8,14,1,1,(Col){.025f,.045f,.035f,fade},24);
    char title[200];
    if(input_device)snprintf(title,sizeof title,"%s",tr?"R analoğunu sağa sola oynat":"Move the R stick left and right");
    else snprintf(title,sizeof title,"%s  ·  %s",SDL_GetScancodeName(bindings[ACT_SHAKE].key),tr?"Kuklayı salla":"Shake the doll");
    ui_text(title,x+120,y+22,17,1,0,white,width-132);
    ui_text(now-doll_shaken_at<.45?(tr?"Kukla sallanıyor...":"Shaking the doll..."):(tr?"Mantis kuklası elinde":"Mantis doll equipped"),x+120,y+52,14,0,0,green,width-132);
}
static void desktop_overlay(int bx,int by,int bw,int bh){
    if(base_overlay)base_overlay(bx,by,bw,bh);int ww,wh;gfx_window_size(&ww,&wh);
    int show=hints_manual>=0?hints_manual:(bx>270||host_now()<hints_until);
    hints_visible=show;pc_ui_begin_window(ww,wh);control_draw_focus();draw_doll_prompt(ww,by,bh);
    Col white={.91f,.94f,.9f,1},dim={.65f,.7f,.65f,1},green={.66f,.81f,.45f,1};
    if(!show){ui_text("F1",8,wh-24,12,1,0,green,30);ui_end();return;}
    int tr=!strcmp(g_cfg.lang,"Turkish");float x=20,y=by+40,w=bx>270?(float)bx-40:350;
    if(w>350)w=350;if(y+262>wh)y=wh-280;
    ui_fill(x,y,w,248,(Col){.03f,.055f,.04f,.94f});ui_frame(x,y,w,248,1,(Col){.3f,.4f,.28f,.8f});
    ui_text(input_device?"GAMEPAD":tr?"KLAVYE / FARE":"KEYBOARD / MOUSE",x+16,y+16,14,1,0,green,w-32);
    char lines[5][320];
    if(input_device){SDL_GamepadType type=pad?SDL_GetGamepadType(pad):SDL_GAMEPAD_TYPE_STANDARD;const char *rt="RT",*lt="LT";if(type==SDL_GAMEPAD_TYPE_PS3||type==SDL_GAMEPAD_TYPE_PS4||type==SDL_GAMEPAD_TYPE_PS5){rt="R2";lt="L2";}else if(type>=SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO&&type<=SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_PAIR){rt="ZR";lt="ZL";}
        snprintf(lines[0],320,"%s  ·  %s",tr?"Sağ analog":"Right stick",tr?"Nişan / imleç":"Aim / cursor");
        snprintf(lines[1],320,"%s / %s  ·  %s",rt,bound_pad(ACT_PRESS),tr?"Ateş / onay":"Fire / confirm");
        snprintf(lines[2],320,"%s / %s  ·  %s",lt,bound_pad(ACT_COVER),tr?"Siper (basılı tut)":"Cover (hold)");
        snprintf(lines[3],320,"%s / %s  ·  %s",bound_pad(ACT_ZOOM_OUT),bound_pad(ACT_ZOOM_IN),tr?"M4 / SVD":"M4 / SVD");
        snprintf(lines[4],320,"%s  ·  %s",bound_pad(ACT_PAUSE),tr?"Duraklat":"Pause");
    }else{
        snprintf(lines[0],320,"%s / %s %s %s %s  ·  %s",tr?"Fare":"Mouse",SDL_GetScancodeName(bindings[ACT_UP].key),SDL_GetScancodeName(bindings[ACT_LEFT].key),SDL_GetScancodeName(bindings[ACT_DOWN].key),SDL_GetScancodeName(bindings[ACT_RIGHT].key),tr?"Nişan":"Aim");
        snprintf(lines[1],320,"%s / %s  ·  %s",tr?"Sol tık":"Left click",SDL_GetScancodeName(bindings[ACT_PRESS].key),tr?"Ateş / onay":"Fire / confirm");
        snprintf(lines[2],320,"%s / %s  ·  %s",tr?"Sağ tık":"Right click",SDL_GetScancodeName(bindings[ACT_COVER].key),tr?"Siper":"Cover");
        snprintf(lines[3],320,"%s / %s  ·  M4 / SVD",SDL_GetScancodeName(bindings[ACT_ZOOM_OUT].key),SDL_GetScancodeName(bindings[ACT_ZOOM_IN].key));
        snprintf(lines[4],320,"%s  ·  %s",SDL_GetScancodeName(bindings[ACT_PAUSE].key),tr?"Duraklat":"Pause");
    }
    if(!pc_active){
        snprintf(lines[0],320,"%s  ·  %s",input_device?(tr?"Sol analog / yön tuşları":"Left stick / D-pad"):(tr?"Yön tuşları / WASD":"Arrow keys / WASD"),tr?"Seç":"Select");
        snprintf(lines[1],320,"%s  ·  %s",input_device?bound_pad(ACT_PRESS):SDL_GetScancodeName(bindings[ACT_PRESS].key),tr?"Onayla / ileri":"Confirm / next");
        snprintf(lines[2],320,"%s  ·  %s",input_device?bound_pad(ACT_BACK):SDL_GetScancodeName(bindings[ACT_PAUSE].key),tr?"Geri / iptal":"Back / cancel");
        snprintf(lines[3],320,"%s  ·  %s",input_device?bound_pad(ACT_PAUSE):SDL_GetScancodeName(bindings[ACT_PAUSE].key),tr?"Duraklat / devam":"Pause / resume");
        snprintf(lines[4],320,"%s",input_device?(tr?"Sağ analog  ·  Metni kaydır":"Right stick  ·  Scroll text"):(tr?"Tekerlek / PgUp / PgDn  ·  Metni kaydır":"Wheel / PgUp / PgDn  ·  Scroll text"));
    }
    if(pc_active&&game_weapon==6){
        snprintf(lines[0],320,"%s",tr?"Mantis kuklası elinde":"Mantis doll equipped");
        snprintf(lines[1],320,"%s",input_device?(tr?"R analoğunu sağa sola oynat":"Move the R stick left and right"):(tr?"Sallama tuşuna bas":"Press the shake key"));
        snprintf(lines[2],320,"%s  ·  %s",input_device?bound_pad(ACT_SHAKE):SDL_GetScancodeName(bindings[ACT_SHAKE].key),tr?"Salla / kuklayı kullan":"Shake / use doll");
        snprintf(lines[3],320,"%s",tr?"Bossun savunması açıldığında kullan":"Use when the boss is vulnerable");
        snprintf(lines[4],320,"%s",tr?"Sallayarak tekrar kullan":"Shake again to repeat");
    }
    if(pc_active&&game_mission==20&&input_device){
        snprintf(lines[0],320,"%s",tr?"Sağ analog sağ / sol  ·  Kaçın":"Right stick left / right  ·  Dodge");
        snprintf(lines[3],320,"%s",tr?"Tekrar kaçınmak için analoğu ortala":"Centre the stick before dodging again");
    }
    for(int i=0;i<5;i++)ui_text(lines[i],x+16,y+53+i*29,14,0,0,white,w-32);
    ui_text(tr?"F1  ·  Yardımı göster / gizle":"F1  ·  Show / hide controls",x+16,y+215,12,0,0,dim,w-32);ui_end();
}
int desktop_open_settings(void){
    /* In-game Patriots links open the website; settings stay in the launcher
     * until this game session ends. SDL uses the registered desktop browser. */
    if(qa_mode){hlog("Patriots website: https://www.patriotsceviri.com.tr/");return 1;}
    if(!SDL_OpenURL("https://www.patriotsceviri.com.tr/"))hlog("Website open failed: %s",SDL_GetError());
    return 1;
}

static void set_window_icon(void){
    HWND hwnd=(HWND)SDL_GetPointerProperty(SDL_GetWindowProperties(window),SDL_PROP_WINDOW_WIN32_HWND_POINTER,NULL);
    HINSTANCE module=GetModuleHandleW(NULL);
    HICON big=(HICON)LoadImageW(module,MAKEINTRESOURCEW(1),IMAGE_ICON,GetSystemMetrics(SM_CXICON),GetSystemMetrics(SM_CYICON),LR_SHARED);
    HICON small=(HICON)LoadImageW(module,MAKEINTRESOURCEW(1),IMAGE_ICON,GetSystemMetrics(SM_CXSMICON),GetSystemMetrics(SM_CYSMICON),LR_SHARED);
    if(hwnd&&big&&small){SendMessageW(hwnd,WM_SETICON,ICON_BIG,(LPARAM)big);SendMessageW(hwnd,WM_SETICON,ICON_SMALL,(LPARAM)small);hlog("Game window icons installed: large and small");}
    else hlog("Game icon unavailable");
}

static void path_join(char *out, size_t cap, const char *a, const char *b) {
    snprintf(out, cap, "%s%s%s", a, a[0] && a[strlen(a)-1] != '/' ? "/" : "", b);
    for (char *p=out; *p; ++p) if (*p=='\\') *p='/';
}
void hlog_platform(const char *line) {
    if(logfile){ fprintf(logfile,"[%9.3f] %s\n",SDL_GetTicks()/1000.0,line); fflush(logfile); }
    fprintf(stderr,"%s\n",line);
}
void *gfx_getproc(const char *name) { return (void *)SDL_GL_GetProcAddress(name); }
void platform_swap(void) { SDL_GL_SwapWindow(window); }

static void SDLCALL audio_callback(void *userdata, SDL_AudioStream *stream, int additional, int total) {
    (void)userdata; (void)total;
    int16_t samples[4096];
    while(additional>0) {
        int bytes=additional>(int)sizeof samples ? (int)sizeof samples : additional;
        bytes-=bytes%4;
        if(!bytes) break;
        audio_mix(samples,bytes/4);
        InterlockedAdd64(&mixed_frames,bytes/4);
        for(int i=0;i<bytes/2;i++)if(samples[i]){InterlockedIncrement64(&audible_buffers);break;}
        SDL_PutAudioStreamData(stream,samples,bytes);
        additional-=bytes;
    }
}
static int module_state(void) {
    if(!started || host_is_crashed()) return 0;
    game_lock(&g_main_thread);
    int state=(int)w2c_mgst_mgst_rtx_cmd(&g_inst,8,0);
    game_scene=w2c_mgst_mgst_pc_status(&g_inst,0);
    game_mission=w2c_mgst_mgst_pc_status(&g_inst,1);
    game_case=w2c_mgst_mgst_pc_status(&g_inst,8);
    game_landscape=w2c_mgst_mgst_pc_status(&g_inst,7);
    int weapon=(int)w2c_mgst_mgst_pc_status(&g_inst,9);
    game_unlock(&g_main_thread);
    if(weapon!=game_weapon){game_weapon=weapon;doll_stick_side=0;doll_shaken_at=0;if(weapon==6){doll_hint_start=host_now();hints_until=host_now()+8;}}
    return state;
}
static void pc_input(int command,float x,float y){if(!started||host_is_crashed())return;game_lock(&g_main_thread);w2c_mgst_mgst_pc_input(&g_inst,command,x,y);game_unlock(&g_main_thread);}
static void doll_stick(float rx){
    if(!pc_active||game_weapon!=6||!focused){doll_stick_side=0;return;}
    double now=host_now();
    if(now-doll_stick_at>.85)doll_stick_side=0;
    int side=rx<-.45f?-1:rx>.45f?1:0;
    if(!side)return;
    if(doll_stick_side&&side!=doll_stick_side&&now-doll_shaken_at>.4){
        pc_input(7,0,0);doll_shaken_at=now;hlog("Doll shake: right-stick direction changed");
    }
    if(side!=doll_stick_side)doll_stick_at=now;
    doll_stick_side=side;
}
static void final_boss_stick(float rx,float ry){
    /* Only the final Liquid fight uses the original horizontal flick dodge.
     * Require neutral after loading/pause and after each dodge: a held stick
     * must not repeat the gesture or trigger it when gameplay resumes. */
    if(!pc_active||game_scene!=8||game_mission!=20||!focused){boss_dodge_armed=0;return;}
    if(fabsf(rx)<.28f&&fabsf(ry)<.45f){boss_dodge_armed=1;return;}
    if(boss_dodge_armed&&fabsf(rx)>=.72f&&fabsf(rx)>fabsf(ry)*1.15f){
        /* The original phone gesture directions are reversed in landscape. */
        boss_dodge_armed=0;pc_input(6,rx<0?1:-1,0);
        hlog("Final boss dodge: %s",rx<0?"left":"right");
    }
}
static void ready_tap(void){host_touch(0,0,20,460);ready_pending=1;ready_release=host_now()+.08;}
static void update_pc_mode(void){game_lock(&g_main_thread);int active=w2c_mgst_mgst_pc_status(&g_inst,5);pc_ready=w2c_mgst_mgst_pc_status(&g_inst,6);game_unlock(&g_main_thread);if(active!=pc_active){pc_active=active;boss_dodge_armed=0;hints_until=host_now()+6;mouse_down=key_down=controller_down=mouse_cover=key_cover=pad_cover=0;pc_input(5,0,0);pc_input(3,0,0);SDL_SetWindowRelativeMouseMode(window,pc_active&&!qa_mode);hlog("PC input mode: %s",pc_active?"gameplay":"menus");}}
static void write_status(double now) {
    if(now-last_status_write<1.0)return;
    last_status_write=now;
    int scene,mission,bg,hp,maxhp;
    game_lock(&g_main_thread);
    scene=w2c_mgst_mgst_pc_status(&g_inst,0);
    mission=w2c_mgst_mgst_pc_status(&g_inst,1);
    bg=w2c_mgst_mgst_pc_status(&g_inst,2);
    hp=w2c_mgst_mgst_pc_status(&g_inst,3);
    maxhp=w2c_mgst_mgst_pc_status(&g_inst,4);
    game_unlock(&g_main_thread);
    char path[1200],temp[1200];
    path_join(path,sizeof path,save_dir,"patriots_state.json");
    path_join(temp,sizeof temp,save_dir,"patriots_state.tmp");
    FILE *f=fopen(temp,"wb");
    if(f){fprintf(f,"{\"pid\":%lu,\"scene\":%d,\"mission\":%d,\"phase\":%d,\"flags\":%d,\"hp\":%d,\"max_hp\":%d,\"elapsed\":%.1f}\n",(unsigned long)GetCurrentProcessId(),scene,mission,bg,game_state,hp,maxhp,now);fclose(f);MoveFileExA(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH);}
}
static void release_inputs(void) {
    doll_stick_side=0;
    boss_dodge_armed=0;
    if(pc_active){pc_input(5,0,0);mouse_down=key_down=controller_down=mouse_cover=key_cover=pad_cover=0;}
    if(mouse_down){host_touch(3,0,mx,my);mouse_down=0;}
    if(pinch_down){host_touch(3,1,mx+80,my);pinch_down=0;}
    if(controller_down || key_down){rtx_pad_button(0);controller_down=key_down=0;}
    rtx_pad_axis(0,0);
    rtx_pad_button(0);
}
#include "windows_navigation.inc"
static void resize(void) {
    int w,h; SDL_GetWindowSizeInPixels(window,&w,&h);
    if(w>0 && h>0) gfx_set_window(w,h);
}
static void window_to_view(float x,float y,float *vx,float *vy) {
    int w,h,pw,ph; SDL_GetWindowSize(window,&w,&h); SDL_GetWindowSizeInPixels(window,&pw,&ph);
    gfx_window_to_view(x*(float)pw/(w?w:1),y*(float)ph/(h?h:1),vx,vy);
}
static void toggle_fullscreen(void) {
    release_inputs(); fullscreen=!fullscreen; SDL_SetWindowFullscreen(window,fullscreen!=0); resize();
}
static void vibrate(int ms) { if(pad) SDL_RumbleGamepad(pad,16000,24000,(Uint32)ms); }
void rtx_plat_immersive(int on) { (void)on; }
void rtx_plat_export_save(const uint8_t *data,int n) {
    char p[1200]; snprintf(p,sizeof p,"%s/SAVE.backup-%llu.data",save_dir,(unsigned long long)SDL_GetTicks());
    FILE *f=fopen(p,"wb"); if(f){fwrite(data,1,n,f);fclose(f);hlog("Save backup: %s",p);rtx_io_result(1,data,n);}
    else rtx_io_result(1,NULL,0);
}
void rtx_plat_import_save(void) {
    /* Save replacement is handled by the launcher, while the game is closed. */
    rtx_io_result(2,NULL,0);
}
void rtx_plat_restart(void) { running=0; }

static void load_config(void) {
    char p[1200],line[1200]; path_join(p,sizeof p,base_dir,"desktop.ini");
    FILE *f=fopen(p,"rb"); if(!f) return;
    while(fgets(line,sizeof line,f)) {
        char *eq=strchr(line,'='); if(!eq || line[0]=='#' || line[0]==';')continue;
        *eq++=0; eq[strcspn(eq,"\r\n")]=0;
        if(!strcmp(line,"language"))snprintf(g_cfg.lang,sizeof g_cfg.lang,"%s",!strcmp(eq,"tr")?"Turkish":"English");
        else if(!strcmp(line,"fullscreen"))fullscreen=atoi(eq)!=0;
        else if(!strcmp(line,"vsync"))vsync=atoi(eq)!=0;
        else if(!strcmp(line,"max_fps"))max_fps=atoi(eq);
        else if(!strcmp(line,"fill"))fill_mode=atoi(eq);
        else if(!strcmp(line,"render_scale"))scale=atoi(eq);
        else if(!strcmp(line,"deadzone"))deadzone=(float)atof(eq);
        else if(!strncmp(line,"key_",4)){for(int i=0;i<ACT_COUNT;i++)if(!strcmp(line+4,bindings[i].name)){SDL_Scancode code=SDL_GetScancodeFromName(eq);if(code!=SDL_SCANCODE_UNKNOWN)bindings[i].key=code;}}
        else if(!strncmp(line,"pad_",4)){for(unsigned i=0;i<sizeof pad_bindings/sizeof pad_bindings[0];i++)if(!strcmp(line+4,pad_bindings[i].name)){int button=atoi(eq);if(button>=0&&button<SDL_GAMEPAD_BUTTON_COUNT)pad_bindings[i].button=button;}}
    }
    fclose(f);
    if(max_fps<30 || max_fps>360)max_fps=120;
    if(scale<1 || scale>4)scale=3;
    if(fill_mode<0 || fill_mode>2)fill_mode=1;
    if(deadzone<0.05f || deadzone>0.8f)deadzone=.18f;
}
static void pinch(int outward) {
    if(pc_active){pc_input(4,outward?1:-1,0);return;}
    control_refresh();if(nav.kind){control_move(outward?1:-1);return;}
    /* Two real UIKit contacts, not a stretched picture or camera scaling. */
    host_touch(0,0,120,240);host_touch(0,1,200,240);
    for(int i=1;i<=6;i++) {
        float d=(outward?1:-1)*i*7.0f;
        host_touch(1,0,120-d,240);host_touch(1,1,200+d,240);
        host_frame(host_now());
    }
    host_touch(3,0,120,240);host_touch(3,1,200,240);
}
static float axis(Sint16 v) {
    float f=v/32767.0f,a=fabsf(f);
    return a<deadzone?0:copysignf((a-deadzone)/(1-deadzone),f);
}
float pc_controller_speed(void);
static void poll_pad(void) {
    float ax=0,ay=0,ry=0;
    doll_stick(pad?axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHTX)):0);
    final_boss_stick(pad?axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHTX)):0,pad?axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHTY)):0);
    if(pad){SDL_GamepadAxis xaxis=pc_active?SDL_GAMEPAD_AXIS_RIGHTX:SDL_GAMEPAD_AXIS_LEFTX,yaxis=pc_active?SDL_GAMEPAD_AXIS_RIGHTY:SDL_GAMEPAD_AXIS_LEFTY;
        ax=axis(SDL_GetGamepadAxis(pad,xaxis));ay=axis(SDL_GetGamepadAxis(pad,yaxis));
        if(pc_active&&!ax&&!ay){ax=axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_LEFTX));ay=axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_LEFTY));}
        if(!pc_active)ry=axis(SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHTY));}
    if(ax||ay)seen_device(1);
    const bool *keys=SDL_GetKeyboardState(NULL);
    int keyboard_aim=keys[bindings[ACT_LEFT].key]||keys[bindings[ACT_RIGHT].key]||keys[bindings[ACT_UP].key]||keys[bindings[ACT_DOWN].key]||keys[SDL_SCANCODE_LEFT]||keys[SDL_SCANCODE_RIGHT]||keys[SDL_SCANCODE_UP]||keys[SDL_SCANCODE_DOWN];
    if(keys[bindings[ACT_LEFT].key]||(keys[SDL_SCANCODE_LEFT]&&action_for_key(SDL_SCANCODE_LEFT)<0))ax=-1;
    if(keys[bindings[ACT_RIGHT].key]||(keys[SDL_SCANCODE_RIGHT]&&action_for_key(SDL_SCANCODE_RIGHT)<0))ax=1;
    if(keys[bindings[ACT_UP].key]||(keys[SDL_SCANCODE_UP]&&action_for_key(SDL_SCANCODE_UP)<0))ay=-1;
    if(keys[bindings[ACT_DOWN].key]||(keys[SDL_SCANCODE_DOWN]&&action_for_key(SDL_SCANCODE_DOWN)<0))ay=1;
    if(pad){if(action_for_pad(SDL_GAMEPAD_BUTTON_DPAD_LEFT)<0&&SDL_GetGamepadButton(pad,SDL_GAMEPAD_BUTTON_DPAD_LEFT))ax=-1;if(action_for_pad(SDL_GAMEPAD_BUTTON_DPAD_RIGHT)<0&&SDL_GetGamepadButton(pad,SDL_GAMEPAD_BUTTON_DPAD_RIGHT))ax=1;if(action_for_pad(SDL_GAMEPAD_BUTTON_DPAD_UP)<0&&SDL_GetGamepadButton(pad,SDL_GAMEPAD_BUTTON_DPAD_UP))ay=-1;if(action_for_pad(SDL_GAMEPAD_BUTTON_DPAD_DOWN)<0&&SDL_GetGamepadButton(pad,SDL_GAMEPAD_BUTTON_DPAD_DOWN))ay=1;}
    control_trigger(pad&&SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER)>14000);
    if(pc_active){double now=host_now(),dt=pad_last_time?now-pad_last_time:0;pad_last_time=now;if(dt<0||dt>.1)dt=0;
        float speed=keyboard_aim?1:pc_controller_speed();
        float dx=ax*220*(float)dt*g_ext.aim_gain*speed,dy=ay*220*(float)dt*g_ext.aim_gain*speed;
        if(g_cfg.rotate==90){float t=dx;dx=-dy;dy=t;}else if(g_cfg.rotate==270){float t=dx;dx=dy;dy=-t;}
        if(dx||dy)pc_input(1,dx,dy);
        trigger_fire=pad && SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER)>14000;
        int trigger_cover=pad && SDL_GetGamepadAxis(pad,SDL_GAMEPAD_AXIS_LEFT_TRIGGER)>14000;
        pc_input(3,(mouse_cover||key_cover||pad_cover||trigger_cover)?1:0,0);
    }else{pad_last_time=0;trigger_fire=0;control_axis(ax,ay);control_scroll(ry);}
}
static void process_event(SDL_Event *e) {
    switch(e->type) {
    case SDL_EVENT_QUIT:running=0;break;
    case SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED:resize();break;
    case SDL_EVENT_WINDOW_FOCUS_LOST:focused=0;if(qa_mode)break;release_inputs();rtx_app_pause();break;
    case SDL_EVENT_WINDOW_FOCUS_GAINED:focused=1;if(!stop_after&&!test_script[0])rtx_app_resume();break;
    case SDL_EVENT_MOUSE_MOTION:
        if(e->motion.xrel||e->motion.yrel){seen_device(0);nav_visual=0;}
        if(pc_active){float x0,y0,x1,y1;window_to_view(e->motion.x-e->motion.xrel,e->motion.y-e->motion.yrel,&x0,&y0);window_to_view(e->motion.x,e->motion.y,&x1,&y1);pc_input(1,(x1-x0)*g_ext.aim_gain,(y1-y0)*g_ext.aim_gain);}
        window_to_view(e->motion.x,e->motion.y,&mx,&my);
        if(!pc_active)control_hover(mx,my);
        if(mouse_down&&!pc_active)host_touch(1,0,mx,my);
        break;
    case SDL_EVENT_MOUSE_BUTTON_DOWN:
    case SDL_EVENT_MOUSE_BUTTON_UP: {
        int down=e->type==SDL_EVENT_MOUSE_BUTTON_DOWN;
        if(down)seen_device(0);
        window_to_view(e->button.x,e->button.y,&mx,&my);
        if(!pc_active)control_hover(mx,my);
        if(e->button.button==SDL_BUTTON_LEFT){mouse_down=down;if(!pc_active)host_touch(down?0:3,0,mx,my);else if(down){pc_input(2,0,0);next_fire=host_now()+.14;}}
        else if(e->button.button==SDL_BUTTON_RIGHT){if(pc_active)mouse_cover=down;else if(down)control_back();}
        break; }
    case SDL_EVENT_MOUSE_WHEEL:seen_device(0);if(e->wheel.y&&!control_wheel(e->wheel.y))pinch(e->wheel.y>0);break;
    case SDL_EVENT_KEY_DOWN:
    case SDL_EVENT_KEY_UP: {
        int down=e->type==SDL_EVENT_KEY_DOWN;
        if(e->key.repeat)break;
        if(down){seen_device(0);nav_keyboard=1;nav_visual=1;}
        if(down&&e->key.scancode==SDL_SCANCODE_F1){hints_manual=!hints_visible;break;}
        int action=action_for_key(e->key.scancode);
        if(down&&!pc_active&&action<0&&(e->key.scancode==SDL_SCANCODE_PAGEUP||e->key.scancode==SDL_SCANCODE_PAGEDOWN)){control_wheel(e->key.scancode==SDL_SCANCODE_PAGEUP?4:-4);break;}
        if(action==ACT_FULLSCREEN && down)toggle_fullscreen();
        else if(action==ACT_PAUSE && down)control_back();
        else if(action==ACT_PRESS){key_down=pc_active?down:0;control_confirm(down);}
        else if(action==ACT_COVER){if(pc_active)key_cover=down;else control_confirm(down);}
        else if(action==ACT_ZOOM_OUT && down)pinch(0);
        else if(action==ACT_ZOOM_IN && down)pinch(1);
        else if(action==ACT_SHAKE && down&&pc_active)pc_input(7,0,0);
        else if(action==ACT_SCREENSHOT && down){char p[1200];snprintf(p,sizeof p,"%s/screenshot-%llu.png",save_dir,(unsigned long long)SDL_GetTicks());gfx_capture_window(p);}
        break; }
    case SDL_EVENT_GAMEPAD_ADDED:
        if(!pad){pad=SDL_OpenGamepad(e->gdevice.which);if(pad)hlog("Controller connected: %s",SDL_GetGamepadName(pad));}break;
    case SDL_EVENT_GAMEPAD_REMOVED:
        if(pad && SDL_GetGamepadID(pad)==e->gdevice.which){release_inputs();SDL_CloseGamepad(pad);pad=NULL;}break;
    case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
    case SDL_EVENT_GAMEPAD_BUTTON_UP: {
        int down=e->type==SDL_EVENT_GAMEPAD_BUTTON_DOWN;
        if(down)seen_device(1);
        for(unsigned i=0;i<sizeof pad_bindings/sizeof pad_bindings[0];i++)if(e->gbutton.button==pad_bindings[i].button){
            switch(pad_bindings[i].action){case ACT_PRESS:controller_down=pc_active?down:0;control_confirm(down);break;case ACT_COVER:if(pc_active)pad_cover=down;break;case ACT_PAUSE:if(down)control_pause();break;case ACT_BACK:if(down)control_back();break;case ACT_ZOOM_IN:if(down)pinch(1);break;case ACT_ZOOM_OUT:if(down)pinch(0);break;case ACT_SHAKE:if(down&&pc_active)pc_input(7,0,0);break;}break;
        }
        break; }
    }
}
static void load_test_script(void){
    if(!test_script[0])return;FILE *f=fopen(test_script,"rb");if(!f)return;char line[1400];
    while(fgets(line,sizeof line,f)&&test_count<256){if(line[0]=='#')continue;if(sscanf(line,"%lf %31s %1023[^\r\n]",&test_steps[test_count].at,test_steps[test_count].verb,test_steps[test_count].args)>=2)test_count++;}
    fclose(f);
}
static void run_test_script(double t){
    if(pending_tap && t>=tap_release_at){host_touch(3,0,tap_x,tap_y);pending_tap=0;}
    while(test_index<test_count && t>=test_steps[test_index].at){
        const char *v=test_steps[test_index].verb,*a=test_steps[test_index].args;float x=160,y=240,z=0;
        if(!strcmp(v,"tap")){sscanf(a,"%f %f",&tap_x,&tap_y);host_touch(0,0,tap_x,tap_y);pending_tap=1;tap_release_at=t+.08;}
        else if(!strcmp(v,"down")||!strcmp(v,"move")||!strcmp(v,"up")){sscanf(a,"%f %f",&x,&y);host_touch(!strcmp(v,"down")?0:!strcmp(v,"move")?1:3,0,x,y);}
        else if(!strcmp(v,"capture"))gfx_capture_window(a);
        else if(!strcmp(v,"accel")){sscanf(a,"%f %f %f",&x,&y,&z);host_accel(x,y,z);}
        else if(!strcmp(v,"pause"))rtx_start_button();
        else if(!strcmp(v,"zoom"))pinch(atoi(a)>0);
        else if(!strcmp(v,"pc")){int command=0;sscanf(a,"%d %f %f",&command,&x,&y);pc_input(command,x,y);}
        else if(!strcmp(v,"probe")){game_lock(&g_main_thread);hlog("PC probe %s: scene=%d mission=%d active=%d sight=(%.3f,%.3f) previous=(%.3f,%.3f)",a,w2c_mgst_mgst_pc_status(&g_inst,0),w2c_mgst_mgst_pc_status(&g_inst,1),w2c_mgst_mgst_pc_status(&g_inst,5),*(float *)MEM(0x84b0c),*(float *)MEM(0x84b10),*(float *)MEM(0x84ac8),*(float *)MEM(0x84acc));game_unlock(&g_main_thread);}
        else if(!strcmp(v,"patriots"))desktop_open_settings();
        else if(!strcmp(v,"pad")){int button=0,down=0;sscanf(a,"%d %d",&button,&down);SDL_Event e={0};e.type=down?SDL_EVENT_GAMEPAD_BUTTON_DOWN:SDL_EVENT_GAMEPAD_BUTTON_UP;e.gbutton.button=button;process_event(&e);}
        else if(!strcmp(v,"stick")){sscanf(a,"%f %f",&qa_ax,&qa_ay);qa_axes=1;seen_device(1);}
        else if(!strcmp(v,"rstick")){qa_ry=(float)atof(a);qa_axes=1;seen_device(1);}
        else if(!strcmp(v,"trigger")){seen_device(1);control_trigger(atoi(a)!=0);}
        else if(!strcmp(v,"doll_stick")){seen_device(1);doll_stick((float)atof(a));}
        else if(!strcmp(v,"rightstick")){sscanf(a,"%f %f",&x,&y);seen_device(1);doll_stick(x);final_boss_stick(x,y);}
        else if(!strcmp(v,"dodgeprobe")){game_lock(&g_main_thread);hlog("DODGE probe %s: mission=%d active=%d state=%d pose=%d frame=%d protected=%d",a,(int)w2c_mgst_mgst_pc_status(&g_inst,1),(int)w2c_mgst_mgst_pc_status(&g_inst,5),*(int *)MEM(0x84b50),*(int *)MEM(0x84be8),*(int *)MEM(0x84bec),*(unsigned char *)MEM(0x84c98));game_unlock(&g_main_thread);}
        else if(!strcmp(v,"qa_hold_doll")){game_lock(&g_main_thread);w2c_mgst_mgst_pc_qa_action(&g_inst,2);game_unlock(&g_main_thread);}
        else if(!strcmp(v,"qa_ending")){game_lock(&g_main_thread);w2c_mgst_mgst_pc_qa_action(&g_inst,3);game_unlock(&g_main_thread);}
        else if(!strcmp(v,"select")){control_refresh();int target=atoi(a);for(int n=0;n<64&&nav.index!=target;n++)control_move(1);}
        else if(!strcmp(v,"qa_doll")){game_lock(&g_main_thread);int hit=(int)w2c_mgst_mgst_pc_qa_action(&g_inst,0);game_unlock(&g_main_thread);hlog("QA doll collision result=%d",hit);}
        else if(!strcmp(v,"qa_die")){game_lock(&g_main_thread);w2c_mgst_mgst_rtx_set(&g_inst,2,0);w2c_mgst_mgst_pc_qa_action(&g_inst,1);game_unlock(&g_main_thread);}
        else if(!strcmp(v,"arm_retry"))qa_early_retry=atoi(a);
        else if(!strcmp(v,"bossprobe")){int q[10];game_lock(&g_main_thread);for(int n=0;n<10;n++)q[n]=(int)w2c_mgst_mgst_pc_boss_probe(&g_inst,n);game_unlock(&g_main_thread);hlog("BOSS probe %s: hp=%d ai=%d step=%d doll=%d fall=%d doll_hp=%d weapon=%d animation=%d life=%d",a,q[0],q[1],q[2],q[3],q[4],q[5],q[7],q[8],q[9]);}
        else if(!strcmp(v,"hover")){sscanf(a,"%f %f",&x,&y);seen_device(0);control_hover(x,y);}
        else if(!strcmp(v,"wheel")){seen_device(0);control_wheel((float)atof(a));}
        else if(!strcmp(v,"viewprobe")){game_lock(&g_main_thread);hlog("VIEW probe %s: scene=%d case=%d landscape=%d rotation=%d hover=%d selected=%d",a,(int)w2c_mgst_mgst_pc_status(&g_inst,0),(int)w2c_mgst_mgst_pc_status(&g_inst,8),(int)w2c_mgst_mgst_pc_status(&g_inst,7),g_cfg.rotate,nav_hover,nav.index);game_unlock(&g_main_thread);}
        else if(!strcmp(v,"scrollprobe")){game_lock(&g_main_thread);int extent=(int)w2c_mgst_mgst_pc_text_scroll(&g_inst,0,0),position=(int)w2c_mgst_mgst_pc_text_scroll(&g_inst,0,2);game_unlock(&g_main_thread);hlog("SCROLL probe %s: extent=%d position=%d",a,extent,position);}
        else if(!strcmp(v,"navprobe")){control_refresh();hlog("NAV probe %s: kind=%d index=%d count=%d busy=%d overlay_focus=%d pc=%d",a,nav.kind,nav.index,nav.count,nav.busy,pc_overlay_navigation(4,0),pc_active);}
        else if(!strcmp(v,"qa_complete")){game_lock(&g_main_thread);*(int *)MEM(0x84d78)=*(int *)MEM(0x84d68);game_unlock(&g_main_thread);}
        else if(!strcmp(v,"quit"))running=0;
        hlog("Test command: %.2f %s %s",t,v,a);test_index++;
    }
}
int main(int argc,char **argv) {
    pc_utf8_arguments(&argc,&argv);
    SDL_SetMainReady();
    if(!SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO|SDL_INIT_GAMEPAD)){MessageBoxA(NULL,SDL_GetError(),"MGS Touch",MB_ICONERROR);return 1;}
    snprintf(base_dir,sizeof base_dir,"%s",SDL_GetBasePath());
    unsigned identity=2166136261u;for(const unsigned char *c=(const unsigned char *)base_dir;*c;c++){unsigned v=*c>='A'&&*c<='Z'?*c+32:*c;identity=(identity^v)*16777619u;}
    char mutex_name[96];snprintf(mutex_name,sizeof mutex_name,"Local\\PatriotsMGSTouchGame_%08x",identity);
    HANDLE game_mutex=CreateMutexA(NULL,TRUE,mutex_name);
    if(game_mutex&&GetLastError()==ERROR_ALREADY_EXISTS){HWND other=FindWindowW(NULL,L"METAL GEAR SOLID TOUCH | Patriots");if(other){ShowWindow(other,SW_RESTORE);SetForegroundWindow(other);}CloseHandle(game_mutex);SDL_Quit();return 0;}
    path_join(g_cfg.app_dir,sizeof g_cfg.app_dir,base_dir,"Assets/MGSTUS.app");
    path_join(font_dir,sizeof font_dir,base_dir,"Assets/fonts");
    path_join(save_dir,sizeof save_dir,base_dir,"../Saves");_mkdir(save_dir);
    snprintf(g_cfg.docs_dir,sizeof g_cfg.docs_dir,"%s",save_dir);
    path_join(g_cfg.overlay_dir,sizeof g_cfg.overlay_dir,base_dir,"languages/tr");
    for(int i=0;i<ACT_COUNT;i++)bindings[i].key=SDL_GetScancodeFromName(bindings[i].default_key);
    load_config();
    for(int i=1;i<argc;i++){
        if(!strcmp(argv[i],"--fullscreen"))fullscreen=1;
        else if(!strcmp(argv[i],"--windowed"))fullscreen=0;
        else if(!strcmp(argv[i],"--trace"))g_cfg.trace=1;
        else if(!strcmp(argv[i],"--hidden-test"))qa_hidden=1;
        else if(!strcmp(argv[i],"--test-seconds") && i+1<argc)stop_after=atof(argv[++i]);
        else if(!strcmp(argv[i],"--capture") && i+1<argc)snprintf(capture_file,sizeof capture_file,"%s",argv[++i]);
        else if(!strcmp(argv[i],"--capture-at") && i+1<argc)capture_at=atof(argv[++i]);
        else if(!strcmp(argv[i],"--script") && i+1<argc)snprintf(test_script,sizeof test_script,"%s",argv[++i]);
        else if(!strcmp(argv[i],"--save-dir") && i+1<argc)snprintf(save_dir,sizeof save_dir,"%s",argv[++i]);
        else if(!strcmp(argv[i],"--language") && i+1<argc)snprintf(g_cfg.lang,sizeof g_cfg.lang,"%s",!strcmp(argv[++i],"tr")?"Turkish":"English");
    }
    qa_mode=stop_after>0||test_script[0];
    snprintf(g_cfg.docs_dir,sizeof g_cfg.docs_dir,"%s",save_dir);_mkdir(save_dir);load_test_script();
    if(strcmp(g_cfg.lang,"Turkish"))g_cfg.overlay_dir[0]=0;
    char p[1200];path_join(p,sizeof p,save_dir,"runtime.log");logfile=fopen(p,"wb");
    hlog("Patriots MGS Touch Windows AOT host; language=%s",g_cfg.lang);
    load_runtime_texts();
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,2);SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,1);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER,1);SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE,0);
    window=SDL_CreateWindow("METAL GEAR SOLID TOUCH | Patriots",1280,800,SDL_WINDOW_OPENGL|SDL_WINDOW_RESIZABLE|SDL_WINDOW_HIGH_PIXEL_DENSITY|((qa_mode&&qa_hidden)?SDL_WINDOW_HIDDEN:0));
    if(!window){hlog("Window failed: %s",SDL_GetError());return 2;}
    set_window_icon();
    SDL_SetWindowMinimumSize(window,640,480);
    SDL_GLContext context=SDL_GL_CreateContext(window);
    if(!context){hlog("OpenGL failed: %s",SDL_GetError());return 3;}
    SDL_GL_MakeCurrent(window,context);SDL_GL_SetSwapInterval(vsync);
    if(fullscreen)SDL_SetWindowFullscreen(window,true);
    gfx_init(320,480);resize();
    char regular[1200],bold[1200],cjk[1200],display[1200];
    path_join(regular,sizeof regular,font_dir,"LiberationSans-Regular.ttf");path_join(bold,sizeof bold,font_dir,"LiberationSans-Bold.ttf");
    path_join(cjk,sizeof cjk,font_dir,"DroidSansFallbackFull.ttf");path_join(display,sizeof display,font_dir,"BebasNeue-Regular.ttf");
    if(text_init(regular,bold,cjk,display)){hlog("Font initialization failed");return 4;}
    platform_vibrate=vibrate;rtx_init();base_overlay=g_ext.overlay;g_ext.overlay=desktop_overlay;
    g_ext.fill=fill_mode;g_ext.render_scale=scale;
    started=host_start()==0;if(!started){hlog("Game boot failed");return 5;}
    pc_input(0,1,0);
    audio_init(48000);
    SDL_AudioSpec spec={SDL_AUDIO_S16,2,48000};
    audio=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,audio_callback,NULL);
    if(audio)SDL_ResumeAudioStreamDevice(audio);else hlog("Audio unavailable: %s",SDL_GetError());
    for(int i=0;i<24;i++)host_accel(-1,0,0);
    double begin=host_now();int captured=0;
    while(running && !host_is_crashed()) {
        Uint64 tick=SDL_GetTicksNS();SDL_Event event;
        update_pc_mode();
        control_refresh();
        if(qa_mode&&qa_early_retry&&nav.kind==3&&nav.busy){hlog("QA early result confirmation, mode=%d",qa_early_retry);if(qa_early_retry==2){control_trigger(0);control_trigger(1);control_trigger(0);}else{control_confirm(1);control_confirm(0);}qa_early_retry=0;}
        while(SDL_PollEvent(&event)){
            if(qa_mode&&(event.type==SDL_EVENT_KEY_DOWN||event.type==SDL_EVENT_KEY_UP||event.type==SDL_EVENT_MOUSE_MOTION||event.type==SDL_EVENT_MOUSE_BUTTON_DOWN||event.type==SDL_EVENT_MOUSE_BUTTON_UP||event.type==SDL_EVENT_MOUSE_WHEEL||event.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN||event.type==SDL_EVENT_GAMEPAD_BUTTON_UP))continue;
            process_event(&event);
        }
        if(focused&&!qa_mode)poll_pad();
        if(qa_mode&&qa_axes){control_axis(qa_ax,qa_ay);control_scroll(qa_ry);}
        double now=host_now();
        control_tap_frame(now);
        if(ready_pending&&now>=ready_release){host_touch(3,0,20,460);ready_pending=0;}
        if(pc_active&&(mouse_down||key_down||controller_down||trigger_fire)&&now>=next_fire){pc_input(2,0,0);next_fire=now+.14;}
        run_test_script(now-begin);
        host_accel(-1,0,0);
        game_state=module_state();
        if((game_state&1)||game_landscape)last_mission_rotation=(game_state&4)?90:270;
        else if(!(game_state&2))last_mission_rotation=0;
        g_cfg.rotate=last_mission_rotation;
        if(capture_file[0] && !captured && now-begin>=capture_at){gfx_capture_window(capture_file);captured=1;}
        host_frame(now);rtx_frame(now);write_status(now);
        if(stop_after>0 && now-begin>=stop_after)break;
        Uint64 elapsed=SDL_GetTicksNS()-tick,target=1000000000ULL/(unsigned)max_fps;
        if(elapsed<target)SDL_DelayNS(target-elapsed);
    }
    release_inputs();host_lifecycle(0);
    if(audio)SDL_DestroyAudioStream(audio);
    if(pad)SDL_CloseGamepad(pad);
    int result=host_is_crashed()?6:0;hlog("Audio mixed frames=%lld; non-silent buffers=%lld",(long long)mixed_frames,(long long)audible_buffers);hlog("Game closed; result=%d",result);
    /* Original detached game worker threads terminate with this process. */
    if(logfile)fclose(logfile);
    return result;
}
