import { useState, useEffect, useCallback } from "react"

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL

interface PredefinedQuestion {
    id: string
    question: string
    category: string
    description: string
}

interface CandidateResult {
    candidate_id: string
    name: string
    party_id: string
    constituency_id: string
    state_id: string
    status: string
    relevance_score: number | null
    document: string
}

interface QuestionAnswer {
    success: boolean
    question: string
    question_id?: string
    category?: string
    answer: string
    candidates: CandidateResult[]
    total_results: number
    error?: string
}

export function useQuestions() {
    const [questions, setQuestions] = useState<PredefinedQuestion[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchQuestions = async () => {
            try {
                setLoading(true)
                const response = await fetch(`${API_BASE_URL}/questions`)
                const data = await response.json()
                if (data.success) {
                    setQuestions(data.data.questions || [])
                    setError(null)
                } else {
                    setError(data.error || "Failed to load questions")
                }
            } catch (err) {
                setError("Error connecting to API")
                console.error("Error fetching questions:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchQuestions()
    }, [])

    return { questions, loading, error }
}

export function useAskQuestion() {
    const [answer, setAnswer] = useState<QuestionAnswer | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const askQuestion = useCallback(
        async (
            question: string,
            candidateId?: string,
            nResults: number = 5
        ) => {
            try {
                setLoading(true)
                setError(null)

                const response = await fetch(`${API_BASE_URL}/questions/ask`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        question,
                        candidate_id: candidateId,
                        n_results: nResults,
                    }),
                })

                const data = await response.json()

                if (data.success) {
                    setAnswer(data)
                    setError(null)
                } else {
                    setError(data.error || "Failed to get answer")
                    setAnswer(null)
                }

                return data
            } catch (err) {
                const errorMessage = "Error connecting to API"
                setError(errorMessage)
                console.error("Error asking question:", err)
                return { success: false, error: errorMessage }
            } finally {
                setLoading(false)
            }
        },
        []
    )

    const askPredefinedQuestion = useCallback(
        async (
            questionId: string,
            candidateId?: string,
            nResults: number = 5
        ) => {
            try {
                setLoading(true)
                setError(null)

                let url = `${API_BASE_URL}/questions/${questionId}/answer?n_results=${nResults}`
                if (candidateId) {
                    url += `&candidate_id=${candidateId}`
                }

                const response = await fetch(url)
                const data = await response.json()

                if (data.success) {
                    setAnswer(data)
                    setError(null)
                } else {
                    setError(data.error || "Failed to get answer")
                    setAnswer(null)
                }

                return data
            } catch (err) {
                const errorMessage = "Error connecting to API"
                setError(errorMessage)
                console.error("Error asking predefined question:", err)
                return { success: false, error: errorMessage }
            } finally {
                setLoading(false)
            }
        },
        []
    )

    const clearAnswer = useCallback(() => {
        setAnswer(null)
        setError(null)
    }, [])

    return { answer, loading, error, askQuestion, askPredefinedQuestion, clearAnswer }
}
