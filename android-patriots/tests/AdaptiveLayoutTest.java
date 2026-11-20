package com.patriots.shared;
public final class AdaptiveLayoutTest {
    private static void check(boolean value,String name){if(!value)throw new AssertionError(name);}
    public static void main(String[] args){
        check(!AdaptiveLayout.wide(360,800),"phone portrait uses compact navigation");
        check(!AdaptiveLayout.wide(600,800),"narrow tablet/split window uses compact navigation");
        check(AdaptiveLayout.wide(1280,800),"landscape tablet uses desktop layout");
        check(!AdaptiveLayout.wide(800,1280),"portrait tablet keeps readable full-width content");
        check(AdaptiveLayout.wide(960,600),"small landscape tablet uses desktop layout");
        check(!AdaptiveLayout.wide(0,0),"unmeasured window starts compact");
        System.out.println("PASS: phone, portrait/landscape tablet and narrow-window navigation");
    }
}
