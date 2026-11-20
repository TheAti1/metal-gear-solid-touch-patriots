package com.patriots.shared;
/** Window size policy shared by phone, tablet, foldable and split-screen layouts. */
public final class AdaptiveLayout {
    private AdaptiveLayout() {}
    public static boolean wide(int widthDp,int heightDp){return widthDp>=840||(widthDp>=720&&widthDp>heightDp);}
}
