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
- [Contributing](#contributing)
- [License](#license)

## Overview

Project Timeline Visualizer is a web-based tool designed to help project managers and team members visualize project schedules, track progress, and manage dependencies between tasks. The application provides an intuitive interface for creating, editing, and sharing project timelines with stakeholders.

## Features

- **Interactive Gantt Charts**: Visualize project schedules with drag-and-drop functionality
- **Milestone Tracking**: Set and monitor key project milestones
- **Dependency Management**: Define and visualize task dependencies
- **Resource Allocation**: Assign team members to tasks and track workload
- **Progress Tracking**: Update and monitor task completion status
- **Timeline Sharing**: Share project timelines with team members and stakeholders
- **Export Options**: Export timelines as PDF, PNG, or CSV
- **Responsive Design**: Access timelines on desktop and mobile devices
- **User Authentication**: Secure user login and project access control
- **Multiple Project Support**: Manage multiple project timelines simultaneously

## Screenshots

*Add screenshots of your application here*

## Technology Stack

- **Backend**: Django 4.x, Python 3.x
- **Frontend**: JavaScript, HTML5, CSS3
- **Data Visualization**: D3.js/Chart.js
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django Authentication System
- **Responsive Design**: Bootstrap/Custom CSS

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

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Usage

### Creating a New Project Timeline

1. Log in to the application
2. Click on "New Project" button
3. Enter project details (name, description, start date, end date)
4. Click "Create" to generate the timeline

### Adding Tasks to Timeline

1. Open your project timeline
2. Click "Add Task" button
3. Fill in task details (name, duration, start date, dependencies)
4. Click "Save" to add the task to the timeline

### Tracking Progress

1. Open your project timeline
2. Click on a task to update its status
3. Set the completion percentage and add notes if needed
4. Click "Update" to save changes

### Sharing Timeline

1. Open your project timeline
2. Click on "Share" button
3. Choose sharing options (view-only or edit)
4. Copy and share the generated link

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
│   ├── models.py              # Data models
│   ├── views.py               # View functions
│   ├── urls.py                # URL patterns
│   ├── forms.py               # Form definitions
│   ├── tests.py               # Test cases
│   └── admin.py               # Admin interface configuration
│
├── static/                    # Static files
│   ├── css/                   # CSS files
│   ├── js/                    # JavaScript files
│   └── img/                   # Image files
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   └── timeline/              # Timeline templates
│
├── media/                     # User-uploaded files
│
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by [Avishek Paul](https://github.com/avishekpaul1310)
