import React, { useState, useEffect, useMemo } from "react";
import "./GlobalViewPage.css"; // Import regular stylesheet
import GlobalTable from "../../Components/GlobalTable/Table";
import { useQuery } from "@tanstack/react-query";
import { useMutation } from "@tanstack/react-query";
import { PostAliasInfo } from "./Utils";
import { GetAllAliases } from "./Utils";
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

  // Update feedback selection
  const updateFeedbackSelection = (index, feedbackSelection) => {
    const newState = [...state];
    newState[index].feedbackSelection = feedbackSelection;
    setState(newState);
  };

  // Update feedback selection
  const updateFeedbackInput = (index, feedbackInput) => {
    const newState = [...state];
    newState[index].feedbackInput = feedbackInput;
    setState(newState);
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
    mutate({ data: state });
  };

  const onSearch = () => {
    if (searchValue != "") {
      alert("Search button clicked. The value is " + searchValue + ". ");
    } else {
      alert("Search button clicked. ");
    }
  };

  // Filtering Logic
  const [unsureFilter, setUnsureFilter] = useState(false);
  const filteredData = useMemo(
    () => filterData(state, unsureFilter),
    [state, unsureFilter]
  );

  const [searchValue, setSearchValue] = useState("");

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
            <a href={getValue()} className="break-all" target="_blank">
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
        width: 150,
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
            onChange={(e) => setSearchValue(e.target.value)}
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
      <div className="flex items-center gap-2 py-5">
        <input
          type="checkbox"
          checked={unsureFilter}
          onChange={() => setUnsureFilter(!unsureFilter)}
        />
        <label className="text-lg font-bold">
          Show only links tagged as Unsure
        </label>
      </div>
      <div className="globalViewPage mt-5">
        <GlobalTable columns={columns} data={filteredData} />
      </div>
      <button
        className="mt-4 bg-green-400 hover:bg-green-600 text-green-100 border py-3 px-6 font-semibold text-md rounded"
        onClick={onSubmit}
      >
        Submit Feedback
      </button>
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

  return <Wrapper data={data} />;
}
