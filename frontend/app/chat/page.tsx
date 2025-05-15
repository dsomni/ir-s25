"use client";

import { useEffect, useState } from "react";
import styles from "./chat.module.css";
import axios from "axios";
import { useRef } from "react";
import Dropdown from '@/components/Dropdown';
import BackLink from "@/components/BackLink";
import { indexerMap, Proposal, THINK_REGEX } from "@/constants";




export default function ChatPage() {
    const [prompt, setPrompt] = useState("");
    const [kValue, setKValue] = useState("5");
    const [proposals, setProposals] = useState<Proposal[]>([]);
    const [showValues, setShowValues] = useState(false);
    const [model, setModel] = useState("");
    const [modelList, setModelList] = useState<string[]>([]);
    const [indexer, setIndexer] = useState("");
    const [indexerList, setIndexerList] = useState<string[]>([]);
    const [messages, setMessages] = useState<{ role: string; content: string; time: number | undefined }[]>([]);
    const [streamingResponse, setStreamingResponse] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement | null>(null);
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);

    // Resize textarea height dynamically
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [prompt]);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, streamingResponse]);

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await axios.get(`${process.env.API_URL}/models`);
                setModelList(response.data || []);
                if (response.data.length > 0) setModel(response.data[0]); // default to first
            } catch (err) {
                console.error("Failed to fetch models", err);
                setError("Unable to load model list");
            }
        };
        const fetchIndexers = async () => {
            try {
                const response = await axios.get(`${process.env.API_URL}/indexers`);
                setIndexerList(response.data || []);
                if (response.data.length > 0) setIndexer(response.data[0]); // default to first
            } catch (err) {
                console.error("Failed to fetch indexers", err);
                setError("Unable to load indexer list");
            }
        };


        fetchIndexers();
        fetchModels();
    }, []);

    const handleSubmit = async () => {
        if (!prompt.trim() || isLoading) return;
        setError("");
        setIsLoading(true);

        // Append user message
        setMessages(prev => [...prev, { role: "user", content: prompt, time: undefined }]);
        setStreamingResponse("");
        setError("");
        const currentPrompt = prompt;
        setPrompt("");
        let current = "";

        try {
            const currentModel = model;
            const response = await fetch(
                `${process.env.API_URL}/chat?prompt=${encodeURIComponent(currentPrompt)}&k=${kValue}&model=${model}&indexer=${indexer}`,
            );

            if (!response.ok || !response.body) {
                throw new Error("Failed to connect to backend or response body is missing.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let elapsedTime: number | undefined = undefined

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const messages = chunk.split('\n\n').filter(m => m.trim() !== '');
                console.log(messages)
                for (const message of messages) {
                    try {
                        const parsed = JSON.parse(message);

                        switch (parsed.type) {
                            case 'proposals':
                                setProposals(parsed.data);
                                break;
                            case 'chunk':
                                current += parsed.data;
                                setStreamingResponse(current);
                                break;
                            case 'complete':
                                setStreamingResponse("");
                                elapsedTime = parsed.data
                                break;
                            case 'error':
                                setError(parsed.data || "Unknown error");
                                setIsLoading(false);
                                return;
                            default:
                                console.warn('Unknown message type:', parsed.type);
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                        setIsLoading(false);
                        return;
                    }
                }
            }
            setStreamingResponse("");
            setMessages(prev => [...prev, { role: currentModel, content: current.replace(THINK_REGEX, '').trim(), time: elapsedTime }]);
        } catch (err) {
            console.error("Error during chat request:", err);
            setError("Error: " + (err instanceof Error ? err.message : "Unknown error"));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.page}>
            <h1 className={styles.header}>Chat</h1>

            <div className={styles.controls}>
                <Dropdown
                    options={[3, 4, 5, 6, 7, 8, 9, 10].map(i => ({ label: `k = ${i}`, value: i.toString() }))}
                    value={kValue}
                    onChange={(newValue) => setKValue(newValue)}
                />

                <Dropdown
                    options={modelList.map(m => ({ label: m, value: m }))}
                    value={model}
                    onChange={(newValue) => setModel(newValue)}
                />
                <Dropdown
                    options={indexerList.map(value => ({ value: value, label: indexerMap.get(value)! }))}
                    value={indexer}
                    onChange={(newValue) => setIndexer(newValue)}
                />

            </div>

            <div className={styles.chatBox}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={msg.role === "user" ? styles.userMsg : styles.modelMsg}>
                        <div className={styles.role}><strong>{msg.role === "user" ? "YOU" : msg.role.toUpperCase()}</strong></div>
                        <div>{msg.content}</div>
                        {msg.time && <div className={styles.time}>{msg.time.toFixed(2)} seconds</div>}
                    </div>
                ))}

                {isLoading && (
                    <div className={styles.modelMsg}>
                        <div className={styles.role}><strong>{model.toUpperCase()}</strong></div>
                        <div className={styles.streamingResponse}>{streamingResponse}<span className={styles.spinner}></span></div>

                    </div>
                )}

                {isLoading && (
                    <div className={styles.thinking}>
                        <span>🤖 Thinking...</span>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div className={styles.inputRow}>
                <textarea
                    ref={textareaRef}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                        }
                    }}
                    placeholder="Type your message..."
                    className={styles.textarea}

                />
                <button onClick={handleSubmit} className={styles.sendButton} disabled={isLoading}>
                    Send
                </button>
            </div>

            {error && <div className={styles.error}>{error}</div>}


            {proposals.length > 0 && !!!error && (
                <div className={styles.valuesSection}>
                    <button
                        onClick={() => setShowValues((prev) => !prev)}
                        className={styles.toggleButton}
                    >
                        {showValues ? "Hide" : "Show References"}
                    </button>

                    {showValues && <div className={styles.results}>
                        {proposals.map((item, index) => (
                            <div key={index} className={styles.resultItem}>
                                <span>[{index + 1}]</span>

                                <a
                                    href={`doc/${item.document}`}
                                    className={styles.document}
                                    target="_blank"
                                >
                                    {item.document}
                                </a>
                                <span className={styles.score}>(score: {item.score.toFixed(2)})</span>
                            </div>
                        ))}
                    </div>}
                </div>
            )}

            <BackLink href="/" />

        </div>
    );
}
