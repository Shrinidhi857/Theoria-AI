import React from "react"
import { useNavigate } from "react-router-dom"
import {
  Sparkles, Brain, Play, ChevronRight,
  Cpu, Mic, Download, ArrowRight,
  BookOpen, Code2, Network, FlaskConical
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useAuth } from "@/context/AuthContext"

import geminiSvg from "@/assets/gemini.svg"
import neo4jSvg from "@/assets/neo4j.svg"
import postgresqlSvg from "@/assets/postgresql.svg"
import reactSvg from "@/assets/react.svg"
import tailwindSvg from "@/assets/tailwind.svg"
import typescriptSvg from "@/assets/typescipt.svg"
import manimSvg from "@/assets/Manim_icon.svg"
import ffmpegSvg from "@/assets/ffmpeg.svg"

const MARQUEE_ITEMS = [
  { src: geminiSvg, alt: "Gemini" },
  { src: neo4jSvg, alt: "Neo4j" },
  { src: postgresqlSvg, alt: "PostgreSQL" },
  { src: ffmpegSvg, alt: "Ffmpeg" },
  { src: reactSvg, alt: "React" },
  { src: tailwindSvg, alt: "Tailwind" },
  { src: typescriptSvg, alt: "TypeScript" },
  { src: manimSvg, alt: "Manim" },
  
]

const FEATURES = [
  {
    icon: Brain,
    title: "AI Lesson Planning",
    desc: "Gemini analyzes your topic, extracts the algorithm, and designs a step-by-step animated lesson plan.",
    color: "text-violet-500",
    bg: "bg-violet-500/10",
  },
  {
    icon: Cpu,
    title: "Manim Animations",
    desc: "Professional math animations using the same engine that powers 3Blue1Brown videos — auto-generated from your prompt.",
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    icon: Mic,
    title: "Voice Narration",
    desc: "TTS narration is synthesized and precisely synchronized with the animations via FFmpeg merge.",
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Download,
    title: "Download MP4",
    desc: "Get a production-ready MP4 teaching video you can share, embed, or study offline anytime.",
    color: "text-orange-500",
    bg: "bg-orange-500/10",
  },
]

const USE_CASES = [
  { icon: Code2, label: "Sorting Algorithms", example: "Explain Quicksort with array [5,2,8,1]" },
  { icon: Network, label: "Graph Traversal", example: "Show DFS on a 6-node graph" },
  { icon: BookOpen, label: "Data Structures", example: "Visualize a Red-Black Tree insertion" },
  { icon: FlaskConical, label: "Math Concepts", example: "Animate the Fourier Transform" },
]

const STEPS = [
  { num: "01", title: "Type a Prompt", desc: "Describe any algorithm, concept, or topic in plain English" },
  { num: "02", title: "AI Plans & Codes", desc: "Gemini designs the scene, generates Manim code & narration" },
  { num: "03", title: "Rendered & Merged", desc: "Manim renders the animation, FFmpeg adds voice narration" },
  { num: "04", title: "Video Ready", desc: "Watch in-browser and download your teaching MP4 instantly" },
]

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-24 md:pt-24 md:pb-32">
        {/* Animated background blobs */}
        <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-1/4 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/8 blur-[100px]" />
          <div className="absolute bottom-0 right-1/4 h-[400px] w-[400px] translate-x-1/2 translate-y-1/2 rounded-full bg-violet-500/8 blur-[100px]" />
        </div>

        <div className="relative max-w-6xl mx-auto px-4 text-center">
          <div className="relative z-10">
            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.08] mb-6">
              <span className="bg-gradient-to-br from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
                Turn Any Topic Into
              </span>
              <br />
              <span className="bg-gradient-to-r from-primary via-violet-500 to-primary bg-clip-text text-transparent">
                an Animated Video
              </span>
            </h1>

            {/* Subhead */}
            <p className="text-muted-foreground text-xl md:text-2xl max-w-2xl mx-auto leading-relaxed mb-10">
              Type any algorithm, data structure, or math concept.
              Theoria AI plans, animates, narrates, and exports a
              <strong className="text-foreground"> professional teaching video</strong> in seconds.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Button
                size="lg"
                onClick={() => navigate("/new")}
                className="h-14 px-8 text-base font-semibold gap-2 shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all"
              >
                <Play className="h-5 w-5" />
                Create a Video Now
                <ChevronRight className="h-4 w-4" />
              </Button>
              {!isAuthenticated && (
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => navigate("/new")}
                  className="h-14 px-8 text-base font-semibold gap-2"
                >
                  <Sparkles className="h-4 w-4" />
                  Try for Free — No Sign Up
                </Button>
              )}
            </div>

            {/* Social proof chips */}
            <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-muted-foreground">
              {["Gemini Flash AI", "Manim Engine", "gTTS Narration", "FFmpeg Merge", "MP4 Download"].map((tag) => (
                <Badge key={tag} variant="secondary" className="px-3 py-1 text-xs font-medium">
                  ✦ {tag}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 border-t border-border/50">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-3">How It Works</h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              A fully automated pipeline from prompt to polished teaching video
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {STEPS.map(({ num, title, desc }, i) => (
              <div key={num} className="relative flex flex-col items-center text-center gap-3 group">
                {i < STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-6 left-[calc(50%+2rem)] w-[calc(100%-2rem)] h-px bg-gradient-to-r from-border to-transparent" />
                )}
                <div className="h-12 w-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-mono font-bold text-sm group-hover:bg-primary/20 transition-colors">
                  {num}
                </div>
                <h3 className="font-semibold text-sm">{title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-muted/30 border-y border-border/50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-3">Everything You Need</h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              A complete pipeline — from a single text prompt to a downloadable MP4
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {FEATURES.map(({ icon: Icon, title, desc, color, bg }) => (
              <Card key={title} className="group hover:border-primary/40 hover:shadow-lg transition-all duration-200 bg-card/80">
                <CardContent className="p-6">
                  <div className={`${bg} ${color} p-3 rounded-xl w-fit mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-bold text-base mb-2">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-3">What Can You Visualize?</h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              From competitive programming to university lectures
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {USE_CASES.map(({ icon: Icon, label, example }) => (
              <button
                key={label}
                onClick={() => navigate("/new")}
                className="flex items-center gap-4 p-5 rounded-xl border border-border bg-card/60 hover:border-primary/40 hover:bg-primary/5 hover:shadow-md transition-all duration-200 text-left group"
              >
                <div className="p-2.5 rounded-lg bg-primary/10 text-primary shrink-0 group-hover:bg-primary/20 transition-colors">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <p className="font-semibold text-sm mb-0.5">{label}</p>
                  <p className="text-xs text-muted-foreground truncate italic">"{example}"</p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 ml-auto group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-24 border-t border-border/50 bg-gradient-to-b from-transparent to-primary/5">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <img src="/Theoria.svg" alt="Theoria AI" className="h-14 w-14 mx-auto mb-6 object-contain" />
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to visualize your first concept?
          </h2>
          <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
            No configuration. No setup. Just type a topic and watch the AI build your teaching video.
          </p>
          <Button
            size="lg"
            onClick={() => navigate("/new")}
            className="h-14 px-10 text-base font-semibold gap-2 shadow-xl shadow-primary/20"
          >
            <Play className="h-5 w-5" />
            Start Creating for Free
          </Button>
        </div>
      </section>

      {/* ── Logo-only Marquee at End of Webpage ─────────────────────────────── */}
      <section
        className="w-full py-6 border-t border-b border-border/40 relative shrink-0 select-none z-10 overflow-hidden bg-background/50 backdrop-blur-sm"
        id="global-marquee-bar"
      >
        {/* Edge fades */}
        <div className="absolute left-0 top-0 bottom-0 w-24 md:w-32 z-20 pointer-events-none bg-gradient-to-r from-background to-transparent" />
        <div className="absolute right-0 top-0 bottom-0 w-24 md:w-32 z-20 pointer-events-none bg-gradient-to-l from-background to-transparent" />

        {/* Scrolling track */}
        <div
          className="animate-marquee flex items-center"
          style={{
            gap: "7rem",
          }}
        >
          {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map(
            (item, i) => (
              <img
                key={i}
                src={item.src}
                alt={item.alt}
                draggable={false}
                className="w-12 h-12 md:w-16 md:h-16 object-contain shrink-0 opacity-70 hover:opacity-100 transition-opacity filter drop-shadow-sm"
              />
            ),
          )}
        </div>
      </section>
    </div>
  )
}
