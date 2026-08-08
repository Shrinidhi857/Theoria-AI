import  { useState } from "react"
import { Routes, Route, useNavigate, useLocation } from "react-router-dom"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider, useAuth } from "@/context/AuthContext"
import { Navbar } from "@/components/Navbar"
import { AuthModal } from "@/components/AuthModal"
import { ThemeToggle } from "@/components/ThemeToggle"
import { LandingPage } from "@/pages/LandingPage"
import { GeneratorPage } from "@/pages/GeneratorPage"
import { HistoryPage } from "@/pages/HistoryPage"
import { ProfilePage } from "@/pages/ProfilePage"
import { KnowledgeGraphPage } from "@/pages/KnowledgeGraphPage"


/** Auth-aware button for the landing page slim header */
function LandingAuthButton({ onAuthClick }: { onAuthClick: () => void }) {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  if (isAuthenticated) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate("/profile")}
          className="h-8 w-8 rounded-full bg-primary/20 border-2 border-primary/40 flex items-center justify-center text-sm font-bold text-primary hover:border-primary transition-all"
          title="View profile"
        >
          {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
        </button>
        <button
          onClick={logout}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded-md hover:bg-muted"
        >
          Sign out
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={onAuthClick}
      className="text-sm font-medium px-4 py-1.5 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
    >
      Sign In
    </button>
  )
}

function AppRoutes() {

  const [authOpen, setAuthOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const isLanding = location.pathname === "/"

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Ambient glow background */}
      <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[600px] w-[600px] rounded-full bg-primary/5 blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-[400px] w-[400px] rounded-full bg-violet-500/3 blur-[100px]" />
      </div>

      {/* Inner-page Navbar (not shown on landing) */}
      {!isLanding && (
        <Navbar onAuthClick={() => setAuthOpen(true)} />
      )}

      {/* Landing-only slim header */}
      {isLanding && (
        <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/70 backdrop-blur-md">
          <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-4 md:px-6">
            <button onClick={() => navigate("/")} className="flex items-center gap-2.5">
              <img src="/Theoria.svg" alt="Theoria AI" className="h-9 w-9 object-contain" />
              <span className="font-bold text-lg tracking-tight">Theoria AI</span>
            </button>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <button
                onClick={() => navigate("/history")}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-md hover:bg-muted"
              >
                History
              </button>
              <LandingAuthButton onAuthClick={() => setAuthOpen(true)} />
            </div>
          </div>
        </header>
      )}

      <main className="flex-1 relative z-10">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/new" element={<GeneratorPage />} />
          <Route path="/graph" element={<KnowledgeGraphPage />} />
          <Route path="/history" element={<HistoryPage onAuthClick={() => setAuthOpen(true)} />} />
          <Route path="/profile" element={<ProfilePage />} />
          {/* Catch-all → landing */}
          <Route path="*" element={<LandingPage />} />
        </Routes>

      </main>

      <footer className="relative z-10 border-t border-border/50 py-4 px-6 text-center text-xs text-muted-foreground">
        Theoria AI · Built with FastAPI, Manim, Gemini, and React ·{" "}
        <span className="text-primary font-medium">2026</span>
      </footer>

      <AuthModal open={authOpen} onOpenChange={setAuthOpen} />
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  )
}
