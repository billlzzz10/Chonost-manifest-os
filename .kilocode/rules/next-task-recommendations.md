## Brief overview
- กฎสำหรับการให้คำแนะนำงานถัดไป โดยอิงจากบริบทการสนทนาก่อนหน้าและสถานะงานล่าสุด เพื่อให้การพัฒนาต่อเนื่องและป้องกันปัญหาซ้ำซาก

## Communication style
- ให้คำแนะนำงานถัดไปที่ชัดเจนและเฉพาะเจาะจง โดยอิงจากบริบทล่าสุด เช่น หลังแก้ไขปัญหา API keys แล้ว แนะนำการตั้งค่า CI/CD hooks สำหรับ secret scanning
- ใช้ภาษาไทยที่กระชับ สนับสนุน และเป็นมิตร เหมือนคู่หูเขียนโค้ด โดยอธิบายเหตุผลสั้นๆ ว่าทำไมขั้นตอนนั้นเหมาะสม

## Development workflow
- จดจำสถานะงานก่อนหน้าเสมอ เช่น หลังแก้ไข API keys ใน datasets และ .env แล้ว ให้แนะนำการตรวจสอบ codebase ด้วย git grep และเพิ่ม .env.example
- แนะนำขั้นตอนถัดไปที่ต่อเนื่อง เช่น ถ้างานล่าสุดคือ security fix แนะนำ integration testing และ deployment hooks
- ใช้ update_todo_list เพื่ออัปเดตสถานะงานใหม่ โดยโฟกัสที่ prevention เช่น ตั้งค่า GitHub Actions สำหรับ secret scanning ใน CI/CD

## Coding best practices
- ในโค้ดใหม่ ใช้ os.getenv() และ load_dotenv() สำหรับ API keys เสมอ ไม่ hardcode
- แนะนำการเพิ่ม error handling สำหรับ missing keys เช่น raise ValueError ถ้า .env ไม่โหลด
- สำหรับ datasets และ test data ใช้ placeholders เช่น {API_KEY} แทน real keys เพื่อป้องกัน exposure

## Project context
- โปรเจกต์ Chonost Manuscript OS: เน้น AI integration (Azure, OpenAI, Claude) ดังนั้นแนะนำการตรวจสอบ security ใน components ที่เกี่ยวข้องกับ external APIs
- หลังงาน security fix ล่าสุด (ลบ keys จาก JSONL files) แนะนำ audit อื่นๆ เช่น ตรวจสอบ logs และ environment ใน production

## Other guidelines
- ถ้าปัญหาคล้ายกันเกิดขึ้นในอนาคต แนะนำใช้ tools เช่น truffleHog สำหรับ scan secrets ก่อน commit
- หลังให้คำแนะนำ ใช้ switch_mode เพื่อเปลี่ยนไป mode ที่เหมาะสม เช่น code สำหรับ implement CI/CD hooks