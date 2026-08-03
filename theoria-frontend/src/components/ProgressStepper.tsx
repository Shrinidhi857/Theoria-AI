import React from "react"
import { CheckCircle2, Loader2, Sparkles, Cpu, Film, Volume2, Code } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PIPELINE_STEPS } from "@/utils/constants"

interface ProgressStepperProps {
  currentStep: number // 1 to 5
  statusMessage?: string
}

export const ProgressStepper: React.FC<ProgressStepperProps> = ({
  currentStep,
  statusMessage
}) => {
  const stepIcons = [Cpu, Sparkles, Code, Film, Volume2]
  const progressPercent = Math.min(100, Math.max(10, currentStep * 20))

  return (
    <Card className="w-full border-primary/20 bg-card/60 backdrop-blur-md shadow-lg overflow-hidden my-6">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary animate-pulse">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-semibold text-base flex items-center gap-2">
                AI Engine Generation Pipeline
                <Badge variant="warning" className="animate-pulse">
                  Step {currentStep} of {PIPELINE_STEPS.length}
                </Badge>
              </h3>
              <p className="text-xs text-muted-foreground">
                {statusMessage || PIPELINE_STEPS[currentStep - 1]?.desc || "Processing video..."}
              </p>
            </div>
          </div>
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </div>

        {/* Progress Bar */}
        <Progress value={progressPercent} className="h-2 mb-6" />

        {/* Steps Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          {PIPELINE_STEPS.map((step, idx) => {
            const stepNum = idx + 1
            const isCompleted = stepNum < currentStep
            const isCurrent = stepNum === currentStep
            const StepIcon = stepIcons[idx] || Cpu

            return (
              <div
                key={step.id}
                className={`p-3 rounded-lg border text-xs transition-all duration-300 flex flex-col justify-between ${
                  isCompleted
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
                    : isCurrent
                    ? "bg-primary/10 border-primary text-primary shadow-md ring-2 ring-primary/20 scale-102"
                    : "bg-muted/30 border-border text-muted-foreground opacity-60"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-[10px] uppercase tracking-wider">Step 0{stepNum}</span>
                  {isCompleted ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  ) : isCurrent ? (
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  ) : (
                    <StepIcon className="h-4 w-4 text-muted-foreground" />
                  )}
                </div>
                <div className="font-medium text-xs line-clamp-1">{step.label}</div>
                <div className="text-[10px] text-muted-foreground mt-1 line-clamp-1">{step.desc}</div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
