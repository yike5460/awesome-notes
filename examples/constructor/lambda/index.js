exports.handler = async (event) => {
    const agentName = process.env.AGENT_NAME;
    
    console.log(`AI Agent ${agentName} received an event:`, JSON.stringify(event, null, 2));
    
    // Add your AI agent logic here
    
    return {
      statusCode: 200,
      body: JSON.stringify({ message: `Hello from ${agentName}!` }),
    };
  };
  