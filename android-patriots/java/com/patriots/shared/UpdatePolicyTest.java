package com.patriots.shared;
public final class UpdatePolicyTest {
    static void require(boolean ok){if(!ok)throw new AssertionError();}
    public static void main(String[] args){
        require(UpdatePolicy.versionCode("android-v1.0.0")==1000000);
        require(UpdatePolicy.versionCode("android-v1.2.3")>UpdatePolicy.versionCode("android-v1.1.999"));
        for(String bad:new String[]{"v5.2.0","android-v1.0.0-beta","android-v1.100.0","android-v1.0.-1","https://bad"})require(UpdatePolicy.versionCode(bad)==-1);
        String root="https://github.com/TheAti1/metal-gear-solid-touch-patriots/releases/download/android-v1.0.0/";
        require(UpdatePolicy.assetUrl(root+"game.apk","metal-gear-solid-touch-patriots","game.apk"));
        for(String bad:new String[]{root.replace("https:","http:")+"game.apk",root.replace("github.com","github.com.evil.test")+"game.apk",root+"other.apk",root+"game.apk?redirect=bad"})require(!UpdatePolicy.assetUrl(bad,"metal-gear-solid-touch-patriots","game.apk"));
        require(UpdatePolicy.digest(new String(new char[64]).replace('\0','a')));require(!UpdatePolicy.digest("sha256:no"));
        System.out.println("PASS: Android release ordering, channel isolation, trusted asset URLs and SHA256 syntax");
    }
}
