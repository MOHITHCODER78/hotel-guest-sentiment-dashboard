import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { AppLayout } from "@/components/layout/AppLayout"
import { AnalyzePage } from "@/pages/AnalyzePage"
import { DashboardPage } from "@/pages/DashboardPage"
import { LoginPage } from "@/pages/LoginPage"
import { RegisterPage } from "@/pages/RegisterPage"
import { ReviewsPage } from "@/pages/ReviewsPage"
import { UploadPage } from "@/pages/UploadPage"
import { AppProviders } from "@/providers/AppProviders"

export default function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="analyze" element={<AnalyzePage />} />
              <Route path="upload" element={<UploadPage />} />
              <Route path="reviews" element={<ReviewsPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProviders>
  )
}
