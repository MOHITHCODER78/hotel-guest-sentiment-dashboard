import { motion } from "framer-motion"
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { AspectStat } from "@/types/api"

export function AspectChart({ data }: { data: AspectStat[] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle>Aspect Sentiment Breakdown</CardTitle>
          <CardDescription>Average sentiment score by hotel aspect</CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          {data.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              Upload reviews to see aspect analytics.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="aspect" tick={{ fill: "currentColor" }} />
                <YAxis domain={[0, 1]} tick={{ fill: "currentColor" }} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.75rem",
                  }}
                />
                <Bar dataKey="avg_score" fill="var(--primary)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
