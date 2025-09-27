import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { FileUpload } from './FileUpload'
import { useAuth } from '../hooks/useAuth'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { CheckCircle, AlertCircle, FileText, Download, Trash2 } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { format } from 'date-fns'

export function FileManagement({ isMobile }) {
  const { apiRequest } = useAuth()
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUploadedFiles()
  }, [])

  const fetchUploadedFiles = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiRequest('/api/files/list?type=obsidian', { method: 'GET' })
      const result = await response.json()
      if (result.success) {
        setUploadedFiles(result.data.files)
      } else {
        setError(result.message || 'ไม่สามารถดึงรายการไฟล์ได้')
      }
    } catch (err) {
      setError('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUploaded = (newFiles) => {
    setUploadedFiles(prev => [...newFiles, ...prev])
  }

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('คุณแน่ใจหรือไม่ที่จะลบไฟล์นี้?')) {
      return
    }
    try {
      const response = await apiRequest(`/api/files/${fileId}`, { method: 'DELETE' })
      const result = await response.json()
      if (result.success) {
        setUploadedFiles(prev => prev.filter(file => file.id !== fileId))
      } else {
        setError(result.message || 'ไม่สามารถลบไฟล์ได้')
      }
    } catch (err) {
      setError('เกิดข้อผิดพลาดในการลบไฟล์: ' + err.message)
    }
  }

  return (
    <div className="flex flex-col h-full p-4 overflow-y-auto">
      <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">การจัดการไฟล์</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        อัปโหลดและจัดการไฟล์ประเภทต่างๆ ของคุณในที่เดียว
      </p>

      <FileUpload onFileUploaded={handleFileUploaded} className="mb-6" />

      <Card className="flex-1">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            ไฟล์ที่อัปโหลดแล้ว
          </CardTitle>
          <CardDescription>
            รายการไฟล์ทั้งหมดที่คุณอัปโหลด
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && <p className="text-center text-gray-500">กำลังโหลดไฟล์...</p>}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {!loading && uploadedFiles.length === 0 && !error && (
            <p className="text-center text-gray-500">ยังไม่มีไฟล์ Obsidian ที่อัปโหลด</p>
          )}
          <div className="space-y-3">
            {uploadedFiles.map(file => (
              <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg bg-gray-50 dark:bg-gray-800">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{file.original_name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {file.file_type} - {Math.round(file.file_size / 1024)} KB
                      {file.created_at && ` - อัปโหลดเมื่อ ${format(new Date(file.created_at), 'dd/MM/yyyy HH:mm')}`}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" asChild>
                    <a href={file.url} download={file.original_name}>
                      <Download className="w-4 h-4 mr-2" /> ดาวน์โหลด
                    </a>
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDeleteFile(file.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

