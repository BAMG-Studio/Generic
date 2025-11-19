import { Route } from "wouter";
import AppShell from "./components/Layout/AppShell";
import TitlePage from "./pages/TitlePage";
import MenuPage from "./pages/MenuPage";
import CharacterSelectPage from "./pages/CharacterSelectPage";
import CharacterStatsPage from "./pages/CharacterStatsPage";
import GamePage from "./pages/GamePage";
import EndingPage from "./pages/EndingPage";
import HowToPlayPage from "./pages/HowToPlayPage";

function App() {
  return (
    <AppShell>
      <Route path="/" component={TitlePage} />
      <Route path="/menu" component={MenuPage} />
      <Route path="/how-to-play" component={HowToPlayPage} />
      <Route path="/character-select" component={CharacterSelectPage} />
      <Route path="/character/:id" component={CharacterStatsPage} />
      <Route path="/game" component={GamePage} />
      <Route path="/ending" component={EndingPage} />
    </AppShell>
  );
}

export default App;
