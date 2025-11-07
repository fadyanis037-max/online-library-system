import React from 'react';
import AIPromptBox from '../components/AIPromptBox';

function Home() {
  return (
    <section className="container">
      <h1>Welcome to the AI-Powered Online Library</h1>
      <p>Browse books, make bookings, and use AI to summarize and recommend titles.</p>
      <AIPromptBox />
    </section>
  );
}

export default Home;

