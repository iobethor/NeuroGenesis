 export default function Home() {
   return (
     <main className="container">
       <section className="hero">
         <h1>Builder Console</h1>
         <p>
           Realtime ops for agents, traces, modules, budgets, and incident
           handling.
         </p>
       </section>
       <section className="grid">
         <div className="card">
           <h2>Live Traces</h2>
           <p>SSE/WS streams wired to the event core.</p>
         </div>
         <div className="card">
           <h2>Agent Registry</h2>
           <p>Enable/disable modules and monitor heartbeats.</p>
         </div>
         <div className="card">
           <h2>Budgets</h2>
           <p>Latency budgets, retries, and circuit breakers.</p>
         </div>
         <div className="card">
           <h2>Incidents</h2>
           <p>Auto-fallbacks and incident log visibility.</p>
         </div>
       </section>
     </main>
   );
 }
