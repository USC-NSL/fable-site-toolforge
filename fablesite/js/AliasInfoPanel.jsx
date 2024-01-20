import React, { useState } from 'react';
import './AliasInfoPanel.css'; // Import regular stylesheet

export default function AliasInfoPanel(props) {

    const [infoState, setInfoState] = useState({...props});
    const [componentInfo, setComponentInfo] = useState({
        correct_vote: false,
        cant_tell_vote: false,
        inaccurate_vote: false,
    })

    const good_name = !componentInfo.correct_vote ? "Looks Good" : "Undo Looks Good"
    const med_name = !componentInfo.cant_tell_vote ? "Can't Tell" : "Undo Can't Tell"
    const bad_name = !componentInfo.inaccurate_vote ? "Inaccurate Alias" : "Undo Inaccurate Alias"

    async function sendUpdate(url, change) {
        const data = {
            "_id": infoState["_id"],
            "change": change
        }
        
        await fetch(url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin', 
            headers: {
              'Content-Type': 'application/json'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(data) 
        })
    }


    function goodVoteChange(change) {
        setInfoState({
            ...infoState,
            correct_votes: infoState.correct_votes + change,
        })

        setComponentInfo({
            ...componentInfo,
            correct_vote: !componentInfo.correct_vote,
        })

        sendUpdate("/api/v1/alias/update_correct/", change)

    }

    function medVoteChange(change) {
        setInfoState({
            ...infoState,
            cant_tell_votes: infoState.cant_tell_votes + change
        })

        setComponentInfo({
            ...componentInfo,
            cant_tell_vote: !componentInfo.cant_tell_vote
        })

        sendUpdate("/api/v1/alias/update_cant_tell/", change)
    }

    function badVoteChange(change) {
        setInfoState({
            ...infoState,
            inaccurate_votes: infoState.inaccurate_votes + change
        })

        setComponentInfo({
            ...componentInfo,
            inaccurate_vote: !componentInfo.inaccurate_vote
        })

        sendUpdate("/api/v1/alias/update_inaccurate/", change)
    }

    
    function goodVote() {
        const change = !componentInfo.correct_vote ? 1 : -1

        goodVoteChange(change)
    }

    function medVote() {
        const change = !componentInfo.cant_tell_vote ? 1 : -1

        medVoteChange(change)
    }

    function badVote() {
        const change = !componentInfo.inaccurate_vote ? 1 : -1

        badVoteChange(change)
    }


    return (
        <div className='infoPanel'>
            <h3>Full URL: <a href="">{infoState.brokenLink}{infoState.brokenLink}</a></h3>
            <h3>Alias: <a href={infoState.fixedLink}>{infoState.fixedLink}</a></h3>
            <h3>Method: {infoState.method}</h3>
            <h3>Looks Good Votes: {infoState.correct_votes}</h3>
            <h3>Can't Tell Votes: {infoState.cant_tell_votes}</h3>
            <h3>Looks Good Votes: {infoState.inaccurate_votes}</h3>
            <div className='buttonPanel'>
                <button type="button" onClick={goodVote} class="text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800">{good_name}</button>
                <button type="button" onClick={medVote} class="text-white bg-yellow-400 hover:bg-yellow-500 focus:ring-4 focus:ring-yellow-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:focus:ring-yellow-900">{med_name}</button>
                <button type="button" onClick={badVote} class="text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">{bad_name}</button>
            </div>
        </div>
    );
}