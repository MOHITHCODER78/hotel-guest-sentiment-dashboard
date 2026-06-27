import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { ReviewFeedItem } from "@/types/api"

export function ReviewFeed({ reviews }: { reviews: ReviewFeedItem[] }) {
  if (reviews.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-muted-foreground">
          No reviews yet. Upload a CSV to populate your review feed.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {reviews.map((review, index) => (
        <motion.div
          key={`${review.text}-${index}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>{review.hotel ?? "Hotel Review"}</CardTitle>
              <CardDescription className="leading-relaxed">{review.text}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {review.analysis.map((item) => (
                <Badge
                  key={`${item.aspect}-${item.sentiment}`}
                  className={
                    item.sentiment === "POSITIVE"
                      ? "border-success/30 bg-success/10 text-success"
                      : "border-destructive/30 bg-destructive/10 text-destructive"
                  }
                >
                  {item.aspect}: {item.sentiment}
                </Badge>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
