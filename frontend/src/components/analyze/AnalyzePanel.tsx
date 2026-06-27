import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { motion } from "framer-motion"
import { Loader2, Sparkles } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { analyzeReview } from "@/services/hotel-api"
import { ApiRequestError } from "@/lib/api"

export function AnalyzePanel() {
  const [text, setText] = useState("")
  const mutation = useMutation({
    mutationFn: analyzeReview,
  })

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Live Review Analysis
          </CardTitle>
          <CardDescription>
            Paste a guest review to get instant aspect-based sentiment results.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            rows={6}
            placeholder="Example: The staff were friendly but the WiFi was slow and the room was not very clean."
            className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none ring-primary focus:ring-2"
          />

          <Button
            onClick={() => mutation.mutate(text)}
            disabled={!text.trim() || mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Review"
            )}
          </Button>

          {mutation.isError && (
            <p className="text-sm text-destructive">
              {mutation.error instanceof ApiRequestError
                ? mutation.error.message
                : "Analysis failed."}
            </p>
          )}

          {mutation.data && (
            <div className="space-y-3 rounded-lg border border-border bg-muted/30 p-4">
              <p className="text-sm text-muted-foreground">Detected aspects</p>
              <div className="flex flex-wrap gap-2">
                {mutation.data.sentiments.map((item) => (
                  <Badge
                    key={`${item.aspect}-${item.sentiment}`}
                    className={
                      item.sentiment === "POSITIVE"
                        ? "border-success/30 bg-success/10 text-success"
                        : "border-destructive/30 bg-destructive/10 text-destructive"
                    }
                  >
                    {item.aspect}: {item.sentiment} ({item.score.toFixed(2)})
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
