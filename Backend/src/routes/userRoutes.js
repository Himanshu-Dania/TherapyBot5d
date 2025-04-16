const express = require('express');
const { registerUser, authUser, getUserProfile } = require('../controllers/userController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

router.route('/').post(registerUser);
router.post('/login', authUser);
router.route('/profile').get(protect, getUserProfile);

module.exports = router; 