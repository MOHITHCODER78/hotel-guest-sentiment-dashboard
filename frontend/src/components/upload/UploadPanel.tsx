import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { motion } from "framer-motion"
import { FileUp, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { fetchJobStatus, uploadCsv } from "@/services/hotel-api"
import { ApiRequestError } from "@/lib/api"

async function waitForJob(taskId: string) {
  while (true) {
    const status = await fetchJobStatus(taskId)
    if (status.status === "COMPLETED" || status.status === "FAILED") {
      return status
    }
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }
}

export function UploadPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [progress, setProgress] = useState<number | null>(null)

  const mutation = useMutation({
    mutationFn: async (selectedFile: File) => {
      const job = await uploadCsv(selectedFile)
      setProgress(job.progress)

      const finalStatus = await waitForJob(job.task_id)
      setProgress(finalStatus.progress)
      return finalStatus
    },
  })

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileUp className="h-5 w-5 text-primary" />
            CSV Review Upload
          </CardTitle>
          <CardDescription>
            Upload Kaggle-compatible CSV files with hotel review data for bulk analysis.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            type="file"
            accept=".csv"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null)
              setProgress(null)
              mutation.reset()
            }}
            className="block w-full text-sm text-muted-foreground file:mr-4 file:rounded-lg file:border-0 file:bg-primary file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-foreground hover:file:opacity-90"
          />

          <Button
            onClick={() => file && mutation.mutate(file)}
            disabled={!file || mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              "Start Analysis"
            )}
          </Button>

          {progress !== null && (
            <div className="space-y-2">
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{ width: `${Math.round(progress * 100)}%` }}
                />
              </div>
              <p className="text-sm text-muted-foreground">
                Progress: {Math.round(progress * 100)}%
              </p>
            </div>
          )}

          {mutation.isError && (
            <p className="text-sm text-destructive">
              {mutation.error instanceof ApiRequestError
                ? mutation.error.message
                : "Upload failed."}
            </p>
          )}

          {mutation.data?.status === "COMPLETED" && (
            <p className="text-sm text-success">
              Successfully analyzed {mutation.data.processed_reviews} reviews.
            </p>
          )}

          {mutation.data?.status === "FAILED" && (
            <p className="text-sm text-destructive">
              {mutation.data.error_message ?? "Bulk analysis failed."}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
