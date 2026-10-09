import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import Container from "@mui/material/Container";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import DeleteIcon from "@mui/icons-material/Delete";
import { createTask, deleteTask, getTasks, setTaskCompleted } from "./api.js";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  async function loadTasks() {
    setLoading(true);
    setError("");
    try {
      setTasks(await getTasks());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  async function handleAdd(event) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    setSaving(true);
    setError("");
    try {
      const task = await createTask(trimmed);
      setTasks((current) => [task, ...current]);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle(task) {
    setBusyId(task.id);
    setError("");
    try {
      const updated = await setTaskCompleted(task.id, !task.completed);
      setTasks((current) => current.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(task) {
    setBusyId(task.id);
    setError("");
    try {
      await deleteTask(task.id);
      setTasks((current) => current.filter((t) => t.id !== task.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  const remaining = tasks.filter((t) => !t.completed).length;

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 3, sm: 6 } }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Task Manager
      </Typography>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
        <Stack
          component="form"
          onSubmit={handleAdd}
          direction={{ xs: "column", sm: "row" }}
          spacing={1.5}
        >
          <TextField
            label="New task"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            size="small"
            fullWidth
            disabled={saving}
            slotProps={{ htmlInput: { maxLength: 200 } }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={saving || !title.trim()}
            sx={{ flexShrink: 0 }}
          >
            {saving ? "Adding…" : "Add task"}
          </Button>
        </Stack>

        {error && (
          <Alert
            severity="error"
            sx={{ mt: 2 }}
            onClose={() => setError("")}
            action={
              tasks.length === 0 && !loading ? (
                <Button color="inherit" size="small" onClick={loadTasks}>
                  Retry
                </Button>
              ) : undefined
            }
          >
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress aria-label="Loading tasks" />
          </Box>
        ) : tasks.length === 0 ? (
          !error && (
            <Typography sx={{ mt: 3, textAlign: "center", color: "text.secondary" }}>
              No tasks yet. Add your first one above.
            </Typography>
          )
        ) : (
          <>
            <List sx={{ mt: 1 }}>
              {tasks.map((task) => (
                <ListItem
                  key={task.id}
                  disableGutters
                  divider
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label={`Delete ${task.title}`}
                      onClick={() => handleDelete(task)}
                      disabled={busyId === task.id}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <Checkbox
                    edge="start"
                    checked={task.completed}
                    onChange={() => handleToggle(task)}
                    disabled={busyId === task.id}
                    slotProps={{
                      input: { "aria-label": `Mark ${task.title} as completed` },
                    }}
                  />
                  <ListItemText
                    primary={task.title}
                    sx={{
                      overflowWrap: "anywhere",
                      textDecoration: task.completed ? "line-through" : "none",
                      color: task.completed ? "text.secondary" : "text.primary",
                    }}
                  />
                </ListItem>
              ))}
            </List>
            <Typography variant="body2" sx={{ mt: 1, color: "text.secondary" }}>
              {remaining} of {tasks.length} remaining
            </Typography>
          </>
        )}
      </Paper>
    </Container>
  );
}
