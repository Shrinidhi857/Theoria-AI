import React, { useState } from "react"
import { User, Mail, Shield, Calendar, Pencil, Save, X, AlertCircle, CheckCircle2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useAuth } from "@/context/AuthContext"
import { authService } from "@/services/authService"
import type { User as UserType } from "@/services/authService"
import { formatDate } from "@/utils/formatters"

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth()
  const [editing, setEditing] = useState(false)
  const [fullName, setFullName] = useState(user?.full_name ?? "")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  if (!user) return null

  const handleSave = async () => {
    if (newPassword && newPassword !== confirmPassword) {
      setError("Passwords do not match.")
      return
    }
    if (newPassword && newPassword.length < 6) {
      setError("Password must be at least 6 characters.")
      return
    }

    setError(null)
    setLoading(true)
    try {
      const updated: UserType = await authService.updateProfile({
        full_name: fullName || undefined,
        password: newPassword || undefined,
      })
      updateUser(updated)
      setEditing(false)
      setNewPassword("")
      setConfirmPassword("")
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update profile.")
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setEditing(false)
    setFullName(user?.full_name ?? "")
    setNewPassword("")
    setConfirmPassword("")
    setError(null)
  }

  const avatar = user.full_name?.[0]?.toUpperCase() ?? user.email?.[0]?.toUpperCase() ?? "U"

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <User className="h-7 w-7 text-primary" />
          </div>
          My Profile
        </h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Manage your account information and settings
        </p>
      </div>

      <Card className="border-border shadow-md overflow-hidden">
        <div className="h-24 bg-gradient-to-r from-primary/30 via-primary/10 to-transparent" />
        <CardContent className="relative pt-0 pb-6">
          <div className="-mt-10 mb-4 flex items-end justify-between">
            <div className="h-20 w-20 rounded-2xl border-4 border-background bg-primary/20 flex items-center justify-center text-3xl font-extrabold text-primary shadow-lg">
              {avatar}
            </div>
            {!editing ? (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)} className="gap-2">
                <Pencil className="h-3.5 w-3.5" /> Edit Profile
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSave} disabled={loading} className="gap-2">
                  <Save className="h-3.5 w-3.5" /> {loading ? "Saving..." : "Save"}
                </Button>
                <Button size="sm" variant="ghost" onClick={handleCancel}>
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" /> {error}
            </div>
          )}
          {success && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 shrink-0" /> Profile updated successfully!
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">Full Name</label>
              {editing ? (
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                />
              ) : (
                <p className="font-semibold text-base">
                  {user.full_name ?? <span className="text-muted-foreground italic">Not set</span>}
                </p>
              )}
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1 mb-1">
                <Mail className="h-3 w-3" /> Email Address
              </label>
              <p className="text-sm text-foreground">{user.email}</p>
              <p className="text-xs text-muted-foreground mt-0.5">Email cannot be changed</p>
            </div>

            {editing && user.auth_provider === "email" && (
              <div className="pt-2 space-y-3 border-t border-border">
                <p className="text-xs font-medium text-muted-foreground">Change Password (optional)</p>
                <Input
                  type="password"
                  placeholder="New password (min 6 chars)"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
                <Input
                  type="password"
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Shield className="h-4 w-4 text-primary" /> Account Details
          </CardTitle>
          <CardDescription>Read-only account metadata</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-muted-foreground">User ID</span>
            <span className="font-mono font-medium">#{user.id}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-muted-foreground">Auth Provider</span>
            <Badge variant="outline" className="capitalize">{user.auth_provider}</Badge>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-muted-foreground">Account Status</span>
            <Badge variant={user.is_active ? "success" : "destructive"}>
              {user.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-muted-foreground flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" /> Member Since
            </span>
            <span className="font-medium text-xs">{formatDate(user.created_at)}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
