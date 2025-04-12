# Project Timeline Visualizer

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white)

A Django web application that provides interactive visualization for project timelines, helping teams track milestones, dependencies, and progress throughout the project lifecycle.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

Project Timeline Visualizer is a web-based tool designed to help project managers and team members visualize project schedules, track progress, and manage dependencies between tasks. The application provides an intuitive interface for creating, editing, and sharing project timelines with stakeholders.

## Features

- **Interactive Gantt Charts**: Visualize project schedules with drag-and-drop functionality
- **Milestone Tracking**: Set and monitor key project milestones
- **Dependency Management**: Define and visualize task dependencies between milestones
- **Progress Tracking**: Update and monitor milestone completion status (Pending, In Progress, Completed, Delayed)
- **Timeline Sharing**: Share project timelines with team members and stakeholders
- **Export Options**: Export timelines as PDF, CSV, or PNG
- **Analytics Dashboard**: View project and milestone statistics with interactive charts
- **Notifications System**: Receive alerts for upcoming milestones and shared projects
- **Responsive Design**: Access timelines on desktop and mobile devices
- **User Authentication**: Secure user login and project access control
- **Multiple Project Support**: Manage multiple project timelines simultaneously
- **Project Archiving**: Archive completed projects while keeping them accessible


## Technology Stack

- **Backend**: Django 4.x, Python 3.x
- **Frontend**: JavaScript, HTML5, CSS3
- **Data Visualization**: Chart.js, Frappe Gantt
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django Authentication System
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Forms**: django-crispy-forms with crispy-bootstrap4
- **PDF Generation**: xhtml2pdf, reportlab
- **Image Processing**: Pillow

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/avishekpaul1310/Project-Timeline-Visualizer.git
   cd Project-Timeline-Visualizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=
   ```

5. Set up the database:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at `http://127.0.0.1:8000/`

## Usage

### Creating a New Project Timeline

1. Log in to the application
2. Click on "Create New Project" button on the dashboard
3. Enter project details (name, start date, end date)
4. Click "Create" to generate the project

### Adding Milestones to Timeline

1. Open your project timeline
2. Click "Add Milestone" button
3. Fill in milestone details (name, start date, due date, dependencies)
4. Click "Create Milestone" to add the milestone to the timeline

### Visualizing with Gantt Chart

1. Open your project
2. Click on "Gantt Chart" tab
3. View milestones on the interactive Gantt chart
4. As a project owner, you can drag and drop milestones to update dates
5. Switch between Day, Week, and Month views
6. Export the Gantt chart as PNG

### Tracking Progress

1. Open your project timeline
2. For each milestone, use the dropdown menu to update its status
3. Choose from Pending, In Progress, Completed, or Delayed
4. View progress statistics in the Analytics section

### Sharing Timeline

1. Open your project timeline
2. Click on "Share" button
3. Enter the email address of the collaborator (must be a registered user)
4. Collaborators will receive notifications and can view the project

### Project Analytics

1. Click on "Analytics" in the navigation bar
2. View project statistics and milestone completion rates
3. See a breakdown of milestone statuses
4. Monitor your most complex projects by milestone count

## Project Structure

```
Project-Timeline-Visualizer/
│
├── timeline_project/          # Main Django project folder
│   ├── settings.py            # Project settings
│   ├── urls.py                # URL configuration
│   └── wsgi.py                # WSGI configuration
│
├── timeline_app/              # Django application folder
│   ├── models.py              # Data models (Project, Milestone, Notification)
│   ├── views.py               # View functions
│   ├── urls.py                # URL patterns
│   ├── forms.py               # Form definitions (ProjectForm, MilestoneForm)
│   ├── utils.py               # Utility functions
│   ├── context_processors.py  # Custom context processors
│   ├── tests.py               # Test cases
│   ├── admin.py               # Admin interface configuration
│   └── templates/             # App-specific templates
│       └── timeline_app/      # Timeline templates
│
├── static/                    # Static files
│   ├── css/                   # CSS files
│   ├── js/                    # JavaScript files
│   └── img/                   # Image files
│
├── templates/                 # Project-wide templates
│   └── registration/          # Authentication templates
│
├── media/                     # User-uploaded files
│
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── manage.py                  # Django management script
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## API Documentation

The application provides a RESTful API for programmatic access to timeline data.

### Endpoints

- `GET /api/projects/`: List all projects
- `POST /api/projects/`: Create a new project
- `GET /api/projects/{id}/`: Get project details
- `PUT /api/projects/{id}/`: Update project details
- `DELETE /api/projects/{id}/`: Delete a project
- `GET /api/projects/{id}/tasks/`: List all tasks for a project
- `POST /api/projects/{id}/tasks/`: Create a new task for a project

### Authentication

API requests require an authentication token that can be obtained via:
`POST /api/token/` with valid username and password.

## Testing

The application includes a comprehensive test suite covering all major functionality. To run the tests:

```bash
python manage.py test timeline_app
```

Tests include:
- Authentication tests
- Project CRUD operations
- Milestone management
- Collaboration features
- Gantt chart functionality
- Notification system
- Export capabilities
- Security and permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

--------

<div align="center">
  <p>Developed by Avishek Paul</p>
  <p>© 2025 All Rights Reserved</p>
</div>
