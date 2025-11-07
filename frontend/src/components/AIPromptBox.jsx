import React, { useState } from 'react';
import { recommend, summarize } from '../api/api';

function AIPromptBox() {
  const [query, setQuery] = useState('');
  const [text, setText] = useState('');
  const [recResult, setRecResult] = useState(null);
  const [sumResult, setSumResult] = useState('');
  const [loadingRec, setLoadingRec] = useState(false);
  const [loadingSum, setLoadingSum] = useState(false);
  const [error, setError] = useState('');

  const handleRecommend = async () => {
    setError('');
    setRecResult(null);
    try {
      setLoadingRec(true);
      const { data } = await recommend(query);
      setRecResult(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Recommendation failed');
    } finally {
      setLoadingRec(false);
    }
  };

  const handleSummarize = async () => {
    setError('');
    setSumResult('');
    try {
      setLoadingSum(true);
      const { data } = await summarize({ text });
      setSumResult(data.summary);
    } catch (err) {
      setError(err.response?.data?.error || 'Summarization failed');
    } finally {
      setLoadingSum(false);
    }
  };

  return (
    <div className="panel">
      <h3>AI Tools</h3>
      <div className="grid-2">
        <div>
          <label>Recommend me a book</label>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g. detective mystery on moors" />
          <button className="btn" onClick={handleRecommend} disabled={loadingRec || !query}>
            {loadingRec ? 'Thinking…' : 'Recommend'}
          </button>
          {recResult && (
            <div className="result">
              Recommended: {recResult.recommended_book || '—'}
            </div>
          )}
        </div>
        <div>
          <label>Summarize text</label>
          <textarea rows={5} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste any text to summarize" />
          <button className="btn" onClick={handleSummarize} disabled={loadingSum || !text}>
            {loadingSum ? 'Summarizing…' : 'Summarize'}
          </button>
          {sumResult && (
            <div className="result">
              {sumResult}
            </div>
          )}
        </div>
      </div>
      {error && <div className="error" style={{ marginTop: 8 }}>{error}</div>}
    </div>
  );
}

export default AIPromptBox;

