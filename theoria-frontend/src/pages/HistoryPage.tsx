import React, { useState, useEffect } from "react"
import { History, Play, Download, AlertCircle, Loader2, RefreshCw, Video, Lock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { VideoPlayer } from "@/components/VideoPlayer"
import { engineService } from "@/services/engineService"
import type { VideoHistoryItem } from "@/services/engineService"
import { useAuth } from "@/context/AuthContext"
import { formatDate } from "@/utils/formatters"

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const map: Record<string, "success" | "warning" | "destructive" | "secondary"> = {
    completed: "success",
    processing: "warning",
    failed: "destructive",
    pending: "secondary",
  }
  return <Badge variant={map[status] ?? "outline"}>{status}</Badge>
}

interface HistoryPageProps {
  onAuthClick: () => void
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onAuthClick }) => {
  const { isAuthenticated } = useAuth()
  const [videos, setVideos] = useState<VideoHistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<VideoHistoryItem | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  const loadVideos = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await engineService.getUserVideos()
      setVideos(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not load video history.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      loadVideos()
    }
  }, [isAuthenticated])

  const handleOpenPreview = (video: VideoHistoryItem) => {
    setSelected(video)
    setDialogOpen(true)
  }

  if (!isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="p-5 rounded-full bg-muted w-fit mx-auto">
          <Lock className="h-12 w-12 text-muted-foreground" />
        </div>
        <h2 className="text-2xl font-bold">Sign in to view your history</h2>
        <p className="text-muted-foreground leading-relaxed">
          Your video generation history is saved per account. Sign in to access and re-watch all your AI-generated teaching videos.
        </p>
        <Button onClick={onAuthClick} size="lg" className="gap-2">
          Sign In / Create Account
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <History className="h-7 w-7 text-primary" />
            </div>
            My Video History
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            All AI-generated teaching videos linked to your account
          </p>
        </div>
        <Button variant="outline" onClick={loadVideos} disabled={loading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Loader2 className="h-10 w-10 text-primary animate-spin" />
          <p className="text-muted-foreground">Loading your video history...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-destructive shrink-0" />
            <div>
              <p className="font-semibold text-destructive text-sm">Error Loading History</p>
              <p className="text-xs text-muted-foreground">{error}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={loadVideos} className="ml-auto">
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!loading && !error && videos.length === 0 && (
        <div className="flex flex-col items-center py-20 gap-4 text-center">
          <div className="p-5 rounded-full bg-muted">
            <Video className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold">No videos yet</h3>
          <p className="text-muted-foreground max-w-md">
            Head over to the Studio tab, type any algorithm or concept, and generate your first teaching video!
          </p>
        </div>
      )}

      {/* Video Gallery Grid */}
      {!loading && videos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {videos.map((video) => (
            <Card
              key={video.id}
              className="group hover:border-primary/40 hover:shadow-md transition-all duration-200 bg-card/80 overflow-hidden"
            >
              {/* Thumbnail */}
              <div className="aspect-video bg-gradient-to-br from-primary/10 via-muted to-muted/50 relative flex items-center justify-center overflow-hidden">
                <div className="p-4 rounded-full bg-background/70 backdrop-blur-sm border border-border shadow-md group-hover:scale-105 transition-transform">
                  <Play className="h-7 w-7 text-primary" />
                </div>
                <div className="absolute top-3 right-3">
                  <StatusBadge status={video.status} />
                </div>
              </div>

              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold line-clamp-2 leading-snug">
                  {video.topic}
                </CardTitle>
                <CardDescription className="text-xs">
                  {formatDate(video.created_at)}
                </CardDescription>
              </CardHeader>

              <CardContent className="pt-0 flex items-center gap-2">
                {video.status === "completed" && video.video_path ? (
                  <>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleOpenPreview(video)}
                      className="flex-1 gap-1.5"
                    >
                      <Play className="h-3.5 w-3.5" /> Preview
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleOpenPreview(video)}
                      className="flex-1 gap-1.5"
                    >
                      <Download className="h-3.5 w-3.5" /> Download
                    </Button>
                  </>
                ) : video.status === "failed" ? (
                  <p className="text-xs text-destructive font-medium">Generation failed</p>
                ) : (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" /> Processing...
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Dialog */}
      {selected && (
        <Dialog
          open={dialogOpen}
          onOpenChange={(open) => {
            setDialogOpen(open)
            if (!open) setSelected(null)
          }}
        >
          <DialogHeader>
            <DialogTitle className="pr-8 text-lg font-bold line-clamp-2">{selected.topic}</DialogTitle>
            <DialogDescription>{formatDate(selected.created_at)}</DialogDescription>
          </DialogHeader>
          {selected.video_path && (
            <div className="mt-2 max-h-[70vh] overflow-y-auto">
              <VideoPlayer
                videoPath={selected.video_path}
                topic={selected.topic}
                extractedParameters={selected.extracted_parameters}
                approach={selected.approach}
              />
            </div>
          )}
        </Dialog>
      )}
    </div>
  )
}
