
import React, { useState, useRef, useEffect } from 'react';
import { JURISDICTIONS, REPORT_SECTIONS, DATA_REQUIREMENTS, FUNCTIONAL_ANALYSIS_SUBSECTIONS } from '../lib/constants.ts';
import { AVAILABLE_DATA_SOURCES } from '../lib/dataSources.ts';
import { runDrafting, runWebSearch } from '../lib/gemini.ts';
import { Button } from './ui/Button.tsx';
import { Select } from './ui/Select.tsx';
import { Textarea } from './ui/Textarea.tsx';
import { Card } from './ui/Card.tsx';
import { Spinner } from './ui/Spinner.tsx';
import { Input } from './ui/Input.tsx';
import { DocumentPlusIcon, ArrowUpOnSquareIcon, CheckCircleIcon, CircleIcon, GlobeAltIcon, MagnifyingGlassIcon } from './icons/Icons.tsx';
import { ReportSection, FunctionalAnalysisSubSection, WebSource } from '../types.ts';

const DocumentComposer: React.FC = () => {
    const [regulatoryBody, setRegulatoryBody] = useState(JURISDICTIONS[0].value);
    const [reportSection, setReportSection] = useState<ReportSection>(REPORT_SECTIONS[0].value as ReportSection);
    const [faSubSection, setFaSubSection] = useState<FunctionalAnalysisSubSection>(FUNCTIONAL_ANALYSIS_SUBSECTIONS[0].value as FunctionalAnalysisSubSection);
    
    // Data Sources State
    const [selectedData, setSelectedData] = useState<{ [key: string]: boolean }>({});
    const [customData, setCustomData] = useState<{ [key: string]: { content: string; name: string } }>({});
    const [textareaData, setTextareaData] = useState<{ [key: string]: string }>({});

    // Web Search State
    const [searchQuery, setSearchQuery] = useState('');
    const [searchDomains, setSearchDomains] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [webSources, setWebSources] = useState<WebSource[]>([]);
    const [webSearchSummary, setWebSearchSummary] = useState('');
    const [selectedWebSources, setSelectedWebSources] = useState<{ [key: string]: boolean }>({});

    // General State
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [draftContent, setDraftContent] = useState<string>('');
    const fileInputRefs = useRef<{ [key: string]: HTMLInputElement | null }>({});

    useEffect(() => {
        setSelectedData({});
        setCustomData({});
        setTextareaData({});
        setWebSources([]);
        setWebSearchSummary('');
        setSelectedWebSources({});
        setError(null);
    }, [reportSection, faSubSection]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, id: string) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setCustomData(prev => ({
                    ...prev,
                    [id]: { content: event.target?.result as string, name: file.name }
                }));
            };
            reader.readAsText(file);
        }
    };

    const handleWebSearch = async () => {
        if (!searchQuery.trim()) return;
        setIsSearching(true);
        setError(null);
        setWebSources([]);
        setWebSearchSummary('');
        setSelectedWebSources({});
        try {
            const result = await runWebSearch(searchQuery, searchDomains);
            setWebSources(result.sources);
            setWebSearchSummary(result.summary);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown web search error occurred.');
        } finally {
            setIsSearching(false);
        }
    };

    const handleGenerateDraft = async () => {
        const finalGroundingData: { [key: string]: string } = {};

        AVAILABLE_DATA_SOURCES.forEach(source => {
            if (selectedData[source.id]) finalGroundingData[source.name] = source.content;
        });

        Object.entries(customData).forEach(([id, data]) => {
            if (data.content) finalGroundingData[`Custom Upload: ${data.name}`] = data.content;
        });

        Object.entries(textareaData).forEach(([id, content]) => {
            if (content) {
                const label = DATA_REQUIREMENTS[reportSection]?.textarea?.label || id;
                finalGroundingData[label] = content;
            }
        });

        const selectedWebSourceTitles = webSources
            .filter(source => selectedWebSources[source.id])
            .map(source => source.title);
        
        if (selectedWebSourceTitles.length > 0 && webSearchSummary) {
            finalGroundingData[`Web Search Summary (Sources: ${selectedWebSourceTitles.join(', ')})`] = webSearchSummary;
        }

        if (Object.keys(finalGroundingData).length === 0 && reportSection !== 'Executive Summary') {
             setError(`Please select, upload, or add at least one data source for the '${reportSection}' section.`);
             return;
        }

        setIsLoading(true);
        setError(null);
        setDraftContent('');

        try {
            const response = await runDrafting(
                regulatoryBody,
                reportSection,
                finalGroundingData,
                reportSection === 'Functional Analysis' ? faSubSection : undefined
            );
            setDraftContent(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        } finally {
            setIsLoading(false);
        }
    };

    const renderDataInputs = () => {
        const requirements = DATA_REQUIREMENTS[reportSection];
        if (!requirements) return <p className="text-sm text-slate-500">No data sources applicable for this section.</p>;

        return (
            <div className="space-y-3">
                {requirements.predefined?.map(sourceId => {
                    const source = AVAILABLE_DATA_SOURCES.find(s => s.id === sourceId);
                    if (!source) return null;
                    const isSelected = !!selectedData[source.id];
                    return (
                        <button key={source.id} onClick={() => setSelectedData(prev => ({ ...prev, [source.id]: !prev[source.id] }))} className={`w-full text-left p-3 border rounded-lg flex items-center transition-colors ${isSelected ? 'bg-sky-50 border-sky-300' : 'bg-white hover:bg-slate-50'}`}>
                            {isSelected ? <CheckCircleIcon className="h-5 w-5 text-sky-600 mr-3 flex-shrink-0" /> : <CircleIcon className="h-5 w-5 text-slate-400 mr-3 flex-shrink-0" />}
                            <span className="text-sm font-medium text-slate-700 truncate" title={source.name}>{source.name}</span>
                        </button>
                    );
                })}
                {requirements.custom && (
                    <div className="p-3 border rounded-lg bg-slate-50/50">
                        <label className="block text-sm font-medium text-slate-700 mb-2">{requirements.custom.label}</label>
                        <input type="file" ref={el => fileInputRefs.current[requirements.custom.id] = el} onChange={(e) => handleFileChange(e, requirements.custom.id)} className="hidden" accept=".csv,.txt,.json,.md" />
                        <Button variant="outline" onClick={() => fileInputRefs.current[requirements.custom.id]?.click()} className="w-full">
                            <ArrowUpOnSquareIcon className="mr-2 h-5 w-5" /> Upload Custom File
                        </Button>
                        {customData[requirements.custom.id]?.name && <p className="text-xs text-slate-500 mt-2 truncate" title={customData[requirements.custom.id].name}>File: {customData[requirements.custom.id].name}</p>}
                    </div>
                )}
                {requirements.textarea && (
                     <div className="pt-2">
                        <label className="block text-sm font-medium text-slate-700 mb-1">{requirements.textarea.label}</label>
                        <Textarea value={textareaData[requirements.textarea.id] || ''} onChange={(e) => setTextareaData(prev => ({...prev, [requirements.textarea.id]: e.target.value}))} rows={4} placeholder={`Paste ${requirements.textarea.label} here...`} />
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="max-w-7xl mx-auto h-full flex flex-col">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Document Composer</h1>
                <p className="text-slate-600 mt-1">Generate compliant TP documentation with the Drafting Agent.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
                <div className="lg:col-span-1 flex flex-col gap-6 overflow-y-auto pr-2">
                    <Card>
                        <div className="p-6">
                            <h3 className="font-semibold text-lg text-slate-800 mb-4">1. Select Scope</h3>
                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="regulatoryBody" className="block text-sm font-medium text-slate-700 mb-1">Regulatory Body</label>
                                    <Select id="regulatoryBody" value={regulatoryBody} onChange={(e) => setRegulatoryBody(e.target.value)} options={JURISDICTIONS} />
                                </div>
                                <div>
                                    <label htmlFor="reportSection" className="block text-sm font-medium text-slate-700 mb-1">Report Section</label>
                                    <Select id="reportSection" value={reportSection} onChange={(e) => setReportSection(e.target.value as ReportSection)} options={REPORT_SECTIONS} />
                                </div>
                                {reportSection === 'Functional Analysis' && (
                                    <div>
                                        <label htmlFor="faSubSection" className="block text-sm font-medium text-slate-700 mb-1">Functional Analysis Type</label>
                                        <Select id="faSubSection" value={faSubSection} onChange={(e) => setFaSubSection(e.target.value as FunctionalAnalysisSubSection)} options={FUNCTIONAL_ANALYSIS_SUBSECTIONS} />
                                    </div>
                                )}
                            </div>
                        </div>
                    </Card>
                    <Card>
                        <div className="p-6">
                            <h3 className="font-semibold text-lg text-slate-800 mb-4">2. Data Sources</h3>
                            {renderDataInputs()}
                            <div className="mt-4 pt-4 border-t border-slate-200">
                                <h4 className="font-medium text-slate-800 mb-3 flex items-center"><GlobeAltIcon className="h-5 w-5 mr-2 text-slate-500" /> Add Sources from Web</h4>
                                <div className="space-y-3">
                                    <Input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search query..." />
                                    <Input value={searchDomains} onChange={e => setSearchDomains(e.target.value)} placeholder="Optional: irs.gov, oecd.org..." />
                                    <Button variant="outline" onClick={handleWebSearch} disabled={isSearching || !searchQuery.trim()} className="w-full">
                                        {isSearching ? <><Spinner className="mr-2" />Searching...</> : <><MagnifyingGlassIcon className="mr-2 h-5 w-5" />Search</>}
                                    </Button>
                                </div>
                                {isSearching && <div className="text-center p-4"><Spinner /></div>}
                                {webSources.length > 0 && (
                                    <div className="mt-4 space-y-2 max-h-48 overflow-y-auto">
                                        <p className="text-sm font-medium text-slate-600">Select relevant sources:</p>
                                        {webSources.map(source => {
                                            const isSelected = !!selectedWebSources[source.id];
                                            return (
                                                <button key={source.id} onClick={() => setSelectedWebSources(prev => ({ ...prev, [source.id]: !prev[source.id] }))} className={`w-full text-left p-2 border rounded-md flex items-start transition-colors ${isSelected ? 'bg-sky-50 border-sky-300' : 'bg-white hover:bg-slate-50'}`}>
                                                    {isSelected ? <CheckCircleIcon className="h-4 w-4 text-sky-600 mr-2 mt-0.5 flex-shrink-0" /> : <CircleIcon className="h-4 w-4 text-slate-400 mr-2 mt-0.5 flex-shrink-0" />}
                                                    <div className="overflow-hidden">
                                                        <p className="text-xs font-medium text-slate-700 truncate" title={source.title}>{source.title}</p>
                                                        <p className="text-xs text-slate-500 truncate" title={source.uri}>{source.uri}</p>
                                                    </div>
                                                </button>
                                            )
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    </Card>
                    <Card>
                        <div className="p-6">
                            <h3 className="font-semibold text-lg text-slate-800 mb-4">3. Generate Draft</h3>
                            <Button onClick={handleGenerateDraft} disabled={isLoading} className="w-full">
                                {isLoading ? (<><Spinner className="mr-2" />Generating...</>) : (<><DocumentPlusIcon className="mr-2 h-5 w-5" />Generate Draft</>)}
                            </Button>
                        </div>
                    </Card>
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg" role="alert">
                            <strong className="font-bold">Error: </strong>
                            <span className="block sm:inline">{error}</span>
                        </div>
                    )}
                </div>

                <div className="lg:col-span-2 flex flex-col">
                    <Card className="flex-1 flex flex-col">
                        <div className="p-6 border-b border-slate-200">
                            <h3 className="font-semibold text-lg text-slate-800">Generated Draft: <span className="font-normal text-slate-600">{reportSection === 'Functional Analysis' ? `Functional Analysis - ${faSubSection}` : reportSection}</span></h3>
                        </div>
                        <div className="flex-1 p-1 bg-slate-50 rounded-b-lg">
                            <Textarea value={isLoading ? 'Drafting Agent is preparing the document...' : draftContent} onChange={(e) => setDraftContent(e.target.value)} placeholder="Your generated document will appear here..." className="h-full w-full resize-none border-0 focus:ring-0 bg-slate-50" readOnly={isLoading} />
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default DocumentComposer;
