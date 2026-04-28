import './App.css'
import { Route, Routes } from 'react-router-dom'
import { AuthProvider } from './app/AuthContext'
import { RequireAuth } from './app/RequireAuth'
import { Layout } from './components/Layout'
import { HomeRedirect } from './pages/HomeRedirect'
import { LoginPage } from './pages/LoginPage'
import { ValidateMemberPage } from './pages/provider/ValidateMemberPage'
import { BillServicePage } from './pages/provider/BillServicePage'
import { ProviderDirectoryPage } from './pages/provider/ProviderDirectoryPage'
import { MySubmittedServicesPage } from './pages/provider/MySubmittedServicesPage'
import { MembersPage } from './pages/manager/MembersPage'
import { ProvidersPage } from './pages/manager/ProvidersPage'
import { ServicesPage } from './pages/manager/ServicesPage'
import { ReportsPage } from './pages/manager/ReportsPage'
import { AcmePage } from './pages/manager/AcmePage'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<RequireAuth />}>
          <Route element={<Layout />}>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/provider/validate" element={<ValidateMemberPage />} />
            <Route path="/provider/bill" element={<BillServicePage />} />
            <Route path="/provider/directory" element={<ProviderDirectoryPage />} />
            <Route path="/provider/services" element={<MySubmittedServicesPage />} />
            <Route path="/manager/members" element={<MembersPage />} />
            <Route path="/manager/providers" element={<ProvidersPage />} />
            <Route path="/manager/services" element={<ServicesPage />} />
            <Route path="/manager/reports" element={<ReportsPage />} />
            <Route path="/manager/acme" element={<AcmePage />} />
          </Route>
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
