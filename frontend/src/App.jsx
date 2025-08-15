import { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Callback from './Callback';
import ProtectedRoute from './ProtectedRoute';
import Navbar from './components/Navbar';
import About from './pages/About';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Quizzes from './pages/Quizzes';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch('http://localhost:8001/auth/user', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            console.error('Failed to fetch user data');
            localStorage.removeItem('access_token');
            setUser(null);
          }
        } catch (error) {
          console.error('Error fetching user data:', error);
          localStorage.removeItem('access_token');
          setUser(null);
        }
      }
    };
    fetchUser();
  }, []);

  const handleGoogleLogin = () => {
    setLoading(true)
    // Redirect to backend Google login endpoint
    window.location.href = 'http://localhost:8001/auth/login'
  }

  const handleLogout = () => {
    // Clear local storage
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar user={user} onLogout={handleLogout} />
      <Routes>
        <Route
          path="/"
          element={
            <div className="container mx-auto p-8">
              <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
                <h1 className="text-3xl font-bold text-center mb-6">Welcome to Quiz App</h1>
                {!user ? (
                  <div className="text-center">
                    <p className="mb-4">Sign in to start taking quizzes!</p>
                    <button
                      onClick={handleGoogleLogin}
                      className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                      disabled={loading}
                    >
                      {loading ? 'Loading...' : 'Sign in with Google'}
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="mb-4">Welcome back, {user.name}!</p>
                    <Link
                      to="/dashboard"
                      className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                    >
                      Go to Dashboard
                    </Link>
                  </div>
                )}
              </div>
            </div>
          }
        />
        <Route path="/callback" element={<Callback />} />
        <Route path="/about" element={<About />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute user={user}>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute user={user}>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quizzes"
          element={
            <ProtectedRoute user={user}>
              <Quizzes />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default App
