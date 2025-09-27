import React from 'react'
import { Home, ArrowLeft } from 'lucide-react'
import { Button } from '@/shared/ui/button'

const NotFound = () => {
  const handleGoHome = () => {
    window.location.href = '/'
  }

  const handleGoBack = () => {
    window.history.back()
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300 dark:text-gray-600">404</h1>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            ไม่พบหน้าที่ต้องการ
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            ขออภัย หน้าที่คุณกำลังมองหาไม่มีอยู่ หรืออาจถูกย้ายไปแล้ว
          </p>
        </div>
        
        <div className="space-y-3">
          <Button onClick={handleGoHome} className="w-full">
            <Home className="mr-2 h-4 w-4" />
            กลับหน้าหลัก
          </Button>
          <Button onClick={handleGoBack} variant="outline" className="w-full">
            <ArrowLeft className="mr-2 h-4 w-4" />
            กลับหน้าก่อนหน้า
          </Button>
        </div>
      </div>
    </div>
  )
}

export { NotFound }


