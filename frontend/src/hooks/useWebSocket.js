import { useEffect, useRef, useState } from 'react';
import useResearchStore from '../store/researchStore';
import { API_BASE_URL } from '../api/client';

const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

const useWebSocket = (jobId) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const addStep = useResearchStore((state) => state.addStep);
  const fetchJobDetails = useResearchStore((state) => state.fetchJobDetails);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);

  useEffect(() => {
    if (!jobId) return;

    const connect = () => {
      const token = localStorage.getItem('access_token');
      const wsUrl = `${WS_BASE_URL}/ws/research/${jobId}/?token=${token}`;
      
      console.log(`Connecting to WebSocket: ${wsUrl}`);
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket connection established.');
        setConnected(true);
        reconnectAttemptsRef.current = 0;
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'step') {
            addStep(data);
            
            // If the step is "write" and has report output, update live report preview
            if (data.step_type === 'write' && data.tool_output) {
              useResearchStore.setState({
                currentReport: {
                  full_report_markdown: data.tool_output,
                  executive_summary: "Generating summary...",
                  title: "Report Draft Preview"
                }
              });
            }
          } else if (data.type === 'complete') {
            console.log('Research job complete event received.');
            fetchJobDetails(jobId);
          } else if (data.type === 'error') {
            console.error('WebSocket agent error message:', data.message);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message content:', err);
        }
      };

      socket.onclose = (event) => {
        console.log('WebSocket connection closed.', event.reason);
        setConnected(false);
        
        // Reconnect with exponential backoff
        const maxAttempts = 6;
        if (reconnectAttemptsRef.current < maxAttempts) {
          const delay = Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [jobId, addStep, fetchJobDetails]);

  return connected;
};

export default useWebSocket;
