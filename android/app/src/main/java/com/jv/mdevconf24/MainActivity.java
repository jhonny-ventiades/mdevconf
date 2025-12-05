package com.jv.mdevconf24;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import javax.net.ssl.HttpsURLConnection;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    
    private static final String TAG = "MainActivity";
    private SharedPreferences prefs;
    
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // VULNERABILIDAD: Almacenamiento inseguro de credenciales en SharedPreferences sin encriptar
        prefs = getSharedPreferences("user_data", MODE_WORLD_READABLE);
        String username = "admin";
        String password = "password123";
        prefs.edit().putString("username", username).apply();
        prefs.edit().putString("password", password).apply();
        
        // VULNERABILIDAD: WebView con JavaScript habilitado sin validación
        WebView webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("https://example.com");
        
        // PROBLEMA DE LÓGICA: División por cero potencial
        int userCount = 0;
        int averageScore = 100 / userCount; // Esto causará ArithmeticException
        
        // VULNERABILIDAD: Conexión HTTP sin validación SSL
        new Thread(() -> {
            try {
                URL url = new URL("http://insecure-api.example.com/login");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                
                // VULNERABILIDAD: Envío de credenciales en texto plano
                String credentials = "username=admin&password=secret123";
                OutputStreamWriter writer = new OutputStreamWriter(conn.getOutputStream());
                writer.write(credentials);
                writer.flush();
                writer.close();
                
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(conn.getInputStream())
                );
                String response = reader.readLine();
                Log.d(TAG, "Response: " + response);
                
            } catch (Exception e) {
                Log.e(TAG, "Error: " + e.getMessage());
            }
        }).start();
        
        // PROBLEMA DE LÓGICA: Validación de entrada débil
        String userInput = getIntent().getStringExtra("user_id");
        if (userInput != null && userInput.length() > 0) {
            // VULNERABILIDAD: SQL Injection potencial si se usa en query
            String query = "SELECT * FROM users WHERE id = " + userInput;
            Log.d(TAG, "Query: " + query);
        }
        
        // PROBLEMA DE LÓGICA: Uso de método deprecado
        String deviceId = android.provider.Settings.Secure.getString(
            getContentResolver(),
            android.provider.Settings.Secure.ANDROID_ID
        );
        
        // VULNERABILIDAD: Logging de información sensible
        Log.d(TAG, "User credentials: " + username + " / " + password);
        Log.d(TAG, "Device ID: " + deviceId);
        
        // PROBLEMA DE LÓGICA: Manejo de errores inadecuado
        try {
            processUserData(null);
        } catch (Exception e) {
            // Solo loguea, no maneja el error apropiadamente
            Log.e(TAG, "Error occurred");
        }
    }
    
    // PROBLEMA DE LÓGICA: Método sin validación de entrada
    private void processUserData(String data) {
        // No valida si data es null antes de usar
        String processed = data.toUpperCase();
        Log.d(TAG, "Processed: " + processed);
    }
    
    // VULNERABILIDAD: Método que expone información sensible
    public String getUserToken() {
        // Retorna token sin validación de expiración
        return prefs.getString("auth_token", "");
    }
}
