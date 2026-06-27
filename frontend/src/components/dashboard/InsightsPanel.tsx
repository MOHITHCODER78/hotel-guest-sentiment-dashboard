import { motion } from "framer-motion"
import { Download, Lightbulb } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { downloadPdfReport } from "@/services/hotel-api"
import type { InsightsResponse } from "@/types/api"

export function InsightsPanel({ insights }: { insights: InsightsResponse }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              AI Executive Insights
            </CardTitle>
            <CardDescription>Actionable recommendations for hotel managers</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => downloadPdfReport()}>
            <Download className="mr-2 h-4 w-4" />
            PDF Report
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-relaxed">{insights.summary}</p>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-border bg-muted/30 p-3">
              <p className="text-xs uppercase text-muted-foreground">Top Strength</p>
              <p className="font-medium">{insights.top_strength ?? "Not enough data"}</p>
            </div>
            <div className="rounded-lg border border-border bg-muted/30 p-3">
              <p className="text-xs uppercase text-muted-foreground">Top Weakness</p>
              <p className="font-medium">{insights.top_weakness ?? "Not enough data"}</p>
            </div>
          </div>

          <div className="space-y-3">
            {insights.recommendations.map((item) => (
              <div key={item.title} className="rounded-lg border border-border p-4">
                <div className="mb-1 flex items-center gap-2">
                  <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                    {item.priority}
                  </span>
                  <p className="font-medium">{item.title}</p>
                </div>
                <p className="text-sm text-muted-foreground">{item.detail}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
