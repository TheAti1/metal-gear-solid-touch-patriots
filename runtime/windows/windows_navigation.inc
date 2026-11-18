/* SPDX-License-Identifier: MIT -- shared keyboard/gamepad menu actions. */
int pc_overlay_navigation(int command,int delta);
void pc_overlay_hover(float vx,float vy);
void gfx_view_to_window(float vx,float vy,float *wx,float *wy);
static struct {int kind,count,key,busy,back,index;float bx,by,x[64],y[64];int enabled[64];} nav;
static int nav_context=-1,nav_wait_neutral,nav_axis_dir,nav_visual;
static int nav_hover=-1,nav_keyboard;
static double nav_repeat_at;
static int nav_tap_pending;
static float nav_tap_x,nav_tap_y;
static double nav_tap_until;
static int confirm_queued,confirm_context,menu_trigger_armed=1,menu_trigger_previous;
static double confirm_deadline;
static void control_confirm(int down);
static double text_scroll_time;
static void control_scroll(float ry){
    double now=host_now(),dt=text_scroll_time?now-text_scroll_time:0;text_scroll_time=now;
    if(dt<0||dt>.1)dt=0;
    if(pc_active||pc_overlay_navigation(0,0)||fabsf(ry)<.01f)return;
    game_lock(&g_main_thread);w2c_mgst_mgst_pc_text_scroll(&g_inst,ry*220*(float)dt,1);game_unlock(&g_main_thread);
}
static void control_refresh(void){
    int overlay=pc_overlay_navigation(0,0),context;
    if(overlay){nav.kind=10+overlay;nav.count=nav.back=nav.busy=0;context=100000+overlay;}
    else if(pc_active){nav.kind=nav.count=nav.back=nav.busy=0;context=-2;}
    else{
        game_lock(&g_main_thread);
        nav.kind=w2c_mgst_mgst_pc_nav(&g_inst,0,0);
        nav.count=w2c_mgst_mgst_pc_nav(&g_inst,1,0);
        nav.key=w2c_mgst_mgst_pc_nav(&g_inst,2,0);
        nav.busy=w2c_mgst_mgst_pc_nav(&g_inst,3,0);
        nav.bx=(int)w2c_mgst_mgst_pc_nav(&g_inst,4,0)/1000.0f;
        nav.by=(int)w2c_mgst_mgst_pc_nav(&g_inst,5,0)/1000.0f;
        nav.back=w2c_mgst_mgst_pc_nav(&g_inst,6,0);
        if(nav.count<0||nav.count>64)nav.count=0;
        for(int i=0;i<nav.count;i++){
            nav.x[i]=(int)w2c_mgst_mgst_pc_nav(&g_inst,8,i)/1000.0f;
            nav.y[i]=(int)w2c_mgst_mgst_pc_nav(&g_inst,9,i)/1000.0f;
            nav.enabled[i]=w2c_mgst_mgst_pc_nav(&g_inst,10,i);
        }
        game_unlock(&g_main_thread);
        /* Original GameScene case 11 is the post-death advice screen. It uses
         * the same UIKit Next rectangle as pre-mission advice (case 0), but is
         * a distinct scene case and must also receive controller confirmation. */
        if(!nav.kind&&game_scene==8&&game_case==11){
            nav.kind=2;nav.count=1;nav.key=8*256+11*8;nav.busy=nav.back=0;
            nav.x[0]=20;nav.y[0]=460;nav.enabled[0]=1;
        }
        context=nav.kind?nav.key:0;
    }
    if(context!=nav_context){
        confirm_queued=0;
        nav_context=context;nav.index=0;nav_axis_dir=0;nav_wait_neutral=1;
        nav_visual=input_device==1||nav_keyboard;nav_hover=-1;
        while(nav.index+1<nav.count&&!nav.enabled[nav.index])nav.index++;
        if(nav.kind==1)for(int i=0;i<nav.count;i++)if(nav.enabled[i]&&nav.x[i]>100&&nav.y[i]>284&&nav.y[i]<442){nav.index=i;break;}
        hlog("Control context: kind=%d count=%d key=%d",nav.kind,nav.count,context);
    }
    if(nav.index>=nav.count)nav.index=0;
}
static void control_tap(float x,float y){
    if(nav_tap_pending)return;
    nav_tap_x=x;nav_tap_y=y;nav_tap_pending=1;nav_tap_until=host_now()+.10;
    host_touch(0,0,x,y);
}
static void control_tap_frame(double now){
    if(nav_tap_pending&&now>=nav_tap_until){host_touch(3,0,nav_tap_x,nav_tap_y);nav_tap_pending=0;}
    if(confirm_queued){
        if(now>confirm_deadline||nav_context!=confirm_context)confirm_queued=0;
        else if(!nav.busy){confirm_queued=0;hlog("Deferred result confirm delivered");control_confirm(1);}
    }
}
static void control_move(int direction){
    confirm_queued=0;
    control_refresh();nav_visual=1;
    if(nav.kind>=10){pc_overlay_navigation(1,direction);return;}
    if(!nav.count||nav.busy)return;
    int next=nav.index;
    for(int n=0;n<nav.count;n++){next=(next+(direction>0?1:nav.count-1))%nav.count;if(nav.enabled[next])break;}
    nav.index=next;
    game_lock(&g_main_thread);w2c_mgst_mgst_pc_nav(&g_inst,11,nav.index);game_unlock(&g_main_thread);
    control_refresh();
}
static void control_confirm(int down){
    control_refresh();
    if(!down){rtx_pad_button(0);return;}
    nav_visual=1;
    if(nav.kind>=10){pc_overlay_navigation(2,0);return;}
    if(pc_active){pc_input(2,0,0);next_fire=host_now()+.14;return;}
    if(nav.kind){
        if(nav.kind==3&&nav.busy){confirm_queued=1;confirm_context=nav_context;confirm_deadline=host_now()+2.5;hlog("Result confirm queued during animation");return;}
        if(nav.count&&!nav.busy&&nav.enabled[nav.index]){confirm_queued=0;hlog("Menu confirm: kind=%d item=%d at=%.1f,%.1f",nav.kind,nav.index,nav.x[nav.index],nav.y[nav.index]);control_tap(nav.x[nav.index],nav.y[nav.index]);}return;
    }
    if(pc_ready||game_scene==6){ready_tap();return;}
    if(game_scene==0||game_scene==8||game_scene==11)return;
    rtx_pad_button(1);
}
static void control_trigger(int down){
    if(pc_active){trigger_fire=down;menu_trigger_armed=!down;menu_trigger_previous=down;return;}
    trigger_fire=0;
    if(!down){menu_trigger_armed=1;menu_trigger_previous=0;return;}
    if(menu_trigger_armed&&!menu_trigger_previous){menu_trigger_armed=0;control_confirm(1);}
    menu_trigger_previous=down;
}
static void control_back(void){
    confirm_queued=0;
    control_refresh();
    if(nav.kind>=10){pc_overlay_navigation(3,0);return;}
    if(pc_active){release_inputs();rtx_back();return;}
    if(nav.kind==3){nav.index=1;nav_visual=1;return;} /* EXIT must still be confirmed. */
    if(nav.back&&!nav.busy){control_tap(nav.bx,nav.by);return;}
    if(rtx_back_wanted())rtx_back();
}
static void control_pause(void){
    control_refresh();
    if(nav.kind>=10){pc_overlay_navigation(3,0);return;}
    if(pc_active){release_inputs();rtx_start_button();return;}
    control_confirm(1);
}
static void control_axis(float ax,float ay){
    if(pc_active)return;
    control_refresh();
    int dir=fabsf(ay)>=.55f?(ay>0?1:-1):fabsf(ax)>=.55f?(ax>0?1:-1):0;
    if(!dir){nav_wait_neutral=0;nav_axis_dir=0;rtx_pad_axis(0,0);return;}
    if(!nav.kind){if(game_scene==0||game_scene==6||game_scene==8||game_scene==11)rtx_pad_axis(0,0);else rtx_pad_axis(ax,ay);return;}
    rtx_pad_axis(0,0);
    if(nav_wait_neutral)return;
    double now=host_now();
    if(dir!=nav_axis_dir||now>=nav_repeat_at){int first=dir!=nav_axis_dir;control_move(dir);nav_axis_dir=dir;nav_repeat_at=now+(first?.36:.15);}
}
static int control_wheel(float steps){
    if(pc_active||pc_overlay_navigation(0,0))return 0;
    game_lock(&g_main_thread);
    int extent=(int)w2c_mgst_mgst_pc_text_scroll(&g_inst,0,0);
    if(extent>0)w2c_mgst_mgst_pc_text_scroll(&g_inst,-steps*55,1);
    game_unlock(&g_main_thread);return extent>0;
}
static void control_target_bounds(int i,float *l,float *t,float *r,float *b){
    float x=nav.x[i],y=nav.y[i];
    if(nav.kind==1&&x>100){*l=10;*r=310;*t=fmaxf(284,y-16);*b=fminf(444,y+16);}
    else{*l=nav.kind==3?40:0;*r=nav.kind==3?100:50;*t=y<100?0:380;*b=y<100?100:480;}
}
static void control_hover(float x,float y){
    nav_keyboard=0;nav_visual=0;nav_hover=-1;
    if(pc_active)return;
    control_refresh();
    if(nav.kind>=10){pc_overlay_hover(x,y);return;}
    if(nav.busy)return;
    for(int i=0;i<nav.count;i++){
        float l,t,r,b;control_target_bounds(i,&l,&t,&r,&b);
        if(nav.enabled[i]&&x>l&&x<r&&y>t&&y<b){if(nav.index!=i)confirm_queued=0;nav_hover=i;nav.index=i;break;}
    }
}
static void control_draw_focus(void){
    if(pc_active||nav.kind>=10||nav.busy||!nav.count)return;
    int i=nav_visual?nav.index:nav_hover;if(i<0||i>=nav.count)return;
    float l,t,r,b,a0,b0,a1,b1;control_target_bounds(i,&l,&t,&r,&b);
    if(t>=b||nav.y[i]<0||nav.y[i]>480)return;
    gfx_view_to_window(l,t,&a0,&b0);gfx_view_to_window(r,b,&a1,&b1);
    ui_fill(fminf(a0,a1),fminf(b0,b1),fabsf(a1-a0),fabsf(b1-b0),(Col){.35f,.68f,.20f,.36f});
}
