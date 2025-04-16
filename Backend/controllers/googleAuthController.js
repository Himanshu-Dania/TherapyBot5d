const jwt = require('jsonwebtoken');
const { OAuth2Client } = require('google-auth-library');
const User = require('../src/models/User');
const Therapist = require('../src/models/Therapist');

// Initialize the Google OAuth client
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const client = new OAuth2Client(CLIENT_ID);

// Verify Google token with explicit redirect URI
async function verifyGoogleToken(token, redirectUri) {
  try {
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: CLIENT_ID,
      // Only include redirectUri if provided
      ...(redirectUri && { redirectUri })
    });
    
    return ticket.getPayload();
  } catch (error) {
    console.error('Error verifying Google token:', error);
    throw new Error(`Invalid Google token: ${error.message}`);
  }
}

// Login with Google
exports.googleLogin = async (req, res) => {
  try {
    const { token, redirectUri } = req.body;
    
    if (!token) {
      return res.status(400).json({ message: 'Google token is required' });
    }
    
    console.log('Received login request with token and redirectUri:', { 
      tokenLength: token.length,
      redirectUri
    });
    
    // Verify the token and get user data
    const payload = await verifyGoogleToken(token, redirectUri);
    const { email, name, picture, sub } = payload;
    
    // Check if user exists in either collection
    let user = await User.findOne({ email });
    let userType = 'user';
    
    if (!user) {
      // Check if it's a therapist
      const therapist = await Therapist.findOne({ email });
      
      if (!therapist) {
        return res.status(404).json({ 
          message: 'No account found with this Google email. Please sign up first.' 
        });
      }
      
      user = therapist;
      userType = 'therapist';
    }
    
    // Generate JWT token
    const authToken = jwt.sign(
      { id: user._id, email: user.email, userType },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    // Return user data and token
    return res.status(200).json({
      _id: user._id,
      email: user.email,
      name: user.name || user.username,
      userType,
      token: authToken
    });
  } catch (error) {
    console.error('Google login error:', error);
    return res.status(500).json({ message: error.message });
  }
};

// Sign up with Google (User)
exports.googleSignupUser = async (req, res) => {
  try {
    const { token, redirectUri, additionalData } = req.body;
    
    if (!token) {
      return res.status(400).json({ message: 'Google token is required' });
    }
    
    // Check for required additional data
    if (!additionalData || !additionalData.username) {
      return res.status(400).json({ message: 'Username is required' });
    }
    
    if (!additionalData.interests || !additionalData.interests.length) {
      return res.status(400).json({ message: 'At least one interest is required' });
    }
    
    const { username, interests } = additionalData;
    
    console.log('Received user signup request with complete data:', { 
      tokenLength: token.length,
      redirectUri,
      username,
      interestsCount: interests.length
    });
    
    // Verify the token and get user data
    const payload = await verifyGoogleToken(token, redirectUri);
    const { email, name, picture, sub } = payload;
    
    // Check if user already exists with this email
    let user = await User.findOne({ email });
    
    if (user) {
      return res.status(400).json({ message: 'User already exists with this email' });
    }
    
    // Check if username is already taken
    const usernameExists = await User.findOne({ username });
    if (usernameExists) {
      return res.status(400).json({ message: 'Username is already taken. Please choose another one.' });
    }
    
    // Also check therapist collection
    const therapist = await Therapist.findOne({ email });
    
    if (therapist) {
      return res.status(400).json({ 
        message: 'An account already exists with this email as a therapist' 
      });
    }
    
    // Create a new user
    user = new User({
      username,
      email,
      password: sub, // Using the Google ID as password (it will be hashed by the model)
      googleId: sub,
      profileImage: picture || '',
      interests,
      isGoogleLogin: true
    });
    
    await user.save();
    
    // Generate JWT token
    const authToken = jwt.sign(
      { id: user._id, email: user.email, userType: 'user' },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    // Return user data and token
    return res.status(201).json({
      _id: user._id,
      username: user.username,
      email: user.email,
      userType: 'user',
      token: authToken
    });
  } catch (error) {
    console.error('Google signup error:', error);
    return res.status(500).json({ message: error.message });
  }
};

// Sign up with Google (Therapist)
exports.googleSignupTherapist = async (req, res) => {
  try {
    const { token, redirectUri, additionalData } = req.body;
    
    if (!token) {
      return res.status(400).json({ message: 'Google token is required' });
    }
    
    // Check for required additional data
    if (!additionalData || !additionalData.username) {
      return res.status(400).json({ message: 'Username is required' });
    }
    
    if (!additionalData.specializations || !additionalData.specializations.length) {
      return res.status(400).json({ message: 'At least one specialization is required' });
    }
    
    const { username, specializations } = additionalData;
    
    console.log('Received therapist signup request with complete data:', { 
      tokenLength: token.length,
      redirectUri,
      username,
      specializationsCount: specializations.length
    });
    
    // Verify the token and get user data
    const payload = await verifyGoogleToken(token, redirectUri);
    const { email, name, picture, sub } = payload;
    
    // Check if therapist already exists
    let therapist = await Therapist.findOne({ email });
    
    if (therapist) {
      return res.status(400).json({ message: 'Therapist already exists with this email' });
    }
    
    // Check if username is already taken
    const usernameExists = await User.findOne({ username });
    if (usernameExists) {
      return res.status(400).json({ message: 'Username is already taken. Please choose another one.' });
    }
    
    // Also check user collection
    const user = await User.findOne({ email });
    
    if (user) {
      return res.status(400).json({ 
        message: 'An account already exists with this email as a user' 
      });
    }
    
    // Create a new therapist
    therapist = new Therapist({
      name, // Use the name from Google
      username, // Add the username field
      email,
      password: sub, // Using the Google ID as password (it will be hashed by the model)
      googleId: sub,
      profileImage: picture || '',
      specializations,
      document: {
        path: '',
        isVerified: false
      },
      isGoogleLogin: true
    });
    
    await therapist.save();
    
    // Generate JWT token
    const authToken = jwt.sign(
      { id: therapist._id, email: therapist.email, userType: 'therapist' },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    // Return therapist data and token
    return res.status(201).json({
      _id: therapist._id,
      name: therapist.name,
      username: therapist.username,
      email: therapist.email,
      userType: 'therapist',
      token: authToken
    });
  } catch (error) {
    console.error('Google signup error:', error);
    return res.status(500).json({ message: error.message });
  }
}; 