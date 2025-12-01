
import React, { useState, useEffect } from 'react';
import { JURISDICTIONS, REGULATORY_AREAS } from '../lib/constants.ts';
import { runResearch } from '../lib/gemini.ts';
import { Button } from './ui/Button.tsx';
import { Select } from './ui/Select.tsx';
import { Input } from './ui/Input.tsx';
import { Card } from './ui/Card.tsx';
import { Spinner } from './ui/Spinner.tsx';
import { MagnifyingGlassIcon } from './icons/Icons.tsx';
import { Jurisdiction } from '../types.ts';

const ResearchCenter: React.FC = () => {
    const [jurisdiction, setJurisdiction] = useState<Jurisdiction>(JURISDICTIONS[0].value as Jurisdiction);
    const [regulatoryArea, setRegulatoryArea] = useState(REGULATORY_AREAS[jurisdiction][0]?.value || '');
    const [topic, setTopic] = useState('Arm\'s Length Principle for services');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<string | null>(null);

    useEffect(() => {
        const availableAreas = REGULATORY_AREAS[jurisdiction];
        setRegulatoryArea(availableAreas[0]?.value || '');
    }, [jurisdiction]);

    const handleResearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) {
            setError('Research topic cannot be empty.');
            return;
        }
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await runResearch(topic, jurisdiction, regulatoryArea);
            setResult(response);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
            setError(`Failed to get research results: ${errorMessage}`);
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Research Center</h1>
                <p className="text-slate-600 mt-1">Find facts and regulatory insights with the Research Agent.</p>
            </header>

            <Card>
                <form onSubmit={handleResearch} className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <label htmlFor="jurisdiction" className="block text-sm font-medium text-slate-700 mb-1">
                                Jurisdiction
                            </label>
                            <Select
                                id="jurisdiction"
                                value={jurisdiction}
                                onChange={(e) => setJurisdiction(e.target.value as Jurisdiction)}
                                options={JURISDICTIONS}
                            />
                        </div>
                        <div>
                            <label htmlFor="regulatoryArea" className="block text-sm font-medium text-slate-700 mb-1">
                                Regulatory Area
                            </label>
                            <Select
                                id="regulatoryArea"
                                value={regulatoryArea}
                                onChange={(e) => setRegulatoryArea(e.target.value)}
                                options={REGULATORY_AREAS[jurisdiction]}
                                disabled={REGULATORY_AREAS[jurisdiction].length === 0}
                            />
                        </div>
                    </div>
                    <div>
                        <label htmlFor="topic" className="block text-sm font-medium text-slate-700 mb-1">
                            Research Topic
                        </label>
                        <Input
                            id="topic"
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="e.g., Commensurate with income standard for intangibles"
                        />
                    </div>
                    <div className="mt-6 flex justify-end">
                        <Button type="submit" disabled={isLoading || !regulatoryArea}>
                            {isLoading ? (
                                <>
                                    <Spinner className="mr-2" />
                                    Researching...
                                </>
                            ) : (
                                <>
                                    <MagnifyingGlassIcon className="mr-2 h-5 w-5" />
                                    Research
                                </>
                            )}
                        </Button>
                    </div>
                </form>
            </Card>

            {error && (
                <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}

            {isLoading && !result && (
                 <Card className="mt-6 p-6">
                    <div className="flex items-center justify-center flex-col text-slate-600">
                        <Spinner className="h-8 w-8 mb-4" />
                        <p className="font-medium">Agent is researching...</p>
                        <p className="text-sm text-slate-500">This may take a moment.</p>
                    </div>
                </Card>
            )}

            {result && (
                <Card className="mt-6">
                    <div className="p-6">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">Research Findings</h2>
                        <div className="prose prose-slate max-w-none" dangerouslySetInnerHTML={{ __html: result.replace(/\n/g, '<br />') }} />
                    </div>
                </Card>
            )}
        </div>
    );
};

export default ResearchCenter;
