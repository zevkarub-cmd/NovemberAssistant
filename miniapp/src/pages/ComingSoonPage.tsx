import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ComingSoonPageProps {
  title: string
  description: string
}

export function ComingSoonPage({ title, description }: ComingSoonPageProps) {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-400">
      <Link
        to="/"
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        На главную
      </Link>

      <Card className="p-0 overflow-hidden">
        <CardHeader className="border-b border-border/50 px-5 py-5">
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
        <CardContent className="px-5 py-6">
          <p className="text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
          <p className="mt-4 text-sm font-medium text-foreground">Скоро</p>
        </CardContent>
      </Card>
    </div>
  )
}
