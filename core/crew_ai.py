from crewai import Agent, Task, Crew, Process
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool
from crewai_tools.tools.serper_dev_tool.serper_dev_tool import SerperDevTool
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Pydantic models for structured output
class InsightItem(BaseModel):
    title: str = Field(description="Compelling insight title")
    summary: str = Field(description="Detailed insight summary")
    key_points: List[str] = Field(description="Key bullet points")
    detailed_report: str = Field(description="Comprehensive detailed analysis (500-800 words)")
    significance: str = Field(description="Why this insight matters")
    sources: List[str] = Field(description="Source URLs")
    confidence_score: float = Field(description="Confidence score 0-1")
    research_quality: str = Field(description="Quality assessment")

class GeneratedInsights(BaseModel):
    id: str = Field(description="Unique insight ID")
    topic: str = Field(description="Research topic")
    instructions: str = Field(description="User instructions")
    source_type: str = Field(description="Search source type (general/news)", default="general")
    time_range: Optional[str] = Field(description="Search time range filter", default=None)
    timestamp: str = Field(description="Generation timestamp")
    insights: List[InsightItem] = Field(description="Generated insights")
    total_insights: int = Field(description="Total number of insights")
    processing_time: float = Field(description="Time taken to generate")
    total_tokens: int = Field(description="Total tokens used", default=0)
    agent_notes: str = Field(description="Notes from AI agents")
    
    # Social features
    author_id: Optional[str] = Field(description="User ID of the author", default=None)
    author_name: Optional[str] = Field(description="Display name of the author", default="Anonymous")
    author_email: Optional[str] = Field(description="Email of the author", default=None)
    is_shared: bool = Field(description="Whether this insight is publicly shared", default=True)
    likes: int = Field(description="Number of likes", default=0)
    liked_by: List[str] = Field(description="List of user IDs who liked this", default_factory=list)

class AIInsightsCrew:
    """CrewAI crew for generating custom insights based on user input"""
    
    def __init__(self, tavily_key: str = None, serper_key: str = None, openai_key: str = None):
        self.tavily_key = tavily_key
        self.serper_key = serper_key
        self.openai_key = openai_key
        self.search_topic = "general"  # Default to general search
        self.search_time_range = None  # Default to no time range
        
        # Configure LLM
        self.llm = self._setup_llm()
        
        # Initialize search tools
        self.search_tools = []
        
        if tavily_key:
            try:
                # Try to initialize TavilySearchTool with error handling for version compatibility
                self.tavily_tool = TavilySearchTool(api_key=tavily_key)
                self.search_tools.append(self.tavily_tool)
                logger.info("✅ Tavily search tool initialized")
            except Exception as e:
                logger.warning(f"Warning: TavilySearchTool initialization failed: {e}")
                try:
                    # Create a basic web search tool as fallback
                    logger.info("🔄 Attempting to create fallback search tool...")
                    
                    # If we can't use Tavily, we'll rely on the SerperDevTool or basic web search
                    if serper_key:
                        from crewai_tools.tools.serper_dev_tool.serper_dev_tool import SerperDevTool
                        self.serper_tool = SerperDevTool(api_key=serper_key, n_results=10)
                        self.search_tools.append(self.serper_tool)
                        logger.info("✅ Serper search tool initialized as Tavily fallback")
                    else:
                        logger.warning("⚠️ No backup search tool available - continuing without advanced search")
                    
                except Exception as fallback_error:
                    logger.error(f"❌ Failed to initialize fallback search tools: {fallback_error}")
                    logger.warning("⚠️ Continuing with limited search capabilities")
        
        if serper_key and not self.search_tools:
            # Only initialize Serper if no search tools are available
            try:
                self.serper_tool = SerperDevTool(api_key=serper_key, n_results=10)
                self.search_tools.append(self.serper_tool)
                logger.info("✅ Serper search tool initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Serper search tool: {e}")
        
        if not tavily_key and not serper_key:
            raise ValueError("At least one search API key (Tavily or Serper) is required")
    
    def _setup_llm(self):
        """Setup LLM configuration using OpenAI API"""
        from crewai.llm import LLM
        
        if self.openai_key:
            return LLM(
                model="gpt-4o-mini",
                api_key=self.openai_key,
                temperature=0.1,
                max_tokens=16000
            )
        else:
            raise ValueError("OpenAI API key is required for CrewAI agents")
    
    def create_research_agent(self) -> Agent:
        """Research Specialist - finds information based on user topic"""
        return Agent(
            role="Senior Research Specialist",
            goal="Find comprehensive, accurate, and up-to-date information on any topic specified by the user",
            backstory="""You are an expert researcher with deep knowledge across multiple domains. 
            You excel at finding reliable sources, fact-checking information, and understanding 
            the nuances of different topics. You can quickly identify the most relevant and 
            significant information for any research query.""",
            verbose=True,
            tools=self.search_tools,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_validation_agent(self) -> Agent:
        """Content Validation Specialist - validates and scores information quality"""
        return Agent(
            role="Information Validation Specialist",
            goal="Validate information accuracy, assess source credibility, and ensure content quality",
            backstory="""You are an expert fact-checker and information analyst with years of experience 
            in validating content across various domains. You have a keen eye for identifying reliable 
            sources, detecting misinformation, and assessing the credibility of claims. You excel at 
            providing confidence scores and quality assessments.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_insights_agent(self) -> Agent:
        """Insights Generator - creates meaningful insights and analysis"""
        return Agent(
            role="Senior Insights Analyst",
            goal="Transform research findings into meaningful insights, patterns, and actionable intelligence",
            backstory="""You are a brilliant analyst who excels at connecting dots, identifying patterns, 
            and extracting meaningful insights from complex information. You have the ability to see 
            the bigger picture and understand implications that others might miss. You're known for 
            creating clear, actionable insights that help people make better decisions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_research_task(self, researcher_agent: Agent, topic: str, instructions: str) -> Task:
        """Research task for finding information on user-specified topic"""
        
        # Build search preferences based on user selections
        search_focus = ""
        if self.search_topic == "news":
            search_focus = "\n🔍 SEARCH FOCUS: Prioritize recent news articles, press releases, and current events related to this topic."
        elif self.search_topic == "finance":
            search_focus = "\n🔍 SEARCH FOCUS: Focus on financial data, business reports, market analysis, economic indicators, and finance-related content from reputable financial sources."
        else:
            search_focus = "\n🔍 SEARCH FOCUS: Search broadly across general web sources including academic papers, official websites, and comprehensive resources."
        
        time_preference = ""
        if self.search_time_range:
            time_periods = {
                "day": "past 24 hours",
                "week": "past week", 
                "month": "past month",
                "year": "past year"
            }
            time_preference = f"\n⏰ TIME PREFERENCE: Focus on information from the {time_periods.get(self.search_time_range, 'recent period')}."
        
        return Task(
            description=f"""Conduct comprehensive research on the topic: "{topic}"

            User Instructions: {instructions}{search_focus}{time_preference}

            Research Requirements:
            1. Find the most current and relevant information about this topic
            2. Look for multiple perspectives and viewpoints
            3. Identify key facts, statistics, and data points
            4. Find expert opinions and authoritative sources
            5. Look for recent developments and trends
            6. Gather information from reputable sources

            For each piece of information found, note:
            - The source and its credibility
            - The recency of the information
            - Key facts and data points
            - Expert opinions or quotes
            - Any conflicting viewpoints

            Focus on providing comprehensive coverage while following the user's specific instructions and search preferences.""",
            expected_output="A detailed research report with key findings, sources, and relevant information organized by importance and credibility.",
            agent=researcher_agent
        )
    
    def create_validation_task(self, validator_agent: Agent, research_task: Task) -> Task:
        """Validation task for assessing information quality and credibility"""
        return Task(
            description="""Validate and assess the quality of the research findings:

            1. **Source Credibility Assessment**:
               - Evaluate the reliability and authority of each source
               - Check for potential bias or conflicts of interest
               - Assess the expertise of authors/organizations

            2. **Information Accuracy Validation**:
               - Cross-reference facts and claims across multiple sources
               - Identify any inconsistencies or contradictions
               - Flag any unverified or questionable claims

            3. **Quality Scoring**:
               - Assign confidence scores (0-1) to each major finding
               - Rate the overall research quality
               - Identify the strongest and weakest evidence

            4. **Credibility Notes**:
               - Provide notes on source reliability
               - Highlight any limitations or caveats
               - Suggest areas that might need additional verification

            Provide a comprehensive validation report with confidence scores and quality assessments.""",
            expected_output="A validation report with confidence scores, source credibility assessments, and quality ratings for all research findings.",
            agent=validator_agent,
            context=[research_task]
        )
    
    def create_insights_task(self, insights_agent: Agent, research_task: Task, validation_task: Task, topic: str, instructions: str) -> Task:
        """Insights generation task for creating meaningful analysis"""
        return Task(
            description=f"""Generate meaningful insights and analysis based on the validated research:

            Topic: "{topic}"
            User Instructions: {instructions}

            Create comprehensive insights that include:

            1. **Key Insights** (3-5 main insights):
               - Clear, actionable insights derived from the research
               - Each insight should have a compelling title and detailed explanation
               - Include supporting evidence and data points
               - Explain the significance and implications

            2. **Analysis and Patterns**:
               - Identify important trends or patterns
               - Connect different pieces of information
               - Highlight cause-and-effect relationships
               - Draw meaningful conclusions

            3. **Practical Applications**:
               - How can this information be used?
               - What actions or decisions does it inform?
               - What are the practical implications?

            4. **Future Outlook**:
               - What trends are emerging?
               - What should people watch for?
               - What are the potential future developments?

            Ensure each insight is:
            - Well-supported by evidence
            - Clearly explained and actionable
            - Relevant to the user's topic and instructions
            - Properly sourced with URLs when available

            Structure the output to be engaging and easy to understand.
            
            **IMPORTANT**: Return the insights in the following structured format using the GeneratedInsights model:
            - id: Will be set automatically
            - topic: "{topic}"
            - instructions: "{instructions}"
            - timestamp: Will be set automatically
            - insights: List of InsightItem objects with title, summary, key_points, detailed_report, significance, sources, confidence_score, research_quality
            - total_insights: Count of insights
            - processing_time: Will be set automatically
            - agent_notes: Additional notes about the research process
            
            For each insight, the detailed_report field should contain:
            - Comprehensive analysis (500-800 words)
            - In-depth explanation of the findings
            - Supporting data and evidence
            - Context and background information
            - Implications and potential impact
            - Connections to related concepts or trends
            - Expert perspectives and opinions
            - Statistical data and research findings""",
            expected_output="A structured GeneratedInsights object containing 3-5 detailed insights with titles, summaries, key points, comprehensive detailed reports (500-800 words each), significance, sources, confidence scores, and quality assessments.",
            agent=insights_agent,
            context=[research_task, validation_task],
            output_pydantic=GeneratedInsights
        )
    
    def generate_insights(self, topic: str, instructions: str, source: str = "general", time_range: str = None) -> GeneratedInsights:
        """Generate insights based on user topic and instructions"""
        start_time = datetime.now()
        
        # Set search parameters for this session
        self.search_topic = source
        self.search_time_range = time_range if time_range and time_range != "none" else None
        
        # Create agents
        researcher = self.create_research_agent()
        validator = self.create_validation_agent()
        insights_agent = self.create_insights_agent()
        
        # Create tasks
        research_task = self.create_research_task(researcher, topic, instructions)
        validation_task = self.create_validation_task(validator, research_task)
        insights_task = self.create_insights_task(insights_agent, research_task, validation_task, topic, instructions)
        
        # Create and run crew
        crew = Crew(
            agents=[researcher, validator, insights_agent],
            tasks=[research_task, validation_task, insights_task],
            process=Process.sequential,
            verbose=True,
            memory=False
        )
        
        result = crew.kickoff()
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate total tokens used
        total_tokens = self._calculate_total_tokens(crew)
        
        # Extract insights from result
        if hasattr(result, 'pydantic') and result.pydantic:
            insights = result.pydantic
            # Ensure required fields are set
            insights.id = str(uuid.uuid4())
            insights.topic = topic
            insights.instructions = instructions
            insights.source_type = source
            insights.time_range = time_range
            insights.timestamp = datetime.now().isoformat()
            insights.processing_time = processing_time
            insights.total_tokens = total_tokens
            insights.total_insights = len(insights.insights) if insights.insights else 0
        else:
            # Fallback: create insights from text result
            insights = GeneratedInsights(
                id=str(uuid.uuid4()),
                topic=topic,
                instructions=instructions,
                source_type=source,
                time_range=time_range,
                timestamp=datetime.now().isoformat(),
                insights=[],
                total_insights=0,
                processing_time=processing_time,
                total_tokens=total_tokens,
                agent_notes=str(result)
            )
        
        return insights
    
    def _calculate_total_tokens(self, crew) -> int:
        """Calculate total tokens used by all agents in the crew"""
        total_tokens = 0
        
        try:
            # Try to get token usage from crew usage metrics (CrewAI 0.80+)
            if hasattr(crew, 'usage_metrics') and crew.usage_metrics:
                logger.info(f"Found usage_metrics: {crew.usage_metrics}")
                for metric in crew.usage_metrics:
                    if hasattr(metric, 'total_tokens'):
                        total_tokens += metric.total_tokens
                    elif hasattr(metric, 'prompt_tokens') and hasattr(metric, 'completion_tokens'):
                        total_tokens += metric.prompt_tokens + metric.completion_tokens
            
            # Try to get from crew._token_process (newer CrewAI versions)
            elif hasattr(crew, '_token_process') and crew._token_process:
                logger.info(f"Found _token_process: {crew._token_process}")
                if hasattr(crew._token_process, 'get_summary'):
                    summary = crew._token_process.get_summary()
                    if 'total_tokens' in summary:
                        total_tokens = summary['total_tokens']
            
            # Try to access from the crew's execution result
            elif hasattr(crew, '_execution_logs'):
                logger.info("Checking execution logs for token usage")
                # Parse execution logs for token information
                pass
            
            # If no token tracking available, provide intelligent estimation
            if total_tokens == 0:
                # More intelligent estimation based on task complexity with detailed reports
                # Research task: ~2000-3500 tokens (search + analysis)
                # Validation task: ~1500-2000 tokens (verification)
                # Insights task: ~5000-8000 tokens (synthesis + detailed reports + structured output)
                base_estimate = 8500
                
                # Adjust based on number of agents and tasks
                num_agents = len(crew.agents) if hasattr(crew, 'agents') else 3
                num_tasks = len(crew.tasks) if hasattr(crew, 'tasks') else 3
                
                total_tokens = base_estimate + (num_agents * 800) + (num_tasks * 500)
                logger.info(f"Estimated token usage: {total_tokens} (based on {num_agents} agents, {num_tasks} tasks)")
                
        except Exception as e:
            logger.warning(f"Could not calculate exact token usage: {e}")
            # Fallback estimation - conservative but reasonable for detailed reports
            total_tokens = 12000
        
        return total_tokens
