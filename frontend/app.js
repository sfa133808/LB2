const apiBaseUrl = (window.API_BASE_URL || "http://localhost:8080").replace(/\/$/, "");

const usersTotal = document.getElementById("usersTotal");
const tasksTotal = document.getElementById("tasksTotal");
const openTasks = document.getElementById("openTasks");
const usersList = document.getElementById("usersList");
const tasksList = document.getElementById("tasksList");
const userForm = document.getElementById("userForm");
const taskForm = document.getElementById("taskForm");
const refreshUsersButton = document.getElementById("refreshUsers");
const refreshTasksButton = document.getElementById("refreshTasks");
const toast = document.getElementById("toast");

function setToast(message, kind = "ok") {
  toast.textContent = message;
  toast.className = `toast ${kind}`;
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || `Request failed (${response.status})`);
  }

  return response.json();
}

function renderUsers(items) {
  usersList.innerHTML = "";
  if (!items.length) {
    usersList.innerHTML = "<li>Noch keine Benutzer vorhanden.</li>";
    return;
  }

  for (const user of items) {
    const li = document.createElement("li");
    li.textContent = `#${user.id} ${user.name} (${user.email})`;
    usersList.appendChild(li);
  }
}

function renderTasks(items) {
  tasksList.innerHTML = "";
  if (!items.length) {
    tasksList.innerHTML = "<li>Noch keine Aufgaben vorhanden.</li>";
    return;
  }

  for (const task of items) {
    const li = document.createElement("li");
    li.textContent = `#${task.id} [User ${task.user_id}] ${task.title} - ${task.status}`;
    tasksList.appendChild(li);
  }
}

async function refreshAnalytics() {
  const data = await request("/analytics/summary");
  usersTotal.textContent = data.users_total;
  tasksTotal.textContent = data.tasks_total;
  openTasks.textContent = data.open_tasks;
}

async function refreshUsers() {
  const data = await request("/users");
  renderUsers(data.items || []);
}

async function refreshTasks() {
  const data = await request("/tasks");
  renderTasks(data.items || []);
}

async function bootstrap() {
  try {
    await Promise.all([refreshAnalytics(), refreshUsers(), refreshTasks()]);
    setToast("Dashboard geladen.");
  } catch (error) {
    setToast(`Fehler beim Laden: ${error.message}`, "error");
  }
}

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(userForm);

  try {
    await request("/users", {
      method: "POST",
      body: JSON.stringify({
        name: formData.get("name"),
        email: formData.get("email"),
      }),
    });

    userForm.reset();
    await Promise.all([refreshUsers(), refreshAnalytics()]);
    setToast("Benutzer erfolgreich erstellt.");
  } catch (error) {
    setToast(`Benutzer konnte nicht erstellt werden: ${error.message}`, "error");
  }
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(taskForm);

  try {
    await request("/tasks", {
      method: "POST",
      body: JSON.stringify({
        user_id: Number(formData.get("userId")),
        title: formData.get("title"),
        status: formData.get("status"),
      }),
    });

    taskForm.reset();
    await Promise.all([refreshTasks(), refreshAnalytics()]);
    setToast("Aufgabe erfolgreich erstellt.");
  } catch (error) {
    setToast(`Aufgabe konnte nicht erstellt werden: ${error.message}`, "error");
  }
});

refreshUsersButton.addEventListener("click", async () => {
  try {
    await refreshUsers();
    setToast("Benutzerliste aktualisiert.");
  } catch (error) {
    setToast(`Fehler: ${error.message}`, "error");
  }
});

refreshTasksButton.addEventListener("click", async () => {
  try {
    await refreshTasks();
    setToast("Aufgabenliste aktualisiert.");
  } catch (error) {
    setToast(`Fehler: ${error.message}`, "error");
  }
});

bootstrap();
