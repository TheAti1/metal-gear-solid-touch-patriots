/* SPDX-License-Identifier: MIT -- UTF-8 paths for the Windows desktop host. */
#ifndef PATRIOTS_WINDOWS_UTF8_H
#define PATRIOTS_WINDOWS_UTF8_H
#ifdef _WIN32
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <direct.h>
static inline wchar_t *pc_path_wide(const char *s){
    int n=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s,-1,NULL,0);if(!n)return NULL;
    wchar_t *w=(wchar_t *)malloc((size_t)n*sizeof(wchar_t));
    if(w)MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s,-1,w,n);return w;
}
static inline FILE *pc_utf8_fopen(const char *path,const char *mode){
    wchar_t *p=pc_path_wide(path),*m=pc_path_wide(mode);FILE *f=p&&m?_wfopen(p,m):NULL;free(p);free(m);return f;
}
static inline int pc_utf8_mkdir(const char *path){wchar_t *p=pc_path_wide(path);int r=p?_wmkdir(p):-1;free(p);return r;}
static inline BOOL pc_utf8_move(const char *from,const char *to,DWORD flags){
    wchar_t *a=pc_path_wide(from),*b=pc_path_wide(to);BOOL r=a&&b?MoveFileExW(a,b,flags):FALSE;free(a);free(b);return r;
}
static inline void pc_utf8_arguments(int *argc,char ***argv){
    int n=0;wchar_t **wide=CommandLineToArgvW(GetCommandLineW(),&n);if(!wide)return;
    char **utf8=(char **)calloc((size_t)n+1,sizeof(char *));if(!utf8){LocalFree(wide);return;}
    for(int i=0;i<n;i++){int len=WideCharToMultiByte(CP_UTF8,0,wide[i],-1,NULL,0,NULL,NULL);utf8[i]=(char *)malloc(len);if(utf8[i])WideCharToMultiByte(CP_UTF8,0,wide[i],-1,utf8[i],len,NULL,NULL);}
    *argc=n;*argv=utf8;LocalFree(wide);
}
#define fopen(path,mode) pc_utf8_fopen(path,mode)
#define _mkdir(path) pc_utf8_mkdir(path)
#define MoveFileExA(from,to,flags) pc_utf8_move(from,to,flags)
#endif
#endif
