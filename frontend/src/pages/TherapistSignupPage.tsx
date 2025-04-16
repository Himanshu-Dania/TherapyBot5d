import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Header from '../components/Header';
import axios from 'axios';
import GoogleAuth from '../components/GoogleAuth';

const SPECIALIZATION_OPTIONS = [
  'Cognitive Behavioral Therapy (CBT)',
  'Depression',
  'Anxiety',
  'Trauma',
  'PTSD',
  'Marriage Counseling',
  'Family Therapy',
  'Addiction',
  'Eating Disorders',
  'Child Psychology',
  'Grief Counseling',
  'Stress Management',
];

const TherapistSignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    specializations: [] as string[],
  });
  const [document, setDocument] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const { name, username, email, password, confirmPassword, specializations } = formData;

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

  const handleSpecializationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (e.target.checked) {
      setFormData({
        ...formData,
        specializations: [...specializations, value],
      });
    } else {
      setFormData({
        ...formData,
        specializations: specializations.filter((spec) => spec !== value),
      });
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setDocument(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!document) {
      setError('Please upload a document for verification');
      return;
    }

    setLoading(true);
    setError('');

    const formDataToSend = new FormData();
    formDataToSend.append('name', name);
    formDataToSend.append('username', username);
    formDataToSend.append('email', email);
    formDataToSend.append('password', password);
    formDataToSend.append('document', document);
    specializations.forEach((spec) => {
      formDataToSend.append('specializations', spec);
    });

    console.log('Submitting therapist signup form with data:', { 
      name, 
      username,
      email, 
      passwordLength: password.length,
      documentName: document.name,
      documentSize: document.size,
      documentType: document.type,
      specializations 
    });

    try {
      console.log('Making API request to:', 'http://localhost:3000/api/therapists');
      
      // Create axios config with appropriate headers
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        },
        withCredentials: false
      };
      
      const response = await axios.post(
        'http://localhost:3000/api/therapists',
        formDataToSend,
        config
      );
      
      console.log('API Response:', response);
      localStorage.setItem('user', JSON.stringify(response.data));
      navigate('/profile');
    } catch (error: any) {
      console.error('Registration error details:', {
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
        setError(`Server error: ${error.response.data?.message || error.response.statusText || 'Unknown error'}`);
      } else if (error.request) {
        // The request was made but no response was received
        setError('No response from server. Please check your internet connection or try again later.');
        console.error('Request was made but no response received:', error.request);
        
        // Try direct fetch API approach as a fallback
        console.log('Attempting alternative request with fetch API...');
        try {
          const fetchFormData = new FormData();
          fetchFormData.append('name', name);
          fetchFormData.append('email', email);
          fetchFormData.append('password', password);
          fetchFormData.append('document', document);
          specializations.forEach((spec) => {
            fetchFormData.append('specializations', spec);
          });
          
          const fetchResponse = await fetch('http://localhost:3000/api/therapists', {
            method: 'POST',
            body: fetchFormData
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
          <h1 className="text-xl font-bold mb-6 text-center">Sign Up as Therapist</h1>
          
          {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="name" className="block mb-2">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={name}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="username" className="block mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={username}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
              <small className="text-gray-500">
                Choose a unique username. This will be used to identify you on the platform.
              </small>
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

            <div className="mb-4">
              <label htmlFor="confirmPassword" className="block mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={confirmPassword}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>

            <div className="mb-4">
              <label htmlFor="document" className="block mb-2">
                Verification Document (PDF, DOC, DOCX)
              </label>
              <input
                type="file"
                id="document"
                name="document"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
              <small className="text-gray-500">
                Please upload a document to verify your credentials as a therapist
              </small>
            </div>

            <div className="mb-4">
              <label className="block mb-2">Specializations</label>
              <div className="grid grid-cols-2 gap-2">
                {SPECIALIZATION_OPTIONS.map((specialization) => (
                  <div key={specialization}>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="specializations"
                        value={specialization}
                        checked={specializations.includes(specialization)}
                        onChange={handleSpecializationChange}
                        className="mr-2"
                      />
                      {specialization}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded"
              disabled={loading}
            >
              {loading ? 'Signing up...' : 'Sign Up'}
            </button>
          </form>

          {/* Google Authentication */}
          <GoogleAuth mode="signup" userType="therapist" />

          {/* Debugging info */}
          <div className="mt-4 text-xs text-gray-400 text-center">
            <p>Current URL: {window.location.href}</p>
            <p>If you see OAuth errors, make sure this URL is in your Google Console</p>
          </div>

          <div className="mt-4 text-center">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="text-blue-500">
                Login
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TherapistSignupPage; 