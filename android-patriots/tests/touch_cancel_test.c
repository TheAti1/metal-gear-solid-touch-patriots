#include <assert.h>
#include <stdio.h>
/* Compile the real filter without linking the private recovered game module. */
#define HOST_H
typedef struct {
    int render_scale;float touch_slop,aim_gain,music_gain,effects_gain;
    int hq_resample;int (*touch)(int,int,float,float);
} HostExt;
struct {int raw_touch;} g_cfg;
static int phase_seen=-1,deliveries,overlay_active;
void host_touch_deliver(int phase,int id,float x,float y){(void)id;(void)x;(void)y;phase_seen=phase;deliveries++;}
#include "../native/engine/host/touch.c"
static int overlay(int phase,int id,float x,float y){(void)phase;(void)id;(void)x;(void)y;return overlay_active;}
int main(void){
    g_ext.touch=overlay;
    host_touch(0,0,40,50);assert(phase_seen==0);
    overlay_active=1;int old=deliveries;
    host_touch(4,0,0,0);assert(deliveries==old+1&&phase_seen==4);
    overlay_active=0;old=deliveries;
    host_touch(1,0,100,100);assert(deliveries==old); // stale drag cannot return
    host_touch(0,0,40,50);host_touch(1,0,60,60);assert(phase_seen==1);
    host_touch(3,0,60,60);assert(phase_seen==3);
    host_touch(0,1,20,30);overlay_active=1;host_touch(4,1,0,0);assert(phase_seen==4);
    overlay_active=0;old=deliveries;host_touch(3,1,20,30);assert(deliveries==old);
    puts("PASS: overlay cannot swallow rotation cancellation; stale gestures stop, new aim/taps work");
    return 0;
}
