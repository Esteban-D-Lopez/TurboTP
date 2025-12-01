
import React from 'react';
import { Mode } from '../types.ts';
import { BriefcaseIcon, DocumentTextIcon, ChatBubbleLeftRightIcon, BuildingLibraryIcon } from './icons/Icons.tsx';

interface SidebarProps {
    currentMode: Mode;
    setMode: (mode: Mode) => void;
}

const NavItem: React.FC<{
    icon: React.ReactNode;
    label: string;
    isActive: boolean;
    onClick: () => void;
}> = ({ icon, label, isActive, onClick }) => (
    <button
        onClick={onClick}
        aria-current={isActive ? 'page' : undefined}
        className={`flex items-center w-full px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
            isActive
                ? 'bg-slate-700 text-white'
                : 'text-slate-300 hover:bg-slate-600 hover:text-white'
        }`}
    >
        {icon}
        <span className="ml-3">{label}</span>
    </button>
);

const Sidebar: React.FC<SidebarProps> = ({ currentMode, setMode }) => {
    return (
        <aside className="flex flex-col w-64 bg-slate-800 text-white p-4">
            <div className="flex items-center mb-8">
                <BuildingLibraryIcon className="h-8 w-8 text-sky-400" />
                <h1 className="ml-3 text-xl font-bold tracking-tight">TP Workspace</h1>
            </div>
            <nav className="flex-1 space-y-2">
                <NavItem
                    icon={<BriefcaseIcon className="h-5 w-5" />}
                    label="Research Center"
                    isActive={currentMode === 'research'}
                    onClick={() => setMode('research')}
                />
                <NavItem
                    icon={<DocumentTextIcon className="h-5 w-5" />}
                    label="Document Composer"
                    isActive={currentMode === 'composer'}
                    onClick={() => setMode('composer')}
                />
                <NavItem
                    icon={<ChatBubbleLeftRightIcon className="h-5 w-5" />}
                    label="Agent Assistant"
                    isActive={currentMode === 'assistant'}
                    onClick={() => setMode('assistant')}
                />
            </nav>
            <div className="mt-auto text-center text-xs text-slate-400">
                <p>&copy; {new Date().getFullYear()} TP Agent Inc.</p>
                <p>Version 1.0.0</p>
            </div>
        </aside>
    );
};

export default Sidebar;
