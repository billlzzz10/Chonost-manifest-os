import { useState, useRef } from 'react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Progress } from '@/shared/ui/progress'
import { Badge } from '@/shared/ui/badge'
import { 
  Upload, 
  File, 
  FileText, 
  Image, 
  X, 
  CheckCircle, 
  AlertCircle,
  Download,
  ExternalLink
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export function FileUpload({ onFileUploaded, className = '' }) {
  const { apiRequest } = useAuth()
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef(null)

  // ประเภทไฟล์ที่รองรับ
  const supportedTypes = {
    'text/markdown': { icon: FileText, label: 'Markdown', color: 'bg-blue-100 text-blue-800' },
    'text/plain': { icon: FileText, label: 'Text', color: 'bg-gray-100 text-gray-800' },
    'application/json': { icon: File, label: 'JSON', color: 'bg-green-100 text-green-800' },
    'image/png': { icon: Image, label: 'PNG', color: 'bg-purple-100 text-purple-800' },
    'image/jpeg': { icon: Image, label: 'JPEG', color: 'bg-purple-100 text-purple-800' },
    'image/jpg': { icon: Image, label: 'JPG', color: 'bg-purple-100 text-purple-800' },
    'application/pdf': { icon: FileText, label: 'PDF', color: 'bg-red-100 text-red-800' },
    'application/msword': { icon: FileText, label: 'DOC', color: 'bg-blue-200 text-blue-900' },
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { icon: FileText, label: 'DOCX', color: 'bg-blue-200 text-blue-900' },
    'application/vnd.ms-excel': { icon: FileText, label: 'XLS', color: 'bg-green-200 text-green-900' },
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { icon: FileText, label: 'XLSX', color: 'bg-green-200 text-green-900' },
    'text/csv': { icon: FileText, label: 'CSV', color: 'bg-yellow-100 text-yellow-800' }
  }

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files)
    const validFiles = []
    
    selectedFiles.forEach(file => {
      if (supportedTypes[file.type] || file.name.endsWith('.md')) {
        validFiles.push({
          file,
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type || 'text/markdown',
          status: 'pending'
        })
      }
    })

    if (validFiles.length !== selectedFiles.length) {
      setError('บางไฟล์ไม่รองรับ กรุณาเลือกไฟล์ Markdown, Text, JSON หรือรูปภาพเท่านั้น')
    } else {
      setError('')
    }

    setFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const uploadFiles = async () => {
    if (files.length === 0) {
      setError('กรุณาเลือกไฟล์ที่ต้องการอัปโหลด')
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')
    setUploadProgress(0)

    try {
      const uploadedFiles = []
      
      for (let i = 0; i < files.length; i++) {
        const fileData = files[i]
        const formData = new FormData()
        formData.append('file', fileData.file)


        // อัปเดตสถานะไฟล์
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'uploading' }
            : f
        ))

        try {
          const response = await apiRequest('/api/files/upload', {
            method: 'POST',
            body: formData,
            headers: {} // ไม่ต้องใส่ Content-Type สำหรับ FormData
          })

          const result = await response.json()

          if (result.success) {
            // อัปเดตสถานะเป็นสำเร็จ
            setFiles(prev => prev.map(f => 
              f.id === fileData.id 
                ? { ...f, status: 'success', uploadedData: result.data }
                : f
            ))
            uploadedFiles.push(result.data)
          } else {
            // อัปเดตสถานะเป็นผิดพลาด
            setFiles(prev => prev.map(f => 
              f.id === fileData.id 
                ? { ...f, status: 'error', error: result.message }
                : f
            ))
          }
        } catch (fileError) {
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { ...f, status: 'error', error: 'เกิดข้อผิดพลาดในการอัปโหลด' }
              : f
          ))
        }

        // อัปเดต progress
        setUploadProgress(((i + 1) / files.length) * 100)
      }

      if (uploadedFiles.length > 0) {
        setSuccess(`อัปโหลดไฟล์สำเร็จ ${uploadedFiles.length} ไฟล์`)
        if (onFileUploaded) {
          onFileUploaded(uploadedFiles)
        }
      }

    } catch (error) {
      console.error('Upload error:', error)
      setError('เกิดข้อผิดพลาดในการอัปโหลดไฟล์')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const clearAll = () => {
    setFiles([])
    setError('')
    setSuccess('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getFileIcon = (type) => {
    const fileType = supportedTypes[type]
    return fileType ? fileType.icon : File
  }

  const getFileLabel = (type) => {
    const fileType = supportedTypes[type]
    return fileType ? fileType.label : 'Unknown'
  }

  const getFileColor = (type) => {
    const fileType = supportedTypes[type]
    return fileType ? fileType.color : 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'uploading':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      default:
        return null
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          อัปโหลดไฟล์
        </CardTitle>
        <CardDescription>
          อัปโหลดไฟล์ Markdown, Text, JSON, รูปภาพ หรือไฟล์อื่นๆ ที่รองรับ
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {/* File Input */}
        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".md,.txt,.json,.png,.jpg,.jpeg,.pdf,.doc,.docx,.csv,.xls,.xlsx"
            onChange={handleFileSelect}
            className="hidden"
            disabled={uploading}
          />
          
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            คลิกเพื่อเลือกไฟล์หรือลากไฟล์มาวางที่นี่
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mb-4">
            รองรับ: .md, .txt, .json, .png, .jpg, .jpeg, .pdf, .doc, .docx, .csv, .xls, .xlsx
          </p>
          
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            variant="outline"
          >
            เลือกไฟล์
          </Button>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium">ไฟล์ที่เลือก ({files.length})</h4>
              <Button
                onClick={clearAll}
                variant="ghost"
                size="sm"
                disabled={uploading}
              >
                ล้างทั้งหมด
              </Button>
            </div>

            <div className="max-h-60 overflow-y-auto space-y-2">
              {files.map((fileData) => {
                const Icon = getFileIcon(fileData.type)
                return (
                  <div
                    key={fileData.id}
                    className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    <Icon className="w-5 h-5 text-gray-500" />
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {fileData.name}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className={getFileColor(fileData.type)}>
                          {getFileLabel(fileData.type)}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {formatFileSize(fileData.size)}
                        </span>
                      </div>
                      {fileData.error && (
                        <p className="text-xs text-red-500 mt-1">{fileData.error}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {getStatusIcon(fileData.status)}
                      
                      {fileData.status === 'success' && fileData.uploadedData && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => window.open(fileData.uploadedData.url, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      )}
                      
                      {fileData.status !== 'uploading' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeFile(fileData.id)}
                          disabled={uploading}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {uploading && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>กำลังอัปโหลด...</span>
              <span>{Math.round(uploadProgress)}%</span>
            </div>
            <Progress value={uploadProgress} className="w-full" />
          </div>
        )}

        {/* Upload Button */}
        {files.length > 0 && (
          <div className="flex gap-2">
            <Button
              onClick={uploadFiles}
              disabled={uploading || files.length === 0}
              className="flex-1"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  กำลังอัปโหลด...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  อัปโหลด {files.length} ไฟล์
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

