import { UploadPanel } from "@/components/upload/UploadPanel"

export function UploadPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Reviews</h1>
        <p className="text-muted-foreground">
          Import guest reviews from CSV and process them in the background.
        </p>
      </div>
      <UploadPanel />
    </div>
  )
}
