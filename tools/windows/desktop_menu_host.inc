/* SPDX-License-Identifier: MIT -- semantic navigation for the desktop pause UI. */
float pc_controller_speed(void){static const float speeds[]={.65f,1.0f,1.6f};return speeds[S.pad_speed<0?0:S.pad_speed>2?2:S.pad_speed];}
int pc_overlay_navigation(int command,int delta){
    int kind=msg[0]?3:screen==SCR_PAUSE?(quit_confirm?2:1):0;
    if(!command)return kind;
    if(command==4)return quit_confirm?quit_focus:pause_focus;
    if(!kind)return 0;
    if(command>=1&&command<=3)overlay_mouse=0;
    if(command==1){
        if(kind==1)pause_focus=(pause_focus+(delta>0?1:2))%3;
        if(kind==2)quit_focus=!quit_focus;
    }else if(command==2){
        if(kind==3){msg[0]=0;if(restart_pending)rtx_plat_restart();}
        else if(kind==2){if(quit_focus==0)do_quit_mission();else quit_confirm=0;}
        else if(pause_focus==0)do_resume();
        else if(pause_focus==1)desktop_open_settings();
        else{quit_confirm=1;quit_focus=1;}
    }else if(command==3){
        if(kind==2)quit_confirm=0;
        else if(kind==1)do_resume();
        else msg[0]=0;
    }
    return 1;
}
void pc_overlay_hover(float vx,float vy){
    if(screen!=SCR_PAUSE)return;
    ui_set_space(1,!(st&ST_INCLINATION));float x,y;ui_to_ui(vx,vy,&x,&y);
    overlay_mouse=1;pause_hover=quit_hover=-1;
    float W=ui_w(),H=ui_h();
    if(quit_confirm){
        float bw=W<300?W-40:260,bh=120,bx=(W-bw)/2,by=(H-bh)/2,yy=by+bh-46;
        if(y>yy&&y<yy+34){if(x>bx+14&&x<bx+114)quit_hover=0;else if(x>bx+bw-114&&x<bx+bw-14)quit_hover=1;}
        if(quit_hover>=0)quit_focus=quit_hover;
    }else if(fabsf(x-W/2)<80){
        for(int i=0;i<3;i++)if(y>H*.42f+i*50&&y<H*.42f+i*50+36)pause_hover=i;
        if(pause_hover>=0)pause_focus=pause_hover;
    }
}
