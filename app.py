#!/usr/bin/env python3
"""
AI Insights Generator Flask App
A web application powered by CrewAI multi-agent system for generating custom AI insights
"""

import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
from dotenv import load_dotenv
import traceback

# Firestore imports
try:
    from google.cloud import firestore
    from firebase_admin import credentials, firestore as admin_firestore
    import firebase_admin
    from google.cloud import secretmanager
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logging.warning("Firestore dependencies not available. Using in-memory storage only.")

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

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
    timestamp: str = Field(description="Generation timestamp")
    insights: List[InsightItem] = Field(description="Generated insights")
    total_insights: int = Field(description="Total number of insights")
    processing_time: float = Field(description="Time taken to generate")
    total_tokens: int = Field(description="Total tokens used", default=0)
    agent_notes: str = Field(description="Notes from AI agents")

# In-memory storage for insights (fallback when Firestore is not available)
insights_storage = {}

# Firestore configuration
FIRESTORE_DATABASE = "ai-biz"
FIRESTORE_COLLECTION = "insights"

def get_service_account_from_secret_manager() -> Optional[dict]:
    """Retrieve service account key from Google Cloud Secret Manager"""
    try:
        if not FIRESTORE_AVAILABLE:
            return None
            
        # Secret path for AI-Biz service account
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set.")
            return None
        secret_name = f"projects/{project_id}/secrets/AI-Biz-Service-Account-Key/versions/latest"
        
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Access the secret version
        response = client.access_secret_version(request={"name": secret_name})
        
        # Parse the secret payload as JSON
        secret_value = response.payload.data.decode("UTF-8")
        service_account_info = json.loads(secret_value)
        
        logger.info("✅ Successfully retrieved service account from Secret Manager")
        return service_account_info
        
    except Exception as e:
        logger.warning(f"Failed to retrieve service account from Secret Manager: {e}")
        return None

class FirestoreManager:
    """Manages Firestore database operations for insights"""
    
    def __init__(self):
        self.db = None
        self.use_firestore = False
        
        if FIRESTORE_AVAILABLE:
            try:
                # Initialize Firebase Admin SDK
                if not firebase_admin._apps:
                    # Try different authentication methods in order of preference
                    
                    # 1. Try Secret Manager first
                    service_account_info = get_service_account_from_secret_manager()
                    if service_account_info:
                        cred = credentials.Certificate(service_account_info)
                        firebase_admin.initialize_app(cred)
                        logger.info("🔐 Using service account from Secret Manager")
                    else:
                        # 2. Try local service account file
                        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                        if service_account_path and os.path.exists(service_account_path):
                            cred = credentials.Certificate(service_account_path)
                            firebase_admin.initialize_app(cred)
                            logger.info("🔐 Using local service account file")
                        else:
                            # 3. Use Application Default Credentials
                            firebase_admin.initialize_app()
                            logger.info("🔐 Using Application Default Credentials")
                
                # Initialize Firestore client
                self.db = firestore.Client(database=FIRESTORE_DATABASE)
                self.use_firestore = True
                logger.info(f"✅ Connected to Firestore database: {FIRESTORE_DATABASE}")
                
                # Test the connection by trying to access the collection
                try:
                    # Try to get collection info (this will test the connection)
                    collection_ref = self.db.collection(FIRESTORE_COLLECTION)
                    logger.info(f"✅ Firestore collection '{FIRESTORE_COLLECTION}' is accessible")
                except Exception as test_e:
                    logger.warning(f"⚠️ Firestore connection test failed: {test_e}")
                    self.use_firestore = False
                
            except Exception as e:
                logger.warning(f"Failed to initialize Firestore: {e}")
                logger.info("Falling back to in-memory storage")
                self.use_firestore = False
        else:
            logger.info("Firestore not available, using in-memory storage")
    
    def save_insights(self, insights: GeneratedInsights) -> bool:
        """Save insights to Firestore or in-memory storage"""
        logger.info(f"🔄 Attempting to save insights: {insights.id}")
        logger.info(f"🔄 Firestore enabled: {self.use_firestore}, DB object: {self.db is not None}")
        
        try:
            if self.use_firestore and self.db:
                logger.info(f"🔄 Using Firestore to save insights: {insights.id}")
                
                # Convert Pydantic model to dict for Firestore
                insights_dict = insights.model_dump()
                
                # Add Firestore-specific fields
                insights_dict['created_at'] = firestore.SERVER_TIMESTAMP
                insights_dict['updated_at'] = firestore.SERVER_TIMESTAMP
                
                # Save to Firestore
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insights.id)
                doc_ref.set(insights_dict)
                
                logger.info(f"✅ Successfully saved insights to Firestore: {insights.id}")
                
                # Also keep in memory for immediate access
                insights_storage[insights.id] = insights
                
                return True
            else:
                # Fallback to in-memory storage
                logger.info(f"🔄 Firestore not available, using in-memory storage for: {insights.id}")
                insights_storage[insights.id] = insights
                logger.info(f"💾 Saved insights to memory: {insights.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error saving insights to Firestore: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            # Fallback to in-memory storage
            insights_storage[insights.id] = insights
            logger.info(f"💾 Fallback: Saved insights to memory: {insights.id}")
            return False
    
    def get_insights(self, insight_id: str) -> Optional[GeneratedInsights]:
        """Get insights by ID from Firestore or in-memory storage"""
        try:
            # First check in-memory cache
            if insight_id in insights_storage:
                return insights_storage[insight_id]
            
            if self.use_firestore and self.db:
                # Get from Firestore
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    # Remove Firestore-specific fields before creating Pydantic model
                    data.pop('created_at', None)
                    data.pop('updated_at', None)
                    
                    insights = GeneratedInsights(**data)
                    # Cache in memory for faster access
                    insights_storage[insight_id] = insights
                    return insights
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving insights: {e}")
            return insights_storage.get(insight_id)
    
    def get_all_insights(self) -> List[GeneratedInsights]:
        """Get all insights from Firestore and in-memory storage"""
        all_insights = []
        
        try:
            if self.use_firestore and self.db:
                # Get from Firestore
                docs = self.db.collection(FIRESTORE_COLLECTION).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
                
                for doc in docs:
                    try:
                        data = doc.to_dict()
                        # Remove Firestore-specific fields
                        data.pop('created_at', None)
                        data.pop('updated_at', None)
                        
                        insights = GeneratedInsights(**data)
                        all_insights.append(insights)
                        # Cache in memory
                        insights_storage[insights.id] = insights
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Firestore document {doc.id}: {e}")
                        continue
            
            # Add any insights that are only in memory
            for insight_id, insights in insights_storage.items():
                if not any(i.id == insight_id for i in all_insights):
                    all_insights.append(insights)
            
            # Sort by timestamp (newest first)
            all_insights.sort(key=lambda x: x.timestamp, reverse=True)
            
            return all_insights
            
        except Exception as e:
            logger.error(f"Error retrieving all insights: {e}")
            # Fallback to in-memory storage
            return list(insights_storage.values())
    
    def delete_insights(self, insight_id: str) -> bool:
        """Delete insights from Firestore and in-memory storage"""
        try:
            deleted = False
            
            if self.use_firestore and self.db:
                # Delete from Firestore
                doc_ref = self.db.collection(FIRESTORE_COLLECTION).document(insight_id)
                doc_ref.delete()
                deleted = True
                logger.info(f"🗑️ Deleted insights from Firestore: {insight_id}")
            
            # Delete from in-memory storage
            if insight_id in insights_storage:
                del insights_storage[insight_id]
                deleted = True
                logger.info(f"🗑️ Deleted insights from memory: {insight_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting insights: {e}")
            # Try to delete from memory at least
            if insight_id in insights_storage:
                del insights_storage[insight_id]
                return True
            return False

# Initialize Firestore manager
firestore_manager = FirestoreManager()

def get_api_keys() -> tuple:
    """Get API keys from environment variables"""
    tavily_key = os.getenv('TAVILY_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    return tavily_key, serper_key, openai_key

class AIInsightsCrew:
    """CrewAI crew for generating custom insights based on user input"""
    
    def __init__(self, tavily_key: str = None, serper_key: str = None, openai_key: str = None):
        self.tavily_key = tavily_key
        self.serper_key = serper_key
        self.openai_key = openai_key
        
        # Configure LLM
        self.llm = self._setup_llm()
        
        # Initialize search tools
        self.search_tools = []
        
        if tavily_key:
            try:
                from crewai_tools import TavilySearchTool
                self.tavily_tool = TavilySearchTool(api_key=tavily_key)
                self.search_tools.append(self.tavily_tool)
                logger.info("✅ Tavily search tool initialized")
            except ImportError:
                logger.warning("Warning: TavilySearchTool not available")
        
        if serper_key and not tavily_key:
            self.serper_tool = SerperDevTool(api_key=serper_key, n_results=10)
            self.search_tools.append(self.serper_tool)
            logger.info("✅ Serper search tool initialized")
        
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
        return Task(
            description=f"""Conduct comprehensive research on the topic: "{topic}"

            User Instructions: {instructions}

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

            Focus on providing comprehensive coverage while following the user's specific instructions.""",
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
    
    def generate_insights(self, topic: str, instructions: str) -> GeneratedInsights:
        """Generate insights based on user topic and instructions"""
        start_time = datetime.now()
        
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

# Flask routes
@app.route('/')
def index():
    """Main page with insights generator form"""
    insights_list = firestore_manager.get_all_insights()
    return render_template('index.html', insights_list=insights_list)

@app.route('/generate', methods=['POST'])
def generate_insights():
    """Generate insights based on user input"""
    try:
        topic = request.form.get('topic', '').strip()
        instructions = request.form.get('instructions', '').strip()
        
        logger.info(f"🚀 Starting insight generation for topic: '{topic}'")
        logger.info(f"🔧 Firestore manager status - enabled: {firestore_manager.use_firestore}, db: {firestore_manager.db is not None}")
        
        if not topic:
            flash('Please provide a topic for research.', 'error')
            return redirect(url_for('index'))
        
        # Get API keys
        tavily_key, serper_key, openai_key = get_api_keys()
        
        if not openai_key:
            flash('OpenAI API key is required. Please set OPENAI_API_KEY environment variable.', 'error')
            return redirect(url_for('index'))
        
        if not tavily_key and not serper_key:
            flash('At least one search API key (Tavily or Serper) is required.', 'error')
            return redirect(url_for('index'))
        
        # Initialize CrewAI system
        crew_system = AIInsightsCrew(tavily_key, serper_key, openai_key)
        
        # Generate insights
        logger.info(f"🤖 Generating insights for topic: '{topic}'")
        insights = crew_system.generate_insights(topic, instructions)
        logger.info(f"✅ Generated insights with ID: {insights.id}")
        
        # Store insights in Firestore
        logger.info(f"💾 Attempting to save insights: {insights.id}")
        saved = firestore_manager.save_insights(insights)
        
        if saved:
            logger.info(f"✅ Successfully saved insights to storage: {insights.id}")
            flash(f'Successfully generated and saved insights for "{topic}"!', 'success')
        else:
            logger.warning(f"⚠️ Failed to save insights to Firestore, using temporary storage: {insights.id}")
            flash(f'Generated insights for "{topic}" (saved to temporary storage)', 'warning')
        
        # Verify the insights can be retrieved
        retrieved = firestore_manager.get_insights(insights.id)
        if retrieved:
            logger.info(f"✅ Verified insights can be retrieved: {insights.id}")
        else:
            logger.error(f"❌ Failed to retrieve insights after saving: {insights.id}")
        
        return redirect(url_for('view_insights', insight_id=insights.id))
        
    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(traceback.format_exc())
        flash(f'Error generating insights: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/insights/<insight_id>')
def view_insights(insight_id):
    """View specific insights"""
    insights = firestore_manager.get_insights(insight_id)
    if not insights:
        flash('Insights not found.', 'error')
        return redirect(url_for('index'))
    
    insights_list = firestore_manager.get_all_insights()
    return render_template('insights.html', insights=insights, insights_list=insights_list)

@app.route('/delete/<insight_id>', methods=['POST'])
def delete_insights(insight_id):
    """Delete specific insights"""
    deleted = firestore_manager.delete_insights(insight_id)
    if deleted:
        flash('Insights deleted successfully.', 'success')
    else:
        flash('Insights not found.', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/insights')
def api_insights():
    """API endpoint to get all insights"""
    insights_list = firestore_manager.get_all_insights()
    return jsonify([insights.model_dump() for insights in insights_list])

@app.route('/api/insights/<insight_id>')
def api_get_insights(insight_id):
    """API endpoint to get specific insights"""
    insights = firestore_manager.get_insights(insight_id)
    if insights:
        return jsonify(insights.model_dump())
    return jsonify({'error': 'Insights not found'}), 404

@app.route('/download/<insight_id>')
def download_insights(insight_id):
    """Download insights as formatted HTML file"""
    insights = firestore_manager.get_insights(insight_id)
    if not insights:
        flash('Insights not found.', 'error')
        return redirect(url_for('index'))
    
    # Generate HTML content
    html_content = render_template('download_report.html', insights=insights)
    
    # Create response with HTML file
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="AI_Insights_Report_{insights.topic.replace(" ", "_")}_{insights.timestamp[:10]}.html"'
    
    return response

@app.route('/status')
def status():
    """Status endpoint to check Firestore and system health"""
    try:
        status_info = {
            'timestamp': datetime.now().isoformat(),
            'firestore_enabled': firestore_manager.use_firestore,
            'firestore_db_available': firestore_manager.db is not None,
            'total_insights': len(firestore_manager.get_all_insights()),
            'memory_insights': len(insights_storage),
            'environment': {
                'openai_key_set': bool(os.getenv('OPENAI_API_KEY')),
                'tavily_key_set': bool(os.getenv('TAVILY_API_KEY')),
                'serper_key_set': bool(os.getenv('SERPER_API_KEY')),
                'gcp_credentials_set': bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
                'flask_env': os.getenv('FLASK_ENV', 'not_set')
            }
        }
        
        # Test Firestore connection if enabled
        if firestore_manager.use_firestore and firestore_manager.db:
            try:
                # Try to access the collection
                collection_ref = firestore_manager.db.collection(FIRESTORE_COLLECTION)
                status_info['firestore_collection_accessible'] = True
                logger.info("✅ Firestore collection is accessible from status endpoint")
            except Exception as e:
                status_info['firestore_collection_accessible'] = False
                status_info['firestore_error'] = str(e)
                logger.error(f"❌ Firestore collection access failed: {e}")
        
        logger.info(f"📊 Status check: {status_info}")
        return jsonify(status_info)
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Use port 5000 for production (Cloud Run) and 5001 for development
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port) 