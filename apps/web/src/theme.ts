import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#002f6c" },
    secondary: { main: "#00a3e0" },
    error: { main: "#c8102e" },
    success: { main: "#00843d" },
    warning: { main: "#ffb81c" },
    background: { default: "#f4f7fb" }
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: ["Inter", "Segoe UI", "Arial", "sans-serif"].join(","),
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 }
  }
});
