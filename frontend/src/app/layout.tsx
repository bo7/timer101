import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Zeit Erfassung',
  description: 'Time tracking system for field employees',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  )
}
