/* SPDX-License-Identifier: MIT -- standard PNG screenshots using the bundled zlib. */
#include "host.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>
static void png_u32(FILE *f,uint32_t n){unsigned char b[4]={(unsigned char)(n>>24),(unsigned char)(n>>16),(unsigned char)(n>>8),(unsigned char)n};fwrite(b,1,4,f);}
static void png_chunk(FILE *f,const char *type,const void *data,uint32_t n){png_u32(f,n);fwrite(type,1,4,f);if(n)fwrite(data,1,n,f);uLong crc=crc32(0,(const Bytef *)type,4);if(n)crc=crc32(crc,data,n);png_u32(f,(uint32_t)crc);}
int pc_write_png(const char *path,int w,int h,const uint8_t *rgba){
    size_t stride=(size_t)w*3+1,total=stride*h;
    uint8_t *raw=malloc(total);if(!raw)return -1;
    for(int y=0;y<h;y++){uint8_t *row=raw+(size_t)y*stride;row[0]=0;for(int x=0;x<w;x++)memcpy(row+1+x*3,rgba+((size_t)(h-1-y)*w+x)*4,3);}
    uLongf packed_size=compressBound((uLong)total);uint8_t *packed=malloc(packed_size);
    if(!packed){free(raw);return -1;}
    int result=compress2(packed,&packed_size,raw,(uLong)total,3);free(raw);
    if(result!=Z_OK){free(packed);return -1;}
    FILE *f=fopen(path,"wb");if(!f){free(packed);return -1;}
    fwrite("\x89PNG\r\n\x1a\n",1,8,f);
    uint8_t ihdr[13]={(uint8_t)(w>>24),(uint8_t)(w>>16),(uint8_t)(w>>8),(uint8_t)w,(uint8_t)(h>>24),(uint8_t)(h>>16),(uint8_t)(h>>8),(uint8_t)h,8,2,0,0,0};
    png_chunk(f,"IHDR",ihdr,13);png_chunk(f,"IDAT",packed,(uint32_t)packed_size);png_chunk(f,"IEND",NULL,0);
    free(packed);result=ferror(f)?-1:0;fclose(f);return result;
}
