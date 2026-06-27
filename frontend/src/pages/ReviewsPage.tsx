import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { ReviewTable } from "@/components/reviews/ReviewTable"
import { Skeleton } from "@/components/ui/skeleton"
import { downloadReviewsCsv, fetchReviews } from "@/services/hotel-api"
import { ApiRequestError } from "@/lib/api"

export function ReviewsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [aspect, setAspect] = useState("")
  const [sentiment, setSentiment] = useState("")
  const [hotel, setHotel] = useState("")
  const [sortBy, setSortBy] = useState<"created_at" | "hotel" | "sentiment_score">("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [debouncedSearch, setDebouncedSearch] = useState("")

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search), 300)
    return () => window.clearTimeout(timer)
  }, [search])

  useEffect(() => {
    setPage(1)
  }, [debouncedSearch, aspect, sentiment, hotel, sortBy, sortOrder])

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["reviews", page, debouncedSearch, aspect, sentiment, hotel, sortBy, sortOrder],
    queryFn: () =>
      fetchReviews({
        page,
        page_size: 10,
        search: debouncedSearch || undefined,
        aspect: aspect || undefined,
        sentiment: sentiment || undefined,
        hotel: hotel || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review Explorer</h1>
        <p className="text-muted-foreground">
          Search, filter, and browse analyzed guest reviews with aspect tags.
        </p>
      </div>

      {isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      )}

      {isError && (
        <p className="text-destructive">
          {error instanceof ApiRequestError ? error.message : "Failed to load reviews."}
        </p>
      )}

      {data && (
        <ReviewTable
          data={data}
          search={search}
          aspect={aspect}
          sentiment={sentiment}
          hotel={hotel}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSearchChange={setSearch}
          onAspectChange={setAspect}
          onSentimentChange={setSentiment}
          onHotelChange={setHotel}
          onSortByChange={setSortBy}
          onSortOrderChange={setSortOrder}
          onPageChange={setPage}
          onExport={() =>
            downloadReviewsCsv({
              search: debouncedSearch || undefined,
              aspect: aspect || undefined,
              sentiment: sentiment || undefined,
              hotel: hotel || undefined,
            })
          }
        />
      )}
    </div>
  )
}
