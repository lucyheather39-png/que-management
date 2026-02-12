put it # Government Queue & Appointment System

A professional, user-friendly Django application for managing government service queues and appointments with atomic design principles.

## Features

### 🔐 Security Management
- User registration with email verification
- Secure login/logout system
- User profile management
- Password hashing and validation
- Session management

### 👥 User Types & Priority Logic
- **Senior Citizens**: Priority Level 1
- **Person with Disability (PWD)**: Priority Level 2
- **Regular Citizens**: Priority Level 3

### 📋 Queue Management
- Real-time queue number generation
- Priority-based queue positioning
- Queue status tracking (Waiting, Serving, Completed, Cancelled)
- Position tracking in queue
- Service type selection

### 📅 Appointment System
- Appointment booking for future dates
- Status tracking (Pending, Approved, Rejected, Completed, Cancelled)
- Priority consideration in appointments
- Admin approval workflow

### ✅ Admin Verification Workflow
- User verification requests and approval
- Admin dashboard with statistics
- Appointment approval/rejection
- Queue management capabilities
- User management interface
- Admin activity logging

### 🎨 Professional UI/UX
- Minimalist, clean design
- Atomic design principles
- Bootstrap 5 responsive layout
- Mobile-friendly interface
- Smooth animations and transitions

## Project Structure

```
queue_system/
├── config/              # Django settings and URLs
├── apps/
│   ├── accounts/       # User profiles and account management
│   ├── security/       # Authentication (login, register, logout)
│   ├── queues/         # Queue management
│   ├── appointments/   # Appointment system
│   └── admin_management/  # Admin dashboard and verification
├── templates/          # HTML templates (atomic design)
│   ├── layouts/        # Base layouts
│   ├── components/     # Reusable components
│   └── pages/          # Page templates
├── static/            # CSS, JavaScript
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual Environment (recommended)

### Step 1: Clone or Extract Project
```bash
cd "queue management/queue_system"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy .env.example to .env
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Update .env with your settings
```

### Step 5: Create Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 7: Create Sample Services
```bash
python manage.py shell
# Then run:
from apps.queues.models import Service
Service.objects.create(
    name='Birth Certificate',
    code='BC',
    description='Request and obtain birth certificates',
    service_type='birth',
    estimated_time=15,
    max_daily_queue=50,
    is_active=True
)
Service.objects.create(
    name='Business Permit',
    code='BP',
    description='Business permit registration and renewal',
    service_type='permit',
    estimated_time=30,
    max_daily_queue=30,
    is_active=True
)
# Add more services as needed
exit()
```

### Step 8: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 9: Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Usage

### For Regular Users
1. **Register**: Create an account with your details
2. **Select Citizen Type**: Choose appropriate category (Senior/PWD/Regular)
3. **Take Queue**: Join a queue for immediate service
4. **Book Appointment**: Schedule for a future time
5. **Track Status**: Monitor queue and appointment status

### For Admin
1. **Login**: Use superuser credentials
2. **Access Admin Panel**: Click "Admin Panel" in navigation
3. **Verify Users**: Review pending user verifications
4. **Approve Appointments**: Manage appointment requests
5. **Manage Queues**: Update queue status
6. **View Logs**: Monitor admin activities

## Database Models

### UserProfile
- Stores user citizen type and verification status
- Links to Django User model
- Priority level calculation

### Queue
- Manages queue entries with priority levels
- Tracks queue status and position
- Associates with services

### Appointment
- Stores appointment requests
- Tracks approval status
- Contains priority information

### VerificationRequest
- Manages admin approval workflow
- Stores verification documents
- Tracks review status

## API Routes

### Authentication
- `GET/POST /auth/register/` - User registration
- `GET/POST /auth/login/` - User login
- `GET /auth/logout/` - User logout
- `GET/POST /auth/profile/` - User profile

### Queue Management
- `GET /queue/dashboard/` - User queue dashboard
- `GET/POST /queue/take/` - Take a queue
- `GET /queue/detail/<id>/` - View queue details
- `GET /queue/list/` - View queue history
- `POST /queue/cancel/<id>/` - Cancel queue

### Appointments
- `GET/POST /appointment/book/` - Book appointment
- `GET /appointment/my-appointments/` - View appointments
- `GET /appointment/detail/<id>/` - View appointment details
- `POST /appointment/cancel/<id>/` - Cancel appointment

### Admin Panel
- `GET /admin-panel/` - Admin dashboard
- `GET /admin-panel/verifications/pending/` - Pending verifications
- `POST /admin-panel/verifications/<id>/approve/` - Approve verification
- `GET /admin-panel/appointments/pending/` - Pending appointments
- `POST /admin-panel/appointments/<id>/manage/` - Manage appointment
- `GET /admin-panel/queue/management/` - Queue management
- `POST /admin-panel/queue/<id>/update/` - Update queue status
- `GET /admin-panel/users/` - Users management
- `GET /admin-panel/logs/` - Admin logs

## Design Principles

### Atomic Design
- **Atoms**: Basic HTML elements and styles
- **Molecules**: Small reusable components (buttons, form fields)
- **Organisms**: Complex components (forms, cards, tables)
- **Templates**: Page layouts
- **Pages**: Full page implementations

### Minimalist Design
- Clean, simple interface
- Focus on functionality
- Professional color scheme
- Consistent spacing and typography
- Smooth interactions

## Security Features

- CSRF Protection (Django built-in)
- Password hashing and validation
- Session-based authentication
- Login required decorators on protected views
- Admin-only access control
- SQL injection prevention (ORM)
- XSS protection via Django templates

## Technologies Used

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (default, configurable)
- **Forms**: Django Forms, Crispy Forms

## Configuration

Edit `config/settings.py` for:
- Database configuration
- Email settings
- Static files location
- Security settings
- Session timeout
- Time zone

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
```bash
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

## Future Enhancements

- SMS/Email notifications
- Real-time queue updates with WebSockets
- QR code queue numbers
- Payment integration
- Advanced analytics and reporting
- Multi-language support
- Mobile app

## License

This project is developed for government services. Use according to local regulations.

## Support

For issues and questions, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Developed with Django & Bootstrap**
