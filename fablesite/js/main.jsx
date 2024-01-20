import React, { StrictMode } from "react";
import GlobalViewPage from "./Pages/GlobalViewPage/GlobalViewPage";
import IndividualAliasPage from "./Pages/IndividualAliasPage/IndividualAliasPage";
import ErrorPage from "./ErrorPage";
import { createRoot } from "react-dom/client";
import { Routes, Route, BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'; // Import regular stylesheet
import './style.css'; // Import regular stylesheet

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

const queryClient = new QueryClient()

root.render(
  <StrictMode>
      <div className="App">
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Routes>
              <Route exact path="/" element={<GlobalViewPage /> } title="Fable" />
              <Route exact path="/alias/:aliasId" element={<IndividualAliasPage />} title="Fable" />
              <Route exact path="/error" element={<ErrorPage /> } title="Fable Error"/>
            </Routes>
          </BrowserRouter>
        </QueryClientProvider>
    </div>
  </StrictMode>
);
