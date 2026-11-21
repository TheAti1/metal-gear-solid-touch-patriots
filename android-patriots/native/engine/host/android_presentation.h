/* Android window/portrait-game transforms; independent of GL and the game module. */
#ifndef PATRIOTS_ANDROID_PRESENTATION_H
#define PATRIOTS_ANDROID_PRESENTATION_H
static inline int patriots_window_rotation(int w,int h,int state,int scene_landscape,int previous){
    /* Scene orientation belongs to the virtual phone, not the Android window. */
    if(w<=0||h<=0)return previous;
    if((state&1)||scene_landscape)return (state&4)?90:270;
    return (state&2)?previous:0;
}
static inline void patriots_screen_to_view(int rotation,float x,float y,float *vx,float *vy){
    if(rotation==90){*vx=320-y;*vy=x;}
    else if(rotation==270){*vx=y;*vy=480-x;}
    else{*vx=x;*vy=y;}
}
static inline void patriots_view_to_screen(int rotation,float x,float y,float *sx,float *sy){
    if(rotation==90){*sx=y;*sy=320-x;}
    else if(rotation==270){*sx=480-y;*sy=x;}
    else{*sx=x;*sy=y;}
}
static inline void patriots_sensor_to_portrait(int natural_landscape,float x,float y,float *px,float *py){
    if(natural_landscape){*px=y;*py=-x;}else{*px=x;*py=y;}
}
#endif
