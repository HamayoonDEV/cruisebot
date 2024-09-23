import React, { useState } from "react";
import { getResponse } from "../Apis";

const QueryComponent = () => {
    const [query, setQuery] = useState("");
    const [responses, setResponses] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = await getResponse(query);
        const newResponse = result.response || result.error;
        setResponses((prevResponses) => [...prevResponses, newResponse]);
        setQuery(""); // Clear the input after submission
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
            <h1 className="text-3xl font-bold mb-2 text-center">Welcome to Cruise Assistant</h1>
            <h4 className="text-lg text-gray-600 mb-6">What are your preferences?</h4>
            <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg h-[300px] overflow-y-auto md:h-[500px]">
                <h3 className="text-xl font-semibold mb-4">Responses:</h3>
                {responses.length > 0 ? (
                    responses.map((res, index) => (
                        <p key={index} className="mb-2 text-gray-700 bg-gray-100 p-4 rounded">{res}</p>
                    ))
                ) : (
                    <p className="text-gray-700">Your responses will appear here.</p>
                )}
            </div>
            <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg mt-4">
                <form onSubmit={handleSubmit} className="flex">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter your query"
                        className="flex-grow border border-gray-300 rounded-l-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        type="submit"
                        className="bg-blue-500 text-white rounded-r-md p-2 hover:bg-blue-600 transition"
                    >
                        Submit
                    </button>
                </form>
            </div>
        </div>
    );
};

export default QueryComponent;
