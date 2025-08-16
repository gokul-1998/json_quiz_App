import { Link } from 'react-router-dom';

const Navbar = ({ user, onLogout }) => {
  const handleGoogleLogin = () => {
    // Redirect to backend Google login endpoint
    window.location.href = 'http://localhost:8001/auth/login'
  }
  console.log(user)
  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-white font-bold">
            Quiz App
          </Link>
          <Link to="/about" className="text-gray-300 hover:text-white">
            About
          </Link>
          {user && (
            <>
              <Link to="/dashboard" className="text-gray-300 hover:text-white">
                Dashboard
              </Link>
              <Link to="/profile" className="text-gray-300 hover:text-white">
                Profile
              </Link>
              <Link to="/quizzes" className="text-gray-300 hover:text-white">
                Quizzes
              </Link>
            </>
          )}
        </div>
        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">{user.name}</span>
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                  <span className="text-gray-700 font-bold">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <button
                onClick={onLogout}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={handleGoogleLogin}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center"
            >
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.47-1 7.29-2.71l-3.57-2.77c-.98.66-2.23 1.06-3.72 1.06-2.87 0-5.3-1.95-6.19-4.65H3.2v2.77C4.82 20.8 8.1 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.81 14.35c-.19-.57-.31-1.17-.31-1.79 0-.63.12-1.23.31-1.79V7.99H3.2C2.47 9.45 2 11.17 2 13c0 1.83.47 3.55 1.2 5.01l2.61-2.66z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 4.32 3.81 2.8 7.99l3.01 2.36C6.7 7.34 9.15 5.38 12 5.38z"
                  fill="#EA4335"
                />
              </svg>
              Sign in with Google
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
