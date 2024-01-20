import React, { useEffect } from "react"
import { GetAliasInfo, PostAliasInfo } from "./Utils"
import { useForm } from "react-hook-form"
import './AliasInfoPanel.css' // Import regular stylesheet
import { useQuery, useMutation } from "@tanstack/react-query"
import Table from "../Table/Table"

export function AliasInfoPanel(id) {
    const { isLoading, error, data } = useQuery(['aliasInfo'], () => GetAliasInfo(id.id))
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
    const onSubmit = uploadData => mutate({data: uploadData, id: id.id})

    useEffect(
        () => {
            if (isLoading || error) {
                document.title = 'Information Loading...'
                return
            }

            document.title = `New URL for ${data.url}`
        }, [isLoading, error]
    )

    if (isLoading) {
        return <h2>Loading</h2>
    }

    if (error) {
        return <h2>Could not fetch Alias Info</h2>
    }

    return (
        <div className="content">
            <h2><b>Link Info</b></h2>
            <div className="w-full py-10 mt-5 mb-5 px-12 border">
                <p>Broken link: <a href={data.link}><b>{data.link}</b></a></p>
                <p>Potential new URL for same page: <a href={data.alias}><b>{data.alias}</b></a></p>
                <p>Article: <a href={data.article}><b>{data.article}</b></a></p>
            </div>
            <h2><b>Ratings</b></h2>
            <div className="w-full py-10 mt-5 mb-5 px-12 border">
                <p>Accurate: <b>{data.accurate}</b></p>
                <p>Can't Tell: <b>{data.mid}</b></p>
                <p>Inaccurate: <b>{data.inaccurate}</b></p>
            </div>
            <h2><b>Feedback</b></h2>
            <div>
                <form
                    className="w-full py-10 mt-5 mb-5 px-12 border" 
                    onSubmit={handleSubmit(onSubmit)}
                >
                    <label className="text-gray-600 font-medium block mt-4">Does the new URL look accurate to you?</label>
                    <select {...register("quality", { required: true})}>
                        <option value="accurate">Accurate</option>
                        <option value="inaccurate">Can't Tell</option>
                        <option value="pass">Inaccurate</option>
                    </select>
                    {errors.quality && (
                        <div className="mb-3 text-normal text-red-500 ">
                            <span>Accuracy Tag Required</span>
                        </div>
                    )}
                    <label className="text-gray-600 font-medium block mt-4">Additional feedback</label>
                    <textarea {...register('description')} id="message" rows="4" class="block p-2.5 w-full text-sm rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"></textarea>
                    <br ></br>
                    <label className="text-gray-600 font-medium">{"Wikipedia Username (Optional)"}</label>
                    <p>{"(so that we can check back with you on your Talk page if needed)"}</p>
                    <input
                        {...register('username')}
                        className="border-solid border-gray-300 border py-2 px-4 w-full rounded text-gray-700"
                        name="username"
                    />
                    <button
                        className="mt-4 w-full bg-green-400 hover:bg-green-600 text-green-100 border py-3 px-6 font-semibold text-md rounded"
                        type="submit"
                    >
                        Submit
                    </button>
            </form>
            </div>
        </div>
    );
}