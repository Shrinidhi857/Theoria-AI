import React, { useState } from "react"
import { Sparkles, Send, Lightbulb } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { SAMPLE_PROMPTS } from "@/utils/constants"

interface PromptInputProps {
  onGenerate: (topic: string) => void
  isLoading: boolean
  /** When true: hides sample prompt chips and the label (used in side panel) */
  compact?: boolean
}

export const PromptInput: React.FC<PromptInputProps> = ({ onGenerate, isLoading, compact = false }) => {
  const [topic, setTopic] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim() || isLoading) return
    onGenerate(topic.trim())
    setTopic("")
  }

  return (
    <Card className="w-full border-primary/20 bg-card/80 backdrop-blur-md shadow-xl transition-all">
      <CardContent className={compact ? "p-3" : "p-6"}>
        <form onSubmit={handleSubmit} className={compact ? "space-y-0" : "space-y-4"}>
          <div className="flex flex-col gap-2">
            <div className="relative flex items-center">
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder={compact ? "Try another topic…" : "e.g. Explain Binary Search with an array [2, 5, 8, 12, 16, 23, 38] and target 23"}
                rows={compact ? 2 : 3}
                disabled={isLoading}
                className="w-full rounded-lg border border-input bg-background p-4 pr-32 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50 resize-none shadow-inner transition-all"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
              />
              <Button
                type="submit"
                disabled={!topic.trim() || isLoading}
                size={compact ? "sm" : "default"}
                className="absolute right-3 bottom-3 gap-2 shadow-lg hover:scale-102 active:scale-98 transition-transform"
              >
                {isLoading ? (
                  <>Generating...</>
                ) : (
                  <>
                    {compact ? "Go" : ""} <Send className="h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Sample prompt chips — hidden in compact mode */}
          {!compact && (
            <div className="space-y-2 pt-2">
              <div className="flex items-center gap-1 text-xs text-muted-foreground font-medium">
                <Lightbulb className="h-3.5 w-3.5 text-amber-500" />
                Try a sample prompt:
              </div>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_PROMPTS.map((promptText, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setTopic(promptText)}
                    disabled={isLoading}
                    className="text-xs px-3 py-1.5 rounded-full border border-border bg-muted/40 hover:bg-primary/10 hover:border-primary/40 hover:text-primary transition-all text-left truncate max-w-xs"
                  >
                    {promptText}
                  </button>
                ))}
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
