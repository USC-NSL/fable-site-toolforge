import React from "react";
import {
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
    useReactTable,
    getSortedRowModel,
} from '@tanstack/react-table'

export default function GlobalTable({columns, data}) {
    const table = useReactTable({
        data,
        columns,
        getPaginationRowModel: getPaginationRowModel(),
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
    })

    if (data === null || data === undefined || data.length === 0) {
        return (
            <p>No Data</p>
        )
    }

    return (
        <div className="relative overflow-x-auto">
            <table className="table-auto w-full text-medium text-left bg-gray-150 dark:text-black">
                <thead className="text-medium dark:bg-slate-100 break-word w-auto">
                    {table.getHeaderGroups().map(headerGroup => (
                    <tr key={headerGroup.id}>
                        {headerGroup.headers.map((header, index) => (
                            <th key={header.id} onClick={index < 2 ? header.column.getToggleSortingHandler() : undefined} scope="col" className={`py-3 px-4 flex-wrap cursor-pointer ${index < 2 ? '' : 'pointer-events-none'}`}>
                                {header.isPlaceholder
                                ? null
                                : flexRender(
                                    header.column.columnDef.header,
                                    header.getContext()
                                )}
                            </th>
                        ))}
                    </tr>
                    ))}
                </thead>
                <tbody>
                    {table.getRowModel().rows.map(row => {
                        return (
                            <tr className="bg-white border-b dark:border-gray-700 w-2" key={row.id}>
                            {row.getVisibleCells().map(cell => {
                                const element = flexRender(cell.column.columnDef.cell, cell.getContext())
                                return (
                                    <td className="py-4 px-4" key={cell.id}>
                                        {element}
                                    </td>
                                )
                            })}
                        </tr>
                        )
                    })}
                </tbody>
            </table>
            <div className="flex items-center gap-2 py-5">
                <button
                    className="border rounded p-1"
                    onClick={() => table.setPageIndex(0)}
                    disabled={!table.getCanPreviousPage()}
                >
                {'<<'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                {'<'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                >
                {'>'}
                </button>
                <button
                    className="border rounded p-1"
                    onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                    disabled={!table.getCanNextPage()}
                >
                {'>>'}
                </button>
                <span className="flex items-center gap-1">
                <div>Page</div>
                <strong>
                    {table.getState().pagination.pageIndex + 1} of{' '}
                    {table.getPageCount()}
                </strong>
                </span>
                <span className="flex items-center gap-1">
                | Go to page:
                <input
                    type="number"
                    defaultValue={table.getState().pagination.pageIndex + 1}
                    onChange={e => {
                    const page = e.target.value ? Number(e.target.value) - 1 : 0
                    table.setPageIndex(page)
                    }}
                    className="border p-1 rounded w-16"
                />
                </span>
                <select
                    value={table.getState().pagination.pageSize}
                    onChange={e => {
                        table.setPageSize(Number(e.target.value))
                    }}
                >
                {[10, 20, 30, 40, 50].map(pageSize => (
                    <option key={pageSize} value={pageSize}>
                    Show {pageSize}
                    </option>
                ))}
                </select>
            </div>
        </div>
    )
}