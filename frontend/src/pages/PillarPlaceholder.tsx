import { motion } from 'framer-motion'
import { CircleDashed } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function PillarPlaceholder({ name, description }: { name: string; description: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex h-full items-center justify-center"
    >
      <Card className="glass-panel max-w-md border-0 text-center">
        <CardHeader className="items-center">
          <CircleDashed className="mb-2 h-8 w-8 text-muted-foreground" />
          <CardTitle className="font-heading text-xl">{name}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{description}</p>
          <p className="mt-3 font-mono text-xs text-muted-foreground/70">
            Awaiting data source specification before calculations go live.
          </p>
        </CardContent>
      </Card>
    </motion.div>
  )
}
