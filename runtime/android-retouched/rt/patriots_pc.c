/* SPDX-License-Identifier: MIT
 * Small typed runtime interface for desktop integrations. No fabricated progress.
 */
#include "rt.h"
int *rtxf_scene(void *d);
int *rtxf_case(void *d);
int rtxf_pc_active(void *d);
int rtxf_pc_ready(void *d);
int rtxf_pc_landscape(void *d);
int rtxf_pc_case(void *d);
void rtxf_pc_apply(void *d, int cover, int fire, int zoom, float dx, float dy, int weapon);
void rtxf_pc_prepare_scene(void *d);
void rtxf_pc_navigation(void *d,int menu,float bar_h,int *out);
float rtxf_pc_scroll(void *d,int menu,float bar_h,int index);
void *rtxf_pc_scroll_object(void *d);
void *rtxf_menu_bar(void *d);
int rtxf_pc_text_scroll(void *d,float delta,int query);
void *rtxf_pc_mantis_doll(void *boss);
int rtxf_pc_mantis_probe(void *boss,int field);
void rtxf_pc_qa_ending(void *delegate);
static int pc_enabled,pc_cover,pc_fire,pc_zoom,pc_dodge,pc_shake;
static float pc_dx,pc_dy;
static u32 pc_delegate(void) {
    u32 app=(u32)msg_sendv(class_named("UIApplication"),"sharedApplication",0);
    return app?(u32)msg_sendv(app,"delegate",0):0;
}
EXPORT(mgst_pc_text_scroll) int mgst_pc_text_scroll(float delta,int query){
    u32 d=pc_delegate();return d?rtxf_pc_text_scroll(P(d),delta,query):0;
}
EXPORT(mgst_pc_boss_probe) int mgst_pc_boss_probe(int field){
    if(field==7)return (int)msg_sendv(class_named("Player"),"getWeapon",0);
    if(field==8)return *(int *)P(0x84becu);
    if(field==9)return *(int *)P(0x84b54u);
    if((int)msg_sendv(class_named("Stage"),"getNum",0)!=18)return -1;
    u32 boss=(u32)msg_sendv(class_named("EnemyManager"),"enemyOfType:",1,12);
    return rtxf_pc_mantis_probe(P(boss),field);
}
/* Deterministic QA fixtures; the host only calls this from its test-script path.
 * Damage and pickup still use the original game's collision/death handlers. */
EXPORT(mgst_pc_qa_action) int mgst_pc_qa_action(int command){
    if(command==3){u32 d=pc_delegate();if(d)rtxf_pc_qa_ending(P(d));return d!=0;}
    if(command==1){msg_sendv(class_named("Player"),"setDamage:::",3,999,0x43700000u,0x43200000u);return 1;}
    if(command==2){msg_sendv(class_named("Player"),"setDoll",0);return 1;}
    if(command==0&&(int)msg_sendv(class_named("Stage"),"getNum",0)==18){
        u32 boss=(u32)msg_sendv(class_named("EnemyManager"),"enemyOfType:",1,12);
        u32 doll=A(rtxf_pc_mantis_doll(P(boss)));
        struct{float x,y,w,h;} rect={-64,-64,1024,768};
        return doll?(int)msg_sendv(doll,"checkCollisionWithBullet_Dmg:weaponType:damage:",3,A(&rect),1,99):0;
    }
    return 0;
}
EXPORT(mgst_pc_nav) int mgst_pc_nav(int field,int index){
    static int nav[200];
    u32 d=pc_delegate();
    if(field==0||field==11){
        if(!d)return 0;
        int menu=(int)msg_sendv(d,"GetMenuNum:",1,*rtxf_scene(P(d)));
        int scene=*rtxf_scene(P(d));
        union{u32 bits;float value;} h={0};h.value=32;
        if(menu>=0&&menu<=10&&scene!=8&&scene!=6&&*rtxf_case(P(d))==1){
            u32 bar=A(rtxf_menu_bar(P(d)));if(bar)h.bits=(u32)msg_sendv(bar,"getImgH",0);
        }
        if(field==11){
            if(nav[0]==1){
                union{float value;u32 bits;} position={rtxf_pc_scroll(P(d),menu,h.value,index)};
                msg_sendv(A(rtxf_pc_scroll_object(P(d))),"setScrollPos:",1,position.bits);
            }
            return 0;
        }
        rtxf_pc_navigation(P(d),menu,h.value,nav);
    }
    if(field>=0&&field<8)return nav[field];
    if(index>=0&&index<64&&field>=8&&field<=10)return nav[8+index*3+field-8];
    return 0;
}
EXPORT(mgst_pc_status) int mgst_pc_status(int key) {
    u32 d=pc_delegate();
    switch(key) {
    case 0: return d?*rtxf_scene(P(d)):-1;
    case 1: return (int)msg_sendv(class_named("Stage"),"getNum",0);
    case 2: return (int)msg_sendv(class_named("Stage"),"getBgNum",0);
    case 3: return *(int *)P(0x84b44u); /* Player_s_hp, pinned executable SHA256 */
    case 4: return *(int *)P(0x84b48u); /* Player_s_maxHp */
    case 5: return d && rtxf_pc_active(P(d)) && (int)msg_sendv(class_named("Player"),"getControlMode",0)==1;
    case 6: return d && rtxf_pc_ready(P(d));
    case 7: return d && rtxf_pc_landscape(P(d));
    case 8: return d?rtxf_pc_case(P(d)):-1;
    case 9: return (int)msg_sendv(class_named("Player"),"getWeapon",0);
    }
    return -1;
}
EXPORT(mgst_pc_input) void mgst_pc_input(int command,float x,float y) {
    switch(command){
    case 0:pc_enabled=x!=0;break;
    case 1:pc_dx+=x;pc_dy+=y;break;
    case 2:if((int)msg_sendv(class_named("Player"),"getWeapon",0)!=6)pc_fire=1;break;
    case 3:pc_cover=x!=0;break;
    case 4:{int weapon=(int)msg_sendv(class_named("Player"),"getWeapon",0);if((x>0&&weapon==0)||(x<=0&&weapon==1))pc_zoom=x>0?1:-1;break;}
    case 5:pc_fire=pc_zoom=pc_dodge=pc_shake=0;pc_dx=pc_dy=0;pc_cover=1;break;
    case 6:pc_dodge=x<0?1:2;break;
    case 7:pc_shake=1;break;
    }
}
/* Called immediately before the game's own Player controller reads UIKit state. */
void patriots_pc_before_controller(void){
    u32 d=pc_delegate();
    if(!pc_enabled || !d || !rtxf_pc_active(P(d)))return;
    if((int)msg_sendv(class_named("Player"),"getControlMode",0)!=1){pc_dx=pc_dy=0;return;}
    int weapon=(int)msg_sendv(class_named("Player"),"getWeapon",0);
    /* Deliver the gesture in the same game tick that reads it. Two desktop
     * accelerometer calls could previously be cleared before this 20 Hz tick. */
    if(pc_shake){u32 shake=*(u32 *)P(0x69038u);if(shake)*(u8 *)P(shake)=1;pc_shake=0;}
    /* private_getRotPoint(160,240,90) = (240,160). These two pinned
     * image fields are the original MoveSight previous-touch coordinates. */
    *(float *)P(0x84ac8u)=240;*(float *)P(0x84accu)=160;
    rtxf_pc_apply(P(d),pc_cover,pc_fire,pc_zoom,pc_dx,pc_dy,weapon);
    pc_fire=pc_zoom=0;pc_dx=pc_dy=0;
}
void patriots_pc_before_scene(void){u32 d=pc_delegate();if(pc_enabled&&d)rtxf_pc_prepare_scene(P(d));}
int patriots_pc_flick(const u32 *args,u64 *result){
    u32 d=pc_delegate();if(!pc_enabled||!d||!rtxf_pc_active(P(d)))return 0;
    if((int)msg_sendv(class_named("Stage"),"getNum",0)!=20)return 0;
    int want=(int)args[1]?1:2;*result=pc_dodge==want;if(*result)pc_dodge=0;return 1;
}
