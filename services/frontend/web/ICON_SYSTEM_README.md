# 🎨 Chonost Icon System

ระบบไอคอนที่มีสีสันสวยงามแบบพาสเทลสำหรับ Chonost Writing Platform

## 📦 ไอคอนที่ติดตั้งแล้ว

### 1. Noto Emoji Icons
- **Package**: `@iconify-json/noto`
- **Description**: ไอคอน Emoji สวยงามจาก Google Noto
- **Usage**: `noto:books`, `noto:house`, `noto:robot`, etc.

### 2. Brand Icons (Boxicons)
- **Package**: `@iconify-json/bxl`
- **Description**: ไอคอนแบรนด์ต่างๆ
- **Usage**: `bxl:github`, `bxl:twitter`, `bxl:discord-alt`

### 3. Skill Icons
- **Package**: `@iconify-json/skill-icons`
- **Description**: ไอคอนเทคโนโลยีและทักษะ
- **Usage**: `skill-icons:react-dark`, `skill-icons:typescript`, `skill-icons:python-dark`

### 4. Devicon
- **Package**: `@iconify-json/devicon`
- **Description**: ไอคอนเครื่องมือพัฒนา
- **Usage**: `devicon:vscode`, `devicon:git`, `devicon:docker`

## 🎨 สีพาสเทลไล่สี

### Primary Colors (พาสเทลอ่อน)
```css
#FFB3BA  /* พาสเทลชมพู */
#BAFFC9  /* พาสเทลเขียว */
#BAE1FF  /* พาสเทลฟ้า */
#FFFFBA  /* พาสเทลเหลือง */
#FFB3F7  /* พาสเทลม่วง */
#B3FFE6  /* พาสเทลมินต์ */
#FFD4B3  /* พาสเทลส้ม */
#E6B3FF  /* พาสเทลลาเวนเดอร์ */
```

### Secondary Colors (พาสเทลเข้ม)
```css
#FF8A9A  /* ชมพูเข้ม */
#8AFF9A  /* เขียวเข้ม */
#8AC4FF  /* ฟ้าเข้ม */
#FFFF8A  /* เหลืองเข้ม */
#FF8AFF  /* ม่วงเข้ม */
#8AFFE6  /* มินต์เข้ม */
#FFB38A  /* ส้มเข้ม */
#B38AFF  /* ลาเวนเดอร์เข้ม */
```

## 🚀 การใช้งาน

### 1. ไอคอนพื้นฐาน
```jsx
<ChonostIcon name="logo" size="2rem" />
<ChonostIcon name="dashboard" color="#FFB3BA" />
<ChonostIcon name="ai" className="custom-class" />
```

### 2. ไอคอนแบบ Animated
```jsx
<AnimatedIcon name="brain" animation="pulse" />
<AnimatedIcon name="magic" animation="bounce" />
<AnimatedIcon name="ai" animation="spin" />
<AnimatedIcon name="happy" animation="wiggle" />
```

### 3. ไอคอนแบบ Gradient
```jsx
<GradientIcon name="logo" gradient="linear-gradient(45deg, #FFB3BA, #BAE1FF)" />
<GradientIcon name="brain" gradient="linear-gradient(45deg, #FFD4B3, #E6B3FF)" />
```

### 4. ไอคอนแบบ Floating
```jsx
<FloatingIcon name="plus" onClick={handleClick} />
<FloatingIcon name="save" color="#4ADE80" />
```

## 📋 รายการไอคอนที่มี

### Navigation Icons
- `logo` - ไอคอนหลักของแอป
- `dashboard` - แดชบอร์ด
- `editor` - ตัวแก้ไข
- `characters` - ตัวละคร
- `projects` - โปรเจกต์

### Editor Tools
- `save` - บันทึก
- `bold` - ตัวหนา
- `italic` - ตัวเอียง
- `heading` - หัวข้อ

### Character Analysis
- `character` - ตัวละคร
- `relationship` - ความสัมพันธ์
- `stats` - สถิติ

### AI Features
- `ai` - AI
- `brain` - สมอง
- `magic` - เวทมนตร์

### Mood Tracking (Ashval)
- `happy` - มีความสุข
- `stressed` - เครียด
- `focused` - โฟกัส
- `bored` - เบื่อ

### Task Management
- `task` - งาน
- `priority` - ความสำคัญ
- `deadline` - เวลาจำกัด
- `plus` - เพิ่ม

### Technology Stack
- `react` - React
- `typescript` - TypeScript
- `tailwind` - Tailwind CSS
- `nodejs` - Node.js
- `python` - Python
- `openai` - OpenAI

### Social & Brand
- `github` - GitHub
- `twitter` - Twitter
- `discord` - Discord

### Development Tools
- `vscode` - VS Code
- `git` - Git
- `docker` - Docker

### UI Elements
- `sun` - ดวงอาทิตย์ (โหมดสว่าง)
- `moon` - ดวงจันทร์ (โหมดมืด)

## 🎭 Animation Types

### 1. Pulse
- **Effect**: ขยายและหดตัว
- **Duration**: 2s
- **Use**: สำหรับไอคอนที่ต้องการความสนใจ

### 2. Bounce
- **Effect**: กระเด้งขึ้นลง
- **Duration**: 1s
- **Use**: สำหรับไอคอนที่สนุกสนาน

### 3. Spin
- **Effect**: หมุน
- **Duration**: 1s
- **Use**: สำหรับไอคอนที่กำลังโหลด

### 4. Wiggle
- **Effect**: สั่น
- **Duration**: 1s
- **Use**: สำหรับไอคอนที่ต้องการการตอบสนอง

### 5. Float
- **Effect**: ลอยขึ้นลง
- **Duration**: 3s
- **Use**: สำหรับไอคอนที่ต้องการความรู้สึกเบา

### 6. Glow
- **Effect**: เรืองแสง
- **Duration**: 2s
- **Use**: สำหรับไอคอนที่สำคัญ

## 🎨 Customization

### เพิ่มไอคอนใหม่
```javascript
const ChonostIcons = {
    // ... existing icons
    newIcon: {
        icon: 'noto:new-icon',
        color: pastelColors.primary[0],
        size: '1.5rem'
    }
};
```

### เปลี่ยนสีไอคอน
```jsx
<ChonostIcon name="logo" color="#FF6B9D" />
```

### เปลี่ยนขนาดไอคอน
```jsx
<ChonostIcon name="logo" size="3rem" />
```

### เพิ่ม CSS Class
```jsx
<ChonostIcon name="logo" className="my-custom-class" />
```

## 📱 Responsive Design

ระบบไอคอนรองรับการแสดงผลบนอุปกรณ์ต่างๆ:

- **Desktop**: ขนาดเต็ม
- **Tablet**: ขนาดปานกลาง
- **Mobile**: ขนาดเล็ก

## 🌙 Dark Mode Support

ไอคอนทั้งหมดรองรับ Dark Mode โดยอัตโนมัติ:

```css
.dark .floating-icon {
    background: rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.1);
}
```

## 🔧 การติดตั้ง

1. ติดตั้ง packages:
```bash
npm i -D @iconify-json/noto
npm i -D @iconify-json/bxl
npm i -D @iconify-json/skill-icons
npm i -D @iconify-json/devicon
npm install @iconify/react
```

2. Import ระบบไอคอน:
```javascript
import { ChonostIcon, AnimatedIcon, GradientIcon, FloatingIcon } from './IconSystem';
```

3. ใช้งาน:
```jsx
<ChonostIcon name="logo" />
```

## 🎯 Best Practices

1. **ใช้ไอคอนที่เหมาะสม**: เลือกไอคอนที่สื่อความหมายชัดเจน
2. **ขนาดที่เหมาะสม**: ใช้ขนาดที่เหมาะสมกับบริบท
3. **สีที่สอดคล้อง**: ใช้สีที่สอดคล้องกับธีม
4. **Animation ที่เหมาะสม**: ใช้ animation ที่ไม่รบกวนผู้ใช้
5. **Accessibility**: ใส่ alt text สำหรับไอคอนที่สำคัญ

## 🚀 Future Enhancements

- [ ] เพิ่มไอคอนแบบ 3D
- [ ] เพิ่มไอคอนแบบ Interactive
- [ ] เพิ่มไอคอนแบบ Custom SVG
- [ ] เพิ่มไอคอนแบบ Lottie Animation
- [ ] เพิ่มไอคอนแบบ Micro-interactions

---

*ระบบไอคอนนี้ถูกออกแบบมาเพื่อให้ Chonost มีความสวยงามและใช้งานง่าย พร้อมรองรับการขยายตัวในอนาคต*
