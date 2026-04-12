import React, { useState, useEffect, useRef } from 'react';
import VapiModule from '@vapi-ai/web';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Settings, BookOpen, Scaling, Contrast, Activity } from 'lucide-react';

const VapiConstructor = VapiModule.default || VapiModule;
const vapi = new VapiConstructor("2730e829-8411-4cf1-997c-9c60b57651c2");
const ASSISTANT_ID = "024574ad-baac-4ffd-b038-eddadb4e2735";

function App() {
  const [isCalling, setIsCalling] = useState(false);
  const [callStatus, setCallStatus] = useState('inactive'); // inactive, connecting, active, thinking
  const [transcript, setTranscript] = useState([]);
  const [currentText, setCurrentText] = useState('');
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);
  const transcriptEndRef = useRef(null);

  useEffect(() => {
    vapi.on('call-start', () => {
      setIsCalling(true);
      setCallStatus('active');
    });

    vapi.on('call-end', () => {
      setIsCalling(false);
      setCallStatus('inactive');
    });

    vapi.on('message', (message) => {
      if (message.type === 'transcript') {
        if (message.transcriptType === 'final') {
          setTranscript(prev => [...prev, {
            role: message.role,
            text: message.text
          }]);
          setCurrentText('');
        } else {
          setCurrentText(message.text);
        }
      }
    });

    vapi.on('error', (e) => {
      console.error(e);
      setCallStatus('inactive');
    });

    return () => vapi.removeAllListeners();
  }, []);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript, currentText]);

  const toggleCall = () => {
    if (isCalling) {
      vapi.stop();
    } else {
      setCallStatus('connecting');
      vapi.start(ASSISTANT_ID);
    }
  };

  return (
    <div className={`dashboard ${highContrast ? 'high-contrast' : ''} ${largeText ? 'large-text' : ''}`}>
      {/* Main Experience */}
      <div className="main-view">
        <header style={{ textAlign: 'center' }}>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-1px' }}
          >
            Omni<span style={{ color: 'var(--primary)' }}>Voice</span>
          </motion.h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>Universal Accessibility Advocate</p>
        </header>

        <div className="orb-container">
          <motion.div 
            className={`orb ${callStatus}`}
            animate={{
              scale: isCalling ? [1, 1.05, 1] : 1,
            }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
          <div style={{ position: 'absolute', zIndex: 10 }}>
            {callStatus === 'connecting' && <Activity className="spin" size={48} color="white" />}
          </div>
        </div>

        <button 
          onClick={toggleCall}
          className={`glass control-pill`}
          style={{ 
            background: isCalling ? '#ef4444' : 'var(--primary)',
            color: isCalling ? 'white' : '#030712',
            fontSize: '1.1rem',
            padding: '16px 40px'
          }}
        >
          {isCalling ? <MicOff size={24} /> : <Mic size={24} />}
          {isCalling ? 'Terminate Session' : 'Initiate Voice Protocol'}
        </button>

        <div style={{ display: 'flex', gap: '15px' }}>
          <button onClick={() => setHighContrast(!highContrast)} className="glass control-pill">
            <Contrast size={20} /> Contrast
          </button>
          <button onClick={() => setLargeText(!largeText)} className="glass control-pill">
            <Scaling size={20} /> Text Size
          </button>
        </div>
      </div>

      {/* Side Intelligence Panel */}
      <div className="side-panel">
        <div className="glass" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen size={20} color="var(--primary)" />
            <span style={{ fontWeight: 600 }}>Live Transcript</span>
          </div>
          <div className="transcript-area">
            {transcript.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`transcript-bubble ${msg.role}`}
                style={{
                  marginBottom: '15px',
                  padding: '12px 16px',
                  borderRadius: '16px',
                  background: msg.role === 'user' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  border: msg.role === 'user' ? '1px solid rgba(56, 189, 248, 0.2)' : '1px solid rgba(255, 255, 255, 0.1)',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%'
                }}
              >
                <div style={{ fontSize: '0.7rem', color: 'var(--primary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  {msg.role}
                </div>
                <p style={{ margin: 0, lineHeight: 1.5 }}>{msg.text}</p>
              </motion.div>
            ))}
            
            {currentText && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ 
                  color: 'var(--text-muted)', 
                  fontStyle: 'italic', 
                  fontSize: '0.9rem',
                  padding: '0 10px'
                }}
              >
                {currentText}...
              </motion.div>
            )}
            
            {transcript.length === 0 && !currentText && (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', textAlign: 'center', marginTop: '40px' }}>
                Awaiting voice command initialization...
              </p>
            )}
            <div ref={transcriptEndRef} />
          </div>
        </div>

        <div className="glass" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Settings size={20} color="var(--primary)" />
            <span style={{ fontWeight: 600 }}>System Status</span>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <p>• Connectivity: <span style={{ color: '#10b981' }}>Secure</span></p>
            <p>• Brain: Llama 3.1 (Groq)</p>
            <p>• Memory: Qdrant Vector Cloud</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
