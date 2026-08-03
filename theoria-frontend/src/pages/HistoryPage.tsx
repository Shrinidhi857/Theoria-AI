import React, { useState, useEffect } from "react"
import { History, Play, Download, AlertCircle, Loader2, RefreshCw, Video, Lock, Code2, Sparkles, Database, Server } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { VideoPlayer } from "@/components/VideoPlayer"
import { engineService } from "@/services/engineService"
import type { VideoHistoryItem, UserUsageResponse } from "@/services/engineService"
import { useAuth } from "@/context/AuthContext"
import { formatDate, getFullVideoUrl } from "@/utils/formatters"

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
  const [usage, setUsage] = useState<UserUsageResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<VideoHistoryItem | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [showDsl, setShowDsl] = useState(false)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [videoList, usageStats] = await Promise.all([
        engineService.getUserVideos(),
        engineService.getUserUsage().catch(() => null)
      ])
      setVideos(videoList)
      if (usageStats) setUsage(usageStats)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not load video history.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      loadData()
    }
  }, [isAuthenticated])

  const handleOpenPreview = (video: VideoHistoryItem) => {
    setSelected(video)
    setShowDsl(false)
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
          Your video generation history is saved per account in PostgreSQL/Aurora RDS and S3. Sign in to access and re-watch all your AI-generated teaching videos.
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
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
        <Button variant="outline" onClick={loadData} disabled={loading} className="gap-2 self-start sm:self-auto">
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Usage Quota Banner */}
      {usage && (
        <Card className="mb-8 bg-gradient-to-r from-primary/10 via-card to-background border-primary/20 shadow-sm">
          <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20 text-primary">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold">Account Quota Usage</p>
                <p className="text-xs text-muted-foreground">
                  You have generated <span className="font-bold text-foreground">{usage.usage_count}</span> of <span className="font-bold text-foreground">{usage.usage_limit}</span> allowed videos.
                </p>
              </div>
            </div>
            <div className="w-full sm:w-48 bg-muted rounded-full h-2.5 overflow-hidden border border-border/50">
              <div
                className={`h-full transition-all duration-500 ${
                  usage.is_limit_reached ? "bg-destructive" : "bg-primary"
                }`}
                style={{ width: `${Math.min(100, (usage.usage_count / usage.usage_limit) * 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Loader2 className="h-10 w-10 text-primary animate-spin" />
          <p className="text-muted-foreground">Loading your video history...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card className="border-destructive/30 bg-destructive/5 mb-6">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-destructive shrink-0" />
            <div>
              <p className="font-semibold text-destructive text-sm">Error Loading History</p>
              <p className="text-xs text-muted-foreground">{error}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={loadData} className="ml-auto">
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
          <h3 className="text-xl font-semibold">No videos generated yet</h3>
          <p className="text-muted-foreground max-w-md">
            Head over to the Studio tab, type any algorithm or concept, and generate your first teaching video!
          </p>
        </div>
      )}

      {/* Video Gallery Grid */}
      {!loading && videos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {videos.map((video) => {
            const videoSource = video.video_url || video.video_path
            return (
              <Card
                key={video.id}
                className="group hover:border-primary/40 hover:shadow-md transition-all duration-200 bg-card/80 overflow-hidden"
              >
                {/* Thumbnail */}
                <div className="aspect-video bg-gradient-to-br from-primary/10 via-muted to-muted/50 relative flex items-center justify-center overflow-hidden">
                  <div className="p-4 rounded-full bg-background/70 backdrop-blur-sm border border-border shadow-md group-hover:scale-105 transition-transform cursor-pointer" onClick={() => handleOpenPreview(video)}>
                    <Play className="h-7 w-7 text-primary fill-primary/20" />
                  </div>
                  <div className="absolute top-3 right-3 flex items-center gap-1.5">
                    {video.video_url && video.video_url.includes("s3") && (
                      <Badge variant="secondary" className="text-[10px] gap-1 bg-background/80 backdrop-blur-sm">
                        <Database className="h-3 w-3 text-blue-500" /> S3
                      </Badge>
                    )}
                    <StatusBadge status={video.status} />
                  </div>
                </div>

                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold line-clamp-2 leading-snug">
                    {video.topic}
                  </CardTitle>
                  <CardDescription className="text-xs flex items-center justify-between">
                    <span>{formatDate(video.created_at)}</span>
                  </CardDescription>
                </CardHeader>

                <CardContent className="pt-0 flex items-center gap-2">
                  {video.status === "completed" && videoSource ? (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleOpenPreview(video)}
                        className="flex-1 gap-1.5 text-xs"
                      >
                        <Play className="h-3.5 w-3.5" /> Preview
                      </Button>
                      <a
                        href={getFullVideoUrl(videoSource)}
                        target="_blank"
                        rel="noreferrer"
                        download
                        className="flex-1"
                      >
                        <Button
                          size="sm"
                          className="w-full gap-1.5 text-xs"
                        >
                          <Download className="h-3.5 w-3.5" /> Download
                        </Button>
                      </a>
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
            )
          })}
        </div>
      )}

      {/* Preview & DSL Inspector Dialog */}
      {selected && (
        <Dialog
          open={dialogOpen}
          onOpenChange={(open) => {
            setDialogOpen(open)
            if (!open) setSelected(null)
          }}
        >
          <DialogHeader className="space-y-2">
            <div className="flex items-center justify-between pr-8">
              <DialogTitle className="text-lg font-bold line-clamp-2">{selected.topic}</DialogTitle>
            </div>
            <DialogDescription className="text-xs flex items-center gap-2">
              <span>{formatDate(selected.created_at)}</span>
              {selected.video_url && (
                <Badge variant="outline" className="text-[10px] gap-1">
                  <Server className="h-3 w-3" /> Storage: S3 / Cloud
                </Badge>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="mt-3 space-y-4 max-h-[75vh] overflow-y-auto pr-1">
            {/* Video Player */}
            {(selected.video_url || selected.video_path) && (
              <VideoPlayer
                videoPath={selected.video_url || selected.video_path!}
                topic={selected.topic}
                extractedParameters={selected.extracted_parameters}
                approach={selected.approach}
              />
            )}

            {/* Toggle Intermediate DSL Code */}
            {selected.dsl_code && (
              <div className="border border-border/60 rounded-xl p-3 bg-muted/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold flex items-center gap-1.5 text-muted-foreground">
                    <Code2 className="h-4 w-4 text-primary" /> Intermediate Animation DSL Code
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDsl(!showDsl)}
                    className="text-xs h-7 px-2"
                  >
                    {showDsl ? "Hide DSL" : "View DSL JSON"}
                  </Button>
                </div>

                {showDsl && (
                  <pre className="p-3 bg-black/80 text-emerald-400 font-mono text-[11px] rounded-lg overflow-x-auto max-h-60 border border-emerald-500/20">
                    {JSON.stringify(selected.dsl_code, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
        </Dialog>
      )}
    </div>
  )
}
