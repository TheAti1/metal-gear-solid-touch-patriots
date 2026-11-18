/* SPDX-License-Identifier: MIT
 * Use recovered types for the PC mouse/keyboard/controller bridge. The original
 * Player code still performs firing, cooldowns, cover, damage and weapon changes.
 */
#include "mgst_types.fixed.h"
int rtxf_pc_active(void *delegate){
    CrashLandingAppDelegate *d=delegate;
    return d->_Scene==8 && d->_case==1 && d->sh_case==0 && !d->SleepOn && d->glView;
}
int rtxf_pc_ready(void *delegate){CrashLandingAppDelegate *d=delegate;return d->_Scene==8 && ((d->_case==1 && d->sh_case==3)||(d->_case==0 && d->advice_case==1)) && !d->SleepOn;}
int rtxf_pc_landscape(void *delegate){CrashLandingAppDelegate *d=delegate;return d->_Scene==6||d->_Scene==8||d->_Scene==13||(d->_Scene==21&&(d->_case==7||d->_case==9));}
int rtxf_pc_case(void *delegate){return ((CrashLandingAppDelegate *)delegate)->_case;}
void rtxf_pc_prepare_scene(void *delegate){
    CrashLandingAppDelegate *d=delegate;
    /* The mandatory first-run phone-gesture slideshow is replaced by PC hints.
     * Let the original final-page handler release its textures and save the flag. */
    if(d->_Scene==17 && d->_case==7 && d->manual_pass_flag){
        d->manual_select_num=7;d->manual_txt_flg=1;d->bar_anim_cnt=1;
    }
}
/* Navigation targets come from the recovered menu data, in original UIKit
 * coordinates. Results and story buttons use their original hit rectangles. */
void rtxf_pc_navigation(void *delegate,int menu,float bar_h,int *out){
    CrashLandingAppDelegate *d=delegate;
    for(int i=0;i<200;i++)out[i]=0;
    out[2]=d->_Scene*256+d->_case*8;
    out[7]=d->sh_case;
    if(d->SleepOn)return;
    /* Survival-mode unlock advice after the last boss uses the same original
     * landscape Next button as mission advice, outside the gameplay scene. */
    if(d->_Scene==13){
        if(d->_case==1&&d->advice_case==1){
            out[0]=2;out[1]=1;out[3]=d->bar_anim_cnt>0||d->back_anim_cnt>0;
            out[8]=20000;out[9]=460000;out[10]=1;
        }
        return;
    }
    if(d->_Scene==8){
        if(d->_case==0&&d->advice_case==1){out[0]=2;out[1]=1;out[8]=20000;out[9]=460000;out[10]=1;return;}
        if(d->_case!=1)return;
        if(d->sh_case==3){out[0]=2;out[1]=1;out[8]=20000;out[9]=460000;out[10]=1;return;}
        if(d->sh_case==1||d->sh_case==2){
            out[0]=3;out[1]=2;out[2]+=d->sh_case;
            out[3]=d->result_effect!=4;
            out[8]=70000;out[9]=430000;out[10]=1;
            out[11]=70000;out[12]=50000;out[13]=1;
        }
        return;
    }
    if(d->_Scene==6){
        if(d->_case!=1)return;
        out[0]=2;out[1]=1;out[2]+=d->flg_storytxt;
        out[3]=d->bar_anim_cnt>0||d->back_anim_cnt>0;
        out[8]=20000;out[9]=460000;out[10]=1;
        out[4]=20000;out[5]=40000;out[6]=1;return;
    }
    if(d->_Scene==21&&d->_case==7){
        out[0]=5;out[1]=d->history_txt_flg?1:2;out[2]+=d->history_txt_flg;
        out[3]=d->bar_anim_cnt>0||d->back_anim_cnt>0;
        out[4]=20000;out[5]=40000;out[6]=1;
        out[8]=20000;out[9]=d->history_txt_flg?40000:460000;out[10]=1;
        out[11]=20000;out[12]=40000;out[13]=1;return;
    }
    if(d->flg_help){
        out[0]=4;out[1]=1;out[2]+=4;out[4]=20000;out[5]=460000;out[6]=1;
        out[8]=20000;out[9]=460000;out[10]=1;return;
    }
    if(menu<0||menu>10||d->_case!=1)return;
    struct CrashLandingAppDelegate_menu_data *m=&d->menu_data[menu];
    if(m->max_num<1||m->max_num>60||!m->select_flag)return;
    out[0]=1;out[1]=m->max_num;
    out[3]=d->immueMenuTouch||d->bar_anim_cnt>0||d->back_anim_cnt>0;
    float stride=bar_h+8;if(stride<20||stride>100)stride=40;
    for(int i=0;i<m->max_num;i++){
        out[8+i*3]=160000;
        out[9+i*3]=(int)((284+d->menu_scr_pos.y+i*stride+(stride-8)/2)*1000);
        out[10+i*3]=m->select_flag[i]!=(char)-1&&m->move_num[i]!=23;
    }
    if(m->back_num>=0){
        int i=out[1]++;out[4]=20000;out[5]=460000;out[6]=1;
        out[8+i*3]=out[4];out[9+i*3]=out[5];out[10+i*3]=1;
    }
}
float rtxf_pc_scroll(void *delegate,int menu,float bar_h,int index){
    CrashLandingAppDelegate *d=delegate;
    if(menu<0||menu>10||index<0||index>=d->menu_data[menu].max_num)return d->menu_scr_pos.y;
    float stride=bar_h+8;if(stride<20||stride>100)stride=40;
    int top=index>2?index-2:0,max=d->menu_data[menu].max_num-4;if(max<0)max=0;if(top>max)top=max;
    d->menu_scr_pos.y=-top*stride;d->MenuMoveflg=0;
    return d->menu_scr_pos.y;
}
void *rtxf_pc_scroll_object(void *delegate){return ((CrashLandingAppDelegate *)delegate)->menu_scroll;}
void rtxf_pc_qa_ending(void *delegate){
    /* QA-only fixture: let original GameScene create/release all advice assets. */
    CrashLandingAppDelegate *d=delegate;
    d->_Scene=13;d->_case=0;d->Load_count=0;d->advice_case=0;
}
void *rtxf_pc_mantis_doll(void *boss){return boss?((Mantis *)boss)->doll[0]:0;}
int rtxf_pc_mantis_probe(void *boss,int field){
    if(!boss)return -1;Mantis *m=boss;Doll *d=m->doll[0];
    switch(field){case 0:return m->pEneDat?m->pEneDat->param.hp:-1;case 1:return m->aiControl;case 2:return m->aiStep;case 3:return d?d->step:-1;case 4:return d?d->fallStep:-1;case 5:return d?d->HP:-1;}
    return -1;
}
int rtxf_pc_text_scroll(void *delegate,float delta,int query){
    CrashLandingAppDelegate *d=delegate;
    if(d->SleepOn||d->bar_anim_cnt>0||d->back_anim_cnt>0)return 0;
    MenuScroll *s=0;float *position=0;
    if(d->_Scene==6&&d->_case==1&&d->flg_storytxt){s=d->menu_scroll;position=&d->story_scr_y;}
    else if(d->flg_help){s=d->plus_scroll;position=&d->help_scr_y;}
    else if(d->_Scene==21&&d->_case==7&&d->history_txt_flg){s=d->menu_scroll;position=&d->history_scr_y;}
    if(!s||!s->isScroll)return 0;
    float extent=s->scrollSize.width>s->scrollSize.height?s->scrollSize.width:s->scrollSize.height;
    if(extent<=0||extent>100000)return 0;
    if(query==0)return (int)(extent*1000);
    if(query==1&&delta==delta){
        float next=s->scrollPos-delta;if(next>0)next=0;if(next<-extent)next=-extent;
        s->scrollPos=s->scrollPosPrv=s->scrollPosOld=next;
        s->scrollPosOver=s->scrollPosOverDef=s->scrollReflectCnt=s->scrollReflectValue=0;
        s->isFlick=s->isMove=s->touchFlag=0;
        *position=next;d->MenuMoveflg=0;
    }
    return (int)(s->scrollPos*1000);
}
void rtxf_pc_apply(void *delegate,int cover,int fire,int zoom,float dx,float dy,int weapon){
    CrashLandingAppDelegate *d=delegate;
    MyEAGLView *v=d->glView;
    static int zoom_frames;static float zoom_ratio=2;
    /* Player treats a negative previous touch coordinate as "no finger".
     * A relative PC pointer must never accumulate an unbounded UIKit position.
     * Each frame starts at the same positive anchor; the bridge rebases Player's
     * previous position to that anchor before its original movement code runs. */
    if(dx!=dx)dx=0;if(dy!=dy)dy=0;
    if(dx>120)dx=120;if(dx<-120)dx=-120;
    if(dy>200)dy=200;if(dy<-200)dy=-200;
    float px=160+dx,py=240+dy;
    v->touchFlag[0]=cover||(fire&&weapon>=4)?0:1;v->touchFlag[1]=0;
    v->touch_in[0]=0;v->touch_out[0]=fire&&!cover;v->touch_move[0]=fire?0:1;
    v->touch_time[0]=fire?0:5;v->touch_move_time[0]=5;
    v->startTouchPos[0].x=px;v->startTouchPos[0].y=py;
    v->moveTouchPos[0]=v->startTouchPos[0];
    if(zoom){zoom_frames=2;zoom_ratio=zoom>0?3.0f:1.0f;}
    v->MultiTouchflg=zoom_frames>0;
    if(zoom_frames>0){
        v->StandardDistance=6400;v->StandardRatio=zoom_ratio;
        v->moveTouchPos[0].x=px-40;v->moveTouchPos[0].y=py;
        v->moveTouchPos[1].x=px+40;v->moveTouchPos[1].y=py;
        zoom_frames--;
    }
}
