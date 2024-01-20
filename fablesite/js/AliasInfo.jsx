import React, { useState, useEffect } from 'react';
import { Disclosure } from '@headlessui/react'
import { ChevronUpIcon } from '@heroicons/react/solid'
import AliasInfoPanel from './AliasInfoPanel';

// const truncate = (input) => input.length > 30 ? `${input.substring(0, 30)}...` : input;

export default function AliasInfo(props) {

    const id = props.props
    const [info, setInfo] = useState({});

    async function getAliasInfo() {
        const url = "/api/v1/get_alias/" + id
        const response = await fetch(url, {
            method: "GET", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", // no-cors, *cors, same-origin
            cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
            credentials: "same-origin", // include, *same-origin, omit
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                // Authorization: token,
            },
        });

        const json = await response.json()
        setInfo(json)
    }

    useEffect(() => { 
        getAliasInfo()
    }, []);


    return (
        <div className="w-full p-2 mx-auto">
            <Disclosure>
            {({ open }) => (
                <>
                <Disclosure.Button className="flex justify-between w-full px-4 py-2 text-sm font-medium text-left text-green-900 bg-green-300 rounded-lg hover:bg-green-400 focus:outline-none focus-visible:ring focus-visible:ring-green-700 focus-visible:ring-opacity-75">
                    <span>{info.brokenLink}</span>
                    <ChevronUpIcon
                    className={`${
                        open ? 'transform rotate-180' : ''
                    } w-5 h-5 text-green-700`}
                    />
                </Disclosure.Button>
                <Disclosure.Panel className="px-4 pt-4 pb-2 text-sm text-gray-500 bg-gray-100 rounded-lg ">
                    <AliasInfoPanel {...info}/>
                </Disclosure.Panel>
                </>
            )}
            </Disclosure>
        </div>
    )
}
