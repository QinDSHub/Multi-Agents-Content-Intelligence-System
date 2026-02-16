"""
Multi-Agent Marketing Intelligence System using LangGraph

This graph orchestrates a pipeline of 7 specialized agents:
1. Search Agent - Finds relevant news articles via Google Search
2. Document Loaders - Loads content from web and local PDF sources
3. RAG Agent - Creates vector store and retrieves relevant content
4. Insights Extraction - Synthesizes strategic insights
5. Content Generation - Creates marketing content
6. Auto Publishing - Distributes to Facebook
7. Analytics - Analyzes post performance
"""

from typing import TypedDict, Optional, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
import operator

from agent.services.search_agent import google_search, AllSearchResults
from agent.services.search_doc_load import text_loader, AllSearchDocResults
from agent.services.local_doc_load import extract_text_from_pdf, AllLocalDocResults
from agent.services.rag_agent import reduce_agent, RagResult
from agent.services.insights_extract import insights_agent, AllStrategicInsights
from agent.services.content_generation import marketing_content_agent, AllMarketingContents
from agent.services.auto_publish import distributor_agent, FacebookPostRequest, DistributorOutput
from agent.services.auto_analysis_report import analytics_agent, AnalyticsReport


class MarketingState(TypedDict):
    """State object that flows through the multi-agent pipeline"""
    
    # Input parameters
    query: str
    local_pdf_path: Optional[str]
    facebook_page_id: Optional[str]
    facebook_access_token: Optional[str]
    db_path: str  # Vector store path
    
    # Intermediate results
    search_results: Optional[AllSearchResults]
    web_documents: Optional[AllSearchDocResults]
    local_documents: Optional[AllLocalDocResults]
    rag_results: Optional[RagResult]
    strategic_insights: Optional[AllStrategicInsights]
    marketing_contents: Optional[AllMarketingContents]
    publish_results: Optional[DistributorOutput]
    analytics_report: Optional[AnalyticsReport]
    
    # Control flow
    skip_local_docs: bool
    skip_publishing: bool
    skip_analytics: bool
    require_human_approval: bool
    
    # Human-in-the-loop
    human_approval: Optional[str]  # "approved", "rejected", or None
    human_feedback: Optional[str]  # Optional feedback from human reviewer
    
    # Error tracking
    errors: Annotated[List[str], operator.add]


def search_node(state: MarketingState) -> MarketingState:
    """Node 1: Execute Google Search for news articles"""
    print(f"🔍 Executing search for query: {state['query']}")
    try:
        results = google_search(state["query"])
        state["search_results"] = results
        print(f"✅ Found {len(results.results)} search results")
    except Exception as e:
        error_msg = f"Search node error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
    return state


def web_loader_node(state: MarketingState) -> MarketingState:
    """Node 2a: Load and clean content from web search results"""
    print("🌐 Loading content from web sources...")
    try:
        if state.get("search_results") and state["search_results"].results:
            docs = text_loader(state["search_results"])
            state["web_documents"] = docs
            print(f"✅ Loaded {len(docs.results)} web documents")
        else:
            state["web_documents"] = AllSearchDocResults()
            print("⚠️ No search results to load")
    except Exception as e:
        error_msg = f"Web loader error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
        state["web_documents"] = AllSearchDocResults()
    return state


def local_loader_node(state: MarketingState) -> MarketingState:
    """Node 2b: Load content from local PDF documents"""
    if state.get("skip_local_docs", False) or not state.get("local_pdf_path"):
        print("⏭️ Skipping local document loading")
        state["local_documents"] = AllLocalDocResults()
        return state
    
    print(f"📄 Loading local PDF: {state['local_pdf_path']}")
    try:
        docs = extract_text_from_pdf(state["local_pdf_path"])
        state["local_documents"] = docs
        print(f"✅ Loaded {len(docs.results)} local documents")
    except Exception as e:
        error_msg = f"Local loader error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
        state["local_documents"] = AllLocalDocResults()
    return state


def rag_node(state: MarketingState) -> MarketingState:
    """Node 3: Create vector store and retrieve relevant content"""
    print("🗄️ Building vector store and retrieving relevant content...")
    try:
        web_docs = state.get("web_documents") or AllSearchDocResults()
        local_docs = state.get("local_documents") or AllLocalDocResults()
        db_path = state.get("db_path", "./chroma_db")
        
        rag_results = reduce_agent(web_docs, local_docs, db_path)
        state["rag_results"] = rag_results
        print(f"✅ Retrieved {len(rag_results.content)} relevant chunks")
    except Exception as e:
        error_msg = f"RAG node error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
        # Create empty result to allow pipeline to continue
        state["rag_results"] = RagResult(content=[])
    return state


def insights_node(state: MarketingState) -> MarketingState:
    """Node 4: Extract and synthesize strategic insights"""
    print("💡 Extracting strategic insights...")
    try:
        if state.get("rag_results") and state["rag_results"].content:
            insights = insights_agent(state["rag_results"])
            state["strategic_insights"] = insights
            print(f"✅ Generated {len(insights.insights)} strategic insights")
        else:
            print("⚠️ No RAG results available for insights extraction")
            state["strategic_insights"] = None
    except Exception as e:
        error_msg = f"Insights node error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
    return state


def content_generation_node(state: MarketingState) -> MarketingState:
    """Node 5: Generate marketing content"""
    print("✍️ Generating marketing content...")
    try:
        if state.get("strategic_insights"):
            contents = marketing_content_agent(state["strategic_insights"])
            state["marketing_contents"] = contents
            print(f"✅ Generated {len(contents.contents)} marketing pieces")
        else:
            print("⚠️ No insights available for content generation")
            state["marketing_contents"] = None
    except Exception as e:
        error_msg = f"Content generation error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
    return state


def publishing_node(state: MarketingState) -> MarketingState:
    """Node 6: Publish content to Facebook"""
    if state.get("skip_publishing", False):
        print("⏭️ Skipping content publishing")
        return state
    
    print("📤 Publishing content to Facebook...")
    try:
        if not state.get("marketing_contents"):
            print("⚠️ No marketing content to publish")
            return state
            
        if not state.get("facebook_page_id") or not state.get("facebook_access_token"):
            print("⚠️ Facebook credentials not provided, skipping publishing")
            state["skip_publishing"] = True
            return state
        
        request = FacebookPostRequest(
            marketing_data=state["marketing_contents"],
            page_id=state["facebook_page_id"],
            access_token=state["facebook_access_token"]
        )
        results = distributor_agent(request)
        state["publish_results"] = results
        
        successful = sum(1 for r in results.results if r.status == "success")
        print(f"✅ Published {successful}/{len(results.results)} posts successfully")
    except Exception as e:
        error_msg = f"Publishing error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
    return state


def human_review_node(state: MarketingState) -> MarketingState:
    """Human-in-the-loop: Review and approve/reject content before publishing"""
    print("\n" + "=" * 60)
    print("👤 HUMAN REVIEW REQUIRED")
    print("=" * 60)
    
    if not state.get("marketing_contents"):
        print("⚠️ No marketing content available for review")
        state["human_approval"] = "rejected"
        return state
    
    # Display content for review
    print("\n📋 Generated Marketing Content:")
    print("-" * 60)
    
    for idx, content in enumerate(state["marketing_contents"].contents, 1):
        print(f"\n[Content #{idx}]")
        print(f"  Format: {content.content_format}")
        print(f"  Headline: {content.headline}")
        print(f"  Target Audience: {content.target_audience}")
        print(f"  Channels: {', '.join(content.distribution_channel)}")
        print(f"  Body: {content.body_text[:200]}...")
        print(f"  CTA: {content.call_to_action}")
        print("-" * 60)
    
    # Request human input
    print("\n🔍 Please review the content above.")
    print("Options:")
    print("  1. Type 'approve' or 'yes' to publish")
    print("  2. Type 'reject' or 'no' to skip publishing")
    print("  3. Add feedback after your choice (optional)")
    
    try:
        user_input = input("\nYour decision: ").strip().lower()
        
        if user_input in ["approve", "approved", "yes", "y"]:
            state["human_approval"] = "approved"
            print("✅ Content approved for publishing!")
        elif user_input in ["reject", "rejected", "no", "n"]:
            state["human_approval"] = "rejected"
            print("❌ Content rejected. Publishing will be skipped.")
        else:
            # Allow for feedback with decision
            if "approve" in user_input or "yes" in user_input:
                state["human_approval"] = "approved"
                state["human_feedback"] = user_input
                print("✅ Content approved with feedback!")
            else:
                state["human_approval"] = "rejected"
                state["human_feedback"] = user_input
                print("❌ Content rejected with feedback.")
        
        # Optional: Get additional feedback
        if state.get("human_approval") and not state.get("human_feedback"):
            feedback = input("\nOptional feedback (press Enter to skip): ").strip()
            if feedback:
                state["human_feedback"] = feedback
                
    except Exception as e:
        print(f"⚠️ Error getting human input: {e}")
        print("Defaulting to rejection for safety.")
        state["human_approval"] = "rejected"
    
    print("=" * 60 + "\n")
    return state


def check_approval(state: MarketingState) -> str:
    """Conditional edge: Route based on human approval"""
    approval_status = state.get("human_approval")
    
    if approval_status == "approved":
        return "publishing"
    else:
        # Skip publishing and analytics if rejected
        return "end"


def analytics_node(state: MarketingState) -> MarketingState:
    """Node 7: Analyze post performance"""
    if state.get("skip_analytics", False):
        print("⏭️ Skipping analytics")
        return state
    
    print("📊 Analyzing post performance...")
    try:
        if not state.get("publish_results"):
            print("⚠️ No published posts to analyze")
            return state
        
        # Extract post IDs from successful publications
        post_ids = [
            r.post_id for r in state["publish_results"].results 
            if r.status == "success" and r.post_id
        ]
        
        if not post_ids:
            print("⚠️ No successful posts to analyze")
            return state
        
        if not state.get("facebook_access_token"):
            print("⚠️ Facebook access token not provided, skipping analytics")
            return state
        
        report = analytics_agent(post_ids, state["facebook_access_token"])
        state["analytics_report"] = report
        print(f"✅ Generated analytics report for {len(report.summary_report)} posts")
        print(f"   Average CTR: {report.total_avg_ctr:.2%}")
        if report.top_performing_post_id:
            print(f"   Top post: {report.top_performing_post_id}")
    except Exception as e:
        error_msg = f"Analytics error: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"] = state.get("errors", []) + [error_msg]
    return state


# Build the graph
def create_graph(require_human_approval: bool = False) -> CompiledStateGraph:
    """
    Constructs and compiles the multi-agent marketing intelligence graph.
    
    Args:
        require_human_approval: If True, adds human-in-the-loop before publishing
    
    Returns:
        CompiledStateGraph: Ready-to-execute workflow
    """
    workflow = StateGraph(MarketingState)
    
    # Add all nodes
    workflow.add_node("search", search_node)
    workflow.add_node("web_loader", web_loader_node)
    workflow.add_node("local_loader", local_loader_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("insights", insights_node)
    workflow.add_node("content_generation", content_generation_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("publishing", publishing_node)
    workflow.add_node("analytics", analytics_node)
    
    # Define the flow
    workflow.set_entry_point("search")
    workflow.add_edge("search", "web_loader")
    workflow.add_edge("search", "local_loader")
    workflow.add_edge("web_loader", "rag")
    workflow.add_edge("local_loader", "rag")
    workflow.add_edge("rag", "insights")
    workflow.add_edge("insights", "content_generation")
    
    # Human-in-the-loop: Conditional routing after content generation
    if require_human_approval:
        workflow.add_edge("content_generation", "human_review")
        workflow.add_conditional_edges(
            "human_review",
            check_approval,
            {
                "publishing": "publishing",
                "end": END
            }
        )
    else:
        workflow.add_edge("content_generation", "publishing")
    
    workflow.add_edge("publishing", "analytics")
    workflow.add_edge("analytics", END)
    
    return workflow.compile()


# Create the compiled graph instance (default without human approval)
graph = create_graph(require_human_approval=False)


# Example usage function
def run_marketing_pipeline(
    query: str,
    local_pdf_path: Optional[str] = None,
    facebook_page_id: Optional[str] = None,
    facebook_access_token: Optional[str] = None,
    db_path: str = "./chroma_db",
    skip_publishing: bool = False,
    skip_analytics: bool = False,
    require_human_approval: bool = False
) -> MarketingState:
    """
    Execute the complete marketing intelligence pipeline.
    
    Args:
        query: Search query for finding relevant news
        local_pdf_path: Optional path to local PDF for additional context
        facebook_page_id: Facebook Page ID for publishing
        facebook_access_token: Facebook access token
        db_path: Path for vector store persistence
        skip_publishing: Skip the publishing step
        skip_analytics: Skip the analytics step
        require_human_approval: If True, pauses for human review before publishing
    
    Returns:
        Final state containing all results
    """
    # Create graph with appropriate configuration
    execution_graph = create_graph(require_human_approval=require_human_approval)
    
    initial_state: MarketingState = {
        "query": query,
        "local_pdf_path": local_pdf_path,
        "facebook_page_id": facebook_page_id,
        "facebook_access_token": facebook_access_token,
        "db_path": db_path,
        "search_results": None,
        "web_documents": None,
        "local_documents": None,
        "rag_results": None,
        "strategic_insights": None,
        "marketing_contents": None,
        "publish_results": None,
        "analytics_report": None,
        "skip_local_docs": local_pdf_path is None,
        "skip_publishing": skip_publishing,
        "skip_analytics": skip_analytics,
        "require_human_approval": require_human_approval,
        "human_approval": None,
        "human_feedback": None,
        "errors": []
    }
    
    print("🚀 Starting Multi-Agent Marketing Pipeline")
    if require_human_approval:
        print("👤 Human-in-the-loop: ENABLED")
    print("=" * 60)
    
    final_state = execution_graph.invoke(initial_state)
    
    print("=" * 60)
    if final_state.get("errors"):
        print(f"⚠️ Pipeline completed with {len(final_state['errors'])} error(s)")
        for error in final_state["errors"]:
            print(f"   • {error}")
    else:
        print("✅ Pipeline completed successfully!")
    
    return final_state


if __name__ == "__main__":
    # Example execution with human-in-the-loop
    result = run_marketing_pipeline(
        query="AI marketing trends 2025",
        # local_pdf_path="./path/to/document.pdf",  # Optional
        require_human_approval=True,  # Enable human review before publishing
        skip_publishing=False,  # Allow publishing if approved
        skip_analytics=True,
        # facebook_page_id="your_page_id",  # Add credentials when ready
        # facebook_access_token="your_token"
    )
    
    # Access results
    if result.get("strategic_insights"):
        print("\n📋 Strategic Insights:")
        for insight in result["strategic_insights"].insights:
            print(f"  • {insight.key_insight_content[:100]}...")
    
    if result.get("marketing_contents"):
        print(f"\n✍️ Generated {len(result['marketing_contents'].contents)} marketing pieces")
