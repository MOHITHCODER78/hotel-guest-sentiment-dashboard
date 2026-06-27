import { NavLink, Outlet } from "react-router-dom"
import {
  BarChart3,
  FileUp,
  Hotel,
  LogOut,
  MessageSquareText,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/layout/ThemeToggle"
import { useAuth } from "@/context/AuthContext"
import { cn } from "@/lib/utils"

const navItems = [
  { to: "/", label: "Dashboard", icon: BarChart3 },
  { to: "/analyze", label: "Analyze", icon: Sparkles },
  { to: "/upload", label: "Upload CSV", icon: FileUp },
  { to: "/reviews", label: "Reviews", icon: MessageSquareText },
]

export function AppLayout() {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-background lg:flex">
      <aside className="border-b border-border bg-card lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
        <div className="flex items-center justify-between gap-3 p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <Hotel className="h-5 w-5" />
            </div>
            <div>
              <p className="font-semibold">Hotel Sentiment</p>
              <p className="text-xs text-muted-foreground">Manager Dashboard</p>
            </div>
          </div>
          <ThemeToggle />
        </div>

        <nav className="space-y-1 px-4 pb-4 lg:pb-6">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden px-4 pb-6 lg:block">
          <Button variant="outline" className="w-full justify-start gap-2" onClick={logout}>
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 p-4 md:p-8">
        <Outlet />
      </main>
    </div>
  )
}
