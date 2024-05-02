import React, { useState, useEffect, useMemo, useRef } from "react";
import "./GlobalViewPage.css"; // Import regular stylesheet
import GlobalTable from "../../Components/GlobalTable/Table";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { GetLogin, GetLogout, PostAliasInfo } from "./Utils";
import { GetAllAliases } from "./Utils";
import { GetSearchAliases } from "./Utils";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import FeedbackSelector from "../../Components/GlobalTable/FeedbackSelector";
import FeedbackInput from "../../Components/GlobalTable/FeedbackInput";

function extractArticleTitleFromUrl(article) {
  let parsed_url = new URL(article); // Create a new URL object
  let article_title = decodeURIComponent(parsed_url.pathname.split("/").pop()); // Extract the last part of the URL and decode it
  article_title = article_title.replace(/_/g, " ");
  return article_title;
}

// Need for local state mutation
function Wrapper({ data }) {
  const [formData, setFormData] = useState(data);
  const [searchResult, setSearchResult] = useState([]);
  const [unsureFilter, setUnsureFilter] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [searchBool, setSearchBoolValue] = useState(false);
  const [markAllValue, setMarkAllValue] = useState("Unsure");
  const [autoResetPageIndex, setAutoResetPageIndex] = useState(true);
  const [oldFeedbackValue, setoldFeedbackValue] = useState({
    oldIndex: -1,
    value: "",
  });
  const queryClient = useQueryClient();

  const formDataLatest = useRef(formData);
  const searchBoolRef = useRef(searchBool);
  const [username, setUsername] = useState(window.APP_DATA.username !== "None" ? window.APP_DATA.username : null);

  useEffect(() => {
    formDataLatest.current = formData;
  }, [formData]);

  useEffect(() => {
    searchBoolRef.current = searchBool;
  }, [searchBool]);

  //Search on Enter key
  const handleKeyPress = (e) => {
    if (e.code == "Enter") {
      onSearch();
    }
  };

  //Data Filter
  const unsureFilterFunc = (unsureFilterValue) => {
    console.log('unsurefilterfunc ', unsureFilterValue, formDataLatest.current.length);
    setUnsureFilter(unsureFilterValue);
    if (unsureFilterValue != 'All') {
      if (searchBoolRef.current) {
        formDataLatest.current = searchResult;
      } else {
        formDataLatest.current = data;
      }
      formDataLatest.current = formDataLatest.current.filter((v) => v.feedbackSelection == unsureFilterValue);
    } else {
      if (searchBoolRef.current) {
        formDataLatest.current = searchResult;
      } else {
        formDataLatest.current = data;
      }
    }
    console.log(formDataLatest.current.length);
    setFormData(formDataLatest.current);
    if (searchBoolRef.current) {
      setMarkAllValue("Unsure");
    }
  }

  //Flag to display Dropdown options
  const handleSearchInput = (value) => {
    setSearchValue(value);
  };

  //Submit Response for all Feedback Selection
  const markAll = (res) => {
    let subData = [];
    formDataLatest.current.forEach((item) => {
      item.feedbackSelection = res;
      subData.push(item);
    });
    onSubmit(subData);
  };

  //Login API Call
  const onLogin = () => {
    queryClient
      .fetchQuery(["login"], () => GetLogin())
      .then((res) => {
        window.location.href = res.url;
      })
      .catch(error => {
        toast.error("Failed to Login", {
          autoClose: 2000,
        });
      });

  }

  //Logout API Call
  const onLogout = () => {
    queryClient.fetchQuery(["logout"], GetLogout)
      .then(response => {
        setUsername(null);
        window.APP_DATA.username = "None";
      })
      .catch(error => {
        toast.error("Failed to Logout", {
          autoClose: 2000,
        });
      });
  }

  //Search for specfic aliases
  const onSearch = () => {
    setAutoResetPageIndex(true);
    if (searchValue !== "") {
      queryClient
        .fetchQuery(["searchAliases", searchValue], () =>
          GetSearchAliases(searchValue)
        )
        .then((searchData) => {
          searchData.forEach((item) => {
            if (item.feedbackSelection == null) {
              item.feedbackSelection = "Unsure";
            }
            if (item.feedbackInput == null) {
              item.feedbackInput = "";
            }
            item.newLink = item.link.replace(/^https?:\/\//, "");
          });
          formDataLatest.current = searchData;
          setSearchResult(formDataLatest.current);
          setFormData(formDataLatest.current);
          setUnsureFilter(false);
          setSearchBoolValue(true);
          setMarkAllValue("Unsure");
        })
        .catch((error) => {
          toast.error("Search unsuccessful", {
            autoClose: 2000,
          });
          setSearchBoolValue(false);
        });
    } else {
      queryClient
        .fetchQuery(["aliasInfo"], () => GetAllAliases())
        .then((searchData) => {
          searchData.forEach((item) => {
            if (item.feedbackSelection == null) {
              item.feedbackSelection = "Unsure";
            }
            if (item.feedbackInput == null) {
              item.feedbackInput = "";
            }
            item.newLink = item.link.replace(/^https?:\/\//, "");
          });
          formDataLatest.current = searchData;
          setFormData(formDataLatest.current);
          setSearchResult([]);
          setUnsureFilter(false);
          setSearchBoolValue(false);
        })
        .catch((error) => {
          toast.error("Failed to fetch data", {
            autoClose: 2000,
          });
          setSearchBoolValue(false);
        });
      setSearchBoolValue(false);
    }
  };

  // Update feedback selection
  const updateFeedbackSelection = (index, feedbackSelection) => {
    formDataLatest.current[index].feedbackSelection = feedbackSelection;
    setFormData(formDataLatest.current);
    const subData = [formDataLatest.current[index]];
    onSubmit(subData);
  };

  //SubmitFeedbackInput
  const submitFeedbackInput = (index, feedbackInput) => {
    if (
      oldFeedbackValue.oldIndex == index &&
      oldFeedbackValue.value != feedbackInput
    ) {
      formDataLatest.current[index].feedbackInput = feedbackInput;
      setFormData(formDataLatest.current);
      const subData = [formDataLatest.current[index]];
      oldFeedbackValue.oldIndex = -1;
      oldFeedbackValue.value = "";
      setoldFeedbackValue({ oldIndex: -1, value: "" });
      onSubmit(subData);
    }
  };

  // Update feedback Input
  const updateFeedbackInput = (index, feedbackInput) => {
    setFormData((currentState) => {
      const newState = [...currentState];
      if (oldFeedbackValue.oldIndex == -1) {
        oldFeedbackValue.oldIndex = index;
        oldFeedbackValue.value = newState[index].feedbackInput;
        setoldFeedbackValue({
          oldIndex: index,
          value: newState[index].feedbackInput,
        });
      }
      newState[index].feedbackInput = feedbackInput;
      return newState;
    });
  };

  // Form Submit Logic
  const { mutate } = useMutation(PostAliasInfo, {
    onSuccess: () => {
      const message = "Feedback Uploaded Successfully!";
      toast.success(message, {
        autoClose: 2000,
      });
    },
    onError: () => {
      toast.error("There was an error uploading your feedback", {
        autoClose: 2000,
      });
    },
  });

  const onSubmit = (submitData) => {
    if (username) {
      let newSubmitData = submitData.map(item => ({
        ...item,
        username: username
      }));
      mutate({ data: newSubmitData });
    } else {
      onLogin();
    }
  };

  //Main HTML Page
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
            <select
              className="form-select block pl-3 pr-3 py-2 text-base leading-6 border-gray-300 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 sm:text-sm sm:leading-5"
              value={row.original.feedbackSelection}
              onChange={(e) => {
                e.preventDefault();
                updateFeedbackSelection(row.index, e.target.value);
              }}
            >
              <option>Correct</option>
              <option>Incorrect</option>
              <option>Unsure</option>
            </select>
            //<FeedbackSelector row={row} setState={updateFeedbackSelection} />
          );
        },
      },
      {
        header: "Additional feedback",
        accessorKey: "feedbackInput",
        cell: ({ row }) => {
          return (
            //<FeedbackInput row={row} setFormData={updateFeedbackInput} />
            <textarea
              rows="3"
              className="py-3 mt-5 mb-5 px-3 border"
              value={row.original.feedbackInput}
              onChange={(e) => {
                setAutoResetPageIndex(false);
                e.preventDefault();
                updateFeedbackInput(row.index, e.target.value);
              }}
              onBlur={(e) => {
                e.preventDefault();
                submitFeedbackInput(row.index, e.target.value);
              }}
            />
          );
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
        <div className="flex items-center gap-2">
          {username ? <p>Welcome, {username}!</p> : <p>Welcome, Guest!</p>}
          {username ? (
            <button
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              type="button"
              onClick={onLogout}
            >
              Logout
            </button>
          ) : (
            <button
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
              type="button"
              onClick={onLogin}
            >
              Login
            </button>
          )}

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
          {/* <input
            type="checkbox"
            checked={unsureFilter}
            onChange={() => {
              unsureFilterFunc(unsureFilter);
            }}
          /> */}
          <label className="text-lg font-bold">
            Show only links tagged as :
          </label>
          <select
            className="form-select block pl-3 pr-3 py-2 text-base leading-6 border-gray-300 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 sm:text-sm sm:leading-5"
            value={unsureFilter}
            onChange={(e) => {
              e.preventDefault();
              unsureFilterFunc(e.target.value);
            }}
          >
            <option>All</option>
            <option>Correct</option>
            <option>Incorrect</option>
            <option>Unsure</option>
          </select>
        </div>
        <div className="flex gap-2 ml-auto">
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
        <ToastContainer />
      </div>
      {searchBool ? (
        <div className="flex items-center gap-2">
          <label className="text-lg font-bold">
            Mark response for all search results :
          </label>
          <select
            value={markAllValue}
            onChange={(e) => {
              e.preventDefault();
              setMarkAllValue(e.target.value);
              markAll(e.target.value);
            }}
          >
            <option>Unsure</option>
            <option>Correct</option>
            <option>Incorrect</option>
          </select>
        </div>
      ) : (
        ""
      )}
      <div className="globalViewPage mt-5">
        <GlobalTable
          columns={columns}
          data={formDataLatest.current}
          autoResetPageIndex={autoResetPageIndex}
        />
      </div>
    </div>
  );
}

export default function GlobalViewPage() {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    GetAllAliases()
      .then((fetchedData) => {
        fetchedData.forEach((item) => {
          if (item.feedbackSelection == null) {
            item.feedbackSelection = "Unsure";
          }
          if (item.feedbackInput == null) {
            item.feedbackInput = "";
          }
          item.newLink = item.link.replace(/^https?:\/\//, "");
        });
        setData(fetchedData);
        setIsLoading(false);
        setError(false);
        return <Wrapper data={fetchedData} />;
      })
      .catch((err) => {
        setError(err);
        setIsLoading(false);
      });
  }, []);

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
