from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import mimetypes
from datetime import datetime
from src.database import get_db_connection
from src.routes.user import token_required
from src.models.file import FileModel
from flask_restx import Api, Resource, fields

file_bp = Blueprint("files", __name__)
api = Api(file_bp, doc="/doc", title="File Management API", description="API for managing user files")

ns = api.namespace("files", description="File operations")

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
ALLOWED_EXTENSIONS = {
    "md", "txt", "json", "png", "jpg", "jpeg", "gif", "pdf",
    "doc", "docx", "csv", "xlsx", "zip"
}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# สร้างโฟลเดอร์ upload ถ้ายังไม่มี
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """ตรวจสอบว่าไฟล์ที่อัปโหลดเป็นประเภทที่อนุญาตหรือไม่"""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """กำหนดประเภทไฟล์จากนามสกุล"""
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    type_mapping = {
        "md": "markdown",
        "txt": "text",
        "json": "json",
        "png": "image",
        "jpg": "image",
        "jpeg": "image",
        "gif": "image",
        "pdf": "document",
        "doc": "document",
        "docx": "document",
        "csv": "data",
        "xlsx": "data",
        "zip": "archive"
    }

    return type_mapping.get(ext, "unknown")

def process_markdown_file(file_path):
    """ประมวลผลไฟล์ Markdown และแยกข้อมูล metadata"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # แยก frontmatter (YAML metadata) ถ้ามี
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                content = parts[2].strip()

                # Parse YAML frontmatter (simple parsing)
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()

        # แยกหัวข้อ (headers)
        headers = []
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                headers.append({"level": level, "title": title})

        return {
            "content": content,
            "metadata": metadata,
            "headers": headers,
            "word_count": len(content.split()),
            "char_count": len(content)
        }

    except Exception as e:
        return {"error": f"Error processing markdown: {str(e)}"}

# Models for API documentation
file_upload_parser = api.parser()
file_upload_parser.add_argument("file", type="file", location="files", required=True, help="File to upload")
file_upload_parser.add_argument("type", type=str, location="form", default="general", help="Type of upload (e.g., general, obsidian)")

file_model = api.model("File", {
    "id": fields.String(required=True, description="File ID"),
    "original_name": fields.String(required=True, description="Original filename"),
    "filename": fields.String(required=True, description="Stored filename"),
    "file_type": fields.String(required=True, description="Type of file (e.g., markdown, image)"),
    "file_size": fields.Integer(required=True, description="Size of the file in bytes"),
    "mime_type": fields.String(required=True, description="MIME type of the file"),
    "user_id": fields.String(required=True, description="User ID who uploaded the file"),
    "upload_type": fields.String(required=True, description="Category of upload"),
    "created_at": fields.String(required=True, description="Timestamp of upload"),
    "processed_data": fields.Raw(description="Processed data for markdown files"),
    "url": fields.String(description="URL to access the file")
})

file_list_item_model = api.model("FileListItem", {
    "id": fields.String(required=True, description="File ID"),
    "original_name": fields.String(required=True, description="Original filename"),
    "file_type": fields.String(required=True, description="Type of file (e.g., markdown, image)"),
    "file_size": fields.Integer(required=True, description="Size of the file in bytes"),
    "mime_type": fields.String(required=True, description="MIME type of the file"),
    "upload_type": fields.String(required=True, description="Category of upload"),
    "created_at": fields.String(required=True, description="Timestamp of upload"),
    "url": fields.String(description="URL to access the file")
})

file_list_model = api.model("FileList", {
    "success": fields.Boolean(required=True),
    "files": fields.List(fields.Nested(file_list_item_model)),
    "total_files": fields.Integer,
    "total_pages": fields.Integer,
    "current_page": fields.Integer
})

@ns.route("/upload")
class FileUpload(Resource):
    @api.expect(file_upload_parser)
    @api.marshal_with(file_model, code=201)
    @api.doc(security="apiKey")
    @token_required
    def post(self):
        """อัปโหลดไฟล์"""
        try:
            if "file" not in request.files:
                api.abort(400, "ไม่พบไฟล์ที่ต้องการอัปโหลด")

            file = request.files["file"]
            if file.filename == "":
                api.abort(400, "ไม่ได้เลือกไฟล์")

            if not allowed_file(file.filename):
                api.abort(400, "ประเภทไฟล์ไม่รองรับ")

            # ตรวจสอบขนาดไฟล์
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_FILE_SIZE:
                api.abort(400, "ไฟล์มีขนาดใหญ่เกินไป (สูงสุด 16MB)")

            # สร้างชื่อไฟล์ที่ปลอดภัย
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
            new_filename = f"{file_id}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, new_filename)

            # บันทึกไฟล์
            file.save(file_path)

            # ประมวลผลไฟล์ตามประเภท
            processed_data = {}
            file_type = get_file_type(filename)

            if file_type == "markdown":
                processed_data = process_markdown_file(file_path)

            # บันทึกข้อมูลไฟล์ลงฐานข้อมูล
            with get_db_connection() as conn:
                file_model_db = FileModel(conn)

            file_data = {
                "id": file_id,
                "original_name": filename,
                "filename": new_filename,
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size,
                "mime_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
                "user_id": request.current_user["id"],
                "upload_type": request.form.get("type", "general"),
                "processed_data": processed_data
            }

            result = file_model_db.create_file(file_data)

            if result["success"]:
                return {
                    "id": file_id,
                    "original_name": filename,
                    "filename": new_filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "mime_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
                    "user_id": request.current_user["id"],
                    "upload_type": request.form.get("type", "general"),
                    "created_at": datetime.now().isoformat(), # Placeholder, actual from DB
                    "processed_data": processed_data,
                    "url": f"/api/files/{file_id}"
                }, 201
            else:
                # ลบไฟล์ถ้าบันทึกฐานข้อมูลไม่สำเร็จ
                if os.path.exists(file_path):
                    os.remove(file_path)
                api.abort(500, result["message"])

        except Exception as e:
            api.abort(500, f"เกิดข้อผิดพลาด: {str(e)}")

@ns.route("/<string:file_id>")
@api.param("file_id", "The file identifier")
class File(Resource):
    @api.doc(security="apiKey")
    @token_required
    def get(self, file_id):
        """ดาวน์โหลดไฟล์"""
        try:
            with get_db_connection() as conn:
                file_model_db = FileModel(conn)
                file_data = file_model_db.get_file_by_id(file_id)

            if not file_data:
                api.abort(404, "ไม่พบไฟล์")

            # ตรวจสอบสิทธิ์การเข้าถึง
            if file_data["user_id"] != request.current_user["id"]:
                api.abort(403, "ไม่มีสิทธิ์เข้าถึงไฟล์นี้")

            file_path = file_data["file_path"]
            if not os.path.exists(file_path):
                api.abort(404, "ไฟล์ไม่พบในระบบ")

            return send_file(
                file_path,
                as_attachment=True,
                download_name=file_data["original_name"],
                mimetype=file_data["mime_type"]
            )

        except Exception as e:
            api.abort(500, f"เกิดข้อผิดพลาด: {str(e)}")

    @api.doc(security="apiKey")
    @api.response(200, "File successfully deleted")
    @api.response(404, "File not found")
    @api.response(403, "Permission denied")
    @token_required
    def delete(self, file_id):
        """ลบไฟล์"""
        try:
            with get_db_connection() as conn:
                file_model_db = FileModel(conn)
                file_data = file_model_db.get_file_by_id(file_id)

                if not file_data:
                    api.abort(404, "ไม่พบไฟล์")

                # ตรวจสอบสิทธิ์การเข้าถึง
                if file_data["user_id"] != request.current_user["id"]:
                    api.abort(403, "ไม่มีสิทธิ์ลบไฟล์นี้")

                # ลบไฟล์จากระบบ
                file_path = file_data["file_path"]
                if os.path.exists(file_path):
                    os.remove(file_path)

                # ลบข้อมูลจากฐานข้อมูล
                result = file_model_db.delete_file(file_id)
                
                if result["success"]:
                    return {"message": "File successfully deleted"}, 200
                else:
                    api.abort(500, result["message"])

        except Exception as e:
            api.abort(500, f"เกิดข้อผิดพลาด: {str(e)}")

@ns.route("/<string:file_id>/info")
@api.param("file_id", "The file identifier")
class FileInfo(Resource):
    @api.marshal_with(file_model)
    @api.doc(security="apiKey")
    @token_required
    def get(self, file_id):
        """ดึงข้อมูลไฟล์"""
        try:
            with get_db_connection() as conn:
                file_model_db = FileModel(conn)
                file_data = file_model_db.get_file_by_id(file_id)

            if not file_data:
                api.abort(404, "ไม่พบไฟล์")

            # ตรวจสอบสิทธิ์การเข้าถึง
            if file_data["user_id"] != request.current_user["id"]:
                api.abort(403, "ไม่มีสิทธิ์เข้าถึงไฟล์นี้")

            return {
                "id": file_data["id"],
                "original_name": file_data["original_name"],
                "filename": file_data["filename"],
                "file_type": file_data["file_type"],
                "file_size": file_data["file_size"],
                "mime_type": file_data["mime_type"],
                "user_id": file_data["user_id"],
                "upload_type": file_data["upload_type"],
                "created_at": file_data["created_at"],
                "processed_data": file_data.get("processed_data", {}),
                "url": f"/api/files/{file_id}"
            }

        except Exception as e:
            api.abort(500, f"เกิดข้อผิดพลาด: {str(e)}")

@ns.route("/list")
class FileList(Resource):
    @api.expect(api.parser().add_argument("type", type=str, help="Filter by file type").add_argument("page", type=int, help="Page number").add_argument("per_page", type=int, help="Items per page"))
    @api.marshal_with(file_list_model)
    @api.doc(security="apiKey")
    @token_required
    def get(self):
        """ดึงรายการไฟล์ของผู้ใช้"""
        try:
            user_id = request.current_user["id"]
            file_type = request.args.get("type")  # filter by type
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 20))

            with get_db_connection() as conn:
                file_model_db = FileModel(conn)
                result = file_model_db.get_user_files(user_id, file_type, page, per_page)

            return result

        except Exception as e:
            api.abort(500, f"เกิดข้อผิดพลาด: {str(e)}")

# Error handlers
@file_bp.errorhandler(413)
def too_large(e):
    return jsonify({"success": False, "message": "ไฟล์มีขนาดใหญ่เกินไป"}), 413


