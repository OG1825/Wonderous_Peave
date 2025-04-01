// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/peach-brawl/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Tab Switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        // Update active tab button
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update active tab content
        const tabId = button.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            if (content.id === tabId) {
                content.classList.add('active');
            }
        });
    });
});

// API endpoint - Update this to your actual Render.com URL
const API_URL = 'https://canvas-calendar-api.onrender.com/api/all';

// DOM elements
const assignmentsList = document.getElementById('assignments-list');
const scheduleList = document.getElementById('schedule-list');

// Format date for display
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
    }
}

// Display assignments
function displayAssignments(assignments) {
    if (!assignments || assignments.length === 0) {
        assignmentsList.innerHTML = '<div class="text-center text-muted">No upcoming assignments</div>';
        return;
    }

    const html = assignments.map(assignment => `
        <div class="assignment-item">
            <div class="assignment-date">
                <i class="bi bi-calendar"></i> ${formatDate(assignment.due_date)}
            </div>
            <div class="assignment-course">
                <i class="bi bi-book"></i> ${assignment.course}
            </div>
            <div class="assignment-name">
                <i class="bi bi-pencil"></i> ${assignment.name}
            </div>
        </div>
    `).join('');

    assignmentsList.innerHTML = html;
}

// Display schedule
function displaySchedule(schedule) {
    if (!schedule || schedule.length === 0) {
        scheduleList.innerHTML = '<div class="text-center text-muted">No courses found</div>';
        return;
    }

    const html = schedule.map(course => `
        <div class="list-group-item schedule-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${course.name}</h6>
                    <div class="course-code">${course.code}</div>
                </div>
                <span class="badge bg-success">${course.term}</span>
            </div>
        </div>
    `).join('');

    scheduleList.innerHTML = html;
}

// Fetch data from API
async function fetchData() {
    try {
        console.log('Fetching data from:', API_URL);
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        
        if (!data || (!data.assignments && !data.schedule)) {
            throw new Error('Invalid data format received from API');
        }
        
        displayAssignments(data.assignments);
        displaySchedule(data.schedule);
    } catch (error) {
        console.error('Error fetching data:', error);
        assignmentsList.innerHTML = `
            <div class="error">
                <i class="bi bi-exclamation-triangle"></i>
                Failed to load assignments. Please check the console for details.
            </div>`;
        scheduleList.innerHTML = `
            <div class="error">
                <i class="bi bi-exclamation-triangle"></i>
                Failed to load schedule. Please check the console for details.
            </div>`;
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, fetching data...');
    fetchData();
});

// Refresh data every 5 minutes
setInterval(fetchData, 5 * 60 * 1000); 
