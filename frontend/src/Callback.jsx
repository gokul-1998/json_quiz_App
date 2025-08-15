import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Callback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Handle the authentication callback
    const handleCallback = async () => {
      // Get the full URL including hash fragment
      const url = new URL(window.location.href);
      const hash = url.hash;
      
      // Extract the authorization code from the hash fragment
      if (hash) {
        const hashParams = new URLSearchParams(hash.substring(1));
        const code = hashParams.get('code');
        
        if (code) {
          try {
            // Redirect to backend callback endpoint with the code
            window.location.href = `http://localhost:8000/auth/callback?code=${code}`;
          } catch (error) {
            console.error('Error during authentication:', error);
            navigate('/');
          }
        } else {
          console.error('No authorization code found');
          navigate('/');
        }
      } else {
        // No hash in URL, check if we're being redirected from backend
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token');
        
        if (accessToken) {
          // Store the access token in localStorage
          localStorage.setItem('access_token', accessToken);
          // Redirect to the main app
          navigate('/');
        } else {
          console.error('No access token found');
          navigate('/');
        }
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-center">Processing Authentication...</h2>
        <p className="text-gray-600 text-center mt-2">Please wait while we process your authentication.</p>
      </div>
    </div>
  );
};

export default Callback;