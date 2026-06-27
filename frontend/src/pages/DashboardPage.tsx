import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { AspectChart } from "@/components/dashboard/AspectChart"
import { CriticalIssues } from "@/components/dashboard/CriticalIssues"
import { InsightsPanel } from "@/components/dashboard/InsightsPanel"
import { KeywordPanel } from "@/components/dashboard/KeywordPanel"
import { StatCards } from "@/components/dashboard/StatCards"
import { TrendsChart } from "@/components/dashboard/TrendsChart"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { downloadAnalyticsCsv, fetchInsights, fetchKeywords, fetchStats, fetchTrends } from "@/services/hotel-api"
import { ApiRequestError } from "@/lib/api"

export function DashboardPage() {
  const [trendPeriod, setTrendPeriod] = useState<"weekly" | "monthly">("weekly")
  const [hotel, setHotel] = useState("")

  const statsQuery = useQuery({ queryKey: ["stats", hotel], queryFn: () => fetchStats(hotel || undefined) })
  const trendsQuery = useQuery({
    queryKey: ["trends", trendPeriod, hotel],
    queryFn: () => fetchTrends(trendPeriod, hotel || undefined),
  })
  const insightsQuery = useQuery({
    queryKey: ["insights", hotel],
    queryFn: () => fetchInsights(hotel || undefined),
  })
  const keywordsQuery = useQuery({
    queryKey: ["keywords", hotel],
    queryFn: () => fetchKeywords(hotel || undefined),
  })

  const isLoading =
    statsQuery.isLoading || trendsQuery.isLoading || insightsQuery.isLoading || keywordsQuery.isLoading

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <Skeleton className="h-80" />
      </div>
    )
  }

  if (statsQuery.isError || trendsQuery.isError || insightsQuery.isError || keywordsQuery.isError) {
    const error = statsQuery.error ?? trendsQuery.error ?? insightsQuery.error ?? keywordsQuery.error
    return (
      <p className="text-destructive">
        {error instanceof ApiRequestError ? error.message : "Failed to load dashboard."}
      </p>
    )
  }

  if (!statsQuery.data || !trendsQuery.data || !insightsQuery.data || !keywordsQuery.data) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor guest sentiment trends, insights, and operational issues.
          </p>
        </div>
        <div className="flex flex-col gap-2 md:flex-row">
          <Input
            value={hotel}
            onChange={(event) => setHotel(event.target.value)}
            placeholder="Filter by hotel/property"
            className="md:w-56"
          />
          <button
            type="button"
            className={`rounded-lg px-3 py-2 text-sm ${trendPeriod === "weekly" ? "bg-primary text-primary-foreground" : "bg-muted"}`}
            onClick={() => setTrendPeriod("weekly")}
          >
            Weekly
          </button>
          <button
            type="button"
            className={`rounded-lg px-3 py-2 text-sm ${trendPeriod === "monthly" ? "bg-primary text-primary-foreground" : "bg-muted"}`}
            onClick={() => setTrendPeriod("monthly")}
          >
            Monthly
          </button>
          <Button variant="outline" onClick={() => downloadAnalyticsCsv(hotel || undefined)}>
            Export CSV
          </Button>
        </div>
      </div>

      <StatCards stats={statsQuery.data} />

      <div className="grid gap-6 xl:grid-cols-2">
        <TrendsChart data={trendsQuery.data.points} />
        <AspectChart data={statsQuery.data.aspect_breakdown} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
        <InsightsPanel insights={insightsQuery.data} />
        <CriticalIssues issues={statsQuery.data.critical_issues} />
      </div>

      <KeywordPanel keywords={keywordsQuery.data} />
    </div>
  )
}
