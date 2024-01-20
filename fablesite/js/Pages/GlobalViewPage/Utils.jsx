export async function GetAllAliases() {
    const url = "/api/v1/get_all_aliases"
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
    
    let obj = await response.json()

    // Need to add feedback items to objects
    obj = obj.map(v => ({...v, feedbackSelection: "Unsure", feedbackInput: ""}))

    return obj
}

export async function PostAliasInfo({data}) {
    const url = "/api/v1/post_aliases/"
    const response = await fetch(url, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, *cors, same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, *same-origin, omit
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    });
    
    const obj = await response.json()
    return obj
}