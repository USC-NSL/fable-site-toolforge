import React from "react";

export default function Table({aliases}) {
    if (aliases === null || aliases === undefined || aliases.length === 0) {
        return (
            <p>No Data</p>
        )
    }

    const tableRows = aliases.map(
        (alias) => {
            return (
                <tr className="bg-white border-b dark:border-gray-700">
                    <td className="py-4 px-6">
                        <a href={alias["url"]} className="break-all"><b>{alias["url"]}</b></a>
                    </td>
                    <td className="py-4 px-6">
                        <a href={alias["alias"]} className="break-all"><b>{alias["alias"]}</b></a>
                    </td>
                </tr>
            )
        }
    )

    return (
        <div className="overflow-x-auto relative">
            <table className="w-full text-medium text-left bg-gray-150 dark:text-black">
                <thead className="text-medium dark:bg-slate-100">
                    <tr>
                        <th scope="col" className="py-3 px-6">
                            Broken link
                        </th>
                        <th scope="col" className="py-3 px-6">
                            New URL for same page
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {tableRows}
                </tbody>
            </table>
        </div>
    )
}