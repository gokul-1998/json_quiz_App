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
import Decks from './pages/Decks';

function App() {
    const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      try {
        if (token) {
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
        } 
      } catch (error) {
        console.error('Error fetching user data:', error);
        localStorage.removeItem('access_token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

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
                    <p className="text-gray-600">Use the Google login button in the navbar above</p>
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
            <ProtectedRoute user={user} loading={loading}>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute user={user} loading={loading}>
              <Profile user={user} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quizzes"
          element={
            <ProtectedRoute user={user} loading={loading}>
              <Quizzes />
            </ProtectedRoute>
          }
        />
        <Route
          path="/decks"
          element={
            <ProtectedRoute user={user} loading={loading}>
              <Decks />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default App
