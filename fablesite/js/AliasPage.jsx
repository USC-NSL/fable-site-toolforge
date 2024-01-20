import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import './AliasPage.css'; // Import regular stylesheet

import AliasInfo from './AliasInfo';

export default function AliasPage() {

    const navigate = useNavigate();
    const { wiki_url } = useParams();
    const [ articleInfo, setArticleInfo ] = useState({
        title: "",
        article_url: "",
        alias: [],
    })

    async function getInfo() {
        const url = "/api/v1/get_article/" + wiki_url

        try {
            const response = await fetch(url, {
                method: "GET", // *GET, POST, PUT, DELETE, etc.
                mode: "cors", // no-cors, *cors, same-origin
                cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
                credentials: "same-origin", // include, *same-origin, omit
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
            });
            
            const obj = await response.json()

            setArticleInfo({...articleInfo,
                title: obj.article_title,
                article_url: obj.article_url,
                alias: obj["alias_ids"],
            })

        } catch {
            navigate("/error")
        }
    }

    // Load in Aliases for article
    useEffect(() => { 
        getInfo()
        document.title = articleInfo.title
    }, []);

    // Create list of alias objects
    const aliasItems = articleInfo["alias"].map(
        (id) => {
            return <li key={id}><AliasInfo props={id} /></li>
        }
    );

    return (
        <div className='aliasPage'>
            <h2>{articleInfo["alias"].length} {articleInfo["alias"].length === 1 ? "alias": "aliases"} found for permanently dead links on <a href={articleInfo.article_url}>{articleInfo.title}</a></h2>
            <ul>{aliasItems}</ul>
        </div>
    )
}