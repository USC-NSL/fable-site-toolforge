import React, { useState, useEffect, useMemo } from "react";
import "./GlobalViewPage.css"; // Import regular stylesheet
import GlobalTable from "../../Components/GlobalTable/Table";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PostAliasInfo } from "./Utils";
import { GetAllAliases } from "./Utils";
import { GetSearchAliases } from "./Utils";
import FeedbackSelector from "../../Components/GlobalTable/FeedbackSelector";
import FeedbackInput from "../../Components/GlobalTable/FeedbackInput";

const filterData = (data, unsureFilter) => {
  if (unsureFilter) {
    return data.filter((v) => v.feedbackSelection === "Unsure");
  }
  return data;
};

function extractArticleTitleFromUrl(article) {
  let parsed_url = new URL(article); // Create a new URL object
  let article_title = decodeURIComponent(parsed_url.pathname.split("/").pop()); // Extract the last part of the URL and decode it
  article_title = article_title.replace(/_/g, " ");
  return article_title;
}

// Need for local state mutation
function Wrapper({ data }) {
  const [state, setState] = useState(data);
  const queryClient = useQueryClient();
  const [submitData, setSubmitData] = useState([]);
  //Search on Enter key
  const handleKeyPress = (e) => {
    if (e.code == "Enter") {
      onSearch();
    }
  };

  //Flag to display Dropdown options
  const handleSearchInput = (value) => {
    if (value == "") {
      setSearchBoolValue(false);
    }
    setSearchValue(value);
  };

  //Mark response for all Feedback Selection
  const markAll = (res) => {
    state.forEach((item) => {
      item.FeedbackSelector = res;
      item.FeedbackInput = "";
    });
  };

  //Search for specfic aliases
  const onSearch = () => {
    if (searchValue !== "") {
      queryClient
        .fetchQuery(["searchAliases", searchValue], () =>
          GetSearchAliases(searchValue)
        )
        .then((searchData) => {
          console.log("Search results:", searchData);
          setState(searchData);
          setSearchBoolValue(true);
        })
        .catch((error) => {
          alert("Search unsuccessful.");
          console.error("Search alias failed: ", error);
          setSearchBoolValue(false);
        });
    } else {
      queryClient
        .fetchQuery(["aliasInfo"], () => GetAllAliases())
        .then((searchData) => {
          console.log("All data:", searchData);
          setState(searchData);
          setSearchBoolValue(true);
        })
        .catch((error) => {
          alert("Failed to fetch data.");
          console.log("Error fetching the data: ", error);
          setSearchBoolValue(false);
        });
      setSearchBoolValue(false);
    }
  };

  // Update feedback selection
  const updateFeedbackSelection = (index, feedbackSelection) => {
    setState((currentState) => {
      const newState = [...currentState];
      newState[index].feedbackSelection = feedbackSelection;
      
      //Saving the changed table row to SubmitData
      const existIndex = submitData.findIndex(data => data.id === newState[index].id);
      if (existIndex < 0) {
        submitData.push(newState[index]);
        setSubmitData(submitData);
      } else{
        submitData[existIndex].feedbackSelection = feedbackSelection
      }

      return newState;
    });
  };

  // Update feedback selection
  const updateFeedbackInput = (index, feedbackInput) => {
    setState((currentState) => {
      const newState = [...currentState];
      newState[index].feedbackInput = feedbackInput;

      //Saving the changed table row to SubmitData
      const existIndex = submitData.findIndex(data => data.id === newState[index].id);
      if (existIndex < 0) {
        submitData.push(newState[index]);
        setSubmitData(submitData);
      } else{
        submitData[existIndex].feedbackInput = feedbackInput
      }

      return newState;
    });
  };

  // Form Logic
  const { mutate } = useMutation(PostAliasInfo, {
    onSuccess: () => {
      const message = "Feedback Uploaded Successfully!";
      alert(message);
    },
    onError: () => {
      alert("There was an error uploading your feedback.");
    },
  });

  const onSubmit = () => {
    mutate({ data: submitData });
  };

  // Filtering Logic
  const [unsureFilter, setUnsureFilter] = useState(false);
  const filteredData = useMemo(
    () => filterData(state, unsureFilter),
    [state, unsureFilter]
  );

  const [searchValue, setSearchValue] = useState("");
  const [searchBool, setSearchBoolValue] = useState(false);

  const columns = useMemo(
    () => [
      {
        header: () => (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            Article where broken link appears
            <span
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                marginLeft: "4px",
                color: "#696969",
              }}
            >
              <span style={{ lineHeight: "0.8", fontSize: "0.8em" }}>
                &#9650;
              </span>{" "}
              {/* Upward arrow */}
              <span style={{ lineHeight: "0.8", fontSize: "0.8em" }}>
                &#9660;
              </span>{" "}
              {/* Downward arrow */}
            </span>
          </div>
        ),
        accessorKey: "article",
        width: 220,
        cell: ({ getValue }) => {
          return (
            <a href={getValue()} className="break-word" target="_blank">
              {extractArticleTitleFromUrl(getValue())}
            </a>
          );
        },
      },
      {
        header: () => (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            Broken link
            <span
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                marginLeft: "4px",
                color: "#696969",
              }}
            >
              <span style={{ lineHeight: "0.8", fontSize: "0.8em" }}>
                &#9650;
              </span>{" "}
              {/* Upward arrow */}
              <span style={{ lineHeight: "0.8", fontSize: "0.8em" }}>
                &#9660;
              </span>{" "}
              {/* Downward arrow */}
            </span>
          </div>
        ),
        accessorKey: "link",
        width: 350,
        cell: ({ getValue }) => {
          return (
            <a href={getValue()} className="break-all" target="_blank">
              {getValue()}
            </a>
          );
        },
      },
      {
        header: "New URL for same page",
        accessorKey: "alias",
        width: 350,
        cell: ({ getValue }) => {
          return (
            <a href={getValue()} className="break-all" target="_blank">
              {getValue()}
            </a>
          );
        },
      },
      {
        header: "Is new URL correct?",
        width: 130,
        accessorKey: "feedbackSelection",
        cell: ({ row }) => {
          return (
            <FeedbackSelector row={row} setState={updateFeedbackSelection} />
          );
        },
      },
      {
        header: "Additional feedback",
        accessorKey: "feedbackInput",
        cell: ({ row }) => {
          return <FeedbackInput row={row} setState={updateFeedbackInput} />;
        },
      },
      {
        header: () => (
          <div
            style={{
              display: "none",
            }}
          ></div>
        ),
        accessorKey: "newLink",
        width: 350,
        cell: ({ getValue }) => {
          return (
            <a
              href={getValue()}
              style={{
                display: "none",
              }}
              target="_blank"
            >
              {getValue()}
            </a>
          );
        },
      },
    ],
    []
  );

  return (
    <div>
      <div className="flex justify-between">
        <h1 className="text-3xl font-bold">
          Replacement URLs for links marked permanently dead
        </h1>
        <div className="flex gap-2">
          <input
            type="text"
            id="Search"
            name="Search"
            className="border-2 border-gray-300"
            style={{ borderRadius: "5px" }}
            value={searchValue}
            onChange={(e) => handleSearchInput(e.target.value)}
            onKeyDownCapture={handleKeyPress}
          />
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            type="button"
            onClick={onSearch}
          >
            Search
          </button>
        </div>
      </div>
      <h3>
        For more information about FABLE, click{" "}
        <a href="https://webresearch.eecs.umich.edu/fable/">
          <b>here</b>
        </a>
      </h3>
      <div className="flex items-center justify-between py-5">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={unsureFilter}
            onChange={() => setUnsureFilter(!unsureFilter)}
          />
          <label className="text-lg font-bold">
            Show only links tagged as Unsure
          </label>
        </div>

        <button
          className="bg-green-400 hover:bg-green-600 text-green-100 border py-3 px-6 font-semibold text-md rounded"
          onClick={onSubmit}
        >
          Submit Feedback
        </button>
    </div>
      {searchBool && searchValue != "" ? (
        <div className="flex items-center gap-2">
          <label className="text-lg font-bold">
            Mark response for all search results :
          </label>
          <select
            onChange={(e) => {
              markAll(e.target.value);
            }}
          >
            <option>Correct</option>
            <option>Incorrect</option>
            <option>Unsure</option>
          </select>
        </div>
      ) : (
        ""
      )}
      <div className="globalViewPage mt-5">
        <GlobalTable columns={columns} data={filteredData} />
      </div>
    </div>
  );
}

export default function GlobalViewPage() {
  const { isLoading, error, data } = useQuery(["aliasInfo"], () =>
    GetAllAliases()
  );

  useEffect(() => {
    document.title =
      "FABLE: Replacement URLs for links marked permanently dead";
  }, []);

  if (isLoading) {
    return <p>Loading Data</p>;
  }

  if (error) {
    return <p>Error Fetching Data</p>;
  }

  data.forEach((item) => {
    item.newLink = item.link.replace(/^https?:\/\//, "");
  });
  return <Wrapper data={data} />;
}
