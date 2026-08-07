import { FeatureCard } from '@/components/FeatureCard'
import { featureCards } from '@/services/navigation'

export function HomePage() {
  return (
    <section className="flex flex-col gap-3">
      {featureCards.map((item, index) => (
        <div
          key={item.id}
          className="animate-in fade-in slide-in-from-bottom-2 fill-mode-both duration-500"
          style={{ animationDelay: `${70 + index * 45}ms` }}
        >
          <FeatureCard item={item} />
        </div>
      ))}
    </section>
  )
}
