export async function GetAliasInfo(id) {
    const url = "/api/v1/get_alias/" + id
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
    return obj
}

export async function PostAliasInfo({data, id}) {
    const url = "/api/v1/post_alias/" + id
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

