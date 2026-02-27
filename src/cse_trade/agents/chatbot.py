import json
import logging
import re
from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from .providers import LLMProviderFactory, get_settings

logger = logging.getLogger(__name__)


@tool
def get_market_indices():
    """Fetch current ASPI and S&P SL20 index data for the Colombo Stock Exchange."""
    from ..api.client import CSEClient
    client = CSEClient()
    indices = {
        "aspi": client.get_aspi_data(),
        "snp": client.get_snp_data()
    }
    return json.dumps(indices)


@tool
def get_trending_stocks():
    """Fetch the top 5 gainers and top 5 losers currently trending on the CSE."""
    from ..api.client import CSEClient
    client = CSEClient()
    trending = {
        "gainers": (client.get_top_gainers() or [])[:5],
        "losers": (client.get_top_losers() or [])[:5]
    }
    return json.dumps(trending)


@tool
def get_stock_quote(symbol: str):
    """Fetch detailed information and current price for a specific stock symbol (e.g., 'LOLC.N0000')."""
    from ..api.client import CSEClient
    client = CSEClient()
    return json.dumps(client.get_company_info(symbol.upper()))


@tool
def get_market_summary():
    """Fetch general market summary including total trades, volume, and turnover."""
    from ..api.client import CSEClient
    client = CSEClient()
    return json.dumps(client.get_market_summary())


def format_response(text: str) -> str:
    """Format response to be human readable, removing dictionary/list formatting and metadata."""
    if not text:
        return text

    # Convert to string if not already
    text = str(text)

    # If it's a JSON string, try to extract the 'content' field if it exists
    if (text.startswith("{") and text.endswith("}")) or (
        text.startswith("[") and text.endswith("]")
    ):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "content" in data:
                text = str(data["content"])
            elif isinstance(data, list) and len(data) > 0:
                # If it's a list, it might be a list of messages
                last = data[-1]
                if isinstance(last, dict) and "content" in last:
                    text = str(last["content"])
        except:
            pass

    # Remove content= prefix if present (common in LangChain string representations)
    text = re.sub(r"^content=['\"]", "", text)
    text = re.sub(r"['\"]$", "", text)

    # Remove any AIMessage, HumanMessage, etc wrapper text
    text = re.sub(
        r"^(AIMessage|HumanMessage|SystemMessage|ChatMessage)\(content=['\"]",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    # Also handle simpler class wrappers
    text = re.sub(
        r"^(AIMessage|HumanMessage|SystemMessage|ChatMessage)\s*",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Remove common metadata keys often found in raw LLM output strings
    metadata_patterns = [
        r"\bcontent=['\"].*?['\"]",
        r"additional_kwargs=\{.*?\}",
        r"response_metadata=\{.*?\}",
        r"usage_metadata=\{.*?\}",
        r"id=['\"].*?['\"]",
        r"name=['\"].*?['\"]",
        r"type=['\"].*?['\"]",
        r"example=\w+",
        r"tool_calls=\[.*?\]",
        r"invalid_tool_calls=\[.*?\]",
        # Aggressively remove signature and extras blocks
        r"signature:\s*['\"].*?['\"]",
        r"extras:\s*\{.*?\}",
        r"signature=['\"].*?['\"]",
        r"extras=.*?(\n|$)",
    ]

    for pattern in metadata_patterns:
        # Only remove if it looks like it's part of a metadata block (not regular text)
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

    # Specific fix for "type: 'text' text: '...' extras: signature: '...'"
    # Instead of non-greedy search which clips at first internal quote,
    # we first try to strip the problematic 'extras: signature:' block entirely
    # and then clean up the remaining prefixes.
    
    # Strip signature/extras first to avoid greedy/non-greedy confusion
    text = re.split(r"\bextras:\s*signature:", text, flags=re.IGNORECASE)[0]
    
    # Now try to extract from text: '...' by looking for the last quote if possible,
    # or just stripping the prefix if it's there.
    if re.search(r"^\s*type:\s*['\"]text['\"]\s+text:\s*['\"]", text, flags=re.IGNORECASE):
        # Remove the prefix
        text = re.sub(r"^\s*type:\s*['\"]text['\"]\s+text:\s*['\"]", "", text, flags=re.IGNORECASE)
        # Strip the trailing quote if it exists
        if text.endswith("'") or text.endswith('"'):
            text = text[:-1]
    elif re.search(r"^\s*text:\s*['\"]", text, flags=re.IGNORECASE):
        text = re.sub(r"^\s*text:\s*['\"]", "", text, flags=re.IGNORECASE)
        if text.endswith("'") or text.endswith('"'):
            text = text[:-1]

    # Strip structural prefixes if they are still at the start of the text
    obj_prefixes = [
        r"^(type:\s*['\"]?\w+['\"]?\s+)?text:\s*",
        r"^content:\s*",
        r"^response:\s*",
        r"^message:\s*",
    ]
    for p in obj_prefixes:
        text = re.sub(p, "", text, flags=re.IGNORECASE).strip()

    # Clean up lingering structural characters if they were part of a wrapper
    if text.strip().startswith("(") and text.strip().endswith(")"):
        text = text.strip()[1:-1]
    if text.strip().startswith("{") and text.strip().endswith("}"):
        text = text.strip()[1:-1]
    
    # Handle dictionary-like strings if they're still there
    if re.match(r"^\s*[\[{]", text.strip()):
        # Replace 'key': 'value' with 'key: value'
        text = re.sub(r"['\"]([\w\s]+)['\"]:\s*", r"\1: ", text)
        # Remove structural braces and brackets
        text = re.sub(r"[{\[\]}]", "", text)
        # Replace commas with newlines (often separates fields)
        text = re.sub(r",\s*", "\n", text)

    # Format bullets for consistency
    text = re.sub(r"^\s*[-*]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "• ", text, flags=re.MULTILINE)

    # Final cleanup of whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # If the text still looks like it's wrapped in quotes, strip them
    if (text.startswith("'") and text.endswith("'")) or (
        text.startswith('"') and text.endswith('"')
    ):
        # We only strip if it's likely a single quoted string (no internal quotes of same type at same nesting level)
        text = text[1:-1].strip()

    # Handle escaped newlines (literal \n) - common in some raw outputs
    text = text.replace("\\n", "\n")

    # Re-check bullets after newline replacement and header stripping
    text = re.sub(r"^\s*[-*•]\s+", "• ", text, flags=re.MULTILINE)

    # Final pass to remove common metadata prefixes that might have become visible
    final_prefixes = ["content=", "text=", "response=", "message=", "type: text text:"]
    for prefix in final_prefixes:
        if text.lower().startswith(prefix):
            text = text[len(prefix) :].strip().strip("'\"")

    # If there's a signature: header or similar left, strip it and everything after
    text = re.split(r"\bsignature:", text, flags=re.IGNORECASE)[0]
    text = re.split(r"\bextras:", text, flags=re.IGNORECASE)[0]

    return text.strip()


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]


class CSEAgent:
    def __init__(self, client, db):
        self.client = client
        self.db = db
        self.settings = get_settings()
        self.llm = None
        self.graph = None
        self.history = self.db.get_chat_history()
        self.tools = [get_market_indices, get_trending_stocks, get_stock_quote, get_market_summary]
        self._setup_agent()

    def clear_chat(self):
        """Clear the chat history in memory and database."""
        self.history = []
        self.db.clear_chat_history()
        logger.info("Chat history cleared")

    def _setup_agent(self):
        provider = self.settings.provider
        api_key = self.settings.api_key
        model = self.settings.model
        temperature = self.settings.temperature
        max_tokens = self.settings.max_tokens

        logger.info(
            f"Setting up agent: provider={provider}, model='{model}', has_api_key={bool(api_key)}"
        )

        if provider == "none":
            logger.info("Running in offline mode - no LLM configured")
            self.graph = self._build_offline_graph()
            return

        if not api_key and provider != "ollama":
            logger.warning(f"No API key for {provider}, running in offline mode")
            self.graph = self._build_offline_graph()
            return

        self.llm = LLMProviderFactory.create_llm(
            provider, api_key, model, temperature, max_tokens
        )

        if self.llm is None:
            logger.error(f"Failed to create LLM for {provider}")
            self.graph = self._build_offline_graph()
        else:
            # Bind tools if the LLM supports it
            try:
                if hasattr(self.llm, "bind_tools"):
                    self.llm = self.llm.bind_tools(self.tools)
                    logger.info("Tools bound to LLM")
            except Exception as e:
                logger.error(f"Error binding tools: {e}")

            logger.info(f"LLM initialized: {provider}/{model or 'default'}")
            self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("call_llm", self._call_llm)
        workflow.add_node("execute_tools", ToolNode(self.tools))

        workflow.set_entry_point("call_llm")

        # Routing logic
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "execute_tools"
            return END

        workflow.add_conditional_edges(
            "call_llm",
            should_continue,
            {
                "execute_tools": "execute_tools",
                END: END,
            },
        )
        workflow.add_edge("execute_tools", "call_llm")

        return workflow.compile()

    def _build_offline_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("generate_response", self._generate_offline_response)
        workflow.set_entry_point("generate_response")
        workflow.add_edge("generate_response", END)
        return workflow.compile()

    def refresh_llm(self):
        self._setup_agent()

    def _call_llm(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        system_prompt = self._build_system_prompt()
        
        # Ensure system prompt is always at the beginning
        # We handle this by prepending it if it's missing or if we're starting a new turn
        if not messages or not isinstance(messages[0], SystemMessage):
            chain_messages = [SystemMessage(content=system_prompt)] + list(messages)
        else:
            chain_messages = list(messages)

        try:
            logger.info("Invoking LLM for tool choice or response")
            response = self.llm.invoke(chain_messages)
            return {"messages": messages + [response]}
        except Exception as e:
            logger.error(f"LLM Error in _call_llm: {e}")
            # Fallback to a simple error message if something goes wrong
            error_msg = AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try again.")
            return {"messages": messages + [error_msg]}

    def _generate_offline_response(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Simple offline logic using the client directly for common queries
        # Re-using logic but cleaner
        market_data = {}
        try:
            market_data["aspi"] = self.client.get_aspi_data()
            market_data["snp"] = self.client.get_snp_data()
            market_data["gainers"] = self.client.get_top_gainers()
            market_data["losers"] = self.client.get_top_losers()
            market_data["summary"] = self.client.get_market_summary()
        except:
            pass

        response_text = self._generate_offline_fallback(str(last_message), market_data)
        return {"messages": messages + [AIMessage(content=response_text)]}

    def _build_system_prompt(self) -> str:
        return """You are the official Colombo Stock Exchange (CSE) Market Analyst Assistant. 
Your goal is to provide accurate, reliable, and professional financial data and analysis for the Sri Lankan market.

CORE INSTRUCTIONS:
1. NEVER hallucinate or guess stock prices, index values, or market statistics.
2. If you don't have the data, use the provided tools to fetch it.
3. If a tool returns no data or an error, explicitly state that the information is currently unavailable from the exchange.
4. Maintain a professional, objective, and data-centric tone.
5. Provide investment disclaimers when appropriate.
6. Use clear formatting: emojis (📈, 📉, 💰), bold headers, and bullet points.

AVAILABLE TOOLS:
- get_market_indices: Use this for overall market performance (ASPI, S&P SL20).
- get_trending_stocks: Use this to see which companies are moving the most today.
- get_stock_quote: Use this for detailed info on a specific symbol (e.g., LOLC, SAMP, COMB).
- get_market_summary: Use this for volume and turnover totals.

Always prioritize tool data over any internal knowledge. Re-format the raw tool data into professional, human-readable Sri Lankan market reports."""

    def _generate_offline_fallback(self, question: str, market_data: dict) -> str:
        # (keep existing fallback logic but make it a private helper)
        question_lower = question.lower()
        if "aspi" in question_lower or ("index" in question_lower and "s&p" not in question_lower):
            if market_data.get("aspi"):
                data = market_data["aspi"]
                return f"📊 **ASPI Index**\n\n• **Value:** {data.get('value', 'N/A')}\n• **Change:** {data.get('change', 'N/A')} ({data.get('changePercentage', 'N/A')}%)"
            return "ASPI data is currently unavailable in offline mode."
        
        if "gainers" in question_lower:
            gainers = market_data.get("gainers", [])
            if gainers:
                resp = "📈 **Top Gainers**\n\n"
                for g in gainers[:5]:
                    resp += f"• **{g.get('symbol')}**: Rs. {g.get('price')} (+{g.get('change')}%)\n"
                return resp
            return "Trending data unavailable."

        return """I am currently in **offline mode**. 

To get real-time AI analysis and handle complex stock queries, please configure an LLM provider (OpenAI, Gemini, etc.) in the Settings tab. 

In offline mode, I can only provide basic data for:
• ASPI / S&P SL20 Indices
• Top Gainers & Losers
• Market Summary"""

    def stream_chat(self, user_input: str):
        """Stream responses from the agent."""
        if not hasattr(self, "graph") or self.graph is None:
            yield "Agent not initialized. Please configure your LLM provider in Settings."
            return

        user_msg = HumanMessage(content=user_input)
        self.history.append(user_msg)
        self.db.save_chat_history(self.history)

        try:
            # We track the last AI message added to update it
            final_response = ""
            for event in self.graph.stream(
                {"messages": self.history},
                stream_mode="values",
                config={"configurable": {"thread_id": "cse_trade_session"}},
            ):
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if isinstance(last_msg, AIMessage) and last_msg.content:
                        content = format_response(str(last_msg.content))
                        if content and content != final_response:
                            final_response = content
                            yield final_response
            
            # Save the final consolidated history
            if final_response:
                self.history.append(AIMessage(content=final_response))
                self.db.save_chat_history(self.history)
                
        except Exception as e:
            logger.error(f"Stream Chat error: {e}")
            yield f"Error: {str(e)}"

    def chat(self, user_input: str) -> str:
        if not hasattr(self, "graph") or self.graph is None:
            return "Agent not initialized. Please configure your LLM provider in Settings."

        user_msg = HumanMessage(content=user_input)
        self.history.append(user_msg)
        self.db.save_chat_history(self.history)

        try:
            result = self.graph.invoke(
                {"messages": self.history},
                config={"configurable": {"thread_id": "cse_trade_session"}},
            )
            
            if not result.get("messages"):
                return "No response generated."

            last_msg = result["messages"][-1]
            response_text = format_response(str(last_msg.content))
            
            self.history.append(AIMessage(content=response_text))
            self.db.save_chat_history(self.history)
            
            return response_text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error: {str(e)}"


_agent_instance = None


def get_agent(client, db):
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CSEAgent(client, db)
    return _agent_instance


def reset_agent():
    global _agent_instance
    _agent_instance = None
