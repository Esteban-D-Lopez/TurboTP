
import React,
{
  useState
} from 'react';
import Sidebar from './components/Sidebar.tsx';
import ResearchCenter from './components/ResearchCenter.tsx';
import DocumentComposer from './components/DocumentComposer.tsx';
import AgentAssistant from './components/AgentAssistant.tsx';
import {
  Mode
} from './types.ts';

const App: React.FC = () => {
  const [mode, setMode] = useState < Mode > ('research');

  const renderContent = () => {
    switch (mode) {
      case 'research':
        return < ResearchCenter / > ;
      case 'composer':
        return < DocumentComposer / > ;
      case 'assistant':
        return < AgentAssistant / > ;
      default:
        return < ResearchCenter / > ;
    }
  };

  return ( <
    div className = "flex h-screen bg-slate-100 font-sans" >
    <
    Sidebar currentMode = {
      mode
    }
    setMode = {
      setMode
    }
    /> <
    main className = "flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8" > {
      renderContent()
    } <
    /main> <
    /div>
  );
};

export default App;
