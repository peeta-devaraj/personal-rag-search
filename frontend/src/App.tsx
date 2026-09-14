import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AskPage from "./pages/AskPage";
import EvalDashboardPage from "./pages/EvalDashboardPage";
import LibraryPage from "./pages/LibraryPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/library" replace />} />
        <Route path="library" element={<LibraryPage />} />
        <Route path="ask" element={<AskPage />} />
        <Route path="eval" element={<EvalDashboardPage />} />
      </Route>
    </Routes>
  );
}
