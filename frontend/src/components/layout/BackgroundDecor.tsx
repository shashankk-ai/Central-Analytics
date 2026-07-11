import { createPortal } from 'react-dom'

export function BackgroundDecor() {
  return createPortal(
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute -top-40 -left-32 h-[36rem] w-[36rem] rounded-full bg-primary/50 blur-[110px] dark:bg-primary/35" />
      <div className="absolute top-1/4 -right-32 h-[32rem] w-[32rem] rounded-full bg-secondary/45 blur-[120px] dark:bg-secondary/25" />
      <div className="absolute bottom-[-12rem] left-1/3 h-[30rem] w-[30rem] rounded-full bg-[#2563EB]/35 blur-[120px] dark:bg-[#2563EB]/25" />
    </div>,
    document.body,
  )
}
