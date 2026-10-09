// Small wrapper around fetch for the Flask task API.
async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(data?.error || `Request failed (${res.status}).`);
  }
  return data;
}

export const getTasks = () => request("/api/tasks");

export const createTask = (title) =>
  request("/api/tasks", { method: "POST", body: JSON.stringify({ title }) });

export const setTaskCompleted = (id, completed) =>
  request(`/api/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ completed }),
  });

export const deleteTask = (id) =>
  request(`/api/tasks/${id}`, { method: "DELETE" });
