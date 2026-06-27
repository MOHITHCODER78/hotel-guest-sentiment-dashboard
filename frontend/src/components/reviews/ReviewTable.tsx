import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { PaginatedReviewsResponse } from "@/types/api"

interface ReviewTableProps {
  data: PaginatedReviewsResponse
  search: string
  aspect: string
  sentiment: string
  hotel: string
  sortBy: "created_at" | "hotel" | "sentiment_score"
  sortOrder: "asc" | "desc"
  onSearchChange: (value: string) => void
  onAspectChange: (value: string) => void
  onSentimentChange: (value: string) => void
  onHotelChange: (value: string) => void
  onSortByChange: (value: "created_at" | "hotel" | "sentiment_score") => void
  onSortOrderChange: (value: "asc" | "desc") => void
  onPageChange: (page: number) => void
  onExport: () => void
}

export function ReviewTable({
  data,
  search,
  aspect,
  sentiment,
  hotel,
  sortBy,
  sortOrder,
  onSearchChange,
  onAspectChange,
  onSentimentChange,
  onHotelChange,
  onSortByChange,
  onSortOrderChange,
  onPageChange,
  onExport,
}: ReviewTableProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Search & Filters</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
          <div className="space-y-2">
            <Label htmlFor="search">Search reviews</Label>
            <Input
              id="search"
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Search text..."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="aspect">Aspect</Label>
            <Input
              id="aspect"
              value={aspect}
              onChange={(event) => onAspectChange(event.target.value)}
              placeholder="Staff, WiFi..."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sentiment">Sentiment</Label>
            <Input
              id="sentiment"
              value={sentiment}
              onChange={(event) => onSentimentChange(event.target.value)}
              placeholder="POSITIVE or NEGATIVE"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="hotel">Hotel</Label>
            <Input
              id="hotel"
              value={hotel}
              onChange={(event) => onHotelChange(event.target.value)}
              placeholder="Property name"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sortBy">Sort by</Label>
            <select
              id="sortBy"
              value={sortBy}
              onChange={(event) => onSortByChange(event.target.value as "created_at" | "hotel" | "sentiment_score")}
              className="flex h-10 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none ring-primary focus:ring-2"
            >
              <option value="created_at">Created At</option>
              <option value="hotel">Hotel</option>
              <option value="sentiment_score">Sentiment Score</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="sortOrder">Order</Label>
            <select
              id="sortOrder"
              value={sortOrder}
              onChange={(event) => onSortOrderChange(event.target.value as "asc" | "desc")}
              className="flex h-10 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none ring-primary focus:ring-2"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
          <div className="flex items-end">
            <Button variant="outline" className="w-full" onClick={onExport}>
              Export CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {data.items.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              No reviews match your filters.
            </CardContent>
          </Card>
        ) : (
          data.items.map((review) => (
            <Card key={review.id}>
              <CardHeader>
                <CardTitle className="text-base">
                  {review.hotel ?? "Hotel Review"} · #{review.id}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm leading-relaxed">{review.text}</p>
                {review.avg_score !== undefined && review.avg_score !== null && (
                  <p className="text-xs text-muted-foreground">
                    Average sentiment score: {review.avg_score.toFixed(2)}
                  </p>
                )}
                <div className="flex flex-wrap gap-2">
                  {review.analysis.map((item) => (
                    <Badge
                      key={`${review.id}-${item.aspect}-${item.sentiment}`}
                      className={
                        item.sentiment === "POSITIVE"
                          ? "border-success/30 bg-success/10 text-success"
                          : "border-destructive/30 bg-destructive/10 text-destructive"
                      }
                    >
                      {item.aspect}: {item.sentiment}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page {data.meta.page} of {data.meta.total_pages} · {data.meta.total_items} reviews
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={data.meta.page <= 1}
            onClick={() => onPageChange(data.meta.page - 1)}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={data.meta.page >= data.meta.total_pages}
            onClick={() => onPageChange(data.meta.page + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
