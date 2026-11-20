#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../native/engine/host/android_presentation.h"

int main(void){
    assert(patriots_window_rotation(800,1280,1,1,270)==0);
    assert(patriots_window_rotation(1280,800,0,0,270)==0);
    assert(patriots_window_rotation(1280,800,1,0,0)==270);
    assert(patriots_window_rotation(1280,800,5,0,0)==90);
    assert(patriots_window_rotation(1280,800,0,1,0)==270);
    assert(patriots_window_rotation(1280,800,2,0,90)==90);
    assert(patriots_window_rotation(0,800,1,1,90)==0);
    for(int r=0;r<3;r++)for(int y=0;y<=480;y+=24)for(int x=0;x<=320;x+=16){
        int rotation=r==0?0:r==1?90:270;float sx,sy,vx,vy;
        patriots_view_to_screen(rotation,x,y,&sx,&sy);
        assert(sx>=0&&sx<=(rotation?480:320));
        assert(sy>=0&&sy<=(rotation?320:480));
        patriots_screen_to_view(rotation,sx,sy,&vx,&vy);
        assert(fabsf(vx-x)<.001f&&fabsf(vy-y)<.001f);
    }
    float x,y;patriots_sensor_to_portrait(0,2,3,&x,&y);assert(x==2&&y==3);
    patriots_sensor_to_portrait(1,2,3,&x,&y);assert(x==3&&y==-2);
    puts("PASS: phone/tablet scene rotation, both inclinations, pause, pointer round trips and sensor axes");
    return 0;
}
