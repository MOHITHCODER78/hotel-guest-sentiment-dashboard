import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { CriticalIssue } from "@/types/api"

export function CriticalIssues({ issues }: { issues: CriticalIssue[] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle>Operational Alerts</CardTitle>
          <CardDescription>Areas that may need manager attention</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {issues.map((issue) => (
            <div
              key={issue.issue}
              className="rounded-lg border border-border bg-muted/40 p-4"
            >
              <p className="font-medium">{issue.issue}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Impact: {issue.impact} · {issue.frequency}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  )
}
