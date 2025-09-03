import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useTheme } from '../../shared/ThemeProvider'
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Database,
  Download,
  Upload,
  Trash2,
  Sun,
  Moon,
  Monitor
} from 'lucide-react'

export function Settings() {
  const { theme, setLightTheme, setDarkTheme, toggleTheme } = useTheme()
  
  const [settings, setSettings] = useState({
    // User Settings
    username: 'ผู้ใช้งาน',
    email: 'user@example.com',
    
    // Notification Settings
    emailNotifications: true,
    pushNotifications: false,
    workflowNotifications: true,
    
    // Privacy Settings
    dataSharing: false,
    analytics: true,
    
    // Appearance Settings
    language: 'th',
    
    // API Settings
    openaiApiKey: '',
    maxTokens: 2000,
    temperature: 0.7
  })

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleThemeChange = (newTheme) => {
    if (newTheme === 'light') {
      setLightTheme()
    } else if (newTheme === 'dark') {
      setDarkTheme()
    }
  }

  const saveSettings = () => {
    // TODO: Implement save settings API call
    alert('บันทึกการตั้งค่าเรียบร้อยแล้ว')
  }

  const exportData = () => {
    // TODO: Implement data export
    alert('กำลังเตรียมข้อมูลสำหรับการส่งออก...')
  }

  const importData = () => {
    // TODO: Implement data import
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = (e) => {
      const file = e.target.files[0]
      if (file) {
        alert(`กำลังนำเข้าข้อมูลจากไฟล์: ${file.name}`)
      }
    }
    input.click()
  }

  const clearAllData = () => {
    if (confirm('คุณแน่ใจหรือไม่ที่จะลบข้อมูลทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้')) {
      // TODO: Implement clear all data
      alert('ลบข้อมูลทั้งหมดเรียบร้อยแล้ว')
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">ตั้งค่า</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">จัดการการตั้งค่าและการกำหนดค่าระบบ</p>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="max-w-4xl space-y-6">
          {/* User Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="mr-2 h-5 w-5" />
                ข้อมูลผู้ใช้
              </CardTitle>
              <CardDescription>
                จัดการข้อมูลส่วนตัวและโปรไฟล์ของคุณ
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="username">ชื่อผู้ใช้</Label>
                  <Input
                    id="username"
                    value={settings.username}
                    onChange={(e) => handleSettingChange('username', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="email">อีเมล</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.email}
                    onChange={(e) => handleSettingChange('email', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="mr-2 h-5 w-5" />
                การแจ้งเตือน
              </CardTitle>
              <CardDescription>
                กำหนดการแจ้งเตือนที่คุณต้องการรับ
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="email-notifications">การแจ้งเตือนทางอีเมล</Label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">รับการแจ้งเตือนสำคัญทางอีเมล</p>
                </div>
                <Switch
                  id="email-notifications"
                  checked={settings.emailNotifications}
                  onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="push-notifications">การแจ้งเตือนแบบ Push</Label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">รับการแจ้งเตือนผ่านเบราว์เซอร์</p>
                </div>
                <Switch
                  id="push-notifications"
                  checked={settings.pushNotifications}
                  onCheckedChange={(checked) => handleSettingChange('pushNotifications', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="workflow-notifications">การแจ้งเตือน Workflow</Label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">รับการแจ้งเตือนเมื่อ workflow เสร็จสิ้น</p>
                </div>
                <Switch
                  id="workflow-notifications"
                  checked={settings.workflowNotifications}
                  onCheckedChange={(checked) => handleSettingChange('workflowNotifications', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Privacy Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="mr-2 h-5 w-5" />
                ความเป็นส่วนตัว
              </CardTitle>
              <CardDescription>
                ควบคุมการใช้งานและการแชร์ข้อมูลของคุณ
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="data-sharing">การแชร์ข้อมูล</Label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">อนุญาตให้แชร์ข้อมูลเพื่อปรับปรุงบริการ</p>
                </div>
                <Switch
                  id="data-sharing"
                  checked={settings.dataSharing}
                  onCheckedChange={(checked) => handleSettingChange('dataSharing', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="analytics">การวิเคราะห์การใช้งาน</Label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">ช่วยปรับปรุงประสบการณ์การใช้งาน</p>
                </div>
                <Switch
                  id="analytics"
                  checked={settings.analytics}
                  onCheckedChange={(checked) => handleSettingChange('analytics', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Appearance Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Palette className="mr-2 h-5 w-5" />
                รูปแบบการแสดงผล
              </CardTitle>
              <CardDescription>
                ปรับแต่งธีมและภาษาของแอปพลิเคชัน
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>ธีม</Label>
                <div className="flex gap-2 mt-2">
                  <Button
                    variant={theme === 'light' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleThemeChange('light')}
                  >
                    <Sun className="mr-2 h-4 w-4" />
                    สว่าง
                  </Button>
                  <Button
                    variant={theme === 'dark' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleThemeChange('dark')}
                  >
                    <Moon className="mr-2 h-4 w-4" />
                    มืด
                  </Button>
                </div>
              </div>
              
              <div>
                <Label htmlFor="language">ภาษา</Label>
                <select
                  id="language"
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                  className="w-full mt-1 p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                >
                  <option value="th">ไทย</option>
                  <option value="en">English</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* API Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="mr-2 h-5 w-5" />
                การตั้งค่า API
              </CardTitle>
              <CardDescription>
                กำหนดค่า API keys และพารามิเตอร์สำหรับ AI
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="openai-api-key">OpenAI API Key</Label>
                <Input
                  id="openai-api-key"
                  type="password"
                  value={settings.openaiApiKey}
                  onChange={(e) => handleSettingChange('openaiApiKey', e.target.value)}
                  placeholder="กรอก OpenAI API Key"
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  API Key ของคุณจะถูกเข้ารหัสและเก็บไว้อย่างปลอดภัย
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="max-tokens">Max Tokens</Label>
                  <Input
                    id="max-tokens"
                    type="number"
                    value={settings.maxTokens}
                    onChange={(e) => handleSettingChange('maxTokens', parseInt(e.target.value))}
                    min="100"
                    max="4000"
                  />
                </div>
                <div>
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input
                    id="temperature"
                    type="number"
                    value={settings.temperature}
                    onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
                    min="0"
                    max="2"
                    step="0.1"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Data Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="mr-2 h-5 w-5" />
                การจัดการข้อมูล
              </CardTitle>
              <CardDescription>
                ส่งออก นำเข้า หรือลบข้อมูลของคุณ
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="outline" onClick={exportData}>
                  <Download className="mr-2 h-4 w-4" />
                  ส่งออกข้อมูล
                </Button>
                <Button variant="outline" onClick={importData}>
                  <Upload className="mr-2 h-4 w-4" />
                  นำเข้าข้อมูล
                </Button>
                <Button variant="destructive" onClick={clearAllData}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  ลบข้อมูลทั้งหมด
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={saveSettings} size="lg">
              บันทึกการตั้งค่า
            </Button>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}

