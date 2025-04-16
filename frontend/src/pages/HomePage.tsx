import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import axios from 'axios';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState<string>('Checking...');
  const [statusColor, setStatusColor] = useState<string>('text-yellow-500');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [userType, setUserType] = useState<string>('');

  // Check if user is logged in
  useEffect(() => {
    const checkLoginStatus = () => {
      const userString = localStorage.getItem('user');
      if (userString) {
        try {
          const userData = JSON.parse(userString);
          if (userData.token) {
            setIsLoggedIn(true);
            setUserType(userData.userType || '');
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
          localStorage.removeItem('user');
        }
      }
    };

    checkLoginStatus();
  }, []);

  // Check API connectivity on component mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await fetch('http://localhost:3000/');
        if (response.ok) {
          const text = await response.text();
          setApiStatus(`Connected: ${text}`);
          setStatusColor('text-green-500');
        } else {
          setApiStatus(`Error: ${response.status} ${response.statusText}`);
          setStatusColor('text-red-500');
        }
      } catch (error) {
        console.error('API check error:', error);
        setApiStatus(`Connection failed: ${error instanceof Error ? error.message : String(error)}`);
        setStatusColor('text-red-500');
      }
    };

    checkApiStatus();
  }, []);

  return (
    <div>
      <Header />
      <main className="container mx-auto my-8">
        <div className="flex flex-col items-center text-center">
          <h1 className="text-2xl font-bold mb-4">Welcome to Therapy Connect</h1>
          <p className="mb-6">
            A platform connecting individuals with professional therapists
          </p>
          
          <div className={`mb-6 font-bold ${statusColor}`}>
            <p>Backend API Status: {apiStatus}</p>
          </div>

          {isLoggedIn ? (
            <div className="flex flex-col gap-4">
              <p className="mb-4">You are logged in as a {userType}.</p>
              <Link
                to="/profile"
                className="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded"
              >
                Go to Profile
              </Link>
              <button
                onClick={() => {
                  localStorage.removeItem('user');
                  setIsLoggedIn(false);
                  window.location.reload();
                }}
                className="bg-red-500 hover:bg-red-600 text-white p-4 rounded"
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <div className="flex gap-4">
                <Link
                  to="/signup/user"
                  className="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded"
                >
                  Sign Up as User
                </Link>
                <Link
                  to="/signup/therapist"
                  className="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded"
                >
                  Sign Up as Therapist
                </Link>
              </div>
              <div className="mt-4">
                <p>
                  Already have an account?{' '}
                  <Link to="/login" className="text-blue-500">
                    Login here
                  </Link>
                </p>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default HomePage; 