import { useParams } from 'react-router-dom';
import React from 'react';
import { useNavigate } from "react-router-dom";
import './AliasPage.css'; // Import regular stylesheet
import {AliasInfoPanel} from '../../Components/AliasInfoPanel/AliasInfoPanel'


export default function IndividualAliasPage() {
    const { aliasId } = useParams()
    console.log(aliasId)
    //             <a href={"https://fable.eecs.umich.edu/all"}>{"<-- Back to list of all replacement URLs found by FABLE"}</a>
    return (
        <>
            <h1 className="text-3xl font-bold">
                Replacement URL for dead link
            </h1>
            <h3>For more information about FABLE, click <a href="https://webresearch.eecs.umich.edu/fable/"><b>here</b></a></h3>
            <div className='aliasPage'>
                <AliasInfoPanel
                    id={aliasId}
                />
            </div>
        </>
    )
}