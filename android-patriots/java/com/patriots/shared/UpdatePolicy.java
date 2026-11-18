package com.patriots.shared;

import java.net.URI;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Pure policy shared by both Android apps and tested without a device. */
public final class UpdatePolicy {
    private UpdatePolicy() {}
    public static int versionCode(String tag) {
        Matcher m=Pattern.compile("^android-v(\\d{1,2})\\.(\\d{1,2})\\.(\\d{1,3})$").matcher(tag);
        if(!m.matches())return -1;
        return Integer.parseInt(m.group(1))*1000000+Integer.parseInt(m.group(2))*1000+Integer.parseInt(m.group(3));
    }
    public static boolean assetUrl(String value,String repo,String filename) {
        try {
            URI uri=new URI(value);
            return "https".equals(uri.getScheme())&&"github.com".equals(uri.getHost())&&uri.getUserInfo()==null&&uri.getPort()==-1
                &&uri.getQuery()==null&&uri.getFragment()==null&&uri.getPath().startsWith("/TheAti1/"+repo+"/releases/download/android-v")&&uri.getPath().endsWith("/"+filename);
        }catch(Exception e){return false;}
    }
    public static boolean digest(String value){return value!=null&&value.matches("[a-fA-F0-9]{64}");}
}
