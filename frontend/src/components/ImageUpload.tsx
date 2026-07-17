import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react'
import { cn } from '../utils/cn'
import { useToast } from '../hooks/useToast'
import api from '../services/api'

interface ImageUploadProps {
  onUpload: (imageUrl: string, imageData: ImageData) => void
  onCancel?: () => void
  maxSize?: number // in MB
  className?: string
}

interface ImageData {
  url: string
  fileName: string
  fileSize: number
  fileType: string
  width?: number
  height?: number
  thumbnailUrl?: string
}

export function ImageUpload({
  onUpload,
  onCancel,
  maxSize = 10,
  className,
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [imageData, setImageData] = useState<ImageData | null>(null)
  const { error: showError } = useToast()

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return

      // Validate file size
      if (file.size > maxSize * 1024 * 1024) {
        showError(`Image size must be less than ${maxSize}MB`)
        return
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        showError('Please upload an image file')
        return
      }

      // Create preview
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      // Upload to server
      setUploading(true)
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await api.post<ImageData>('/upload/image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        setImageData(response.data)
      } catch (error: any) {
        showError(error.response?.data?.detail || 'Failed to upload image')
        setPreview(null)
      } finally {
        setUploading(false)
      }
    },
    [maxSize, showError]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  const handleConfirm = () => {
    if (imageData) {
      onUpload(imageData.url, imageData)
      setPreview(null)
      setImageData(null)
    }
  }

  const handleCancel = () => {
    setPreview(null)
    setImageData(null)
    onCancel?.()
  }

  return (
    <div className={cn('space-y-4', className)}>
      <AnimatePresence mode="wait">
        {!preview ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div
              {...getRootProps()}
              className={cn(
                'glass rounded-2xl p-8 border-2 border-dashed transition-all cursor-pointer',
                isDragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-neutral-300 dark:border-neutral-600 hover:border-primary-400',
                uploading && 'opacity-50 cursor-not-allowed'
              )}
            >
              <input {...getInputProps()} />
              
              <div className="flex flex-col items-center gap-4 text-center">
                {uploading ? (
                  <>
                    <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Uploading image...
                    </p>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                      <Upload className="w-8 h-8 text-white" />
                    </div>
                    
                    <div>
                      <p className="text-base font-medium text-neutral-900 dark:text-neutral-100">
                        {isDragActive
                          ? 'Drop image here'
                          : 'Click or drag image to upload'}
                      </p>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                        PNG, JPG, GIF, WEBP up to {maxSize}MB
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="space-y-4"
          >
            <div className="glass rounded-2xl p-4 relative">
              <button
                onClick={handleCancel}
                className="absolute top-2 right-2 z-10 liquid-btn p-2 rounded-full bg-neutral-900/50 hover:bg-neutral-900/70 transition-colors"
                disabled={uploading}
              >
                <X className="w-5 h-5 text-white" />
              </button>

              <div className="relative rounded-xl overflow-hidden">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-auto max-h-96 object-contain"
                />
                
                {uploading && (
                  <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
                    <Loader2 className="w-12 h-12 text-white animate-spin" />
                  </div>
                )}
              </div>

              {imageData && (
                <div className="mt-3 flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                  <ImageIcon className="w-4 h-4" />
                  <span>{imageData.fileName}</span>
                  <span>•</span>
                  <span>{(imageData.fileSize / 1024 / 1024).toFixed(2)} MB</span>
                  {imageData.width && imageData.height && (
                    <>
                      <span>•</span>
                      <span>{imageData.width} × {imageData.height}</span>
                    </>
                  )}
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCancel}
                className="flex-1 liquid-btn rounded-xl px-6 py-3 font-medium text-sm"
                disabled={uploading}
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                className="flex-1 liquid-btn-primary rounded-xl px-6 py-3 font-medium text-sm"
                disabled={uploading || !imageData}
              >
                {uploading ? 'Uploading...' : 'Send Image'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface ImagePreviewProps {
  src: string
  alt?: string
  className?: string
  onClick?: () => void
}

export function ImagePreview({ src, alt, className, onClick }: ImagePreviewProps) {
  const [loaded, setLoaded] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: loaded ? 1 : 0 }}
      transition={{ duration: 0.3 }}
      className={cn('relative rounded-xl overflow-hidden', className)}
      onClick={onClick}
    >
      <img
        src={src}
        alt={alt || 'Image'}
        className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform duration-300"
        onLoad={() => setLoaded(true)}
      />
      
      {!loaded && (
        <div className="absolute inset-0 liquid-skeleton" />
      )}
    </motion.div>
  )
}
