import React from 'react';
import { Icon } from '@iconify/react';

// สีพาสเทลไล่สีสำหรับไอคอน
const pastelColors = {
  primary: [
    '#FFB3BA', // พาสเทลชมพู
    '#BAFFC9', // พาสเทลเขียว
    '#BAE1FF', // พาสเทลฟ้า
    '#FFFFBA', // พาสเทลเหลือง
    '#FFB3F7', // พาสเทลม่วง
    '#B3FFE6', // พาสเทลมินต์
    '#FFD4B3', // พาสเทลส้ม
    '#E6B3FF', // พาสเทลลาเวนเดอร์
  ],
  secondary: [
    '#FF8A9A', // ชมพูเข้ม
    '#8AFF9A', // เขียวเข้ม
    '#8AC4FF', // ฟ้าเข้ม
    '#FFFF8A', // เหลืองเข้ม
    '#FF8AFF', // ม่วงเข้ม
    '#8AFFE6', // มินต์เข้ม
    '#FFB38A', // ส้มเข้ม
    '#B38AFF', // ลาเวนเดอร์เข้ม
  ]
};

// ระบบไอคอนสำหรับ Chonost
export const ChonostIcons = {
  // ไอคอนหลักของแอป
  logo: {
    icon: 'noto:books',
    color: pastelColors.primary[2], // พาสเทลฟ้า
    size: '2rem'
  },
  
  // ไอคอนสำหรับ Navigation
  dashboard: {
    icon: 'noto:house',
    color: pastelColors.primary[0], // พาสเทลชมพู
    size: '1.5rem'
  },
  editor: {
    icon: 'noto:memo',
    color: pastelColors.primary[1], // พาสเทลเขียว
    size: '1.5rem'
  },
  characters: {
    icon: 'noto:people',
    color: pastelColors.primary[4], // พาสเทลม่วง
    size: '1.5rem'
  },
  projects: {
    icon: 'noto:open-book',
    color: pastelColors.primary[3], // พาสเทลเหลือง
    size: '1.5rem'
  },
  
  // ไอคอนสำหรับ Editor Tools
  save: {
    icon: 'noto:floppy-disk',
    color: pastelColors.secondary[1], // เขียวเข้ม
    size: '1.2rem'
  },
  bold: {
    icon: 'noto:bold-letter-b',
    color: pastelColors.secondary[0], // ชมพูเข้ม
    size: '1.2rem'
  },
  italic: {
    icon: 'noto:italic-letter-i',
    color: pastelColors.secondary[2], // ฟ้าเข้ม
    size: '1.2rem'
  },
  heading: {
    icon: 'noto:hash',
    color: pastelColors.secondary[3], // เหลืองเข้ม
    size: '1.2rem'
  },
  
  // ไอคอนสำหรับ Character Analysis
  character: {
    icon: 'noto:person',
    color: pastelColors.primary[4], // พาสเทลม่วง
    size: '1.2rem'
  },
  relationship: {
    icon: 'noto:heart',
    color: pastelColors.primary[0], // พาสเทลชมพู
    size: '1.2rem'
  },
  stats: {
    icon: 'noto:bar-chart',
    color: pastelColors.primary[1], // พาสเทลเขียว
    size: '1.2rem'
  },
  
  // ไอคอนสำหรับ AI Features
  ai: {
    icon: 'noto:robot',
    color: pastelColors.primary[5], // พาสเทลมินต์
    size: '1.2rem'
  },
  brain: {
    icon: 'noto:brain',
    color: pastelColors.primary[6], // พาสเทลส้ม
    size: '1.2rem'
  },
  magic: {
    icon: 'noto:sparkles',
    color: pastelColors.primary[7], // พาสเทลลาเวนเดอร์
    size: '1.2rem'
  },
  
  // ไอคอนสำหรับ Mood Tracking (Ashval)
  happy: {
    icon: 'noto:grinning-face',
    color: pastelColors.primary[3], // พาสเทลเหลือง
    size: '2rem'
  },
  stressed: {
    icon: 'noto:anxious-face-with-sweat',
    color: pastelColors.secondary[0], // ชมพูเข้ม
    size: '2rem'
  },
  focused: {
    icon: 'noto:face-with-monocle',
    color: pastelColors.primary[2], // พาสเทลฟ้า
    size: '2rem'
  },
  bored: {
    icon: 'noto:expressionless-face',
    color: pastelColors.primary[6], // พาสเทลส้ม
    size: '2rem'
  },
  
  // ไอคอนสำหรับ Task Management
  task: {
    icon: 'noto:check-box-with-check',
    color: pastelColors.primary[1], // พาสเทลเขียว
    size: '1.2rem'
  },
  priority: {
    icon: 'noto:exclamation-mark',
    color: pastelColors.secondary[0], // ชมพูเข้ม
    size: '1.2rem'
  },
  deadline: {
    icon: 'noto:alarm-clock',
    color: pastelColors.secondary[3], // เหลืองเข้ม
    size: '1.2rem'
  },
  
  // ไอคอนสำหรับ Technology Stack
  react: {
    icon: 'skill-icons:react-dark',
    color: '#61DAFB',
    size: '1.5rem'
  },
  typescript: {
    icon: 'skill-icons:typescript',
    color: '#3178C6',
    size: '1.5rem'
  },
  tailwind: {
    icon: 'skill-icons:tailwindcss-dark',
    color: '#06B6D4',
    size: '1.5rem'
  },
  nodejs: {
    icon: 'skill-icons:nodejs-dark',
    color: '#339933',
    size: '1.5rem'
  },
  python: {
    icon: 'skill-icons:python-dark',
    color: '#3776AB',
    size: '1.5rem'
  },
  ai: {
    icon: 'skill-icons:openai-dark',
    color: '#412991',
    size: '1.5rem'
  },
  
  // ไอคอนสำหรับ Social & Brand
  github: {
    icon: 'bxl:github',
    color: '#181717',
    size: '1.5rem'
  },
  twitter: {
    icon: 'bxl:twitter',
    color: '#1DA1F2',
    size: '1.5rem'
  },
  discord: {
    icon: 'bxl:discord-alt',
    color: '#5865F2',
    size: '1.5rem'
  },
  
  // ไอคอนสำหรับ Development Tools
  vscode: {
    icon: 'devicon:vscode',
    color: '#007ACC',
    size: '1.5rem'
  },
  git: {
    icon: 'devicon:git',
    color: '#F05032',
    size: '1.5rem'
  },
  docker: {
    icon: 'devicon:docker',
    color: '#2496ED',
    size: '1.5rem'
  }
};

// Component สำหรับแสดงไอคอน
export const ChonostIcon = ({ 
  name, 
  size = '1.5rem', 
  color = null, 
  className = '',
  onClick = null,
  style = {}
}) => {
  const iconConfig = ChonostIcons[name];
  
  if (!iconConfig) {
    console.warn(`Icon "${name}" not found in ChonostIcons`);
    return null;
  }
  
  const iconColor = color || iconConfig.color;
  const iconSize = size || iconConfig.size;
  
  return (
    <Icon
      icon={iconConfig.icon}
      width={iconSize}
      height={iconSize}
      color={iconColor}
      className={`chonost-icon ${className}`}
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        ...style
      }}
    />
  );
};

// Component สำหรับแสดงไอคอนแบบ Animated
export const AnimatedIcon = ({ 
  name, 
  size = '1.5rem', 
  color = null, 
  animation = 'pulse',
  className = '',
  onClick = null 
}) => {
  const animationStyles = {
    pulse: {
      animation: 'pulse 2s infinite'
    },
    bounce: {
      animation: 'bounce 1s infinite'
    },
    spin: {
      animation: 'spin 1s linear infinite'
    },
    wiggle: {
      animation: 'wiggle 1s ease-in-out infinite'
    }
  };
  
  return (
    <ChonostIcon
      name={name}
      size={size}
      color={color}
      className={`animated-icon ${className}`}
      onClick={onClick}
      style={animationStyles[animation]}
    />
  );
};

// Component สำหรับแสดงไอคอนแบบ Gradient
export const GradientIcon = ({ 
  name, 
  size = '1.5rem', 
  gradient = 'linear-gradient(45deg, #FFB3BA, #BAE1FF)',
  className = '',
  onClick = null 
}) => {
  return (
    <div
      className={`gradient-icon ${className}`}
      onClick={onClick}
      style={{
        background: gradient,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease'
      }}
    >
      <ChonostIcon name={name} size={size} />
    </div>
  );
};

// Component สำหรับแสดงไอคอนแบบ Floating
export const FloatingIcon = ({ 
  name, 
  size = '1.5rem', 
  color = null, 
  className = '',
  onClick = null 
}) => {
  return (
    <div
      className={`floating-icon ${className}`}
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.1))'
      }}
    >
      <ChonostIcon name={name} size={size} color={color} />
    </div>
  );
};

// CSS สำหรับ Animation
const iconStyles = `
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  @keyframes bounce {
    0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
    40%, 43% { transform: translate3d(0,-30px,0); }
    70% { transform: translate3d(0,-15px,0); }
    90% { transform: translate3d(0,-4px,0); }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes wiggle {
    0%, 7% { transform: rotateZ(0); }
    15% { transform: rotateZ(-15deg); }
    20% { transform: rotateZ(10deg); }
    25% { transform: rotateZ(-10deg); }
    30% { transform: rotateZ(6deg); }
    35% { transform: rotateZ(-4deg); }
    40%, 100% { transform: rotateZ(0); }
  }
  
  .chonost-icon {
    display: inline-block;
    vertical-align: middle;
  }
  
  .chonost-icon:hover {
    transform: scale(1.1);
  }
  
  .animated-icon {
    display: inline-block;
  }
  
  .gradient-icon {
    display: inline-block;
    padding: 4px;
    border-radius: 8px;
  }
  
  .gradient-icon:hover {
    transform: scale(1.05);
  }
  
  .floating-icon {
    display: inline-block;
    padding: 8px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
  }
  
  .floating-icon:hover {
    transform: translateY(-2px);
    filter: drop-shadow(0 6px 12px rgba(0,0,0,0.15));
  }
`;

// เพิ่ม CSS styles เข้าไปใน document
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = iconStyles;
  document.head.appendChild(style);
}

export default ChonostIcon;
