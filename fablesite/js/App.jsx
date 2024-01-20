import React from "react";
import GlobalViewPage from "./Pages/GlobalViewPage/GlobalViewPage";
import ErrorPage from "./ErrorPage";
import InputPage from "./InputPage";
import IndividualAliasPage from "./Pages/IndividualAliasPage/IndividualAliasPage";
import { Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'; // Import regular stylesheet

const queryClient = new QueryClient()

export default function App() {
  return (
    <div>
      <h1>Fable-Bot</h1>
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route exact path="/" element={<GlobalViewPage /> } title="Fable-Bot" />
          <Route exact path="/error" element={<ErrorPage /> } title="Fable-Bot-Error"/>
        </Routes>
      </QueryClientProvider>
    </div>
  )
}

// <Route exact path="/alias/:aliasId" element={<IndividualAliasPage />} title="Fable Alias" />
// <Route exact path="/all" element={<GlobalViewPage />} title="Fable Aliases" />