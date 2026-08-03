import React, { useState } from "react"
import { LogIn, UserPlus, AlertCircle } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { Dialog, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
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
      <DialogHeader>
        <div className="flex items-center gap-3 mb-1">
          <img src="/Theoria.svg" alt="Theoria AI" className="h-10 w-10 object-contain" />
          <div>
            <DialogTitle className="text-xl font-bold">Welcome to Theoria AI</DialogTitle>
            <DialogDescription>
              Sign in to save your video generation history and access premium features.
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-destructive/15 text-destructive text-sm flex items-center gap-2 border border-destructive/30">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <Tabs defaultValue="login" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="login" className="gap-2">
            <LogIn className="h-4 w-4" /> Sign In
          </TabsTrigger>
          <TabsTrigger value="signup" className="gap-2">
            <UserPlus className="h-4 w-4" /> Register
          </TabsTrigger>
        </TabsList>

        <TabsContent value="login">
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Email Address</label>
              <Input type="email" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Password</label>
              <Input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Sign In with Email"}
            </Button>
          </form>
        </TabsContent>

        <TabsContent value="signup">
          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Full Name</label>
              <Input type="text" placeholder="John Doe" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Email Address</label>
              <Input type="email" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Password</label>
              <Input type="password" placeholder="At least 6 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating Account..." : "Create Account"}
            </Button>
          </form>
        </TabsContent>
      </Tabs>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground font-medium">Or continue with</span>
        </div>
      </div>

      {!showGoogleInput ? (
        <Button variant="outline" type="button" onClick={() => setShowGoogleInput(true)} className="w-full gap-2 hover:bg-muted">
          <svg className="h-4 w-4" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
          </svg>
          Sign in with Google OAuth
        </Button>
      ) : (
        <form onSubmit={handleGoogleSubmit} className="space-y-3">
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-1">Google OAuth ID / Access Token</label>
            <Input type="text" placeholder="Paste Google Token..." value={googleTokenInput} onChange={(e) => setGoogleTokenInput(e.target.value)} required />
          </div>
          <div className="flex gap-2">
            <Button type="submit" className="flex-1" disabled={loading}>Authenticate Google Token</Button>
            <Button variant="ghost" type="button" onClick={() => setShowGoogleInput(false)}>Cancel</Button>
          </div>
        </form>
      )}
    </Dialog>
  )
}
