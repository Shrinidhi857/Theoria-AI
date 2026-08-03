import React, { useState, useRef, useEffect } from "react"
import { engineService } from "@/services/engineService"
import type { VideoResponse } from "@/services/engineService"
import { PromptInput } from "@/components/PromptInput"
import { VideoPlayer } from "@/components/VideoPlayer"
import { PIPELINE_STEPS } from "@/utils/constants"
import {
  CheckCircle2, Loader2, AlertCircle,
  Brain, Lightbulb, PenLine, Clapperboard, Mic,
  RotateCcw, Sparkles,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

type Phase = "idle" | "loading" | "done" | "error"

const STEP_ICONS = [Brain, Lightbulb, PenLine, Clapperboard, Mic]

const ROTATING_QUESTIONS = [
  "Stuck on a tricky LeetCode problem?",
  "Want to visualize algorithm flow step-by-step?",
  "Struggling to imagine data structures in motion?",
  "Need visual intuition for mathematical proofs?",
  "Curious how graph traversal & recursion work?",
]

function DynamicQuestionHeader() {
  const [index, setIndex] = useState(0)
  const [fade, setFade] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false)
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % ROTATING_QUESTIONS.length)
        setFade(true)
      }, 250)
    }, 3500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="text-center space-y-3">
      <div className="h-16 flex items-center justify-center">
        <h1
          className={`text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight transition-all duration-300 transform bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent ${
            fade ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"
          }`}
        >
          {ROTATING_QUESTIONS[index]}
        </h1>
      </div>
    </div>
  )
}

// ─── Animated "building" visual for left panel ─────────────────────────────

const CODE_LINES = [
  { indent: 0, text: "class AnimatedScene(Scene):", color: "text-violet-400" },
  { indent: 1, text: "def construct(self):", color: "text-blue-400" },
  { indent: 2, text: 'arr = [5, 2, 8, 1, 9, 3]', color: "text-emerald-400" },
  { indent: 2, text: "bars = VGroup(*self.make_bars(arr))", color: "text-emerald-400" },
  { indent: 2, text: "self.play(Create(bars))", color: "text-amber-400" },
  { indent: 2, text: "self.animate_sort(bars)", color: "text-amber-400" },
  { indent: 2, text: "self.wait(1.5)", color: "text-emerald-400" },
  { indent: 1, text: "def make_bars(self, arr):", color: "text-blue-400" },
  { indent: 2, text: "return [Rectangle(...) for v in arr]", color: "text-emerald-400" },
]

function CreationCard() {
  return (
    <div className="h-full min-h-[520px] rounded-2xl border border-primary/25 bg-[#0d0d14] overflow-hidden flex flex-col shadow-2xl shadow-primary/10">
      {/* macOS-style titlebar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/8 bg-white/3">
        <div className="flex gap-1.5">
          <span className="h-3 w-3 rounded-full bg-red-500/80" />
          <span className="h-3 w-3 rounded-full bg-yellow-500/80" />
          <span className="h-3 w-3 rounded-full bg-green-500/80" />
        </div>
        <span className="text-[11px] text-white/30 font-mono ml-2 flex-1">manim_scene.py</span>
        <Loader2 className="h-3.5 w-3.5 text-primary/70 animate-spin" />
      </div>

      {/* Code editor body */}
      <div className="flex-1 p-5 font-mono text-[12px] leading-6 space-y-0.5 overflow-hidden">
        {CODE_LINES.map((line, i) => (
          <div
            key={i}
            className={`flex opacity-0 ${line.color}`}
            style={{ animation: `fadeInLine 0.3s ease forwards`, animationDelay: `${i * 0.28}s` }}
          >
            <span className="w-6 shrink-0 text-white/15 select-none text-right mr-4">{i + 1}</span>
            <span style={{ paddingLeft: `${line.indent * 16}px` }}>{line.text}</span>
          </div>
        ))}
        {/* blinking cursor line */}
        <div
          className="flex items-center opacity-0"
          style={{ animation: `fadeInLine 0.3s ease forwards`, animationDelay: `${CODE_LINES.length * 0.28}s` }}
        >
          <span className="w-6 shrink-0 text-white/15 select-none text-right mr-4">{CODE_LINES.length + 1}</span>
          <span className="inline-block w-[2px] h-[14px] bg-primary animate-pulse rounded-full" />
        </div>
      </div>

      {/* Progress bar footer */}
      <div className="px-5 pb-5 pt-2 space-y-2">
        <div className="h-1 rounded-full bg-white/8 overflow-hidden">
          <div className="h-full rounded-full bg-gradient-to-r from-primary via-violet-500 to-primary creation-progress" />
        </div>
        <p className="text-[10px] text-white/30 text-center font-mono tracking-wide">
          rendering animation · please wait
        </p>
      </div>
    </div>
  )
}

// ─── Pipeline Steps Panel ──────────────────────────────────────────────────

function StepsPanel({ currentStep }: { currentStep: number }) {
  return (
    <Card className="border-border/50 bg-card/70 backdrop-blur-sm">
      <CardContent className="p-4 space-y-1.5">
        <p className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-widest mb-3 px-1">
          Pipeline Progress
        </p>
        {PIPELINE_STEPS.map((step, i) => {
          const Icon = STEP_ICONS[i]
          const stepNum = i + 1
          const done = currentStep > stepNum
          const active = currentStep === stepNum
          return (
            <div
              key={step.id}
              className={`flex items-start gap-3 px-3 py-2.5 rounded-xl transition-all duration-500 ${
                done
                  ? "bg-primary/8 text-primary"
                  : active
                  ? "bg-primary/15 ring-1 ring-primary/30 text-foreground"
                  : "text-muted-foreground/40"
              }`}
            >
              {/* Icon / spinner / check */}
              <div className="mt-0.5 shrink-0">
                {done ? (
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 text-primary animate-spin" />
                ) : (
                  <Icon className="h-4 w-4 opacity-30" />
                )}
              </div>
              {/* Text */}
              <div className="min-w-0 flex-1">
                <p className={`text-sm font-medium leading-tight ${active ? "text-foreground" : ""}`}>
                  {step.label}
                </p>
                {(active || done) && (
                  <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">{step.desc}</p>
                )}
              </div>
              {/* Badge */}
              {done && (
                <Badge variant="secondary" className="shrink-0 text-[9px] px-1.5 h-4 mt-0.5">
                  ✓
                </Badge>
              )}
              {active && (
                <Badge className="shrink-0 text-[9px] px-1.5 h-4 mt-0.5 animate-pulse">
                  Running
                </Badge>
              )}
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export const GeneratorPage: React.FC = () => {
  const [phase, setPhase] = useState<Phase>("idle")
  const [currentStep, setCurrentStep] = useState(0)
  const [result, setResult] = useState<VideoResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const stepIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startProgressSimulation = () => {
    let step = 1
    setCurrentStep(step)
    stepIntervalRef.current = setInterval(() => {
      step++
      if (step <= PIPELINE_STEPS.length) {
        setCurrentStep(step)
      }
    }, 9000)
  }

  const stopProgressSimulation = () => {
    if (stepIntervalRef.current) {
      clearInterval(stepIntervalRef.current)
      stepIntervalRef.current = null
    }
  }

  const handleGenerate = async (topic: string) => {
    setPhase("loading")
    setResult(null)
    setError(null)
    setCurrentStep(0)
    startProgressSimulation()

    try {
      const response = await engineService.generateVideo(topic)
      stopProgressSimulation()
      setCurrentStep(PIPELINE_STEPS.length + 1) // mark all done
      await new Promise((res) => setTimeout(res, 700))
      setResult(response)
      setPhase("done")
    } catch (err: unknown) {
      stopProgressSimulation()
      setError(err instanceof Error ? err.message : "Video generation failed.")
      setPhase("error")
    }
  }

  const handleReset = () => {
    setPhase("idle")
    setResult(null)
    setError(null)
    setCurrentStep(0)
  }

  // ── IDLE ──────────────────────────────────────────────────────────────────
  if (phase === "idle") {
    return (
      <div className="min-h-[calc(100vh-7rem)] flex flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-2xl space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <DynamicQuestionHeader />
          <PromptInput onGenerate={handleGenerate} isLoading={false} />
        </div>
      </div>
    )
  }

  // ── LOADING / DONE / ERROR ─────────────────────────────────────────────────
  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 md:px-6 py-6">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-5 items-start">

        {/* ── LEFT: animated card → video player ── */}
        <div className="animate-in fade-in slide-in-from-left-6 duration-500">
          {phase === "loading" && <CreationCard />}

          {phase === "done" && result && (
            <div className="animate-in fade-in zoom-in-95 duration-500">
              <VideoPlayer
                videoPath={result.video}
                topic={result.topic}
                extractedParameters={result.extracted_parameters}
                approach={result.approach}
              />
            </div>
          )}

          {phase === "error" && (
            <div className="min-h-[400px] rounded-2xl border border-destructive/30 bg-destructive/5 flex flex-col items-center justify-center gap-4 p-10 text-center animate-in fade-in duration-300">
              <AlertCircle className="h-12 w-12 text-destructive/70" />
              <div>
                <p className="font-semibold text-lg text-destructive mb-1">Generation Failed</p>
                <p className="text-sm text-muted-foreground max-w-sm">{error}</p>
              </div>
              <Button variant="outline" onClick={handleReset} className="gap-2 mt-2">
                <RotateCcw className="h-4 w-4" /> Try Again
              </Button>
            </div>
          )}
        </div>

        {/* ── RIGHT: steps + prompt input ── */}
        <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-right-6 duration-500">
          {/* Pipeline steps */}
          <StepsPanel currentStep={currentStep} />

          {/* Prompt input for next gen */}
          <div className="space-y-2">
            <p className="text-[11px] text-muted-foreground/60 uppercase tracking-widest px-1 font-semibold">
              {phase === "done" ? "Generate another" : "Queued topic"}
            </p>
            <PromptInput onGenerate={handleGenerate} isLoading={phase === "loading"} compact />
          </div>

          {/* Reset button when done */}
          {(phase === "done" || phase === "error") && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="gap-2 text-muted-foreground hover:text-foreground"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Back to studio
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
