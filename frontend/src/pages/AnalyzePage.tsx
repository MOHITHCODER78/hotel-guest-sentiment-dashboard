import { AnalyzePanel } from "@/components/analyze/AnalyzePanel"

export function AnalyzePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analyze Review</h1>
        <p className="text-muted-foreground">
          Run real-time aspect-based sentiment analysis on individual guest feedback.
        </p>
      </div>
      <AnalyzePanel />
    </div>
  )
}
