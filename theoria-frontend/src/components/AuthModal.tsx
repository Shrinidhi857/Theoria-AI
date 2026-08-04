import React, { useState, useEffect } from "react"
import { LogIn, UserPlus, AlertCircle, Mail, Lock, User, KeyRound, ArrowRight } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { Dialog, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface AuthModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const AuthModal: React.FC<AuthModalProps> = ({ open, onOpenChange }) => {
  const { login, signup, googleLogin } = useAuth()

  const [activeTab, setActiveTab] = useState("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [googleTokenInput, setGoogleTokenInput] = useState("")
  const [showGoogleInput, setShowGoogleInput] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Initialize Google Identity Services SDK Sign-In Button
  useEffect(() => {
    if (!open) return

    const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    if (!googleClientId) {
      console.warn("VITE_GOOGLE_CLIENT_ID not configured in the environment.")
      return
    }

    const initGoogleSignIn = () => {
      const gAccount = (window as any).google?.accounts?.id
      if (gAccount) {
        gAccount.initialize({
          client_id: googleClientId,
          callback: async (response: any) => {
            setError(null)
            setLoading(true)
            try {
              // The credential returned from Google is the ID Token
              await googleLogin(response.credential)
              onOpenChange(false)
            } catch (err: unknown) {
              setError(err instanceof Error ? err.message : "Google Authentication failed.")
            } finally {
              setLoading(false)
            }
          },
        })

        // Render button inside matching div
        const container = document.getElementById("google-signin-btn")
        if (container) {
          gAccount.renderButton(container, {
            theme: "outline",
            size: "large",
            width: 380,
            text: "signin_with",
            shape: "rectangular",
          })
        }
      } else {
        // Retry if script has not fully initialized
        setTimeout(initGoogleSignIn, 150)
      }
    }

    initGoogleSignIn()
  }, [open, googleLogin, onOpenChange])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login({ email, password })
      onOpenChange(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to log in.")
    } finally {
      setLoading(false)
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await signup({ email, password, full_name: fullName || undefined })
      onOpenChange(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create account.")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!googleTokenInput.trim()) return
    setError(null)
    setLoading(true)
    try {
      await googleLogin(googleTokenInput.trim())
      onOpenChange(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Google Authentication failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <div className="py-2 px-1 space-y-6">
        {/* Header */}
        <DialogHeader className="mb-2">
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-2xl bg-gradient-to-br from-primary/20 via-violet-500/10 to-primary/5 border border-primary/20 shadow-md">
              <img src="/Theoria.svg" alt="Theoria AI" className="h-10 w-10 object-contain" />
            </div>
            <div>
              <DialogTitle className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
                Welcome to Theoria AI
              </DialogTitle>
            </div>
          </div>
        </DialogHeader>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-destructive/10 text-destructive text-sm flex items-center gap-3 border border-destructive/20 animate-in fade-in duration-200">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Auth Tabs */}
        <Tabs defaultValue="login" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 h-12 p-1 bg-muted/60 rounded-xl mb-6 border border-border/40">
            <TabsTrigger 
              value="login" 
              className="gap-2 h-10 text-sm font-semibold rounded-lg transition-all data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm"
            >
              <LogIn className="h-4 w-4 text-primary" /> Sign In
            </TabsTrigger>
            <TabsTrigger 
              value="signup" 
              className="gap-2 h-10 text-sm font-semibold rounded-lg transition-all data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm"
            >
              <UserPlus className="h-4 w-4 text-primary" /> Register
            </TabsTrigger>
          </TabsList>

          {/* SIGN IN FORM */}
          <TabsContent value="login" className="space-y-5 mt-0 focus-visible:outline-none">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5 text-primary" /> Email Address
                </label>
                <Input 
                  type="email" 
                  placeholder="name@example.com" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                  className="h-11 px-4 rounded-xl border-border/80 bg-background/50 focus:bg-background focus:ring-2 focus:ring-primary/40 transition-all"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Lock className="h-3.5 w-3.5 text-primary" /> Password
                </label>
                <Input 
                  type="password" 
                  placeholder="••••••••" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                  className="h-11 px-4 rounded-xl border-border/80 bg-background/50 focus:bg-background focus:ring-2 focus:ring-primary/40 transition-all"
                />
              </div>

              <Button 
                type="submit" 
                disabled={loading}
                className="w-full h-11 rounded-xl text-sm font-bold gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all mt-2"
              >
                {loading ? (
                  "Signing in..."
                ) : (
                  <>
                    Sign In with Email <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          </TabsContent>

          {/* REGISTER FORM */}
          <TabsContent value="signup" className="space-y-5 mt-0 focus-visible:outline-none">
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5 text-primary" /> Full Name
                </label>
                <Input 
                  type="text" 
                  placeholder="John Doe" 
                  value={fullName} 
                  onChange={(e) => setFullName(e.target.value)} 
                  className="h-11 px-4 rounded-xl border-border/80 bg-background/50 focus:bg-background focus:ring-2 focus:ring-primary/40 transition-all"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5 text-primary" /> Email Address
                </label>
                <Input 
                  type="email" 
                  placeholder="name@example.com" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                  className="h-11 px-4 rounded-xl border-border/80 bg-background/50 focus:bg-background focus:ring-2 focus:ring-primary/40 transition-all"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Lock className="h-3.5 w-3.5 text-primary" /> Password
                </label>
                <Input 
                  type="password" 
                  placeholder="At least 6 characters" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                  minLength={6} 
                  className="h-11 px-4 rounded-xl border-border/80 bg-background/50 focus:bg-background focus:ring-2 focus:ring-primary/40 transition-all"
                />
              </div>

              <Button 
                type="submit" 
                disabled={loading}
                className="w-full h-11 rounded-xl text-sm font-bold gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all mt-2"
              >
                {loading ? (
                  "Creating Account..."
                ) : (
                  <>
                    Create Account 
                  </>
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        {/* Divider */}
        <div className="relative pt-1 pb-1">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border/60" />
          </div>
          <div className="relative flex justify-center text-xs uppercase tracking-widest font-mono">
            <span className="bg-background px-3 text-muted-foreground/70 font-semibold">Or continue with</span>
          </div>
        </div>

        {/* Google OAuth Section */}
        <div className="space-y-3">
          {!showGoogleInput ? (
            <div className="flex flex-col items-center gap-3">
              {/* Dynamic Google Button Container */}
              <div id="google-signin-btn" className="w-full flex justify-center min-h-[44px]" />
              
              <Button
                variant="link"
                size="sm"
                onClick={() => setShowGoogleInput(true)}
                className="text-[11px] text-muted-foreground hover:text-primary transition-all gap-1.5"
              >
                <KeyRound className="h-3 w-3" /> Paste raw token / credentials manually
              </Button>
            </div>
          ) : (
            <form onSubmit={handleGoogleSubmit} className="space-y-3.5 bg-muted/30 p-4 rounded-xl border border-border/50 animate-in fade-in duration-200">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                  <KeyRound className="h-3.5 w-3.5 text-primary" /> Google OAuth ID / Access Token
                </label>
                <Input 
                  type="text" 
                  placeholder="Paste Google Token..." 
                  value={googleTokenInput} 
                  onChange={(e) => setGoogleTokenInput(e.target.value)} 
                  required 
                  className="h-10 px-3.5 rounded-lg border-border/80 bg-background text-sm"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="flex-1 h-10 rounded-lg text-xs font-bold" disabled={loading}>
                  Authenticate Token
                </Button>
                <Button variant="ghost" type="button" onClick={() => setShowGoogleInput(false)} className="h-10 rounded-lg text-xs">
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </Dialog>
  )
}
