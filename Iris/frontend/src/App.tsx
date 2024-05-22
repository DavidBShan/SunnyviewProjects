import React, { useEffect, useState } from "react";
import "./App.css";
import { RetellWebClient } from "retell-client-js-sdk";

const agentId = "a29d458e9d138371eeecb3932f328ed9";

interface RegisterCallResponse {
  call_id?: string;
  sample_rate: number;
}

const webClient = new RetellWebClient();

const App = () => {
  const [isCalling, setIsCalling] = useState(false);
  const [spongebobImage, setSpongebobImage] = useState("spongebob6");

  // Initialize the SDK
  useEffect(() => {
    // Setup event listeners
    webClient.on("conversationStarted", () => {
      console.log("conversationStarted");
      // Start switching between images every 1 second
      console.log("YO2");
      const intervalId = setInterval(() => {
        console.log("YO");
        setSpongebobImage((prevImage) =>
          prevImage === "spongebob6" ? "spongebob6" : "spongebob6"
        );
      }, 500);

      return () => clearInterval(intervalId); // Cleanup on unmount or conversation end
    });

    webClient.on("conversationEnded", ({ code, reason }) => {
      console.log("Closed with code:", code, ", reason:", reason);
      setIsCalling(false); // Update button to "Start" when conversation ends
    });

    webClient.on("error", (error) => {
      console.error("An error occurred:", error);
      setIsCalling(false); // Update button to "Start" in case of error
    });
  }, []);

  const toggleConversation = async () => {
    if (isCalling) {
      webClient.stopConversation();
    } else {
      const registerCallResponse = await registerCall(agentId);
      console.log(registerCallResponse)
      if (registerCallResponse.call_id) {
        webClient
          .startConversation({
            callId: registerCallResponse.call_id,
            sampleRate: registerCallResponse.sample_rate,
            enableUpdate: true,
          })
          .catch(console.error);
        setIsCalling(true); // Update button to "Stop" when conversation starts
      }
    }
  };

  async function registerCall(agent_id_path: string): Promise<RegisterCallResponse> {
    try {
      // Replace with your server url
      const response = await fetch(
        "http://localhost:8080/register-call-on-your-server",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          }
        },
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data: RegisterCallResponse = await response.json();
      console.log(data);
      return data;
    } catch (err) {
      console.log(err);
      throw new Error(err);
    }
  }

  return (
    <div className="App" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <img 
        src={process.env.PUBLIC_URL + `/image/spongebob3.jpg`} 
        alt="Spongebob" 
        style={{
          maxWidth: "100%",
          height: "650px",
          borderRadius: "5px"
        }}
      />
      <button 
        onClick={toggleConversation}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          backgroundColor: isCalling ? "#ff4500" : "#008000",
          color: "#ffffff",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          outline: "none",
          marginTop: "10px"
        }}
      >
        {isCalling ? "Stop" : "Start"}
      </button>
    </div>
  );
}

export default App;