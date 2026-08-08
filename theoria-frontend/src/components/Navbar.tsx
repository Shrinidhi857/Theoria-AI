import React, { useState, useRef, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { History, User, LogOut, Zap, Network } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ThemeToggle } from "@/components/ThemeToggle"
import { useAuth } from "@/context/AuthContext"

interface NavbarProps {
  onAuthClick: () => void
}

const NAV_LINKS = [
  { path: "/new", id: "studio", label: "Studio", icon: Zap },
  { path: "/graph", id: "graph", label: "Knowledge Graph", icon: Network },
  { path: "/history", id: "history", label: "History", icon: History },
]


export const Navbar: React.FC<NavbarProps> = ({ onAuthClick }) => {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [profileOpen, setProfileOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const activePath = location.pathname

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setProfileOpen(false)
      }
    }
    if (profileOpen) document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [profileOpen])

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-4 md:px-6">
        {/* Logo */}
        <button onClick={() => navigate("/")} className="flex items-center gap-3 group">
          <img src="/Theoria.svg" alt="Theoria AI Logo" className="h-10 w-10 object-contain" />
          <div className="flex flex-col items-start leading-none">
            <span className="font-bold text-lg tracking-tight">Theoria</span>
            <span className="text-[10px] text-primary font-medium tracking-widest uppercase">AI Teaching Engine</span>
          </div>
        </button>

        {/* Nav Links */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ path, id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => navigate(path)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                activePath === path
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
              {id === "history" && isAuthenticated && (
                <Badge variant="secondary" className="ml-0.5 h-4 px-1 text-[10px]">My</Badge>
              )}
            </button>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {isAuthenticated ? (
            <div ref={dropdownRef} className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="h-9 w-9 rounded-full bg-primary/20 border-2 border-primary/30 flex items-center justify-center text-sm font-bold text-primary hover:border-primary transition-all"
              >
                {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
              </button>
              {profileOpen && (
                <div className="absolute top-12 right-0 w-56 bg-popover border border-border rounded-xl shadow-xl p-2 z-50 animate-in slide-in-from-top-2 duration-150">
                  <div className="px-3 py-2 mb-1">
                    <p className="font-semibold text-sm">{user?.full_name || "User"}</p>
                    <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                    <Badge variant="outline" className="mt-1 text-[10px]">
                      via {user?.auth_provider}
                    </Badge>
                  </div>
                  <div className="border-t border-border my-1" />
                  <button
                    onClick={() => { setProfileOpen(false); navigate("/profile") }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-muted transition-colors"
                  >
                    <User className="h-4 w-4" /> View Profile
                  </button>
                  <button
                    onClick={() => { setProfileOpen(false); logout() }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-destructive hover:bg-destructive/10 transition-colors"
                  >
                    <LogOut className="h-4 w-4" /> Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Button onClick={onAuthClick} className="gap-2" size="sm">
              <User className="h-4 w-4" /> Sign In
            </Button>
          )}
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="md:hidden flex items-center gap-1 px-4 pb-2">
        {NAV_LINKS.map(({ path, id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => navigate(path)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all flex-1 justify-center ${
              activePath === path
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted"
            }`}
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>
    </header>
  )
}
