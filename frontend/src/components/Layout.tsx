import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../app/AuthContext'

export function Layout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  async function onLogout() {
    await signOut()
    navigate('/login')
  }

  const role = user?.role

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Link to="/">ChocAn DPS</Link>
          <div className="muted small">Localhost system</div>
        </div>

        <nav className="nav">
          {role === 'provider' || role === 'admin' ? (
            <>
              <div className="navSection">Provider</div>
              <NavLink to="/provider/validate">Validate Member</NavLink>
              <NavLink to="/provider/bill">Bill Service</NavLink>
              <NavLink to="/provider/directory">Provider Directory</NavLink>
              <NavLink to="/provider/services">My Submitted Services</NavLink>
            </>
          ) : null}

          {role === 'manager' || role === 'admin' ? (
            <>
              <div className="navSection">Manager</div>
              <NavLink to="/manager/members">Members</NavLink>
              <NavLink to="/manager/providers">Providers</NavLink>
              <NavLink to="/manager/services">Services</NavLink>
              <NavLink to="/manager/reports">Weekly Reports</NavLink>
              <NavLink to="/manager/acme">Simulate Acme</NavLink>
            </>
          ) : null}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="pill">
            {user ? (
              <>
                <strong>{user.username}</strong> <span className="muted">({user.role})</span>
              </>
            ) : (
              'Not signed in'
            )}
          </div>
          <button className="btn" onClick={onLogout}>
            Logout
          </button>
        </header>
        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

