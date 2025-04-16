const express = require('express');
const { 
  registerTherapist, 
  authTherapist, 
  getTherapistProfile 
} = require('../controllers/therapistController');
const { protect } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

router.route('/').post(upload.single('document'), registerTherapist);
router.post('/login', authTherapist);
router.route('/profile').get(protect, getTherapistProfile);

module.exports = router; 