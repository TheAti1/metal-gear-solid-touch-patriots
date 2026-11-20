package com.patriots.shared;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;

/** The reviewed Patriots catalogue, with English fallback for older/partial assets. */
final class AndroidLocale {
    private static JSONObject portuguese;
    private static boolean loaded;
    private static synchronized JSONObject catalogue(Context context) {
        if (!loaded) {
            loaded = true;
            try (InputStream in = context.getAssets().open("localization/pt-br.json");
                 ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                byte[] b = new byte[8192]; int n;
                while ((n = in.read(b)) != -1) {
                    if (out.size() + n > 2 * 1024 * 1024) throw new java.io.IOException("Catalogue too large");
                    out.write(b, 0, n);
                }
                portuguese = new JSONObject(new String(out.toByteArray(), StandardCharsets.UTF_8));
            } catch (Exception e) { portuguese = new JSONObject(); }
        }
        return portuguese;
    }
    static String text(Context context, String tr, String en) {
        String id = HomeActivity.locale(context);
        if ("tr".equals(id)) return tr;
        JSONObject strings = catalogue(context).optJSONObject("strings");
        return "pt-br".equals(id) && strings != null ? strings.optString(en, en) : en;
    }
    static String author(Context context) { return catalogue(context).optString("author", ""); }
}
