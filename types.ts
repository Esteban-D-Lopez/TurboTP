
export type Mode = 'research' | 'composer' | 'assistant';

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}

export type Jurisdiction = 'US' | 'OECD';

export type ReportSection = 'Executive Summary' | 'Company Analysis' | 'Industry Analysis' | 'Functional Analysis' | 'Economic Analysis';

export type FunctionalAnalysisSubSection = 'Functions' | 'Assets' | 'Risks';

export interface GroundingData {
    [key: string]: {
        content: string;
        name: string; // filename or 'Text Input'
    }
}

export interface WebSource {
    id: string;
    title: string;
    uri: string;
}
