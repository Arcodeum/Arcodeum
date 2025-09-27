// frontend/app.js

const API_BASE_URL = 'http://127.0.0.1:8000';

// --- View References ---
const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const userInfo = document.getElementById('user-info');
const loginButton = document.getElementById('login-button');
const webhookInfoView = document.getElementById('webhook-info-view');

// --- Event Listeners ---
loginButton.addEventListener('click', () => {
    // Redirect to backend which will redirect to GitHub
    window.location.href = `${API_BASE_URL}/auth/github`;
});

// --- Main App Logic ---
document.addEventListener('DOMContentLoaded', () => {
    // Check for our temporary "token" (the username) in the URL
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (token) {
        // We "logged in"
        localStorage.setItem('arcodeum_token', token);
        // Clean the URL
        window.history.replaceState({}, document.title, "/");
        showDashboard(token);
    } else if (localStorage.getItem('arcodeum_token')) {
        // We are already logged in
        showDashboard(localStorage.getItem('arcodeum_token'));
    } else {
        // We need to log in
        showLogin();
    }
});

function showLogin() {
    loginView.style.display = 'block';
    dashboardView.style.display = 'none';
    userInfo.innerHTML = '';
}

function showDashboard(username) {
    loginView.style.display = 'none';
    dashboardView.style.display = 'block';
    userInfo.innerHTML = `<span>Logged in as: <strong>${username}</strong></span> <button id="logout-button">Logout</button>`;
    
    document.getElementById('logout-button').addEventListener('click', () => {
        localStorage.removeItem('arcodeum_token');
        showLogin();
    });
    
    // In a real app, you would fetch and display the user's projects here.
    // We'll leave the project creation and webhook display logic for the next step.
    setupProjectCreation();
}

function setupProjectCreation() {
    const createButton = document.getElementById('create-project-button');
    createButton.addEventListener('click', async () => {
        // In a real app, this would call a backend endpoint to save the project.
        // For now, let's just generate and display the webhook info.
        const repoUrl = document.getElementById('repo-url').value;
        if (!repoUrl) {
            alert('Please enter a repository URL.');
            return;
        }

        // Mock a project ID for the URL
        const mockProjectId = Math.floor(Math.random() * 1000);
        const webhookUrl = `${API_BASE_URL}/webhooks/github?project_id=${mockProjectId}`;

        // Display the webhook setup instructions
        document.getElementById('webhook-url').value = webhookUrl;
        document.getElementById('repo-link').href = repoUrl;
        document.getElementById('repo-link').textContent = repoUrl.split('/').slice(-2).join('/');
        
        dashboardView.style.display = 'none'; // Hide the dashboard
        webhookInfoView.style.display = 'block';
    });
}