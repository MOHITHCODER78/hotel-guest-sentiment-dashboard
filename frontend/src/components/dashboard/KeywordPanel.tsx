import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { KeywordsResponse } from "@/types/api"

function KeywordGroup({ title, items }: { title: string; items: { term: string; score: number }[] }) {
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium">{title}</p>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">No keywords available yet.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {items.map((item) => (
            <span
              key={`${title}-${item.term}`}
              className="rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium"
              title={`Score: ${item.score.toFixed(3)}`}
            >
              {item.term}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export function KeywordPanel({ keywords }: { keywords: KeywordsResponse }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle>Keyword Intelligence</CardTitle>
          <CardDescription>Recurring complaint and praise themes from guest reviews</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <KeywordGroup title="Top Overall Terms" items={keywords.overall_keywords} />
          <KeywordGroup title="Positive Terms" items={keywords.positive_keywords} />
          <KeywordGroup title="Negative Terms" items={keywords.negative_keywords} />
        </CardContent>
      </Card>
    </motion.div>
  )
}