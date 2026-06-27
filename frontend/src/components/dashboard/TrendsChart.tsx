import { motion } from "framer-motion"
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { TrendPoint } from "@/types/api"

export function TrendsChart({ data }: { data: TrendPoint[] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Trends</CardTitle>
          <CardDescription>Average guest sentiment over time</CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          {data.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              Upload more reviews to unlock trend analysis.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="period" tick={{ fill: "currentColor" }} />
                <YAxis domain={[0, 1]} tick={{ fill: "currentColor" }} />
                <Tooltip
                  formatter={(value) => [
                    `${Number(value ?? 0) * 100}%`,
                    "Sentiment",
                  ]}
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.75rem",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_sentiment"
                  stroke="var(--primary)"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
