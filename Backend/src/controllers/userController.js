const User = require('../models/User');
const Therapist = require('../models/Therapist');
const generateToken = require('../utils/generateToken');

// @desc    Register a new user
// @route   POST /api/users
// @access  Public
const registerUser = async (req, res, next) => {
  try {
    console.log('User registration request received:', {
      username: req.body.username,
      email: req.body.email,
      interestsCount: req.body.interests ? req.body.interests.length : 0
    });

    const { username, email, password, interests, isGoogleLogin } = req.body;

    // Validate request body
    if (!username || !email || !password) {
      console.log('Registration error: Missing required fields');
      return res.status(400).json({ 
        message: 'Please provide all required fields (username, email, password)' 
      });
    }

    // Check if user already exists with this email
    const userExists = await User.findOne({ email });

    if (userExists) {
      console.log('Registration error: User already exists with email', email);
      return res.status(400).json({ message: 'User already exists with this email' });
    }

    // Check if username already exists in either collection
    const usernameExists = await User.findOne({ username }) || await Therapist.findOne({ username });
    if (usernameExists) {
      console.log('Registration error: Username already exists', username);
      return res.status(400).json({ message: 'Username is already taken. Please choose another one.' });
    }

    // Also check if user exists in the therapist collection with the same email
    const therapistExists = await Therapist.findOne({ email });
    if (therapistExists) {
      console.log('Registration error: A therapist account exists with email', email);
      return res.status(400).json({ message: 'An account already exists with this email as a therapist' });
    }

    try {
      const user = await User.create({
        username,
        email,
        password,
        interests: interests || [],
        isGoogleLogin: isGoogleLogin || false,
      });

      if (user) {
        console.log('User registered successfully:', {
          userId: user._id,
          username: user.username,
          email: user.email
        });
        
        const token = generateToken(user._id, user.userType);
        
        res.status(201).json({
          _id: user._id,
          username: user.username,
          email: user.email,
          interests: user.interests,
          userType: user.userType,
          token: token,
        });
      } else {
        console.log('Registration error: User creation failed');
        res.status(400).json({ message: 'Invalid user data' });
      }
    } catch (createError) {
      console.error('User creation error:', createError);
      
      if (createError.name === 'ValidationError') {
        return res.status(400).json({ message: createError.message });
      }
      
      return res.status(500).json({ message: 'Error creating user', error: createError.message });
    }
  } catch (error) {
    console.error('User registration error:', error);
    
    if (error.name === 'ValidationError') {
      return res.status(400).json({ message: error.message });
    }
    
    if (error.code === 11000) {
      return res.status(400).json({ message: 'Duplicate field value entered' });
    }
    
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// @desc    Auth user & get token
// @route   POST /api/users/login
// @access  Public
const authUser = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ message: 'Please provide email and password' });
    }

    const user = await User.findOne({ email });

    if (user && (await user.matchPassword(password))) {
      console.log('User logged in successfully:', {
        userId: user._id,
        email: user.email
      });
      
      res.json({
        _id: user._id,
        username: user.username,
        email: user.email,
        interests: user.interests,
        userType: user.userType,
        token: generateToken(user._id, user.userType),
      });
    } else {
      console.log('Login failed for email:', email);
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    console.error('User login error:', error);
    next(error);
  }
};

// @desc    Get user profile
// @route   GET /api/users/profile
// @access  Private
const getUserProfile = async (req, res, next) => {
  try {
    const user = await User.findById(req.user._id);

    if (user) {
      res.json({
        _id: user._id,
        username: user.username,
        email: user.email,
        interests: user.interests,
        userType: user.userType,
      });
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  } catch (error) {
    console.error('Get user profile error:', error);
    next(error);
  }
};

module.exports = { registerUser, authUser, getUserProfile }; 