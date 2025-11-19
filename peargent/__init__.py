# my_agent_lib/__init__.py

from os import name
from typing import Optional, Union, Type
from dotenv import load_dotenv

from peargent.core.router import round_robin_router
from peargent.core.state import State

load_dotenv()

from .core.agent import Agent
from .core.tool import Tool
from .tools import get_tool_by_name
from peargent.core.router import RouterResult, RoutingAgent
from .core.stopping import limit_steps, StepLimitCondition
from .core.pool import Pool
from .core.history import (
    ConversationHistory,
    HistoryStore,
    FunctionalHistoryStore,
    InMemoryHistoryStore,
    FileHistoryStore,
    Thread,
    Message,
    StorageType,
    SessionBuffer,
    File,
    Sqlite,
    Postgresql,
    Redis
)
from .config import HistoryConfig

# Try to import SQL-based stores
try:
    from .core.history import PostgreSQLHistoryStore
except ImportError:
    PostgreSQLHistoryStore = None

try:
    from .core.history import SQLiteHistoryStore
except ImportError:
    SQLiteHistoryStore = None

# Define what gets imported with "from peargent import *"
__all__ = [
    'create_agent',
    'create_tool',
    'create_pool',
    'create_routing_agent',
    'create_history',
    'Agent',
    'Tool',
    'Pool',
    'RoutingAgent',
    'RouterResult',
    'State',
    'SessionBuffer',
    'File',
    'Sqlite',
    'Postgresql',
    'Redis',
    'limit_steps',
    'StepLimitCondition',
    'ConversationHistory',
    'HistoryStore',
    'FunctionalHistoryStore',
    'InMemoryHistoryStore',
    'FileHistoryStore',
    'Thread',
    'Message',
    'HistoryConfig',
]

# Add SQL stores to __all__ if available
if PostgreSQLHistoryStore:
    __all__.append('PostgreSQLHistoryStore')
if SQLiteHistoryStore:
    __all__.append('SQLiteHistoryStore')

# Sentinel value to detect if tracing was explicitly passed
_TRACING_NOT_SET = object()

def create_agent(name: str, description: str, persona: str, model=None, tools=None, stop=None, history=None, tracing=_TRACING_NOT_SET, output_schema=None, max_retries: int = 3):
    """
    Create an agent with optional persistent history.

    Args:
        name: Agent name
        description: Agent description
        persona: Agent persona/system prompt
        model: LLM model instance
        tools: List of tool names (str) or Tool objects
        stop: Stop condition
        history: Optional ConversationHistory, HistoryConfig, or None for persistent conversation storage
        tracing: Enable/disable tracing for this agent. Behavior:
                 - None (default): Inherits from global tracer if enable_tracing() was called
                 - True: Explicitly enable tracing for this agent
                 - False: Explicitly disable tracing (opt-out), even if global tracing is enabled
        output_schema: Optional Pydantic model for structured output validation
        max_retries: Maximum number of retries for structured output validation (default: 3)

    Returns:
        Agent instance

    Examples:
        # Agent with default tracing behavior (inherits from global)
        enable_tracing(store_type="sqlite", ...)  # Enable global tracing
        agent = create_agent(
            name="Assistant",
            description="A helpful assistant",
            persona="You are helpful",
            model=groq()
        )  # This agent will be traced

        # Explicitly enable tracing for one agent
        agent = create_agent(..., tracing=True)  # Always traced

        # Opt-out from global tracing
        enable_tracing(...)  # Global tracing on
        agent = create_agent(..., tracing=False)  # This agent won't be traced

        # With history
        agent = create_agent(
            name="Assistant",
            description="A helpful assistant",
            persona="You are helpful",
            model=groq(),
            history=HistoryConfig(
                auto_manage_context=True,
                max_context_messages=10,
                strategy="smart",
                store=File(storage_dir="./conversations")
            )
        )
    """
    parsed_tools = []
    for t in tools or []:
        if isinstance(t, str):
            parsed_tools.append(get_tool_by_name(t))
        elif isinstance(t, Tool):
            parsed_tools.append(t)
        else:
            raise ValueError("Tools must be instances of the Tool class.")

    # Determine if tracing was explicitly set
    tracing_explicitly_set = tracing is not _TRACING_NOT_SET

    # Smart tracing logic:
    # 1. If tracing=True explicitly -> enable tracing
    # 2. If tracing=False explicitly -> disable tracing (opt-out)
    # 3. If tracing not set (None/default):
    #    - Check if global tracer was configured (enable_tracing() was called)
    #    - If global tracer configured and enabled -> inherit (enable tracing)
    #    - If global tracer not configured -> disable tracing (default off)
    if tracing is _TRACING_NOT_SET:
        # Check if global tracer was explicitly configured
        from peargent.telemetry.tracer import _global_tracer
        if _global_tracer is not None and _global_tracer.enabled:
            # Global tracer was configured with enable_tracing() and is enabled
            actual_tracing = True
        else:
            # No global tracer configured, default to disabled
            actual_tracing = False
    else:
        # User explicitly set tracing=True or tracing=False
        actual_tracing = tracing

    # Handle HistoryConfig
    if isinstance(history, HistoryConfig):
        config = history
        actual_history = config.create_history()
        return Agent(
            name=name,
            description=description,
            persona=persona,
            model=model,
            tools=parsed_tools,
            stop=stop,
            history=actual_history,
            tracing=actual_tracing,
            _tracing_explicitly_set=tracing_explicitly_set,
            output_schema=output_schema,
            max_retries=max_retries
        )

    # Legacy behavior
    return Agent(
        name=name,
        description=description,
        persona=persona,
        model=model,
        tools=parsed_tools,
        stop=stop,
        history=history,
        tracing=actual_tracing,
        _tracing_explicitly_set=tracing_explicitly_set,
        output_schema=output_schema,
        max_retries=max_retries
    )

def create_tool(
    name: str,
    description: str,
    input_parameters: dict,
    call_function,
    timeout: Optional[float] = None,
    max_retries: int = 0,
    retry_delay: float = 1.0,
    retry_backoff: bool = True,
    on_error: str = "raise",
    output_schema: Optional[Type] = None
):
    """
    Create a tool that agents can use.

    Args:
        name: Tool name
        description: Tool description
        input_parameters: Dictionary of parameter names to types
        call_function: Function to execute when tool is called
        timeout: Maximum execution time in seconds (None = no limit)
        max_retries: Number of retry attempts on failure (0 = no retries)
        retry_delay: Initial delay between retries in seconds
        retry_backoff: Use exponential backoff for retries (True = exponential, False = fixed delay)
        on_error: Error handling strategy - "raise" (default), "return_error", or "return_none"
        output_schema: Optional Pydantic model for output validation

    Returns:
        Tool instance

    Examples:
        # Basic tool
        tool = create_tool("calculator", "Does math", {"expr": str}, eval_expr)

        # Tool with 5-second timeout
        tool = create_tool("api_call", "Calls API", {"url": str}, fetch_api,
                          timeout=5.0)

        # Tool with retries and exponential backoff
        tool = create_tool("flaky_api", "Sometimes fails", {"id": int}, call_api,
                          max_retries=3, retry_delay=1.0, retry_backoff=True)

        # Tool with graceful error handling
        tool = create_tool("optional_tool", "Nice to have", {"x": str}, process,
                          on_error="return_error")

        # Tool with output validation
        class WeatherOutput(BaseModel):
            temp: float
            condition: str

        tool = create_tool("weather", "Get weather", {"city": str}, get_weather,
                          output_schema=WeatherOutput)
    """
    return Tool(
        name=name,
        description=description,
        input_parameters=input_parameters,
        call_function=call_function,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_backoff=retry_backoff,
        on_error=on_error,
        output_schema=output_schema
    )

def create_pool(agents, default_model=None, router=None, max_iter=5, default_state=None, history=None, tracing=False):
    """
    Create a pool of agents with optional persistent history.

    Args:
        agents: List of Agent instances
        default_model: Default LLM model for agents without one
        router: Router function or RoutingAgent
        max_iter: Maximum number of agent executions
        default_state: Optional State instance
        history: Optional ConversationHistory, HistoryConfig, or None for persistent conversation storage
        tracing: Enable tracing for all agents in the pool (default: False).
                 Individual agents with explicit tracing=False will not be overridden.

    Returns:
        Pool instance

    Examples:
        # New DSL with HistoryConfig
        pool = create_pool(
            agents=[agent1, agent2],
            history=HistoryConfig(
                auto_manage_context=True,
                max_context_messages=15,
                strategy="smart",
                store=SessionBuffer()
            )
        )

        # Enable tracing for all agents in pool
        pool = create_pool(
            agents=[agent1, agent2, agent3],
            tracing=True
        )

        # Mix: pool tracing enabled, but one agent explicitly opts out
        agent1 = create_agent(..., tracing=False)  # Will stay False
        agent2 = create_agent(...)  # Will become True from pool
        pool = create_pool(agents=[agent1, agent2], tracing=True)
    """
    # Handle HistoryConfig
    actual_history = None
    if isinstance(history, HistoryConfig):
        actual_history = history.create_history()
    else:
        actual_history = history

    return Pool(
        agents=agents,
        default_model=default_model,
        router=router or round_robin_router([agent.name for agent in agents]),
        max_iter=max_iter,
        default_state=default_state or State(),
        history=actual_history,
        tracing=tracing
    )

def create_routing_agent(name: str, model, persona: str, agents: list):
    """
    Create a routing agent that intelligently selects the next agent.

    Args:
        name: Router agent name
        model: LLM model instance
        persona: Router persona/system prompt
        agents: List of available agents

    Returns:
        RoutingAgent instance
    """
    return RoutingAgent(name=name, model=model, persona=persona, agents=agents)

def create_history(store_type=None, **kwargs) -> ConversationHistory:
    """
    Create a conversation history manager.

    Args:
        store_type: Either a string ("session_buffer", "file", "sqlite", "postgresql") for backward compatibility,
                   or a StorageType instance (SessionBuffer(), File(), Sqlite(), Postgresql(), Redis()) for new DSL.
        **kwargs: Additional parameters for backward compatibility with string-based API:
                 - storage_dir: Directory for file-based storage
                 - connection_string: PostgreSQL connection string
                 - database_path: SQLite database file path
                 - table_prefix: Prefix for database tables

    Returns:
        ConversationHistory instance

    Examples:
        # New DSL (recommended)
        history = create_history(store_type=SessionBuffer())
        history = create_history(store_type=File(storage_dir="./my_conversations"))
        history = create_history(store_type=Sqlite(database_path="./my_app.db"))
        history = create_history(store_type=Postgresql(
            connection_string="postgresql://user:pass@localhost:5432/mydb"
        ))
        history = create_history(store_type=Redis(host="localhost", port=6379))

        # Old string-based API (backward compatibility)
        history = create_history("session_buffer")
        history = create_history("file", storage_dir="./my_conversations")
        history = create_history("sqlite", database_path="./my_app.db")
        history = create_history("postgresql", connection_string="postgresql://...")
    """
    # Default to session_buffer if no store_type provided
    if store_type is None:
        store_type = "session_buffer"

    # Handle new class-based DSL
    if isinstance(store_type, StorageType):
        if isinstance(store_type, SessionBuffer):
            store = InMemoryHistoryStore()
        elif isinstance(store_type, File):
            store = FileHistoryStore(storage_dir=store_type.storage_dir)
        elif isinstance(store_type, Sqlite):
            if not SQLiteHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for SQLite storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = SQLiteHistoryStore(
                database_path=store_type.database_path,
                table_prefix=store_type.table_prefix
            )
        elif isinstance(store_type, Postgresql):
            if not PostgreSQLHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for PostgreSQL storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = PostgreSQLHistoryStore(
                connection_string=store_type.connection_string,
                table_prefix=store_type.table_prefix
            )
        elif isinstance(store_type, Redis):
            # Import Redis store dynamically
            try:
                from .core.history import RedisHistoryStore
            except ImportError:
                RedisHistoryStore = None
            
            if not RedisHistoryStore:
                raise ImportError(
                    "Redis is required for Redis storage. "
                    "Install it with: pip install redis"
                )
            store = RedisHistoryStore(
                host=store_type.host,
                port=store_type.port,
                db=store_type.db,
                password=store_type.password,
                key_prefix=store_type.key_prefix
            )
        else:
            raise ValueError(f"Unknown storage type: {type(store_type)}")
    
    # Handle backward-compatible string-based API
    elif isinstance(store_type, str):
        # Extract keyword arguments for backward compatibility
        storage_dir = kwargs.get("storage_dir", ".peargent_history")
        connection_string = kwargs.get("connection_string")
        database_path = kwargs.get("database_path", "peargent_history.db")
        table_prefix = kwargs.get("table_prefix", "peargent")
        
        if store_type == "session_buffer":
            store = InMemoryHistoryStore()
        elif store_type == "file":
            store = FileHistoryStore(storage_dir=storage_dir)
        elif store_type == "sqlite":
            if not SQLiteHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for SQLite storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = SQLiteHistoryStore(
                database_path=database_path,
                table_prefix=table_prefix
            )
        elif store_type == "postgresql":
            if not PostgreSQLHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for PostgreSQL storage. "
                    "Install it with: pip install sqlalchemy"
                )
            if not connection_string:
                raise ValueError("connection_string is required for PostgreSQL storage")
            store = PostgreSQLHistoryStore(
                connection_string=connection_string,
                table_prefix=table_prefix
            )
        else:
            raise ValueError(f"Unknown store_type: {store_type}. Use 'session_buffer', 'file', 'sqlite', or 'postgresql'")
    else:
        raise ValueError(f"store_type must be a string or StorageType instance, got {type(store_type)}")

    return ConversationHistory(store=store)