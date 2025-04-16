import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [authStatus, setAuthStatus] = useState<'valid' | 'invalid' | 'checking'>('checking');

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userString = localStorage.getItem('user');
        if (!userString) {
          setAuthStatus('invalid');
          return;
        }

        const userData = JSON.parse(userString);
        
        // Check if token exists and is valid
        if (!userData.token) {
          setAuthStatus('invalid');
          return;
        }

        // Set user data
        setUser(userData);
        setAuthStatus('valid');

        // Optionally verify the token with the backend here
        // This is a lightweight check; the actual verification happens when accessing protected routes
      } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('user');
        setAuthStatus('invalid');
      }
    };

    checkAuth();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setAuthStatus('invalid');
    navigate('/login');
  };

  return (
    <header className="bg-blue-600 p-4 text-white">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          Therapy Connect
        </Link>
        <div className="flex items-center">
          {authStatus === 'checking' && (
            <span className="mr-4 text-yellow-300">⟳ Checking auth...</span>
          )}
          {authStatus === 'valid' && (
            <span className="mr-4 text-green-300">✓ Authenticated</span>
          )}
          <nav>
            <ul className="flex space-x-4">
              {authStatus === 'valid' && user ? (
                <>
                  <li>
                    <Link to="/profile" className="hover:text-blue-200">
                      Profile ({user.userType})
                    </Link>
                  </li>
                  <li>
                    <button
                      onClick={handleLogout}
                      className="hover:text-blue-200"
                    >
                      Logout
                    </button>
                  </li>
                </>
              ) : (
                <>
                  <li>
                    <Link to="/login" className="hover:text-blue-200">
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link to="/signup/user" className="hover:text-blue-200">
                      Sign Up
                    </Link>
                  </li>
                </>
              )}
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header; 