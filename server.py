""" 
Exposes at http://localhost:7777/mcp with tools: run_agent, get_agentos_config, etc. 
"""

from agno.os import AgentOS   
from agent import substack_author_agent                                                                                                                                

agent_os = AgentOS(                                                                                                                                           
    description="Substack Author Agent - content strategy powered by AI",                                                                                     
    agents=[substack_author_agent],                                                                                                                                           
    enable_mcp_server=True,                                                                                                                                   
)                                                                                                                                                             
app = agent_os.get_app()                                                                                                                                      
                                                                                                                                                              
if __name__ == "__main__":
    agent_os.serve(app="server:app", reload=False)