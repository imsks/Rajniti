'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

// Types for our API data
interface Election {
    id: string;
    name: string;
    year: number;
    type: string;
    statistics: {
        total_candidates: number;
        total_constituencies: number;
        total_parties: number;
        total_winners: number;
    };
}

interface Candidate {
    id: string;
    name: string;
    party_name: string;
    party_short_name: string;
    constituency_name: string;
    status: string;
    image_url?: string;
}

interface Party {
    party_name: string;
    party_short_name: string;
    total_seats?: number;
    party_symbol?: string;
}

// API Base URL - configurable via environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export default function Dashboard() {
    const [selectedElection, setSelectedElection] = useState<Election | null>(null);
    const [candidates, setCandidates] = useState<Candidate[]>([]);
    const [parties, setParties] = useState<Party[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [searchLoading, setSearchLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch elections on component mount
    useEffect(() => {
        fetchElections();
    }, []);

    // Fetch parties when election is selected
    useEffect(() => {
        if (selectedElection) {
            fetchParties(selectedElection.id);
        }
    }, [selectedElection]);

    const fetchElections = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/elections`);
            const data = await response.json();
            if (data.success) {
                if (data.data.length > 0) {
                    setSelectedElection(data.data[0]);
                }
            } else {
                setError('Failed to load elections');
            }
        } catch (err) {
            setError('Error connecting to API. Make sure the backend is running on port 8080.');
            console.error('Error fetching elections:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchParties = async (electionId: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/elections/${electionId}/parties`);
            const data = await response.json();
            if (data.success && data.data.parties) {
                // Map the API response to our Party interface
                interface PartyApiResponse {
                    name: string;
                    short_name: string;
                    seats_won: number;
                    symbol: string;
                }
                const mappedParties = data.data.parties.slice(0, 10).map((p: PartyApiResponse) => ({
                    party_name: p.name,
                    party_short_name: p.short_name,
                    total_seats: p.seats_won,
                    party_symbol: p.symbol
                }));
                setParties(mappedParties);
            }
        } catch (err) {
            console.error('Error fetching parties:', err);
        }
    };

    const searchCandidates = async (query: string) => {
        if (!query.trim()) {
            setCandidates([]);
            return;
        }

        try {
            setSearchLoading(true);
            const response = await fetch(
                `${API_BASE_URL}/candidates/search?q=${encodeURIComponent(query)}&limit=10`
            );
            const data = await response.json();
            if (data.success) {
                setCandidates(data.data.candidates || []);
            }
        } catch (err) {
            console.error('Error searching candidates:', err);
        } finally {
            setSearchLoading(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        searchCandidates(searchQuery);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent"></div>
                    <p className="mt-4 text-gray-600 font-semibold">Loading Election Data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="text-red-500 text-3xl">⚠️</div>
                        <h2 className="text-xl font-bold text-gray-900">Connection Error</h2>
                    </div>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={fetchElections}
                        className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50">
            {/* Header */}
            <header className="border-b border-orange-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="text-2xl font-bold">🗳️</div>
                            <span className="text-xl font-bold text-gray-900">Rajniti Dashboard</span>
                        </div>
                        <Link
                            href="/"
                            className="text-gray-600 hover:text-orange-600 transition-colors font-semibold"
                        >
                            ← Home
                        </Link>
                    </div>
                </div>
            </header>

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
                {/* Election Overview Section */}
                {selectedElection && (
                    <div className="mb-8">
                        <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-8 text-white shadow-lg">
                            <h1 className="text-3xl font-bold mb-2">{selectedElection.name}</h1>
                            <p className="text-orange-100 mb-6">Year: {selectedElection.year} | Type: {selectedElection.type}</p>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                                    <div className="text-3xl font-bold">{selectedElection.statistics.total_constituencies}</div>
                                    <div className="text-orange-100 text-sm mt-1">Constituencies</div>
                                </div>
                                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                                    <div className="text-3xl font-bold">{selectedElection.statistics.total_candidates.toLocaleString()}</div>
                                    <div className="text-orange-100 text-sm mt-1">Candidates</div>
                                </div>
                                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                                    <div className="text-3xl font-bold">{selectedElection.statistics.total_parties}</div>
                                    <div className="text-orange-100 text-sm mt-1">Parties</div>
                                </div>
                                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                                    <div className="text-3xl font-bold">{selectedElection.statistics.total_winners}</div>
                                    <div className="text-orange-100 text-sm mt-1">Winners</div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Search Section */}
                <div className="mb-8">
                    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">🔍 Search Candidates</h2>
                        <form onSubmit={handleSearch} className="flex gap-2">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search by candidate name..."
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                            />
                            <button
                                type="submit"
                                disabled={searchLoading}
                                className="bg-orange-500 hover:bg-orange-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {searchLoading ? 'Searching...' : 'Search'}
                            </button>
                        </form>

                        {/* Search Results */}
                        {candidates.length > 0 && (
                            <div className="mt-6 space-y-3">
                                <h3 className="font-semibold text-gray-700">Results ({candidates.length})</h3>
                                <div className="grid gap-3">
                                    {candidates.map((candidate) => (
                                        <div
                                            key={candidate.id}
                                            className="bg-gradient-to-r from-gray-50 to-white rounded-lg p-4 border border-gray-200 hover:border-orange-300 transition-colors"
                                        >
                                            <div className="flex items-center gap-4">
                                                {candidate.image_url && (
                                                    // eslint-disable-next-line @next/next/no-img-element
                                                    <img
                                                        src={candidate.image_url}
                                                        alt={candidate.name}
                                                        className="w-16 h-16 rounded-full object-cover border-2 border-orange-200"
                                                        onError={(e) => {
                                                            (e.target as HTMLImageElement).style.display = 'none';
                                                        }}
                                                    />
                                                )}
                                                <div className="flex-1">
                                                    <h4 className="font-bold text-gray-900">{candidate.name}</h4>
                                                    <p className="text-sm text-gray-600">
                                                        {candidate.party_name} ({candidate.party_short_name})
                                                    </p>
                                                    <p className="text-sm text-gray-500">
                                                        {candidate.constituency_name}
                                                    </p>
                                                </div>
                                                <div>
                                                    <span
                                                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                                            candidate.status === 'WON'
                                                                ? 'bg-green-100 text-green-700'
                                                                : 'bg-gray-100 text-gray-600'
                                                        }`}
                                                    >
                                                        {candidate.status}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {searchQuery && !searchLoading && candidates.length === 0 && (
                            <div className="mt-6 text-center text-gray-500">
                                No candidates found for &quot;{searchQuery}&quot;
                            </div>
                        )}
                    </div>
                </div>

                {/* Parties Section */}
                {parties.length > 0 && (
                    <div className="mb-8">
                        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                            <h2 className="text-2xl font-bold text-gray-900 mb-4">🎯 Major Parties</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {parties.map((party, index) => (
                                    <div
                                        key={index}
                                        className="bg-gradient-to-br from-orange-50 to-white rounded-lg p-4 border border-orange-200 hover:border-orange-400 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold">
                                                {party.party_short_name.charAt(0)}
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="font-bold text-gray-900 text-sm">
                                                    {party.party_name}
                                                </h4>
                                                <p className="text-xs text-gray-600">
                                                    {party.party_short_name}
                                                    {party.total_seats && ` • ${party.total_seats} seats`}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Footer Info */}
                <div className="text-center py-8">
                    <div className="inline-flex items-center gap-2 bg-white rounded-full px-6 py-3 shadow-md border border-gray-200">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-sm text-gray-600">
                            Data powered by Rajniti Election API
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
