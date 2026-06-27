import { motion } from "framer-motion"
import { AlertTriangle, BarChart3, TrendingUp } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { StatsResponse } from "@/types/api"

export function StatCards({ stats }: { stats: StatsResponse }) {
  const avgScore =
    stats.aspect_breakdown.length > 0
      ? stats.aspect_breakdown.reduce((sum, item) => sum + item.avg_score, 0) /
        stats.aspect_breakdown.length
      : 0

  const cards = [
    {
      title: "Total Reviews",
      value: stats.total_reviews.toLocaleString(),
      icon: BarChart3,
    },
    {
      title: "Guest Sentiment",
      value: `${(avgScore * 100).toFixed(1)}%`,
      icon: TrendingUp,
    },
    {
      title: "Critical Issues",
      value: String(stats.critical_issues.length),
      icon: AlertTriangle,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.08 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <card.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
