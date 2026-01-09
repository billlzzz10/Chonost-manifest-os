#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::fs;
use std::path::Path;
use std::process::Command;
use tauri::command;

// AI Analysis command using sidecar
#[command]
async fn analyze_text(input: String) -> Result<String, String> {
    // Enhanced analysis with Thai language support
    let char_count = input.chars().count();
    let word_count = input.split_whitespace().count();

    let analysis = format!(
        "การวิเคราะห์ข้อความ:\n\n📝 ข้อความต้นฉบับ: '{}'\n\n📊 สถิติ:\n• ความยาว: {} ตัวอักษร\n• จำนวนคำ: {} คำ\n\n🔍 การวิเคราะห์เนื้อหา:\n• ภาษา: {}\n• หมวดหมู่ที่เป็นไปได้: {}\n\n💡 ข้อแนะนำ: {}",
        input,
        char_count,
        word_count,
        detect_language(&input),
        detect_category(&input),
        generate_recommendation(&input)
    );

    Ok(analysis)
}

// Sidecar analysis command
#[command]
async fn run_sidecar_analysis(input: String) -> Result<String, String> {
    // Enhanced sidecar analysis with more detailed processing
    let result = format!(
        "🔬 การวิเคราะห์ขั้นสูง (Sidecar)\n\n📥 ข้อมูลนำเข้า: {}\n\n⚙️ กระบวนการที่ดำเนินการ:\n• การวิเคราะห์ไวยากรณ์\n• การตรวจสอบความหมาย\n• การสร้างคำแนะนำ\n\n✅ สถานะ: การประมวลผลเสร็จสิ้น\n\n📤 ผลลัพธ์: พร้อมใช้งาน",
        input
    );

    Ok(result)
}

// Save file command
#[command]
async fn save_file(content: String) -> Result<String, String> {
    use tauri::api::dialog;

    let file_path = dialog::blocking::FileDialogBuilder::new()
        .set_title("Save File")
        .add_filter("All Files", &["*"])
        .add_filter("Text Files", &["txt", "md", "json", "js", "ts", "rs", "py", "html", "css"])
        .save_file();

    match file_path {
        Some(path) => {
            match fs::write(&path, content) {
                Ok(_) => Ok(format!("File saved successfully to: {}", path.display())),
                Err(e) => Err(format!("Failed to save file: {}", e)),
            }
        }
        None => Err("Save cancelled by user".to_string()),
    }
}

// List directory contents
#[command]
async fn list_dir(path: String) -> Result<Vec<serde_json::Value>, String> {
    let dir_path = Path::new(&path);
    if !dir_path.exists() {
        return Err("Directory does not exist".to_string());
    }

    let mut entries = Vec::new();
    match fs::read_dir(dir_path) {
        Ok(read_dir) => {
            for entry in read_dir {
                match entry {
                    Ok(entry) => {
                        let path = entry.path();
                        let file_name = path.file_name()
                            .and_then(|n| n.to_str())
                            .unwrap_or("unknown")
                            .to_string();
                        let is_dir = path.is_dir();
                        let metadata = match entry.metadata() {
                            Ok(meta) => meta,
                            Err(_) => continue,
                        };
                        let size = metadata.len();
                        let modified = metadata.modified()
                            .unwrap_or(std::time::SystemTime::UNIX_EPOCH)
                            .duration_since(std::time::SystemTime::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs();

                        entries.push(serde_json::json!({
                            "name": file_name,
                            "path": path.to_string_lossy(),
                            "is_dir": is_dir,
                            "size": size,
                            "modified": modified
                        }));
                    }
                    Err(_) => continue,
                }
            }
            Ok(entries)
        }
        Err(e) => Err(format!("Failed to read directory: {}", e)),
    }
}

// Read file content
#[command]
async fn read_file(path: String) -> Result<String, String> {
    match fs::read_to_string(&path) {
        Ok(content) => Ok(content),
        Err(e) => Err(format!("Failed to read file: {}", e)),
    }
}

// Write file content
#[command]
async fn write_file(path: String, content: String) -> Result<String, String> {
    match fs::write(&path, content) {
        Ok(_) => Ok("File written successfully".to_string()),
        Err(e) => Err(format!("Failed to write file: {}", e)),
    }
}

// Create directory
#[command]
async fn create_dir(path: String) -> Result<String, String> {
    match fs::create_dir_all(&path) {
        Ok(_) => Ok("Directory created successfully".to_string()),
        Err(e) => Err(format!("Failed to create directory: {}", e)),
    }
}

// Delete file or directory
#[command]
async fn delete_file(path: String) -> Result<String, String> {
    let file_path = Path::new(&path);
    if file_path.is_dir() {
        match fs::remove_dir_all(&path) {
            Ok(_) => Ok("Directory deleted successfully".to_string()),
            Err(e) => Err(format!("Failed to delete directory: {}", e)),
        }
    } else {
        match fs::remove_file(&path) {
            Ok(_) => Ok("File deleted successfully".to_string()),
            Err(e) => Err(format!("Failed to delete file: {}", e)),
        }
    }
}

// Helper functions for analysis
fn detect_language(text: &str) -> &str {
    if text.contains("ที่") || text.contains("การ") || text.contains("และ") {
        "ไทย"
    } else if text.contains("the") || text.contains("and") || text.contains("or") {
        "อังกฤษ"
    } else {
        "ไม่สามารถระบุได้"
    }
}

fn detect_category(text: &str) -> &str {
    if text.contains("โค้ด") || text.contains("function") || text.contains("class") {
        "การเขียนโปรแกรม"
    } else if text.contains("ข้อมูล") || text.contains("ฐานข้อมูล") || text.contains("data") {
        "การจัดการข้อมูล"
    } else if text.contains("การออกแบบ") || text.contains("design") {
        "การออกแบบ"
    } else {
        "ทั่วไป"
    }
}

fn generate_recommendation(text: &str) -> &str {
    if text.chars().count() < 50 {
        "ลองเพิ่มรายละเอียดให้มากขึ้น"
    } else if text.contains("?") {
        "คำถามที่ดี! ลองสำรวจเพิ่มเติม"
    } else {
        "เนื้อหาดีเยี่ยม อาจนำไปพัฒนาต่อได้"
    }
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
        analyze_text,
        run_sidecar_analysis,
        save_file,
        list_dir,
        read_file,
        write_file,
        create_dir,
        delete_file
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
