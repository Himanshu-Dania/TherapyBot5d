import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import axios from 'axios';
import { User, Therapist } from '../types';
import ProtectedRoute from '../components/ProtectedRoute';

const ProfileContent: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<User | Therapist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      const userString = localStorage.getItem('user');
      
      if (!userString) {
        setError('You must be logged in to view this page');
        return;
      }
      
      try {
        const userData = JSON.parse(userString);
        const token = userData.token;
        const userType = userData.userType;
        
        if (!token) {
          setError('Authentication token not found. Please log in again.');
          localStorage.removeItem('user');
          return;
        }

        console.log('Fetching profile with token:', token.substring(0, 15) + '...');

        try {
          const endpoint = userType === 'user' 
            ? 'http://localhost:3000/api/users/profile' 
            : 'http://localhost:3000/api/therapists/profile';
          
          const { data } = await axios.get(endpoint, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          
          console.log('Profile data fetched successfully:', data);
          setProfile(data);
        } catch (requestError: any) {
          console.error('Error fetching profile data:', requestError);
          
          // Check if this is an authentication error
          if (requestError.response?.status === 401) {
            setError('Authentication failed. Your session may have expired. Please log in again.');
            localStorage.removeItem('user');
            setTimeout(() => {
              navigate('/login');
            }, 1500);
          } else {
            setError(`Failed to load profile: ${requestError.response?.data?.message || requestError.message}`);
          }
        }
      } catch (parseError) {
        console.error('Error parsing user data:', parseError);
        setError('Invalid user data. Please log in again.');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  if (loading) {
    return (
      <div>
        <Header />
        <main className="container mx-auto my-8 text-center">
          <p>Loading profile...</p>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Header />
        <main className="container mx-auto my-8 text-center">
          <p className="text-red-500">{error}</p>
          {error.includes('expired') && <p>Redirecting to login...</p>}
        </main>
      </div>
    );
  }

  // Check if the profile is a user or therapist
  const isUser = profile && 'username' in profile;

  return (
    <div>
      <Header />
      <main className="container mx-auto my-8">
        <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
          <h1 className="text-xl font-bold mb-6 text-center">
            {isUser ? 'User Profile' : 'Therapist Profile'}
          </h1>

          {isUser ? (
            // User profile
            <div>
              <div className="mb-4">
                <p className="font-bold">Username:</p>
                <p>{(profile as User).username}</p>
              </div>
              <div className="mb-4">
                <p className="font-bold">Email:</p>
                <p>{profile?.email}</p>
              </div>
              <div className="mb-4">
                <p className="font-bold">Interests:</p>
                {(profile as User).interests && (profile as User).interests.length > 0 ? (
                  <ul className="list-disc pl-5">
                    {(profile as User).interests.map((interest, index) => (
                      <li key={index}>{interest}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No interests specified</p>
                )}
              </div>
            </div>
          ) : (
            // Therapist profile
            <div>
              <div className="mb-4">
                <p className="font-bold">Name:</p>
                <p>{(profile as Therapist).name}</p>
              </div>
              <div className="mb-4">
                <p className="font-bold">Email:</p>
                <p>{profile?.email}</p>
              </div>
              <div className="mb-4">
                <p className="font-bold">Verification Status:</p>
                <p>
                  {(profile as Therapist).document?.isVerified
                    ? 'Verified ✓'
                    : 'Pending Verification'}
                </p>
              </div>
              <div className="mb-4">
                <p className="font-bold">Specializations:</p>
                {(profile as Therapist).specializations && (profile as Therapist).specializations.length > 0 ? (
                  <ul className="list-disc pl-5">
                    {(profile as Therapist).specializations.map((spec, index) => (
                      <li key={index}>{spec}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No specializations specified</p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

const ProfilePage: React.FC = () => {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
};

export default ProfilePage; 