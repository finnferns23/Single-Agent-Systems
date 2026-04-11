import os
import pandas as pd
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool, FunctionTool
from llama_index.core.agent import ReActAgent
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI LLM and embeddings
llm = OpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# Define index storage path
INDEX_STORAGE_DIR = "index_storage"

# Tool 1: Order ID lookup tool (for specific order queries)
def lookup_order(order_id: str) -> str:
    """Look up specific order details by Order ID."""
    try:
        df = pd.read_csv("sales_data.csv")
        
        # Clean the order ID (remove spaces, make uppercase)
        order_id = order_id.strip().upper()
        
        # Search for the order
        order_data = df[df['OrderID'].str.upper() == order_id]
        
        if order_data.empty:
            return f"No order found with ID: {order_id}"
        
        order = order_data.iloc[0]
        return (f"Order Details for {order_id}:\n"
                f"Date: {order['Date']}\n"
                f"Region: {order['Region']}\n"
                f"Product: {order['Product']}\n"
                f"Category: {order['Category']}\n"
                f"Quantity: {order['Quantity']}\n"
                f"Unit Price: ${order['UnitPrice']:.2f}\n"
                f"Total Sale: ${order['TotalSale']:.2f}")
    
    except Exception as e:
        return f"Error looking up order: {str(e)}"

order_lookup_tool = FunctionTool.from_defaults(
    fn=lookup_order,
    name="order_lookup_tool",
    description="Look up specific order details by Order ID. Use for queries about specific orders like 'ORD0001', 'ORD0002', etc."
)

# Tool 2: Analytics tool for calculations
def compute_analytics(metric: str, column: str, filter_condition: str = None) -> str:
    """Compute statistical metrics on sales data with optional filtering."""
    try:
        df = pd.read_csv("sales_data.csv")
        if filter_condition:
            # Map common column name variations to actual CSV columns
            filter_condition = filter_condition.replace("product", "Product")
            filter_condition = filter_condition.replace("region", "Region")
            filter_condition = filter_condition.replace("category", "Category")
            filter_condition = filter_condition.replace("unit_price", "UnitPrice")
            filter_condition = filter_condition.replace("total_sale", "TotalSale")
            filter_condition = filter_condition.replace("sales", "TotalSale")
            df = df.query(filter_condition)
        
        # Map column names to actual CSV columns
        column_mapping = {
            "sales": "TotalSale",
            "unit_price": "UnitPrice",
            "quantity": "Quantity",
            "total_sale": "TotalSale"
        }
        actual_column = column_mapping.get(column, column)
        
        if actual_column not in df.columns:
            return f"Error: Column '{actual_column}' not found. Available columns: {list(df.columns)}"
        
        if metric == "sum":
            result = df[actual_column].sum()
            return f"The total {column} is ${result:.2f}" if column in ['sales', 'total_sale'] else f"The total {column} is {result:.2f}"
        elif metric == "average":
            result = df[actual_column].mean()
            return f"The average {column} is ${result:.2f}" if column in ['sales', 'total_sale'] else f"The average {column} is {result:.2f}"
        elif metric == "count":
            result = len(df)
            return f"The count is {result}"
        return "Error: Unsupported metric. Use 'sum', 'average', or 'count'."
    except Exception as e:
        return f"Error in computation: {str(e)}"

analytics_tool = FunctionTool.from_defaults(
    fn=compute_analytics,
    name="analytics_tool",
    description="Computes statistical metrics (sum, average, count) on sales data with optional filters. Use for calculations across multiple orders."
)

# Tool 3: Data summary tool
def get_data_summary() -> str:
    """Get overall summary of the sales data."""
    try:
        df = pd.read_csv("sales_data.csv")
        summary = (
            f"Sales Data Summary:\n"
            f"Total Orders: {len(df)}\n"
            f"Total Sales: ${df['TotalSale'].sum():.2f}\n"
            f"Average Order Value: ${df['TotalSale'].mean():.2f}\n"
            f"Date Range: {df['Date'].min()} to {df['Date'].max()}\n"
            f"Regions: {', '.join(df['Region'].unique())}\n"
            f"Categories: {', '.join(df['Category'].unique())}\n"
            f"Products: {', '.join(df['Product'].unique())}"
        )
        return summary
    except Exception as e:
        return f"Error getting summary: {str(e)}"

summary_tool = FunctionTool.from_defaults(
    fn=get_data_summary,
    name="summary_tool",
    description="Get overall summary of sales data including total orders, sales, date range, and available regions/categories."
)

# Check if index exists on disk and is complete
index_storage_path = Path(INDEX_STORAGE_DIR)
index_exists = index_storage_path.exists()

if index_exists:
    try:
        logger.info("Loading existing index from disk...")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_DIR)
        index = load_index_from_storage(storage_context=storage_context, embed_model=embed_model)
        logger.info("Index loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading index: {e}. Recreating index...")
        index_exists = False

if not index_exists:
    logger.info("Indexing sales data...")
    sales_df = pd.read_csv("sales_data.csv")
    
    documents = []
    for _, row in sales_df.iterrows():
        text = (f"Order {row['OrderID']}: On {row['Date']}, in {row['Region']} region, "
                f"sold {row['Quantity']} units of {row['Product']} ({row['Category']}) "
                f"at ${row['UnitPrice']:.2f} each, totaling ${row['TotalSale']:.2f}")
        documents.append(Document(text=text))
    
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, transformations=[splitter])
    index.storage_context.persist(persist_dir=INDEX_STORAGE_DIR)
    logger.info("Indexing complete and saved to disk.")

# Create query engine for general queries
query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)

# Define query engine tool
sales_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="sales_data_tool",
    description="Provides general insights and trends from sales data. Use for questions about patterns, trends, or general information."
)

# Create ReAct agent with all tools
agent = ReActAgent.from_tools(
    [sales_tool, order_lookup_tool, analytics_tool, summary_tool], 
    llm=llm, 
    verbose=True,
    context="You are a sales data analyst. Use order_lookup_tool for specific order IDs, analytics_tool for calculations, summary_tool for overview, and sales_data_tool for general trends."
)

# Function to query sales data using the agent
def analyze_sales(query, query_history):
    response = agent.chat(query)
    query_history.append((query, str(response)))
    return response

# Interactive query loop with query history
if __name__ == "__main__":
    query_history = []
    print("Welcome to InsightPulse: Your AI-Powered Sales Report Analysis Tool!")
    print("Enter your query (e.g., 'What is the total sale of order ORD0004?')")
    print("Type 'history' to view recent queries, 'exit' to quit.")
    
    while True:
        user_query = input("\nYour query: ").strip()
        if user_query.lower() == "exit":
            print("Exiting InsightPulse. Goodbye!")
            break
        if user_query.lower() == "history":
            if query_history:
                print("\nRecent Queries:")
                for i, (q, r) in enumerate(query_history[-5:], 1):
                    print(f"{i}. Query: {q}\n   Response: {r[:100]}...")
            else:
                print("No query history yet.")
            continue
        if not user_query:
            print("Please enter a valid query.")
            continue
            
        print(f"\nProcessing query: {user_query}")
        try:
            response = analyze_sales(user_query, query_history)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error processing query: {e}")