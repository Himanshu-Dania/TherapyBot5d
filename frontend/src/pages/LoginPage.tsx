import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Header from '../components/Header';
import axios from 'axios';
import GoogleAuth from '../components/GoogleAuth';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    userType: 'user',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const { email, password, userType } = formData;

  // Check if user is already logged in
  useEffect(() => {
    const checkLoginStatus = () => {
      const userString = localStorage.getItem('user');
      if (userString) {
        try {
          const userData = JSON.parse(userString);
          if (userData.token) {
            // User is already logged in, redirect to profile
            navigate('/profile');
            return;
          }
        } catch (error) {
          // Invalid user data
          localStorage.removeItem('user');
        }
      }
      setCheckingAuth(false);
    };

    checkLoginStatus();
  }, [navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUserTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, userType: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    console.log('Submitting login form with data:', { 
      email, 
      passwordLength: password.length, 
      userType 
    });

    try {
      const endpoint = userType === 'user' 
        ? 'http://localhost:3000/api/users/login' 
        : 'http://localhost:3000/api/therapists/login';
      
      console.log('Making API request to:', endpoint);
      
      // Create axios config with CORS settings
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        withCredentials: false
      };
      
      // Log the request payload
      console.log('Request payload:', JSON.stringify({ email, password }));
      
      const response = await axios.post(endpoint, { email, password }, config);
      
      console.log('API Response:', response);
      localStorage.setItem('user', JSON.stringify(response.data));
      navigate('/profile');
    } catch (error: any) {
      console.error('Login error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        name: error.name,
        stack: error.stack,
        config: error.config,
        code: error.code
      });
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(`Server error: ${error.response.data?.message || error.response.statusText || 'Invalid email or password'}`);
      } else if (error.request) {
        // The request was made but no response was received
        setError('No response from server. Please check your internet connection or try again later.');
        console.error('Request was made but no response received:', error.request);
        
        // Try an alternative approach with fetch API
        console.log('Attempting alternative request with fetch API...');
        try {
          const endpoint = userType === 'user' 
            ? 'http://localhost:3000/api/users/login' 
            : 'http://localhost:3000/api/therapists/login';
            
          const fetchResponse = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email,
              password,
            }),
          });
          
          if (fetchResponse.ok) {
            const data = await fetchResponse.json();
            console.log('Fetch API response:', data);
            localStorage.setItem('user', JSON.stringify(data));
            navigate('/profile');
            return;
          } else {
            console.error('Fetch API failed with status:', fetchResponse.status);
            setError(`Server error (fetch): ${fetchResponse.status} ${fetchResponse.statusText}`);
          }
        } catch (fetchError) {
          console.error('Fetch API error:', fetchError);
        }
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  if (checkingAuth) {
    return (
      <div>
        <Header />
        <main className="container mx-auto my-8 text-center">
          <p>Checking authentication status...</p>
        </main>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <main className="container mx-auto my-8">
        <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
          <h1 className="text-xl font-bold mb-6 text-center">Login</h1>
          
          {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="userType" className="block mb-2">
                User Type
              </label>
              <select
                id="userType"
                name="userType"
                value={userType}
                onChange={handleUserTypeChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="user">Regular User</option>
                <option value="therapist">Therapist</option>
              </select>
            </div>
            
            <div className="mb-4">
              <label htmlFor="email" className="block mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={email}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>

            <div className="mb-4">
              <label htmlFor="password" className="block mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={password}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          {/* Google Authentication */}
          <GoogleAuth mode="login" />
          
          {/* Debugging info */}
          <div className="mt-4 text-xs text-gray-400 text-center">
            <p>Current URL: {window.location.href}</p>
            <p>If you see OAuth errors, make sure this URL is in your Google Console</p>
          </div>

          <div className="mt-4 text-center">
            <p>
              Don't have an account?{' '}
              <Link to="/signup/user" className="text-blue-500">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LoginPage; 