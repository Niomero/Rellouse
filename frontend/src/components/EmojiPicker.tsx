import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import EmojiPickerReact, { EmojiClickData, Theme } from 'emoji-picker-react'
import { Smile } from 'lucide-react'
import { useThemeStore } from '../store/themeStore'
import { cn } from '../utils/cn'

interface EmojiPickerProps {
  onEmojiSelect: (emoji: string) => void
  className?: string
}

export function EmojiPicker({ onEmojiSelect, className }: EmojiPickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const { theme } = useThemeStore()
  const pickerRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        pickerRef.current &&
        !pickerRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleEmojiClick = (emojiData: EmojiClickData) => {
    onEmojiSelect(emojiData.emoji)
    setIsOpen(false)
  }

  return (
    <div className={cn('relative', className)}>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'liquid-btn liquid-hover liquid-press p-2 rounded-xl transition-all',
          isOpen && 'bg-primary-100 dark:bg-primary-900/30'
        )}
        aria-label="Open emoji picker"
      >
        <Smile className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={pickerRef}
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.15 }}
            className="absolute bottom-full mb-2 right-0 z-50 glass rounded-2xl shadow-2xl overflow-hidden"
          >
            <EmojiPickerReact
              onEmojiClick={handleEmojiClick}
              theme={theme === 'dark' ? Theme.DARK : Theme.LIGHT}
              width={350}
              height={450}
              searchPlaceHolder="Search emoji..."
              previewConfig={{
                showPreview: false,
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
