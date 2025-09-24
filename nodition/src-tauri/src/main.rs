#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

// Define commands for frontend-backend communication
#[tauri::command]
fn show_notification(title: String, message: String) -> Result<(), String> {
    println!("🔔 Notification: {} - {}", title, message);
    Ok(())
}

#[tauri::command]
fn validation_complete(results: String) -> Result<(), String> {
    println!("📊 Validation results: {}", results);
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![show_notification, validation_complete])
        .setup(|app| {
            let window = tauri::WindowBuilder::new(app, "main", tauri::WindowUrl::App("index.html".into()))
                .title("Nodition Desktop")
                .inner_size(800f64, 600f64)
                .resizable(true)
                .build()?;
            
            // Emit initial app ready event
            let _ = window.emit("app-ready", "Nodition desktop initialized");
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}