import React, { useState, useEffect, useMemo } from 'react';
import './GlobalViewPage.css'; // Import regular stylesheet
import GlobalTable from '../../Components/GlobalTable/Table';
import { useQuery } from '@tanstack/react-query';
import { useForm } from "react-hook-form"
import { useMutation } from "@tanstack/react-query"
import { PostAliasInfo } from "./Utils"
import { GetAllAliases } from './Utils';
import FeedbackSelector from '../../Components/GlobalTable/FeedbackSelector'
import FeedbackInput from '../../Components/GlobalTable/FeedbackInput'

const filterData = (data, unsureFilter) => {
    if (unsureFilter) {
        return data.filter(v => v.feedbackSelection === "Unsure")
    }
    return data
}

// Need for local state mutation
function Wrapper({data}) {
    const [state, setState] = useState(data);

    // Update feedback selection
    const updateFeedbackSelection = (index, feedbackSelection) => {
        const newState = [...state]
        newState[index].feedbackSelection = feedbackSelection
        setState(newState)
    }

    // Update feedback selection
    const updateFeedbackInput = (index, feedbackInput) => {
        const newState = [...state]
        newState[index].feedbackInput = feedbackInput
        setState(newState)
    }

    // Form Logic
    const { mutate } = useMutation(PostAliasInfo, {
        onSuccess: () => {
           const message = "Feedback Uploaded Successfully!"
           alert(message)
         },
       onError: () => {
            alert("There was an error uploading your feedback.")
        }
     })

    const { register, handleSubmit, formState: { errors } } = useForm()
    const onSubmit = uploadData => mutate({data: state})

    // Filtering Logic
    const [unsureFilter, setUnsureFilter] = useState(false)
    const filteredData = useMemo(
        () => filterData(state, unsureFilter),
        [state, unsureFilter]
    )

    const columns = useMemo(
        () => [
            {   
                header: "Article where broken link appears",
                accessorKey: "article",
                cell: ({getValue}) => {
                    return <a href={getValue()} className="break-all">{getValue()}</a>
                }
            },
            {   
                header: "Broken link",
                accessorKey: "link",
                cell: ({getValue}) => {
                    return <a href={getValue()} className="break-all">{getValue()}</a>
                }

            },
            {   
                header: "New URL for same page",
                accessorKey: "alias",
                cell: ({getValue}) => {
                    return <a href={getValue()} className="break-all">{getValue()}</a>
                }
            },
            {   
                header: "Is new URL correct?",
                accessorKey: "feedbackSelection",
                cell: ({row}) => {
                    return <FeedbackSelector row={row} setState={updateFeedbackSelection}/>
                }
            },
            {   
                header: "Additional feedback",
                accessorKey: "feedbackInput",
                cell: ({row}) => {
                    return <FeedbackInput row={row} setState={updateFeedbackInput}/>
                }
            },
        ],
        []
    )

    return (
        <form
            onSubmit={handleSubmit(onSubmit)}
        >
            <h1 className="text-3xl font-bold">
                Replacement URLs for links marked permanently dead
            </h1>
            <h3>For more information about FABLE, click <a href="https://webresearch.eecs.umich.edu/fable/"><b>here</b></a></h3>
            <div className="flex items-center gap-2 py-5">
                <input
                    type="checkbox"
                    checked={unsureFilter}
                    onChange={() => setUnsureFilter(!unsureFilter)}
                />
                <label className="text-lg font-bold">Show only links tagged as Unsure</label>
            </div>
            <div className='globalViewPage mt-5'>
                <GlobalTable
                    columns={columns}
                    data={filteredData}
                />
            </div>
            <button
                className="mt-4 bg-green-400 hover:bg-green-600 text-green-100 border py-3 px-6 font-semibold text-md rounded"
                type="submit"
            >
                Submit Feedback
            </button>
        </form>
    )
}

export default function GlobalViewPage() {
    const { isLoading, error, data } = useQuery(['aliasInfo'], () => GetAllAliases())

    useEffect(
        () => {
            document.title = "FABLE: Replacement URLs for links marked permanently dead"
        }, []
    )

    if (isLoading) {
        return (
            <p>Loading Data</p>
        )
    }

    if (error) {
        return (
            <p>Error Fetching Data</p>
        )
    } 

    return (
        <Wrapper data={data} />
    )
}